# OST-compare-opportunities HTML rendering

**Date:** 2026-05-22
**Skill:** `product-discovery/skills/OST-compare-opportunities`
**Scope:** Add HTML rendering to the skill (no HTML output today). The JSON schema and markdown template stay unchanged.

## Motivation

`OST-compare-opportunities` currently produces a paired JSON + markdown matrix output. At workshop scale on the Metria dataset (96 opportunities across 5 phases — 480 matrix cells), the markdown table is unscannable. A previous session experimented with a literal HTML matrix table; that experiment never shipped to GitHub and is being abandoned. Going straight to a journey-grouped, scannable card view skips the dead-end matrix-HTML iteration.

The HTML output supports trio triage: scroll the journey phase-by-phase, spot promising candidates, drill into details on demand, filter to thin the herd.

## What changes

- **HTML template section** is added to `OST-compare-opportunities/SKILL.md`.
- **HTML rendering rules section** is added.
- **AI summary title pass** is added to the render step (generates one short noun-phrase title per opportunity, stored in the composed JSON).
- **Score-count fields** are computed per opportunity and stored in the composed JSON.
- **Procedure steps** gain a new step for AI title generation and a new step for HTML rendering. The write step now writes three files.
- **Front matter and intro** update to mention HTML.
- **Output principles** gain entries for "Three artifacts, one render" and the relaxed JS rule.

## What does NOT change

- JSON schema **version** stays at `opportunity-comparison v0.1`. New fields (below) are additive — they extend the composed object at the same version. No consumer breaks.
- Markdown template — keeps the matrix table and per-criterion rationale lists. Markdown is the "complete view"; HTML is the "skim view."
- Existing output paths: `<scope>/comparison-matrix.json` and `<scope>/comparison-matrix.md` keep their current shape. The skill adds `<scope>/comparison-matrix.html` as a third paired output.
- Hard-exit rules (an additional row is added for AI title failure, but the format and discipline are unchanged).
- Upstream-immutability and single-pass render discipline.

## Composed JSON additions

Three new additive fields. All written into the persisted JSON so a re-render produces byte-identical HTML without re-reading upstream files.

**Per opportunity** in `opportunities_compared[]`:

- `summary_title` (string) — 3-6 word AI-generated noun phrase. Language matches `<html lang>`.
- `score_counts` (object) — `{ strong, medium, weak, unknown, na }`, integers, computed deterministically from the existing per-cell scores.

**Top-level:**

- `journey_phases` (array of `{ id, name }`) — snapshotted from `experience-map-clustered.json` at render time, in upstream order. Carries empty phases (zero-opp Fulfillment) so the swim-lane grid can render an empty column for them. The unphased bucket is **not** an entry here; it is rendered as a final column when ≥1 opportunity has no `phase` set.

Reuse and recomputation rules:

- `summary_title`: persisted in JSON; on re-render, existing values are reused. Only opportunities missing the field trigger an LLM call.
- `score_counts`: recomputed every render (cheap, deterministic).
- `journey_phases`: re-snapshotted every render. If the upstream `experience-map-clustered.json` has changed between renders, the new value wins. The trio sees the current journey, not a stale one.

## HTML structure

```
<header>            title + meta + paired-paths
<section#outcome>   outcome blockquote
<section#excluded>  excluded-from-comparison list (omit if empty)
<nav#filters>       filter bar
<section#journey>   swim-lane grid with phase columns
<section#gaps>      evidence gaps (omit if empty)
<section#notes>     n/a-for-all-opps notes (omit if empty)
<details#steps>     collapsed step-id index (anchor targets)
<script>            ~50 LOC filter logic
```

## Layout: swim-lanes

One column per entry in the composed JSON's `journey_phases[]`, in array order. Each column shows the matching opportunities (those whose `phase_id` equals the column's phase id), including zero-opp columns. A final column for the unphased bucket is rendered only when ≥1 opportunity has no `phase` set.

- **Grid:** `display: grid; grid-template-columns: repeat(N, minmax(220px, 1fr))`. On narrow viewports the grid overflows horizontally; the trio always sees all phases (no collapsing).
- **Column header:** phase name (full, untruncated) + opportunity count in muted text. `position: sticky; top: <filter-bar-height>`.
- **Empty phase columns** (e.g., Fulfillment with 0 opps) render the header plus a single muted line `"No opportunities in this phase."`. The column still occupies one grid slot — the absence is itself a discovery insight.
- **Phase color accents:** subtle left-border tint per column, rotated through 5 warm neutrals keyed off phase index. Distinct from score-chip colors to avoid semantic confusion.

## Card design

### Collapsed (default)

```
┌──────────────────────────────┐
│ Otydlig beställningsprocess  │   AI summary_title, 3-6 words
│                    step-1-1  │   small muted, top-right, anchor link
│ strong: outcome, importance  │   only standout chips (strong + weak)
│ weak:   strategic-fit        │
│                          ▾   │   <details> caret
└──────────────────────────────┘
```

- `summary_title` is the visible headline. The full quote is hidden until expansion.
- `step-X-Y` label is `<a href="#step-X-Y">` pointing into the step index at the bottom of the page.
- "Strong" and "weak" lines render only if their bucket is non-empty. Cards with no standouts (all medium/unknown/n/a) render a muted `"No standout scores"` line — still visually distinct from a loading/empty state.
- `<details open>` toggle reveals the expanded view via native browser behavior (no JS).

### Expanded

- Full `quote` (italicized) and `source` citation.
- Per-criterion rationale list, one row per criterion in upstream `criteria[]` order:
  - Criterion display name + score word.
  - Rationale prose.
  - Cites line — omitted for `unknown` and `n/a`, matching the markdown rule.

### Card sort within column

Deterministic three-key sort:

1. `strong_count` descending.
2. `weak_count` ascending.
3. Upstream `opportunities_compared[]` order (tiebreaker).

No randomness. Same input → same order on every render.

### Card anchors

- `<details id="opp-X-Y">` so URL fragments open the right card expanded.
- A printed/PDF copy forces `details { open: true }` via the print stylesheet, so all cards expand for offline review.

## Filter bar

```
[ ▢ strong-heavy (≥3 strongs) ]  [ ▢ has weak ]  [ ▢ has unknown ]  [ Reset ]    96 of 96 shown
```

- **Position:** `position: sticky; top: 0; z-index: 2`. Stays visible during vertical scroll.
- **Chips** are AND-combined when multiple are active.
  - **strong-heavy** = `score_counts.strong >= 3`. Threshold of 3 matches the OST convention for a multi-criterion winner.
  - **has weak** = `score_counts.weak >= 1`.
  - **has unknown** = `score_counts.unknown >= 1` — surfaces evidence-gap candidates.
- **Reset** clears all chips.
- **Counter** updates live to `"N of 96 shown"`.
- **Empty-result state per column:** each column shows `"No matching opportunities"` placeholder when no cards survive the filter. The column header keeps the unfiltered total count so the trio doesn't lose context.

**Filter scope rationale.** Per-criterion filtering ("show only strong on outcome-alignment") is intentionally absent. That is what the markdown matrix is for. If the trio needs per-cell inspection, they have the markdown view and Cmd-F.

## JavaScript

~50 LOC, inline `<script>` at the end of `<body>`. Shape:

- Each card carries `data-strong-count`, `data-weak-count`, `data-unknown-count` attributes.
- One delegated click handler on the filter bar reads which chips are active, walks `.opp-card` elements, toggles a `.filtered-out` class. CSS hides via `display: none`.
- The "N of M shown" counter updates from the loop's running count.
- The per-column "No matching" placeholder is always in the DOM, hidden via `:not(:has(.opp-card:not(.filtered-out)))` on the column.
- `<details>` expansion uses the browser's native toggle — no JS.

**No build step. No framework. No external dependencies. No remote fonts or scripts.** The file remains self-contained and openable offline.

## AI title pass

Single batched LLM call per render, generating one `summary_title` per opportunity missing the field. Style: short descriptive noun phrase, 3-6 words, in the source language of the underlying quote.

- Title generation runs before the JSON/MD/HTML write step so all three artifacts see the same titles in the composed object.
- On re-render of an existing comparison, opportunities with a non-empty `summary_title` skip the LLM pass. Trio can override a title by editing the JSON directly and re-rendering.
- If title generation fails for any opportunity (LLM returns empty or unparseable), hard-exit. No partial output.

## Print and share

- `@media print` forces `details { open: true; }` so PDFs show every card fully expanded.
- Filter bar is `display: none` in print. Already-filtered-out cards stay hidden (current filter state applies to print).
- Phase column headers and the swim-lane grid keep their layout in print but lose `position: sticky`.

## Verification checklist

Run after editing the SKILL.md, before committing.

1. Render produces all three files at `<scope>/comparison-matrix.{json,md,html}`.
2. JSON diff against a pre-change render of the same fixture shows only the three new fields (`summary_title` per opp, `score_counts` per opp, `journey_phases` top-level). Schema version stays `0.1`.
3. Markdown byte-diffs identically. Title generation does not leak into the markdown.
4. HTML opens in Chrome and Safari and renders correctly:
   - Filter bar sticks on scroll.
   - Each phase column header sticks under the filter bar.
   - Clicking a chip filters live; counter updates.
   - Chip combinations AND-combine correctly.
   - Reset clears all chips.
   - Empty Fulfillment column shows the placeholder.
   - Cards expand inline; multiple can be open at once.
   - Cmd-P preview shows every card expanded.
   - Sort within column matches the three-key rule above.
5. Hard-exit paths still trigger on missing inputs and malformed JSON.
6. HTML works offline (open via `file://` with wifi off).

**Smoke fixture:** the existing Metria dataset (96 opps across 5 phases including the 0-opp Fulfillment and the 40 Unphased). It is the worst case the redesign targets; if it scans cleanly there, smaller datasets follow.

No automated test additions — the OST plugin has no test runner and adding one for this skill alone isn't worth the scope. Matches the verification pattern from `cost-review` and `transcript-cleaner`.

## Risks and mitigations

- **Cost of the AI title pass.** ~96 completions per fresh render on the Metria dataset. Mitigated by JSON-cached `summary_title` on re-render.
- **Render non-determinism.** AI titles can drift between fresh renders. Mitigated by the cache rule above; documented behavior is "first render generates, subsequent renders reuse."
- **Inline JS in HTML output.** Other OST skills produce static HTML or none at all. This skill is the first with runtime JS. The updated HTML rendering rules document the scope explicitly. Remote scripts and external dependencies remain forbidden.
- **Swim-lane awkwardness on lopsided datasets** (0-opp Fulfillment, 40-opp Unphased on Metria). Accepted trade-off — see Layout section. Columns fall back to `min-width: 220px` and the trio scrolls horizontally on narrow viewports.

## Out of scope

- Changes to the JSON schema or markdown template.
- Changes to upstream skills or the experience-mapping layout.
- A test runner for OST skills.
- Per-criterion filtering, full-text search, or sort controls beyond the three filter chips.
- Cross-rendering (e.g., a single HTML index across multiple opportunity selections).
