# NVDA Coach - Interactive Screen Reader Training
# A global plugin that provides guided, hands-on NVDA training.
# Built by Tony Gebhard, Assistive Technology Instructor.
# info@tonygebhard.me  |  https://tonygebhard.me/NVDACoach

import os
import json
import ctypes
import ctypes.wintypes
import webbrowser
import globalPluginHandler
from scriptHandler import script
import ui
import gui
import gui.settingsDialogs
import wx
from logHandler import log
import tones
import config
import languageHandler
import addonHandler
addonHandler.initTranslation()

from .lessonRunner import LessonRunner
from .progressTracker import ProgressTracker

# Register NVDA Coach config spec so settings persist across sessions.
config.conf.spec["nvdaCoach"] = {
	"playSounds": "boolean(default=True)",
	"userName": "string(default='')",
	"instructorName": "string(default='')",
	"trainingCenter": "string(default='')",
}


# ---------------------------------------------------------------------------
# NVDA Settings panel
# ---------------------------------------------------------------------------

class NvdaCoachSettingsPanel(gui.settingsDialogs.SettingsPanel):
	"""NVDA Coach settings panel — appears in NVDA Preferences > NVDA Coach."""

	title = _("NVDA Coach")

	def makeSettings(self, settingsSizer):
		self._playSoundsCheckbox = wx.CheckBox(
			self,
			label=_("Play sounds during lessons (correct/incorrect/completion chimes)"),
		)
		self._playSoundsCheckbox.SetValue(config.conf["nvdaCoach"]["playSounds"])
		settingsSizer.Add(self._playSoundsCheckbox)

	def onSave(self):
		config.conf["nvdaCoach"]["playSounds"] = self._playSoundsCheckbox.GetValue()


# ---------------------------------------------------------------------------
# PersonalizationDialog — set user and instructor names (F7)
# ---------------------------------------------------------------------------

class PersonalizationDialog(wx.Dialog):
	"""Dialog for entering the student's name and instructor's name."""

	def __init__(self, parent):
		super().__init__(
			parent,
			title=_("NVDA Coach — Your Profile"),
			size=(460, 250),
		)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)

		fgs = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=8)
		fgs.AddGrowableCol(1)
		fgs.Add(
			wx.StaticText(panel, label=_("Your name (optional):")),
			0, wx.ALIGN_CENTER_VERTICAL,
		)
		self._nameField = wx.TextCtrl(
			panel,
			value=config.conf["nvdaCoach"].get("userName", ""),
		)
		fgs.Add(self._nameField, 1, wx.EXPAND)
		fgs.Add(
			wx.StaticText(panel, label=_("Your instructor's name (optional):")),
			0, wx.ALIGN_CENTER_VERTICAL,
		)
		self._instrField = wx.TextCtrl(
			panel,
			value=config.conf["nvdaCoach"].get("instructorName", ""),
		)
		fgs.Add(self._instrField, 1, wx.EXPAND)
		fgs.Add(
			wx.StaticText(panel, label=_("Training center or program (optional):")),
			0, wx.ALIGN_CENTER_VERTICAL,
		)
		self._centerField = wx.TextCtrl(
			panel,
			value=config.conf["nvdaCoach"].get("trainingCenter", ""),
		)
		fgs.Add(self._centerField, 1, wx.EXPAND)
		sizer.Add(fgs, 0, wx.ALL | wx.EXPAND, 12)

		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		saveBtn = wx.Button(panel, wx.ID_OK, label=_("&Save"))
		saveBtn.SetDefault()
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, label=_("&Cancel"))
		btnSizer.Add(saveBtn, flag=wx.RIGHT, border=5)
		btnSizer.Add(cancelBtn)
		sizer.Add(btnSizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

		panel.SetSizer(sizer)
		saveBtn.Bind(wx.EVT_BUTTON, self._onSave)
		cancelBtn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
		self.Bind(wx.EVT_CHAR_HOOK, self._onKey)
		self._nameField.SetFocus()

	def _onSave(self, evt):
		name = self._nameField.GetValue().strip()
		instructor = self._instrField.GetValue().strip()
		center = self._centerField.GetValue().strip()
		config.conf["nvdaCoach"]["userName"] = name
		config.conf["nvdaCoach"]["instructorName"] = instructor
		config.conf["nvdaCoach"]["trainingCenter"] = center
		self.EndModal(wx.ID_OK)
		if name:
			ui.message(_("Hello, {name}!").format(name=name))
		else:
			ui.message(_("Profile saved."))

	def _onKey(self, evt):
		if evt.GetKeyCode() == wx.WXK_ESCAPE:
			self.EndModal(wx.ID_CANCEL)
			return
		evt.Skip()


# ---------------------------------------------------------------------------
# CertificateDialog — shown after all lessons are complete
# ---------------------------------------------------------------------------

class CertificateDialog(wx.Dialog):
	"""Congratulations dialog shown when the student finishes every lesson."""

	def __init__(self, parent, name=""):
		super().__init__(
			parent,
			title=_("NVDA Coach — Certificate of Completion"),
			size=(520, 220),
		)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)

		if name:
			msg = _(
				"Congratulations, {name}! You have completed every lesson in NVDA Coach. "
				"Your certificate of completion has been saved to your Downloads folder "
				"and opened in your web browser."
			).format(name=name)
		else:
			msg = _(
				"Congratulations! You have completed every lesson in NVDA Coach. "
				"Your certificate of completion has been saved to your Downloads folder "
				"and opened in your web browser."
			)

		lbl = wx.StaticText(panel, label=msg)
		lbl.Wrap(480)
		sizer.Add(lbl, 0, wx.ALL, 16)

		okBtn = wx.Button(panel, wx.ID_OK, label=_("&OK"))
		okBtn.SetDefault()
		sizer.Add(okBtn, 0, wx.ALL | wx.ALIGN_CENTER, 10)

		panel.SetSizer(sizer)
		okBtn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
		self.Bind(wx.EVT_CHAR_HOOK, self._onKey)

	def _onKey(self, evt):
		if evt.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			self.EndModal(wx.ID_OK)
			return
		evt.Skip()


def _loadLessonCategories():
	"""Load all lesson category JSON files from the lessons directory.

	Looks for lessons in a language-specific subfolder first (e.g. lessons/fr/
	for French, lessons/pt_BR/ for Brazilian Portuguese), then the base language
	code alone (e.g. lessons/pt/ from pt_BR), then falls back to lessons/en/.
	This allows translators to contribute localized lesson sets by dropping a
	new language subfolder into the lessons/ directory.
	"""
	baseDir = os.path.join(os.path.dirname(__file__), "lessons")

	# Build a prioritized list of candidate directories.
	lang = languageHandler.getLanguage()  # e.g. "fr_BE", "pt_BR", "en", "Windows"
	candidates = []
	if lang and lang != "Windows":
		candidates.append(os.path.join(baseDir, lang))        # e.g. lessons/fr_BE/
		baseLang = lang.split("_")[0]
		if baseLang != lang:
			candidates.append(os.path.join(baseDir, baseLang))  # e.g. lessons/fr/
	candidates.append(os.path.join(baseDir, "en"))             # Always-present fallback.

	lessonsDir = None
	for candidate in candidates:
		if os.path.isdir(candidate):
			lessonsDir = candidate
			break

	categories = []
	if not lessonsDir:
		log.warning(
			f"NVDA Coach: No lessons directory found for language '{lang}'. "
			f"Checked: {candidates}"
		)
		return categories

	log.info(f"NVDA Coach: Loading lessons from {lessonsDir}")
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


def _localizedDocPath(filename):
	"""Return the path to a localized doc file, falling back to doc/en/.

	Mirrors the language-resolution logic in _loadLessonCategories():
	tries doc/{lang}/, then doc/{baseLang}/, then doc/en/.
	"""
	addonRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	lang = languageHandler.getLanguage()
	candidates = []
	if lang and lang != "Windows":
		candidates.append(os.path.join(addonRoot, "doc", lang, filename))
		baseLang = lang.split("_")[0]
		if baseLang != lang:
			candidates.append(os.path.join(addonRoot, "doc", baseLang, filename))
	candidates.append(os.path.join(addonRoot, "doc", "en", filename))
	for candidate in candidates:
		if os.path.isfile(candidate):
			return candidate
	return candidates[-1]  # Return fallback path even if not present.


def _generateCertificate():
	"""Generate a completion certificate HTML file, save to Downloads, and open it.

	Returns the path to the saved file.
	"""
	import datetime
	name = config.conf["nvdaCoach"].get("userName", "").strip() or _("Student")
	instructor = config.conf["nvdaCoach"].get("instructorName", "").strip()
	center = config.conf["nvdaCoach"].get("trainingCenter", "").strip()
	date_str = datetime.date.today().strftime("%B %d, %Y")
	lang = languageHandler.getLanguage() or "en"

	instructor_html = (
		"<p class='instructor'><strong>{label}</strong> {instructor}</p>".format(
			label=_("Instructor:"),
			instructor=instructor,
		)
		if instructor else ""
	)
	center_html = (
		"<p class='center'><strong>{label}</strong> {center}</p>".format(
			label=_("Training Center / Program:"),
			center=center,
		)
		if center else ""
	)

	# Translators: heartfelt closing message on the completion certificate
	heartfelt = _(
		"Your dedication and persistence have brought you to this moment. "
		"The skills you have learned in NVDA Coach will serve you every day — "
		"at work, at home, and everywhere in between. "
		"Every expert was once a beginner, and you have proven that with patience "
		"and practice, anything is possible. "
		"Well done, and welcome to a world of greater independence."
	)

	# Translators: title of the completion certificate document
	title_text = _("Certificate of Completion")
	addon_name = _("NVDA Coach")
	# Translators: opening line of certificate, followed by the student's name
	certifies = _("This certifies that")
	# Translators: line below student name on certificate
	completed = _("has successfully completed all lessons in")
	# Translators: label for the completion date on the certificate
	date_label = _("Date of Completion")
	# Translators: label for the signer's title on the certificate
	author_title = _("Assistive Technology Instructor")

	html = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <title>{title} \u2014 {addon_name}</title>
  <style>
    body {{ font-family: Georgia, serif; background: #f5f0e8; margin: 0; padding: 40px; }}
    .certificate {{
      background: white; border: 8px double #4a6741; max-width: 760px;
      margin: 0 auto; padding: 60px; text-align: center;
      box-shadow: 0 4px 20px rgba(0,0,0,.15);
    }}
    h1 {{ font-size: 2.2em; color: #4a6741; margin-bottom: .3em; letter-spacing: 2px; }}
    .certifies {{ font-size: 1.1em; color: #555; margin: .8em 0 .3em; }}
    .student-name {{ font-size: 2.4em; color: #222; font-style: italic; margin: .2em 0 .6em; }}
    .completed {{ font-size: 1.1em; color: #555; margin-bottom: .3em; }}
    .program {{ font-size: 1.5em; color: #4a6741; font-weight: bold; margin-bottom: 1.2em; }}
    hr {{ border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }}
    .date, .instructor, .center {{ font-size: 1em; color: #444; margin: .4em 0; }}
    .heartfelt {{ font-size: 1em; color: #333; line-height: 1.8; margin: 1.5em 0; font-style: italic; }}
    .sig-name {{ font-size: 1.2em; font-weight: bold; color: #222; margin-top: 1.5em; }}
    .sig-title {{ font-size: 1em; color: #444; margin: .2em 0; }}
  </style>
</head>
<body>
  <div class="certificate">
    <h1>{title}</h1>
    <p class="certifies">{certifies}</p>
    <p class="student-name">{name}</p>
    <p class="completed">{completed}</p>
    <p class="program">{addon_name}</p>
    <hr>
    <p class="date"><strong>{date_label}:</strong> {date_str}</p>
    {instructor_html}
    {center_html}
    <p class="heartfelt">{heartfelt}</p>
    <hr>
    <p class="sig-name">Tony Gebhard</p>
    <p class="sig-title">{author_title}</p>
  </div>
</body>
</html>""".format(
		lang=lang,
		title=title_text,
		addon_name=addon_name,
		certifies=certifies,
		name=name,
		completed=completed,
		date_label=date_label,
		date_str=date_str,
		instructor_html=instructor_html,
		center_html=center_html,
		heartfelt=heartfelt,
		author_title=author_title,
	)

	safe_name = "".join(
		c for c in name if c.isalnum() or c in (" ", "-", "_")
	).strip() or _("Student")
	filename = _("NVDA Coach - {name} certificate of completion.html").format(name=safe_name)
	downloads = os.path.join(os.path.expanduser("~"), "Downloads")
	filepath = os.path.join(downloads, filename)
	with open(filepath, "w", encoding="utf-8") as f:
		f.write(html)
	os.startfile(filepath)
	return filepath


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
			title=_("NVDA Coach"),
			size=(820, 760),
			style=wx.DEFAULT_FRAME_STYLE,
		)
		self._plugin = plugin
		self._escapeCount = 0
		self._escapeTimer = None
		self._f4Armed = False
		self._f4Timer = None
		self._f5Armed = False
		self._f5Timer = None
		self._buildUI()
		self.Centre()
		# Hidden on startup; shown when NVDA+Shift+C is pressed.

	def _buildUI(self):
		panel = wx.Panel(self)
		self._panel = panel
		sizer = wx.BoxSizer(wx.VERTICAL)

		# Status line: "Category  ›  Lesson  ·  Step N of M"
		self._statusText = wx.StaticText(panel, label=_("NVDA Coach — ready"))
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
		self._instructionText.SetValue(_(
			"Welcome to NVDA Coach\n"
			"Created by Tony Gebhard, Assistive Technology Instructor\n"
			"github.com/tonygeb23/nvdacoach\n\n"
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
			"--- KEYS AVAILABLE DURING EVERY LESSON ---\n"
			"  Enter  —  Confirm you have tried the step and move to the next one.\n"
			"  F1  —  Repeat the current instruction.\n"
			"  F2  —  Hear a hint. Press again for more hints.\n"
			"  F3  —  Skip the current step.\n"
			"  Escape  —  Stop the lesson. Press three times to close NVDA Coach.\n\n"
			"--- KEYS AVAILABLE ANY TIME IN THIS WINDOW ---\n"
			"  F4  —  Open help documentation (press twice within 5 seconds).\n"
			"  F5  —  Send feedback by email (press twice within 5 seconds).\n"
			"  F6  —  Toggle lesson sounds on or off.\n"
			"  F7  —  Open your profile (name, instructor, training center).\n\n"
			"--- LESSON NAVIGATION ---\n"
			"  Ctrl+N  —  Next lesson  ·  Ctrl+B  —  Previous  ·  Ctrl+R  —  Restart\n\n"
			"When you are ready to begin, press Tab to find the Start Course button below "
			"and press Enter or Space to start the first lesson. "
			"You can also press NVDA+Shift+C to open the lesson picker and choose any lesson directly."
		))
		sizer.Add(self._instructionText, 1, wx.ALL | wx.EXPAND, 8)

		sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

		# During-lesson shortcut reminder (two compact lines).
		smallFont = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		lessonBar = wx.StaticText(
			panel,
			label=_(
				"During a lesson:  "
				"Enter — Next Step  ·  "
				"F1 Repeat  ·  F2 Hint  ·  F3 Skip  ·  "
				"Esc Stop"
			),
		)
		lessonBar.SetFont(smallFont)
		sizer.Add(lessonBar, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		fKeyBar = wx.StaticText(
			panel,
			label=_(
				"F4 Help  ·  F5 Feedback  ·  F6 Sounds  ·  F7 Profile"
			),
		)
		fKeyBar.SetFont(smallFont)
		sizer.Add(fKeyBar, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

		# Primary action button: advance the current lesson step.
		self._nextStepBtn = wx.Button(panel, label=_("Next Step  (Enter)"))
		self._nextStepBtn.SetToolTip(
			_("Confirm you have tried the current step and move to the next one.")
		)
		self._nextStepBtn.Bind(
			wx.EVT_BUTTON,
			lambda e: self._plugin._lessonRunner.advanceCurrentStep(),
		)
		sizer.Add(self._nextStepBtn, 0, wx.ALL | wx.EXPAND, 8)

		# Start Course button — shown only on the introduction screen.
		self._startCourseBtn = wx.Button(panel, label=_("Start Course  (Enter)"))
		self._startCourseBtn.SetToolTip(
			_("Begin the first lesson of the Getting Started chapter.")
		)
		self._startCourseBtn.Bind(
			wx.EVT_BUTTON,
			lambda e: self._plugin.startFirstLesson(),
		)
		sizer.Add(self._startCourseBtn, 0, wx.ALL | wx.EXPAND, 8)
		self._startCourseBtn.Hide()

		# Secondary navigation buttons — lesson-level, always visible.
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		self._prevBtn = wx.Button(panel, label=_("◄ Back  (Ctrl+B)"))
		self._repeatBtn = wx.Button(panel, label=_("↺ Restart  (Ctrl+R)"))
		self._nextBtn = wx.Button(panel, label=_("Next Lesson ►  (Ctrl+N)"))
		self._prevBtn.SetToolTip(_("Go to the previous lesson in this category."))
		self._repeatBtn.SetToolTip(_("Restart the current lesson from the beginning."))
		self._nextBtn.SetToolTip(_("Go to the next lesson in this category."))
		self._prevBtn.Bind(wx.EVT_BUTTON, lambda e: self._plugin.prevLesson())
		self._repeatBtn.Bind(wx.EVT_BUTTON, lambda e: self._plugin.repeatLesson())
		self._nextBtn.Bind(wx.EVT_BUTTON, lambda e: self._plugin.nextLesson())
		btnSizer.Add(self._prevBtn, 1, wx.RIGHT, 4)
		btnSizer.Add(self._repeatBtn, 1, wx.LEFT | wx.RIGHT, 4)
		btnSizer.Add(self._nextBtn, 1, wx.LEFT, 4)
		sizer.Add(btnSizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

		# Certificate button — hidden until all lessons are complete.
		self._certBtn = wx.Button(
			panel,
			label=_("Export Certificate of Completion"),
		)
		self._certBtn.SetToolTip(_(
			"You have completed every lesson in NVDA Coach. "
			"Click to save your certificate of completion to your Downloads folder."
		))
		self._certBtn.Bind(
			wx.EVT_BUTTON,
			lambda e: self._plugin._showCompletionCertificate(),
		)
		self._certBtn.Hide()
		sizer.Add(self._certBtn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

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
			# Translators: status bar showing step position within a lesson
			f"  ·  " + _("Step {stepNum} of {stepTotal}").format(stepNum=stepIdx + 1, stepTotal=stepTotal)
		)
		self._statusText.SetLabel(status)
		self._statusText.GetParent().Layout()
		self._instructionText.SetValue(instruction)
		self._startCourseBtn.Hide()
		self._nextStepBtn.Show()
		self._panel.Layout()
		# A new step means any pending escape sequence is cancelled.
		self._clearEscapeCount()
		if not self.IsShown():
			self.Show()

	def showCertificateButton(self, silent=False):
		"""Reveal the certificate export button once all lessons are complete.

		Pass silent=True when called on startup so NVDA does not announce
		course completion every time the add-on loads.
		"""
		if not self._certBtn.IsShown():
			self._certBtn.Show()
			self._panel.Layout()
		if not silent:
			ui.message(_(
				"Congratulations — you have completed every lesson in NVDA Coach! "
				"Tab to the Export Certificate of Completion button to save your certificate."
			))

	def showIntroduction(self):
		"""Show the full introduction/welcome text and speak it."""
		self._statusText.SetLabel(_("NVDA Coach — Introduction"))
		self._statusText.GetParent().Layout()
		name = config.conf["nvdaCoach"].get("userName", "").strip()
		instructor = config.conf["nvdaCoach"].get("instructorName", "").strip()
		if name:
			welcome_heading = _("Welcome, {name}, to NVDA Coach").format(name=name)
			spoken_welcome = _(
				"Welcome, {name}, to NVDA Coach. "
				"Use your reading cursor or arrow keys to read this introduction. "
				"When you are ready, press Tab to reach the Start Course button and press Enter to begin."
			).format(name=name)
		else:
			welcome_heading = _("Welcome to NVDA Coach")
			spoken_welcome = _(
				"Welcome to NVDA Coach. "
				"Use your reading cursor or arrow keys to read this introduction. "
				"When you are ready, press Tab to reach the Start Course button and press Enter to begin."
			)
		if instructor:
			instructor_line = _(
				"Your instructor today is {instructor}. "
				"Let them know you are starting — they can help you find keys, "
				"adjust settings, or answer questions before you begin."
			).format(instructor=instructor)
		else:
			instructor_line = _(
				"If you have an assistive technology instructor nearby, let them know you are "
				"starting NVDA Coach. They can help you find keys, adjust settings, or answer "
				"questions before you begin. If you are working on your own, that is perfectly "
				"fine too. NVDA Coach is built to guide you step by step, at your own pace."
			)
		introText = (
			welcome_heading + "\n"
			+ _("Created by Tony Gebhard, Assistive Technology Instructor") + "\n"
			"github.com/tonygeb23/nvdacoach\n\n"
			+ _(
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
			)
			+ instructor_line + "\n\n"
			+ _(
				"--- KEYS AVAILABLE DURING EVERY LESSON ---\n"
				"These function keys work at any time while a lesson is open:\n\n"
				"  Enter  —  Confirm you have tried the step and move to the next one.\n"
				"  F1  —  Repeat the current instruction. Use this whenever you want "
				"NVDA to read the step again.\n"
				"  F2  —  Hear a hint. If you are not sure what to do, press F2 for "
				"a helpful suggestion. Press it again for additional hints.\n"
				"  F3  —  Skip the current step and move on. Use this if you cannot "
				"complete a step right now and want to continue.\n"
				"  Escape  —  Stop the lesson. Press Escape three times to close NVDA Coach.\n\n"
				"--- KEYS AVAILABLE ANY TIME IN THIS WINDOW ---\n"
				"These keys work whether a lesson is running or not:\n\n"
				"  F4  —  Open the NVDA Coach help documentation in your web browser. "
				"Press F4 once to arm it, then press F4 again within five seconds to open.\n"
				"  F5  —  Send feedback to the developer by email. "
				"Press F5 once to arm it, then press F5 again within five seconds to open.\n"
				"  F6  —  Toggle lesson sounds on or off. "
				"Press once to silence sounds, press again to restore them.\n"
				"  F7  —  Open your profile. Set your name, your instructor's name, "
				"and your training center. This information personalizes your lessons "
				"and appears on your certificate of completion.\n\n"
				"--- LESSON NAVIGATION ---\n"
				"  Ctrl+N  —  Move to the next lesson in the current chapter.\n"
				"  Ctrl+B  —  Go back to the previous lesson.\n"
				"  Ctrl+R  —  Restart the current lesson from the beginning.\n\n"
			)
			+ _(
				"When you are ready to begin, press Tab to find the Start Course button below "
				"and press Enter or Space to start the first lesson. "
				"You can also press NVDA+Shift+C to open the lesson picker and choose any lesson directly."
			)
		)
		self._instructionText.SetValue(introText)
		self._startCourseBtn.Show()
		self._nextStepBtn.Hide()
		self._panel.Layout()
		self._clearEscapeCount()
		ui.message(spoken_welcome)

	def showDrillProgress(self, current, total, message):
		"""Update the window during a multi-press practice drill.

		Shows a simple filled/empty block progress bar so the student can
		see at a glance how many presses they have completed.
		"""
		bar = "\u25a0" * current + "\u25a1" * (total - current)
		self._instructionText.SetValue(
			_("Practice drill — {current} of {total} complete").format(current=current, total=total) + "\n"
			f"[{bar}]\n\n"
			f"{message}"
		)
		if not self.IsShown():
			self.Show()

	def showIdle(self, message=None):
		"""Show the idle/between-lesson state in the window."""
		name = config.conf["nvdaCoach"].get("userName", "").strip()
		default_msg = _("Ready, {name}.").format(name=name) if name else _("Ready.")
		self._statusText.SetLabel(_("NVDA Coach — ready"))
		self._statusText.GetParent().Layout()
		self._startCourseBtn.Hide()
		self._nextStepBtn.Show()
		self._panel.Layout()
		self._instructionText.SetValue(
			(message or default_msg) + "\n\n"
			+ _(
				"--- WHAT TO DO NEXT ---\n"
				"  Press NVDA+Shift+C to open the lesson picker and choose a lesson.\n\n"
				"--- LESSON NAVIGATION ---\n"
				"  Ctrl+N  —  Move to the next lesson in this category.\n"
				"  Ctrl+B  —  Go back to the previous lesson.\n"
				"  Ctrl+R  —  Restart this lesson from the beginning.\n\n"
				"The Control key (Ctrl) is in the bottom-left corner of your keyboard.\n\n"
				"--- NEW TO KEYBOARD NAVIGATION? ---\n"
				"Use NVDA Input Help: press NVDA+1 to turn it on, press any key to hear "
				"what it does without anything happening, then press NVDA+1 to turn it off.\n\n"
				"--- A NOTE FOR INSTRUCTORS AND STUDENTS ---\n"
				"If an instructor is present, this is a great time to ask any questions "
				"before the next lesson. If you are working independently, keep going "
				"at your own pace. Every step forward counts.\n\n"
				"--- QUICK KEYS (available any time in this window) ---\n"
				"  F4 — Open help documentation\n"
				"  F5 — Send feedback to the developer\n"
				"  F6 — Toggle lesson sounds on or off\n"
				"  F7 — Set your name and instructor's name"
			)
		)

	def showBrowseModeCompletion(self):
		"""Show the chapter-completion congratulations screen for Browse Mode."""
		name = config.conf["nvdaCoach"].get("userName", "").strip()
		congrats_heading = (
			_("Congratulations, {name} — Browse Mode and Web Navigation Complete!").format(name=name)
			if name else
			_("Congratulations — Browse Mode and Web Navigation Complete!")
		)
		congrats_spoken = (
			_("Congratulations, {name}! You have completed Browse Mode and Web Navigation, "
			"Chapter 4 of NVDA Coach. "
			"The practice page in your browser can now be closed. "
			"Press NVDA+Shift+C to continue to additional training resources.").format(name=name)
			if name else
			_("Congratulations! You have completed Browse Mode and Web Navigation, "
			"Chapter 4 of NVDA Coach. "
			"The practice page in your browser can now be closed. "
			"Press NVDA+Shift+C to continue to additional training resources.")
		)
		self._statusText.SetLabel(_("NVDA Coach — Chapter 4 Complete!"))
		self._statusText.GetParent().Layout()
		self._startCourseBtn.Hide()
		self._nextStepBtn.Hide()
		self._panel.Layout()
		self._instructionText.SetValue(
			congrats_heading + "\n\n"
			+ _(
				"You have finished all lessons in Chapter 4. "
				"You now know how to navigate any web page using NVDA's browse mode.\n\n"
				"Commands you have mastered:\n"
				"  H — Jump between headings\n"
				"  1 through 6 — Jump to heading levels\n"
				"  K — Jump between links\n"
				"  F, E, B — Navigate form fields and buttons\n"
				"  D — Jump between landmarks\n"
				"  L — Jump between lists\n"
				"  NVDA+Space — Toggle browse mode and focus mode\n"
				"  NVDA+F7 — Open the Elements List\n\n"
				"The practice page in your browser can now be closed.\n\n"
				"What to do next:\n"
				"  Press NVDA+Shift+C to open the lesson picker.\n"
				"  Choose Additional Training and Help for more resources.\n"
				"  Or press Ctrl+R to repeat any lesson in this chapter."
			)
		)
		self._clearEscapeCount()
		ui.message(congrats_spoken)

	def showFinalCompletion(self):
		"""Show the full-course heartfelt congratulations screen when every lesson is done."""
		name = config.conf["nvdaCoach"].get("userName", "").strip()
		instructor = config.conf["nvdaCoach"].get("instructorName", "").strip()
		trainingCenter = config.conf["nvdaCoach"].get("trainingCenter", "").strip()

		heading = (
			_("Congratulations, {name} — You Have Completed NVDA Coach!").format(name=name)
			if name else
			_("Congratulations — You Have Completed NVDA Coach!")
		)
		spoken = (
			_("Congratulations, {name}! You have finished every lesson in NVDA Coach. "
			  "This is a tremendous achievement. "
			  "Tab to the Export Certificate of Completion button to save your certificate.").format(name=name)
			if name else
			_("Congratulations! You have finished every lesson in NVDA Coach. "
			  "This is a tremendous achievement. "
			  "Tab to the Export Certificate of Completion button to save your certificate.")
		)

		instructor_line = (
			"\n" + _("Instructor: {instructor}").format(instructor=instructor)
			if instructor else ""
		)
		center_line = (
			"\n" + _("Training Program: {center}").format(center=trainingCenter)
			if trainingCenter else ""
		)

		heartfelt = _(
			"Your dedication and persistence have brought you to this moment. "
			"The skills you have learned in NVDA Coach will serve you every day — "
			"at work, at home, and everywhere in between. "
			"Every expert was once a beginner, and you have proven that with patience "
			"and practice, anything is possible. "
			"Well done, and welcome to a world of greater independence."
		)

		body = (
			heading
			+ instructor_line
			+ center_line
			+ "\n\n"
			+ heartfelt
			+ "\n\n"
			+ _(
				"--- WHAT YOU HAVE LEARNED ---\n"
				"  Chapter 1: Getting Started with NVDA\n"
				"  Chapter 2: Your Keyboard\n"
				"  Chapter 3: Reading Text\n"
				"  Chapter 4: Browse Mode and Web Navigation\n"
				"  Chapter 5: Object Navigation\n"
				"  Chapter 6: Customizing NVDA\n\n"
			)
			+ _(
				"--- YOUR CERTIFICATE OF COMPLETION ---\n"
				"Tab to the Export Certificate button below and press Enter.\n"
				"Your certificate will open in your web browser.\n\n"
				"To save or print your certificate:\n"
				"  1. In your browser, press Ctrl+S to save the page, "
				"or press Ctrl+P to print it.\n"
				"  2. To print to PDF, choose 'Save as PDF' or 'Microsoft Print to PDF' "
				"as your printer.\n"
				"  3. A copy is also saved automatically to your Downloads folder."
			)
		)

		self._statusText.SetLabel(_("NVDA Coach — Course Complete!"))
		self._statusText.GetParent().Layout()
		self._startCourseBtn.Hide()
		self._nextStepBtn.Hide()
		if not self._certBtn.IsShown():
			self._certBtn.Show()
		self._panel.Layout()
		self._instructionText.SetValue(body)
		self._clearEscapeCount()
		ui.message(spoken)

	def showCompletionReturn(self):
		"""Show the course-complete screen quietly when the student re-opens Coach.

		Called on subsequent sessions after the full completion fanfare has already
		been presented. No lesson-complete sound plays — just updates the window
		content and makes a brief spoken announcement.
		"""
		name = config.conf["nvdaCoach"].get("userName", "").strip()

		heading = (
			_("Welcome back, {name} — NVDA Coach Complete!").format(name=name)
			if name else
			_("Welcome back — NVDA Coach Complete!")
		)
		spoken = (
			_("Welcome back, {name}. You have already completed every lesson in NVDA Coach. "
			  "Your certificate is available below.").format(name=name)
			if name else
			_("Welcome back. You have already completed every lesson in NVDA Coach. "
			  "Your certificate is available below.")
		)

		body = (
			heading + "\n\n"
			+ _(
				"You have completed all six chapters of NVDA Coach. "
				"Your progress is saved and your certificate of completion is ready.\n\n"
				"--- YOUR CERTIFICATE ---\n"
				"Tab to the Export Certificate of Completion button below and press Enter "
				"to open your certificate in your web browser. A copy is also saved to your "
				"Downloads folder automatically.\n\n"
				"--- CONTINUE LEARNING ---\n"
				"Press NVDA+Shift+C to open the lesson picker. "
				"You can revisit any lesson at any time to review commands and practice.\n\n"
				"--- LESSON NAVIGATION ---\n"
				"  Ctrl+N  —  Next lesson in the current category\n"
				"  Ctrl+B  —  Previous lesson\n"
				"  Ctrl+R  —  Restart the current lesson\n\n"
				"--- QUICK KEYS ---\n"
				"  F4 — Open help documentation\n"
				"  F5 — Send feedback to the developer\n"
				"  F6 — Toggle lesson sounds on or off\n"
				"  F7 — Update your profile (name, instructor, training center)"
			)
		)

		self._statusText.SetLabel(_("NVDA Coach — Course Complete!"))
		self._statusText.GetParent().Layout()
		self._startCourseBtn.Hide()
		self._nextStepBtn.Hide()
		if not self._certBtn.IsShown():
			self._certBtn.Show()
		self._panel.Layout()
		self._instructionText.SetValue(body)
		self._clearEscapeCount()
		ui.message(spoken)

	def beginEscapeSequence(self):
		"""Arm the 3-Escape-to-close sequence after a lesson is stopped by Escape.

		stopLesson() already announced the stop via speech, so we only update
		the visual text here without generating extra audio.
		"""
		self._escapeCount = 1
		self._instructionText.SetValue(_(
			"Lesson stopped.\n\n"
			"Press Escape two more times to close NVDA Coach.\n"
			"Or press NVDA+Shift+C to start another lesson."
		))
		self._resetEscapeTimer()

	# ------------------------------------------------------------------
	# F4 / F5 / F6 / F7 — quick keys (available at all times in the window)
	# ------------------------------------------------------------------

	_HELP_URL = "https://tonygebhard.me/NVDACoach"
	_FEEDBACK_URL = "mailto:info@tonygebhard.me?subject=Feedback%20for%20NVDA%20Coach"

	def _handleF4(self):
		"""First press: confirm prompt. Second press within 5 s: open help site."""
		if self._f4Armed:
			self._f4Armed = False
			if self._f4Timer:
				try:
					self._f4Timer.Stop()
				except Exception:
					pass
				self._f4Timer = None
			webbrowser.open(self._HELP_URL)
			ui.message(_("Opening NVDA Coach help documentation in your web browser."))
		else:
			self._f4Armed = True
			ui.message(_(
				"If you wish to view the NVDA Coach help documentation, press F4 once more."
			))
			self._f4Timer = wx.CallLater(5000, self._resetF4)

	def _resetF4(self):
		self._f4Armed = False
		self._f4Timer = None

	def _handleF5(self):
		"""First press: confirm prompt. Second press within 5 s: open feedback email."""
		if self._f5Armed:
			self._f5Armed = False
			if self._f5Timer:
				try:
					self._f5Timer.Stop()
				except Exception:
					pass
				self._f5Timer = None
			webbrowser.open(self._FEEDBACK_URL)
			ui.message(_("Opening a feedback email to the developer."))
		else:
			self._f5Armed = True
			ui.message(_(
				"Press F5 once more to open a feedback email to the developer."
			))
			self._f5Timer = wx.CallLater(5000, self._resetF5)

	def _resetF5(self):
		self._f5Armed = False
		self._f5Timer = None

	def _handleF6(self):
		"""Toggle lesson sounds on/off and announce the new state."""
		current = config.conf["nvdaCoach"]["playSounds"]
		config.conf["nvdaCoach"]["playSounds"] = not current
		if config.conf["nvdaCoach"]["playSounds"]:
			ui.message(_("Sounds enabled."))
		else:
			ui.message(_("Sounds disabled."))

	def _handleF7(self):
		"""Open the personalization dialog to set user and instructor names."""
		gui.mainFrame.prePopup()
		dlg = PersonalizationDialog(self)
		dlg.ShowModal()
		dlg.Destroy()
		gui.mainFrame.postPopup()

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

		# F4–F7 work at all times (during a lesson or idle).
		if key == wx.WXK_F4:
			self._handleF4()
			return
		if key == wx.WXK_F5:
			self._handleF5()
			return
		if key == wx.WXK_F6:
			self._handleF6()
			return
		if key == wx.WXK_F7:
			self._handleF7()
			return

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
		# Enter / Numpad Enter → go to next lesson (mirrors the "Next Step" button intent).
		if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			focused = wx.Window.FindFocus()
			# Let Back, Restart, and other buttons handle their own Enter.
			if isinstance(focused, wx.Button) and focused is not self._nextStepBtn:
				evt.Skip()
				return
			self._plugin.nextLesson()
			return

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
			msg = _("Press Escape two more times to close NVDA Coach.")
			ui.message(msg)
			self._instructionText.SetValue(
				msg + "\n\n" + _("Or press NVDA+Shift+C to start a lesson.")
			)
			self._resetEscapeTimer()
		elif self._escapeCount == 2:
			msg = _("Press Escape one more time to close NVDA Coach.")
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
			title=_("NVDA Coach — Practice Area"),
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
		title = lessonTitle or _("Practice Area")
		self.SetTitle(_("NVDA Coach — Practice: {title}").format(title=title))
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
			label=_(
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
		self._addHeading(_("Tab Navigation Practice Form"))
		self._addDesc(_(
			"Press Tab to move forward through these controls. "
			"Press Shift+Tab to move backward. "
			"NVDA announces each control as you land on it."
		))
		self._addSep()

		fgs = wx.FlexGridSizer(rows=0, cols=2, hgap=10, vgap=6)
		fgs.AddGrowableCol(1)
		for labelText, fieldName in [
			(_("First name:"), _("First name")),
			(_("Last name:"), _("Last name")),
			(_("Email address:"), _("Email address")),
		]:
			fgs.Add(
				wx.StaticText(self._scroll, label=labelText),
				0, wx.ALIGN_CENTER_VERTICAL,
			)
			field = wx.TextCtrl(self._scroll)
			field.SetName(fieldName)
			fgs.Add(field, 0, wx.EXPAND)
		self._scrollSizer.Add(fgs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

		cb = wx.CheckBox(self._scroll, label=_("Subscribe to the NVDA Coach newsletter"))
		self._scrollSizer.Add(cb, 0, wx.LEFT | wx.TOP, 12)

		radioBox = wx.RadioBox(
			self._scroll,
			label=_("Preferred contact method"),
			choices=[_("Email"), _("Phone"), _("No preference")],
			majorDimension=3,
			style=wx.RA_SPECIFY_COLS,
		)
		self._scrollSizer.Add(radioBox, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)

		choiceSizer = wx.BoxSizer(wx.HORIZONTAL)
		choiceSizer.Add(
			wx.StaticText(self._scroll, label=_("Country:")),
			0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6,
		)
		choiceSizer.Add(wx.Choice(
			self._scroll,
			choices=[_("United States"), _("Canada"), _("United Kingdom"), _("Australia"), _("Other")],
		))
		self._scrollSizer.Add(choiceSizer, 0, wx.LEFT | wx.TOP, 12)

		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		submitBtn = wx.Button(self._scroll, label=_("Submit form"))
		cancelBtn = wx.Button(self._scroll, label=_("Cancel"))
		btnSizer.Add(submitBtn, 0, wx.RIGHT, 8)
		btnSizer.Add(cancelBtn)
		self._scrollSizer.Add(btnSizer, 0, wx.LEFT | wx.TOP, 12)
		self._addTip()

		submitBtn.Bind(wx.EVT_BUTTON, lambda e: ui.message(
			_("Form submitted. In a real form, this would send your information."),
		))
		cancelBtn.Bind(wx.EVT_BUTTON, lambda e: ui.message(
			_("Cancelled. The form was not submitted."),
		))
		cb.Bind(wx.EVT_CHECKBOX, lambda e: ui.message(
			_("Subscribed to newsletter.") if e.IsChecked() else _("Unsubscribed."),
		))

	# ---- Activate Controls -----------------------------------------------

	def _buildActivateControls(self):
		self._addHeading(_("Activating Controls Practice"))
		self._addDesc(_(
			"Tab to a control and activate it. "
			"Press Space to check or uncheck a checkbox. "
			"Press Enter to activate a button."
		))
		self._addSep()

		self._scrollSizer.Add(
			wx.StaticText(self._scroll, label=_("Checkboxes — press Space to toggle:")),
			0, wx.LEFT | wx.TOP, 12,
		)
		cb1 = wx.CheckBox(self._scroll, label=_("Enable screen reader tips"))
		cb2 = wx.CheckBox(self._scroll, label=_("Show practice hints during lessons"))
		cb3 = wx.CheckBox(self._scroll, label=_("Open Coach window automatically on startup"))
		for cb in (cb1, cb2, cb3):
			self._scrollSizer.Add(cb, 0, wx.LEFT | wx.TOP, 8)

		self._scrollSizer.Add(
			wx.StaticText(self._scroll, label=_("Buttons — press Enter to activate:")),
			0, wx.LEFT | wx.TOP, 16,
		)
		playBtn = wx.Button(self._scroll, label=_("Play a beep sound"))
		greetBtn = wx.Button(self._scroll, label=_("Say hello"))
		tipBtn = wx.Button(self._scroll, label=_("Show keyboard tip"))
		for btn in (playBtn, greetBtn, tipBtn):
			self._scrollSizer.Add(btn, 0, wx.LEFT | wx.TOP, 8)
		self._addTip()

		cb1.Bind(wx.EVT_CHECKBOX, lambda e: ui.message(
			_("Screen reader tips enabled.") if e.IsChecked()
			else _("Screen reader tips disabled."),
		))
		cb2.Bind(wx.EVT_CHECKBOX, lambda e: ui.message(
			_("Practice hints on.") if e.IsChecked() else _("Practice hints off."),
		))
		cb3.Bind(wx.EVT_CHECKBOX, lambda e: ui.message(
			_("Auto-start enabled.") if e.IsChecked() else _("Auto-start disabled."),
		))

		def _playBeep(e):
			tones.beep(880, 120)
			ui.message(_("Beep! You activated the button."))

		playBtn.Bind(wx.EVT_BUTTON, _playBeep)
		greetBtn.Bind(wx.EVT_BUTTON, lambda e: ui.message(
			_("Hello! You just activated a button. Great work."),
		))
		tipBtn.Bind(wx.EVT_BUTTON, lambda e: ui.message(_(
			"Tip: Tab moves between controls. "
			"Enter activates buttons. Space checks or unchecks checkboxes."
		),))

	# ---- Where Am I? / Focus Reporter -----------------------------------

	def _buildWhereAmI(self):
		self._addHeading(_("Find Your Focus — Practice Login Form"))
		self._addDesc(_(
			"Tab around this form. When you land on a control, press "
			"NVDA+Tab to hear its name, type, and current state."
		))
		self._addSep()

		fgs = wx.FlexGridSizer(rows=0, cols=2, hgap=10, vgap=6)
		fgs.AddGrowableCol(1)
		fgs.Add(wx.StaticText(self._scroll, label=_("Username:")), 0, wx.ALIGN_CENTER_VERTICAL)
		userField = wx.TextCtrl(self._scroll)
		userField.SetName(_("Username"))
		fgs.Add(userField, 0, wx.EXPAND)
		fgs.Add(wx.StaticText(self._scroll, label=_("Password:")), 0, wx.ALIGN_CENTER_VERTICAL)
		passField = wx.TextCtrl(self._scroll, style=wx.TE_PASSWORD)
		passField.SetName(_("Password"))
		fgs.Add(passField, 0, wx.EXPAND)
		self._scrollSizer.Add(fgs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

		rememberCb = wx.CheckBox(self._scroll, label=_("Remember me on this computer"))
		self._scrollSizer.Add(rememberCb, 0, wx.LEFT | wx.TOP, 12)

		for label, msg in [
			(_("Sign in"), _("Sign in activated. In a real application, this would log you in.")),
			(_("Create account"), _("Create account activated. This would open a registration form.")),
			(_("Forgot your password?"), _("Password reset activated. A reset link would be sent.")),
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

	def __init__(self, parent, categories, progressTracker, onLessonSelected, coachWindow=None):
		super().__init__(
			parent,
			title=_("NVDA Coach — Choose a Lesson"),
			size=(600, 500),
		)
		self._categories = categories
		self._progress = progressTracker
		self._onLessonSelected = onLessonSelected
		self._coachWindow = coachWindow
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
			label=_(
				"Browse lessons and resources below. "
				"Right arrow expands a section, Left arrow collapses it. "
				"Press Enter or the Open / Start button to activate the selected item. "
				"Press F4 for help, F5 for feedback, F6 to toggle sounds, "
				"F7 or the Profile button to set your name and instructor."
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
		root = self._tree.AddRoot(_("NVDA Coach"))

		# ---- Introduction ------------------------------------------------
		introItem = self._tree.AppendItem(root, _("Introduction / About NVDA Coach"))
		self._tree.SetItemData(introItem, {"type": "intro"})

		# ---- Lesson categories -------------------------------------------
		for category in self._categories:
			catId = category.get("id", "")
			catTitle = category.get("title", _("Unknown Category"))
			lessons = category.get("lessons", [])
			completed, total = self._progress.getCategoryProgress(catId, len(lessons))
			# Translators: progress label in the lesson picker tree
			catLabel = f"{catTitle}  —  " + _("{completed} of {total} complete").format(completed=completed, total=total)
			catItem = self._tree.AppendItem(root, catLabel)
			self._tree.SetItemData(catItem, {"type": "category"})
			for lesson in sorted(lessons, key=lambda l: l.get("order", 999)):
				lessonId = lesson.get("id", "")
				lessonTitle = lesson.get("title", _("Untitled"))
				done = self._progress.isLessonComplete(catId, lessonId)
				# Translators: suffix shown next to a completed lesson in the picker
				label = lessonTitle + ("  " + _("[Done]") if done else "")
				lessonItem = self._tree.AppendItem(catItem, label)
				self._tree.SetItemData(lessonItem, {
					"type": "lesson",
					"categoryId": catId,
					"lesson": lesson,
				})

		# ---- Additional Training and Help --------------------------------
		# Opens a single standalone resources page in the browser.
		helpItem = self._tree.AppendItem(root, _("Additional Training and Help"))
		self._tree.SetItemData(helpItem, {
			"type": "file",
			"label": _("Additional Training and Help"),
			"path": _localizedDocPath("resources.html"),
		})

		# Focus Introduction by default.
		self._tree.SelectItem(introItem)
		sizer.Add(self._tree, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		startBtn = wx.Button(panel, wx.ID_OK, label=_("&Open / Start"))
		startBtn.SetDefault()
		profileBtn = wx.Button(panel, label=_("&Profile  (F7)"))
		profileBtn.SetToolTip(_(
			"Set your name, instructor name, and training center. "
			"This information appears on your certificate of completion and "
			"personalizes lesson instructions throughout NVDA Coach. "
			"You can update your profile at any time."
		))
		cancelBtn = wx.Button(panel, wx.ID_CANCEL, label=_("&Cancel"))
		btnSizer.Add(startBtn, flag=wx.RIGHT, border=5)
		btnSizer.Add(profileBtn, flag=wx.RIGHT, border=5)
		btnSizer.Add(cancelBtn)
		sizer.Add(btnSizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=10)

		panel.SetSizer(sizer)
		startBtn.Bind(wx.EVT_BUTTON, self._onActivate)
		profileBtn.Bind(wx.EVT_BUTTON, self._onProfile)
		cancelBtn.Bind(wx.EVT_BUTTON, self._onCancel)
		self._tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._onActivate)
		self.Bind(wx.EVT_CHAR_HOOK, self._onKeyPress)
		self._tree.SetFocus()

	def _onActivate(self, event):
		"""Handle Enter / double-click / Start button on the selected tree item."""
		item = self._tree.GetSelection()
		if not item.IsOk():
			ui.message(_("Please select an item first."))
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
				ui.message(_("Section collapsed. {count} items hidden.").format(count=count))
			else:
				self._tree.Expand(item)
				count = self._tree.GetChildrenCount(item, recursively=False)
				ui.message(
					_("Section expanded. {count} items available. "
					"Use the Down arrow to browse them.").format(count=count)
				)

		elif itemType == "file":
			path = data.get("path", "")
			label = data.get("label", _("File"))
			if not os.path.exists(path):
				ui.message(
					_("{label} is not available in this version of NVDA Coach.").format(label=label)
				)
				return
			try:
				os.startfile(path)
				ui.message(_("Opening {label}.").format(label=label))
			except Exception as e:
				log.warning(f"NVDA Coach: Could not open {path}: {e}")
				ui.message(
					_("Could not open {label}. "
					"Please check that the add-on is installed correctly.").format(label=label)
				)

		elif itemType == "url":
			url = data.get("url", "")
			try:
				webbrowser.open(url)
				ui.message(_("Opening {url} in your web browser.").format(url=url))
			except Exception as e:
				log.warning(f"NVDA Coach: Could not open URL {url}: {e}")
				ui.message(_(
					"Could not open the website. "
					"Please check your internet connection."
				))

	def _onCancel(self, event):
		self.Destroy()

	def _onProfile(self, event):
		"""Open the personalization dialog (same as F7) from the lesson picker."""
		if self._coachWindow:
			self._coachWindow._handleF7()

	def _onKeyPress(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.Destroy()
			return
		# F4–F7 delegate to CoachWindow handlers so they work here too.
		if self._coachWindow:
			if key == wx.WXK_F4:
				self._coachWindow._handleF4()
				return
			if key == wx.WXK_F5:
				self._coachWindow._handleF5()
				return
			if key == wx.WXK_F6:
				self._coachWindow._handleF6()
				return
			if key == wx.WXK_F7:
				self._coachWindow._handleF7()
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
		self._lessonRunner.onLessonComplete = self._onLessonComplete
		# Create the practice window (hidden; shown automatically per lesson).
		self._practiceFrame = PracticeFrame(gui.mainFrame, self)
		# Register NVDA settings panel.
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(NvdaCoachSettingsPanel)
		# Add NVDA Coach item to NVDA Help menu.
		self._helpMenuItem = gui.mainFrame.sysTrayIcon.helpMenu.Append(
			wx.ID_ANY,
			_("&NVDA Coach"),
			_("Open NVDA Coach lesson picker"),
		)
		gui.mainFrame.sysTrayIcon.helpMenu.Bind(
			wx.EVT_MENU, self._onHelpMenuActivated, self._helpMenuItem
		)
		log.info(f"NVDA Coach loaded. {len(self._categories)} lesson categories found.")
		# If the student has already completed the final chapter in a prior session,
		# quietly show the certificate button when the add-on loads (no fanfare, no speech).
		if self._categories and self._nvdaSettingsComplete():
			self._coachWindow.showCertificateButton(silent=True)

	def terminate(self):
		self._lessonRunner.cleanup()
		# Deregister settings panel.
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(NvdaCoachSettingsPanel)
		except ValueError:
			pass
		# Remove Help menu item.
		try:
			gui.mainFrame.sysTrayIcon.helpMenu.Remove(self._helpMenuItem)
		except Exception:
			pass
		for win in (self._coachWindow, self._practiceFrame):
			try:
				win.Destroy()
			except Exception:
				pass

	def _onHelpMenuActivated(self, evt):
		"""Open the NVDA Coach lesson picker from the NVDA Help menu."""
		self._activateCoach()

	def _activateCoach(self):
		"""Open the lesson picker, or refocus the coach window if a lesson is active."""
		if self._lessonRunner.isActive:
			if not self._coachWindow.IsShown():
				self._coachWindow.Show()
			self._coachWindow.Raise()
			wx.CallAfter(self._coachWindow.focusInstructionText)
			ui.message(_(
				"NVDA Coach. "
				"Press Enter or Next Step to continue, "
				"or Escape to stop the lesson."
			))
			return
		if not self._categories:
			ui.message(_(
				"NVDA Coach: No lesson files found. "
				"Please check that the lessons folder is in the add-on directory."
			))
			return
		if not self._coachWindow.IsShown():
			self._coachWindow.Show()
		self._coachWindow.Raise()
		# If the student has already completed every lesson, show the quiet
		# "welcome back / course complete" screen before the picker opens.
		if self._allLessonsComplete():
			self._coachWindow.showCompletionReturn()
		self._showLessonPicker()

	@script(
		description=_("Show NVDA Coach window, or open the lesson picker"),
		gesture="kb:NVDA+shift+c",
		category=_("NVDA Coach"),
	)
	def script_toggleCoach(self, gesture):
		"""Show and focus the CoachWindow.

		During a lesson: brings CoachWindow to the foreground so the student
		can press Enter to advance after trying a command in another window.
		Between lessons: opens the lesson picker.
		"""
		self._activateCoach()

	def _showLessonPicker(self):
		"""Show the lesson selection dialog and wire up the selection callback."""
		# Reload progress to get the latest completed status.
		self._progressTracker = ProgressTracker()
		self._lessonRunner = LessonRunner(self._progressTracker)
		self._lessonRunner.coachWindow = self._coachWindow
		self._lessonRunner.onLessonComplete = self._onLessonComplete
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
			# Wire up practice frame callback so it opens only after the priming step.
			lessonId = lesson.get("id", "")
			if lessonId in PracticeFrame.SUPPORTED_LESSONS:
				_lid, _ltitle = lessonId, lesson.get("title", "")
				self._lessonRunner.onOpenPracticeFrame = (
					lambda lid=_lid, lt=_ltitle: self._practiceFrame.showForLesson(lid, lt)
				)

			if category and category.get("practicePage"):
				# Wire up browse-mode callbacks on the runner.
				self._lessonRunner.onOpenPracticePage = self._openPracticePage
				self._lessonRunner.onChapterComplete = self._onBrowseModeComplete
				self._coachWindow.Show()
				self._coachWindow.Raise()
				lessonId = lesson.get("id", "")
				if lessonId != "intro_browse_mode":
					# For non-intro browse lessons the practice page opens after 2s
					# so the student can hear the first step before the browser appears.
					wx.CallLater(2000, self._openPracticePage)
				# intro_browse_mode handles opening via its openPracticePageAfter step flag.
				wx.CallLater(
					300,
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
			coachWindow=self._coachWindow,
		)
		dialog.Show()
		gui.mainFrame.postPopup()

	# ------------------------------------------------------------------
	# Lesson navigation — called from CoachWindow keyboard handler
	# ------------------------------------------------------------------

	def _wirePracticeFrame(self, lessonId, lessonTitle):
		"""If the lesson uses a PracticeFrame, wire the callback for deferred opening."""
		if lessonId in PracticeFrame.SUPPORTED_LESSONS:
			self._lessonRunner.onOpenPracticeFrame = (
				lambda lid=lessonId, lt=lessonTitle: self._practiceFrame.showForLesson(lid, lt)
			)
		else:
			self._lessonRunner.onOpenPracticeFrame = None

	def nextLesson(self):
		"""Advance to the next lesson in the current category (Ctrl+N)."""
		if not self._currentCategoryLessons:
			ui.message(_("No active category. Press NVDA+Shift+C to choose a lesson."))
			return
		if self._currentLessonIndex >= len(self._currentCategoryLessons) - 1:
			ui.message(_(
				"You are on the last lesson in this category. "
				"Press NVDA+Shift+C to open the lesson picker "
				"and continue to the next chapter."
			))
			return
		if self._lessonRunner.isActive:
			self._lessonRunner.stopLesson(announce=False)
		self._currentLessonIndex += 1
		lesson = self._currentCategoryLessons[self._currentLessonIndex]
		lessonId = lesson.get("id", "")
		self._wirePracticeFrame(lessonId, lesson.get("title", ""))
		ui.message(_("Moving to: {title}.").format(title=lesson.get("title", _("next lesson"))))
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
			ui.message(_("No active category. Press NVDA+Shift+C to choose a lesson."))
			return
		if self._currentLessonIndex <= 0:
			ui.message(_("You are on the first lesson in this category."))
			return
		if self._lessonRunner.isActive:
			self._lessonRunner.stopLesson(announce=False)
		self._currentLessonIndex -= 1
		lesson = self._currentCategoryLessons[self._currentLessonIndex]
		lessonId = lesson.get("id", "")
		self._wirePracticeFrame(lessonId, lesson.get("title", ""))
		ui.message(_("Going back to: {title}.").format(title=lesson.get("title", _("previous lesson"))))
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
			ui.message(_("No active category. Press NVDA+Shift+C to choose a lesson."))
			return
		if self._lessonRunner.isActive:
			self._lessonRunner.stopLesson(announce=False)
		lesson = self._currentCategoryLessons[self._currentLessonIndex]
		lessonId = lesson.get("id", "")
		self._wirePracticeFrame(lessonId, lesson.get("title", ""))
		ui.message(_("Restarting lesson."))
		wx.CallLater(
			600,
			self._lessonRunner.startLesson,
			self._currentCategoryId,
			lesson,
			self._currentCategoryTitle,
		)

	def startFirstLesson(self):
		"""Start the first lesson of the Getting Started chapter (Start Course button)."""
		category = next(
			(c for c in self._categories if c.get("id") == "getting_started"), None
		)
		if not category:
			ui.message(_("Could not find the Getting Started chapter."))
			return
		lessons = sorted(
			category.get("lessons", []), key=lambda l: l.get("order", 999)
		)
		if not lessons:
			return
		lesson = lessons[0]
		self._currentCategoryId = "getting_started"
		self._currentCategoryTitle = category.get("title", "")
		self._currentCategoryLessons = lessons
		self._currentLessonIndex = 0
		self._coachWindow.Show()
		self._coachWindow.Raise()
		wx.CallLater(
			300,
			self._lessonRunner.startLesson,
			"getting_started",
			lesson,
			category.get("title", ""),
		)

	def _openPracticePage(self):
		"""Open the browse mode practice HTML page in the default browser."""
		practiceFile = _localizedDocPath("practice.html")
		try:
			os.startfile(practiceFile)
		except Exception as e:
			log.warning(f"NVDA Coach: Could not open practice page: {e}")

	def _onBrowseModeComplete(self):
		"""Handle browse mode chapter completion: show congrats screen and close browser."""
		self._coachWindow.showBrowseModeCompletion()
		wx.CallLater(1500, self._closePracticeBrowserWindow)

	def _closePracticeBrowserWindow(self):
		"""Close any browser window whose title contains 'NVDA Coach Practice Page'."""
		TITLE_PARTIAL = _("NVDA Coach Practice Page")
		try:
			found = []

			def _enum_cb(hwnd, _param):
				length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
				if length > 0:
					buf = ctypes.create_unicode_buffer(length + 1)
					ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
					if TITLE_PARTIAL in buf.value:
						found.append(hwnd)
				return True

			_WNDENUMPROC = ctypes.WINFUNCTYPE(
				ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
			)
			ctypes.windll.user32.EnumWindows(_WNDENUMPROC(_enum_cb), 0)
			for hwnd in found:
				ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
		except Exception as e:
			log.warning(f"NVDA Coach: Could not close practice browser window: {e}")

	# ------------------------------------------------------------------
	# Course completion certificate
	# ------------------------------------------------------------------

	def _nvdaSettingsComplete(self):
		"""Return True when every lesson in the final chapter (nvda_settings) is marked complete."""
		for category in self._categories:
			if category.get("id") == "nvda_settings":
				return all(
					self._progressTracker.isLessonComplete("nvda_settings", l.get("id", ""))
					for l in category.get("lessons", [])
				)
		return False

	def _allLessonsComplete(self):
		"""Return True only when every lesson in every category is marked complete."""
		for category in self._categories:
			catId = category.get("id", "")
			for lesson in category.get("lessons", []):
				if not self._progressTracker.isLessonComplete(catId, lesson.get("id", "")):
					return False
		return True

	def _onLessonComplete(self, categoryId, lessonId):
		"""Called by LessonRunner after every lesson finishes.

		Returns True when the final chapter (nvda_settings) is fully complete,
		so lessonRunner skips the standard idle/navigation screen for the last lesson.
		"""
		# Trigger final completion when the Customizing NVDA chapter is all done.
		if categoryId == "nvda_settings":
			for category in self._categories:
				if category.get("id") == "nvda_settings":
					all_done = all(
						self._progressTracker.isLessonComplete("nvda_settings", l.get("id", ""))
						for l in category.get("lessons", [])
					)
					if all_done:
						wx.CallLater(2500, self._coachWindow.showFinalCompletion)
						return True
		return False

	def _showCompletionCertificate(self):
		"""Generate and present the certificate of completion."""
		try:
			_generateCertificate()
		except Exception as e:
			log.error(f"NVDA Coach: Could not generate certificate: {e}")
			ui.message(_(
				"Could not save the certificate. "
				"Please check that your Downloads folder is accessible."
			))
			return
		name = config.conf["nvdaCoach"].get("userName", "").strip()
		gui.mainFrame.prePopup()
		dlg = CertificateDialog(gui.mainFrame, name)
		dlg.ShowModal()
		dlg.Destroy()
		gui.mainFrame.postPopup()
