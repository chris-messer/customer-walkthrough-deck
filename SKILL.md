---
name: customer-walkthrough-deck
description: >-
  Turns a project and/or chat history into a customer-facing HTML walkthrough
  deck plus synced speaker-notes companion. Use
  when the user asks for a walkthrough deck, speaker notes, customer
  presentation, HTML slides, github.io presentation, screen-share notes,
  interactive slide visuals, or sparse walkthrough slides. Ships two self-contained
  HTML files with BroadcastChannel sync for dual-monitor presenting.
---

# Customer Walkthrough Deck

Build a sparse, customer-facing HTML slide deck and a synced speaker-notes window in a sparse, one-idea-per-slide style.

## When to use

User wants a walkthrough deck, speaker notes, customer presentation, HTML slides, github.io deck, interactive slide visuals, or screen-share + second-monitor notes from a project/chat.

## Workflow

### 1. Plan first (unless user says build immediately)

Propose before writing HTML:

- Slide list (title → close, ~10–16 slides typical)
- **Composition map** — assign a layout type to every slide before writing HTML; confirm no two adjacent slides share the same layout and at least 6 distinct layouts appear in a 10–12 slide deck
- Audience + brand line (e.g. `Databricks × Acme`)
- Product/deck name (slug for filenames + sync channel)
- Whether to include: cost/calculator, live demo CTA, interactive visuals, navigation rail

Confirm with the user, then gather material.

### 2. Gather source material

Extract from chat history, transcripts, READMEs, notebooks, app URLs, eval results:

| Capture | Use on |
|---|---|
| Customer problem / recurring pain | Early problem slides |
| What was built (honest scope) | Architecture / system slides |
| Trust, eval, limitations | Honesty / boundary slides |
| Demo sequence + prompts | Live demo slide + notes |
| Next steps / ask | Close |

Prefer customer language over internal jargon. No Slack citations on the customer deck.

### 3. Author sparse slides

Rules — see [design-system.md](design-system.md):

- One idea per slide
- Headline ≤ ~12 words; must describe the slide's subject and conclusion
- One short framing/lead line
- Visual over paragraphs (flow, grid, metrics, boundary split, interactive figure)
- Light oat canvas; coral accent sparingly
- On-slide text is scannable — full talk track lives in notes

### 4. Write speaker notes (do NOT duplicate slide text)

Per slide, notes must include dual-track talk content plus prep:

1. **Cues** — scannable live-reference: section labels + short bullets, derived from the pitch (not a chopped-up paragraph)
2. **Say this** — full conversational spoken paragraph; the `say` field *is* the spoken text (do not wrap in "Here's how I'd say it:" / "Here's how I'd open:")
3. **Transition** — bridge to the next slide (placement moves with the cues/script cluster by mode — see cadence)
4. **Purpose** — one line: what this slide must accomplish for the audience
5. Optional **Key nuance** — honesty callout, edge case, or internal context for presenter
6. Optional **Discovery questions** — open-ended questions to surface customer context (see below)
7. Optional **How to demo live** — for an interactive slide, name the clicks in order

Notes UI: Both / Cues / Full script toggle (default Both); transition sits between cues and say in Both, under cues in Cues mode, under say in Full script mode. Prep blocks stay below that cluster. Full rules: [speaker-notes-cadence.md](speaker-notes-cadence.md).

Notes are the talk track; slides are the visual.

### 5. Ship two HTML files

Under the project, create `presentations/`:

```
presentations/
├── {slug}-walkthrough.html    # or index.html if publishing to github.io
└── {slug}-speaker-notes.html
```

Bootstrap from:

- [templates/deck-shell.html](templates/deck-shell.html)
- [templates/notes-shell.html](templates/notes-shell.html)

Wire sync from [sync-template.md](sync-template.md):

- Same `CHANNEL` and `STORAGE_KEY` in both files (derive from slug)
- Same slide count / index order
- Deck: "Open speaker notes" button
- Both: ← → Space navigation; BroadcastChannel + localStorage fallback

Two self-contained files, no build step, inline CSS/JS. Interactive visuals and the navigation rail below both work inside this — neither needs a build.

### 6. Optional extras (only if relevant / asked)

- Demo CTA button → live app URL
- Interactive calculator / widgets (keep honest about estimates)
- GitHub Pages publish — **only if user asks** (see Publishing)

## If the deck is already multi-file

Some large decks are generated from per-slide sources instead of hand-authored. **Only** if the user explicitly asks for a generated deck, or the repo already works that way, see [generated-deck-architecture.md](generated-deck-architecture.md) — do not introduce a build step otherwise.

Detection cues, any one of which means you are in a generated deck: a `build.py` (or equivalent) at the repo root; a per-slide source directory such as `src/deck/slides/NN-stem.html`; an `outline.py` or equivalent section map; an output file carrying a `GENERATED FILE` banner. In that case edit the sources and rebuild — never hand-edit generated output.

## Navigation rail

A rail showing sections, subsections and current position earns its place on a long deck, any deck with real chapters, or whenever the user asks for the graph SME navigation. The deck and notes shells ship with that implementation wired in; remove it only when the agreed composition explicitly omits navigation.

The canonical visual is the graph SME three-level rail: top-level sections in small caps on 2px progress tracks, the active section's subsections after a chevron, and the active subsection's slides as clickable pips inside one pill. Passed sections fill; the current pip uses the coral signal token. Title and close slides remain visually bare, but still belong to the map.

**Declare the hierarchy once**, as a JavaScript array beside the deck constants, and render the rail from it. In the separately self-contained notes HTML, mirror the same array exactly and derive its `Section › Subsection` breadcrumb from it. For generated decks, define it once in the source map and generate both views:

```js
const OUTLINE = [
  ['Overview',   [['Opening', [0, 1]], ['Framing', [2, 3, 4]]]],
  ['Options',    [['What it is', [5]], ['Build', [6, 7]], ['Retrieve', [8, 9]]]],
  ['Next steps', [['Where you land', [10]], ['Discussion', [11, 12]]]],
];
```

Rules that make it survive editing:

- **One source of truth.** Hand-maintained navigation written into each slide's markup rots on the first reorder. Nothing about the hierarchy belongs in per-slide markup.
- **Every slide appears exactly once**, and each subsection is a contiguous run in deck order. Assert all three conditions at boot and throw after logging the full failure list — a rail that lies is worse than no rail.
- **Subsection names must be short.** The rail is a horizontal band with finite width; one- or two-word names let it carry the organizing division as a visible label.
- **Pin the box, not the active contents.** The graph SME geometry is a `1060px × 34px` fixed box at `top: clamp(24px, 3.2vw, 56px)`, with the right edge on the slide gutter and a fixed left origin. Expansion grows rightward inside that box, so passed sections never move and section-opener padding cannot make the rail jump.
- **Degrade without reflow.** Below `1480px`, keep only the section spine and right-align it; below the mobile breakpoint, hide the rail. The rail costs slide content no vertical space.
- **Appendix treatment is semantic.** A section named `Appendix` receives the compact label/no-track treatment. Do not style the last section as an appendix merely because it is last.
- **All levels are clickable.** Section and subsection labels jump to their first slide; pips jump directly. Blur rail buttons after click so focused controls do not swallow the next Space navigation step.
- **Notes use the hierarchy.** Render `Section › Subsection` from the matching OUTLINE rather than storing a breadcrumb on each note.

Canonical annotated CSS + JS: [templates/rail-snippet.html](templates/rail-snippet.html). The working integration is already present in [templates/deck-shell.html](templates/deck-shell.html) and [templates/notes-shell.html](templates/notes-shell.html).

## Interactive visuals

Inline SVG, drawn with D3 or hand-rolled JS inside the same file. No per-slide dependency, no external chart libraries. Two proven patterns:

- **One persistent visual with selectable states** — a single figure, a rail of state buttons, elements that move and recolour per selection, plus a per-selection info panel. One network read four ways beats four small multiples.
- **Selectable card rail beside a changing stage** — cards stacked left; a fixed-height illustration track over a fixed-height detail track on the right.

Non-negotiables:

- **Fixed geometry.** Every state must occupy identical rects so the slide does not jump as the presenter clicks. Declared track heights, never content-sized ones, and reserve space for elements that appear in only some states.
- **Deterministic layouts, not live force simulation.** Pre-solve one arrangement per state and transition between them. Re-running a simulation on each click makes the figure jump-cut and re-roll; transitioning between solved states is what reads as rearranging rather than redrawing. Keep transitions quick — this is a presentation, not a demo reel.
- **Leave and return must redraw cleanly** — one SVG, state retained, no duplicated elements.
- **Show a real network** when illustrating a graph: branching, fan-out, edges that cross and share endpoints. A straight chain of circles is still a flowchart. Instantiate a schema with realistic multiplicity rather than one node per type.
- Nested toggles inside a selected state are fine, but they must preserve the pinned geometry too.

Patterns, geometry recipes and failure modes: [interactive-visuals.md](interactive-visuals.md).

## Accuracy discipline

Cheap habits that prevent the bugs that actually ship. These are authoring rules, not a verification pass.

- **Derive captions, counts, badges and legends from the same data the visual is drawn from.** A hand-typed "five hops" beside a path drawn from an array will eventually disagree with it. Compute the caption.
- **Everything a visual references must exist in its own data.** A highlighted path must be a real walk over the drawn edges; a legend entry must correspond to something rendered.
- **If a visual asserts a property — a shortest path, a count, a ranking, a reachable set — compute it.** A "shortest path" label is a claim about the graph, and it can be false even when every segment drawn is real.
- **Check external capability claims against primary documentation.** A vendor claim the vendor's own docs contradict will propagate into several descriptions before anyone notices. If a heading and a headline disagree on a factual point, fix the heading rather than weakening the honest statement.
- **After any reorder, sweep for dangling references to neighbours.** "The next slide lays out…" pointers go stale in both slide copy and speaker notes.

## Composition variety

A deck must not repeat the same "title + 3 cards" layout across most slides. Maintain one design system while varying hierarchy, density, alignment, and information shape. Interactivity is itself a form of composition variety — a selectable slide reads differently from a static one at the same density.

| Layout type | Description |
|---|---|
| Metric-led statement | 3 large numbers that make the problem visceral |
| Before/after split (fork) | Two strategic paths or states side-by-side |
| Architecture flow | Sequential pipeline stages with labeled nodes |
| Side-by-side comparison | Two options with same-dimension rows |
| Per-source / scale pattern | Inline flow + 2–3 supporting panels below |
| Phased roadmap | 3-column phase track with numbered headers |
| Boundary / parameter matrix | Table: topic + deployment implication |
| Two-lane cost model | Independent cost lanes with drivers + sizing footer |
| Proof / status grid | Two-column checklist with check circles |
| Discussion slide | Left: ask/proposal · Right: numbered open questions |
| Minimal close (title style) | Large type, overline, subtitle, meta — no body |
| Selectable card rail + stage | Cards stacked left; fixed illustration track over fixed detail track on the right |
| Persistent visual, selectable states | One figure re-read several ways; state rail + per-state info panel |
| Document facsimile | Page-shaped surface: letterhead, metadata line, body text with the key phrase highlighted, folded corner, stacked sheets behind |
| Two halves with a central hinge | Two lanes meeting at one shared pivot element both refer to |
| Multi-beat pipeline row | 3–5 beats left to right with labelled arrows (excerpt → statement → result rows → graph form) |

**Rules:**
- Assign a layout type to every slide in the plan; at least 6 distinct types in 10–12 slides
- Adjacent slides must not share the same core composition
- Use `https://github.com/bhavink/applied-ai-governance/tree/main/presentations` as optional inspiration; do not copy

## Slide title guidance

Content slide titles must be **descriptive and specific** — not punchy slogans.

| ❌ Avoid | ✅ Prefer |
|---|---|
| "One path ends the contention." | "Expanding SQL capacity extends fragmentation; CDC into the lakehouse separates analytics from production" |
| "Pilot. Prove. Expand by priority." | "A phased rollout sizes each source from pilot telemetry before expanding to the full estate" |
| "Known parameters for planning." | "Deployment constraints and configuration parameters to account for when scoping the pilot" |

Rules:
- Title must orient the audience to the slide's subject **and** conclusion
- Aim for 8–14 words; title should make sense read alone in a PDF table of contents
- Assertive is fine; vague or slogan-like is not
- Reserve short/punchy titles for: opener, section divider, close — not content slides

## Eyebrow vocabulary

The eyebrow labels a slide's role in the argument, and the set is closed. Reuse existing labels — Client need, Options, Recommendation, Problem space, Framing, Vocabulary — before coining anything.

- **Section-name eyebrows are reserved for section-opener slides.** Borrowing one elsewhere falsely marks that slide as a section start.
- Coin a new label only when none honestly fits, and match the convention: two or three words, sentence case, naming the slide's **role** rather than its content.

## Customer-facing language

Visible slides are artifacts shown directly to customers.

**Prohibited on visible slides:**
- Presenter or meta language: "talk track," "call this out," "ask them," "what to say," "gotchas," "objections," "note for presenter"
- Internal IDs, internal-only links, Slack citations, secrets
- Roadmap commitments or unsupported performance claims
- Overclaiming: soft filters ≠ security; illustrative pricing ≠ a quote

**Frame caveats neutrally:**
- Use: "planning considerations," "current boundaries," "design parameters," "known constraints"
- Avoid: "gotcha," "limitation," "warning," "problem"

Put all presenter guidance and internal nuance in speaker notes only.

## Copy discipline

- **Do not claim exhaustive counts.** Prefer "there are multiple ways to do X" over "there are five ways to do X" unless the set genuinely is closed. A count asserts the list is complete.
- **No time or effort estimates on option cards** — no "2–4 weeks", no Low/Medium/High effort badges — unless explicitly asked. If the kickers already convey escalation, an effort scale is redundant; delete it rather than reducing it to a bare word.
- **Describe mechanisms accurately for the actor involved.** Name what the actor actually does. "The agent writes a recursive CTE" was wrong because an agent will not author a single recursive query by default; "agent traversal — successive queries following edges" is what happens.
- **Cutting words is the goal, and leftover whitespace is acceptable.** Slides routinely lose 50–65% of their copy. Rebalance the space; do not refill it with prose.

## Speaker notes: discovery questions

For customer decks, embed open-ended discovery questions in speaker notes for slides where they are contextually relevant. Distribute questions across 4–8 slides rather than dumping them on one.

**Questions must:**
- Be open-ended and specific (not "Does this make sense?")
- Expose current state, constraints, decision criteria, ownership, or success metrics
- Map directly to the slide's topic

Categories to cover across a full deck:
- **Priority and mapping** — which workloads/sources matter most, how they map to business units or clients
- **Current tooling** — BI tools in use, refresh schedules, concurrency requirements, SLAs
- **Data readiness** — schemas and tables needed, PK coverage, CT/CDC enablement status
- **Volume and change rate** — initial size, daily change volume, TPS, acceptable latency
- **History and governance** — SCD2 requirements, PHI handling, client isolation, data retention policy
- **Infrastructure topology** — HA/AG, read replicas, network path, authentication constraints
- **Ownership and timeline** — budget owner, implementation owner, phase-one success criteria, target dates
- **Decision dynamics** — comparison criteria vs alternatives, pending commitments or procurement timelines

Format in notes as a "Discovery" bullet block. Do NOT surface discovery questions visibly on the slide unless the slide is a discussion slide.

## Pricing / sizing guidance

When cost is in scope:

- **Separate independent cost components** — do not blend ingestion/data movement with serving/consumption
- Show what is known (component names, DBU rates), cost drivers, missing inputs, and discovery questions needed to estimate
- Explain units and eligibility caveats (free tier limits, compute types) accurately
- Do not invent estimates without concrete customer inputs
- If inputs are unknown, surface the required inputs list on the slide itself as sizing questions

## Design system (summary)

| Token | Value |
|---|---|
| Oat | `#F9F7F4` / `#EEEDE9` |
| Ink | `#1B3139` |
| Accent (coral/lava) | `#FF3621` (sparingly) |
| Blue / Green / Dark Red | `#2272B4` / `#00A972` / `#98102A` |
| Type | DM Sans / Inter |
| Format | 16:9 feel, keyboard-nav HTML, no build step, self-contained |

Avoid: yellow/gold unless asked; purple AI cliché; cream + terracotta combo; dark-mode default.

Full rules: [design-system.md](design-system.md).

## Validation before handoff

Run all four checks:

1. **Composition check** — list layout type for each slide; fail if >50% share the same type or more than one adjacent pair share a type.

2. **Language check** — search visible slide HTML for: `talk track`, `call this out`, `ask them`, `what to say`, `gotcha`, `objection`, `note for presenter`. None should appear.

3. **Title quality check** — read each content slide h2 aloud. If it sounds like a slogan or could apply to any deck, rewrite it to be specific.

4. **Slide/notes sync** — count `.slide` elements in deck HTML; count entries in `NOTES` array in notes HTML. They must match exactly.

For a large or heavily interactive deck, or when the user asks for verification, there is a heavier browser-driven battery in [deep-verification.md](deep-verification.md). It is disproportionate for a normal deck — do not run it by default.

## Publishing

Only if the user asks. GitHub Pages serves `index.html` from the repo root on `main` with no workflow, so a push is the deploy and it propagates in under a minute.

Verify a publish by comparing a checksum of the fetched page against the local file — not by grepping for strings. Content generated at runtime by JS does not appear in the static HTML and grep will produce false negatives.

## Anti-patterns

- Text walls / dense paragraphs on slides
- Identical "title + 3 cards" layout across most slides
- Punchy slogan titles on every content slide
- Section labels or navigation state hand-written into per-slide markup
- Content-sized regions in a multi-state interactive slide (the slide jumps on click)
- Re-running a force simulation on every selection
- Hand-typed counts beside data-driven drawings
- Exhaustive counts ("five ways to…") where the set is not closed
- Effort or duration badges on option cards unless asked
- Agent-vs-agent scorecards unless asked
- Internal Slack citations on customer-facing decks
- Overclaiming (soft filters ≠ security; illustrative pricing ≠ quote)
- Breaking sync: different slide counts between deck and notes
- Em-dash-heavy marketing prose in spoken notes — keep conversational
- Meta openers in `say` ("Here's how I'd say it:", "Here's how I'd open:") — start with spoken words
- Chopping `say` into bullets as "cues" — cues need section labels + short scan phrases derived from the pitch
- Transition fixed under prep blocks in Both mode — must sit between cues and say (CSS `order` on one node)
- Generic discovery questions ("Does this make sense?", "Any questions?")
- Introducing a build step on a deck that does not need one

## Checklist before handing off

- [ ] Slide list confirmed (or user said build immediately)
- [ ] Composition map planned; ≥6 distinct layouts; no adjacent repeats
- [ ] Deck + notes in `presentations/` with matching slide counts
- [ ] Sync channel/key shared; Open speaker notes works
- [ ] Keyboard nav works in both windows
- [ ] Rail (if present) built from one declared map; every slide in it exactly once
- [ ] Interactive slides hold fixed geometry across states and redraw cleanly on re-entry
- [ ] Captions, counts and legends derived from the data they describe
- [ ] Content slide h2 titles are descriptive and specific (not slogans)
- [ ] Eyebrows drawn from the closed set; section names only on section openers
- [ ] No prohibited presenter/meta language on visible slides
- [ ] Notes include cues + say (dual track); NOTES.length matches deck slide count
- [ ] Notes mode toggle present (Both / Cues / Full script); transition placement correct per mode
- [ ] Notes use Purpose / cues / Say this / Transition cadence
- [ ] Discovery questions distributed across relevant slides in notes
- [ ] Honesty slides call out real limits in neutral framing
- [ ] Demo CTA only if URL exists; calculator only if cost is in scope

## Reference files

- [design-system.md](design-system.md) — palette, layout building blocks, density
- [interactive-visuals.md](interactive-visuals.md) — interaction patterns, fixed geometry, SVG recipes
- [speaker-notes-cadence.md](speaker-notes-cadence.md) — dual-track cues/say, toggle UX, transition placement, examples
- [sync-template.md](sync-template.md) — BroadcastChannel / localStorage boilerplate
- [templates/deck-shell.html](templates/deck-shell.html) — stripped deck shell
- [templates/notes-shell.html](templates/notes-shell.html) — stripped notes shell
- [templates/rail-snippet.html](templates/rail-snippet.html) — drop-in navigation rail CSS + JS

Conditional — read only when they apply:

- [generated-deck-architecture.md](generated-deck-architecture.md) — for a deck that is already multi-file, or when the user asks for one
- [deep-verification.md](deep-verification.md) — heavy browser verification loop, on request or for a large interactive deck
