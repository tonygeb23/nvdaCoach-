"""Pre-release gate for NVDA Coach.

Run this before every build. It derives what it checks from the add-on itself
rather than from a list somebody has to remember to update, because a check
that is typed twice goes stale and starts lying.

Written 2026-09-20 during the 1.6.0 review, after a release pass found:

  - a keyboard command the add-on taught that NVDA does not have, translated
    faithfully into all nine languages
  - a .mo compiled without its header, which made NVDA's gettext fall back to
    ASCII and raise UnicodeDecodeError on the first Turkish character
  - a locale folder that had shipped as an English copy since 1.5.1
  - seven documentation pages each advertising a different, older version
  - translator worksheets about to be packaged into the add-on users download

Every one of those is checked below.

    python tools/validate_addon.py            # report
    python tools/validate_addon.py --strict   # non-zero exit on any warning

Exit code is non-zero if anything FAILS, so it can gate a build.
"""
import gettext
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS = os.path.join(ROOT, "globalPlugins", "nvdaCoach", "lessons")
LOCALE = os.path.join(ROOT, "locale")
DOC = os.path.join(ROOT, "doc")

CHAPTERS = [
    "getting_started.json",
    "keyboard_reference.json",
    "reading_text.json",
    "browse_mode.json",
    "object_navigation.json",
    "nvda_settings.json",
]
# Chapters added in 1.7.0. English must have them. Another language may be
# waiting for its translator, which is reported as a warning rather than a
# failure: a missing chapter is simply not offered to that language's
# students, and shipping an English copy in its place is the mistake the
# "is actually translated" check exists to catch.
NEW_CHAPTERS = [
    "addon_store.json",
    "braille.json",
]
ALL_CHAPTERS = CHAPTERS + NEW_CHAPTERS
# Chapters that must never count toward the certificate, and the only ones
# that may be marked optional.
OPTIONAL_CHAPTERS = ["braille.json"]
DOC_PAGES = ["readme.html", "practice.html", "resources.html"]

# Things the add-on once claimed that NVDA does not do. Each was verified
# against https://download.nvaccess.org/documentation/keyCommands.html
# If one reappears in English, it is a regression, not a style choice.
KNOWN_WRONG = [
    (r"NVDA\+Shift\+Comma", "NVDA binds NVDA+shift+o, not shift+comma"),
    (r"kb:nvda\+shift\+,", "dead gesture binding"),
    (r"Reset to defaults", "the Speech category has no reset button"),
    (r"device picker|listing all available audio", "NVDA+Ctrl+U opens Audio settings, not a picker"),
    (r"and so on up to 6", "heading quick-nav goes to 9"),
    (r"one of two options: Insert", "NVDA offers three modifier keys"),
    (r"Moving Between Controls", "no lesson by that name"),
]

results = []


def check(ok, label, detail="", warn=False):
    results.append(("WARN" if (warn and not ok) else ("PASS" if ok else "FAIL"), label, detail))
    return ok


def manifest_version():
    with io.open(os.path.join(ROOT, "manifest.ini"), encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("version"):
                return line.split("=", 1)[1].strip()
    return None


def languages():
    return sorted(d for d in os.listdir(LESSONS) if os.path.isdir(os.path.join(LESSONS, d)))


def lesson_sig(path):
    with io.open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    out = []
    for les in d["lessons"]:
        out.append((les["id"], len(les.get("steps", []))))
    return d, out


def main(strict):
    # Chinese and Japanese chapter titles appear in the report, and a Windows
    # console on its default code page cannot print them.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    version = manifest_version()
    check(bool(version), "manifest.ini states a version", version or "")

    langs = languages()
    check(len(langs) >= 2, "languages present", " ".join(langs))

    # --- every language is complete -------------------------------------
    for lang in langs:
        missing = [c for c in CHAPTERS if not os.path.isfile(os.path.join(LESSONS, lang, c))]
        check(not missing, "%s: all six core chapter files" % lang, ", ".join(missing))
        waiting = [c for c in NEW_CHAPTERS if not os.path.isfile(os.path.join(LESSONS, lang, c))]
        if lang == "en":
            check(not waiting, "en: both 1.7.0 chapter files", ", ".join(waiting))
        else:
            check(not waiting, "%s: 1.7.0 chapters translated" % lang,
                  "awaiting translation: " + ", ".join(waiting), warn=True)

        docmissing = [p for p in DOC_PAGES if not os.path.isfile(os.path.join(DOC, lang, p))]
        check(not docmissing, "%s: all three doc pages" % lang, ", ".join(docmissing))

        if lang != "en":
            po = os.path.join(LOCALE, lang, "LC_MESSAGES", "nvda.po")
            mo = os.path.join(LOCALE, lang, "LC_MESSAGES", "nvda.mo")
            mani = os.path.join(LOCALE, lang, "manifest.ini")
            check(os.path.isfile(po), "%s: has nvda.po" % lang)
            check(os.path.isfile(mo), "%s: has compiled nvda.mo" % lang)
            check(os.path.isfile(mani), "%s: has a translated store listing" % lang)

    # --- every .mo actually loads, with a charset -----------------------
    # A .mo whose header was dropped makes gettext fall back to ASCII and
    # raise on the first accented character. It looks fine in ls.
    for lang in langs:
        mo = os.path.join(LOCALE, lang, "LC_MESSAGES", "nvda.mo")
        if not os.path.isfile(mo):
            continue
        try:
            with open(mo, "rb") as fh:
                cat = gettext.GNUTranslations(fh)
            ct = cat.info().get("content-type", "")
            check("utf-8" in ct.lower(), "%s: .mo declares UTF-8" % lang, ct)
        except Exception as e:
            check(False, "%s: .mo loads" % lang, "%s: %s" % (type(e).__name__, e))

    # --- lesson files parse, and structure matches English --------------
    en_sigs = {}
    for c in ALL_CHAPTERS:
        p = os.path.join(LESSONS, "en", c)
        if os.path.isfile(p):
            en_sigs[c] = lesson_sig(p)[1]

    for lang in langs:
        broken = []
        for c in ALL_CHAPTERS:
            p = os.path.join(LESSONS, lang, c)
            if not os.path.isfile(p):
                continue
            try:
                lesson_sig(p)
            except Exception as e:
                broken.append("%s (%s)" % (c, e))
        check(not broken, "%s: every chapter file parses" % lang, "; ".join(broken))

    # --- no hint tells a blind student to look at something --------------
    # The hint is what you press F2 for when you are already stuck. Eight of
    # them used to answer "look at the labels on your keyboard", in a course
    # whose whole premise is that the student cannot see. Instructions that
    # say "sighted users see X, NVDA announces Y" are fine and deliberately
    # not matched here: they explain, they do not ask.
    sighted = re.compile(
        r"look at (your|the)|printed on (it|them|your)|indicator light|"
        r"small icons|coloured squares|colored squares|click into|by clicking",
        re.I,
    )
    for lang in ("en",):
        offenders = []
        for c in ALL_CHAPTERS:
            p = os.path.join(LESSONS, lang, c)
            if not os.path.isfile(p):
                continue
            data = json.load(io.open(p, encoding="utf-8"))
            for les in data["lessons"]:
                for n, st in enumerate(les.get("steps", [])):
                    texts = [st.get("instruction", "")] + list(st.get("hints", []))
                    for t in texts:
                        if sighted.search(t or ""):
                            offenders.append("%s/%s step %d" % (c.replace(".json", ""), les["id"], n))
        check(not offenders, "%s: no lesson asks the student to look at something" % lang,
              "; ".join(sorted(set(offenders))[:4]))

    # --- only the braille chapter is optional ------------------------------
    # "optional": true takes a chapter out of the certificate. Set on a core
    # chapter by accident, in any language, it would hand out certificates for
    # a course the student had not finished.
    for lang in langs:
        wrong = []
        for c in ALL_CHAPTERS:
            p = os.path.join(LESSONS, lang, c)
            if not os.path.isfile(p):
                continue
            flag = json.load(io.open(p, encoding="utf-8")).get("optional")
            if (flag is True) != (c in OPTIONAL_CHAPTERS) or flag not in (None, True, False):
                wrong.append("%s optional=%r" % (c, flag))
        check(not wrong, "%s: only the braille chapter is optional" % lang, "; ".join(wrong))

    # --- lesson ids are identifiers, not text ----------------------------
    # A bulk text pass over the Turkish files rewrote activate_controls to
    # activate_Kontrols. The practice-window registry is keyed on the English
    # id, so it silently never matched and Turkish students got no practice
    # window and no explanation. Progress is stored under the id too.
    en_ids = {}
    for c in ALL_CHAPTERS:
        p = os.path.join(LESSONS, "en", c)
        if os.path.isfile(p):
            en_ids[c] = [l["id"] for l in json.load(io.open(p, encoding="utf-8"))["lessons"]]
    for lang in langs:
        if lang == "en":
            continue
        strays = []
        for c, ids in en_ids.items():
            p = os.path.join(LESSONS, lang, c)
            if not os.path.isfile(p):
                continue
            for l in json.load(io.open(p, encoding="utf-8"))["lessons"]:
                if l["id"] not in ids:
                    strays.append("%s/%s" % (c.replace(".json", ""), l["id"]))
        check(not strays, "%s: lesson ids match English" % lang, ", ".join(strays))

    # --- NVDA can reach the documentation we ship ------------------------
    # Without docFileName the Add-on Store's Help button is disabled, so nine
    # localised readme.html files ship and none of them is reachable.
    doc_name = fields.get("docFileName") if "fields" in dir() else None
    with io.open(os.path.join(ROOT, "manifest.ini"), encoding="utf-8") as fh:
        mani = fh.read()
    has_doc = "docFileName" in mani
    check(has_doc, "manifest names a help file (docFileName)",
          "without it NVDA's Add-on Help button is disabled")
    if has_doc:
        name = [l.split("=", 1)[1].strip() for l in mani.splitlines()
                if l.startswith("docFileName")][0]
        missing = [lang for lang in langs
                   if not os.path.isfile(os.path.join(DOC, lang, name))]
        check(not missing, "every language ships %s" % name, ", ".join(missing))

    # --- a locale that is secretly an English copy ----------------------
    def strings_of(o, out):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("id", "type", "order", "expectedGestures", "monitorGestures"):
                    continue
                strings_of(v, out)
        elif isinstance(o, list):
            for v in o:
                strings_of(v, out)
        elif isinstance(o, str) and len(o.strip()) > 12:
            out.append(o.strip())
        return out

    en_all = set()
    for c in ALL_CHAPTERS:
        p = os.path.join(LESSONS, "en", c)
        if os.path.isfile(p):
            en_all |= set(strings_of(json.load(io.open(p, encoding="utf-8")), []))

    for lang in langs:
        if lang == "en":
            continue
        mine = []
        for c in ALL_CHAPTERS:
            p = os.path.join(LESSONS, lang, c)
            if os.path.isfile(p):
                mine += strings_of(json.load(io.open(p, encoding="utf-8")), [])
        if not mine:
            continue
        same = sum(1 for s in mine if s in en_all) * 100.0 / len(mine)
        check(same < 90, "%s: is actually translated" % lang,
              "%.1f%% of its lesson text is identical to English" % same)

    # --- errors that must never come back --------------------------------
    for pattern, why in KNOWN_WRONG:
        hits = []
        for root, _dirs, files in os.walk(LESSONS):
            if os.sep + "en" not in root + os.sep:
                continue
            for f in files:
                if not f.endswith(".json"):
                    continue
                raw = io.open(os.path.join(root, f), encoding="utf-8").read()
                if re.search(pattern, raw):
                    hits.append(f)
        check(not hits, "English is free of: %s" % why, ", ".join(sorted(set(hits))))

    # --- gesture bindings are real NVDA gestures -------------------------
    bad_gestures = []
    for root, _dirs, files in os.walk(LESSONS):
        for f in files:
            if not f.endswith(".json"):
                continue
            raw = io.open(os.path.join(root, f), encoding="utf-8").read()
            for g in re.findall(r'"(kb:[^"]+)"', raw):
                # A gesture with a non-ASCII key name is a translated one,
                # which NVDA will never match.
                if any(ord(ch) > 127 for ch in g):
                    bad_gestures.append("%s: %s" % (os.path.basename(root), g))
    check(not bad_gestures, "no gesture identifiers were translated",
          "; ".join(sorted(set(bad_gestures))[:6]), warn=True)

    # --- doc pages declare their language --------------------------------
    for lang in langs:
        for page in DOC_PAGES:
            p = os.path.join(DOC, lang, page)
            if not os.path.isfile(p):
                continue
            raw = io.open(p, encoding="utf-8", errors="replace").read()
            m = re.search(r"<html[^>]*\blang=[\"']([^\"']+)", raw, re.I)
            declared = m.group(1) if m else None
            want = lang.replace("_", "-")
            ok = declared is not None and declared.lower().split("-")[0] == want.lower().split("-")[0]
            check(ok, "%s/%s declares its language" % (lang, page),
                  "lang=%r, folder says %r" % (declared, want), warn=True)

    # --- version is stated consistently ----------------------------------
    stale = []
    for lang in langs:
        p = os.path.join(DOC, lang, "readme.html")
        if not os.path.isfile(p):
            continue
        raw = io.open(p, encoding="utf-8", errors="replace").read()
        # Strip <style> first: "line-height: 1.6" reads as a version number
        # otherwise, and this check reported a page as claiming 1.6 when it
        # actually claimed 1.5.2. A check that lies is worse than no check.
        body = re.sub(r"<style\b.*?</style>", " ", raw, flags=re.S | re.I)
        body = re.sub(r"<[^>]+>", " ", body)
        head = body[:2500]
        found = re.findall(r"\b\d+\.\d+(?:\.\d+)?\b", head)
        if found and version not in found:
            stale.append("%s says %s" % (lang, found[0]))
    check(not stale, "every readme states the current version", "; ".join(stale))

    # --- the readme advertises the lessons that actually ship ------------
    # Chapters 1, 3 and 6 each gained a lesson in 1.5.4 and no documentation
    # page was updated, so four pages spent two releases advertising 41
    # lessons while the add-on shipped 45.
    for lang in langs:
        p = os.path.join(DOC, lang, "readme.html")
        if not os.path.isfile(p):
            continue
        raw = io.open(p, encoding="utf-8", errors="replace").read()
        ships = {}
        for c in ALL_CHAPTERS:
            f = os.path.join(LESSONS, lang, c)
            if os.path.isfile(f):
                d = json.load(io.open(f, encoding="utf-8"))
                ships[d.get("title", c)] = len(d["lessons"])
        wrong = []
        for block in re.split(r"<h3>", raw)[1:]:
            name = re.sub(r"^\d+[.、\s]*", "", block.split("</h3>")[0].strip())
            listed = len(re.findall(r"<li><strong>", block.split("<h2")[0]))
            actual = ships.get(name)
            if actual is not None and actual != listed:
                wrong.append("%s lists %d, ships %d" % (name[:24], listed, actual))
        check(not wrong, "%s: readme lists every lesson that ships" % lang,
              "; ".join(wrong), warn=True)

    # --- nothing internal gets packaged ----------------------------------
    leak = []
    for root, _dirs, files in os.walk(DOC):
        for f in files:
            if f.endswith(".md") and f != "readme.md":
                leak.append(os.path.relpath(os.path.join(root, f), ROOT))
    check(not leak, "no internal notes inside doc/ (it is packaged)", ", ".join(leak))

    # --- report -----------------------------------------------------------
    width = max(len(l) for _s, l, _d in results)
    fails = warns = 0
    for status, label, detail in results:
        if status == "FAIL":
            fails += 1
        elif status == "WARN":
            warns += 1
        if status == "PASS" and "-v" not in sys.argv:
            continue
        print("%-4s %-*s %s" % (status, width, label, detail))

    total = len(results)
    print()
    print("%d checks, %d failed, %d warnings" % (total, fails, warns))
    if fails:
        print("NOT READY TO BUILD")
    elif warns and strict:
        print("warnings present and --strict given")
    else:
        print("OK to build %s" % version)
    return 1 if fails or (warns and strict) else 0


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
