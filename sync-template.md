# Sync template — deck ↔ speaker notes

Both windows stay on the same slide via **BroadcastChannel** (same origin) with **localStorage** fallback for late-join / storage events.

## Naming

Derive from the deck slug:

```js
const CHANNEL = '{slug}-deck';       // e.g. 'signal-desk-deck'
const STORAGE_KEY = '{slug}-slide';  // e.g. 'signal-desk-slide'
```

Use the **same** constants in `{slug}-walkthrough.html` and `{slug}-speaker-notes.html`.

Hard rule: **identical slide count and order** in both files. Mismatched lengths break presenting.

## Shared helpers (copy into both files)

```js
const CHANNEL = '{slug}-deck';
const STORAGE_KEY = '{slug}-slide';
const bc = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel(CHANNEL) : null;
let index = 0;
let applyingRemote = false;
let lastNavAt = 0;

function broadcastSlide(i) {
  try { localStorage.setItem(STORAGE_KEY, String(i)); } catch (_) {}
  if (bc) bc.postMessage({ slideIndex: i, source: 'deck' /* or 'notes' */ });
}

function applyRemote(i) {
  if (!Number.isFinite(i) || i === index) return;
  applyingRemote = true;
  show(i, { silent: true });
  applyingRemote = false;
}

if (bc) {
  bc.onmessage = (event) => {
    const i = event?.data?.slideIndex;
    if (typeof i === 'number') applyRemote(i);
  };
}
window.addEventListener('storage', (event) => {
  if (event.key !== STORAGE_KEY || event.newValue == null) return;
  applyRemote(Number(event.newValue));
});
```

## `show()` contract

```js
function show(next, opts = {}) {
  index = Math.max(0, Math.min(TOTAL - 1, next));
  // … update UI …
  // paintRail(index);                       // if the deck has a position rail
  history.replaceState(null, '', `#${index + 1}`);
  if (!opts.silent && !applyingRemote) broadcastSlide(index);
  // requestAnimationFrame(() => VIZ[index]?.enter?.());   // if the slide draws
}
```

- Local nav → broadcast
- Remote apply → `silent: true` (no echo loop)
- Rail painting and visual `enter()` hang off `show()`, so every entry point — keys, touch, rail click, remote sync — gets them for free

## Initial index

```js
let start = Number(location.hash.slice(1)) - 1;
if (!Number.isFinite(start) || start < 0) {
  try { start = Number(localStorage.getItem(STORAGE_KEY)); } catch (_) { start = 0; }
}
show(Number.isFinite(start) && start >= 0 ? start : 0, { silent: true });
// Notes window may broadcast once after silent show so a late-open catches up:
// broadcastSlide(index);
```

## Open speaker notes (deck only)

```js
document.querySelector('#open-notes')?.addEventListener('click', () => {
  const url = new URL('{slug}-speaker-notes.html', window.location.href);
  url.hash = String(index + 1);
  window.open(url.toString(), '{slug}-notes', 'width=520,height=900,menubar=no,toolbar=no,location=no,status=no');
  broadcastSlide(index);
});
```

## Keyboard (both windows)

| Key | Action |
|---|---|
| → / Space / PageDown | Next |
| ← / PageUp | Prev |
| Home / End | First / last |

Debounce step keys (~180ms). Ignore step keys when focus is in `input, textarea, select` so a calculator slider does not advance the deck.

Do **not** ignore arrow keys for a focused `button` — that breaks navigation the moment the presenter clicks a control on an interactive slide. Swallow only Space for a focused button (so it can activate it), and blur slide controls after a click so Space returns to the deck:

```js
const swallowsKey = (target, key) =>
  target.closest('input, textarea, select') || (key === ' ' && target.closest('button'));

// capture phase — in-slide handlers stop propagation
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.deck button');
  if (btn) setTimeout(() => btn.blur(), 0);
}, true);
```

## Presenting setup

1. Open walkthrough full-screen on the shared display
2. Click **Open speaker notes** → second monitor
3. Navigate from either window; both stay aligned

## Checklist

- [ ] Same `CHANNEL` + `STORAGE_KEY` in both files
- [ ] Same number of slides / `NOTES.length`
- [ ] Hash `#N` deep-links work
- [ ] Late-open notes pick up `localStorage` index
- [ ] No broadcast loop (`applyingRemote` / `silent`)
