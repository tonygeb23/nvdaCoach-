"""Tests for NVDA Coach that run outside NVDA.

NVDA's own modules are replaced with small stand-ins, and wxPython is the
real thing, so the add-on's own logic runs unchanged. Nothing is shown on
screen, nothing is spoken, and no window takes keyboard focus: speech goes
to a list, and SetFocus and Show are switched off for the run.

    python -m unittest discover -s tests -v

Set COACH_ROOT to test another copy of the add-on (an unpacked build, or an
older checkout) instead of this one.
"""
import builtins
import json
import os
import shutil
import sys
import tempfile
import types
import unittest

import wx

ROOT = os.environ.get("COACH_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS = os.path.join(ROOT, "globalPlugins", "nvdaCoach", "lessons")

spoken = []
_tmp = tempfile.mkdtemp(prefix="coachtest_")
_app = wx.App(False)

# Never take focus or put a window on screen during a test run.
wx.Window.SetFocus = lambda self: None
wx.Frame.Show = lambda self, show=True: True
wx.Frame.Raise = lambda self: None
wx.Dialog.Show = lambda self, show=True: True


def _module(name, **attrs):
	mod = types.ModuleType(name)
	mod.__dict__.update(attrs)
	sys.modules[name] = mod
	return mod


class _Conf(dict):
	spec = {}


class _Log:
	def __getattr__(self, name):
		return lambda *a, **k: None


class _MainFrame(wx.Frame):
	def __init__(self):
		super().__init__(None)
		self.sysTrayIcon = types.SimpleNamespace(helpMenu=wx.Menu())

	def prePopup(self):
		pass

	def postPopup(self):
		pass


def _installStubs(language="en"):
	conf = _Conf(nvdaCoach={
		"playSounds": False, "userName": "", "instructorName": "", "trainingCenter": "",
	})
	_module("config", conf=conf)
	_module("ui", message=lambda text, *a, **k: spoken.append(text))
	_module("tones", beep=lambda *a, **k: None)
	_module("nvwave", playWaveFile=lambda *a, **k: None)
	_module("api", getFocusObject=lambda: None)
	_module("logHandler", log=_Log())
	_module("languageHandler", getLanguage=lambda: language)
	_module("globalVars", appArgs=types.SimpleNamespace(configPath=_tmp))
	_module("globalPluginHandler", GlobalPlugin=type("GlobalPlugin", (), {"__init__": lambda self: None}))
	_module("scriptHandler", script=lambda **kw: (lambda fn: fn))
	_module("addonHandler", initTranslation=lambda: None)
	builtins._ = lambda text: text
	settingsDialogs = _module(
		"gui.settingsDialogs",
		SettingsPanel=type("SettingsPanel", (), {}),
		NVDASettingsDialog=type("NVDASettingsDialog", (), {"categoryClasses": []}),
	)
	_module("gui", settingsDialogs=settingsDialogs, mainFrame=_MainFrame())
	return conf


def _loadCoach(language="en"):
	conf = _installStubs(language)
	for name in [n for n in sys.modules if n.startswith("globalPlugins")]:
		del sys.modules[name]
	if ROOT not in sys.path:
		sys.path.insert(0, ROOT)
	import globalPlugins.nvdaCoach as coach
	return coach, conf


def _resetProgress():
	path = os.path.join(_tmp, "nvdaCoachProgress.json")
	if os.path.exists(path):
		os.remove(path)


def _complete(plugin, categoryIds):
	for category in plugin._categories:
		if category["id"] in categoryIds:
			for lesson in category["lessons"]:
				plugin._progressTracker.markLessonComplete(category["id"], lesson["id"], {}, 1)


class LessonFiles(unittest.TestCase):
	"""The English lesson files are well formed and say what the code needs."""

	def setUp(self):
		self.chapters = {}
		for name in sorted(os.listdir(os.path.join(LESSONS, "en"))):
			if name.endswith(".json"):
				with open(os.path.join(LESSONS, "en", name), encoding="utf-8") as f:
					self.chapters[name] = json.load(f)

	def test_eight_chapters_in_order(self):
		orders = sorted((c["order"], c["id"]) for c in self.chapters.values())
		self.assertEqual([o for o, _i in orders], list(range(1, 9)))
		self.assertEqual(orders[6][1], "addon_store")
		self.assertEqual(orders[7][1], "braille")

	def test_only_braille_is_optional(self):
		optional = [c["id"] for c in self.chapters.values() if c.get("optional") is True]
		self.assertEqual(optional, ["braille"])

	def test_every_step_is_complete(self):
		for name, chapter in self.chapters.items():
			ids = [l["id"] for l in chapter["lessons"]]
			self.assertEqual(len(ids), len(set(ids)), name)
			orders = [l["order"] for l in chapter["lessons"]]
			self.assertEqual(sorted(orders), list(range(1, len(orders) + 1)), name)
			for lesson in chapter["lessons"]:
				self.assertTrue(lesson["title"].strip(), lesson["id"])
				self.assertTrue(lesson["steps"], lesson["id"])
				for step in lesson["steps"]:
					self.assertIn(step["type"], ("info", "gesture"), lesson["id"])
					self.assertTrue(step["instruction"].strip(), lesson["id"])
					self.assertTrue(step.get("hints") or step.get("hint"), lesson["id"])

	def test_chapter_end_marker_is_on_the_last_lesson(self):
		"""A chapter may leave the marker out, but may not misplace it."""
		for name, chapter in self.chapters.items():
			marked = [l["id"] for l in chapter["lessons"] if l.get("chapterComplete")]
			last = max(chapter["lessons"], key=lambda l: l["order"])["id"]
			self.assertIn(marked, ([], [last]), name)

	def test_new_chapters_never_strand_the_student(self):
		"""Every step in the new chapters says how to move on.

		These lessons send the student into other windows, so each step has to
		end by telling them to press Enter (back in the Coach) to continue.
		"""
		for name in ("addon_store.json", "braille.json"):
			for lesson in self.chapters[name]["lessons"]:
				for n, step in enumerate(lesson["steps"], 1):
					tail = step["instruction"][-170:]
					self.assertIn("ress Enter", tail, "%s step %d" % (lesson["id"], n))
					self.assertEqual(len(step["hints"]), 3, "%s step %d" % (lesson["id"], n))

	def test_twenty_five_addons_are_named(self):
		names = [
			"Windows App Essentials", "Resource Monitor", "Emoticons", "Nao", "Clock",
			"GoldWave", "ObjPad", "Place markers", "Mozilla Apps Enhancements",
			"Clip Contents Designer", "Input lock", "VLC Media Player", "mp3DirectCut",
			"Read Feeds", "Instant Translate", "Tele NVDA", "Report Symbols",
			"Day of the week", "Switch synth", "SentenceNav", "Enhanced Touch Gestures",
			"StationPlaylist", "Speech history", "Access8Math", "Outlook Extended",
		]
		self.assertEqual(len(names), 25)
		text = " ".join(
			step["instruction"]
			for lesson in self.chapters["addon_store.json"]["lessons"]
			if lesson["id"].startswith("popular_")
			for step in lesson["steps"]
		)
		missing = [n for n in names if n not in text]
		self.assertEqual(missing, [])


class CourseCompletion(unittest.TestCase):
	"""Which chapters count toward the certificate, and when it is offered."""

	REQUIRED = [
		"getting_started", "keyboard_reference", "reading_text", "browse_mode",
		"object_navigation", "nvda_settings", "addon_store",
	]

	def setUp(self):
		_resetProgress()
		del spoken[:]
		self.coach, self.conf = _loadCoach()
		self.plugin = self.coach.GlobalPlugin()

	def tearDown(self):
		self.plugin.terminate()

	def test_loads_eight_chapters(self):
		self.assertEqual(
			[c["id"] for c in self.plugin._categories],
			self.REQUIRED + ["braille"],
		)

	def test_fresh_student_is_not_complete(self):
		self.assertFalse(self.plugin._allLessonsComplete())
		self.assertFalse(self.plugin._coachWindow._certBtn.IsShown())

	def test_last_old_chapter_alone_is_not_complete(self):
		"""1.6.0 offered the certificate button for this on every start."""
		_complete(self.plugin, ["nvda_settings"])
		self.assertFalse(self.plugin._allLessonsComplete())
		self.assertFalse(self.plugin._onLessonComplete("nvda_settings", "audio_ducking"))

	def test_six_old_chapters_now_need_the_addon_store(self):
		_complete(self.plugin, self.REQUIRED[:6])
		self.assertFalse(self.plugin._allLessonsComplete())

	def test_complete_without_braille(self):
		_complete(self.plugin, self.REQUIRED)
		self.assertTrue(self.plugin._allLessonsComplete())
		self.assertTrue(self.plugin._onLessonComplete("addon_store", "popular_app_support"))
		learned = self.plugin.chaptersLearned()
		self.assertEqual([n for n, _t in learned], [1, 2, 3, 4, 5, 6, 7])

	def test_braille_alone_is_not_complete(self):
		_complete(self.plugin, ["braille"])
		self.assertFalse(self.plugin._allLessonsComplete())

	def test_braille_lesson_does_not_replay_the_fanfare(self):
		_complete(self.plugin, self.REQUIRED)
		self.assertFalse(self.plugin._onLessonComplete("braille", "connect_display"))

	def test_finished_braille_is_listed(self):
		_complete(self.plugin, self.REQUIRED + ["braille"])
		learned = self.plugin.chaptersLearned()
		self.assertEqual(learned[-1], (8, "Using a Braille Display"))

	def test_completion_screen_lists_real_chapters(self):
		_complete(self.plugin, self.REQUIRED)
		window = self.plugin._coachWindow
		window.showFinalCompletion()
		body = window._instructionText.GetValue()
		self.assertIn("Chapter 7: Add-ons and the Add-on Store", body)
		self.assertIn("Chapter 3: Reading and Moving Through Text", body)
		self.assertNotIn("Braille", body)
		self.assertNotIn("six", body)
		window.showCompletionReturn()
		self.assertNotIn("six chapters", window._instructionText.GetValue())

	def test_optional_string_is_not_optional(self):
		self.assertFalse(self.coach._isOptionalCategory({"optional": "true"}))
		self.assertFalse(self.coach._isOptionalCategory({"optional": 1}))
		self.assertTrue(self.coach._isOptionalCategory({"optional": True}))

	def test_picker_marks_the_optional_chapter(self):
		dialog = self.coach.LessonPickerDialog(
			self.plugin._coachWindow, self.plugin._categories,
			self.plugin._progressTracker, lambda *a: None,
		)
		tree = dialog._tree
		labels = []
		item, cookie = tree.GetFirstChild(tree.GetRootItem())
		while item.IsOk():
			labels.append(tree.GetItemText(item))
			item, cookie = tree.GetNextChild(tree.GetRootItem(), cookie)
		dialog.Destroy()
		braille = [l for l in labels if l.startswith("Using a Braille Display")]
		self.assertEqual(len(braille), 1)
		self.assertTrue(braille[0].endswith("optional"), braille[0])
		self.assertIn("0 of 8 complete", braille[0])
		self.assertEqual(len([l for l in labels if l.endswith("optional")]), 1)
		store = [l for l in labels if l.startswith("Add-ons and the Add-on Store")]
		self.assertIn("0 of 11 complete", store[0])


class Certificate(unittest.TestCase):
	"""The certificate file is actually written. In 1.6.0 it never was."""

	def setUp(self):
		_resetProgress()
		self.coach, self.conf = _loadCoach()
		self.outDir = tempfile.mkdtemp(prefix="coachcert_")
		self.opened = []
		self._startfile = os.startfile
		os.startfile = lambda path, *a: self.opened.append(path)
		if hasattr(self.coach, "_downloadsFolder"):
			self.coach._downloadsFolder = lambda: self.outDir
		else:  # 1.6.0 builds the path from the home folder
			self._home = os.environ.get("USERPROFILE")
			os.environ["USERPROFILE"] = self.outDir
			os.makedirs(os.path.join(self.outDir, "Downloads"))

	def tearDown(self):
		os.startfile = self._startfile
		if hasattr(self, "_home"):
			os.environ["USERPROFILE"] = self._home
		shutil.rmtree(self.outDir, ignore_errors=True)

	def test_certificate_is_written_and_escaped(self):
		self.conf["nvdaCoach"]["userName"] = "Ada <b>Lovelace</b>"
		self.conf["nvdaCoach"]["instructorName"] = "Smith & Jones"
		path = self.coach._generateCertificate()
		self.assertEqual(self.opened, [path])
		with open(path, encoding="utf-8") as f:
			page = f.read()
		self.assertIn("Ada &lt;b&gt;Lovelace&lt;/b&gt;", page)
		self.assertIn("Smith &amp; Jones", page)
		self.assertNotIn("<b>Lovelace", page)
		self.assertIn("Certificate of Completion", page)

	def test_real_downloads_folder_exists(self):
		if not hasattr(self.coach, "_downloadsFolder"):
			self.skipTest("this build guesses the folder")
		coach, _conf = _loadCoach()
		self.assertTrue(os.path.isdir(coach._downloadsFolder()))


class EveryLanguage(unittest.TestCase):
	"""Each language loads, runs to the end, and agrees with English."""

	def _english(self):
		out = {}
		for name in sorted(os.listdir(os.path.join(LESSONS, "en"))):
			if name.endswith(".json"):
				with open(os.path.join(LESSONS, "en", name), encoding="utf-8") as f:
					out[name] = json.load(f)
		return out

	def test_new_chapters_match_english_structure(self):
		english = self._english()
		for language in sorted(os.listdir(LESSONS)):
			for name in ("addon_store.json", "braille.json"):
				path = os.path.join(LESSONS, language, name)
				if language == "en" or not os.path.isfile(path):
					continue
				with open(path, encoding="utf-8") as f:
					mine = json.load(f)
				where = "%s/%s" % (language, name)
				self.assertEqual(mine["id"], english[name]["id"], where)
				self.assertEqual(mine.get("optional"), english[name].get("optional"), where)
				self.assertEqual(
					[(l["id"], l["order"], len(l["steps"]), bool(l.get("chapterComplete"))) for l in mine["lessons"]],
					[(l["id"], l["order"], len(l["steps"]), bool(l.get("chapterComplete"))) for l in english[name]["lessons"]],
					where,
				)
				for lesson in mine["lessons"]:
					for step in lesson["steps"]:
						self.assertEqual(len(step["hints"]), 3, "%s %s" % (where, lesson["id"]))
						self.assertTrue(step["instruction"].strip(), "%s %s" % (where, lesson["id"]))

	def test_a_language_has_both_new_chapters_or_neither(self):
		for language in sorted(os.listdir(LESSONS)):
			have = [
				os.path.isfile(os.path.join(LESSONS, language, name))
				for name in ("addon_store.json", "braille.json")
			]
			self.assertIn(have, ([True, True], [False, False]), language)

	def test_every_language_runs_to_its_certificate(self):
		for language in sorted(os.listdir(LESSONS)):
			_resetProgress()
			coach, _conf = _loadCoach(language)
			plugin = coach.GlobalPlugin()
			try:
				runner = plugin._lessonRunner
				self.assertGreaterEqual(len(plugin._categories), 6, language)
				for category in plugin._categories:
					for lesson in category["lessons"]:
						runner.isActive = False
						runner.startLesson(category["id"], lesson, category["title"])
						runner._speakCurrentStep()
						for _step in lesson["steps"]:
							runner.speakHint()
							runner.advanceCurrentStep()
						self.assertFalse(runner.isActive, "%s %s" % (language, lesson["id"]))
				self.assertTrue(plugin._allLessonsComplete(), language)
				optional = [c["id"] for c in plugin._categories if coach._isOptionalCategory(c)]
				self.assertIn(optional, ([], ["braille"]), language)
			finally:
				plugin.terminate()


class PracticePage(unittest.TestCase):
	def test_title_is_read_in_each_language(self):
		expected = {
			"en": "NVDA Coach Practice Page",
			"es": "Página de Práctica de NVDA Coach",
			"ja": "NVDAコーチ — 練習ページ",
			"zh_TW": "NVDA Coach 練習頁面",
		}
		for language, title in expected.items():
			coach, _conf = _loadCoach(language)
			if not hasattr(coach, "_practicePageTitle"):
				self.skipTest("this build matches the English title only")
			self.assertEqual(coach._practicePageTitle(), title, language)


class Runner(unittest.TestCase):
	def setUp(self):
		_resetProgress()
		del spoken[:]
		self.coach, self.conf = _loadCoach()
		self.plugin = self.coach.GlobalPlugin()

	def tearDown(self):
		self.plugin.terminate()

	def test_every_lesson_runs_to_the_end(self):
		"""Walk all lessons step by step through the real runner."""
		runner = self.plugin._lessonRunner
		count = 0
		for category in self.plugin._categories:
			for lesson in category["lessons"]:
				runner.isActive = False
				runner.startLesson(category["id"], lesson, category["title"])
				runner._speakCurrentStep()
				for _step in lesson["steps"]:
					self.assertTrue(runner.isActive, lesson["id"])
					runner.repeatInstruction()
					runner.speakHint()
					runner.advanceCurrentStep()
				self.assertFalse(runner.isActive, lesson["id"])
				self.assertTrue(
					self.plugin._progressTracker.isLessonComplete(category["id"], lesson["id"])
				)
				count += 1
		self.assertEqual(count, 64)
		self.assertTrue(self.plugin._allLessonsComplete())

	def test_stopped_lesson_does_not_announce_itself(self):
		runner = self.plugin._lessonRunner
		if not hasattr(runner, "_speakIfActive"):
			self.skipTest("this build has no guard")
		lesson = self.plugin._categories[0]["lessons"][0]
		runner.startLesson("getting_started", lesson, "Getting Started")
		runner.stopLesson(announce=False)
		del spoken[:]
		runner._speakIfActive("Starting lesson")
		self.assertEqual(spoken, [])


if __name__ == "__main__":
	unittest.main()
