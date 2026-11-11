# Speaker notes cadence

Match a clean talk-track style. Notes are what the presenter *says*; slides are what the room *sees*. Never paste slide bullets into the say-block.

## Dual track (cues + full script)

Each note entry should support two parallel talk tracks derived from the same pitch:

1. **Cues** — scannable live-reference: section labels + short bullets. Derived from the spoken pitch, but **not** a chopped-up paragraph. Built for glance-while-presenting.
2. **Full script (`say`)** — complete conversational spoken paragraph for when the presenter needs to read.

Prep blocks (Purpose, Discovery, How to demo, Frame, Gap closed, etc.) stay in `bullets` and always sit **below** the cues/script/transition cluster.

### Data shape

```js
{
  title: '…',
  onscreen: '…',
  say: 'Full spoken paragraph — start with words said to the room.',
  cues: [
    ['Section label', ['Short bullet', 'Short bullet']],
    ['Another beat', ['…']],
  ],
  bullets: [
    ['Purpose', ['…']],
    ['Discovery', ['…']],
  ],
  transition: 'Transition: "…"',
}
```

| Field | Content |
|---|---|
| `title` | Short slide name |
| `onscreen` | One-line reminder of what's visible |
| `cues` | `[["Label", ["…"]], …]` — live-reference groups |
| `say` | Full spoken paragraph — the text said to the room |
| `bullets` | Prep blocks: Purpose, Discovery, How to demo, etc. |
| `transition` | `"Transition: \"…\""` or end cue |

### Writing cues vs say

- Write `say` first as the conversational pitch, then **derive** cues from it.
- Cue labels name beats ("Who I am", "The real gap"), not slide chrome.
- Cue bullets are short phrases a presenter can scan mid-sentence — not full sentences copied from `say`.
- Do not auto-split `say` on periods and call that cues.

## Toggle UX

Speaker notes UI should include a mode toggle (segmented control in the header), preferably:

| Mode | Shows |
|---|---|
| **Both** (default) | Cues on top, full script below |
| **Cues** | Cues only (+ transition) |
| **Full script** | Full spoken paragraph only (+ transition) |

Optional but recommended:

- Keyboard shortcut **`M`** cycles Both → Cues → Full script → Both
- Persist mode in `localStorage`, namespaced per deck (e.g. `'{slug}-notes-mode'`)
- Sync mode across notes windows via the `storage` event on that key
- Footer hint mentions `M switches view`

## Transition line placement

The **transition** line must move with the cues/script cluster — not sit fixed at the bottom of `main`.

| Mode | Transition sits |
|---|---|
| **Both** | **Between** the cues block and the full script |
| **Cues** | **Just under** the cues |
| **Full script** | **Just under** the full script |

Prep blocks (`#bullets`: Purpose, Discovery, How to demo, etc.) always stay **below** that cluster.

### Implementation (single transition node)

Use flex column on `main` with CSS `order` so **one** transition element repositions by mode without duplicating DOM:

```css
main { display: flex; flex-direction: column; }
.cues { order: 1; }
.transition { order: 2; }
.say { order: 3; }
#bullets { order: 4; }

body[data-mode="cues"] .say,
body[data-mode="cues"] #bullets { display: none; }

body[data-mode="full"] .cues { display: none; }
body[data-mode="full"] .say { order: 1; }
```

DOM order in markup can be cues → say → bullets → transition; visual order is driven by `order` + mode. In Both: cues (1) → transition (2) → say (3) → bullets (4). In Full: say bumped to 1, transition stays 2 (just under script), bullets 4.

The default notes shell ships this pattern: [templates/notes-shell.html](templates/notes-shell.html).

## Required structure (per slide)

```text
Cues — labeled live-reference groups (scan while presenting)
Transition — bridge to next slide  ← sits with the cluster per mode above
Say this — spoken paragraph (start directly with what the presenter says)
[optional] Purpose / Discovery / Point / Gap closed / How to demo live
```

In **Both** mode the on-screen stack is: cues → transition → say → prep. Modes hide cues or say but keep transition adjacent to whatever remains.

## Voice

- Conversational, first person or "we" where natural
- The `say` field **is** the spoken paragraph — start directly with what the presenter says to the room
- Do **not** wrap spoken notes in meta phrases like "Here's how I'd say it:", "Here's how I'd open:", "I'd say something like…", or "Close with:"
- Name the customer problem in *their* words
- Land one punchline per slide
- Honest about limits (soft scoping ≠ security; estimates ≠ quotes)
- Demo cues are concrete actions ("bump questions by 1", "open a citation")
- On an interactive slide, name the clicks in order and say what to do while clicking — "toggle through all three domains and stop talking while you do it" beats "the domains are selectable"
- Transitions are spoken bridges, not "Next slide"

## Examples

### Wow moment (automated brief)

**Say this:** "Another journey both sides kept coming back to: the alerts already exist, but someone still writes the starting brief by hand. Alerts fire — reasoning doesn't. On Databricks we close that gap end-to-end: the events land in Delta, a declarative pipeline promotes bronze → silver → gold, and the gold table calls a model via ai_query() so a draft brief appears with nobody typing."

**Cues:**

- **The pain** — alerts without triage; brief still written by hand
- **The close** — events → pipeline bronze/silver/gold → ai_query() → draft brief

**Point:** alerts without triage → pipeline → ai_query() → draft brief.

**Gap closed:** existing systems alert but don't reason; briefs are written manually.

**How to demo live:** trigger an event, switch to the app, watch the brief appear unprompted.

**Transition:** "And a good brief leans on history — that's the next journey."

### Architecture opener (data inputs)

**Say this:** "This section is architecture — inputs, components, outputs — with no data-model detail. Start with the problem those journeys depend on: today the inputs arrive as manual exports… On Databricks, the input types land in the lakehouse under Unity Catalog…"

**Cues:**

- **Frame** — architecture section; inputs / components / outputs; no data-model detail
- **Today** — inputs are manual exports
- **On Databricks** — governed input types; lakehouse under Unity Catalog

**Point:** governed inputs land in the lakehouse, not in manual exports.

**Transition:** "Now, what turns those inputs into answers — the stack."

### Honesty / boundary

**Say this:** "Useful workflow control — not a security boundary. Soft scoping is prompt contract plus leakage tests. That's the right fit for this stage. Hard filtering — retrieval that cannot return unauthorized rows — is what you'd need for true tenant isolation. We're not pretending those are the same."

**Cues:**

- **Claim** — useful workflow control, not a security boundary
- **Soft scoping** — prompt contract + leakage tests; right for the current stage
- **Upgrade path** — hard filtering for true tenant isolation; don't equate them

**Point:** don't overclaim security; name the upgrade path without derailing.

**Transition:** "Trust next — how we build a labeled eval set from known evidence."

## Blank template (markdown planning)

```markdown
## Slide NN — {Title}

### On screen
{one-line visual reminder}

### Cues
- **{Label}**
  - {short bullet}
  - {short bullet}

### Say this
{spoken paragraph — no meta opener; start with the words said to the room}

### Purpose
- …

### Discovery
- …

### How to demo live
- …

### Transition
Transition: "…"
```

## Reference implementation

Live pattern (cues + say + Both/Cues/Full toggle + order-based transition):

- The published github.io notes page for any deck built with this skill

Use as an example to copy from — the skill works without that path. Prefer bootstrapping from [templates/notes-shell.html](templates/notes-shell.html), which includes the toggle pattern.

## Anti-patterns for notes

- Meta openers around `say`: "Here's how I'd say it:", "Here's how I'd open:", "I'd say something like…", "Close with:" — write the spoken paragraph directly
- Chopping `say` into bullets and calling that cues — cues need section labels and short scan phrases
- Reading the headline aloud then stopping
- Duplicating every on-slide bullet
- Internal citations ("per Slack from…") in customer-facing notes
- Skipping Transition (presenter loses the thread)
- Transition fixed at the bottom of `main` in Both mode (it must sit between cues and say)
- Duplicating the transition node per mode instead of one node + CSS `order`
- Stale forward references after a reorder — "the next slide lays out…" pointers rot the moment a slide moves, in notes as well as on the slide
- Over-long say blocks (> ~90 seconds of speech) — split the slide instead
- Notes with `say` but no `cues` (or vice versa) when shipping the dual-track toggle
