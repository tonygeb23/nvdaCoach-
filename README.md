# NVDA Coach

Interactive screen reader training inside NVDA. 45 lessons across six chapters,
taught step by step — no videos, no PDFs, no switching windows.

Free. GPL v2. By Tony Gebhard, Assistive Technology Instructor.

**Current version:** 1.5.7

## Install

**[Download NVDA Coach v1.5.7](https://github.com/tonygeb23/nvdaCoach-/releases/download/v1.5.7/nvdaCoach-1.5.7.nvda-addon)**
— or get it from the NVDA Add-on Store (Tools → Add-on Store).

Open the `.nvda-addon` file; NVDA installs it and asks you to confirm. Then
press **NVDA+Shift+C**.

Needs NVDA 2024.1 or later. Tested through 2026.1.1.

## What's new in 1.5.7

- **Chinese (Simplified)** — all six chapters, every interface string, the
  documentation and the store listing.
- **Chinese (Traditional)** — a full translation using Taiwan NVDA terminology,
  not a character swap.
- **Practice-window labels are now translatable**, including the field names
  NVDA announces, so students hear the names the lessons tell them to find.
- Fixed the wrong next-chapter hint at the end of Getting Started, and
  regenerated a translation template stale since 1.5.1 — recovering about 95
  strings that had been falling back to English.

[Full history](CHANGELOG.md).

## Coverage

**1. Getting Started — 14 lessons.** The three kinds of keyboard command, then
the essentials: the NVDA key, title bar, time, silencing speech, current focus,
Tab, buttons and checkboxes, reading a line, Input Help, the user guide,
keyboard layout, Alt+Tab, battery. Several use a live practice form.

**2. Your Keyboard — 3 lessons.** Where the modifier keys are on desktop and
laptop boards, how Fn and the function keys work, choosing your NVDA keyboard
layout. Early on purpose: physical confidence before commands.

**3. Reading and Moving Through Text — 8 lessons.** Character, word and line
navigation; document start and end; Say All; selection with Shift+arrows;
paragraph and page movement; font and formatting with NVDA+F. Each lesson has a
practice text area in the Coach window.

**4. Browse Mode and the Web — 10 lessons.** Browse mode, headings and heading
levels, links, form fields, browse/focus toggling, landmarks and lists, the
Elements List, Find, and table cells. A practice web page opens automatically.

**5. Object Navigation — 6 lessons.** The object pyramid, moving across a level,
up and down levels, reading the navigator object, routing focus, and when to
reach for it. Desktop and laptop layouts both documented.

**6. Customizing NVDA — 4 lessons.** Keyboard layout, speech rate and voice
including the synth settings ring, audio output device, and audio ducking.
Finishing this chapter triggers the Certificate of Completion.

## How it works

One step at a time. Each step speaks an instruction, names the key, and waits
for you to do it and press Enter.

| Key | Action |
|-----|--------|
| Enter / Space | Next step, or next lesson once complete |
| F1 | Repeat the instruction |
| F2 | Hint (press again for up to 3) |
| F3 | Skip this step |
| Ctrl+N | Next lesson |
| Ctrl+B | Previous lesson |
| Ctrl+R | Restart this lesson |
| NVDA+Shift+C | Lesson picker, or back to the Coach window |
| Escape × 3 | Close |

Completed lessons are marked in the picker and survive an NVDA restart.

`NVDA+Shift+C` can be remapped: NVDA menu → Preferences → Input Gestures → NVDA
Coach.

## In use

- **[NVDA Coach: From First Keystroke to Confidence](https://www.youtube.com/watch?v=hpbxCDttU5A)** — *Blind Abilities*, Jeff Thompson
- **[Bits & Bytes S2 Ep10](https://www.youtube.com/watch?v=SR-sR0in_Dk)** — *The Knowledge Chest*
- **[RNIB Tech Talk #614](https://podcasts.apple.com/ke/podcast/tech-talk-614-activision-nvda-coach-rnib-shop/id1151878596?i=1000764115174)** — 28 April 2026
- **[Demonstration walk-through](https://www.youtube.com/watch?v=-JXX_u-RQB4)** — a full lesson, start to finish
- **[Can't find a teacher? Use the NVDA Coach](https://www.youtube.com/shorts/0KtsuOs2Lqg)** — *Guidance for the Blind*

## For instructors and TVIs

Built by an AT instructor for classroom and one-to-one use. Assign a chapter
before a session, use it as a warm-up, or set it for independent practice
between appointments. The picker shows progress at a glance.

**Custom lessons:** every lesson is a JSON file in
`globalPlugins/nvdaCoach/lessons/`. Drop in a new `.json` to add a set; the
existing files are the templates, and the format is in the
[user guide](doc/en/readme.html).

For custom lesson development, email
[info@tonygebhard.me](mailto:info@tonygebhard.me).

## Building

```bash
cd nvdaCoach-source
python -c "
import zipfile, os
output = 'nvdaCoach-1.5.7.nvda-addon'
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

## Planned

Email and Office chapters · braille display module · difficulty and pace
settings · instructor progress reporting.

Ideas and corrections: [open an issue](https://github.com/tonygeb23/nvdaCoach-/issues)
or email [info@tonygebhard.me](mailto:info@tonygebhard.me).

## Thanks

- **Valentin Kupriyanov** and the **[NVDA.ru community](https://nvda.ru)** — as
  head of the Russian-speaking NVDA community, Valentin identified the broken
  localization architecture that had been failing silently from the start,
  proposed the internationalization overhaul that made NVDA Coach usable
  worldwide, contributed the complete Russian translation across all six
  chapters, and caught the missing `nvda.mo` in 1.5 that left Russian speakers
  reading English. Far beyond translation.
- **Jessica Tegner** — early feedback, feature and lesson requests
- **John Hess** — corrected the laptop layout gestures in Object Navigation
- **Brandon Patterson** — corrected the synth settings ring keystrokes
- **Darrell Hilliker** — accessibility review
- **Rui Fontes** — NVDA Portuguese translation team
- **Umut KORKMAZ** — Turkish translation
- **Edson Miranda** — Brazilian Portuguese translation (in progress)
- **Mateo Quintela** — Spanish localization testing and practice text
- **Chris, Mike, Kevin, Julie, Larry, Jim, McKayla and Skyler** — AT
  specialists, from the April 2026 training sessions
- **Nash** — feature and lesson requests
- **Brian**, **Gene**, **Joseph**, and the anonymous community members who wrote
  in with corrections and encouragement

## Contact

**Tony Gebhard**, Assistive Technology Instructor
[info@tonygebhard.me](mailto:info@tonygebhard.me) · [tonygebhard.me](https://tonygebhard.me)
