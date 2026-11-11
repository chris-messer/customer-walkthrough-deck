#!/usr/bin/env python3
"""Assemble a walkthrough deck and its speaker notes from src/.

    python3 build.py

Set DECK_SLUG and DECK_TITLE below, then drop this at the repo root. It emits
four files, all generated — never hand-edit them:

    presentations/{slug}-walkthrough.html
    presentations/{slug}-speaker-notes.html
    index.html                       (root copy of the deck, for GitHub Pages)
    {slug}-speaker-notes.html        (root copy of the notes)

Slide order comes from the numeric filename prefix in src/deck/slides/. Footer
counters, eyebrow numbers, and the data-slide-id used by the per-slide JS
registry are all generated from that position, so no counter is ever
hand-maintained. Gaps in the prefixes are allowed on purpose; duplicates are an
error.

The position rail is generated from src/outline.py, which is the only place the
section/subsection hierarchy is written down. A slide missing from that map is a
build failure, not a silently wrong rail.

No dependencies. The outputs stay self-contained single-file HTML.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

DECK_SLUG = "your-deck"          # filenames + BroadcastChannel name
DECK_TITLE = "Your Deck"         # only used in the build log

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DECK_SRC = SRC / "deck"
NOTES_SRC = SRC / "notes"

BANNER = (
    "<!-- GENERATED FILE — do not edit.\n"
    "     Source lives in src/. Rebuild with: python3 build.py -->"
)

NAME_RE = re.compile(r"^(\d{2})-([a-z0-9][a-z0-9-]*)$")

errors: list[str] = []
notices: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def read(path: Path) -> str:
    return path.read_text().rstrip("\n")


def indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.split("\n"))


def load_outline() -> list:
    spec = importlib.util.spec_from_file_location("outline", SRC / "outline.py")
    if spec is None or spec.loader is None:
        sys.exit("build: cannot load src/outline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.OUTLINE


def numbered(directory: Path, suffix: str) -> list[tuple[int, str, Path]]:
    """Every NN-slug file in a directory, ordered by NN."""
    out = []
    for path in sorted(directory.glob(f"*{suffix}")):
        match = NAME_RE.match(path.name[: -len(suffix)])
        if not match:
            fail(f"{path.relative_to(ROOT)}: filename must look like NN-slug{suffix}")
            continue
        out.append((int(match.group(1)), path.name[: -len(suffix)], path))
    out.sort(key=lambda item: item[0])
    return out


# ── inventory ──────────────────────────────────────────────────────────────
slides = numbered(DECK_SRC / "slides", ".html")
if not slides:
    sys.exit("build: no slides found in src/deck/slides/")

total = len(slides)
prefixes = [n for n, _, _ in slides]
# Gaps are allowed on purpose: deleting a slide must not force a renumber of
# every slide after it. Displayed position is the ordinal, not the prefix.
duplicates = sorted({n for n in prefixes if prefixes.count(n) > 1})
if duplicates:
    fail("two slides share the numeric prefix " + ", ".join(f"{n:02d}" for n in duplicates))
if len({slug for _, slug, _ in slides}) != total:
    fail("two slides share the same slug")
drifted = [(slug, i) for i, (n, slug, _) in enumerate(slides, start=1) if n != i]
if drifted:
    notices.append(
        "filename prefixes no longer match deck position (harmless — counters "
        "follow position): " + ", ".join(f"{slug} shows as {i:02d}" for slug, i in drifted)
    )

slide_ids = [slug for _, slug, _ in slides]

notes = numbered(NOTES_SRC, ".js")
note_ids = [slug for _, slug, _ in notes]
if len(notes) != total:
    fail(f"slide count ({total}) does not match speaker-notes entry count ({len(notes)})")
for slug in slide_ids:
    if slug not in note_ids:
        fail(f"slide '{slug}' has no matching notes file src/notes/{slug}.js")
for slug in note_ids:
    if slug not in slide_ids:
        fail(f"notes file '{slug}.js' has no matching slide src/deck/slides/{slug}.html")
if note_ids[: len(slide_ids)] != slide_ids and not errors:
    fail("notes files are not in the same order as the slides")

slide_js = numbered(DECK_SRC / "js" / "slides", ".js")
REGISTER_RE = re.compile(r"DECK\.registerViz\(\s*['\"]([^'\"]+)['\"]")
for _, slug, path in slide_js:
    if slug not in slide_ids:
        fail(f"{path.relative_to(ROOT)}: no slide src/deck/slides/{slug}.html exists")
    ids = REGISTER_RE.findall(path.read_text())
    if not ids:
        fail(f"{path.relative_to(ROOT)}: no DECK.registerViz(...) call found")
    for registered in ids:
        if registered not in slide_ids:
            fail(f"{path.relative_to(ROOT)}: registers unknown slide id '{registered}'")
        elif registered != slug:
            fail(
                f"{path.relative_to(ROOT)}: registers '{registered}' but the file is "
                f"named '{slug}' — they must match"
            )

slide_css = numbered(DECK_SRC / "styles" / "slides", ".css")
for _, slug, path in slide_css:
    if slug not in slide_ids:
        fail(f"{path.relative_to(ROOT)}: no slide src/deck/slides/{slug}.html exists")


# ── outline: every slide accounted for, exactly once, in deck order ────────
# The rail lies to the audience if this map drifts from the deck, so drift is a
# hard failure rather than a notice.
OUTLINE = load_outline()

# A stem is the slug without its NN- ordering prefix, which is the part that
# survives a renumber.
stem_of = {slug: slug.split("-", 1)[1] for slug in slide_ids}
deck_stems = [stem_of[slug] for slug in slide_ids]
if len(set(deck_stems)) != len(deck_stems):
    duped = sorted({s for s in deck_stems if deck_stems.count(s) > 1})
    fail("two slides share a stem, so the outline cannot address them: " + ", ".join(duped))

outline_stems: list[str] = []
outline_where: dict[str, tuple[str, str]] = {}
for section_name, subsections in OUTLINE:
    if not subsections:
        fail(f"outline section '{section_name}' has no subsections")
    for sub_name, stems in subsections:
        if not stems:
            fail(f"outline subsection '{section_name} / {sub_name}' lists no slides")
        for stem in stems:
            if stem in outline_where:
                first = outline_where[stem]
                fail(
                    f"outline lists '{stem}' twice — in '{first[0]} / {first[1]}' and "
                    f"again in '{section_name} / {sub_name}'"
                )
                continue
            outline_where[stem] = (section_name, sub_name)
            outline_stems.append(stem)

for stem in outline_stems:
    if stem not in deck_stems:
        fail(
            f"src/outline.py lists '{stem}' but no slide src/deck/slides/NN-{stem}.html "
            "exists — remove it from the outline or add the slide"
        )
missing = [stem for stem in deck_stems if stem not in outline_where]
if missing:
    fail(
        "these slides are not in src/outline.py, so the position rail cannot place "
        "them: " + ", ".join(missing) + " — add each one to a subsection"
    )

# Order has to agree, or a subsection is not a contiguous run of slides and the
# rail's third level would show pips that are not neighbours.
if not missing and not errors and outline_stems != deck_stems:
    disagreements = [
        f"position {i:02d} is '{deck}' but the outline has '{out}'"
        for i, (deck, out) in enumerate(zip(deck_stems, outline_stems), start=1)
        if deck != out
    ]
    fail(
        "src/outline.py is not in deck order, so at least one subsection is not a "
        "contiguous run: " + "; ".join(disagreements[:4])
    )

if errors:
    print("build failed:", file=sys.stderr)
    for err in errors:
        print(f"  · {err}", file=sys.stderr)
    sys.exit(1)


# ── slide markup ───────────────────────────────────────────────────────────
SECTION_RE = re.compile(r'(<section\s+class="[^"]*")((?:\s+data-slide-id="[^"]*")?)')
COUNTER_RE = re.compile(r'(<span class="counter">)([^<]*)(</span>)')
EYEBROW_NUM_RE = re.compile(r'(<span class="num">)([^<]*)(</span>)')
LEAD_COMMENT_RE = re.compile(r"^(\s*<!--\s*)(\d+)(\s*·)")

rewrites: list[str] = []
slide_markup: list[str] = []

for position, (_, slug, path) in enumerate(slides, start=1):
    body = read(path)
    nn = f"{position:02d}"

    body, count = SECTION_RE.subn(rf'\1 data-slide-id="{slug}"', body, count=1)
    if count != 1:
        sys.exit(f"build: {path.relative_to(ROOT)} has no <section class=\"slide …\"> element")

    def stamp(regex: re.Pattern[str], value: str, label: str, text: str, slug=slug) -> str:
        def repl(match: re.Match[str]) -> str:
            if match.group(2) != value:
                rewrites.append(f"{slug}: {label} '{match.group(2)}' → '{value}'")
            return f"{match.group(1)}{value}{match.group(3)}"
        return regex.sub(repl, text)

    body = stamp(COUNTER_RE, f"{nn} / {total:02d}", "counter", body)
    body = stamp(EYEBROW_NUM_RE, nn, "eyebrow number", body)
    body = LEAD_COMMENT_RE.sub(rf"\g<1>{nn}\g<3>", body)
    slide_markup.append(body)


# ── position rail ──────────────────────────────────────────────────────────
HEADLINE_RE = re.compile(r"<h[12][^>]*>(.*?)</h[12]>", re.S)
BREAK_RE = re.compile(r"<br\s*/?>", re.I)
TAG_RE = re.compile(r"<[^>]+>")
ENTITIES = {
    "&ldquo;": "\u201c", "&rdquo;": "\u201d", "&lsquo;": "\u2018", "&rsquo;": "\u2019",
    "&mdash;": "\u2014", "&ndash;": "\u2013", "&hellip;": "\u2026", "&nbsp;": " ",
    "&rarr;": "\u2192", "&times;": "\u00d7", "&lt;": "<", "&gt;": ">", "&amp;": "&",
}


def headline(markup: str) -> str:
    """The slide's own headline, plain, for the pip's hover label."""
    match = HEADLINE_RE.search(markup)
    if not match:
        return ""
    text = BREAK_RE.sub(" ", match.group(1))
    text = TAG_RE.sub("", text)
    for entity, char in ENTITIES.items():
        text = text.replace(entity, char)
    text = " ".join(text.split())
    return text if len(text) <= 78 else text[:77].rstrip() + "\u2026"


def attr(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;").replace('"', "&quot;"))


position_of = {stem_of[slug]: i for i, slug in enumerate(slide_ids, start=1)}
headline_of = {stem_of[slug]: headline(markup)
               for slug, markup in zip(slide_ids, slide_markup)}

rail_lines = ['  <nav class="rail" aria-label="Where you are in the deck">']
# Per-slide breadcrumb, handed to the speaker notes so both views agree.
crumbs: list[tuple[str, str]] = [("", "")] * total

for section_name, subsections in OUTLINE:
    sec_stems = [stem for _, stems in subsections for stem in stems]
    sec_from, sec_to = position_of[sec_stems[0]], position_of[sec_stems[-1]]
    rail_lines.append(f'    <div class="rail-sec" data-from="{sec_from}" data-to="{sec_to}">')
    rail_lines.append(
        f'      <button type="button" class="rail-sname" data-slide="{sec_from}">'
        f'{attr(section_name)}<i class="rail-fill"></i></button>'
    )
    rail_lines.append('      <div class="rail-subs">')
    for sub_name, stems in subsections:
        sub_from, sub_to = position_of[stems[0]], position_of[stems[-1]]
        rail_lines.append(f'        <div class="rail-sub" data-from="{sub_from}" data-to="{sub_to}">')
        rail_lines.append(
            f'          <button type="button" class="rail-uname" data-slide="{sub_from}">'
            f'{attr(sub_name)}</button>'
        )
        rail_lines.append('          <div class="rail-pips">')
        for stem in stems:
            n = position_of[stem]
            crumbs[n - 1] = (section_name, sub_name)
            label = headline_of[stem] or sub_name
            rail_lines.append(
                f'            <button type="button" class="rail-pip" data-slide="{n}" '
                f'title="{attr(f"{n:02d} · {label}")}" '
                f'aria-label="{attr(f"Slide {n} of {total}: {label}")}"><i></i></button>'
            )
        rail_lines.append('          </div>')
        rail_lines.append('        </div>')
    rail_lines.append('      </div>')
    rail_lines.append('    </div>')
rail_lines.append('  </nav>')

chrome = read(DECK_SRC / "chrome.html")
if "__RAIL__" not in chrome:
    sys.exit("build: src/deck/chrome.html is missing the __RAIL__ marker")
chrome = chrome.replace("__RAIL__", "\n".join(rail_lines))


# ── stylesheet ─────────────────────────────────────────────────────────────
css_parts = [read(DECK_SRC / "styles" / "base.css"),
             read(DECK_SRC / "styles" / "components.css"),
             read(DECK_SRC / "styles" / "rail.css")]
css_parts += [read(path) for _, _, path in slide_css]
# emitted last so the narrow-viewport fallback wins on ties
css_parts.append(read(DECK_SRC / "styles" / "responsive.css"))
css = indent("\n\n".join(css_parts), 4)


# ── script ─────────────────────────────────────────────────────────────────
js_parts = [read(DECK_SRC / "js" / "core.js"), read(DECK_SRC / "js" / "shared.js")]
js_parts += [read(path) for _, _, path in slide_js]
js_parts.append("DECK.boot();")
js = indent("\n\n".join(js_parts), 6)

deck_head = read(DECK_SRC / "head.html").split("\n")
deck_html = "\n".join(
    [deck_head[0], BANNER, *deck_head[1:], "  <style>", css, "  </style>", "</head>", "<body>",
     '  <main class="deck" aria-live="polite">', ""]
    + [f"{markup}\n" for markup in slide_markup]
    + ["  </main>", "", chrome, "", "  <script>", "    (() => {",
       js, "    })();", "  </script>", "</body>", "</html>", ""]
)


# ── speaker notes ──────────────────────────────────────────────────────────
notes_entries = "\n\n".join(read(path) for _, _, path in notes)
notes_runtime = read(NOTES_SRC / "_shell" / "runtime.js")
for marker in ("__NOTES_ENTRIES__", "__OUTLINE_CRUMBS__"):
    if marker not in notes_runtime:
        sys.exit(f"build: src/notes/_shell/runtime.js is missing the {marker} marker")
notes_runtime = notes_runtime.replace("__NOTES_ENTRIES__", notes_entries)
# The notes show the same Section › Subsection breadcrumb as the deck rail, from
# the same map, so the presenter view can never disagree with the audience view.
crumbs_js = ",\n  ".join(
    "['{}', '{}']".format(sec.replace("'", "\\'"), sub.replace("'", "\\'"))
    for sec, sub in crumbs
)
notes_runtime = notes_runtime.replace("__OUTLINE_CRUMBS__", f"[\n  {crumbs_js},\n]")

notes_head = read(NOTES_SRC / "_shell" / "head.html").split("\n")
notes_html = "\n".join(
    [notes_head[0], BANNER, *notes_head[1:], "  <style>",
     indent(read(NOTES_SRC / "_shell" / "notes.css"), 4), "  </style>", "</head>", "<body>",
     read(NOTES_SRC / "_shell" / "body.html"), "", "  <script>", "    (() => {",
     indent(notes_runtime, 6), "    })();", "  </script>", "</body>", "</html>", ""]
)


# ── emit ───────────────────────────────────────────────────────────────────
DECK_LINK_RE = re.compile(r'(id="deck-link"\s+href=")([^"]*)(")')

outputs = {
    ROOT / "presentations" / f"{DECK_SLUG}-walkthrough.html": deck_html,
    ROOT / "presentations" / f"{DECK_SLUG}-speaker-notes.html": notes_html,
    # Root copies are what GitHub Pages serves; there the deck is index.html.
    ROOT / "index.html": deck_html,
    ROOT / f"{DECK_SLUG}-speaker-notes.html": DECK_LINK_RE.sub(r"\1index.html\3", notes_html),
}
for path, text in outputs.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

print(f"built {DECK_TITLE}: {total} slides · {len(notes)} notes entries · "
      f"{len(slide_js)} slide modules")
for line in notices:
    print(f"  note: {line}")
for line in rewrites:
    print(f"  renumbered {line}")
for path in outputs:
    print(f"  → {path.relative_to(ROOT)}")
