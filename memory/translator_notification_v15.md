# GitHub Issue Draft — Translator Notification for v1.5

**Issue title:** New strings for translation — v1.5

**Repo:** https://github.com/tonygeb23/nvdaCoach-

---

## Issue body (paste as-is)

Hi @nvda-ru (Valentin) and Umut KORKMAZ (Turkish — Umut doesn't have a GitHub username on file, so Umut please reply by email to info@tonygebhard.me or open a PR if you prefer),

NVDA Coach v1.5 was released 2026-04-10. It adds a significant number of new user-facing strings. I'd love to get Russian and Turkish translations updated for v1.5.1.

**Note for Valentin:** Your v1.4 Russian translation zip (submitted 2026-04-08) has not yet been integrated — I'll apply that alongside the v1.5 strings so you only need to send one combined update. Sorry for the delay!

---

### New strings in v1.5

All new strings are in `globalPlugins/nvdaCoach/__init__.py` and `lessonRunner.py`. Categories:

**F4/F5 confirmation and action messages (4 strings)**
Two-press confirmation prompts and action announcements for the help (F4) and feedback email (F5) quick keys.

**F6 sounds toggle (2 strings)**
Spoken announcements for "Sounds on" and "Sounds off" when the user presses F6.

**F7 personalization dialog (5 strings)**
Dialog title, field labels (name, instructor name, training center), and save button label.

**PersonalizationDialog spoken confirmations (2 strings)**
Spoken messages after saving the profile: a personalized greeting ("Hello, {name}!") and a generic confirmation ("Profile saved.").

**Certificate dialog and generation (many strings)**
Certificate heading, heartfelt completion message, full certificate HTML content (including all inline labels and layout text), and save/print instructions shown to the user.

**Final completion screen (many strings)**
The end-of-course screen shown in browse mode: page title ("NVDA Coach — Course Complete!"), congratulations headings (personalized name variant and no-name variant), spoken congratulations announcement, chapter summary list, instructor/training center lines, and certificate instructions section.

**showCertificateButton announcement (1 string)**
The spoken announcement when the certificate button appears in the completion screen.

**showIntroduction personalized variants (4 strings)**
The welcome heading and spoken welcome for the personalized (name present) and generic (no name) variants, plus the instructor line variants.

**showIdle QUICK KEYS section (1 string block)**
The quick keys help block shown at the bottom of the idle screen, listing F4–F7 with descriptions.

**lessonRunner.py — startLesson greeting (1 string)**
A one-time personalized greeting spoken at the start of the first lesson if the user has set their name and instructor.

**lessonRunner.py — _completeLesson well_done variants (2 strings)**
Personalized and generic variants of the "well done" spoken message at lesson completion.

---

### Chapter order change

v1.5 reordered the chapters. If any of your lesson files reference chapter numbers in their text (e.g. "This is Chapter 3"), those may need updating. The new order is:

1. Getting Started with NVDA (unchanged)
2. Your Keyboard (was Ch. 6)
3. Reading and Moving Through Text (was Ch. 2)
4. Browse Mode and Web Navigation (was Ch. 3)
5. Object Navigation (was Ch. 4)
6. Customizing NVDA (was Ch. 5)

Please check your lesson files for any hardcoded chapter number references (e.g. "Chapter 3" or "Chapter 4 of NVDA Coach").

---

### Translation files

- **Updated .pot file:** `locale/nvda.pot` — Tony needs to regenerate this using `xgettext` (or the existing pot workflow) before you start, to make sure it reflects all new v1.5 strings. Tony will reply here or email once the updated .pot is ready.
- **Lesson files:** `globalPlugins/nvdaCoach/lessons/ru/` and `lessons/tr/` — update any lesson files that reference chapter numbers or contain new content.
- **Locale .po files:** `locale/ru/LC_MESSAGES/nvda.po` and `locale/tr/LC_MESSAGES/nvda.po`

---

### How to submit

Same as before — no PRs required. Just reply to this issue (or email info@tonygebhard.me) with a zip containing:
- Your updated `.po` file
- Compiled `.mo` file (if possible; I can compile it if not)
- Any updated lesson `.json` files

Thank you both so much — your work makes NVDA Coach accessible to so many more people. I really appreciate it!

— Tony
