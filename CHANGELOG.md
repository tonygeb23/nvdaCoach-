# NVDA Coach — Changelog

## Unreleased (after v1.7.0)

### Translations
- **Japanese, by Katsutoshi Tsuji (pull request #15).** The six original Japanese chapters now carry the 1.6.0 factual corrections: heading levels 1 to 9, the practice checkbox named as the interface names it, the Menu key in the right place, the Windows logo described by touch, and hints that test a key with Input Help instead of asking the student to look at it.
- **Simplified Chinese, by Cary Rowen (pull request #14).** A revision of every Simplified Chinese lesson, the manual, both practice pages, the interface strings and the store listing, with terminology made consistent across all of them. Merged by hand onto 1.7.0. The one change not taken was to the English lesson, which stays at heading levels 1 to 9; the Simplified Chinese text was changed from 6 to 9 to match NVDA.
- **The practice window titles can now be translated**, from the same pull request. Simplified Chinese has them, and the Polish titles Michał Dziwisz wrote in April (pull request #7) are in use for the first time.
- **Pull requests #7 (Polish, Michał Dziwisz), #10 (Simplified Chinese, Cary Rowen) and #12 (Traditional Chinese, keyang556) are now merged in the repository's history.** Their work had been copied into earlier releases without the pull requests being merged, so the contributors' commits were missing from the record. Checked entry by entry before merging: every Polish and Traditional Chinese string in those pull requests is already in the add-on unchanged, and #10 is superseded by Cary Rowen's own #14.

### Credit
- Cary Rowen and keyang556 were not named anywhere in the add-on or the README. They are now, in the README, the English manual, their own language's manual, and the translator line of their catalogues. Katsutoshi Tsuji and Michał Dziwisz were missing from the English manual's acknowledgments and have been added.

## v1.7.0 (2026-11-23)

### New lessons
- **Chapter 7, Add-ons and the Add-on Store: 11 lessons, 48 steps.** What add-ons are and why nobody vets them; opening the store and the first-time warning; the four tabs and the layout of each; searching, the Channel filter and sorting; reading the description, Other details, Community reviews and VirusTotal results before installing; installing and restarting; updating, disabling and removing; add-on files, incompatible add-ons, and restarting with add-ons disabled. Wording, tab names, action names, access keys and status text were taken from the NVDA 2026.3.1 user guide and source, not from memory.
- **Three of those lessons tour 25 of the most downloaded add-ons.** The Add-on Store publishes no usage figures, so the ranking is total GitHub release downloads for every stable add-on the store offers for NVDA 2026.3, counted on 2026-11-22 (581 add-ons counted; 10 are hosted elsewhere and could not be). The lessons say how the list was made and that download counts favour add-ons that update often. BluetoothAudio ranked 21st on downloads but is not offered for NVDA 2026.3, so it was left out and Outlook Extended took the 25th place. Where NVDA now does a similar job itself (sentence navigation, Remote Access, math, OCR, repeating the last speech) the lesson says so.
- **Chapter 8, Using a Braille Display: 8 lessons, 34 steps, optional.** Connecting over USB and Bluetooth, automatic detection and `NVDA+Ctrl+A`; scrolling and line movement; the braille cursor and routing keys; output and input tables; tethering (`NVDA+Ctrl+T`), braille mode (`NVDA+Alt+T`) and speech modes (`NVDA+S`); control abbreviations; braille keyboard input; message, text wrap and paragraph settings. Display-specific keys are not taught, because they differ by model; the lessons teach the command names and send the student to their display's section of the user guide and to Input Help.
- **Optional chapters.** A chapter with `"optional": true` in its JSON does not count toward the certificate, is labelled "optional" in the lesson picker, and is listed on the completion screen only if the student finished it. Only a real boolean `true` counts.
- The course is now 64 lessons in English: 56 required and 8 optional. **The Add-on Store chapter is required**, so a student who finished 1.6.0 needs it before the certificate is offered again.
- **Drafted in all eight other languages, pending native review.** Spanish, Japanese, Polish, Brazilian Portuguese, Russian, Turkish, Simplified Chinese and Traditional Chinese each have both chapters, the two manual sections, and the new interface strings. The drafts are machine-assisted. Interface names and access keys were taken from NVDA 2026.3.1's own translation for each language, and add-on names from the Add-on Store in that language; where NVDA's translation gives a control no access key, or gives two controls the same one, the lesson teaches Tab instead. None of it has been read by a native speaker or tried in NVDA in that language. What each translator should look at first is in `translators/REVIEW-NOTES-1.7.0.md`. The twenty factual corrections to the six original chapters are still English only.

### NVDA 2026.3.1
- `lastTestedNVDAVersion` is 2026.3.1. NVDA Coach 1.6.0 already loaded cleanly on NVDA 2026.3.1rc1 (checked in a live NVDA log), and none of the APIs deprecated in 2026.2 or 2026.3 are used by the add-on.
- All 45 existing English lessons (165 steps, 495 hints) and the English manual were checked against the NVDA 2026.3.1 user guide and change log. Nothing had gone stale between 2026.1.1 and 2026.3.1; the 20 findings were errors of longer standing. All are corrected in English and written up for translators in `translators/FACTUAL-CORRECTIONS-1.7.0.md`. The ones that mattered most:
  1. **Read current line was taught with the desktop key only.** On laptop layout `NVDA+Up Arrow` reads the line above; the key is `NVDA+L`.
  2. **"Most laptops use laptop layout."** NVDA starts on desktop layout on every computer.
  3. **Caps Lock was presented as an NVDA key that already works.** By default only the two Insert keys are.
  4. **Focus mode and browse mode were said to be spoken.** By default NVDA plays a sound for each.
  5. **Num Lock was never mentioned,** and every desktop object navigation command needs it off.
  6. **The Elements List was described as tabs you Tab between.** It has Type radio buttons, and Enter activates a link rather than moving to it.
  7. **A Synthesizer combo box in the Speech category,** which does not exist, and eSpeak NG as the default voice, which it is not on Windows 10 and 11.
  8. **"Saved when you press OK"** in the same step that taught `NVDA+Ctrl+R`, which would undo it.
- New commands from 2026.2 and 2026.3 are mentioned where they fit: `NVDA+X` to repeat the last speech, `Alt+C` in the Formatting window, and the Undo offered after a menu reset to factory defaults.

### Fixed
- **The Certificate of Completion could not be exported in 1.6.0.** The 1.6.0 change that escaped names for HTML used `html.escape()` in a function that also assigned to a local variable called `html`, so every export raised `UnboundLocalError` and the student was told to check their Downloads folder. Reproduced against the released 1.6.0 code and covered by a test.
- **The certificate button appeared after one chapter.** At start-up the add-on still asked only whether Customizing NVDA was complete, while the completion screen asked about the whole course.
- **The certificate finds the real Downloads folder,** asking Windows instead of assuming `~/Downloads`, which OneDrive moves.
- **The practice browser is closed in every language.** The window was matched against the English page title; it is now matched against the title of the page that was opened.
- **A practice page that fails to open is announced.**
- **Escape in the first 600 ms of a lesson** no longer leaves NVDA announcing that the lesson is starting after saying it stopped.
- **Two interface translations lost in 1.6.0 are back.** The welcome text and the gesture description were reworded in 1.6.0 without resyncing the catalogues, so they had been showing in English in every language. `tools/sync_locales.py` now does that step and carries translations across a rewording.

### Tooling
- `tests/test_coach.py`: 25 tests that run the add-on's own code outside NVDA with stand-in NVDA modules and real wxPython. One walks all 64 lessons through the real lesson runner, and another does the same for every language. Nothing is shown, spoken, or focused.
- `tools/sync_locales.py`: regenerates the template, merges every catalogue, and compiles `.mo` files.
- `tools/validate_addon.py`: knows the two new chapters, warns for a language that does not have them, and fails if any chapter other than braille is marked optional.

### Not verified
- **Run inside NVDA in English only.** 1.7.0 was installed on NVDA 2026.3.1rc1 on 2026-11-23 and loads without errors in the NVDA log, and Tony tried it there before release. The translated chapters have not been run in NVDA in their own languages.
- Still open from `reviews/1.6.0-deferred.md`: Escape inside a lesson stops it without asking; Enter means two things in the browse mode chapter; settings are stored per configuration profile.

## v1.6.0 (2026-09-20)

### Localization
- **Japanese (ja):** A complete Japanese localization — all six chapters and 45 lessons, every interface string, and the Add-on Store description. Terminology follows NVDA's own Japanese translation, including 音声エンジン for the synthesizer and 簡単音声設定 for the settings ring rather than transliterations. The user guide page (`doc/ja/readme.html`) and the store listing (`locale/ja/manifest.ini`) were assembled from the translator's own wording in the lessons and interface strings rather than translated afresh from English.
- **Polish (pl):** A complete Polish localization — six chapters, interface strings and documentation. The store listing was expanded from a single sentence to the full description the other languages carry, built from the translator's own documentation page; his summary line and opening sentence are unchanged.
- **Traditional Chinese (zh_TW) revised** throughout the lessons, documentation and interface.
- **Brazilian Portuguese (pt_BR) is a real translation for the first time.** The folder has existed since 1.5.1 and shipped as an English copy: lesson content 98.9% byte-identical to English, and not one of the 204 interface strings translated. Two of its chapters were copies of an *older* English revision, and the audio output and audio ducking lessons had never been carried over at all, leaving it at 44 lessons. It is now the full 45, in Portuguese, with terminology taken from NVDA's own Brazilian Portuguese translation. The existing store listing by Edson Miranda is unchanged; the completion is machine-assisted and marked as pending his review.
- **Every translation catalogue resynced.** All nine now carry exactly the same 204 message ids as the regenerated template, with existing translations preserved byte for byte and new strings added as empty entries.
- **Translator worksheets** in `translators/`. When an English string is edited rather than added, gettext treats it as new and orphans the old translation, so the translator opens the file and finds an empty box with no sign they already translated nine tenths of that sentence. Each worksheet now pairs every owed string with that translator's own earlier version and marks what changed in the English.

### Corrections — commands NVDA Coach taught that NVDA does not have
Every item below was checked against NVDA's own Commands Quick Reference and user guide. All ten are corrected in English and written up for translators in `translators/FACTUAL-CORRECTIONS-1.6.0.md`; items 1 and 2 are corrected in every language.

1. **The laptop command for reading the current object was a key that does not exist.** The lessons taught `NVDA+Shift+Comma`; NVDA binds `NVDA+Shift+O`. `NVDA+shift+comma` appears nowhere in NVDA and is bound to nothing. A student on a laptop pressed it, nothing happened, and nothing told them why — in the lesson whose whole purpose is teaching that laptop layout differs from desktop. Every translator had faithfully translated the error, so it was wrong in all nine languages, in the lessons and in six documentation pages. The sentences that existed only to say where the comma key was have been rewritten to describe the O key.
2. **`NVDA+Ctrl+U` was described as an audio output device picker** that opened "without opening the Settings dialog". It opens the Audio category *of* the NVDA Settings dialog, and has since 2024.1 — the add-on's own minimum version.
3. **A "Reset to defaults" button in the Speech settings category.** No such button exists; the dialog has OK, Cancel and Apply. Resetting is `NVDA+Ctrl+R`.
4. **Heading quick navigation was taught as 1 to 6.** NVDA supports levels 1 to 9.
5. **The audio ducking option was named "Duck While Speaking".** NVDA's option is Audio Ducking Mode.
6. **A lesson 7 of 8 was announced as the last in its chapter.** The following lesson then correctly said one more remained.
7. **A practice checkbox was named "Show practice hints"** in the lesson; the control says "Show practice hints during lessons". For a student matching what they hear against what they were told to find, a partial match is a dead end.
8. **The Menu key was placed "on the left side".** The Applications key is on the right, next to the right Control key.
9. **The NVDA key was described as "one of two options".** NVDA offers three: Caps Lock, Insert, and numpad Insert.
10. **Two cross-references to a "Moving Between Controls" lesson** that does not exist. The lesson is "Move Between Controls with Tab".

### Caught in review, before release
Two adversarial passes over the built package found these. They are listed because they were real and are fixed, not because they shipped.

- **Finishing one chapter announced the whole course complete.** The check looked only at the Customizing NVDA chapter, because that chapter is last. Several earlier lessons point students into it mid-course, so somebody following the add-on's own advice finished four lessons out of forty-five and was told "you have finished every lesson in NVDA Coach" — with a certificate saying the same. A student who cannot see the lesson picker has no way to notice it disagreeing with the speech. Now gated on every chapter.
- **One malformed lesson file took out all nine languages.** The sort that orders chapters read `.get("order")` outside the per-file error handling, so a chapter whose top level was a list, or two chapters whose `order` values were a string and an int, raised out of the plugin's constructor. NVDA only logs that, so the add-on silently failed to load for everybody with nothing spoken. A translator hand-editing one JSON file is the obvious way in, and this release added two languages by hand.
- **A locked or truncated progress file silently destroyed a student's history.** The loader caught everything and returned an empty result, which cannot tell "no file yet" from "the file is there and I could not read it", and the next completed lesson wrote an almost empty file over the top. Saving also truncated the real file before writing it. Progress is the only thing in this add-on that cannot be rebuilt: it is now written beside the original and moved into place in one step, a file that will not parse is moved aside rather than overwritten, and a file that is valid JSON but not an object no longer stops the add-on loading.
- **A bulk text pass had rewritten a lesson identifier in Turkish.** `activate_controls` became `activate_Kontrols`. The practice-window registry is keyed on the identifier, so it never matched: Turkish students on that lesson were told to go to the practice area and no window opened, with nothing spoken. Present since before 1.5.7.
- **NVDA could not reach any of the nine manuals we ship.** Without `docFileName` in the manifest, the Add-on Store's Help button is disabled outright. Added.
- **The welcome screen every new user reads pointed at a 404.** `github.com/tonygeb23/nvdacoach` does not exist; the repository is `nvdaCoach-`.
- **Turkish gesture identifiers had been machine translated** — 44 of them, `kb:sag tamam` in place of `kb:rightArrow` and the like. Those fields are not read by any code today, so nothing was broken; they are fixed because the day gesture checking is wired up, every Turkish lesson would fail silently.
- **Three of the ten corrections above were only half applied** when first made: the heading-level instruction still said 1 to 6 while its own hint said 1 to 9, the audio ducking modes still used names NVDA does not speak, and the `NVDA+Ctrl+U` step still described the picker dialog its own instruction had just stopped describing. All finished, and the release checks now sweep for the concept rather than for the one string that was replaced.
- **The audio output lesson never warned that it can silence NVDA.** Choosing a device that makes no sound leaves a blind student with no speech and no way to hear their way back. The lesson now says so, tells them to note the working device first, and gives them `Ctrl+Alt+N`.
- **The audio ducking lesson blamed the sound card for something else entirely.** `isAudioDuckingSupported()` returns `config.isInstalledCopy()`, so on a portable copy of NVDA the command does nothing at all — common in a training centre or a library. The lesson sent those students off to suspect their audio driver.

### Accessibility
- **NVDA Coach no longer takes `NVDA+Shift+C` away from NVDA in Excel.** NVDA binds that key to "set column headers", and scripts on a global plugin are resolved before scripts on the focused object — so installing NVDA Coach silently removed an NVDA command, inside a table, which is exactly where the add-on's own table lesson sends the student. The Coach now hands the gesture back in Excel, where `ExcelCell.script_setColumnHeader` does real work.

  **Word is deliberately not included.** The first version of this fix handed the key over anywhere the focused object had a `script_setColumnHeader` attribute. Word has one that looks identical from the outside and is a stub whose entire body speaks "Command not supported in this type of document" — and it lives on `WordDocument`, not on a table cell, so it answers everywhere in every Word document and every Outlook message body. That version would have cost the student the only way into the Coach and handed them a refusal in exchange, which is worse than the conflict it was meant to fix. Caught in review before release.

  Input Help now carries the exception too, since the course teaches Input Help as the thing to trust when you are lost. If the hand-off fails for any reason it falls through to opening the Coach, because this gesture is the add-on's only way in.
- **Hong Kong, Macau and European Portuguese no longer fall back to English.** NVDA supplies a full locale such as `zh_HK`; the base-language step reduced it to `zh`, no `zh` folder exists, and the reader dropped to English while a complete Traditional Chinese set sat unused in the add-on. `zh_HK` and `zh_MO` now resolve to Traditional Chinese, `pt_PT` and a bare `pt` to Brazilian Portuguese. The lesson loader and the documentation lookup now share one resolver so they cannot disagree about which language a user is getting.
- **The untranslated lesson-title fallback** in `lessonRunner.py` is now translatable. The same fallback two hundred lines further down already was.

### Internal
- Translation template regenerated from source: 204 strings, up from 203.
- Every `.mo` recompiled from its `.po`.
- Version stated in the add-on manifest, the build script and seven documentation pages, all of which had drifted — the English page still said 1.5.4, Spanish and Polish 1.5.1, Russian 1.5.

---

## v1.5.7 (2026-07-12)

### Localization
- **Chinese (Simplified) translation (zh_CN):** All six lesson chapters (45 lessons, 165 steps), all UI strings, all three HTML documentation files (user guide, practice page, resources), and the Add-on Store description are now available in Simplified Chinese. Users who set NVDA's language to 中文（简体） receive fully localized lesson content, documentation, and interface strings. Terminology follows NVDA's own Simplified Chinese conventions (浏览模式, 对象导航, 台式机/笔记本布局); keyboard command combos remain in Latin (NVDA+Shift+C) with descriptive key names in Chinese (上箭头, 空格键, 小键盘 5).
- **Chinese (Traditional) translation (zh_TW):** A complete Traditional Chinese localization for Taiwan is now included — the same six chapters, UI strings, documentation, and store description. Terminology follows Taiwan NVDA conventions (螢幕閱讀器, 物件導航, 核取方塊, 自訂, 附加元件, 回饋, 檢閱游標); it is a full Traditional conversion, not a character-swap of the Simplified text.
- **Chinese lessons adapted, not just translated:** The reading-practice passages in Chapter 3 were rewritten as natural Chinese prose that keeps every structural claim true (line counts, paragraph counts, first/last-line markers), with a note on how word-by-word navigation (Ctrl+arrows) behaves in Chinese text, which has no word spaces. The NVDA-settings lessons no longer teach first-letter jumps to the Keyboard/Speech categories — those jumps assume English category names — and use arrow-key navigation instead.

### Accessibility
- **Practice-window control labels are now translatable:** Every control label in the three practice environments — the Tab-navigation contact form, the checkboxes-and-buttons frame, and the login form (including the Username/Password field names announced by NVDA) — was hardcoded in English and could not be localized. All of them are now wrapped for translation and are fully localized in both Chinese variants, so students hear the same button and field names the lesson text tells them to find.

### Bug Fixes
- **Wrong next-chapter hint at the end of Getting Started corrected:** The final lesson's first hint said the next chapter was "Reading and Moving Through Text" when the actual next chapter is "Your Keyboard" — a leftover from the v1.5.5 pointer fix, which corrected the spoken instruction but missed the hint. Corrected in English, Spanish, Russian, and Brazilian Portuguese (Turkish and both Chinese variants were already correct).

### Internal
- **Translation template regenerated:** `locale/nvda.pot` had not been rebuilt since v1.5.1, so roughly 95 interface strings added since then (the certificate system, the profile dialog, completion and welcome-back messages, and the practice-window labels above) were missing from it and fell back to English in every language. The template now covers all 203 UI strings. Both Chinese variants translate the full set; the Spanish, Russian, Turkish, and Brazilian Portuguese catalogs have the new strings added as untranslated entries (English fallback, unchanged behavior) for their translators to complete.

---

## v1.5.6 (2026-07-11)

### Bug Fixes
- **F4 help documentation no longer opens a 404 page:** The help URL opened by pressing F4 twice was `https://tonygebhard.me/NVDACoach`, which returns 404 because the web server treats paths case-sensitively — the live page is `https://tonygebhard.me/nvdacoach/`. The URL has been corrected in the F4 handler, `manifest.ini`, and every readme/documentation file in all languages. Reported by Andrew Leland (#014), running NVDA Coach on macOS via Parallels.

---

## v1.5.5 (2026-06-03)

### Compatibility
- **NVDA 2026.1.1:** `lastTestedNVDAVersion` updated from 2026.1 to 2026.1.1, the current NVDA stable release. NVDA 2026.1.1 was a security and bug-fix patch (fixes to File Explorer Ctrl+F handling and Remote Access reconnection) with no API changes affecting add-ons — NVDA Coach required no code changes for compatibility.

### Accessibility
- **Instruction pane is now a RichEdit control:** The lesson instruction text area now uses a Win32 RichEdit control (`TE_RICH2`) instead of a plain edit control. A plain edit did not expose font and formatting information to NVDA+F, and did not support Ctrl+Up/Down paragraph navigation or reliable Page Up/Down — the practice-text lessons in Chapter 3 (Reading and Moving Through Text) depend on all three. Students can now use those commands directly on the lesson instruction text.

### Lesson Fixes
- **Chapter-completion ordering corrected (Reading and Moving Through Text):** The "you have completed the chapter" message previously appeared at the end of Lesson 7, before the chapter's actual final lesson — Lesson 8, *Check Font and Formatting*. The completion message now appears at the end of Lesson 8, and Lesson 8 is correctly flagged as the chapter's final lesson. Lesson 7 now points forward to the font and formatting lesson.
- **Next-chapter pointers corrected (Getting Started):** The end-of-chapter message directed students to "Reading and Moving Through Text" when the actual next chapter is "Your Keyboard" (Chapter 2). This has been corrected, and the Your Keyboard chapter-end message now points to Reading and Moving Through Text.
- **Laptop Fn-key location corrected (all languages):** The "Your Keyboard" chapter previously described laptops as having the Fn key "in the bottom-left corner, pushing Ctrl one key to the right," which is inaccurate on most hardware. Corrected across English, Spanish, Russian, Turkish, and the Portuguese scaffold: on most laptops the Fn key sits between the left Ctrl key and the Windows key (bottom row: Ctrl, Fn, Windows, Alt, space bar), while standard desktop keyboards have no Fn key in that row (Ctrl, Windows, Alt, space bar).
- **Getting Started practice hint reworded:** A hint that referenced Say All before it had been introduced now suggests practicing the Control and Shift speech keys in any application after the lesson.

---

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
- **Practice frame button feedback corrected:** The "Play a beep sound" button in the practice frame announced "Beep! You activated the button with Enter" — but the button responds to both Enter and Space (standard Windows button activation). The message now says "Beep! You activated the button." Reported by AT specialists during training sessions.

### New Lesson Content
- **New lesson: Understanding Your Keyboard** (Chapter 1, Lesson 12) — Physical keyboard reference covering Ctrl key location variants (some laptops place Fn at bottom-left instead of Ctrl), Fn+Arrow keys as Home/End/Page Up/Page Down on compact keyboards, and multimedia vs F-key toggling with Fn Lock.
- **New lesson: Switching Windows with Alt+Tab** (Chapter 1, Lesson 13) — Dedicated lesson covering both Alt+Tab patterns: single Alt+Tab to toggle between two windows, and hold-Alt tap-Tab to cycle through multiple windows and land on the target.
- **New lesson: Navigate by Paragraph and Page** (Chapter 2, Lesson 7) — Ctrl+Up/Down Arrow for paragraph navigation (Windows command), Page Up/Page Down for large document jumps (Windows command). Includes inline practice text with labeled paragraphs.
- **New lesson: Navigate Tables** (Chapter 3, Lesson 10, new chapter complete) — Web table navigation with Ctrl+Alt+Arrow keys (NVDA commands), what NVDA announces when entering a table, and command category context distinguishing NVDA, Windows, and application commands.
- **New Chapter 6: Your Keyboard** — Three-lesson chapter covering modifier key locations, function key and Fn key behavior, and NVDA desktop vs laptop layout selection. Addresses consistent instructor feedback that keyboard orientation is a barrier before command learning begins.

### Lesson Content Changes
- **Object Navigation — terminology:** "Parent object" and "child object" language replaced throughout with levels/pyramid metaphor ("object one level above," "object one level below," "level below," etc.) and a pyramid framing in the chapter intro. Recommended by AT specialists.
- **Object Navigation — maximize window tip:** Added prominent instruction to maximize the current application window (Windows+Up Arrow) before using object navigation. Now appears in the chapter intro and the "When Object Navigation Helps" lesson.
- **Object Navigation — NVDA+Tab distinction:** Added explicit explanation that NVDA+Tab reads the keyboard-focused control while object navigation moves independently of focus — two separate systems.
- **Object Navigation — lesson titles:** "Move to Parent and First Child" renamed to "Move Up and Down Levels" to match the revised terminology.
- **Browse Mode — Toggle Single-Letter Navigation lesson removed:** Per instructor feedback that the lesson's purpose was unclear and potentially confusing. Students discover single-letter navigation through practice.
- **Browse Mode — Focus Mode lesson enhanced:** Added explicit statement that "focus mode puts the cursor in the edit box" — a common point of confusion flagged by instructors.
- **Text Selection lesson — command categories:** Added explicit [Windows command] labels for Shift+Arrow selections, Ctrl+C, Ctrl+V, and Ctrl+A. Added [NVDA command] label for the new report-selection step.
- **Report highlighted text step added:** New step in the Select and Highlight Text lesson teaches NVDA+Shift+Up Arrow (desktop) and NVDA+Shift+S (laptop) to have NVDA read back the current selection before copying. Requested by AT specialists.
- **Command category labels — all five chapters:** Added [NVDA command] and [Windows command] inline labels throughout all lesson files where commands are introduced. Building on the "Understanding Command Categories" lesson established in v1.2.0.
- **Getting Started — lesson 11 closing text:** Updated to indicate two additional lessons remain (keyboard orientation and Alt+Tab) rather than declaring chapter complete at lesson 11.
- **Customizing NVDA — command labels:** Added clarifying labels (NVDA command, Windows command) to NVDA menu navigation steps and synth settings ring steps.

### New Translation
- **Turkish localization** — Full Turkish translation contributed by Umut KORKMAZ (umutkork@gmail.com, Turkey): all lesson chapters, UI strings, and documentation. (Integration pending receipt of final files.)

### Acknowledgments
- **Chris, Mike, Kevin, Julie, Larry, Jim, McKayla, and Skyler** — assistive technology specialists, whose hands-on feedback from the April 2026 training sessions drove the majority of changes in this release.
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
- **Object Navigation — laptop layout:** Four laptop layout gestures were missing the Shift key. Moving to the next and previous object at the same level is NVDA+Shift+Right/Left Arrow; moving to parent and first child is NVDA+Shift+Up/Down Arrow. Without Shift, those keystrokes invoke review cursor movement (by character/line) instead of object navigation. Reported and verified via NVDA input help by John Hess, AT Specialist.
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
