# SCI-242 — OST Viewer redesign: 3 lenses + a rollup guardrail table

**Ticket:** [SCI-242](https://linear.app/scilla/issue/SCI-242) (High). Builds on [SCI-207](https://linear.app/scilla/issue/SCI-207) (Tree view, shipped).
**Follow-up:** [SCI-243](https://linear.app/scilla/issue/SCI-243) — export a row → ticket/prompt (out of scope here).
**File:** `product-discovery/templates/viewer/index.html` (single dependency-free file).

## The job (corrected framing — this drives everything)

This viewer is **not** Torres' living Opportunity Solution Tree that a team returns to over time. It is a **per-iteration sense-making helper**: a trio has just run interviews / mined internal sources, and the viewer helps them organize *one round's* insights and see how they connect — **compare opportunities, compare solutions, and trace solutions → assumptions → experiments → product outcome.**

Today it renders that as **9 co-equal, ID-keyed artifact tabs** — organized by how the pipeline produced the data, not by the job the trio does with it. That's the "overwhelming and visually disconnected" problem. The fix is to organize around a few purposeful lenses plus one raw guardrail.

## Information architecture: 3 lenses + 1 guardrail (replacing 9 tabs)

### 1. Tree (default)
The connected picture (already built in SCI-207). Toggle: **Opportunity space** (horizontal/breadth — scan & compare opportunities, chosen marked) ⇄ **Chosen branch** (vertical/depth — outcome → opp → solutions → assumptions table → experiments). Phase auto-default from `decisions.json`.

Evidence becomes **drill-downs off nodes**, not top-level tabs:
- chosen opportunity → "why this one" (the comparison scores)
- solution layer → "all 18 solutions considered" (the breadth)
- riskiest assumption → the full experiment card (hypothesis · metric · cost · time)

### 2. Prioritise
The **comparison matrix** (opportunities × Torres criteria) — the "which do we pursue, and why" lens. This is today's Comparison Matrix tab, reframed as a first-class lens.

### 3. Journey
**Opportunities clustered by journey phase** — the "where is the pain dense?" lens (the view trios already build in mind-maps to see if one phase carries more opportunities than another). Merges today's Experience Map + Journey Map into one lens; the raw journey (steps/decision-branches) is available beneath as reference.

### 4. Table (guardrail / fallback)
One **denormalized rollup**, sortable / searchable / **downloadable (CSV + JSON)**. The completeness anchor: a skeptical trio member can verify the full output is all there, search it, and export it. Detailed below.

### Cut as top-level tabs (folded in, not lost)
- **Overview** → the outcome banner / round-status header (always visible).
- **Riskiest Assumptions** → already shown in the Chosen-branch assumption table (2×2 axes + flag).
- **Experiments** + **Solutions (18)** → node drill-downs in the Tree.
- **Comparison Matrix** → becomes the Prioritise lens.
- **Decisions (raw json)** → removed from the reader view (it's the data behind the tree, and an edit surface owned by the facilitator/file).
- **Experience Map / Journey Map** → the single Journey lens.

## The rollup table (guardrail)

**Why it exists:** the raw data is in the repo (`<scope>/_working/*.json` + `decisions.json`) but **scattered across ~15 files and keyed by ID** (`sol-r1-pm-1`, `asm-…-004`). The joined, overviewable form exists nowhere. The rollup *is* the join — it puts the solution, opportunity, and outcome on the assumption's own row, so the human doesn't reconstruct relationships from IDs in their head. It is also the **flat backbone the three visual lenses are views onto** (sort by Stage = Journey; filter to scored = Prioritise; filter to chosen = Tree branch).

**Grain:** one row per *deepest leaf that exists on each branch*, along the ladder:
```
outcome → stage → opportunity → solution → assumption → recommended experiment
```
Ragged depth is the point, not a defect:
- **Un-chosen opportunities** stop at the opportunity column — right-hand cells empty (informative: "we have this opportunity but haven't taken it to solutions").
- The **one chosen opportunity** goes deep to assumptions/experiments.
- **Sub-opportunities** (`parent_id`) become child rows with the parent value repeated.

**Columns:** Product outcome · Stage · Opportunity · Sub-opp · Score/chosen · Solution · Assumption · Betydelse · Bevis · Riskigast · Typ · Testmetod · Framgångskriterier.

**Default grain = assumption** (the recommended test inline) → ~75 rows for the golden fixture (≈33 deep chosen-branch rows + ≈43 shallow opportunity rows). A **"show alternative tests" toggle** drops to the true experiment grain — each riskiest assumption has `recommended_test` + 2 `alternative_tests` in `validation-experiments.json`, so the deepest level answers "what could we run to test this?".

**Download:** "Download CSV / JSON" emits the current table (respecting sort/filter) as a file — gives the trio the joined table as a real artifact in their repo and is the substrate for SCI-243 (act on a row).

## Data sources (all already in `_working/`)

| Column(s) | Source |
|---|---|
| Product outcome | `decisions.json` (or clustered) |
| Stage | `experience-map-clustered.json` — opportunity `phase_id` → phase name |
| Opportunity / Sub-opp | `experience-map-clustered.json` — `quote`, `parent_id` |
| Score / chosen | `comparison-matrix.json` (Torres scores) + `decisions.json` (chosen id) |
| Solution | `top-three-solutions.json` (fallback `decisions.json` picks) |
| Assumption + axes + Typ | `riskiest-assumptions.json` (all 33, with importance/evidence/is_riskiest/category) |
| Testmetod / Framgångskriterier + alternatives | `validation-experiments.json` (riskiest only) merged by assumption id |

Reuses the SCI-207 data-layer helpers (`buildOpportunityTree`, `loadTreeData`, `buildAssumptionRows`) and extends them to emit the flat rollup.

## Constraints & non-goals

- Stay in the single dependency-free `index.html`; vanilla JS string-building, CSS, no libraries — same pattern as the Tree.
- Degrade gracefully on partial rounds (no chosen opp, no solutions yet, etc.) — same tolerance the Tree already has.
- **Out of scope:** the row → Linear ticket / Claude Code prompt automation (SCI-243); the living cross-round `tree.json`; any change to the pipeline skills/workflows.

## Open question for the plan stage
- **Solution comparison** as its own front-door vs. a drill-down. The trio compares solutions, but the breadth (18 candidates) reads as "what we considered" — currently a drill-down off the solution layer. Promote to a 5th lens only if the team compares solutions often enough to warrant it. Default: drill-down.
