# Design system — customer walkthrough decks

Distilled from reference walkthrough slides.

## Palette

```css
:root {
  --ink: #1B3139;
  --muted: #52666D;
  --dim: #75868B;
  --oat: #F9F7F4;
  --oat-2: #EEEDE9;
  --panel: #FFFFFF;
  --line: #D7D6D1;
  --signal: #FF3621;   /* coral/lava — sparingly */
  --blue: #2272B4;
  --green: #00A972;
  --danger: #98102A;
  --amber: #B06000;    /* the "look at this one" class in a chart */
  --display: "DM Sans", "Avenir Next", "Inter", sans-serif;
  --body: "Inter", "DM Sans", "Avenir Next", sans-serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
```

### Usage

- **Background:** oat gradient + optional faint grid; light canvas default
- **Accent:** coral for eyebrows, progress bar, key numbers, one emphasis word — never rainbow
- **Blue:** secondary labels, transitions, analogies
- **Green:** verified / positive status labels
- **Dark red:** danger / hard-boundary side of honesty splits
- **Amber:** the one weak result in a set you are being honest about
- **Mono:** identifiers, keys, code, metadata lines — anything the audience should read as literal
- **Avoid:** yellow/gold unless user asks; purple gradients; cream `#F4F1EA` + terracotta; glow-heavy dark mode

## Typography & density

| Element | Rule |
|---|---|
| Headline | ≤ ~8 words; large DM Sans; tight tracking |
| Framing / lead | One sentence; muted; max ~1120px wide |
| Bullets | 4–6 max; ~10–14 words; ≤ ~2 lines each |
| Body on slide | Prefer labels + short phrases over paragraphs |
| Metrics | Big coral numbers + uppercase dim labels |

## Layout building blocks

Reuse these patterns:

| Pattern | When |
|---|---|
| Title slide | Brand overline, huge name, one subtitle, meta row |
| Agenda | Numbered two-column list |
| Rule-block grid (2/3/4) | Parallel concepts |
| Architecture / flow stages | Left→right pipeline with arrows |
| Boundary split | Soft vs hard / honesty framing |
| Metric row | Measured facts |
| Demo question cards | Live demo prompts |
| Close line + next steps | Ask / pilot path |
| Selectable card rail + stage | Comparing options that each deserve their own illustration |
| Persistent visual, selectable states | One figure the presenter re-reads several ways |
| Document facsimile | "This is a page from a real document" has to land instantly |
| Two halves with a central hinge | Two lanes that both turn on one shared element |
| Multi-beat pipeline row | Showing a pipeline end to end (excerpt → statement → rows → result) |

Footer every slide: brand left, `NN / TOTAL` right. Thin coral accent bar top-right of each slide. Progress bar at bottom. When navigation is in scope, use the graph SME three-level position rail already wired into the deck shell: pinned `1060px × 34px` chrome, section tracks → active subsection → slide pips, with the matching notes breadcrumb derived from `OUTLINE` — see `SKILL.md`.

## Section openers

A chapter break is carried by scale and motion, never by a colour shift. An opener sits on exactly the same paper as a content slide:

- Headline about half again the size of a content-slide `h2`, deeper top padding
- The corner accent bar goes full-bleed (`width: 100%`) instead of the usual ~28%
- A giant ghosted section mark behind the content at ~4% ink
- An entrance: the coral rule wipes across, then the eyebrow and headline rise
- **No panel fills.** Content sits directly on the canvas, separated by hairlines instead of white cards; run the hairline a shade darker on openers since it is carrying all the structure

## Multi-state geometry

Any region that changes with a click must be a declared size, not a content size, or the slide moves under the presenter. Declare stage track heights, reserve space for elements that appear in only some states, and pin any chrome (like the position rail) so it cannot key off the active slide. Details in [interactive-visuals.md](interactive-visuals.md).

## Slide authoring rules

1. **One idea per slide** — if you need "and", split
2. **Visual over paragraphs** — diagram/grid first; text supports
3. **Standalone-readable** — someone glancing the shared screen gets the point without audio
4. **16:9 feel** — full-viewport sections; generous padding (`clamp`)
5. **No build step** — single HTML file, inline CSS/JS. Interactive visuals and the position rail both live inside this; a large deck generated from per-slide sources is a documented exception, not the norm
6. **Customer-safe** — no internal Slack refs; no overclaim
7. **Cut, then rebalance** — slides routinely lose 50–65% of their copy. The right response to the leftover space is whitespace, not more prose

## Optional chrome

- **Open speaker notes** button (always for dual-monitor presenting)
- **Launch demo** CTA (only if a real app URL exists)
- Help overlay on `?` (optional)
- Print: each `.slide` as a page

## What not to put on slides

- Full spoken paragraphs (those belong in notes `say`, starting directly with spoken content)
- Eval scorecards / agent-vs-agent tables unless asked
- Dense cost tables without a clear punchline
- Time or effort estimates on option cards (no "2–4 weeks", no Low/Medium/High badges) unless asked
- Counts that assert a set is closed ("five ways to…") when it is not
