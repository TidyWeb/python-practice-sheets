"""Write the shared route rail into every page of Python Practice Sheets.

Run from the repository root:  python3 tools/build_rail.py

Each page keeps its own hints. Everything else in the rail (the brand, the three
stages, the barrier and the TidyWeb credit) comes from ROUTE below, so the rail is
identical in shape on every page. Run it again after adding or renaming a sheet.
"""
import os
import re
import textwrap
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUPPLEMENTARY = "supplementary-sheets/car-park-practice-area/"
HOME = "combined-sheets/"  # Chapter 1 is the beginning: the four shapes

# Sheets are numbered 01-13 straight through, in chapter order.
# "icon" is each chapter's own mark, shown on that chapter's home page;
# every sheet page shows SHEET_ICON, which takes you back to its chapter home.
SHEET_ICON = "&#9656;"
ROUTE = [
    {
        "no": "1", "name": "Combined sheets", "range": "01–06", "icon": "&#8635;",
        "home": "combined-sheets/",
        "sheets": [
            ("01", "Library", "combined-sheets/01-combination-library/"),
            ("02", "Allotment", "combined-sheets/02-combination-allotment/"),
            ("03", "Market", "combined-sheets/03-combination-market/"),
            ("04", "Moorings", "combined-sheets/04-combination-moorings/"),
            ("05", "Buses", "combined-sheets/05-combination-buses/"),
            ("06", "Hall", "combined-sheets/06-combination-hall/"),
        ],
    },
    {
        "no": "2", "name": "Supplementary sheets", "range": "07–11", "icon": "curly-f",
        "home": SUPPLEMENTARY,
        "sheets": [
            ("07", "F-Prints", SUPPLEMENTARY + "07-f-prints/"),
            ("08", "Building", SUPPLEMENTARY + "08-building/"),
            ("09", "Reaching In", SUPPLEMENTARY + "09-reaching-in/"),
            ("10", "Conditionals", SUPPLEMENTARY + "10-conditionals/"),
            ("11", "Loops", SUPPLEMENTARY + "11-loops/"),
        ],
    },
    {
        "no": "3", "name": "Car park barrier", "range": "12–13", "icon": SHEET_ICON,
        "home": "car-park-practice-area/12-flow-control/",
        "barrier": True,
        "sheets": [
            ("12", "Worked example", "car-park-practice-area/12-flow-control/"),
            ("13", "Test", "car-park-practice-area/13-nesting/"),
        ],
    },
]

RAIL_RE = re.compile(r'[ \t]*<aside class="rail[^"]*">.*?</aside>', re.S)
HINTS_RE = re.compile(r'<nav class="course-nav hints"[^>]*>.*?</nav>', re.S)
SECTION_LINKS_RE = re.compile(r'\s*<div class="rail-section-links".*?</div>', re.S)
OLD_SCRIPT_RE = re.compile(r'\s*<script src="[^"]*(?:barrier-link|rail)\.js[^"]*"></script>')


def page_path(url):
    return url + "index.html"


def rel(from_url, to_url):
    """Relative link from one page's folder to another page's folder."""
    path = os.path.relpath(to_url or ".", from_url or ".").replace(os.sep, "/")
    return "./" if path == "." else path + "/"


def page_title(stage, here):
    for no, name, url in stage["sheets"]:
        if url == here:
            return f"{no} {name}"
    return stage["name"]


def build_rail(here, hints_html):
    root = rel(here, "")
    current_stage = None
    for stage in ROUTE:
        if here == stage["home"] or any(here == s[2] for s in stage["sheets"]):
            current_stage = stage["no"]

    out = []
    out.append('<aside class="rail rail--route">')
    # the brand mark: each chapter home shows its own icon; sheet pages show the arrow back to their chapter
    stage = next(st for st in ROUTE if st["no"] == current_stage)
    on_home = here == stage["home"] and not stage.get("barrier")
    icon = stage["icon"] if on_home else SHEET_ICON
    back = stage["home"] if not stage.get("barrier") else HOME
    if icon == "curly-f":
        mark = (f'<span class="brand-mark brand-mark--curly-f" aria-hidden="true"><span class="brand-brace brand-brace--left">{{</span>'
                f'<img src="{root}assets/curly-f-central.png" alt=""><span class="brand-brace brand-brace--right">}}</span></span>')
    else:
        mark = f'<span class="brand-mark brand-mark--glyph" aria-hidden="true">{icon}</span>'
    label = f"Chapter {stage['no']}: {stage['name']}" + ("" if on_home else ", contents")
    out.append(
        f'  <a class="route-brand" href="{rel(here, back)}" aria-label="{escape(label)}">{mark}'
        f'<span class="route-brand-text"><small>Chapter {stage["no"]}</small>'
        f'<strong>{escape(stage["name"].capitalize() if on_home else page_title(stage, here))}</strong></span></a>'
    )

    # where am I, for the small-screen route button
    where = "Start here"
    for stage in ROUTE:
        for no, name, url in stage["sheets"]:
            if url == here:
                where = f"Chapter {stage['no']} · {no} {name}"
        if here == stage["home"] and where == "Start here":
            where = f"Chapter {stage['no']} · {stage['name']}"
    toggles = [f'<button type="button" aria-expanded="false" aria-controls="rail-route"><span><small>The route</small>{escape(where)}</span></button>']
    if hints_html:
        label = "Reference" if ">Reference<" in hints_html else "Hints"
        toggles.append(f'<button type="button" aria-expanded="false" aria-controls="rail-hints"><span><small>This sheet</small>{label}</span></button>')
    out.append('  <div class="rail-toggles">' + "".join(toggles) + "</div>")

    out.append('  <nav class="rail-route" id="rail-route" aria-label="The practice route">')
    out.append('    <p class="rail-route-label">The route</p>')
    out.append('    <ol class="route-stages">')
    for stage in ROUTE:
        is_current = stage["no"] == current_stage
        cls = "stage is-current" if is_current else "stage"
        here_attr = ' aria-current="page"' if here == stage["home"] and not stage.get("barrier") else ""
        out.append(f'      <li class="{cls}">')
        out.append(
            f'        <a class="stage-link" href="{rel(here, stage["home"])}"{here_attr}>'
            f'<span class="stage-no">Chapter {stage["no"]}</span><span class="stage-name">{escape(stage["name"])}</span>'
            f'<span class="stage-range">{stage["range"]}</span></a>'
        )
        if stage.get("barrier"):
            state = " is-open" if is_current else ""
            label = "Through the barrier" if is_current else "Open the barrier: go to the car park project"
            out.append(
                f'        <a class="route-barrier{state}" href="{rel(here, stage["home"])}" aria-label="{label}">'
                f'<span class="barrier-road" aria-hidden="true"><img src="{root}assets/car-park-road.png" alt=""></span>'
                f'<span class="barrier-post" aria-hidden="true"></span><span class="barrier-lamp" aria-hidden="true"></span>'
                f'<span class="barrier-arm" aria-hidden="true"></span></a>'
            )
        if is_current:
            out.append('        <ol class="stage-sheets">')
            for no, name, url in stage["sheets"]:
                cur = ' aria-current="page"' if url == here else ""
                out.append(f'          <li><a href="{rel(here, url)}"{cur}><span>{no}</span>{escape(name)}</a></li>')
            out.append("        </ol>")
        out.append("      </li>")
    out.append("    </ol>")
    out.append("  </nav>")

    if hints_html:
        out.append('  <div class="rail-hints" id="rail-hints">')
        # re-indent the hints the same way every run, so running the script twice changes nothing
        first, _, rest = hints_html.strip().partition("\n")
        out.append("    " + first)
        for line in textwrap.dedent(rest).split("\n"):
            out.append(("      " + line) if line.strip() else "")
        out.append("  </div>")

    out.append(
        f'  <a class="rail-tidy" href="https://github.com/TidyWeb" target="_blank" rel="noopener">'
        f'<img src="{root}assets/tidyweb_logo.png" alt=""><span><strong>TidyWeb</strong>'
        f"<small>View this project on GitHub</small></span></a>"
    )
    out.append("</aside>")
    return "\n".join(out)


def process(here):
    path = os.path.join(ROOT, page_path(here))
    with open(path, encoding="utf-8") as f:
        html = f.read()

    match = RAIL_RE.search(html)
    if not match:
        raise SystemExit(f"No rail found in {path}")
    hints = HINTS_RE.search(match.group(0))
    # the old per-section links inside some hint blocks are replaced by the route
    hints_html = SECTION_LINKS_RE.sub("", hints.group(0)) if hints else ""
    rail = build_rail(here, hints_html)
    indent = re.match(r"[ \t]*", match.group(0)).group(0)
    rail = "\n".join(indent + line if line else line for line in rail.split("\n"))
    html = html[: match.start()] + rail + html[match.end():]

    root = rel(here, "")
    if "rail.css" not in html:
        last_link = list(re.finditer(r'<link rel="stylesheet"[^>]*>', html, re.S))[-1]
        tag = f'\n{indent}<link rel="stylesheet" href="{root}assets/rail.css">'
        html = html[: last_link.end()] + tag + html[last_link.end():]

    html = OLD_SCRIPT_RE.sub("", html)
    html = html.replace("</body>", f'{indent}<script src="{root}assets/rail.js"></script>\n</body>', 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("rail written:", page_path(here))


def main():
    pages = []
    for stage in ROUTE:
        if not stage.get("barrier"):
            pages.append(stage["home"])
        pages.extend(url for _, _, url in stage["sheets"])
    for here in pages:
        process(here)


if __name__ == "__main__":
    main()
