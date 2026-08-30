#!/usr/bin/env python3
"""Render a shareable NVDA Coach download-stats card.

    python build_card.py            # pulls live numbers from GitHub
    python build_card.py --offline  # uses the figures baked in below

Numbers come from the GitHub Releases API, which counts every download of the
`.nvda-addon` asset -- including installs made through the NVDA Add-on Store,
because the store links straight at the same file rather than hosting its own
copy. That is the whole reason this figure is worth publishing: it is the real
total, not just the people who found the GitHub page.

Design notes, both of which are accessibility decisions rather than taste:

  * Every figure is also written out in the alt text this script prints. A
    graphic that only says a number in pixels says nothing at all to a large
    part of Tony's audience.
  * The bars are labelled with their values in the image itself, so nobody has
    to measure a bar against an axis to read it. The chart is a nicety; the
    text is the content.

Palette is lifted from the tonygebhard.me site so this card and the site do not
drift apart.
"""

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
REPO = "tonygeb23/nvdaCoach-"


INK = "#16171a"
CREAM = "#fdfdfc"
EMBER = "#ff9e6b"
SKY = "#6fb3dd"
PANEL = "#1e2024"

SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"
SANS = "'Segoe UI','Helvetica Neue',Arial,sans-serif"

# Used only with --offline, and only so the card can still be rebuilt if the
# API is unreachable. Refreshed 2026-08-19.
FALLBACK = {
    "total": 5752,
    "releases": 16,
    "first": "2026-03-12",
    "latest": "2026-07-13",
    "versions": [
        ("1.5.4", 1073), ("1.5.7", 1007), ("1.5.5", 995),
        ("1.5.1", 526), ("1.5.6", 381), ("1.5.3", 300),
    ],
    "languages": 7,
}


def fetch():
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases?per_page=100",
        headers={"User-Agent": "nvdacoach-stats-card/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        releases = json.loads(response.read().decode("utf-8"))

    rows, total = [], 0
    for release in releases:
        count = sum(a.get("download_count", 0) for a in release.get("assets", []))
        total += count
        rows.append((release["tag_name"].lstrip("v"), count,
                     (release.get("published_at") or "")[:10]))
    dated = [r for r in rows if r[2]]
    return {
        "total": total,
        "releases": len(rows),
        "first": min(r[2] for r in dated) if dated else "",
        "latest": max(r[2] for r in dated) if dated else "",
        "versions": sorted(
            [(r[0], r[1]) for r in rows], key=lambda r: r[1], reverse=True
        )[:6],
        "languages": count_languages(),
    }


def count_languages():
    """How many languages ship, counted from the locale folders themselves.

    Read from the repo rather than copied out of a release note, because a
    number on a public graphic should be checkable against the thing it
    describes.
    """
    locale = HERE.parent / "locale"
    if not locale.is_dir():
        return FALLBACK["languages"]
    return sum(1 for child in locale.iterdir() if child.is_dir())


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def month_year(iso):
    if not iso:
        return ""
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    year, month, _ = iso.split("-")
    return f"{months[int(month) - 1]} {year}"


def build_svg(data, width=1200, height=675):
    total = data["total"]
    versions = data["versions"]
    peak = max(count for _, count in versions) if versions else 1

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{INK}"/>',
        # A warm bar down the left edge, echoing the site's accent rule.
        f'<rect x="0" y="0" width="14" height="{height}" fill="{EMBER}"/>',
    ]

    def text(x, y, content, size, fill, family=SERIF, weight="700",
             anchor="start", spacing=0, opacity=1):
        style = [f"font-family:{family}", f"font-size:{size}px",
                 f"font-weight:{weight}"]
        if spacing:
            style.append(f"letter-spacing:{spacing}px")
        return (f'<text x="{x}" y="{y}" fill="{fill}" text-anchor="{anchor}" '
                f'opacity="{opacity}" style="{";".join(style)}">'
                f'{esc(content)}</text>')

    left = 72
    parts.append(text(left, 92, "NVDA COACH", 26, EMBER, SANS, "700",
                      spacing=6))
    parts.append(text(left, 132, "A free NVDA add-on that teaches NVDA", 24,
                      CREAM, SERIF, "400", opacity=0.75))

    # The headline figure, sized to be the thing you see first.
    parts.append(text(left, 288, f"{total:,}", 150, CREAM, SERIF, "700"))
    parts.append(text(left, 340, "downloads", 40, SKY, SERIF, "400"))

    span = f"{month_year(data['first'])} to {month_year(data['latest'])}"
    parts.append(text(left, 396,
                      f"{data['releases']} releases, {span}", 24, CREAM,
                      SANS, "400", opacity=0.7))

    # Counted from the locale folders in the repo rather than taken from any
    # release note, so the claim on a public graphic is one the source can be
    # checked against.
    parts.append(text(left, 440,
                      f"Available in {data['languages']} languages", 24, CREAM,
                      SANS, "400", opacity=0.7))
    parts.append(text(left, 484,
                      "Also on the NVDA Add-on Store", 24, CREAM,
                      SANS, "400", opacity=0.7))

    # --- the chart ------------------------------------------------------
    chart_x, chart_y, bar_h, gap = 640, 190, 30, 14
    parts.append(text(chart_x, 152, "MOST DOWNLOADED VERSIONS", 18, EMBER,
                      SANS, "700", spacing=3))

    max_bar = 380
    for index, (version, count) in enumerate(versions):
        y = chart_y + index * (bar_h + gap)
        bar_w = max(6, int(max_bar * count / peak))
        parts.append(text(chart_x, y + 22, version, 20, CREAM, SANS, "600"))
        parts.append(
            f'<rect x="{chart_x + 66}" y="{y + 4}" width="{bar_w}" '
            f'height="{bar_h - 8}" rx="4" fill="{SKY}" opacity="0.85"/>'
        )
        # The value is printed next to every bar. Nobody should have to
        # estimate a length against an axis to read a number.
        parts.append(text(chart_x + 66 + bar_w + 12, y + 22, f"{count:,}", 19,
                          CREAM, SANS, "600", opacity=0.9))

    parts.append(f'<rect x="{left}" y="{height - 108}" width="440" height="2" '
                 f'fill="{CREAM}" opacity="0.18"/>')
    parts.append(text(left, height - 62, "tonygebhard.me/nvdacoach", 24, CREAM,
                      SANS, "600", opacity=0.85))
    parts.append(text(width - 72, height - 62,
                      "Free. Open source. Built by a blind developer.", 20,
                      CREAM, SANS, "400", anchor="end", opacity=0.6))

    parts.append("</svg>")
    return "\n".join(parts)


def render(svg_text, out_path, width, height):
    html_path = out_path.with_suffix(".html")
    html_path.write_text(
        f"<style>html,body{{margin:0;padding:0;width:{width}px;"
        f"height:{height}px;overflow:hidden}}"
        f"svg{{display:block;width:{width}px;height:{height}px}}</style>"
        + svg_text,
        encoding="utf-8",
    )
    subprocess.run(
        [str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", f"--window-size={width},{height}",
         f"--screenshot={out_path}", html_path.as_uri()],
        check=True, capture_output=True, timeout=120,
    )
    html_path.unlink(missing_ok=True)


def alt_text(data):
    """The words that carry the image for anyone who cannot see it.

    Written to stand alone: someone hearing only this should end up knowing
    exactly what the picture shows, which means every number in the graphic
    appears here too.
    """
    versions = ", ".join(f"{v} with {c:,}" for v, c in data["versions"])
    return (
        f"A dark card headed NVDA COACH, a free NVDA add-on that teaches NVDA. "
        f"The headline figure is {data['total']:,} downloads, across "
        f"{data['releases']} releases from {month_year(data['first'])} to "
        f"{month_year(data['latest'])}. It is available in "
        f"{data['languages']} languages and on the NVDA Add-on Store. "
        f"A bar chart lists the most downloaded "
        f"versions: {versions}. The footer reads tonygebhard.me slash nvdacoach, "
        f"free, open source, built by a blind developer."
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--out", default=str(HERE / "nvda-coach-downloads.png"))
    args = parser.parse_args()

    data = FALLBACK if args.offline else fetch()
    width, height = 1200, 675

    svg_text = build_svg(data, width, height)
    svg_path = Path(args.out).with_suffix(".svg")
    svg_path.write_text(svg_text, encoding="utf-8")
    render(svg_text, Path(args.out), width, height)

    print(f"wrote {args.out}")
    print(f"wrote {svg_path}")
    print()
    print("ALT TEXT")
    print(alt_text(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
