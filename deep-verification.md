# Deep verification (opt-in)

**Do not run this by default.** The four checks in `SKILL.md` are the normal gate. This battery is browser-driven, slow and fiddly; it earned its keep on a 29-slide deck with several interactive visuals, and it is disproportionate for a normal deck.

Run it when:

- the user asks for verification, or
- the deck is large or heavily interactive, and a wrong figure would be shown to a customer.

Most of what this battery caught is cheaper to prevent than to detect — see the **Accuracy discipline** section of `SKILL.md`. Derive labels from data and most of what follows finds nothing.

## The failure this exists to catch

Overflow and collision checks passed on a slide whose caption claimed a five-hop route while only four segments were drawn, because the fifth referenced an edge that did not exist in the visualization's own data. A second slide drew five tables against four path pills with nothing explaining the collapse. Both passed every geometric check, because no check ever compared the drawing to its own claims.

Both were possible because a count was hand-written while the drawing came from an array. And the first was doubly wrong: a breadth-first search showed the destination was four hops away, so "shortest path" was false regardless of the missing segment.

So the assertions below are the ones worth writing, in this order.

## 1. Caption versus drawing

For every state of every interactive slide, evaluate in the page and assert:

- Every number in a caption or badge equals a count of rendered elements.
- Every legend entry corresponds to something actually drawn in that state.
- Every label the caption names exists in the underlying data.
- A highlighted path is a real walk: consecutive pairs each correspond to an edge in the edge list, and the count of highlighted segments equals the claimed hop count.

```js
const drawn   = [...svg.querySelectorAll('line[stroke="#ff3621"]')].length;
const claimed = Number(caption.textContent.match(/(\w+) hops/)[1]);   // word or digit
const badges  = [...svg.querySelectorAll('.hop-badge')].length;
console.assert(drawn === badges && badges === claimed, { drawn, badges, claimed });
```

If the module keeps its path as a derived array (`PATH_LINKS = LINKS.filter(…)`), assert against that too — the fix for this class of bug is that the caption, the badges and the highlight all read from one list.

## 2. The claim itself

If a visual asserts a graph-theoretic or statistical property, compute it independently rather than trusting the label:

- "shortest path" → run a BFS over the edge list and compare the distance
- "most central", "largest cluster" → recompute the ranking from the same data
- "reaches N of M" → run the traversal and count

A route can be drawn entirely out of real edges and still not be the shortest one.

## 3. Geometry, per state

For each interactive slide, step through every state (and every nested toggle inside a state) and measure:

- Bounding rects of the stage tracks are identical across states — this is the fixed-geometry contract, and it is the one thing that is trivially machine-checkable.
- No element overflows its container: compare `scrollWidth`/`scrollHeight` against `clientWidth`/`clientHeight`.
- **`pre` blocks specifically.** They clip silently rather than wrapping, so an overlong line disappears. Measure the widest line, not the block.
- No text collisions: pairwise-intersect the rects of SVG `text` nodes and of adjacent labels.
- Nothing sits under the footer or the rail.
- Console is clean — no errors, no warnings from the drawing code.

```js
const eq = (a, b) => Math.abs(a - b) < 1;
// capture rects in state 1, click through the rail, compare in each subsequent state
```

## 4. Leave and return

Navigate away and back for each interactive slide, then assert:

- exactly one `svg` per host (a redraw that appends instead of replacing shows up here)
- the selected state is the one you left it in
- no duplicated annotation groups, badges or legend entries

Resize the window and re-check, since resize re-runs the same draw path.

## 5. Chrome will serve you a stale frame

Two separate problems, and the first fix does not solve the second.

- **Cache-bust the URL.** Load `file:///…/index.html?v=<timestamp>` (or a fresh query param per iteration) so you are not reading the previous build.
- **Force a repaint before capturing.** Stale frames get served showing a previous state even after the DOM has already changed. After changing state, force a reflow and wait for paint before screenshotting:

```js
document.body.style.transform = 'translateZ(0)';
void document.body.offsetHeight;
await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
document.body.style.transform = '';
```

If a screenshot disagrees with what a DOM query reports, believe the DOM query and repaint again.

## 6. Viewport versus design canvas

A browser viewport may cap below the deck's design canvas height, so measured figures will not match design targets. That is fine and it is one-directional: **if the content fits in the smaller measured viewport, it fits in the larger design canvas.** Record the measured viewport alongside any figure so the numbers are interpretable later, and do not "fix" a layout to match a measurement taken at the wrong height.

## 7. Publish verification

Compare a checksum of the fetched page against the local file:

```bash
shasum -a 256 index.html
curl -s https://<user>.github.io/<repo>/ | shasum -a 256
```

Do not grep the served page for strings. Anything the visualization modules generate at runtime is absent from the static HTML, so grep produces false negatives.

## Reporting

Report per slide and per state: what was asserted, what passed, what the measured viewport was. A pass with no assertions listed is not a pass — it is the shape of the bug this file exists to prevent.
