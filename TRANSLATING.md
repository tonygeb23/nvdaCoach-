# NVDA Coach — Translator Guide

Thank you for contributing a translation! This guide covers everything you need to translate NVDA Coach into your language and test your work as you go.

---

## What You'll Need

- NVDA installed and running
- NVDA Coach installed — download the latest `.nvda-addon` from the [releases page](https://github.com/tonygeb23/nvdaCoach-/releases) and open it to install
- **Poedit** — a free, accessible translation editor that handles compiling for you. Download it at [poedit.net](https://poedit.net). It works well with NVDA.

---

## What Can Be Translated

NVDA Coach has three layers of translatable content:

| Layer | What it is | Where to find it |
|---|---|---|
| **UI strings** | Button labels, spoken announcements, status messages, dialog text | `locale/[lang]/LC_MESSAGES/nvda.po` |
| **Lesson content** | Step instructions, hints, chapter titles and descriptions | `globalPlugins/nvdaCoach/lessons/[lang]/` |
| **Documentation** | User guide, practice page, resources page | `doc/[lang]/` |

A UI-only translation is still valuable and can be submitted on its own. All three layers together make a complete translation.

---

## Step 1 — Set NVDA's Language to Yours

1. Press `NVDA+N` to open the NVDA menu
2. Go to **Preferences → Settings → General**
3. Find the **Language** dropdown and set it to your language
4. Press OK and let NVDA restart

NVDA Coach will now look for your language's files automatically.

---

## Step 2 — Find the Installed Add-on Folder

Once NVDA Coach is installed, your files live here:

```
C:\Users\[YourName]\AppData\Roaming\nvda\addons\nvdaCoach\
```

Inside that folder you'll find your language's scaffold files at:

```
locale\[lang]\LC_MESSAGES\nvda.po
locale\[lang]\LC_MESSAGES\nvda.mo
globalPlugins\nvdaCoach\lessons\[lang]\
doc\[lang]\
```

Replace `[lang]` with your language code (for example: `ru` for Russian, `tr` for Turkish, `pt_BR` for Brazilian Portuguese).

This is where you copy your translated files to test them.

---

## Step 3 — Translate and Test UI Strings (nvda.po)

The translation template is at `locale/nvda.pot`. A scaffold `.po` file for your language is already in the repository with all strings listed and empty `msgstr` fields ready to fill in.

### Translating

1. Open your `nvda.po` file in **Poedit**
2. Fill in your translations — each entry shows the English source on top and an empty field below for your translation:

```po
msgid "Lesson stopped."
msgstr "Lição interrompida."
```

3. Leave `msgstr ""` empty for any string you are not yet ready to translate — NVDA Coach falls back to English for untranslated strings

### Testing

1. Press **Ctrl+S** in Poedit — it saves the `.po` and automatically compiles the `.mo` file alongside it
2. Copy both `nvda.po` and `nvda.mo` into the add-on folder at the path above
3. **Restart NVDA** — press `NVDA+Q`, choose Restart, then reopen NVDA Coach with `NVDA+Shift+C`

You should now hear your translated strings.

### Tips

- Strings containing `{placeholders}` like `{name}` or `{stepNum}` must keep those placeholders exactly as written — only translate the surrounding text
- Unicode characters (arrows, bullets, em-dashes) can be kept as-is or replaced with equivalents that make sense in your language
- Poedit shows you which strings are still untranslated so you can track your progress

---

## Step 4 — Translate and Test Lesson Files

The JSON lesson files (six core chapters, plus the two added in 1.7.0) are in `globalPlugins/nvdaCoach/lessons/[lang]/`. You can edit these in any plain text editor — Notepad works fine.

### What to translate

Each lesson step looks like this:

```json
{
  "instruction": "Press NVDA+F1 to open the NVDA help menu.",
  "hint": "Hold NVDA, then press F1."
}
```

Translate the `instruction`, `hint`, and `text` fields. Leave everything else exactly as-is — do **not** change:

- `"id"` values
- `"type"` values
- `"gesture"` and `"expectedGestures"` — these are key codes, not text
- `"title"` and `"description"` at the chapter level if you are unsure

### Files and chapters

| File | Chapter |
|---|---|
| `getting_started.json` | Chapter 1: Getting Started with NVDA |
| `reading_text.json` | Chapter 3: Reading and Moving Through Text |
| `browse_mode.json` | Chapter 4: Browse Mode and Web Navigation |
| `object_navigation.json` | Chapter 5: Object Navigation |
| `nvda_settings.json` | Chapter 6: Customizing NVDA |
| `keyboard_reference.json` | Chapter 2: Your Keyboard |

### Testing

After editing a lesson file, copy it into the add-on folder and restart NVDA. Open NVDA Coach with `NVDA+Shift+C`, choose the lesson, and run through it to hear your translation.

---

## Step 5 — Translate and Test Documentation

The three HTML files in `doc/[lang]/` can be edited in any text editor. Translate the visible text between the HTML tags — leave the tags themselves untouched.

| File | What it is |
|---|---|
| `readme.html` | Main user guide — opened with F4 inside NVDA Coach |
| `practice.html` | Practice page used during Browse Mode lessons |
| `resources.html` | Additional resources and links |

To test: copy your updated file into the add-on folder. In NVDA Coach, press **F4** to open the help documentation and confirm it shows your translation.

---

## Submitting Your Translation

When you're ready — or when you have a batch ready — **zip up your translated files and reply to your open GitHub issue** with the zip attached. No pull request needed.

Files to include:

```
locale\[lang]\LC_MESSAGES\nvda.po
locale\[lang]\LC_MESSAGES\nvda.mo
globalPlugins\nvdaCoach\lessons\[lang]\    (every .json file)
doc\[lang]\                                (readme.html, practice.html, resources.html)
locale\[lang]\manifest.ini                 (add-on description in your language, if translated)
```

You don't have to submit everything at once. Partial translations are welcome — submit what you have and we'll track the rest in the issue.

---

## Language Codes Reference

Use the same codes NVDA uses:

| Language | Code |
|---|---|
| Arabic | `ar` |
| Chinese (Simplified) | `zh_CN` |
| Chinese (Traditional) | `zh_TW` |
| French | `fr` |
| German | `de` |
| Japanese | `ja` |
| Portuguese (Brazil) | `pt_BR` |
| Portuguese (Portugal) | `pt_PT` |
| Russian | `ru` |
| Spanish | `es` |
| Turkish | `tr` |

For a full list of codes NVDA supports, see the [NVDA source repository](https://github.com/nvaccess/nvda).

---

## Questions

If you're unsure what a string is for, or want to check your understanding of a lesson step, ask in your GitHub issue and Tony will tell you exactly where it appears in the app.

Thank you for helping make NVDA Coach accessible to more people around the world.

**Tony Gebhard** — Assistive Technology Instructor
info@tonygebhard.me
https://github.com/tonygeb23/nvdaCoach-
