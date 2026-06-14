# SCI-242 — OST Viewer redesign: 3 lenses + a rollup guardrail table

**Ticket:** [SCI-242](https://linear.app/scilla/issue/SCI-242) (High). Builds on [SCI-207](https://linear.app/scilla/issue/SCI-207) (Tree view, shipped).
**Follow-up:** [SCI-243](https://linear.app/scilla/issue/SCI-243) — export a row → ticket/prompt (out of scope here).
**File:** `product-discovery/templates/viewer/index.html` (single dependency-free file).

## The job (corrected framing — this drives everything)

This viewer is **not** Torres' living Opportunity Solution Tree that a team returns to over time. It is a **per-iteration sense-making helper**: a trio has just run interviews / mined internal sources, and the viewer helps them organize *one round's* insights and see how they connect — **compare opportunities, compare solutions, and trace solutions → assumptions → experiments → product outcome.**

Today it renders that as **9 co-equal, ID-keyed artifact tabs** — organized by how the pipeline produced the data, not by the job the trio does with it. That's the "overwhelming and visually disconnected" problem. The fix is to organize around a few purposeful lenses plus one raw guardrail.

## Principle: the HTML is a static, read-only artifact

The viewer *renders* one round's output for humans to see. **Acting on it happens in the terminal**, conversationally, through the skills/agents (the "act on this round" skill, SCI-243, grounded in the action model, SCI-244) — not through buttons in the page. This is a skills/agents toolkit; the terminal is the interface, and a second, worse interface inside the HTML would fight it.

Keep the distinction clean:
- **View-navigation stays in the HTML** — switching lenses, toggling the Tree's two cuts, opening a node drill-down. That's looking at static content different ways; it has to live in the page.
- **Action leaves the HTML** — export, download, sort-to-decide, "make a ticket", "build this", "design a prototype". Those are terminal moves. The agent reads the same `_working/*.json` and answers.

So the rollup renders static (one sensible order); slicing or acting on it is a question you take to Claude Code.

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
One **denormalized rollup**, rendered **static** in a sensible default order (by stage, then opportunity). The completeness anchor: a skeptical trio member can see the full output is all there on one screen. **No in-HTML interactivity** — see the principle below; slicing, sorting, and acting happen in the terminal, not in the page.

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

**Grain = assumption** (the recommended test inline) → ~75 rows for the golden fixture (≈33 deep chosen-branch rows + ≈43 shallow opportunity rows). Each riskiest assumption also has 2 `alternative_tests` in `validation-experiments.json`; these are *not* rendered in the static table — they live in the JSON, and the terminal action skill (SCI-243) surfaces them when someone is actually choosing which test to run. The static table answers "what's the recommended next test?"; "what else could we run?" is a terminal question.

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
- **Static, read-only.** Only view-navigation JS (lens/tab switching, Tree cut toggle, node drill-downs). No download, sort-to-decide, export, or "act" controls — those are terminal moves (see Principle).
- Degrade gracefully on partial rounds (no chosen opp, no solutions yet, etc.) — same tolerance the Tree already has.
- **Out of scope:** acting on the output — the conversational "act on this round" skill (SCI-243) and its action model (SCI-244); the living cross-round `tree.json`; any change to the pipeline skills/workflows.

## Open question for the plan stage
- **Solution comparison** as its own front-door vs. a drill-down. The trio compares solutions, but the breadth (18 candidates) reads as "what we considered" — currently a drill-down off the solution layer. Promote to a 5th lens only if the team compares solutions often enough to warrant it. Default: drill-down.
