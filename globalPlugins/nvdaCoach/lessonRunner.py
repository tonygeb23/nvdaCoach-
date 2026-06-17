# NVDA Coach - Lesson Runner
# Delivers lessons step-by-step through the CoachWindow.
# There is NO global gesture interception — the student tries each command
# freely on their own, then returns to the CoachWindow and presses Enter
# (or clicks Next Step) to confirm and move on.

import os
import wx
import ui
import nvwave
import config
import addonHandler
addonHandler.initTranslation()
from logHandler import log

_SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")


def _playSound(filename):
	"""Play a WAV file from the sounds/ folder, gated on the playSounds setting."""
	if config.conf["nvdaCoach"]["playSounds"]:
		path = os.path.join(_SOUNDS_DIR, filename)
		nvwave.playWaveFile(path)


def personalizeText(text):
	"""Replace {name} token in lesson content with the configured user name.

	Infrastructure for lesson JSON files that include {name} placeholders.
	No lesson files use it today, but the substitution is ready when needed.
	When userName is not configured the token is silently removed.
	"""
	name = config.conf["nvdaCoach"].get("userName", "").strip()
	if "{name}" in text:
		text = text.replace("{name}", name) if name else text.replace("{name}", "")
	return text


class LessonRunner:
	"""Runs an interactive lesson, advancing through steps when the student confirms."""

	# Show full controls reminder only on first lesson per NVDA session.
	_controlsIntroShown = False
	# Show name/instructor greeting only on first lesson per NVDA session.
	_instructorGreetingShown = False

	def __init__(self, progressTracker):
		self._progressTracker = progressTracker
		self.isActive = False
		self._categoryId = None
		self._categoryTitle = ""
		self._lesson = None
		self._stepIndex = 0
		self._pendingTimer = None
		self.coachWindow = None  # Set by GlobalPlugin after creation.
		self.onOpenPracticePage = None  # Callback: fired when a step with openPracticePageAfter is advanced past.
		self.onOpenPracticeFrame = None  # Callback: fired when a step with openPracticeFrameAfter is advanced past.
		self.onChapterComplete = None   # Callback: fired when a lesson with chapterComplete: true finishes.
		self.onLessonComplete = None    # Callback(categoryId, lessonId): fired at end of every lesson.
		self._hintIndex = 0  # Tracks which hint in a hints array to show next.

	# ------------------------------------------------------------------
	# Public API
	# ------------------------------------------------------------------

	def startLesson(self, categoryId, lesson, categoryTitle=""):
		"""Begin running a lesson."""
		if self.isActive:
			return
		self._categoryId = categoryId
		self._categoryTitle = categoryTitle
		self._lesson = lesson
		self._stepIndex = 0
		self.isActive = True

		# Lesson start sound.
		_playSound("lesson_start.wav")

		lessonTitle = self._lesson.get("title", _("Lesson"))

		# One-time personalized greeting at the very first lesson of the session.
		name = config.conf["nvdaCoach"].get("userName", "").strip()
		instructor = config.conf["nvdaCoach"].get("instructorName", "").strip()
		greeting = ""
		if not LessonRunner._instructorGreetingShown:
			if name:
				greeting += _("Hello, {name}! ").format(name=name)
			if instructor:
				greeting += _("Your instructor today is {instructor}. ").format(instructor=instructor)
			if greeting:
				LessonRunner._instructorGreetingShown = True

		if LessonRunner._controlsIntroShown:
			introMsg = greeting + _("Starting lesson: {title}.").format(title=lessonTitle)
		else:
			introMsg = (
				greeting
				+ _("Starting lesson: {title}.").format(title=lessonTitle) + " "
				+ _(
					"Press Enter or the Next Step button to advance. "
					"F1 repeats the instruction, F2 gives a hint, "
					"Escape stops the lesson."
				)
			)
			LessonRunner._controlsIntroShown = True

		wx.CallLater(600, ui.message, introMsg)
		wx.CallLater(600 + self._estimateReadTime(introMsg), self._speakCurrentStep)

	def stopLesson(self, announce=True):
		"""Stop the current lesson."""
		if not self.isActive:
			return
		self._cancelPendingTimer()
		self.isActive = False
		if announce:
			_playSound("lesson_stop.wav")
			ui.message(_(
				"Lesson stopped. "
				"Press NVDA+Shift+C to choose another lesson, "
				"or Ctrl+R to restart this one."
			))
		if self.coachWindow:
			self.coachWindow.showIdle(_("Lesson stopped."))

	def cleanup(self):
		"""Called when the add-on terminates."""
		self.stopLesson(announce=False)

	# ------------------------------------------------------------------
	# Actions called by CoachWindow keyboard handler and buttons
	# ------------------------------------------------------------------

	def advanceCurrentStep(self):
		"""Move to the next step. Called by Enter key or Next Step button."""
		if not self.isActive:
			return
		self._cancelPendingTimer()
		_playSound("step_advance.wav")
		self._advanceStep()

	def repeatInstruction(self):
		"""Re-read the current step instruction. Called by F1."""
		if not self.isActive:
			return
		step = self._currentStep()
		if step:
			ui.message(personalizeText(step.get("instruction", "")))

	def speakHint(self):
		"""Read the hint for the current step. Called by F2. Cycles through hints array."""
		if not self.isActive:
			return
		step = self._currentStep()
		if not step:
			return
		hints = step.get("hints")
		if hints and isinstance(hints, list) and len(hints) > 0:
			hint = personalizeText(hints[self._hintIndex % len(hints)])
			self._hintIndex += 1
			idx = (self._hintIndex - 1) % len(hints) + 1
			if len(hints) > 1:
				# Translators: hint counter, e.g. "Hint 2 of 3: ..."
				label = _("Hint {idx} of {total}: {hint}").format(idx=idx, total=len(hints), hint=hint)
			else:
				label = _("Hint: {hint}").format(hint=hint)
			_playSound("hint.wav")
			ui.message(label)
		else:
			# Fall back to legacy single hint string.
			hint = personalizeText(step.get("hint", _("No additional hint is available for this step.")))
			_playSound("hint.wav")
			ui.message(_("Hint: {hint}").format(hint=hint))

	def skipStep(self):
		"""Skip the current step without marking it correct. Called by F3."""
		if not self.isActive:
			return
		ui.message(_("Step skipped."))
		self._advanceStep()

	# ------------------------------------------------------------------
	# Step navigation
	# ------------------------------------------------------------------

	def _currentStep(self):
		"""Return the current step dict, or None if out of bounds."""
		steps = self._lesson.get("steps", [])
		if 0 <= self._stepIndex < len(steps):
			return steps[self._stepIndex]
		return None

	def _speakCurrentStep(self):
		"""Announce the instruction for the current step and update CoachWindow."""
		if not self.isActive:
			return
		self._hintIndex = 0  # Reset hint cycling whenever a new step begins.
		step = self._currentStep()
		if step is None:
			self._completeLesson()
			return

		instruction = personalizeText(step.get("instruction", ""))
		stepType = step.get("type", "info")
		stepNum = self._stepIndex + 1
		totalSteps = len(self._lesson.get("steps", []))
		# Translators: step position prefix spoken before each instruction
		prefix = _("Step {stepNum} of {totalSteps}. ").format(stepNum=stepNum, totalSteps=totalSteps)

		# Gesture steps tell the student to try the key themselves, then confirm.
		if stepType == "gesture":
			advance_cue = (
				"\n\n" + _(
					"Try it now. When you are ready to continue, "
					"press Enter or click Next Step."
				)
			)
			displayInstruction = instruction + advance_cue
		else:
			displayInstruction = instruction

		# If the step defines inline practice text, append it to the display.
		# The student can arrow down into it directly within the CoachWindow.
		practiceText = step.get("practiceText", "")
		if practiceText:
			displayInstruction += (
				"\n\n"
				# Translators: heading shown above inline practice text area
				+ _("PRACTICE AREA — NAVIGATE WITH ARROW KEYS:") + "\n\n"
				+ practiceText
			)

		if self.coachWindow:
			self.coachWindow.updateDisplay(
				self._categoryTitle,
				self._lesson.get("title", ""),
				self._stepIndex,
				totalSteps,
				displayInstruction,
			)

		spokenMsg = prefix + instruction
		if stepType == "gesture":
			spokenMsg += " " + _(
				"Try it now. When you are ready to continue, press Enter or click Next Step."
			)
		ui.message(spokenMsg)

	def _advanceStep(self):
		"""Move to the next step, or complete the lesson if done."""
		if not self.isActive:
			return
		self._pendingTimer = None
		prevStep = self._currentStep()  # Capture before incrementing.
		self._stepIndex += 1
		steps = self._lesson.get("steps", [])
		if self._stepIndex >= len(steps):
			self._completeLesson()
		else:
			if prevStep and prevStep.get("openPracticePageAfter") and self.onOpenPracticePage:
				wx.CallAfter(self.onOpenPracticePage)
			if prevStep and prevStep.get("openPracticeFrameAfter") and self.onOpenPracticeFrame:
				wx.CallAfter(self.onOpenPracticeFrame)
			self._speakCurrentStep()

	def _completeLesson(self):
		"""Handle lesson completion."""
		self.isActive = False
		self._cancelPendingTimer()

		totalSteps = len(self._lesson.get("steps", []))
		self._progressTracker.markLessonComplete(
			self._categoryId,
			self._lesson.get("id", "unknown"),
			{},
			totalSteps,
		)

		# Lesson complete sound.
		_playSound("lesson_complete.wav")

		lessonTitle = self._lesson.get("title", _("Lesson"))
		name = config.conf["nvdaCoach"].get("userName", "").strip()
		well_done = _("Well done, {name}!").format(name=name) if name else _("Well done.")
		# Check for full-course completion synchronously before scheduling any UI.
		# onLessonComplete returns True when every lesson in the course is now done.
		is_final = False
		if self.onLessonComplete:
			is_final = bool(self.onLessonComplete(self._categoryId, self._lesson.get("id", "")))

		if is_final:
			# Final lesson of the entire course: speak only a brief "well done" —
			# the full heartfelt congratulations screen fires 2500 ms later from GlobalPlugin.
			msg = _("Lesson complete: {title}! ").format(title=lessonTitle) + well_done
			wx.CallLater(600, ui.message, msg)
		else:
			msg = (
				_("Lesson complete: {title}! ").format(title=lessonTitle)
				+ well_done + " "
				+ _(
					"Press NVDA+Shift+C to open the lesson picker and choose your next lesson "
					"or continue to the next chapter. "
					"Ctrl+N moves to the next lesson in this category, "
					"or Ctrl+R repeats this one."
				)
			)
			wx.CallLater(600, ui.message, msg)
			if self.coachWindow:
				idleMsg = (
					_("Lesson complete: {title}!").format(title=lessonTitle) + "\n\n"
					+ well_done + "\n\n"
					"--- " + _("WHAT TO DO NEXT") + " ---\n"
					"  " + _("Press NVDA+Shift+C to open the lesson picker.") + "\n"
					"  " + _("Choose the next lesson in this chapter, or start the next chapter.") + "\n\n"
					"--- " + _("STAY IN THIS CHAPTER") + " ---\n"
					"  Ctrl+N  —  " + _("Next lesson in this category.") + "\n"
					"  Ctrl+R  —  " + _("Repeat this lesson.") + "\n"
					"  Ctrl+B  —  " + _("Go back to the previous lesson.")
				)
				wx.CallLater(600, self.coachWindow.showIdle, idleMsg)
			# If this lesson marks the end of a chapter, fire the chapter-complete callback.
			if self._lesson.get("chapterComplete") and self.onChapterComplete:
				wx.CallLater(3000, self.onChapterComplete)

	# ------------------------------------------------------------------
	# Utility helpers
	# ------------------------------------------------------------------

	def _cancelPendingTimer(self):
		"""Cancel any pending wx.CallLater timer."""
		if self._pendingTimer is not None:
			try:
				self._pendingTimer.Stop()
			except Exception:
				pass
			self._pendingTimer = None

	def _estimateReadTime(self, text):
		"""Estimate milliseconds needed to read a message at typical speech rate."""
		chars = len(text)
		return max(1500, min(8000, int(chars / 15 * 1000)))
