# NVDA Coach — Changelog

## v1.5.4 (2026-04-29)

### Compatibility
- **NVDA 2026.1 compatibility confirmed:** NVDA Coach has been tested and verified to work correctly with NVDA 2026.1 (64-bit, Python 3.13). The `lastTestedNVDAVersion` declaration has been updated to 2026.1 so users on NVDA 2026.1 no longer see a compatibility warning in the Add-on Store. No code changes were required — NVDA Coach is pure Python with no compiled extensions.

---

## v1.5.3 (2026-04-23)

### Bug Fixes
- **Lesson text encoding corrected:** 144 corrupted em dash characters (appearing as "â€"" in three English lesson files) have been replaced with the correct em dash character (—). The corruption affected `getting_started.json` (87 instances), `nvda_settings.json` (20 instances), and `reading_text.json` (37 instances). NVDA would have spoken these as "â€" " instead of a natural pause. No lesson content, commands, or instructions were changed — only the character encoding.

---

## v1.5.2 (2026-04-14)

### Bug Fixes
- **Completion notification no longer fires on every restart:** A bug caused NVDA Coach to announce "Congratulations — you have completed every lesson!" and make a sound through NVDA's speech output each time NVDA restarted (or the computer was rebooted), if the student had previously completed the course. The startup check now silently restores the certificate button without speaking — the announcement only plays during the actual completion event in the current session.

### New Features
- **Profile button in lesson picker:** A new "Profile (F7)" button appears in the lesson picker dialog alongside Open/Start and Cancel. This provides an easily discoverable way to set your name, instructor name, and training center — the same action as pressing F7. The button includes a tooltip describing its purpose.
- **Post-completion return screen:** When a student who has already finished all lessons opens NVDA Coach in a later session, the Coach window now shows a quiet "Welcome back — Course Complete!" screen with instructions for accessing the certificate and revisiting lessons. No completion sound plays — only a brief spoken welcome.
- **F1–F7 key reference in the introduction:** The introduction screen and the initial Coach window text now include a full quick-reference section for all available function keys: Enter (next step), F1 (repeat instruction), F2 (hint), F3 (skip step), Escape (stop lesson), F4 (help docs), F5 (feedback email), F6 (toggle sounds), and F7 (profile). Navigation shortcuts (Ctrl+N, Ctrl+B, Ctrl+R) are also listed. This gives new students a complete overview before their first lesson begins.
- **Lesson picker hint text updated:** The hint at the top of the lesson picker dialog now mentions the F4–F7 keys and the Profile button so students know they have access to these functions while browsing lessons.

### New Lessons (45 total, up from 41)
- **Check Your Battery Status** (Chapter 1: Getting Started, Lesson 14) — NVDA+Shift+B announces battery percentage and charging state on laptops. On desktops, NVDA reports that battery status is not available. Covers why this matters for screen reader users who can't glance at the taskbar.
- **Check Font and Formatting** (Chapter 3: Reading and Moving Through Text, Lesson 8) — NVDA+F reports the font name, size, and attributes (bold, italic, underline) at the cursor. Pressing NVDA+F twice in rapid succession opens a full Font Formatting dialog with all details in a browseable window. Covers when to use each mode for proofreading and document review.
- **Change the Audio Output Device** (Chapter 6: Customizing NVDA, Lesson 3) — NVDA+Ctrl+U opens the audio output device picker. Covers switching NVDA speech to headphones, external speakers, or HDMI when Windows does not route audio automatically.
- **Control Audio Ducking** (Chapter 6: Customizing NVDA, Lesson 4) — NVDA+Shift+D cycles through ducking modes: No Ducking, Duck While Speaking, and Duck While Speaking or Playing Audio. Covers the practical difference between modes and why Duck While Speaking is the recommended default for most users.

### Localization
- **Spanish (es) translation:** All six lesson chapters, all three HTML documentation files, and all UI strings are now available in Spanish. Spanish-speaking users who set their NVDA language to Spanish will receive fully localized lesson content, documentation, and interface strings.
- **Spanish practice text corrected (Mateo Quintela):** The practice text used throughout the Reading and Moving Through Text chapter has been updated to Mateo Quintela's Spanish-idiomatic version — a natural-sounding opening line using the well-known Spanish pangram, clearer phrasing throughout the short block, and a revised paragraph block for the paragraph navigation lesson.

### Acknowledgments
- **Mateo Quintela** (Spain) — Spanish localization testing and practice text.

---

## v1.5.1 (2026-04-11)

### Bug Fixes
- **User Guide shortcut corrected:** Two hint strings in the Getting Started chapter incorrectly told users to press G to open the User Guide from the NVDA Help menu. The correct accelerator is U (User Guide). Fixed in English lesson content (`getting_started.json`).

### Localization
- **Russian translation fully integrated (Valentin Kupriyanov):** All 6 lesson chapters in Russian are now included, along with updated `doc/ru` documentation, updated `locale/ru` PO/MO files (163 strings covering all v1.5 content), and the compiled `nvda.mo` binary that NVDA requires to activate the translation. Russian-speaking users received English content in v1.5 due to the missing binary — this release restores full Russian localization.

---

## v1.5 (2026-04-10)

### New Features

- **Personalization (F7):** A new profile dialog (F7 in the Coach window or lesson picker) lets students enter their name, instructor's name, and training program or center. NVDA Coach uses these throughout the session: a one-time personalized greeting on first lesson start ("Hello, Tony! Your instructor today is Sarah."), personalized lesson completions ("Well done, Tony!"), a named welcome on the introduction screen, and a personalized "Ready, Tony." on the idle screen. All fields are optional — generic text is used when left blank.
- **F4–F7 quick keys:** Four function keys are now available at all times inside the Coach window and the lesson picker. F4 opens the NVDA Coach help documentation in the browser (two presses required, with a 5-second confirmation window). F5 opens a pre-addressed feedback email to the developer (two presses required). F6 immediately toggles lesson sounds on or off and announces the new state. F7 opens the personalization dialog. The shortcut bar in the Coach window now displays both rows.
- **Certificate of Completion:** Finishing all lessons in the Customizing NVDA chapter (Chapter 6) triggers a dedicated congratulations screen with a tabbable Export Certificate button. Activating the button generates a styled HTML certificate, saves it to the user's Downloads folder with a personalized filename, and opens it in the browser. The certificate includes the student's name, date of completion, instructor, training program (if set), a heartfelt message, and Tony Gebhard's signature as Assistive Technology Instructor. Returning users who have already completed the course see the cert button appear automatically when the add-on loads. The completion screen includes step-by-step instructions for printing or saving as PDF.
- **Final course completion screen:** Completing the last lesson of Chapter 6 now replaces the standard idle screen with a full-page heartfelt congratulations message. It lists all six chapters mastered, displays personalized instructor and training program information if set, and guides the student to the certificate export button.

### Content

- **Chapter reordering:** "Your Keyboard" (previously Chapter 6) is now Chapter 2, immediately following Getting Started. This gives students physical keyboard orientation — modifier keys, function keys, Fn behavior, layout selection — before any command learning begins. "Customizing NVDA" (previously Chapter 5) is now the final chapter (Chapter 6), serving as the natural course conclusion that triggers the certificate.

---

## v1.4 (2026-04-07)

### Bug Fixes
- **Practice frame button feedback corrected:** The "Play a beep sound" button in the practice frame announced "Beep! You activated the button with Enter" — but the button responds to both Enter and Space (standard Windows button activation). The message now says "Beep! You activated the button." Reported by AT specialists during Pacific Northwest training sessions.

### New Lesson Content
- **New lesson: Understanding Your Keyboard** (Chapter 1, Lesson 12) — Physical keyboard reference covering Ctrl key location variants (some laptops place Fn at bottom-left instead of Ctrl), Fn+Arrow keys as Home/End/Page Up/Page Down on compact keyboards, and multimedia vs F-key toggling with Fn Lock.
- **New lesson: Switching Windows with Alt+Tab** (Chapter 1, Lesson 13) — Dedicated lesson covering both Alt+Tab patterns: single Alt+Tab to toggle between two windows, and hold-Alt tap-Tab to cycle through multiple windows and land on the target.
- **New lesson: Navigate by Paragraph and Page** (Chapter 2, Lesson 7) — Ctrl+Up/Down Arrow for paragraph navigation (Windows command), Page Up/Page Down for large document jumps (Windows command). Includes inline practice text with labeled paragraphs.
- **New lesson: Navigate Tables** (Chapter 3, Lesson 10, new chapter complete) — Web table navigation with Ctrl+Alt+Arrow keys (NVDA commands), what NVDA announces when entering a table, and command category context distinguishing NVDA, Windows, and application commands.
- **New Chapter 6: Your Keyboard** — Three-lesson chapter covering modifier key locations, function key and Fn key behavior, and NVDA desktop vs laptop layout selection. Addresses consistent instructor feedback that keyboard orientation is a barrier before command learning begins.

### Lesson Content Changes
- **Object Navigation — terminology:** "Parent object" and "child object" language replaced throughout with levels/pyramid metaphor ("object one level above," "object one level below," "level below," etc.) and a pyramid framing in the chapter intro. Recommended by Pacific Northwest AT specialists.
- **Object Navigation — maximize window tip:** Added prominent instruction to maximize the current application window (Windows+Up Arrow) before using object navigation. Now appears in the chapter intro and the "When Object Navigation Helps" lesson.
- **Object Navigation — NVDA+Tab distinction:** Added explicit explanation that NVDA+Tab reads the keyboard-focused control while object navigation moves independently of focus — two separate systems.
- **Object Navigation — lesson titles:** "Move to Parent and First Child" renamed to "Move Up and Down Levels" to match the revised terminology.
- **Browse Mode — Toggle Single-Letter Navigation lesson removed:** Per instructor feedback that the lesson's purpose was unclear and potentially confusing. Students discover single-letter navigation through practice.
- **Browse Mode — Focus Mode lesson enhanced:** Added explicit statement that "focus mode puts the cursor in the edit box" — a common point of confusion flagged by instructors.
- **Text Selection lesson — command categories:** Added explicit [Windows command] labels for Shift+Arrow selections, Ctrl+C, Ctrl+V, and Ctrl+A. Added [NVDA command] label for the new report-selection step.
- **Report highlighted text step added:** New step in the Select and Highlight Text lesson teaches NVDA+Shift+Up Arrow (desktop) and NVDA+Shift+S (laptop) to have NVDA read back the current selection before copying. Requested by Pacific Northwest AT specialists.
- **Command category labels — all five chapters:** Added [NVDA command] and [Windows command] inline labels throughout all lesson files where commands are introduced. Building on the "Understanding Command Categories" lesson established in v1.2.0.
- **Getting Started — lesson 11 closing text:** Updated to indicate two additional lessons remain (keyboard orientation and Alt+Tab) rather than declaring chapter complete at lesson 11.
- **Customizing NVDA — command labels:** Added clarifying labels (NVDA command, Windows command) to NVDA menu navigation steps and synth settings ring steps.

### New Translation
- **Turkish localization** — Full Turkish translation contributed by Umut KORKMAZ (umutkork@gmail.com, Turkey): all lesson chapters, UI strings, and documentation. (Integration pending receipt of final files.)

### Acknowledgments
- **Chris, Mike, Kevin, Julie, Larry, Jim, McKayla, and Skyler** — assistive technology specialists with Pacific Northwest state agencies, whose hands-on feedback from April 1–2, 2026 training sessions drove the majority of changes in this release.
- **Umut KORKMAZ** (umutkork@gmail.com, Turkey) — Turkish translation.

---

## v1.3.2 (2026-03-29)

### Bug Fixes — Localization
- **`addonHandler.initTranslation()` added to both plugin modules:** This call was missing from `__init__.py` and `lessonRunner.py`, which meant all `_()` wrapped strings silently fell back to English regardless of the user's NVDA language. Translation was structurally in place but never activated. Identified by Valentin Kupriyanov.
- **Dialog title now translatable:** The lesson picker window title ("NVDA Coach — Choose a Lesson") was not wrapped in `_()`.
- **Introduction / About NVDA Coach text now translatable:** The full introduction text shown when a user selects "Introduction / About NVDA Coach" from the lesson picker was not wrapped in `_()`.
- **Welcome screen text now translatable:** The initial welcome text displayed in the Coach window on first launch was not wrapped in `_()`.
- **`showIdle()`, `showBrowseModeCompletion()`, and `beginEscapeSequence()` text blocks now translatable:** These display strings were bare Python string literals with no `_()` wrapper.
- **Language-aware doc file resolution:** The resources page, browse mode practice page, and user guide (readme.html) were hardcoded to open from `doc/en/` regardless of the user's language. A new `_localizedDocPath()` helper now resolves to `doc/{lang}/` first, falling back to `doc/en/`. Identified by Valentin Kupriyanov.

### New Translation — Russian
- **First complete Russian localization of NVDA Coach**, contributed by Valentin Kupriyanov, Head of the Russian-speaking NVDA user community (nvda.ru):
  - `locale/ru/LC_MESSAGES/nvda.po` — full translation of all UI strings
  - `locale/ru/manifest.ini` — localized add-on summary and description
  - `globalPlugins/nvdaCoach/lessons/ru/` — all five lesson chapters translated into Russian
  - `doc/ru/` — practice page, user guide, resources page, and TTS scripts translated into Russian

### Acknowledgments
- Valentin Kupriyanov, Head of the Russian-speaking NVDA user community — first complete Russian localization of NVDA Coach, and detailed localization bug report identifying all issues fixed in this release

---

## v1.3.1 (2026-03-28)

### Bug Fixes / Patch
- **Localization scaffolding added:** `locale/nvda.pot` (101-string translation template), `locale/en/LC_MESSAGES/nvda.po` (English base file), and `TRANSLATING.md` (contributor guide) were missing from v1.3. The `_()` wrapping was in place but translators had no `.pot` file to work from and no `locale/` folder structure. Issue identified by Rui Fontes of the NVDA Portuguese translation team.

### Acknowledgments
- Rui Fontes, NVDA Portuguese translation team — identified missing `.pot` file and `locale/` folder structure

---

## v1.3 (2026-03-28)

### New Features
- **Localization infrastructure:** Lesson content is now organized into language subfolders (`lessons/en/`). NVDA Coach automatically detects the active NVDA language using `languageHandler.getLanguage()` and loads lessons from the matching subfolder (e.g. `lessons/fr/` for French, `lessons/pt/` from `pt_BR`), falling back to `lessons/en/` when no translation is available. Translators can contribute localized lesson sets by adding a language folder — no code changes required. Proposed by Valentin Kupriyanov, Head of the Russian-speaking NVDA user community.
- **Full i18n string wrapping (`__init__.py` and `lessonRunner.py`):** All user-facing strings in the add-on code are now wrapped with `_()` for gettext translation. This covers button labels, status bar text, spoken announcements, hint output, lesson picker UI, practice frame headings and feedback messages, and all `ui.message()` calls throughout both plugin files. Combined with the lesson folder architecture, this provides the complete foundation for community-contributed localizations.

### Acknowledgments
- Valentin Kupriyanov, Head of the Russian-speaking NVDA user community — internationalization and localization architecture proposal

---

## v1.2.2 (2026-03-28)

### Bug Fixes
- **Synth settings ring — Customizing NVDA chapter:** The lesson previously stated that NVDA+Ctrl+Right/Left Arrow changes speech speed. This is incorrect. NVDA+Ctrl+Right/Left Arrow navigates between synth settings ring items (Rate, Pitch, Volume, Voice, Variant). Speech speed (Rate) is increased with NVDA+Ctrl+Up Arrow and decreased with NVDA+Ctrl+Down Arrow. Both desktop and laptop layouts documented throughout. Reported by Brandon Patterson.

### New Features
- **F2 hint cycling:** Pressing F2 during a lesson now cycles through up to three hints per step, announced as "Hint 1 of 3", "Hint 2 of 3", etc. The hint index resets automatically when advancing to the next step. Falls back gracefully to the legacy single-hint string format for any steps that use it. Previously, many steps returned "no hint available."
- **All steps fully hinted:** Every step across all five chapters and 35 lessons now has a hints array covering key location, finger placement, and real-world context. Previously only gesture steps had hints; info steps had none.
- **Full cross-chapter connectivity:** Every chapter's final lesson now names the next chapter and references earlier lessons where relevant. Key chapters cross-reference each other — e.g., the synth settings ring step references the Tab navigation lesson from Getting Started; the chapter complete screens name the next chapter explicitly.

### Acknowledgments
- Brandon Patterson — synth settings ring keystroke correction
- Valentin Kupriyanov, Head of the Russian-speaking NVDA user community — internationalization and localization proposal (logged for a future release)

---

## v1.2.1 (2026-03-27)

### Bug Fixes
- **Object Navigation — laptop layout:** Four laptop layout gestures were missing the Shift key. Moving to the next and previous object at the same level is NVDA+Shift+Right/Left Arrow; moving to parent and first child is NVDA+Shift+Up/Down Arrow. Without Shift, those keystrokes invoke review cursor movement (by character/line) instead of object navigation. Reported and verified via NVDA input help by John Hess, AT Specialist, State Services for the Blind, Saint Paul, MN.
- **Say All lesson — laptop layout:** The lesson previously showed only the desktop layout keystroke (NVDA+Down Arrow). Laptop layout users press NVDA+A. Both layouts are now documented in the lesson intro, practice step, and chapter summary. Reported by an anonymous community member using laptop layout.

### Audio
- Lesson complete sound volume raised by 15%.

### Documentation
- README.md, CHANGELOG.md, and doc/en/readme.html updated in tandem.
- Acknowledgments updated to include John Hess and anonymous contributors.

---

## v1.2.0 (2026-03-21)

### New Lesson Content
- **New lesson: Understanding Command Categories** — added as Lesson 1 of Chapter 1 (Getting Started). Four steps teach learners to distinguish Windows commands, program/application commands, and screen reader commands before any command practice begins. Key framing: screen reader commands take no action — they only inform. (#006 — Brian)

### Lesson Content Changes
- **Removed all inline command labels** — all `[NVDA command]`, `[NVDA browse mode key]`, `[NVDA feature]`, and `[Universal shortcut]` tags stripped from every step across all five lesson files (28 instances). The Understanding Command Categories lesson carries this pedagogical weight instead, trusting learners to apply the framework themselves. (#006 — Brian)

### Sound and Audio
- **Sound branding overhaul** — all five sound moments (lesson start, step advance, hint, lesson stop, lesson complete) replaced with custom WAV audio files. The sound toggle in NVDA Settings disables all of them.

### New Features
- **NVDA Coach Help in the NVDA Help menu** — NVDA menu → Help → NVDA Coach Help opens the user guide directly. (#008 — Jessica Tegner)
- **Chapter navigation keys** — Ctrl+N (next lesson), Ctrl+B (previous lesson), Ctrl+R (restart current lesson) added to the Coach window.

---

## v1.1.0 (2026-03-19)

### Bug Fixes
- **"Try it now" prompts now spoken aloud** — gesture steps now include the "Try it now. When you are ready to continue, press Enter" cue in the spoken announcement, not just in the on-screen text (#004 — Darrell Hilliker)
- **Enter key advances after lesson completion** — in the idle/between-lesson state, pressing Enter or Numpad Enter now moves to the next lesson, consistent with other key behaviors (#003 — Darrell Hilliker)
- **Practice windows no longer open unexpectedly** — the Tab Navigation, Activate Controls, and Find Out Where You Are lessons now show a priming step first, giving users the Alt+Tab reminder before the practice window appears (#003 — Darrell Hilliker)

### New Features
- **Sound toggle** — NVDA Settings panel added (NVDA menu > Preferences > Settings > NVDA Coach) with a "Play sounds during lessons" checkbox; all coaching chimes respect this setting (#002 — Gene)

### Lesson Content
- **NVDA vs. Windows labels** — all lesson step instructions now include a `[NVDA command]`, `[NVDA browse mode key]`, or `[Universal shortcut]` label so learners understand which commands are specific to NVDA and which work in any Windows application (#002 — Gene)
- **"Why" framing** — all lessons updated with sighted-equivalent context (e.g., "Sighted users can glance at the title bar. NVDA+T speaks it to you.") (#002 — Gene)
- **New chapter: Object Navigation** — 6 lessons covering the NVDA object tree, moving to next/previous/parent/child objects, reading and examining objects, and routing keyboard focus to inaccessible controls (desktop and laptop layout keys documented throughout) (#001 — Joseph)
- **New chapter: Customizing NVDA** — 2 lessons on changing keyboard layout (desktop vs. laptop) and adjusting speech rate and voice (#001 — Joseph)
- **Browse Mode lesson 9: Find Text on a Page** — NVDA+Ctrl+F, NVDA+F3, NVDA+Shift+F3 (#001 — Joseph)
- **Browse Mode lesson 10: Toggle Single-Letter Navigation** — NVDA+Shift+Space (#001 — Joseph)

### Hotkey Conflict Note
The default gesture `NVDA+Shift+C` conflicts with Excel's "set column headers" command. Users can remap it via NVDA menu > Preferences > Input Gestures > NVDA Coach (#001 — Joseph)

---

## v1.0.0 (2026-03-14)

Initial release. Three chapters covering Getting Started, Reading and Moving Through Text, and Browse Mode and Web Navigation. 24 lessons total.
