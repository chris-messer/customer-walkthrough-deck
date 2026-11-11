# Interactive visuals

Inline SVG inside the deck's single HTML file. D3 from a CDN `<script>` tag if the drawing needs it, otherwise hand-rolled DOM. No external chart library, no per-slide dependency, nothing that has to be built.

Interactivity is the strongest form of composition variety available: one figure the presenter re-reads several ways carries more than four static panels, and it gives the talk track somewhere to go.

## Wiring, in a single-file deck

Interactive slides need one thing the shared navigation already knows: when a slide becomes visible. Widths are meaningless until the slide is on screen, so draw on entry, not at load.

```js
const VIZ = {};                       // slide index → { enter, teardown }
function registerViz(i, setup) { VIZ[i] = setup(slides[i]) || {}; }

// inside show(index), after the active class is applied:
VIZ[prev]?.teardown?.();
requestAnimationFrame(() => VIZ[index]?.enter?.());
// and on a debounced window resize, call enter() again for the active slide
```

Each `setup(slide)` runs once, binds its buttons, and returns `{ enter, teardown }`. Scope every query to its own `slide` element so two slides can never collide. In a generated deck this is the same contract, just one file per slide — see [generated-deck-architecture.md](generated-deck-architecture.md).

## Shared helpers

Write these once near the top of the file rather than per slide:

```js
const C = { ink:'#1b3139', blue:'#2272b4', green:'#00a972', signal:'#ff3621',
            muted:'#52666d', dim:'#75868b', line:'#d7d6d1', faint:'#c9cecf',
            amber:'#b06000', danger:'#98102a', panel:'#ffffff' };

function newSvg(host) {                 // clears first, so a redraw replaces
  host.querySelectorAll('svg').forEach(s => s.remove());
  const r = host.getBoundingClientRect();
  const w = Math.max(160, r.width), h = Math.max(56, r.height);
  return { svg: d3.select(host).append('svg').attr('viewBox', `0 0 ${w} ${h}`), w, h };
}

function arrowDef(svg, id, color) { /* one <marker> per edge colour */ }
```

`panel` (white) is worth calling out: node marks and text get a paper-coloured stroke with `paint-order: stroke`, which haloes them so a label never has to compete with the line it sits over.

## Pattern 1 — one persistent visual, selectable states

The strongest pattern. One figure on one side, a rail of state buttons on the other, and a per-state info panel. Selecting a state moves and recolours the same elements rather than swapping in a new picture, so the audience keeps its bearings and the figure *becomes* the result instead of illustrating it.

Shape:

- One data set — nodes, links, rows — shared by every state.
- Per-state functions rather than per-state drawings: `radiusOf(state, d)`, `fillOf(state, d)`, `edgeStyle(state, d)`, `labelled(state, d)`.
- One pre-solved layout per state, computed once on `enter()`.
- A `paint(animate)` that transitions the existing selection into the new state's positions and styles, updates the legend and info panel, and rebuilds only the per-state annotations (group names, badges).

```js
const move = sel => (animate ? sel.transition().duration(520).ease(d3.easeCubicInOut) : sel);
move(node).attr('transform', d => `translate(${at.get(d.id).x},${at.get(d.id).y})`);
move(mark).attr('r', d => radiusOf(state, d)).attr('fill', d => fillOf(state, d));
```

Fade per-state annotations in *after* the marks arrive (`.transition().delay(300)`), so a badge never sits over an arrangement it does not describe.

## Pattern 2 — selectable card rail beside a changing stage

Cards stacked down the left, each a `<button>` with `aria-pressed`; on the right a stage with two declared tracks — an illustration over its detail rows. Selecting a card re-renders both tracks.

```css
.split { display: grid; grid-template-columns: minmax(0,296px) minmax(0,1fr); gap: 18px; }
.stage { display: grid; grid-template-rows: 392px 214px; gap: 10px; }   /* declared, not auto */
```

Key the stage content on the card's identity (`data-option="…"`), never on its position, so reordering the rail in markup carries the stage with it. Group the cards under short band labels when they fall into families — that turns the rail itself into the argument.

Nested toggles inside a selected state work well (a domain switcher inside one card's illustration, say), but they must preserve the same pinned geometry. Bind them when the illustration is rendered, and re-render through the same path.

## Fixed geometry is a hard requirement

Nothing content-sized may live in a multi-state region. Every state must occupy identical rects so the slide does not move as the presenter clicks — a stage that resizes shifts the card rail, and the audience loses the thread.

- Declare heights on stage tracks (`grid-template-rows: 392px 214px`), not `auto`.
- Inside an illustration, declare its internal rows too: `grid-template-rows: 40px 1fr 40px` for header / stage / caption, filled by every state.
- Reserve space for elements that appear in only some states rather than letting the box shrink when they are absent.
- Give a graph host `position: relative` and lay the SVG out absolutely inside it — a percentage-height SVG in an auto-height box is a sizing cycle:

```css
.gfx { position: relative; min-width: 0; min-height: 0; flex: 1; }
.gfx > svg { position: absolute; inset: 0; width: 100%; height: 100%; }
```

- Pin the one element that must be exact. If a layout means "this node is the centre", fix its coordinates rather than letting a collision force nudge it off.

## Deterministic layouts, not live force simulation

Re-running a force simulation on every click makes the figure jump-cut and re-roll; the same click twice gives two different pictures, and nothing about the drawing is worth asserting against.

Instead, solve once per state and transition between the solutions:

```js
function solve(w, h, state) {
  const nodes = NODES.map(n => ({ ...n }));            // never mutate the source
  nodes.forEach((d, i) => { /* seeded deterministic start, e.g. golden-angle spiral */ });
  const sim = d3.forceSimulation(nodes).stop()
    .force('collide', d3.forceCollide(d => radiusOf(state, d) + 8));
  /* per-state forces: radial for a ranking, x/y seats for clusters,
     fixed fx/fy for a route the layout must actually follow */
  for (let i = 0; i < 480; i++) sim.tick();            // tick to rest up front
  return new Map(nodes.map(d => [d.id, clampToPad(d)]));
}
```

`stop()` before ticking, a deterministic starting position, and `fx`/`fy` for anything whose place is part of the claim. Clamp final positions inside the padding so nothing lands under the caption. Keep transitions around half a second — this is a presentation, not a demo reel.

## Leave and return must redraw cleanly

`enter()` runs every time the slide becomes active and again after a resize. Clearing the host inside `newSvg` is what makes that safe: a redraw replaces rather than stacks. Keep selection state in a closure variable so returning to the slide shows the state the presenter left it in, and re-paint from that state rather than resetting to the default.

If a host is measured while the slide is still hidden it comes back zero-sized. Draw, then draw again on the next frame:

```js
paintNets();
requestAnimationFrame(paintNets);
```

## Draw a real network

When the point is that something is a graph, the picture has to be graph-shaped: branching, fan-out, edges that cross and share endpoints. A straight chain of circles is a flowchart with round corners and it undercuts the whole slide.

Instantiate the schema rather than drawing it. One node per type gives a line; two suppliers, three materials, three products and three customers gives a network where one supplier's reach is visibly partial. Derive the highlight from a real traversal over the edge list:

```js
function reachFrom(edges, seed) { /* BFS → { nodes:Set, edges:Set } */ }
```

Then style edges by membership in that set, so the drawing and the claim come from one computation.

## Multi-beat pipeline rows

A row of beats with labelled arrows between them — document excerpt → SQL statement → result rows → the same rows as a graph — is a good way to show a pipeline end to end, and the last beat earns its place by being the previous one redrawn.

Costs to watch:

- Each added beat compresses the row. Four beats plus three arrows is about the limit at deck scale.
- Give each beat an explicit column width in the grid template (`minmax(0,1.6fr) 50px minmax(0,1.2fr) …`) rather than letting content decide.
- **A `pre` block clips silently.** An overlong line vanishes instead of wrapping, so size the column to the widest line of the code, and indent the sample shallowly to keep that line short. Check the widest line specifically, not the block as a whole.
- `min-width: 0` on every grid child, or a long token blows the track out.

## Document facsimile

To make "this is a page from a real document" legible at a glance, draw the page rather than quoting it: a page-shaped white surface with a letterhead line, a metadata line in mono, greeked rules standing in for body text, the one passage that matters set in real type with the key phrase in `<mark>`, a folded corner, and two offset sheets behind it.

```css
.doc { position: relative; }
.doc::before, .doc::after { content:""; position:absolute; inset:0; background:var(--panel);
  border:1px solid var(--line); border-radius:3px; }
.doc::before { transform: translate(9px,9px); opacity:.45; }
.doc::after  { transform: translate(4.5px,4.5px); opacity:.7; }
.fold { position:absolute; top:-1px; right:-1px; width:0; height:0;
  border-left:17px solid transparent; border-top:17px solid var(--oat-2);
  filter: drop-shadow(-1px 1px 0 rgba(27,49,57,.14)); }   /* the crease, not a tint */
.line { height:5px; border-radius:3px; background:var(--oat-2); }  /* greeked body */
```

Pair it with a list of source documents as selectable buttons and swap the page's contents; the stack behind it says "there are more of these" without a caption.

## Accessibility and presenting

- Every control is a real `<button>` with `aria-pressed`; the panel it drives gets `aria-live="polite"`.
- `ev.stopPropagation()` in slide handlers so a click never also advances the deck.
- Blur a control after it is clicked, or it swallows the next Space — Space is a step key.
- Ignore step keys when focus is in `input, textarea, select`.
- Give small dots a generous invisible hit area; they have to stay quiet but be clickable mid-presentation.
- Respect `@media (prefers-reduced-motion: reduce)` by dropping transitions.
- Provide a narrow-viewport fallback that collapses the split to one column and lets the illustration scroll; fixed track heights are for the presenting size only.
