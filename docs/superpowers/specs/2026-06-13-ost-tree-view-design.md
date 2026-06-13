# SCI-207 — OST Tree View design spec

**Ticket:** [SCI-207](https://linear.app/scilla/issue/SCI-207) — render the actual Opportunity Solution Tree (outcome → opportunities → solutions → assumptions).
**File touched:** `product-discovery/templates/viewer/index.html` (single dependency-free file).
**Visual source of truth:** the design-exploration handover —
`docs/superpowers/specs/2026-06-13-ost-tree-view-design-brief.md` (brief) and the returned
mockup `index.html` + `OST Rationale.html` (in `~/Downloads/OST Visualization (1)/`).
This spec records the decisions that govern the port; the mockup shows the look.

## Goal

A Torres-literate user opens the viewer and sees a recognizable OST: one connected tree with
the product outcome as the root, the opportunity space branching beneath it, solutions under
the chosen opportunity, and assumption tests under the solutions. Today every layer is a
separate per-artifact tab and the connective structure is never drawn. This adds the tree.

## Core concept — one tree, two cuts

One new **Tree** tab (registered first, default-selected). Inside it, a segmented toggle flips
between two cuts of the same tree:

- **Horizontal — "Opportunity space" (breadth).** Root = product outcome; all opportunities
  branch beneath it via `parent_id` (broad → narrow, up to 2 levels). Stops at the opportunity
  layer. The chosen opportunity is marked (blue ring + `Vald` badge); the rest are de-emphasized
  (lower opacity) as "the space not taken." Used while choosing an opportunity.
- **Vertical — "Chosen branch" (depth).** Outcome → chosen opportunity → **top-3 solutions** →
  the assumption table spanning the bottom. One branch, deep. Used once an opportunity is chosen.

**Auto-default on load:** horizontal if no opportunity selected in `decisions.json`, vertical
once one is. Manual toggle overrides freely.

The existing per-artifact tabs (Comparison, Solutions, Assumptions, Experiments, Journey,
Experience Map, Decisions) remain as drill-down detail views.

## Rendering approach (from the handover — keep)

- New `renderTree(decisions, container)` in `index.html`. Vanilla JS string-building, same
  pattern as `renderJourneyMap`. **No frameworks, no graph/tree/charting libraries.**
- **Orthogonal tree edges via the canonical pure-CSS technique:** each `<li>` draws its half of
  the horizontal sibling bus with `::before/::after` borders; each child `<ul>` draws the
  vertical down-stem; single child collapses to a straight line. Arrowheads are CSS triangles
  (`border`) on the node top — no SVG file.
- **Swimlane bands** (`PRODUCT OUTCOME` / `MÖJLIGHETER` / `LÖSNINGAR`; horizontal cut uses the
  first two). Full-width tinted rows behind the tree; labels in a sticky left gutter so they
  stay pinned while the tree scrolls horizontally. **Band heights are measured from the DOM
  after render** (nodes tagged `data-band`; boundary = midpoint between one band's lowest node
  and the next band's highest) so bands track real content and adapt to partial data.
- Tree lives in a horizontally scrollable canvas; auto-centers on the root outcome on load.
  A wide opportunity space scrolls rather than shrinking.

## Adaptations required when porting into the real viewer

The mockup is a standalone page; the build is a renderer inside the tabbed offline viewer.

- **Strip standalone chrome:** topbar, footer, pink `body` background — the viewer supplies these.
- **No Google Fonts.** The viewer is an offline local-file template; use its existing font stack,
  not a fetched Inter. (External fetch also makes DOM band-measurement timing fragile.)
- **Fold the toggle** into the Tree tab header, in the viewer's existing control style.
- **Drop the "Data state" demo buttons** — they're mockup scaffolding. Real state derives from
  `decisions.json` + which `_working/*.json` files exist.
- **Reconcile `--sc-*` token values** against the viewer's real tokens (the mockup inlined a
  guessed subset). Keep the `--ost-*` remappable layer on top (aligns with SCI-31).

## Data mapping (authoritative — this is where the mockup diverged from our schema)

| Layer | Source | Notes |
|---|---|---|
| Outcome (root) | product-outcome / `decisions.json` | persistent root in both cuts |
| Opportunity space | clustered-opportunities JSON | `parent_id` → hierarchy (≤2 levels); chosen from `decisions.json`. Ignore journey-phase tagging — this is the tree, not the journey map. |
| Solutions (vertical) | top-3 from `decisions.json` / selection | 3 branches under the opportunity. **Carry the real solution IDs** (may be e.g. `1.1, 2.3, 1.4`, not renumbered `1.1/1.2/1.3`). Clusters stay in the Solutions drill-down tab. |
| Assumptions | categorized assumptions + riskiest 2×2 + validation-experiments | all categorized assumptions, grouped by solution |

### Assumption table (`ANTAGANDEN`, vertical cut, below the tree)

All categorized assumptions, grouped by the solution they test (group header + count per
solution). Columns:

**Filled from data:**
- `Antagande` — assumption text.
- `Lösning` — solution ID chip (the real ID, cross-referencing the tree node).
- **Risk = two columns + flag** (corrects the mock's single `Risknivå`):
  - `Betydelse` — `importance: high|low` → Hög / Låg.
  - `Bevis` — `evidence: strong|weak` → Starkt / Svagt.
  - Rows where `is_riskiest` (importance:high AND evidence:weak) get a **riskiest flag** —
    red left rule on the row + a flag marker. This is the whole point of phase 4; don't
    collapse it to one level.
- `Typ av antagande` — `category` enum mapped to Swedish, color-coded chip:
  `desirability→Önskvärdhet`, `usability→Användbarhet`, `feasibility→Genomförbarhet`,
  `viability→Lönsamhet`, `other→Övrigt`. (Legend above the table.)
- `Testmetod` / `Framgångskriterier` — from validation-experiments. **These exist only for
  `is_riskiest` assumptions** (experiments are designed for the riskiest only). Non-riskiest
  rows render `—` (sparse). Honest about which assumptions got an experiment.

**Greyed, hatched, labeled "(coming soon)":** `Status` · `Issue ID` · `Insikter` — execution-time
fields the team fills in their own tool; rendered as disabled columns so the eventual shape is
visible without faking data. ("Issue ID", not "Jira" — tool-agnostic.)

## Partial / empty states (data-driven, degrade don't error)

- **No opportunity chosen yet** → default to horizontal cut; vertical toggle still available
  (shows what it can).
- **No solutions yet** → vertical cut's `LÖSNINGAR` band shows a dashed placeholder node; the
  table shows a "choose a solution first" empty state.
- **No assumptions yet** → solutions render; table shows an empty state.
- **Per-solution empty** → a solution with zero assumptions shows an inline "inga antaganden
  ännu" row under its group header.

## Out of scope

- Editing; execution-status fields (Status/Issue ID/Insikter stay "coming soon").
- The full viewer IA redesign deferred from SCI-206.
- The cross-round `tree.json` living tree — this renders a single round's `_working/`.
- Inline opportunity scoring on tree nodes (stays in the Comparison drill-down tab).
- 3+ levels of opportunity nesting (cap at 2; revisit with collapse/expand if ever needed).

## Open questions carried from the handover (non-blocking)

- Very wide breadth tree (6+ top-level opportunities): root centers far right of the first
  opportunity. Auto-scroll frames the root on load; a "fit"/mini-map control is a possible
  later add.
- Table on true mobile: currently horizontal-scroll inside its card (min-width floor). A
  stacked-card row layout is the mobile alternative if usage warrants — decide who opens this
  on a phone first.
