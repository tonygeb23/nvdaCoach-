"""Inspect a built .nvda-addon, not the source tree it came from.

The source passing tells you nothing about what actually went into the zip.
This opens the package NVDA will install and checks it from the inside:
the manifest it will read, the languages it really contains, the catalogues
it will load, and whether anything got in that should not have.

    python tools/verify_package.py nvdaCoach-1.6.0.nvda-addon
"""
import gettext
import io
import json
import os
import sys
import zipfile

CHAPTERS = 6
DOC_PAGES = ["readme.html", "practice.html", "resources.html"]

# Anything matching these has no business inside a user's download.
JUNK = ["__pycache__", ".pyc", ".git", "translators/", "TRANSLATORS-",
        "FACTUAL-CORRECTIONS", "docs-review", "NVDA-RESEARCH", ".bak", "scratchpad"]

problems = []
notes = []


def fail(msg):
    problems.append(msg)


def main(path):
    if not os.path.isfile(path):
        print("no such package: %s" % path)
        return 2

    zf = zipfile.ZipFile(path)
    names = zf.namelist()
    print("%s  %.1f KB  %d entries" % (os.path.basename(path), os.path.getsize(path) / 1024.0, len(names)))
    print()

    bad = zf.testzip()
    if bad:
        fail("corrupt entry in the zip: %s" % bad)

    # --- the manifest NVDA will actually read -------------------------
    if "manifest.ini" not in names:
        fail("no manifest.ini in the package")
        return report()
    manifest = zf.read("manifest.ini").decode("utf-8")
    fields = {}
    for line in manifest.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            fields[k.strip()] = v.strip().strip('"')
    for required in ("name", "summary", "description", "author", "version",
                     "minimumNVDAVersion", "lastTestedNVDAVersion"):
        if required not in fields:
            fail("manifest is missing %s" % required)
    print("  name                  %s" % fields.get("name"))
    print("  version               %s" % fields.get("version"))
    print("  minimum NVDA          %s" % fields.get("minimumNVDAVersion"))
    print("  last tested NVDA      %s" % fields.get("lastTestedNVDAVersion"))
    print()

    # The filename must agree with the manifest, or the wrong thing ships.
    v = fields.get("version", "")
    if v and v not in os.path.basename(path):
        fail("package is named %r but the manifest says %s" % (os.path.basename(path), v))

    # --- nothing that should not be here -------------------------------
    junk = [n for n in names if any(j in n for j in JUNK)]
    if junk:
        fail("%d file(s) that should not ship: %s" % (len(junk), ", ".join(junk[:5])))

    # --- languages, from the inside ------------------------------------
    langs = sorted({n.split("/")[3] for n in names
                    if n.startswith("globalPlugins/nvdaCoach/lessons/") and n.count("/") > 3})
    print("  languages             %s" % " ".join(langs))
    for lang in langs:
        chapters = [n for n in names
                    if n.startswith("globalPlugins/nvdaCoach/lessons/%s/" % lang) and n.endswith(".json")]
        # English carries the two chapters added in 1.7.0. Another language
        # has them only once they are translated, and never just one of them.
        allowed = (CHAPTERS + 2,) if lang == "en" else (CHAPTERS, CHAPTERS + 2)
        if len(chapters) not in allowed:
            fail("%s has %d chapter files, expected %s" % (
                lang, len(chapters), " or ".join(str(n) for n in allowed)))
        for page in DOC_PAGES:
            if "doc/%s/%s" % (lang, page) not in names:
                fail("%s is missing doc/%s" % (lang, page))
        if lang != "en":
            if "locale/%s/LC_MESSAGES/nvda.mo" % lang not in names:
                fail("%s has no compiled catalogue in the package" % lang)
            if "locale/%s/manifest.ini" % lang not in names:
                fail("%s has no translated store listing in the package" % lang)

    # --- every lesson file in the package parses ------------------------
    total = 0
    for n in names:
        if n.startswith("globalPlugins/nvdaCoach/lessons/") and n.endswith(".json"):
            try:
                d = json.loads(zf.read(n).decode("utf-8"))
                total += len(d["lessons"])
            except Exception as e:
                fail("%s does not parse inside the package: %s" % (n, e))
    print("  lessons in package    %d across %d languages" % (total, len(langs)))

    # --- every catalogue in the package loads ---------------------------
    for lang in langs:
        n = "locale/%s/LC_MESSAGES/nvda.mo" % lang
        if n not in names:
            continue
        try:
            cat = gettext.GNUTranslations(io.BytesIO(zf.read(n)))
            ct = cat.info().get("content-type", "")
            if "utf-8" not in ct.lower():
                fail("%s catalogue does not declare UTF-8 (%r)" % (lang, ct))
        except Exception as e:
            fail("%s catalogue will not load from the package: %s (%s)" % (lang, e, type(e).__name__))

    # --- the entry point is there ---------------------------------------
    if "globalPlugins/nvdaCoach/__init__.py" not in names:
        fail("the add-on's entry point is not in the package")

    print()
    return report()


def report():
    if problems:
        print("%d problem(s):" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print()
        print("DO NOT SHIP THIS PACKAGE")
        return 1
    for n in notes:
        print("  note  %s" % n)
    print("Package looks shippable.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
