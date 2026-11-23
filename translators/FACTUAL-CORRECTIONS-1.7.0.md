# Factual corrections in NVDA Coach 1.7.0

Read this before translating or revising any of the six original chapters.

For 1.7.0 every English lesson was checked against the NVDA 2026.3.1 User
Guide. Twenty things the lessons taught were wrong. Most had been wrong since
before your language was added, so the error was translated faithfully. That
is not your mistake. Each one is listed here with the old English, the new
English, and the reason, so you can find the matching sentence in your file.

Nothing in your language's lesson files was changed for these. They are
corrected in English only, and your files keep the old statements until you
update them. No lesson, step or hint was added or removed in these six
chapters, so the structure of your files is still correct.

Two new chapters were also added in English: `addon_store.json` (11 lessons)
and `braille.json` (8 lessons, marked `"optional": true`, which must stay a
real `true` and must not be translated). A draft of both now exists in your
lessons folder. It is machine-assisted and has not been read by a native
speaker; `REVIEW-NOTES-1.7.0.md` says how it was made and what to check first.

Verified on 2026-11-22 against the User Guide installed with NVDA 2026.3.1rc1.

---

## getting_started.json

**Why:** The NVDA key is Insert unless Caps Lock has been switched on (User Guide, About NVDA keyboard commands). Read current line is NVDA+Up Arrow on desktop and NVDA+L on laptop; on laptop layout NVDA+Up Arrow reads the previous line. The battery report does not begin with the word Battery. F12 alone is not an NVDA command; the time is NVDA+F12. The Fn key never reaches NVDA, so Input Help cannot name it.

### 1.

Old English:

> On most keyboards it is the Insert key. On many laptops it is Caps Lock.

New English:

> Unless it has been changed, it is the Insert key. NVDA can also be set to use Caps Lock, which many laptop users prefer.

### 2.

Old English:

> On many laptops, Caps Lock serves as the NVDA key. It is on the far left of the keyboard, just above the left Shift key.

New English:

> Caps Lock can also serve as the NVDA key, but only if that was chosen in NVDA's Welcome dialog or in Keyboard settings. It is on the far left of the keyboard, just above the left Shift key.

### 3.

Old English:

> You can use both Insert and Caps Lock as NVDA keys at the same time. NVDA accepts either one, so you never have to choose between them.

New English:

> Once Caps Lock is switched on as an NVDA key, you can use Insert and Caps Lock interchangeably. If Caps Lock does not work as your NVDA key, it has not been switched on yet. Use Insert for now. The Your Keyboard chapter explains how to change it.

### 4.

Old English:

> NVDA will say something like "Battery: 74 percent, not charging" or "Battery: 91 percent, charging".

New English:

> NVDA reports the percentage of charge and whether the computer is plugged in, for example "74 percent" followed by "unplugged".

### 5.

Old English:

> On a desktop computer, NVDA may say nothing or report no battery found. Press Enter to continue.

New English:

> On a desktop computer, NVDA says there is no system battery. Press Enter to continue.

### 6.

Old English:

> "Not charging" means the charger is unplugged or the battery is full.

New English:

> NVDA may also tell you roughly how much time is left.

### 7.

Old English:

> NVDA+Up Arrow reads the current line — useful whenever

New English:

> On desktop layout, NVDA+Up Arrow reads the current line. On laptop layout, press NVDA+L instead. This is useful whenever

### 8.

Old English:

> NVDA plus Up Arrow reads the current line without moving your cursor.

New English:

> NVDA plus Up Arrow on desktop layout, or NVDA plus L on laptop layout, reads the current line without moving your cursor.

### 9.

Old English:

> Use NVDA plus Up Arrow whenever you lose track of where you are in a document — it re-reads the line your cursor is on without changing anything.

New English:

> Use this command whenever you lose track of where you are in a document — it re-reads the line your cursor is on without changing anything. In NVDA 2026.2 and later, NVDA plus X repeats the last thing NVDA said, whatever it was.

### 10.

Old English:

> Then press NVDA+Up Arrow to have NVDA read the current line aloud. Move to a different line with Up or Down Arrow and press NVDA+Up Arrow again to hear each one.

New English:

> Then press NVDA+Up Arrow on desktop layout, or NVDA+L on laptop layout, to have NVDA read the current line aloud. Move to a different line with Up or Down Arrow and press the command again to hear each one.

### 11.

Old English:

> then press NVDA plus Up Arrow to confirm which line you are on.

New English:

> then press NVDA plus Up Arrow on desktop layout, or NVDA plus L on laptop layout, to confirm which line you are on.

### 12.

Old English:

> If NVDA reads a line but you did not catch it all, just press NVDA plus Up Arrow again. You can press it as many times as needed to re-read the same line.

New English:

> If NVDA reads a line but you did not catch it all, just press the command again. If NVDA plus Up Arrow reads the line above instead of the current one, NVDA is set to laptop layout: use NVDA plus L.

### 13.

Old English:

> press F12 and NVDA will tell you it reads the time, without actually reading the time.

New English:

> hold your NVDA key and press F12, and NVDA will tell you that command reports the time, without actually reading the time.

### 14.

Old English:

> NVDA will name it. If it says Fn, Control is the next key to the right. If it says Control, you are already on it.

New English:

> If NVDA says left control, you are on Control. If NVDA says nothing at all, that key is Fn, because the Fn key is handled inside the keyboard and never reaches NVDA. Control is then the next key to the right.

### 15.

Old English:

> then press the bottom-left key. NVDA will tell you what it is.

New English:

> then press the bottom-left key. NVDA names it if it is Control, and stays silent if it is Fn.

---

## reading_text.json

**Why:** NVDA+Shift+S reports the selection on laptop layout but is sleep mode on desktop layout. NVDA+F pressed twice shows the same information as one press, in a window titled Formatting; Alt+C copies it in NVDA 2026.3 and later.

### 16.

Old English:

> use NVDA plus Up Arrow to re-read the current line.

New English:

> use NVDA plus Up Arrow on desktop layout, or NVDA plus L on laptop layout, to re-read the current line.

### 17.

Old English:

> Laptop layout: hold NVDA and Shift, then press the letter S to hear your current selection read back.

New English:

> Laptop layout: hold NVDA and Shift, then press the letter S to hear your current selection read back. If NVDA goes silent instead, you are on desktop layout, where this key turns on sleep mode for the current program. Press NVDA plus Shift plus S again to wake NVDA.

### 18.

Old English:

> Pressing NVDA+F once quickly reports the basic font name and size. Pressing NVDA+F twice in rapid succession opens a Font Formatting dialog that lists all formatting details in a browseable window — useful when there are many attributes to review. Try both: first a single press to hear the spoken report, then a quick double press to open the dialog.

New English:

> Pressing NVDA+F once speaks the formatting of the text at your cursor. Pressing NVDA+F twice quickly puts the same report in a window called Formatting, where you can read it line by line with the arrow keys — useful when there are many attributes to review. Escape closes that window, and in NVDA 2026.3 and later Alt+C copies the report. Try both: first a single press to hear the spoken report, then a quick double press to open the window.

### 19.

Old English:

> Single press: NVDA speaks the font name and size immediately. Double press: a dialog opens showing all formatting attributes, which you can read and close with Escape.

New English:

> Single press: NVDA speaks the formatting immediately. Double press: a window opens showing the same information, which you can read with the arrow keys and close with Escape.

---

## nvda_settings.json

**Why:** NVDA's default keyboard layout is desktop on every computer. Tab does not move between settings categories; Up and Down Arrow in the list, or Ctrl+Tab, do. The Speech category has a Change button that opens the Select Synthesizer dialog (NVDA+Ctrl+S), not a Synthesizer combo box. Windows OneCore is the default synthesizer on Windows 10 and 11. OK applies settings; they are written to disk when NVDA exits or with NVDA+Ctrl+C. Audio ducking is unavailable with SAPI 4 and 32-bit SAPI 5 voices. NVDA+Ctrl+K opens Keyboard settings, which is the reliable way to hear the current layout.

### 20.

Old English:

> Most desktop computers use desktop layout by default. Most laptops use laptop layout.

New English:

> NVDA starts on desktop layout on every computer, laptops included, unless laptop layout was chosen in NVDA's Welcome dialog or in Keyboard settings.

### 21.

Old English:

> Press Tab (Windows command) to move between settings categories or use the Arrow keys in the category list.

New English:

> Use the Up and Down Arrow keys in the category list to move between settings categories, or press Control+Tab (Windows command) from anywhere in the dialog to move to the next category. Pressing Tab moves from the category list into the settings themselves.

### 22.

Old English:

> Not sure which layout you are using? Press NVDA plus 1 to turn on Input Help, press a numpad key, and listen to what NVDA says. Then press NVDA plus 1 again to turn Input Help off.

New English:

> Not sure which layout you are using? Press NVDA plus Control plus K. Keyboard settings opens on the Keyboard layout box, and NVDA reads out Desktop or Laptop. Press Escape to close it.

### 23.

Old English:

> press Tab to move forward through sliders and combo boxes for rate, pitch, volume, inflection, voice, and synthesizer.

New English:

> press Tab to move forward through the Change button for the synthesizer, and then the combo boxes and sliders for voice, rate, pitch, volume, and inflection.

### 24.

Old English:

> NVDA includes the eSpeak NG synthesizer by default, which supports many languages and voices. If you have installed additional synthesizers — such as Windows OneCore voices or third-party options — you can switch between them in the Speech settings under the Synthesizer combo box.

New English:

> On Windows 10 and 11, NVDA speaks with Windows OneCore voices by default. The eSpeak NG synthesizer, which supports many languages, is also built in, and more synthesizers can be added with add-ons. To switch synthesizer, press NVDA+Control+S (NVDA command) to open the Select Synthesizer dialog, or press the Change button at the top of the Speech category.

### 25.

Old English:

> To switch synthesizers, open NVDA Settings, go to the Speech category, and find the Synthesizer combo box. Use arrow keys to choose a different synthesizer.

New English:

> To switch synthesizers, press NVDA plus Control plus S. In the Select Synthesizer dialog, use the arrow keys to choose a different synthesizer, then press Enter.

### 26.

Old English:

> NVDA saves them automatically when you close the settings dialog with OK. Your preferred rate, voice, and pitch will be active every time NVDA starts.

New English:

> pressing OK applies them straight away. NVDA then writes your settings to disk when it exits, or immediately if you press NVDA+Control+C (NVDA command) to save the configuration. After that, your preferred rate, voice, and pitch will be active every time NVDA starts.

### 27.

Old English:

> NVDA saves all speech settings when you press OK in the Settings dialog. Your preferences are restored every time NVDA starts.

New English:

> OK applies your settings at once. They are saved to disk when NVDA exits, or right away with NVDA plus Control plus C.

### 28.

Old English:

> once reverts to your last saved configuration, and three times restores factory defaults.

New English:

> once reverts to your last saved configuration, and three times restores factory defaults. The NVDA menu also has Reset configuration to factory defaults, and in NVDA 2026.2 and later that route offers an Undo button afterward.

### 29.

Old English:

> Both methods save your preferences.

New English:

> Both are saved when NVDA exits.

### 30.

Old English:

> The change takes effect immediately — you will hear NVDA begin speaking through the selected device right away. No restart is needed.

New English:

> The change takes effect when you press OK or Apply. No restart is needed.

### 31.

Old English:

> On an installed copy, if you hear no difference between modes, your audio driver may not support ducking.

New English:

> On an installed copy, if you hear no difference between modes, the usual cause is the synthesizer: ducking is not available with SAPI 4 voices or 32-bit SAPI 5 voices.

### 32.

Old English:

> On an installed copy it is usually the audio driver, which is common with some USB headsets and virtual audio devices.

New English:

> On an installed copy it is usually the synthesizer: ducking is not available with SAPI 4 voices or 32-bit SAPI 5 voices.

### 33.

Old English:

> Your preferred ducking mode is saved automatically and will be active every time NVDA starts.

New English:

> Your preferred ducking mode is saved with the rest of your settings when NVDA exits, and will be active every time NVDA starts.

---

## browse_mode.json

**Why:** By default NVDA plays a sound when it switches between focus mode and browse mode and does not speak the mode name (Browse Mode settings, Audio indication of focus and browse modes). The Elements List has Type radio buttons, a list, a Filter by box, and Activate and Move to buttons; Enter activates. A failed Find shows a dialog. NVDA says the number of columns before the number of rows, and the heading text before 'heading level'. Table navigation works wherever NVDA finds a table, not only on web pages.

### 34.

Old English:

> You will hear 'browse mode' announced when it activates.

New English:

> By default NVDA does not announce this. It simply starts reading the page.

### 35.

Old English:

> NVDA should announce the page title and 'browse mode' to let you know you are in a web page.

New English:

> NVDA should announce the page title and begin reading the page, which tells you that you are in a web page.

### 36.

Old English:

> You will hear 'focus mode' announced, and your cursor lands in the edit box ready to type.

New English:

> By default NVDA plays a short sound to mark the switch to focus mode, and your cursor lands in the edit box ready to type.

### 37.

Old English:

> NVDA will announce either 'focus mode' or 'browse mode' to tell you which one you are switching to.

New English:

> NVDA tells you which mode you have switched to. By default it does this with two different short sounds, one for focus mode and one for browse mode. If those sounds have been turned off in Browse Mode settings, NVDA says 'focus mode' or 'browse mode' instead.

### 38.

Old English:

> NVDA announces 'focus mode' or 'browse mode' to confirm which mode you switched to.

New English:

> NVDA plays a different sound for each mode, or speaks the mode name if the sounds are turned off.

### 39.

Old English:

> and listen for NVDA to announce the mode name.

New English:

> and listen for the sound, or the mode name, that tells you which mode you are in.

### 40.

Old English:

> NVDA announces the mode name each time you switch.

New English:

> NVDA signals the mode each time you switch.

### 41.

Old English:

> depending on which tab you are on.

New English:

> depending on which type you choose.

### 42.

Old English:

> Inside the Elements List, Tab moves between the category buttons at the top. Arrow keys move through the list of items. Enter jumps to the selected item on the page.

New English:

> The Elements List opens in the list of items, and arrow keys move through it. Shift plus Tab moves back to the Type radio buttons, where Up and Down Arrow choose links, headings, form fields, buttons, or landmarks. Alt plus M, the Move to button, jumps to the selected item on the page.

### 43.

Old English:

> Inside the dialog, press Tab to switch between viewing headings, links, form fields, and landmarks on the current page. Use the arrow keys to move through the list, and press Enter on any item to jump directly to it on the page.

New English:

> The dialog opens in a list of the links on the page. Press Shift+Tab to reach the Type radio buttons, and use Up and Down Arrow there to switch between links, headings, form fields, buttons, and landmarks. Press Tab to return to the list, and use the arrow keys to move through it. Press Alt+M, the Move to button, to jump to an item on the page. Pressing Enter instead activates the item, which for a link means following it.

### 44.

Old English:

> Inside the dialog, Tab moves between the category buttons: headings, links, form fields, buttons, and landmarks. Arrow keys then move through the items in the selected category.

New English:

> Shift plus Tab from the list reaches the Type radio buttons: links, headings, form fields, buttons, and landmarks. Tab returns to the list, where arrow keys move through the items of the chosen type.

### 45.

Old English:

> If no match is found, NVDA says 'not found'. Try a different search term or check your spelling.

New English:

> If no match is found, a small dialog tells you the text was not found. Press Enter to close it, then try a different search term or check your spelling.

### 46.

Old English:

> NVDA announces 'table with X rows and Y columns' so you know the size of the table.

New English:

> NVDA announces something like 'table with 3 columns and 4 rows' so you know the size of the table.

### 47.

Old English:

> NVDA announces 'table with X rows and Y columns' when you land on a table.

New English:

> NVDA announces something like 'table with 3 columns and 4 rows' when you land on a table.

### 48.

Old English:

> they only work when NVDA is running and you are in browse mode on a web page.

New English:

> they only work when NVDA is running. They work wherever NVDA finds a table, including Word documents as well as web pages.

### 49.

Old English:

> They do not work the same way outside of a web page table.

New English:

> They only do something when you are inside a table.

### 50.

Old English:

> is an NVDA command that only activates inside a table in browse mode.

New English:

> is an NVDA command that only activates inside a table.

### 51.

Old English:

> for example 'level 2 heading: Getting Started'.

New English:

> for example 'Getting Started, heading level 2'.

---

## keyboard_reference.json

**Why:** Caps Lock is not an NVDA key by default. To pass a real Caps Lock through, press it twice quickly. NVDA+Ctrl+K is the reliable way to hear the current layout; numpad keys in Input Help report the same command on both layouts.

### 52.

Old English:

> Your NVDA key can be Insert or Caps Lock.

New English:

> Your NVDA key is Insert unless you change it, and it can also be Caps Lock.

### 53.

Old English:

> Both can serve as your NVDA key at the same time — NVDA accepts either.

New English:

> Once Caps Lock is switched on in Keyboard settings, both can serve as your NVDA key at the same time.

### 54.

Old English:

> press NVDA plus F2 and then Caps Lock to actually toggle it when needed.

New English:

> press Caps Lock twice quickly to actually toggle it when needed.

### 55.

Old English:

> Both Insert and Caps Lock work as the NVDA key simultaneously. You do not have to choose —

New English:

> With Caps Lock switched on as an NVDA key, Insert and Caps Lock both work. You do not have to choose —

### 56.

Old English:

> If you are unsure which layout is currently active, press NVDA plus 1 to turn on Input Help, press a numpad key, and listen to what NVDA says. Press NVDA plus 1 again to turn off Input Help.

New English:

> If you are unsure which layout is currently active, press NVDA plus Control plus K. Keyboard settings opens on the Keyboard layout box, and NVDA reads out Desktop or Laptop. Press Escape to close it.

---

## object_navigation.json

**Why:** Numpad commands need Num Lock off (User Guide, Object Navigation). The navigator object follows the focus by default, so it does not start at the top of the hierarchy.

### 57.

Old English:

> and listen for the layout setting. Press Enter to continue.

New English:

> and listen for the layout setting. On desktop layout, Num Lock must be off for the numpad commands to work. If a numpad command types a number instead, press the Num Lock key and try again. Press Enter to continue.

### 58.

Old English:

> If you are not sure which layout you are using, press NVDA+1 (NVDA command) to turn on Input Help, then press one of the object navigation keys to hear which layout NVDA expects. Then press NVDA+1 again to turn Input Help off.

New English:

> If you are not sure which layout you are using, press NVDA+Control+K (NVDA command). Keyboard settings opens on the Keyboard layout box, and NVDA reads out Desktop or Laptop. Press Escape to close it.

### 59.

Old English:

> rather than starting from the top of the pyramid. Press Enter to continue.

New English:

> after the navigator object has wandered somewhere else. Press Enter to continue.

### 60.

Old English:

> to begin exploring from where you are rather than searching from the top of the pyramid.

New English:

> to bring the navigator object back to where your keyboard focus is.

---

## Interface strings

Four strings in the `.po` file are new or reworded: `optional`, the practice
page error message, `--- WHAT YOU HAVE LEARNED ---` and
`Chapter {number}: {title}`. Where your earlier translation could be reused it
has been carried over and marked with a comment asking you to check it.
`You have completed all six chapters of NVDA Coach` is now
`You have completed NVDA Coach`; your existing translation was kept, and it
still says six, which is true for your language until the new chapters are
translated.
