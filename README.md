# NVDA Coach

**Interactive screen reader training built right into NVDA.**

NVDA Coach is a free add-on for the [NVDA screen reader](https://nvaccess.org) that teaches commands through guided, step-by-step practice sessions — from inside NVDA itself. No videos, no PDFs, no switching between windows. Press one key combination and the Coach walks you through what to do and why, one step at a time.

**Current version:** 1.5.4
**Author:** Tony Gebhard, Assistive Technology Instructor
**License:** GPL v2

---

## Download and Install

**[Download NVDA Coach v1.5.4](https://github.com/tonygeb23/nvdaCoach-/releases/download/v1.5.4/nvdaCoach-1.5.4.nvda-addon)**

1. Download the `.nvda-addon` file above
2. Open the file — NVDA handles the installation automatically and asks you to confirm
3. Press **NVDA+Shift+C** — the Coach window opens and you're ready to begin

NVDA 2024.1 or later required. Tested through NVDA 2026.1. Available in the NVDA Add-on Store (Tools → Add-on Store).

---

## What's New in v1.5.4

- **NVDA 2026.1 compatibility confirmed:** Tested and verified to work with NVDA 2026.1 (64-bit, Python 3.13). The compatibility declaration has been updated so users on NVDA 2026.1 no longer see a warning in the Add-on Store. No code changes were required.

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

## What's Included — 45 Lessons Across Six Chapters

### Chapter 1: Getting Started with NVDA — 14 lessons
An orientation to the three categories of keyboard commands (Windows, program, and screen reader), followed by the essential NVDA commands every new user needs: the NVDA modifier key, reading the title bar, checking the time, silencing speech, identifying current focus, Tab navigation, activating buttons and checkboxes, reading the current line, Input Help mode, opening the user guide, keyboard physical orientation, switching windows with Alt+Tab, and checking battery status (NVDA+Shift+B). Several lessons include a live accessible practice form with real buttons, checkboxes, and text fields.

### Chapter 2: Your Keyboard — 3 lessons
Where modifier keys live on standard and laptop keyboards (Ctrl, Shift, Alt, Windows key, NVDA key), how function keys and the Fn key work (Fn+arrows for Home/End/Page Up/Page Down, Fn Lock, multimedia vs F-key mode), and how to select and switch your NVDA keyboard layout setting. Placed early so students have physical keyboard confidence before command learning begins.

### Chapter 3: Reading and Moving Through Text — 8 lessons
Character-by-character, word-by-word, and line-by-line navigation; jumping to document start and end; Say All (desktop: NVDA+Down Arrow, laptop: NVDA+A); text selection with Shift+arrows including NVDA's report-selection command; navigating by paragraph (Ctrl+Up/Down) and page (Page Up/Down); and checking font and formatting (NVDA+F reports font name, size, and bold/italic/underline — double-press opens a full formatting dialog). Every lesson embeds a practice text area directly in the Coach window — no switching to another application required.

### Chapter 4: Browse Mode and Web Navigation — 10 lessons
What browse mode is and how it works, heading navigation, heading level shortcuts, link navigation, form field navigation, toggling between browse mode and focus mode, landmark and list navigation, the Elements List dialog, finding text with NVDA Find, and navigating table cells with Ctrl+Alt+Arrow keys. A fully accessible practice web page opens automatically when you start any lesson in this chapter.

### Chapter 5: Object Navigation — 6 lessons
How NVDA's object pyramid works, moving across objects at the same level, climbing up and descending through levels, reading the current navigator object, routing keyboard focus to any control on screen, and when object navigation is the right tool. Uses levels/pyramid terminology throughout. Desktop and laptop layouts documented.

### Chapter 6: Customizing NVDA — 4 lessons
Changing your keyboard layout between desktop (numpad) and laptop (letter keys); adjusting speech rate, voice, and synthesizer settings including on-the-fly speed shortcuts with the synth settings ring; changing the audio output device (NVDA+Ctrl+U for headphones, speakers, or HDMI); and controlling audio ducking (NVDA+Shift+D to set whether NVDA lowers other audio while speaking). Completing this chapter triggers the Certificate of Completion.

---

## How It Works

The Coach presents one step at a time. Each step:
- Speaks an instruction and tells you which key to press
- Waits for you to perform the action and press Enter to continue
- Offers **F1** to repeat the instruction, **F2** for a hint, **F3** to skip the step

### Coach Window Keyboard Shortcuts
| Key | Action |
|-----|--------|
| Enter / Space | Advance to next step (or next lesson after completion) |
| F1 | Repeat current instruction |
| F2 | Get a hint (press again to cycle through up to 3 hints per step) |
| F3 | Skip this step |
| Ctrl+N | Move to next lesson |
| Ctrl+B | Go back to previous lesson |
| Ctrl+R | Restart current lesson from the beginning |
| NVDA+Shift+C | Open the lesson picker (or return to the Coach window) |
| Escape × 3 | Close the Coach window |

> **Hotkey conflict?** `NVDA+Shift+C` can be remapped via NVDA menu → Preferences → Input Gestures → NVDA Coach.

### Progress Tracking
Completed lessons are marked in the lesson picker and saved across NVDA restarts, so you can pick up exactly where you left off.

---

## For AT Instructors and TVIs

NVDA Coach was built by an AT instructor for classroom and one-on-one use. Assign a chapter before a session, use it as a structured warm-up, or give it to students for independent practice between appointments. The lesson picker shows completed lessons at a glance so you and the student can track progress together.

### Custom Lessons

All lessons are plain JSON files in `globalPlugins/nvdaCoach/lessons/`. Adding a new lesson set is as simple as dropping a new `.json` file in that folder. The existing files serve as templates, and the format is documented in the [user guide](doc/en/readme.html).

Get in touch at [info@tonygebhard.me](mailto:info@tonygebhard.me) to discuss custom lesson development for your program, organization, or student population.

---

## Building from Source

```bash
cd nvdaCoach-source
python -c "
import zipfile, os
output = 'nvdaCoach-1.5.4.nvda-addon'
if os.path.exists(output): os.remove(output)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write('manifest.ini', 'manifest.ini')
    for root, dirs, files in os.walk('globalPlugins'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if not file.endswith('.pyc'): zf.write(os.path.join(root,file), os.path.join(root,file).replace(os.sep,'/'))
    for root, dirs, files in os.walk('doc'):
        for file in files: zf.write(os.path.join(root,file), os.path.join(root,file).replace(os.sep,'/'))
    for root, dirs, files in os.walk('locale'):
        for file in files: zf.write(os.path.join(root,file), os.path.join(root,file).replace(os.sep,'/'))
"
```

---

## Planned for Future Versions

- Working with email and Microsoft Office chapters
- Braille display interaction module
- Lesson difficulty and pace settings
- Instructor progress reporting

If you have ideas for lessons, commands that should be covered, or feedback on your experience, [open an issue](https://github.com/tonygeb23/nvdaCoach-/issues) or email [info@tonygebhard.me](mailto:info@tonygebhard.me).

---

## Acknowledgments

Thank you to the testers and community members who have shaped NVDA Coach through their feedback:

- **Jessica Tegner** (Be My Eyes) — invaluable early feedback and feature and lesson requests
- **Darrell Hilliker**, CPWA, Salesforce Certified UX Designer
- **Rui Fontes** (NVDA Portuguese translation team)
- **John Hess**, Adaptive Technology Specialist, State Services for the Blind — detailed correction of laptop keyboard layout gestures in the Object Navigation chapter
- **Brandon Patterson** — correction of synth settings ring keystrokes in the Customizing NVDA chapter
- **Valentin Kupriyanov** and the **[NVDA.ru community](https://nvda.ru)** — Valentin's work goes far beyond translation. As head of the Russian-speaking NVDA user community, he identified the broken localization architecture that had been silently failing from the start, proposed the full internationalization overhaul that made NVDA Coach a globally accessible tool, contributed the complete Russian translation across all six chapters, and personally caught the missing `nvda.mo` binary in v1.5 that left Russian speakers receiving English content. His dedication to making screen reader training available in Russian — and his detailed, actionable feedback at every stage — has been extraordinary. NVDA.ru is a testament to what community-led accessibility looks like.
- **Umut KORKMAZ** (Turkey) — Turkish translation
- **Edson Miranda** (Brazil) — Brazilian Portuguese translation (in progress)
- **Mateo Quintela** (Spain) — Spanish localization testing and practice text
- **Chris, Mike, Kevin, Julie, Larry, Jim, McKayla, and Skyler** — assistive technology specialists with Pacific Northwest state agencies, hands-on feedback from April 2026 training sessions
- **Nash** — feature and lesson requests
- **Brian**
- **Gene**
- **Joseph**
- Anonymous community members who have written in with corrections and encouragement

---

## Contact

**Tony Gebhard**, Assistive Technology Instructor
[info@tonygebhard.me](mailto:info@tonygebhard.me) · [tonygebhard.me](https://tonygebhard.me)
