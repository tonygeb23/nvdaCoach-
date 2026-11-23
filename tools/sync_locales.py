"""Bring every translation catalogue into line with the code, and compile it.

Run after any change to a _() string in the Python:

    python tools/sync_locales.py            # report only, change nothing
    python tools/sync_locales.py --write    # rewrite .pot, every .po and .mo

What it does, in order:

  1. Collects every _() string from the add-on's Python (the same rule
     build_pot.py uses) and writes locale/nvda.pot and the English .po.
  2. For each language, keeps every existing translation whose English is
     unchanged, drops entries whose English no longer exists, and adds the
     new English strings as empty entries for the translator.
  3. Carries a translation across when the English was only reworded, using
     the CARRIED table below, so a translator's work is not thrown away by an
     edit to one sentence. Those entries are marked for the translator.
  4. Compiles each .po to .mo. This machine has no msgfmt, so the .mo is
     written here; it always includes the header, because a .mo without one
     makes gettext fall back to ASCII and fail on the first accented letter.

Entries are never machine translated. An empty msgstr means NVDA shows the
English, which is the honest result for a string nobody has translated.
"""
import ast
import io
import os
import re
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE = os.path.join(ROOT, "locale")
SOURCES = [
    "globalPlugins/nvdaCoach/__init__.py",
    "globalPlugins/nvdaCoach/lessonRunner.py",
]


def _chapterLine(old):
    """'  Chapter 1: Getting Started with NVDA' in any language -> a pattern."""
    lines = old.split("\n")
    if len(lines) < 2:
        return ""
    line = lines[1].strip()
    match = re.match(r"^(.*?)1(.*?[:\uff1a]\s*)", line)
    if not match:
        return ""
    return match.group(1) + "{number}" + match.group(2) + "{title}"


# English that was reworded. Each row: the start of the old msgid, the start
# of the new msgid, and how to get the new translation from the old one.
# The last two rows were reworded in 1.6.0 without this step, so those
# translations had been silently lost since then.
CARRIED = [
    (
        "--- WHAT YOU HAVE LEARNED ---\n  Chapter 1:",
        "--- WHAT YOU HAVE LEARNED ---",
        lambda old: old.split("\n")[0],
    ),
    (
        "--- WHAT YOU HAVE LEARNED ---\n  Chapter 1:",
        "Chapter {number}: {title}",
        _chapterLine,
    ),
    (
        "You have completed all six chapters of NVDA Coach. ",
        "You have completed NVDA Coach. Your progress is saved",
        lambda old: old,
    ),
    (
        "Welcome to NVDA Coach\nCreated by Tony Gebhard, Assistive Technology Instructor\ngithub.com/tonygeb23/nvdacoach\n",
        "Welcome to NVDA Coach\nCreated by Tony Gebhard, Assistive Technology Instructor\ngithub.com/tonygeb23/nvdaCoach-\n",
        lambda old: old.replace("github.com/tonygeb23/nvdacoach\n", "github.com/tonygeb23/nvdaCoach-\n"),
    ),
    (
        "Show NVDA Coach window, or open the lesson picker",
        "Show NVDA Coach window, or open the lesson picker. In Excel",
        lambda old: old,
    ),
]


def source_strings():
    seen, out = set(), []
    for rel in SOURCES:
        with io.open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_"
                and len(node.args) == 1
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                text = node.args[0].value
                if text and text not in seen:
                    seen.add(text)
                    out.append((rel, node.lineno, text))
    out.sort(key=lambda row: (SOURCES.index(row[0]), row[1]))
    return out


_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}


def _unquote(text):
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            out.append(_ESCAPES.get(text[i + 1], text[i + 1]))
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _quote(text):
    return (
        text.replace("\\", "\\\\").replace('"', '\\"')
        .replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
    )


def read_po(path):
    """Return (header, {msgid: msgstr}, leading comment lines).

    The comment block at the top of a .po is where a translator's name and
    copyright line live, so it is kept and written back unchanged.
    Obsolete (#~) entries are ignored.
    """
    entries, header, preamble = {}, "", []
    msgid = msgstr = None
    target = None

    def flush():
        nonlocal header
        if msgid is None:
            return
        if msgid == "":
            header = msgstr or ""
        else:
            entries[msgid] = msgstr or ""

    with io.open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if line.startswith("#") or not line:
                if msgid is None and line.startswith("#") and not line.startswith(("#:", "#,", "#~", "#.")):
                    preamble.append(line)
                continue
            if line.startswith("msgid "):
                flush()
                msgid, msgstr, target = _unquote(line[6:].strip()[1:-1]), None, "id"
            elif line.startswith("msgstr "):
                msgstr, target = _unquote(line[7:].strip()[1:-1]), "str"
            elif line.startswith('"'):
                piece = _unquote(line[1:-1])
                if target == "id":
                    msgid += piece
                elif target == "str":
                    msgstr += piece
    flush()
    return header, entries, preamble


def write_po(path, header, rows, preamble=()):
    """rows: (location, msgid, msgstr, note)."""
    lines = list(preamble) + ['msgid ""', 'msgstr ""']
    for part in header.split("\n"):
        if part:
            lines.append('"%s\\n"' % _quote(part))
    lines.append("")
    for location, msgid, msgstr, note in rows:
        if note:
            lines.append("#. " + note)
        lines.append("#: " + location)
        lines.append('msgid "%s"' % _quote(msgid))
        lines.append('msgstr "%s"' % _quote(msgstr))
        lines.append("")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def write_mo(path, header, catalogue):
    """Standard little-endian GNU .mo, header entry included."""
    items = {"": header}
    items.update({k: v for k, v in catalogue.items() if v})
    keys = sorted(items)
    ids = [k.encode("utf-8") for k in keys]
    strs = [items[k].encode("utf-8") for k in keys]
    n = len(keys)
    keystart = 7 * 4 + 16 * n
    valuestart = keystart + sum(len(i) + 1 for i in ids)
    koffsets, voffsets = [], []
    offset = keystart
    for i in ids:
        koffsets += [len(i), offset]
        offset += len(i) + 1
    offset = valuestart
    for s in strs:
        voffsets += [len(s), offset]
        offset += len(s) + 1
    out = struct.pack("<Iiiiiii", 0x950412DE, 0, n, 7 * 4, 7 * 4 + n * 8, 0, 0)
    out += struct.pack("<%di" % (2 * n), *koffsets)
    out += struct.pack("<%di" % (2 * n), *voffsets)
    out += b"".join(i + b"\0" for i in ids)
    out += b"".join(s + b"\0" for s in strs)
    with open(path, "wb") as fh:
        fh.write(out)


POT_HEADER = (
    "Project-Id-Version: NVDA Coach {version}\n"
    "Report-Msgid-Bugs-To: info@tonygebhard.me\n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=UTF-8\n"
    "Content-Transfer-Encoding: 8bit\n"
)


def main(write):
    with io.open(os.path.join(ROOT, "manifest.ini"), encoding="utf-8") as fh:
        version = [l.split("=", 1)[1].strip() for l in fh if l.startswith("version")][0]
    strings = source_strings()
    ids = [s for _f, _l, s in strings]
    print("%d strings in the code" % len(ids))

    template = [("%s:%d" % (f, l), s, "", "") for f, l, s in strings]
    if write:
        header = POT_HEADER.format(version=version)
        write_po(os.path.join(LOCALE, "nvda.pot"), header, template)
        write_po(os.path.join(LOCALE, "en", "LC_MESSAGES", "nvda.po"), header, template)

    for lang in sorted(os.listdir(LOCALE)):
        po = os.path.join(LOCALE, lang, "LC_MESSAGES", "nvda.po")
        if lang == "en" or not os.path.isfile(po):
            continue
        header, old, preamble = read_po(po)
        if "charset=UTF-8" not in header:
            header += "Content-Type: text/plain; charset=UTF-8\n"
        carried = {}
        for prefix, newPrefix, convert in CARRIED:
            newId = next((i for i in ids if i.startswith(newPrefix)), None)
            source = next(
                (v for k, v in old.items() if k.startswith(prefix) and k not in ids and v), None
            )
            if newId and source and not old.get(newId):
                value = convert(source)
                if value:
                    carried[newId] = value
        rows, kept, empty = [], 0, []
        for f, l, s in strings:
            note = ""
            value = old.get(s, "")
            if not value and s in carried:
                value = carried[s]
                note = "Carried over from the 1.6.0 wording. Please check it against the new English."
            if value:
                kept += 1
            else:
                empty.append(s)
            rows.append(("%s:%d" % (f, l), s, value, note))
        dropped = [k for k in old if k not in ids]
        print(
            "%-6s %3d translated, %2d carried, %2d untranslated, %2d retired"
            % (lang, kept, len(carried), len(empty), len(dropped))
        )
        if "-v" in sys.argv:
            for s in empty:
                print("        untranslated: %s" % s[:70].replace("\n", " / "))
        if write:
            write_po(po, header, rows, preamble)
            write_mo(po[:-3] + ".mo", header, {s: v for _loc, s, v, _n in rows})
    if not write:
        print("\nNothing was written. Run again with --write to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
