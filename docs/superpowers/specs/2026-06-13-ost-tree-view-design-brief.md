# Design brief — OST Tree View (for design exploration)

> Hand this to a design-focused Claude. It's self-contained — no repo access needed.
> **Attach the 4 reference images** (Horisontell vy / Vertikal vy board, the assumption table,
> the table close-up, the vertical-tree close-up) when you paste this.

## What we're designing

A visual rendering of an **Opportunity Solution Tree (OST)** — Teresa Torres' canonical
discovery artifact: a connected tree with a **product outcome at the root**, an
**opportunity space branching beneath it**, **solutions hanging under the chosen opportunity**,
and **assumption tests under the solutions**. Today our tool shows each layer as a separate
tab and never draws the tree itself. We want the tree.

We've learned from coaching teams that one tree shown two ways beats one giant tree:

1. **Horizontal cut — the opportunity space (breadth).** Used while deciding *which*
   opportunity to pursue. Root = product outcome; all opportunities branch beneath it
   (broad → narrow, up to 2 levels). Stops at the opportunity layer. The chosen opportunity
   is marked; the rest read as "the space not taken." This is the overview before going deep.

2. **Vertical cut — the chosen branch (depth).** Used once an opportunity is chosen. A deep,
   narrow slice: product outcome → chosen opportunity → top-3 solutions → an
   **assumption table** spanning the bottom. Trying to draw every opportunity's full
   sub-tree at once is unreadable — so we go deep on one branch instead.

The two cuts are one tree tab with a segmented toggle (`Opportunity space ⇄ Chosen branch`).

## Visual reference (the attached images)

The attached board is from a real team we coached — **mirror its visual language**:

- **Labeled horizontal swimlane bands** stacked top-to-bottom, each a soft tinted row:
  `PRODUCT OUTCOME` (yellow), `MÖJLIGHETER` / opportunities (light teal),
  `LÖSNINGAR` / solutions (cream), `ANTAGANDEN` / assumptions (table, below the tree).
  Band labels are small, italic, uppercase, left-aligned.
- **Nodes:** rounded pill/lozenge cards. Outcome = filled yellow lozenge. Opportunity =
  outlined teal pill. Solution = small cream pill, numbered (`1.1`, `1.2`…). Crisp
  right-angle (orthogonal) connectors with arrowheads, not curves.
- **Assumption table** (the `ANTAGANDEN` block, separate from the node tree): a dense,
  spreadsheet-style table. See the close-up image for the target feel.

Labels are in **Swedish** (this is a Swedish-market tool): keep `PRODUCT OUTCOME`,
`MÖJLIGHETER`, `LÖSNINGAR`, `ANTAGANDEN` as the band labels.

> **Important — do not reuse the client content from the images.** The images contain a real
> client's data (system names, Swedish domain terms). For your mockup, use the **neutral
> sample data below** instead. Don't carry over any names/terms from the images.

## Hard constraints (what makes this buildable)

The final renderer lives in a **single, dependency-free `index.html`** (vanilla JS that builds
HTML strings; layout via **CSS grid + flexbox**; connectors via **CSS borders/pseudo-elements
or inline SVG**). So:

- **No frameworks, no charting/graph/tree libraries (no D3, no React, no mermaid).** Anything
  you design must be expressible as plain HTML + CSS (+ minimal inline SVG for arrowheads).
- **Deliver a self-contained static HTML file** (single file, inline `<style>`, hard-coded
  sample data) as the mockup — that's the most directly portable handover for us.
- Use CSS custom properties for color (we theme via `--sc-*` tokens) — name your colors as
  variables at `:root` so we can remap them.
- Must **degrade gracefully**: if the solutions or assumptions layer has no data yet, the
  vertical cut shows the layers it has and still renders. Design empty/partial states.
- Horizontal scroll is acceptable for a wide opportunity space; the tree need not fit one screen.

## Data shape (use this neutral sample — NOT the image content)

Outcome (root):
- "Reduce the number of manual steps needed to onboard a new team to the workspace"

Opportunity space (horizontal cut) — note `parent_id` nesting, most are flat, a few nest:
- O1 "New admins can't tell which setup steps are required vs optional"  *(chosen)*
  - O1a "No single place shows onboarding progress"
  - O1b "Required steps aren't visually distinct from optional ones"
- O2 "Invited teammates wait on an admin to assign roles"
- O3 "Teams re-enter data they already gave during signup"
- O4 "Admins can't preview what a teammate will see before inviting"

Top-3 solutions (vertical cut, under chosen opportunity O1):
- S1 "Guided setup checklist with required/optional grouping"
- S2 "Onboarding progress dashboard"
- S3 "Smart defaults that pre-complete optional steps"

Assumption table (vertical cut, grouped by solution). Columns —
**filled from our data:** `Antagande` (text) · `Lösning` (which solution, e.g. S1) ·
`Risknivå` (High/Low, from an importance×evidence 2×2) · `Typ av antagande`
(one of: Användbarhet / Genomförbarhet / Lönsamhet / Önskvärdhet / Övrigt) ·
`Testmetod` · `Framgångskriterier`.
**Greyed-out, labeled "(coming soon)"** (we don't have this data yet — they're execution-time
fields filled in another tool): `Status` · `Issue ID` · `Insikter`.
Riskiest assumptions (High importance + weak evidence) should be visually flagged in their row.

Sample rows:
- "Admins will follow a checklist if shown one" — S1 — High — Användbarhet — Prototype walkthrough — 4/5 admins complete setup unaided
- "We can detect step completion server-side" — S1 — High — Genomförbarhet — Spike on event tracking — Completion event fires reliably
- "A progress dashboard increases day-1 activation" — S2 — Low — Önskvärdhet — Fake-door test — >20% click into dashboard

## What we want back (the handover)

A short handover we can act on:

1. The **self-contained HTML mockup file** (both cuts — either two files or a toggle), with
   inline CSS and the sample data above.
2. A **one-page rationale**: layout decisions, node/edge styling, the swimlane-band approach,
   how the toggle works, responsive/scroll behavior, and the color tokens you used.
3. Any **open questions or trade-offs** you hit (e.g. how deep opportunity nesting can go
   before it breaks, how the table behaves on narrow screens).

Keep it buildable-first: prefer a design we can port into vanilla HTML/CSS over something
that only works with a library.
