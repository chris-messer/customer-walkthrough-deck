# Generated-deck architecture (conditional)

**Read this only if one of these is true:**

- The user explicitly asked for a generated / multi-file deck, or
- You are already standing in one. Detection cues, any one of which is decisive:
  - a `build.py` (or equivalent generator) at the repo root
  - a per-slide source directory such as `src/deck/slides/NN-stem.html`
  - an `outline.py` or equivalent declared section map
  - an output HTML file carrying a `GENERATED FILE — do not edit` banner

**Otherwise ship two hand-authored files.** The default in `SKILL.md` is correct for almost every deck; a build step is cumbersome and only pays for itself on a large, heavily interactive, multi-editor deck.

If you are in one of these repos: edit the sources and run the build. Never hand-edit a generated output — the next build overwrites it.

## What it buys, and what it costs

Buys: several agents or people editing different slides without collisions; counters, eyebrow numbers and the navigation rail generated from position instead of hand-maintained; a build that fails loudly when the deck and its notes drift apart.

Costs: a build command between every edit and every look at the result, four output files to keep straight, and a renumbering chore whenever slides move. Worth it at ~29 slides with interactive visuals. Not worth it at 12.

## Layout

```
build.py                     single build command
src/
  outline.py                 section / subsection map — the rail's only source
  deck/
    head.html                doctype, meta, title, D3 script tag
    chrome.html              progress bar + __RAIL__ marker + nav hint + notes button
    styles/
      base.css               tokens, slide shell, typography, footer
      components.css         shared components used by two or more slides
      rail.css               the position rail
      slides/NN-stem.css     per-slide styles, only when a slide needs its own
      responsive.css         narrow-viewport media query — emitted last so it wins
    slides/NN-stem.html      one file per slide: the whole <section class="slide">…</section>
    js/
      core.js                navigation, sync, progress, rail painting, slide registry
      shared.js              helpers used by two or more slides
      slides/NN-stem.js      per-slide viz + interaction, self-registering
  notes/
    NN-stem.js               one speaker-notes entry per slide, same stems as the slides
    _shell/                  notes head, body markup, styles, runtime
```

Outputs, all generated: `presentations/{slug}-walkthrough.html`, `presentations/{slug}-speaker-notes.html`, `index.html` (root copy of the deck, for GitHub Pages), and a root copy of the notes whose "open main deck" link points at `index.html`.

Scaffolding: [templates/generated-deck/build.py](templates/generated-deck/build.py) and [templates/generated-deck/outline.py](templates/generated-deck/outline.py). The rail's CSS and painting logic are the same as the single-file version in [templates/rail-snippet.html](templates/rail-snippet.html) — only the source of the map differs.

## Order and numbering

Slide order is the numeric filename prefix, sorted ascending. The build regenerates the footer counter (`NN / TOTAL`), the eyebrow number and the `data-slide-id` from **position in that order**, so no counter is ever hand-maintained.

**Gaps in prefixes are allowed on purpose.** Deleting `13-…` leaves `12` and `14` adjacent and the build just renumbers the displayed counters. That is what lets you avoid renumbering slides you do not own. The corollary: inserting between two adjacent numbers forces a cascade, so **leave gaps when first laying out a deck**.

## The outline is the rail's single source of truth

`src/outline.py` is the only place the hierarchy is written down. Nothing about it appears in per-slide markup, because hand-maintained navigation rots on the first reorder.

```python
OUTLINE = [
    ("Overview", [
        ("Opening", ["title", "agenda"]),
        ("Framing", ["framing", "graph-101", "semantic-layers"]),
    ]),
    ("Appendix", [
        ("The two decisions", ["problem-space"]),
    ]),
]
```

**Slides are named by stem** — the slug with its `NN-` ordering prefix removed — because prefixes get renumbered whenever slides move and a map keyed on them would rot on the next restructure. `title` means whichever file is currently `NN-title.html`.

The build fails, rather than drawing a wrong rail, when:

- a slide is missing from the map (the rail could not place it)
- a stem in the map has no matching slide
- a stem is listed twice
- the map's order disagrees with deck order — which would mean a subsection is not a contiguous run of slides, and the rail's slide-level pips would show non-neighbours

The speaker notes render their `Section › Subsection` breadcrumb from the same map, so presenter and audience views cannot disagree.

Rail sizing rules (short subsection names, pinned box, compact treatment for a sixth section) are in `SKILL.md` and apply identically here.

## Per-slide JS contract

`core.js` owns navigation and dispatch. A slide's module never touches it — it registers against its own slug and the core calls it back when that slide becomes active.

```js
/* src/deck/js/slides/07-taxonomy-storage-patterns.js */
DECK.registerViz('07-taxonomy-storage-patterns', (slide) => {
  // Runs once at boot, in slide order. Scope every query to `slide`.
  slide.querySelectorAll('.enc-chip').forEach(chip => {
    chip.addEventListener('click', (ev) => { ev.stopPropagation(); setEncoding(chip.dataset.enc); });
  });
  return {
    enter() {},      // optional · slide became active (also after a debounced resize)
    teardown() {},   // optional · slide stopped being active
  };
});
```

- The registered id **must** equal the filename slug, and the matching `src/deck/slides/<slug>.html` must exist. The build enforces both.
- Returning a bare function is shorthand for `{ enter }`. Returning nothing is fine for slides whose behaviour is all set up once.
- Put a helper in `shared.js` only when two or more slides need it.

## Build validation

`build.py` fails, printing every problem at once, when:

- a filename is not `NN-slug`
- two slides share a numeric prefix, or two share a slug
- slide count and notes count disagree
- a slide has no matching notes file, or a notes file has no matching slide
- notes are not in the same order as the slides
- a per-slide JS module has no `DECK.registerViz(...)` call, registers an unknown id, or registers an id that is not its own filename
- a per-slide CSS file has no matching slide
- any of the outline failures above
- `chrome.html` is missing its `__RAIL__` marker, or the notes runtime is missing its entry/crumb markers

It *notices* (prints, does not fail) when filename prefixes no longer match displayed position, and reports every counter it rewrote.

## Renumbering discipline

`NN-` prefixes reorder constantly, and a reorder touches four directories.

1. **Use `git mv`** so history follows the file.
2. **Renumber across all four directories** — `deck/slides/*.html`, `deck/styles/slides/*.css`, `deck/js/slides/*.js`, `notes/*.js`. Not every slide has CSS or JS; skip what does not exist rather than creating it.
3. **Update the `DECK.registerViz('NN-stem', …)` id** in every renamed module, and the `NN ·` prefix in its header comment. The build catches a mismatched id; it cannot catch a stale comment.
4. **Update the leading `<!-- NN · … -->` comment** in the slide markup. The build rewrites the counter and eyebrow number for you.
5. **Move through a temp prefix.** A reorder mapping usually contains a cycle (slide 5 becomes 23 while 23 becomes 18), so no single ascending or descending pass is safe. Rename everything to a temp prefix first, then to its final name, refusing to overwrite anything that already exists. Verify afterwards that nothing still wears the temp prefix and every file's prefix is in the target set.
6. **Sweep for forward references.** Moving a slide leaves "the next slide lays out…" pointers dangling in both slide copy and speaker notes.
7. Update `outline.py` only if the grouping changed — it is keyed on stems, so a pure renumber leaves it untouched. That is the point of keying on stems.

## Which files to touch

To change slide *N*, edit only these, so several agents can work on different slides simultaneously:

| Changing | File |
|---|---|
| Slide markup and copy | `src/deck/slides/NN-stem.html` |
| Slide-only styles | `src/deck/styles/slides/NN-stem.css` (create if absent) |
| Slide visuals and interactions | `src/deck/js/slides/NN-stem.js` (create if absent) |
| Speaker notes for that slide | `src/notes/NN-stem.js` |

Shared files — `core.js`, `shared.js`, `base.css`, `components.css`, `responsive.css`, `head.html`, `chrome.html`, `notes/_shell/` — affect every slide. Coordinate before editing them.

Then run the build.
