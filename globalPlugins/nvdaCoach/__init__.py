# NVDA Coach - Interactive Screen Reader Training
# A global plugin that provides guided, hands-on NVDA training.
# Built by Tony Gebhard, Assistive Technology Instructor.
# info@tonygebhard.me  |  https://tonygebhard.me/NVDACoach

import os
import json
import webbrowser
import globalPluginHandler
from scriptHandler import script
import ui
import gui
import wx
from logHandler import log
import tones

from .lessonRunner import LessonRunner
from .progressTracker import ProgressTracker


def _loadLessonCategories():
	"""Load all lesson category JSON files from the lessons directory."""
	lessonsDir = os.path.join(os.path.dirname(__file__), "lessons")
	categories = []
	if not os.path.isdir(lessonsDir):
		log.warning(f"NVDA Coach: Lessons directory not found: {lessonsDir}")
		return categories
	for filename in sorted(os.listdir(lessonsDir)):
		if not filename.endswith(".json"):
			continue
		filepath = os.path.join(lessonsDir, filename)
		try:
			with open(filepath, "r", encoding="utf-8") as f:
				data = json.load(f)
			categories.append(data)
		except Exception as e:
			log.error(f"NVDA Coach: Error loading {filename}: {e}")
	categories.sort(key=lambda c: c.get("order", 999))
	return categories


# ---------------------------------------------------------------------------
# CoachWindow — the persistent lesson display window
# ---------------------------------------------------------------------------

class CoachWindow(wx.Frame):
	"""Persistent window that shows the current lesson instruction and status.

	Stays open between lessons so the user always has a visible home base.
	Keyboard shortcuts (Ctrl+N, Ctrl+B, Ctrl+R, Esc×3) are handled here.
	"""

	def __init__(self, parent, plugin):
		super().__init__(
			parent,
			title="NVDA Coach",
			size=(820, 760),
			style=wx.DEFAULT_FRAME_STYLE,
		)
		self._plugin = plugin
		self._escapeCount = 0
		self._escapeTimer = None
		self._buildUI()
		self.Centre()
		# Hidden on startup; shown when NVDA+Shift+C is pressed.

	def _buildUI(self):
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)

		# Status line: "Category  ›  Lesson  ·  Step N of M"
		self._statusText = wx.StaticText(panel, label="NVDA Coach — ready")
		statusFont = self._statusText.GetFont()
		statusFont.SetPointSize(10)
		self._statusText.SetFont(statusFont)
		sizer.Add(self._statusText, 0, wx.ALL | wx.EXPAND, 8)

		sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

		# Main instruction text — large, word-wrapped, accessible via NVDA cursor.
		self._instructionText = wx.TextCtrl(
			panel,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.BORDER_NONE,
		)
		instrFont = wx.Font(
			14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
		)
		self._instructionText.SetFont(instrFont)
		self._instructionText.SetValue(
			"Welcome to NVDA Coach\n"
			"Created by Tony Gebhard, Assistive Technology Instructor\n"
			"tonygebhard.me/NVDACoach\n\n"
			"Before you begin, there is one key you should know right now. "
			"The Control key, labeled Ctrl, is in the bottom-left corner of your keyboard. "
			"Press it once and NVDA stops talking immediately, no matter what it is reading. "
			"This is the single most useful key you will ever learn as an NVDA user. "
			"You will reach for it dozens of times every day, in every program, at any moment.\n\n"
			"NVDA Coach teaches screen reader commands through short, hands-on practice sessions. "
			"Each lesson guides you through one command at a time and waits for you to try it "
			"before moving on. The program is designed for beginners who already have a basic "
			"feel for their keyboard, including letters, numbers, arrow keys, Enter, Escape, and Tab.\n\n"
			"If you are not yet confident with your keyboard, that is completely fine. "
			"NVDA has a built-in tool called Input Help. Press NVDA and the number 1 together "
			"to turn it on. While Input Help is active, pressing any key tells you what that "
			"key does without actually doing it. Press NVDA+1 again to turn it off. "
			"You can use Input Help at any time, even during a lesson.\n\n"
			"If you have an assistive technology instructor nearby, let them know you are "
			"starting NVDA Coach. They can help you find keys, adjust settings, or answer "
			"questions before you begin. If you are working on your own, that is perfectly "
			"fine too. NVDA Coach is built to guide you step by step, at your own pace.\n\n"
			"To get started, press NVDA+Shift+C to open the lesson picker and choose your "
			"first lesson. At any time you can also press Ctrl+N to move to the next lesson, "
			"Ctrl+B to go back, Ctrl+R to restart the current lesson, "
			"or press Escape three times to close this window."
		)
		sizer.Add(self._instructionText, 1, wx.ALL | wx.EXPAND, 8)

		sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

		# During-lesson shortcut reminder (compact, single line).
		lessonBar = wx.StaticText(
			panel,
			label=(
				"During a lesson:  "
				"Enter \u2014 Next Step  \u00b7  "
				"F1 Repeat  \u00b7  F2 Hint  \u00b7  F3 Skip step  \u00b7  "
				"Esc Stop lesson"
			),
		)
		lessonBar.SetFont(
			wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		)
		sizer.Add(lessonBar, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)

		# Primary action button: advance the current lesson step.
		self._nextStepBtn = wx.Button(panel, label="Next Step  (Enter)")
		self._nextStepBtn.SetToolTip(
			"Confirm you have tried the current step and move to the next one."
		)
		self._nextStepBtn.Bind(
			wx.EVT_BUTTON,
			lambda e: self._plugin._lessonRunner.advanceCurrentStep(),
		)
		sizer.Add(self._nextStepBtn, 0, wx.ALL | wx.EXPAND, 8)

		# Secondary navigation buttons — lesson-level, always visible.
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		self._prevBtn = wx.Button(panel, label="\u25c4 Back  (Ctrl+B)")
		self._repeatBtn = wx.Button(panel, label="\u21ba Restart  (Ctrl+R)")
		self._nextBtn = wx.Button(panel, label="Next Lesson \u25ba  (Ctrl+N)")
		self._prevBtn.SetToolTip("Go to the previous lesson in this category.")
		self._repeatBtn.SetToolTip("Restart the current lesson from the beginning.")
		self._nextBtn.SetToolTip("Go to the next lesson in this category.")
		self._prevBtn.Bind(wx.EVT_BUTTON, lambda e: self._plugin.prevLesson())
		self._repeatBtn.Bind(wx.EVT_BUTTON, lambda e: self._plugin.repeatLesson())
		self._nextBtn.Bind(wx.EVT_BUTTON, lambda e: self._plugin.nextLesson())
		btnSizer.Add(self._prevBtn, 1, wx.RIGHT, 4)
		btnSizer.Add(self._repeatBtn, 1, wx.LEFT | wx.RIGHT, 4)
		btnSizer.Add(self._nextBtn, 1, wx.LEFT, 4)
		sizer.Add(btnSizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

		panel.SetSizer(sizer)
		self.Bind(wx.EVT_CHAR_HOOK, self._onKey)
		self.Bind(wx.EVT_CLOSE, self._onClose)

	# ------------------------------------------------------------------
	# Public methods — called by LessonRunner and GlobalPlugin
	# ------------------------------------------------------------------

	def focusInstructionText(self):
		"""Move keyboard focus to the instruction TextCtrl so NVDA can read it.

		Calling SetFocus() on the wx.Frame itself doesn't land on any child
		control — NVDA needs focus on a real control to interact.  Always call
		this (via wx.CallAfter) instead of frame.SetFocus().
		"""
		self._instructionText.SetFocus()

	def updateDisplay(self, categoryTitle, lessonTitle, stepIdx, stepTotal, instruction):
		"""Refresh the window with the current lesson step."""
		status = (
			f"{categoryTitle}  \u203a  {lessonTitle}"
			f"  \u00b7  Step {stepIdx + 1} of {stepTotal}"
		)
		self._statusText.SetLabel(status)
		self._statusText.GetParent().Layout()
		self._instructionText.SetValue(instruction)
		# A new step means any pending escape sequence is cancelled.
		self._clearEscapeCount()
		if not self.IsShown():
			self.Show()

	def showIntroduction(self):
		"""Show the full introduction/welcome text and speak it."""
		self._statusText.SetLabel("NVDA Coach \u2014 Introduction")
		self._statusText.GetParent().Layout()
		introText = (
			"NVDA Coach\n"
			"Created by Tony Gebhard, Assistive Technology Instructor\n"
			"tonygebhard.me/NVDACoach\n\n"
			"Before you begin, there is one key you should know right now. "
			"The Control key, labeled Ctrl, is in the bottom-left corner of your keyboard. "
			"Press it once and NVDA stops talking immediately, no matter what it is reading. "
			"This is the single most useful key you will ever learn as an NVDA user. "
			"You will reach for it dozens of times every day, in every program, at any moment.\n\n"
			"NVDA Coach teaches screen reader commands through short, hands-on practice sessions. "
			"Each lesson guides you through one command at a time and waits for you to try it "
			"before moving on. The program is designed for beginners who already have a basic "
			"feel for their keyboard, including letters, numbers, arrow keys, Enter, Escape, and Tab.\n\n"
			"If you are not yet confident with your keyboard, that is completely fine. "
			"NVDA has a built-in tool called Input Help. Press NVDA and the number 1 together "
			"to turn it on. While Input Help is active, pressing any key tells you what that "
			"key does without actually doing it. Press NVDA+1 again to turn it off. "
			"You can use Input Help at any time, even during a lesson.\n\n"
			"If you have an assistive technology instructor nearby, let them know you are "
			"starting NVDA Coach. They can help you find keys, adjust settings, or answer "
			"questions before you begin. If you are working on your own, that is perfectly "
			"fine too. NVDA Coach is built to guide you step by step, at your own pace.\n\n"
			"To get started, press NVDA+Shift+C to open the lesson picker and choose your "
			"first lesson. At any time you can also press Ctrl+N to move to the next lesson, "
			"Ctrl+B to go back, Ctrl+R to restart the current lesson, "
			"or press Escape three times to close this window."
		)
		self._instructionText.SetValue(introText)
		self._clearEscapeCount()
		ui.message(
			"Welcome to NVDA Coach. "
			"Use your reading cursor or arrow keys to read this introduction. "
			"Press NVDA+Shift+C when you are ready to choose a lesson."
		)

	def showDrillProgress(self, current, total, message):
		"""Update the window during a multi-press practice drill.

		Shows a simple filled/empty block progress bar so the student can
		see at a glance how many presses they have completed.
		"""
		bar = "\u25a0" * current + "\u25a1" * (total - current)
		self._instructionText.SetValue(
			f"Practice drill \u2014 {current} of {total} complete\n"
			f"[{bar}]\n\n"
			f"{message}"
		)
		if not self.IsShown():
			self.Show()

	def showIdle(self, message=None):
		"""Show the idle/between-lesson state in the window."""
		self._statusText.SetLabel("NVDA Coach \u2014 ready")
		self._statusText.GetParent().Layout()
		self._instructionText.SetValue(
			(message or "Ready.") + "\n\n"
			"--- WHAT TO DO NEXT ---\n"
			"  Press NVDA+Shift+C to open the lesson picker and choose a lesson.\n\n"
			"--- LESSON NAVIGATION ---\n"
			"  Ctrl+N  \u2014  Move to the next lesson in this category.\n"
			"  Ctrl+B  \u2014  Go back to the previous lesson.\n"
			"  Ctrl+R  \u2014  Restart this lesson from the beginning.\n\n"
			"The Control key (Ctrl) is in the bottom-left corner of your keyboard.\n\n"
			"--- NEW TO KEYBOARD NAVIGATION? ---\n"
			"Use NVDA Input Help: press NVDA+1 to turn it on, press any key to hear "
			"what it does without anything happening, then press NVDA+1 to turn it off.\n\n"
			"--- A NOTE FOR INSTRUCTORS AND STUDENTS ---\n"
			"If an instructor is present, this is a great time to ask any questions "
			"before the next lesson. If you are working independently, keep going "
			"at your own pace. Every step forward counts."
		)

	def beginEscapeSequence(self):
		"""Arm the 3-Escape-to-close sequence after a lesson is stopped by Escape.

		stopLesson() already announced the stop via speech, so we only update
		the visual text here without generating extra audio.
		"""
		self._escapeCount = 1
		self._instructionText.SetValue(
			"Lesson stopped.\n\n"
			"Press Escape two more times to close NVDA Coach.\n"
			"Or press NVDA+Shift+C to start another lesson."
		)
		self._resetEscapeTimer()

	# ------------------------------------------------------------------
	# Key handling
	# ------------------------------------------------------------------

	def _onKey(self, evt):
		"""Handle all keyboard input for the CoachWindow.

		When a lesson is active this method drives the lesson runner directly —
		no global gesture interception is used. The student tries each command
		on their own, then comes back here and presses Enter (or clicks
		Next Step) to confirm and continue.
		"""
		key = evt.GetKeyCode()
		mods = evt.GetModifiers()
		runner = self._plugin._lessonRunner

		# ----- DURING A LESSON --------------------------------------------
		if runner.isActive:
			# Enter / Numpad Enter → advance to next step.
			# Only intercept Enter when a button is NOT focused, so that
			# Back, Restart, and Next Lesson buttons still respond to Enter
			# normally when the student has Tabbed to them.
			if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
				focused = wx.Window.FindFocus()
				if isinstance(focused, wx.Button) and focused is not self._nextStepBtn:
					evt.Skip()  # Let the focused button handle its own Enter.
					return
				runner.advanceCurrentStep()
				return

			# Space also advances (only when not on a button).
			if key == wx.WXK_SPACE:
				focused = wx.Window.FindFocus()
				if not isinstance(focused, wx.Button):
					runner.advanceCurrentStep()
					return

			if key == wx.WXK_F1:
				runner.repeatInstruction()
				return
			if key == wx.WXK_F2:
				runner.speakHint()
				return
			if key == wx.WXK_F3:
				runner.skipStep()
				return

			if key == wx.WXK_ESCAPE:
				runner.stopLesson()
				self.beginEscapeSequence()
				return

			# Ctrl+N / Ctrl+B / Ctrl+R for lesson-level navigation.
			if mods == wx.MOD_CONTROL:
				if key == ord('N'):
					self._plugin.nextLesson()
					return
				if key == ord('B'):
					self._plugin.prevLesson()
					return
				if key == ord('R'):
					self._plugin.repeatLesson()
					return

			# All other keys pass through freely so NVDA navigation works normally.
			evt.Skip()
			return

		# ----- BETWEEN LESSONS / IDLE -------------------------------------
		if key == wx.WXK_ESCAPE:
			self._handleIdleEscape()
			return

		if mods == wx.MOD_CONTROL:
			if key == ord('N'):
				self._plugin.nextLesson()
				return
			if key == ord('B'):
				self._plugin.prevLesson()
				return
			if key == ord('R'):
				self._plugin.repeatLesson()
				return

		evt.Skip()

	def _handleIdleEscape(self):
		"""Count Escape presses; three in a row hides the window."""
		if self._escapeTimer:
			try:
				self._escapeTimer.Stop()
			except Exception:
				pass
			self._escapeTimer = None

		self._escapeCount += 1

		if self._escapeCount == 1:
			msg = "Press Escape two more times to close NVDA Coach."
			ui.message(msg)
			self._instructionText.SetValue(
				msg + "\n\nOr press NVDA+Shift+C to start a lesson."
			)
			self._resetEscapeTimer()
		elif self._escapeCount == 2:
			msg = "Press Escape one more time to close NVDA Coach."
			ui.message(msg)
			self._instructionText.SetValue(msg)
			self._resetEscapeTimer()
		else:
			self._clearEscapeCount()
			self.Hide()

	def _resetEscapeTimer(self):
		self._escapeTimer = wx.CallLater(2500, self._clearEscapeCount)

	def _clearEscapeCount(self):
		self._escapeCount = 0
		if self._escapeTimer:
			try:
				self._escapeTimer.Stop()
			except Exception:
				pass
			self._escapeTimer = None

	def _onClose(self, evt):
		"""Hide instead of destroy so the window can be re-shown."""
		self.Hide()


# ---------------------------------------------------------------------------
# PracticeFrame — hands-on practice environment for individual lessons
# ---------------------------------------------------------------------------

class PracticeFrame(wx.Frame):
	"""Standalone accessible practice window.

	Opens alongside CoachWindow when a lesson benefits from a concrete
	practice environment. Each lesson type gets its own purpose-built set of
	accessible controls. The student uses Alt+Tab to switch here, tries the
	command, then presses NVDA+Shift+C to return to CoachWindow and press
	Enter to advance.

	Does NOT steal focus on open — the CoachWindow retains focus so the
	student can read the instruction first.
	"""

	# Maps lesson IDs to the builder method that populates the frame.
	# Text-navigation lessons (read_current_line, move_by_character, etc.) use
	# inline practiceText inside CoachWindow instead of an external window.
	_BUILDERS = {
		"tab_navigation": "_buildTabNavigation",
		"activate_controls": "_buildActivateControls",
		"where_am_i": "_buildWhereAmI",
	}

	SUPPORTED_LESSONS = frozenset(_BUILDERS)

	def __init__(self, parent, plugin):
		super().__init__(
			parent,
			title="NVDA Coach \u2014 Practice Area",
			size=(520, 480),
			style=wx.DEFAULT_FRAME_STYLE,
		)
		self._plugin = plugin
		self._currentLessonId = None
		# Scrollable panel so longer content is reachable with arrow keys.
		self._scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
		self._scroll.SetScrollRate(0, 20)
		self._scrollSizer = wx.BoxSizer(wx.VERTICAL)
		self._scroll.SetSizer(self._scrollSizer)
		frameSizer = wx.BoxSizer(wx.VERTICAL)
		frameSizer.Add(self._scroll, 1, wx.EXPAND)
		self.SetSizer(frameSizer)
		self.Bind(wx.EVT_CLOSE, self._onClose)

	# ------------------------------------------------------------------
	# Public API
	# ------------------------------------------------------------------

	def showForLesson(self, lessonId, lessonTitle=""):
		"""Rebuild and show the practice area for the given lesson.

		Called from GlobalPlugin when a lesson with a practice environment
		starts. Does NOT steal focus — CoachWindow keeps focus.
		"""
		if lessonId not in self.SUPPORTED_LESSONS:
			return
		self._currentLessonId = lessonId
		title = lessonTitle or "Practice Area"
		self.SetTitle(f"NVDA Coach \u2014 Practice: {title}")
		self._rebuildContent(lessonId)
		if not self.IsShown():
			self.Show()
		# Explicitly do NOT call Raise() or SetFocus() here.

	# ------------------------------------------------------------------
	# Internal rebuild
	# ------------------------------------------------------------------

	def _rebuildContent(self, lessonId):
		"""Clear and rebuild the scrollable panel for the given lesson."""
		self.Freeze()
		try:
			# Detach sizer items first (without deleting), then destroy windows.
			# Reversing the order prevents double-destroy on repeated rebuilds.
			self._scrollSizer.Clear(delete_windows=False)
			self._scroll.DestroyChildren()
			builder = getattr(self, self._BUILDERS.get(lessonId, ""), None)
			if builder:
				builder()
			self._scroll.Layout()
			# FitInside() is the correct wx.ScrolledWindow call — it updates
			# the virtual size so scrollbars appear when content overflows.
			self._scroll.FitInside()
			self._scroll.Scroll(0, 0)
		finally:
			self.Thaw()

	# ---- layout helpers --------------------------------------------------

	def _addHeading(self, text):
		lbl = wx.StaticText(self._scroll, label=text)
		f = lbl.GetFont()
		f.SetPointSize(12)
		f.SetWeight(wx.FONTWEIGHT_BOLD)
		lbl.SetFont(f)
		self._scrollSizer.Add(lbl, 0, wx.LEFT | wx.TOP | wx.RIGHT, 12)

	def _addDesc(self, text):
		lbl = wx.StaticText(self._scroll, label=text)
		lbl.Wrap(480)
		self._scrollSizer.Add(lbl, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

	def _addSep(self):
		self._scrollSizer.Add(
			wx.StaticLine(self._scroll), 0,
			wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10,
		)

	def _addTip(self):
		lbl = wx.StaticText(
			self._scroll,
			label=(
				"When you are done, press NVDA+Shift+C to return to the "
				"Coach window, then press Enter or Next Step to continue."
			),
		)
		lbl.Wrap(480)
		f = lbl.GetFont()
		f.SetStyle(wx.FONTSTYLE_ITALIC)
		lbl.SetFont(f)
		self._scrollSizer.Add(lbl, 0, wx.ALL, 10)

	# ---- Tab Navigation --------------------------------------------------

	def _buildTabNavigation(self):
		self._addHeading("Tab Navigation Practice Form")
		self._addDesc(
			"Press Tab to move forward through these controls. "
			"Press Shift+Tab to move backward. "
			"NVDA announces each control as you land on it."
		)
		self._addSep()

		fgs = wx.FlexGridSizer(rows=0, cols=2, hgap=10, vgap=6)
		fgs.AddGrowableCol(1)
		for labelText, fieldName in [
			("First name:", "First name"),
			("Last name:", "Last name"),
			("Email address:", "Email address"),
		]:
			fgs.Add(
				wx.StaticText(self._scroll, label=labelText),
				0, wx.ALIGN_CENTER_VERTICAL,
			)
			field = wx.TextCtrl(self._scroll)
			field.SetName(fieldName)
			fgs.Add(field, 0, wx.EXPAND)
		self._scrollSizer.Add(fgs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

		cb = wx.CheckBox(self._scroll, label="Subscribe to the NVDA Coach newsletter")
		self._scrollSizer.Add(cb, 0, wx.LEFT | wx.TOP, 12)

		radioBox = wx.RadioBox(
			self._scroll,
			label="Preferred contact method",
			choices=["Email", "Phone", "No preference"],
			majorDimension=3,
			style=wx.RA_SPECIFY_COLS,
		)
		self._scrollSizer.Add(radioBox, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)

		choiceSizer = wx.BoxSizer(wx.HORIZONTAL)
		choiceSizer.Add(
			wx.StaticText(self._scroll, label="Country:"),
			0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6,
		)
		choiceSizer.Add(wx.Choice(
			self._scroll,
			choices=["United States", "Canada", "United Kingdom", "Australia", "Other"],
		))
		self._scrollSizer.Add(choiceSizer, 0, wx.LEFT | wx.TOP, 12)

		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		submitBtn = wx.Button(self._scroll, label="Submit form")
		cancelBtn = wx.Button(self._scroll, label="Cancel")
		btnSizer.Add(submitBtn, 0, wx.RIGHT, 8)
		btnSizer.Add(cancelBtn)
		self._scrollSizer.Add(btnSizer, 0, wx.LEFT | wx.TOP, 12)
		self._addTip()

		submitBtn.Bind(wx.EVT_BUTTON, lambda e: ui.message(
			"Form submitted. In a real form, this would send your information.",
		))
		cancelBtn.Bind(wx.EVT_BUTTON, lambda e: ui.message(
			"Cancelled. The form was not submitted.",
		))
		cb.Bind(wx.EVT_CHECKBOX, lambda e: ui.message(
			"Subscribed to newsletter." if e.IsChecked() else "Unsubscribed.",
		))

	# ---- Activate Controls -----------------------------------------------

	def _buildActivateControls(self):
		self._addHeading("Activating Controls Practice")
		self._addDesc(
			"Tab to a control and activate it. "
			"Press Space to check or uncheck a checkbox. "
			"Press Enter to activate a button."
		)
		self._addSep()

		self._scrollSizer.Add(
			wx.StaticText(self._scroll, label="Checkboxes \u2014 press Space to toggle:"),
			0, wx.LEFT | wx.TOP, 12,
		)
		cb1 = wx.CheckBox(self._scroll, label="Enable screen reader tips")
		cb2 = wx.CheckBox(self._scroll, label="Show practice hints during lessons")
		cb3 = wx.CheckBox(self._scroll, label="Open Coach window automatically on startup")
		for cb in (cb1, cb2, cb3):
			self._scrollSizer.Add(cb, 0, wx.LEFT | wx.TOP, 8)

		self._scrollSizer.Add(
			wx.StaticText(self._scroll, label="Buttons \u2014 press Enter to activate:"),
			0, wx.LEFT | wx.TOP, 16,
		)
		playBtn = wx.Button(self._scroll, label="Play a beep sound")
		greetBtn = wx.Button(self._scroll, label="Say hello")
		tipBtn = wx.Button(self._scroll, label="Show keyboard tip")
		for btn in (playBtn, greetBtn, tipBtn):
			self._scrollSizer.Add(btn, 0, wx.LEFT | wx.TOP, 8)
		self._addTip()

		cb1.Bind(wx.EVT_CHECKBOX, lambda e: ui.message(
			"Screen reader tips enabled." if e.IsChecked()
			else "Screen reader tips disabled.",
		))
		cb2.Bind(wx.EVT_CHECKBOX, lambda e: ui.message(
			"Practice hints on." if e.IsChecked() else "Practice hints off.",
		))
		cb3.Bind(wx.EVT_CHECKBOX, lambda e: ui.message(
			"Auto-start enabled." if e.IsChecked() else "Auto-start disabled.",
		))

		def _playBeep(e):
			tones.beep(880, 120)
			ui.message("Beep! You activated the button with Enter.")

		playBtn.Bind(wx.EVT_BUTTON, _playBeep)
		greetBtn.Bind(wx.EVT_BUTTON, lambda e: ui.message(
			"Hello! You just activated a button. Great work.",
		))
		tipBtn.Bind(wx.EVT_BUTTON, lambda e: ui.message(
			"Tip: Tab moves between controls. "
			"Enter activates buttons. Space checks or unchecks checkboxes.",
		))

	# ---- Where Am I? / Focus Reporter -----------------------------------

	def _buildWhereAmI(self):
		self._addHeading("Find Your Focus \u2014 Practice Login Form")
		self._addDesc(
			"Tab around this form. When you land on a control, press "
			"NVDA+Tab to hear its name, type, and current state."
		)
		self._addSep()

		fgs = wx.FlexGridSizer(rows=0, cols=2, hgap=10, vgap=6)
		fgs.AddGrowableCol(1)
		fgs.Add(wx.StaticText(self._scroll, label="Username:"), 0, wx.ALIGN_CENTER_VERTICAL)
		userField = wx.TextCtrl(self._scroll)
		userField.SetName("Username")
		fgs.Add(userField, 0, wx.EXPAND)
		fgs.Add(wx.StaticText(self._scroll, label="Password:"), 0, wx.ALIGN_CENTER_VERTICAL)
		passField = wx.TextCtrl(self._scroll, style=wx.TE_PASSWORD)
		passField.SetName("Password")
		fgs.Add(passField, 0, wx.EXPAND)
		self._scrollSizer.Add(fgs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

		rememberCb = wx.CheckBox(self._scroll, label="Remember me on this computer")
		self._scrollSizer.Add(rememberCb, 0, wx.LEFT | wx.TOP, 12)

		for label, msg in [
			("Sign in", "Sign in activated. In a real application, this would log you in."),
			("Create account", "Create account activated. This would open a registration form."),
			("Forgot your password?", "Password reset activated. A reset link would be sent."),
		]:
			btn = wx.Button(self._scroll, label=label)
			self._scrollSizer.Add(btn, 0, wx.LEFT | wx.TOP, 8)
			btn.Bind(wx.EVT_BUTTON, lambda e, m=msg: ui.message(m))
		self._addTip()

	def _onClose(self, evt):
		self.Hide()


# ---------------------------------------------------------------------------
# LessonPickerDialog — lesson selection dialog (tree-based with submenus)
# ---------------------------------------------------------------------------

class LessonPickerDialog(wx.Dialog):
	"""Accessible tree-based dialog for choosing a lesson or resource.

	Top-level items:
	  • Introduction / About NVDA Coach
	  • One expandable node per lesson category
	  • Additional Training and Help (user guide, practice file, websites)

	Navigation: arrow keys move through the tree, Right arrow expands a
	section, Left arrow collapses it, Enter / Start button activates the
	selected item.
	"""

	def __init__(self, parent, categories, progressTracker, onLessonSelected):
		super().__init__(
			parent,
			title="NVDA Coach \u2014 Choose a Lesson",
			size=(600, 500),
		)
		self._categories = categories
		self._progress = progressTracker
		self._onLessonSelected = onLessonSelected
		# Addon root — three directories above this file.
		self._addonRoot = os.path.dirname(
			os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		)
		self._buildUI()

	def _buildUI(self):
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)

		hint = wx.StaticText(
			panel,
			label=(
				"Browse lessons and resources below. "
				"Right arrow expands a section, Left arrow collapses it. "
				"Press Enter or the Open / Start button to activate the selected item."
			),
		)
		hint.Wrap(560)
		sizer.Add(hint, flag=wx.ALL, border=10)

		self._tree = wx.TreeCtrl(
			panel,
			style=(
				wx.TR_HAS_BUTTONS
				| wx.TR_LINES_AT_ROOT
				| wx.TR_HIDE_ROOT
				| wx.TR_SINGLE
			),
		)
		root = self._tree.AddRoot("NVDA Coach")

		# ---- Introduction ------------------------------------------------
		introItem = self._tree.AppendItem(root, "Introduction / About NVDA Coach")
		self._tree.SetItemData(introItem, {"type": "intro"})

		# ---- Lesson categories -------------------------------------------
		for category in self._categories:
			catId = category.get("id", "")
			catTitle = category.get("title", "Unknown Category")
			lessons = category.get("lessons", [])
			completed, total = self._progress.getCategoryProgress(catId, len(lessons))
			catLabel = f"{catTitle}  \u2014  {completed} of {total} complete"
			catItem = self._tree.AppendItem(root, catLabel)
			self._tree.SetItemData(catItem, {"type": "category"})
			for lesson in sorted(lessons, key=lambda l: l.get("order", 999)):
				lessonId = lesson.get("id", "")
				lessonTitle = lesson.get("title", "Untitled")
				done = self._progress.isLessonComplete(catId, lessonId)
				label = lessonTitle + ("  [Done]" if done else "")
				lessonItem = self._tree.AppendItem(catItem, label)
				self._tree.SetItemData(lessonItem, {
					"type": "lesson",
					"categoryId": catId,
					"lesson": lesson,
				})

		# ---- Additional Training and Help --------------------------------
		helpItem = self._tree.AppendItem(root, "Additional Training and Help")
		self._tree.SetItemData(helpItem, {"type": "category"})

		userGuideItem = self._tree.AppendItem(helpItem, "User Guide")
		self._tree.SetItemData(userGuideItem, {
			"type": "file",
			"label": "User Guide",
			"path": os.path.join(self._addonRoot, "doc", "en", "readme.html"),
		})

		practiceItem = self._tree.AppendItem(helpItem, "Practice File")
		self._tree.SetItemData(practiceItem, {
			"type": "file",
			"label": "Practice File",
			"path": os.path.join(self._addonRoot, "doc", "en", "practice.html"),
		})

		nvdaItem = self._tree.AppendItem(
			helpItem, "Visit NV Access  \u2014  nvaccess.org"
		)
		self._tree.SetItemData(nvdaItem, {
			"type": "url",
			"url": "https://www.nvaccess.org",
		})

		devItem = self._tree.AppendItem(
			helpItem, "Visit NVDA Coach Developer  \u2014  tonygebhard.me"
		)
		self._tree.SetItemData(devItem, {
			"type": "url",
			"url": "https://tonygebhard.me/NVDACoach",
		})

		# Focus Introduction by default.
		self._tree.SelectItem(introItem)
		sizer.Add(self._tree, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		startBtn = wx.Button(panel, wx.ID_OK, label="&Open / Start")
		startBtn.SetDefault()
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, label="&Cancel")
		btnSizer.Add(startBtn, flag=wx.RIGHT, border=5)
		btnSizer.Add(cancelBtn)
		sizer.Add(btnSizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=10)

		panel.SetSizer(sizer)
		startBtn.Bind(wx.EVT_BUTTON, self._onActivate)
		cancelBtn.Bind(wx.EVT_BUTTON, self._onCancel)
		self._tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._onActivate)
		self.Bind(wx.EVT_CHAR_HOOK, self._onKeyPress)
		self._tree.SetFocus()

	def _onActivate(self, event):
		"""Handle Enter / double-click / Start button on the selected tree item."""
		item = self._tree.GetSelection()
		if not item.IsOk():
			ui.message("Please select an item first.")
			return

		data = self._tree.GetItemData(item)
		if data is None:
			return
		itemType = data.get("type")

		if itemType == "intro":
			self.Destroy()
			self._onLessonSelected("INTRO", None)

		elif itemType == "lesson":
			self.Destroy()
			self._onLessonSelected(data["categoryId"], data["lesson"])

		elif itemType == "category":
			# Toggle expand / collapse and announce how many items are inside.
			if self._tree.IsExpanded(item):
				self._tree.Collapse(item)
				count = self._tree.GetChildrenCount(item, recursively=False)
				ui.message(f"Section collapsed. {count} items hidden.")
			else:
				self._tree.Expand(item)
				count = self._tree.GetChildrenCount(item, recursively=False)
				ui.message(
					f"Section expanded. {count} items available. "
					"Use the Down arrow to browse them."
				)

		elif itemType == "file":
			path = data.get("path", "")
			label = data.get("label", "File")
			if not os.path.exists(path):
				ui.message(
					f"{label} is not available in this version of NVDA Coach."
				)
				return
			try:
				os.startfile(path)
				ui.message(f"Opening {label}.")
			except Exception as e:
				log.warning(f"NVDA Coach: Could not open {path}: {e}")
				ui.message(
					f"Could not open {label}. "
					"Please check that the add-on is installed correctly."
				)

		elif itemType == "url":
			url = data.get("url", "")
			try:
				webbrowser.open(url)
				ui.message(f"Opening {url} in your web browser.")
			except Exception as e:
				log.warning(f"NVDA Coach: Could not open URL {url}: {e}")
				ui.message(
					"Could not open the website. "
					"Please check your internet connection."
				)

	def _onCancel(self, event):
		self.Destroy()

	def _onKeyPress(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Destroy()
			return
		event.Skip()


# ---------------------------------------------------------------------------
# GlobalPlugin
# ---------------------------------------------------------------------------

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""NVDA Coach global plugin — provides interactive screen reader training."""

	def __init__(self):
		super().__init__()
		self._progressTracker = ProgressTracker()
		self._lessonRunner = LessonRunner(self._progressTracker)
		self._categories = _loadLessonCategories()
		# Lesson navigation state (set when a lesson is selected from the picker).
		self._currentCategoryId = None
		self._currentCategoryTitle = ""
		self._currentCategoryLessons = []
		self._currentLessonIndex = 0
		# Create the persistent display window (hidden until first use).
		self._coachWindow = CoachWindow(gui.mainFrame, self)
		self._lessonRunner.coachWindow = self._coachWindow
		# Create the practice window (hidden; shown automatically per lesson).
		self._practiceFrame = PracticeFrame(gui.mainFrame, self)
		log.info(f"NVDA Coach loaded. {len(self._categories)} lesson categories found.")

	def terminate(self):
		self._lessonRunner.cleanup()
		for win in (self._coachWindow, self._practiceFrame):
			try:
				win.Destroy()
			except Exception:
				pass

	@script(
		description=_("Show NVDA Coach window, or open the lesson picker"),
		gesture="kb:NVDA+shift+c",
		category="NVDA Coach",
	)
	def script_toggleCoach(self, gesture):
		"""Show and focus the CoachWindow.

		During a lesson: brings CoachWindow to the foreground so the student
		can press Enter to advance after trying a command in another window.
		Between lessons: opens the lesson picker.
		"""
		if self._lessonRunner.isActive:
			# Bring CoachWindow to focus — student tried the command and is
			# coming back here to confirm and advance.
			if not self._coachWindow.IsShown():
				self._coachWindow.Show()
			# Raise the window, then use wx.CallAfter to focus a specific child
			# control once the raise is fully processed.  Calling SetFocus() on
			# the wx.Frame itself leaves NVDA with no readable control target.
			self._coachWindow.Raise()
			wx.CallAfter(self._coachWindow.focusInstructionText)
			ui.message(
				"NVDA Coach. "
				"Press Enter or Next Step to continue, "
				"or Escape to stop the lesson."
			)
			return
		if not self._categories:
			ui.message(
				"NVDA Coach: No lesson files found. "
				"Please check that the lessons folder is in the add-on directory."
			)
			return
		# Ensure the coach window is visible before showing the picker.
		if not self._coachWindow.IsShown():
			self._coachWindow.Show()
		self._coachWindow.Raise()
		self._showLessonPicker()

	def _showLessonPicker(self):
		"""Show the lesson selection dialog and wire up the selection callback."""
		# Reload progress to get the latest completed status.
		self._progressTracker = ProgressTracker()
		self._lessonRunner = LessonRunner(self._progressTracker)
		self._lessonRunner.coachWindow = self._coachWindow
		# practiceFrame is managed by GlobalPlugin; no need to set on runner.

		def onLessonSelected(categoryId, lesson):
			if categoryId == "INTRO":
				self._coachWindow.Show()
				self._coachWindow.Raise()
				self._coachWindow.showIntroduction()
				return
			category = next(
				(c for c in self._categories if c.get("id") == categoryId), None
			)
			categoryTitle = category.get("title", "") if category else ""
			sortedLessons = sorted(
				(category or {}).get("lessons", []),
				key=lambda l: l.get("order", 999),
			)
			# Persist navigation state for Ctrl+N / Ctrl+B / Ctrl+R.
			self._currentCategoryId = categoryId
			self._currentCategoryTitle = categoryTitle
			self._currentCategoryLessons = sortedLessons
			self._currentLessonIndex = next(
				(
					i for i, l in enumerate(sortedLessons)
					if l.get("id") == lesson.get("id")
				),
				0,
			)
			# Open practice environment if this lesson has one.
			lessonId = lesson.get("id", "")
			if lessonId in PracticeFrame.SUPPORTED_LESSONS:
				self._practiceFrame.showForLesson(lessonId, lesson.get("title", ""))

			if category and category.get("practicePage"):
				# Open the practice HTML page in the browser.
				addonRoot = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
				practiceFile = os.path.join(addonRoot, "doc", "en", "practice.html")
				try:
					os.startfile(practiceFile)
				except Exception as e:
					log.warning(f"NVDA Coach: Could not open practice page: {e}")
				# Show window but don't steal focus — let the browser come to front.
				self._coachWindow.Show()
				wx.CallLater(
					1500,
					self._lessonRunner.startLesson,
					categoryId,
					lesson,
					categoryTitle,
				)
			else:
				self._coachWindow.Show()
				self._coachWindow.Raise()
				wx.CallLater(
					300,
					self._lessonRunner.startLesson,
					categoryId,
					lesson,
					categoryTitle,
				)

		gui.mainFrame.prePopup()
		dialog = LessonPickerDialog(
			gui.mainFrame,
			self._categories,
			self._progressTracker,
			onLessonSelected,
		)
		dialog.Show()
		gui.mainFrame.postPopup()

	# ------------------------------------------------------------------
	# Lesson navigation — called from CoachWindow keyboard handler
	# ------------------------------------------------------------------

	def nextLesson(self):
		"""Advance to the next lesson in the current category (Ctrl+N)."""
		if not self._currentCategoryLessons:
			ui.message("No active category. Press NVDA+Shift+C to choose a lesson.")
			return
		if self._currentLessonIndex >= len(self._currentCategoryLessons) - 1:
			ui.message(
				"You are on the last lesson in this category. "
				"Press NVDA+Shift+C to open the lesson picker "
				"and continue to the next chapter."
			)
			return
		if self._lessonRunner.isActive:
			self._lessonRunner.stopLesson(announce=False)
		self._currentLessonIndex += 1
		lesson = self._currentCategoryLessons[self._currentLessonIndex]
		lessonId = lesson.get("id", "")
		if lessonId in PracticeFrame.SUPPORTED_LESSONS:
			self._practiceFrame.showForLesson(lessonId, lesson.get("title", ""))
		ui.message(f"Moving to: {lesson.get('title', 'next lesson')}.")
		wx.CallLater(
			1000,
			self._lessonRunner.startLesson,
			self._currentCategoryId,
			lesson,
			self._currentCategoryTitle,
		)

	def prevLesson(self):
		"""Go back to the previous lesson in the current category (Ctrl+B)."""
		if not self._currentCategoryLessons:
			ui.message("No active category. Press NVDA+Shift+C to choose a lesson.")
			return
		if self._currentLessonIndex <= 0:
			ui.message("You are on the first lesson in this category.")
			return
		if self._lessonRunner.isActive:
			self._lessonRunner.stopLesson(announce=False)
		self._currentLessonIndex -= 1
		lesson = self._currentCategoryLessons[self._currentLessonIndex]
		lessonId = lesson.get("id", "")
		if lessonId in PracticeFrame.SUPPORTED_LESSONS:
			self._practiceFrame.showForLesson(lessonId, lesson.get("title", ""))
		ui.message(f"Going back to: {lesson.get('title', 'previous lesson')}.")
		wx.CallLater(
			1000,
			self._lessonRunner.startLesson,
			self._currentCategoryId,
			lesson,
			self._currentCategoryTitle,
		)

	def repeatLesson(self):
		"""Restart the current lesson from the beginning (Ctrl+R)."""
		if not self._currentCategoryLessons:
			ui.message("No active category. Press NVDA+Shift+C to choose a lesson.")
			return
		if self._lessonRunner.isActive:
			self._lessonRunner.stopLesson(announce=False)
		lesson = self._currentCategoryLessons[self._currentLessonIndex]
		lessonId = lesson.get("id", "")
		if lessonId in PracticeFrame.SUPPORTED_LESSONS:
			self._practiceFrame.showForLesson(lessonId, lesson.get("title", ""))
		ui.message("Restarting lesson.")
		wx.CallLater(
			600,
			self._lessonRunner.startLesson,
			self._currentCategoryId,
			lesson,
			self._currentCategoryTitle,
		)
