"""Write the shared route rail into every page of Python Practice Sheets.

Run from the repository root:  python3 tools/build_rail.py

Each page keeps its own hints. Everything else in the rail (the brand, the three
stages, the barrier and the TidyWeb credit) comes from ROUTE below, so the rail is
identical in shape on every page. Run it again after adding or renaming a sheet.
"""
import os
import re
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STAGE_ONE_HOME = "supplementary-sheets/car-park-practice-area/"
HOME = STAGE_ONE_HOME  # the beginning: the curly-f introduction

ROUTE = [
    {
        "no": "1", "name": "Supplementary sheets", "range": "01–05",
        "home": STAGE_ONE_HOME,
        "sheets": [
            ("01", "F-Prints", STAGE_ONE_HOME + "01-f-prints/"),
            ("02", "Building", STAGE_ONE_HOME + "02-building/"),
            ("03", "Reaching In", STAGE_ONE_HOME + "03-reaching-in/"),
            ("04", "Conditionals", STAGE_ONE_HOME + "04-conditionals/"),
            ("05", "Loops", STAGE_ONE_HOME + "05-loops/"),
        ],
    },
    {
        "no": "2", "name": "Combined sheets", "range": "06–11",
        "home": "combined-sheets/",
        "sheets": [
            ("06", "Library", "combined-sheets/06-combination-library/"),
            ("07", "Allotment", "combined-sheets/07-combination-allotment/"),
            ("08", "Market", "combined-sheets/08-combination-market/"),
            ("09", "Moorings", "combined-sheets/09-combination-moorings/"),
            ("10", "Buses", "combined-sheets/10-combination-buses/"),
            ("11", "Hall", "combined-sheets/11-combination-hall/"),
        ],
    },
    {
        "no": "3", "name": "Car park barrier", "range": "Final",
        "home": "car-park-practice-area/01-flow-control/",
        "barrier": True,
        "sheets": [
            ("01", "Worked example", "car-park-practice-area/01-flow-control/"),
            ("02", "Test", "car-park-practice-area/02-nesting/"),
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


def build_rail(here, hints_html):
    root = rel(here, "")
    current_stage = None
    for stage in ROUTE:
        if here == stage["home"] or any(here == s[2] for s in stage["sheets"]):
            current_stage = stage["no"]

    out = []
    out.append('<aside class="rail rail--route">')
    out.append(
        f'  <a class="route-brand" href="{rel(here, HOME)}" aria-label="Python Practice Sheets: start here">'
        f'<span class="brand-mark" aria-hidden="true"><span class="brand-brace brand-brace--left">{{</span>'
        f'<img src="{root}assets/curly-f-central.png" alt=""><span class="brand-brace brand-brace--right">}}</span></span>'
        f'<span class="route-brand-text"><small>Python practice</small><strong>Practice Sheets</strong></span></a>'
    )

    # where am I, for the small-screen route button
    where = "Start here"
    for stage in ROUTE:
        for no, name, url in stage["sheets"]:
            if url == here:
                where = f"{stage['no']} · {no} {name}"
        if here == stage["home"] and where == "Start here":
            where = f"{stage['no']} · {stage['name']}"
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
            f'<span class="stage-no">{stage["no"]}</span><span class="stage-name">{escape(stage["name"])}</span>'
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
        out.append("    " + hints_html.strip())
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
