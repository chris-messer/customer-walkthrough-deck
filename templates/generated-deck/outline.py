"""Section / subsection map for the deck's position rail.

This is the single source of truth for the rail at the top of every slide. Add,
move or regroup slides here and `build.py` regenerates the rail; nothing about
the hierarchy is written into per-slide markup.

Slides are named by their **stem** — the filename slug with its `NN-` ordering
prefix removed — because those prefixes get renumbered whenever slides move and
a map keyed on them would rot on the next restructure. `title` here means
whichever file is currently `NN-title.html`.

build.py fails the build if a slide is missing from this map, listed twice,
listed but nonexistent, or if the order here disagrees with the deck order
(which would mean a subsection is not a contiguous run of slides).

Subsection names should be one or two words. The rail is a horizontal band with
finite width, and short names let it carry the organizing division as a visible
label rather than a sentence about it.

Shape:  [ (section, [ (subsection, [stem, ...]), ... ]), ... ]
"""

OUTLINE = [
    ("Overview", [
        ("Opening", [
            "title",
            "agenda",
        ]),
        ("Framing", [
            "framing",
            "vocabulary",
        ]),
    ]),

    ("The need", [
        ("What it is", [
            "need-overview",
        ]),
        # One word each, so the rail carries the division rather than
        # describing it.
        ("Build", [
            "build-and-retrieve",
            "build-options",
        ]),
        ("Retrieve", [
            "retrieve-options",
            "recommendation",
        ]),
    ]),

    ("Next steps", [
        ("Where you land", [
            "ladder",
        ]),
        ("Discussion", [
            "discussion",
            "close",
        ]),
    ]),

    # Everything after the close. The rail renders a section per entry, so an
    # appendix is just one more — it draws itself, and rail.css gives the last
    # section a compact treatment so the labels still fit the band.
    ("Appendix", [
        ("Detail", [
            "problem-space",
        ]),
    ]),
]
