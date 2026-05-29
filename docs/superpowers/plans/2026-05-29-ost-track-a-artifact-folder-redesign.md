# OST Track A: Artifact Model & Folder Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut a full OST run from ~27 scattered files to 4 readable milestone docs + `decisions.json` + `product-context/` (all JSON & intermediates hidden in `_working/`), and simplify/rename the workspace folder, without touching the divergence or grounding that drive output quality.

**Architecture:** Two layers. *Machine layer* — every skill writes its JSON to a hidden `<scope>/_working/` folder. *Human layer* — only the four HITL-gate phases (06, 09, 12, 13) write a self-contained markdown doc to the scope root (`1-opportunity.md` … `4-experiments.md`). The top folder is renamed `discovery/` → `OST-discovery/` and its layout flattened to single-product/single-round by default (product and round nesting are opt-in). The viewer reads `decisions.json` from the scope root and all other view JSON from `_working/`. A golden-run regression check brackets the work to prove quality survived.

**Tech Stack:** Markdown SKILL.md instruction files; one shared `knowledge/discovery/workspace-scope.md` (symlinked into every skill's `references/`); Python `templates/serve.py` (generic static server, unchanged); vanilla-JS `templates/viewer/index.html`.

**Spec:** `docs/superpowers/specs/2026-05-29-ost-artifact-model-and-speed-redesign-design.md` (SCI-53)

---

## File Structure

| File | Responsibility | Change |
|------|----------------|--------|
| `product-discovery/knowledge/discovery/workspace-scope.md` | Canonical layout + scope-resolution protocol (symlinked into all 15 skills) | **Rewrite** |
| `product-discovery/knowledge/discovery/decisions-json-schema.md` | decisions.json schema + location string | Modify (location + `_working/` note) |
| `product-discovery/knowledge/discovery/viewer-launch.md` | Viewer launch instructions | Modify (`--data` path) |
| `product-discovery/skills/00a-OST-init-workspace/SKILL.md` | Folder scaffolding | **Rewrite scaffolding section** |
| `product-discovery/skills/00b-OST-setup-product/SKILL.md` | Guided setup; writes context + decisions.json | Modify (paths) |
| `product-discovery/skills/{01..13}-*/SKILL.md` | Per-phase output writers | Modify (route JSON → `_working/`; milestone md handling) |
| `product-discovery/templates/viewer/index.html` | View registry + JSON fetch | Modify (fetch base → `_working/`) |
| `product-discovery/CLAUDE.md`, `product-discovery/README.md` (if present) | Docs referencing `discovery/` | Modify (rename) |
| `product-discovery/skills/00a-OST-init-workspace/references/MIGRATION.md` | One-time migration helper for existing workspaces | **Create** |
| `docs/superpowers/fixtures/ost-golden/` | Golden-run baseline outputs + rubric | **Create** |

> **Verification note:** These are prompt/instruction files, not unit-testable functions. "Tests" in this plan are (a) the **golden-run regression check** (Task 0 + Task 16), (b) **path-trace checks** that read a file back and confirm the path strings changed, and (c) **viewer smoke checks** that load a fixture in the browser. There is no pytest suite; do not invent one.

---

## Phase 0 — Golden Baseline (do this BEFORE any edit)

### Task 0: Capture the current-output golden fixture + quality rubric

**Files:**
- Create: `docs/superpowers/fixtures/ost-golden/RUBRIC.md`
- Create: `docs/superpowers/fixtures/ost-golden/baseline/` (captured outputs)
- Create: `docs/superpowers/fixtures/ost-golden/INPUT.md` (the fixed test input)

- [ ] **Step 1: Freeze a fixed test input.** Pick one real, small product example (reuse the demo input already in the repo if one exists, e.g. `scilla-dag-canucci-demo.txt`, or author a minimal product-outcome + 2 interview transcripts). Write it to `docs/superpowers/fixtures/ost-golden/INPUT.md` so every golden run uses identical input.

- [ ] **Step 2: Run the full OST pipeline (phases 00b→13) on the frozen input on the current `master` codebase.** Copy the entire resulting `discovery/` tree into `docs/superpowers/fixtures/ost-golden/baseline/`. This is the pre-change reference.

- [ ] **Step 3: Write the quality rubric** to `RUBRIC.md`. It must define concrete, checkable measures so "quality preserved" is not subjective:

```markdown
# OST Golden-Run Quality Rubric

Compare a NEW run against baseline/ on these axes. Quality is "preserved" if every axis holds.

1. Divergence breadth — phase 07 still produces 18 solution candidates across 3 roles × 3 rounds (count them in _working/solution-candidates.json).
2. Assumption coverage — phase 10 still produces the multi-method assumption set; count of distinct assumptions is within ±10% of baseline.
3. Grounding fidelity — milestone docs still cite the product outcome, experience-map phases, and Torres criteria by name (spot-check 1-opportunity.md and 2-solutions.md).
4. Gate-doc completeness — each milestone doc is self-contained: 1-opportunity.md lists every alternative considered with why-not + the comparison slice; 2-solutions.md lists non-selected clusters; 3 and 4 show alternatives.
5. Schema validity — every JSON in _working/ parses and matches its locked schema_version.
6. Decision spine — decisions.json has all four `decided.*` sections populated.
```

- [ ] **Step 4: Commit the fixture.**

```bash
git add docs/superpowers/fixtures/ost-golden/
git commit -m "test: capture pre-change OST golden baseline + rubric (SCI-53)"
```

---

## Phase 1 — Folder & Scope Foundation

### Task 1: Rewrite the canonical workspace-scope.md

**Files:**
- Modify: `product-discovery/knowledge/discovery/workspace-scope.md` (full body replacement; the 14 skill `references/workspace-scope.md` symlinks pick this up automatically — verified symlinks in Task 1 Step 3)

- [ ] **Step 1: Replace the body** (everything from line 9 `# Discovery scope...` to end) with:

````markdown
# Discovery scope and path conventions

OST skills read and write inside the `OST-discovery/` folder. The default layout is **flat, single-product, single-round**. Product and round nesting are opt-in and appear only when actually needed.

## Default layout

```text
OST-discovery/
├── product-context/              # product-outcome.md, experience-map.md (human-readable inputs)
├── decisions.json                # ratified decisions — the spine
├── 1-opportunity.md              # milestone: opportunity selected (gate 06)
├── 2-solutions.md                # milestone: top-3 solutions (gate 09)
├── 3-riskiest-assumptions.md     # milestone: riskiest assumptions (gate 12)
├── 4-experiments.md              # milestone: validation experiments (gate 13, terminal)
└── _working/                     # ALL phase JSON + ALL intermediate markdown (viewer data source)
```

The scope is `OST-discovery/` itself.

## Multi-product (opt-in)

When one repo holds more than one product, each product gets its own subfolder and the scope is the product folder. The internal layout is identical to the default:

```text
OST-discovery/
├── <product-a>/   # product-context/, decisions.json, 1..4-*.md, _working/
└── <product-b>/
```

## Multiple rounds (opt-in)

The first discovery round lives flat (no date folder). A dated round folder appears **only when a second round starts** for the same product: move the first round's milestones + `decisions.json` + `_working/` into `rounds/<first-date>/`, keep `product-context/` at the product level, and create the new round beside it.

```text
OST-discovery/[<product>/]
├── product-context/
└── rounds/
    ├── <first-round-date>/   # 1..4-*.md + decisions.json + _working/
    └── <second-round-date>/
```

## Scope resolution

A skill resolves its scope (the folder it reads/writes inside), first that exists:

1. Explicit `scope=` argument.
2. `OST-discovery/.current-scope` — one-line relative path to the active scope folder. Written only when product/round nesting exists.
3. Default: `OST-discovery/` when flat. If nesting exists, prompt, defaulting to the only product / latest round.

## Path conventions within a scope

- `product-outcome.md`, `experience-map.md` → `<scope>/product-context/`. When the scope is a `rounds/<date>/` folder, walk up to the product-level context: `<scope>/../../product-context/`.
- `decisions.json` → `<scope>/decisions.json`.
- Milestone docs → `<scope>/<n>-<name>.md` (see table).
- **Everything else — all JSON for every phase, all intermediate markdown — → `<scope>/_working/<artifact>.{md,json}`.**

## Canonical files

**Visible at scope root (milestones + spine):**

| Gate | File |
|------|------|
| Decision record (all gates write here) | `decisions.json` |
| Opportunity selected (06) | `1-opportunity.md` |
| Top-3 solutions (09) | `2-solutions.md` |
| Riskiest assumptions (12) | `3-riskiest-assumptions.md` |
| Validation experiments (13) | `4-experiments.md` |

**Plumbing — written to `<scope>/_working/`:**

| Step | File |
|------|------|
| Opportunity extraction | `opportunities-extracted.{md,json}` |
| Experience map import | `experience-map-extracted.{md,json}` |
| Experience map clustering | `experience-map-clustered.{md,json}` |
| Opportunity validation | `opportunities-validated.md` |
| Comparison matrix | `comparison-matrix.{md,json}` |
| Opportunity selection (machine JSON) | `chosen-opportunity-proposal.json` |
| Solution brainstorm | `solution-candidates.{md,json}` |
| Solution cluster | `clustered-solutions.{md,json}` |
| Top-3 selection (machine JSON) | `top-three-solutions.json` |
| Assumption generation | `assumptions.{md,json}` |
| Assumption categorization | `assumptions-categorized.{md,json}` |
| Riskiest assumptions (machine JSON) | `riskiest-assumptions.json` |
| Validation experiments (machine JSON) | `validation-experiments.json` |

The four gate phases write their machine JSON to `_working/` and their **self-contained** human-readable markdown to the scope root as `<n>-<name>.md`.

## Slug convention

Product and (when nested) round folder names are short, lowercase, ASCII-only slugs. For Swedish names, transliterate `å→a, ä→a, ö→o`. The full title lives in frontmatter inside the folder; the slug is for the path only.
````

- [ ] **Step 2: Update the frontmatter** `purpose:` line to drop the "two layout modes" framing and `date:` to `2026-05-29`.

- [ ] **Step 3: Verify the symlinks still resolve.**

Run: `for d in product-discovery/skills/*/references/workspace-scope.md; do head -1 "$d" >/dev/null && echo "OK $d" || echo "BROKEN $d"; done`
Expected: every line prints `OK` (symlinks point at the rewritten canonical file).

- [ ] **Step 4: Commit.**

```bash
git add product-discovery/knowledge/discovery/workspace-scope.md
git commit -m "feat: flatten + rename OST workspace layout in scope spec (SCI-53)"
```

### Task 2: Rename `discovery/` → `OST-discovery/` across the plugin

**Files:**
- Modify: every file under `product-discovery/` that references the workspace path `discovery/` (NOT the plugin folder name `product-discovery`, NOT the prose words "discovery round"/"discovery scope").

- [ ] **Step 1: Enumerate hits for manual review.**

Run: `grep -rn 'discovery/' product-discovery/ --include='*.md' --include='*.py' --include='*.html' | grep -v 'product-discovery' | grep -v 'knowledge/discovery'`
Expected: a reviewable list of path references (skill prose like `discovery/.current-scope`, `serve.py` `--data path/to/discovery`, `viewer-launch.md`, decisions-json-schema location).

- [ ] **Step 2: For each hit, replace the workspace-path token `discovery/` with `OST-discovery/`** — but only where it denotes the top workspace folder. Do NOT touch `product-discovery`, the `knowledge/discovery/` source path, or the English phrases "discovery round" / "discovery scope" / "discovery trio". When unsure, the token is a path if it is followed by `/`, `.current-scope`, `<team>`, `_product-context`, or appears in a code block / `--data` argument.

- [ ] **Step 3: Path-trace check.**

Run: `grep -rn 'OST-discovery/' product-discovery/ | wc -l` (expect ≥ 1 per skill that names a path) and re-run the Step-1 grep — expect only intentional non-path "discovery" prose remains.

- [ ] **Step 4: Commit.**

```bash
git add -A product-discovery/
git commit -m "feat: rename workspace folder discovery/ -> OST-discovery/ (SCI-53)"
```

### Task 3: Rewrite the 00a scaffolding

**Files:**
- Modify: `product-discovery/skills/00a-OST-init-workspace/SKILL.md`

- [ ] **Step 1: Read the current scaffolding section** (the part that creates folders / branches single-vs-multi-product / handles date folders).

- [ ] **Step 2: Replace it** with single-product/flat scaffolding. The skill must create exactly:

```text
OST-discovery/
├── product-context/
├── _working/
└── decisions.json        # initialized to: {"schema_version":"1.0","product":"<slug>","team":null,"round":".","product_outcome":"","decided":{}}
```

Instruction text to insert (adapt to the skill's voice):

```markdown
Create the workspace at `OST-discovery/` (default, flat, single-product). Create `product-context/` and `_working/`. Initialize `decisions.json` at the root with empty `decided`. Do NOT create date-stamped round folders or `<team>/<product>/` nesting on first init — those are opt-in (see workspace-scope.md → Multi-product / Multiple rounds). Only scaffold a product subfolder if the user explicitly says the repo will hold more than one product.
```

- [ ] **Step 3: Remove** all references to `opportunity-selection/<date>/`, `opportunities/<slug>/<date>/`, `_product-context/` (now `product-context/`), and the single-vs-multi mode question (default to flat; ask only if user volunteers multiple products).

- [ ] **Step 4: Path-trace check.**

Run: `grep -n 'OST-discovery\|_working\|product-context\|opportunity-selection\|YYYY-MM-DD' product-discovery/skills/00a-OST-init-workspace/SKILL.md`
Expected: shows `OST-discovery`, `_working`, `product-context`; shows NO `opportunity-selection` or `YYYY-MM-DD` round scaffolding.

- [ ] **Step 5: Commit.**

```bash
git add product-discovery/skills/00a-OST-init-workspace/SKILL.md
git commit -m "feat: flat single-product scaffolding in 00a init-workspace (SCI-53)"
```

---

## Phase 2 — Route Plumbing JSON & Markdown to `_working/`

> **Uniform transformation rule for Tasks 4–6:** In each skill's input/output section, change every output path of the form `<scope>/<artifact>.json` to `<scope>/_working/<artifact>.json`, and every *plumbing* markdown `<scope>/<artifact>.md` to `<scope>/_working/<artifact>.md`. Change every *input* read of a prior artifact from `<scope>/<artifact>.{md,json}` to `<scope>/_working/<artifact>.{md,json}`. `decisions.json` stays at `<scope>/decisions.json` (root). Milestone markdown is handled in Phase 3, not here.

### Task 4: Relocate plumbing outputs — phases 01–05 (opportunity funnel)

**Files:**
- Modify: `01-OST-extract-experience-map/SKILL.md`, `02-OST-opportunity-extractor/SKILL.md`, `03-OST-validate-opportunities/SKILL.md`, `04-OST-cluster-opportunities/SKILL.md`, `05-OST-compare-opportunities/SKILL.md` (all under `product-discovery/skills/`)

Per-skill values to apply the transformation rule to:

| Skill | Outputs → new location |
|-------|------------------------|
| 01 | `experience-map-extracted.{md,json}` → `_working/`; ALSO write a human `experience-map.md` to `product-context/` |
| 02 | `opportunities-extracted.{md,json}` → `_working/` |
| 03 | `opportunities-validated.md` → `_working/` (reads `_working/opportunities-extracted.*`) |
| 04 | `experience-map-clustered.{md,json}` → `_working/` (reads `_working/opportunities-validated.md`) |
| 05 | `comparison-matrix.{md,json}` → `_working/` |

- [ ] **Step 1:** For each of the 5 skills, apply the uniform transformation rule using the table values. For skill 01 additionally add the instruction: `Also write a short human-readable experience-map.md to <scope>/product-context/ (the visible foundation copy).`
- [ ] **Step 2: Path-trace check.** Run: `grep -n 'scope>/\|_working' product-discovery/skills/0{1,2,3,4,5}-*/SKILL.md` — expect every artifact path now contains `_working/` except `product-context/experience-map.md`.
- [ ] **Step 3: Commit.** `git add product-discovery/skills/0{1,2,3,4,5}-*/SKILL.md && git commit -m "feat: route phase 01-05 plumbing to _working/ (SCI-53)"`

### Task 5: Relocate plumbing outputs — phases 07, 08 (solution funnel)

**Files:**
- Modify: `07-OST-brainstorm-solutions/SKILL.md`, `08-OST-cluster-solutions/SKILL.md`

| Skill | Outputs → new location |
|-------|------------------------|
| 07 | `solution-candidates.{md,json}` → `_working/` (do NOT change the 3-role × 3-round sub-agent structure — only the write path) |
| 08 | `clustered-solutions.{md,json}` → `_working/` (reads `_working/solution-candidates.json`) |

- [ ] **Step 1:** Apply the transformation rule. **Explicitly leave the sub-agent count, rounds, and role-anchor injection untouched** — this is a path-only edit (quality guardrail).
- [ ] **Step 2: Path-trace check.** Run: `grep -n 'solution-candidates\|clustered-solutions' product-discovery/skills/0{7,8}-*/SKILL.md` — expect `_working/` prefix on all.
- [ ] **Step 3: Divergence guard check.** Run: `grep -n -i 'three rounds\|3 round\|role\|sub-agent\|18' product-discovery/skills/07-OST-brainstorm-solutions/SKILL.md` — confirm the divergence instructions are unchanged from baseline (diff against `git show HEAD~:...` if unsure).
- [ ] **Step 4: Commit.** `git add product-discovery/skills/0{7,8}-*/SKILL.md && git commit -m "feat: route phase 07-08 plumbing to _working/ (SCI-53)"`

### Task 6: Relocate plumbing outputs — phases 10, 11 (assumption funnel)

**Files:**
- Modify: `10-OST-generate-assumptions/SKILL.md`, `11-OST-assumption-categorizer/SKILL.md`

| Skill | Outputs → new location |
|-------|------------------------|
| 10 | `assumptions.{md,json}` → `_working/` (do NOT change the multi-method passes) |
| 11 | `assumptions-categorized.{md,json}` → `_working/` (reads `_working/assumptions.json`) |

- [ ] **Step 1:** Apply the transformation rule; leave method-pass structure untouched.
- [ ] **Step 2: Path-trace check.** Run: `grep -n 'assumptions' product-discovery/skills/1{0,1}-*/SKILL.md` — expect `_working/` prefix.
- [ ] **Step 3: Commit.** `git add product-discovery/skills/1{0,1}-*/SKILL.md && git commit -m "feat: route phase 10-11 plumbing to _working/ (SCI-53)"`

---

## Phase 3 — Self-Contained Milestone Docs (gates 06, 09, 12, 13)

> Each gate writes: (a) machine JSON → `_working/<artifact>.json`; (b) `decisions.json` update at scope root (unchanged); (c) a NEW self-contained human markdown at scope root `<n>-<name>.md` that embeds the decision-relevant upstream reasoning so a reader never opens `_working/`.

### Task 7: Phase 06 → `1-opportunity.md`

**Files:**
- Modify: `product-discovery/skills/06-OST-select-opportunity/SKILL.md`

- [ ] **Step 1:** Change the JSON output path to `<scope>/_working/chosen-opportunity-proposal.json`. Keep the `decided.opportunity` write to `<scope>/decisions.json`.
- [ ] **Step 2:** Replace the markdown-output instruction so it writes `<scope>/1-opportunity.md` containing, in this order:

```markdown
1. The proposed opportunity (id, phase, verbatim quote, source) + rationale.
2. "Alternatives considered" — a table of EVERY other approved opportunity with a one-line why-not.
3. "How it compared" — the decision-relevant slice of the comparison matrix (the 5 Torres criteria × the chosen + top alternatives), pulled from _working/comparison-matrix.json so the reader sees what lost and on which criteria.
4. "Evidence gaps carried forward" — the AI-judged subset.
```

- [ ] **Step 3:** Add explicit instruction: `Read _working/comparison-matrix.json and _working/opportunities-validated.md to populate sections 2–3. 1-opportunity.md must stand alone — do not require the reader to open _working/.`
- [ ] **Step 4: Path-trace check.** Run: `grep -n '1-opportunity.md\|_working/chosen-opportunity-proposal.json\|decisions.json' product-discovery/skills/06-OST-select-opportunity/SKILL.md` — expect all three present.
- [ ] **Step 5: Commit.** `git add product-discovery/skills/06-OST-select-opportunity/SKILL.md && git commit -m "feat: phase 06 writes self-contained 1-opportunity.md (SCI-53)"`

### Task 8: Phase 09 → `2-solutions.md`

**Files:**
- Modify: `product-discovery/skills/09-OST-select-top-three-solutions/SKILL.md`

- [ ] **Step 1:** JSON output → `<scope>/_working/top-three-solutions.json`; keep `decided.solutions` write to `decisions.json`.
- [ ] **Step 2:** Markdown → `<scope>/2-solutions.md` containing: the 3 picks (title, description, outcome-mapping rationale) + an "Also considered" section listing the non-selected clusters/candidates (from `_working/clustered-solutions.json`) with why-not.
- [ ] **Step 3: Path-trace check.** Run: `grep -n '2-solutions.md\|_working/top-three-solutions.json' product-discovery/skills/09-*/SKILL.md` — expect both.
- [ ] **Step 4: Commit.** `git add product-discovery/skills/09-*/SKILL.md && git commit -m "feat: phase 09 writes self-contained 2-solutions.md (SCI-53)"`

### Task 9: Phase 12 → `3-riskiest-assumptions.md`

**Files:**
- Modify: `product-discovery/skills/12-OST-riskiest-assumptions/SKILL.md`

- [ ] **Step 1:** JSON output → `<scope>/_working/riskiest-assumptions.json`; keep `decided.assumptions` write to `decisions.json`.
- [ ] **Step 2:** Markdown → `<scope>/3-riskiest-assumptions.md` containing: the riskiest assumptions (importance=high AND evidence=weak) with rationale, shown **against the full categorized set** (from `_working/assumptions-categorized.json`) so the reader sees why the others were not flagged.
- [ ] **Step 3: Path-trace check.** Run: `grep -n '3-riskiest-assumptions.md\|_working/riskiest-assumptions.json' product-discovery/skills/12-*/SKILL.md` — expect both.
- [ ] **Step 4: Commit.** `git add product-discovery/skills/12-*/SKILL.md && git commit -m "feat: phase 12 writes self-contained 3-riskiest-assumptions.md (SCI-53)"`

### Task 10: Phase 13 → `4-experiments.md`

**Files:**
- Modify: `product-discovery/skills/13-OST-validation-experiment-designer/SKILL.md`

- [ ] **Step 1:** JSON output → `<scope>/_working/validation-experiments.json`; keep `decided.experiments` write to `decisions.json`.
- [ ] **Step 2:** Markdown → `<scope>/4-experiments.md` containing: one Bland Test Card per riskiest assumption (hypothesis, test, metric, numeric-anchored success criteria) + the 2 alternative tests per card.
- [ ] **Step 3: Path-trace check.** Run: `grep -n '4-experiments.md\|_working/validation-experiments.json' product-discovery/skills/13-*/SKILL.md` — expect both.
- [ ] **Step 4: Commit.** `git add product-discovery/skills/13-*/SKILL.md && git commit -m "feat: phase 13 writes self-contained 4-experiments.md (SCI-53)"`

### Task 11: Phase 00b setup paths

**Files:**
- Modify: `product-discovery/skills/00b-OST-setup-product/SKILL.md`

- [ ] **Step 1:** Update context-file writes: `product-outcome.md` and `experience-map.md` → `<scope>/product-context/` (was `_product-context/`). `decisions.json` → `<scope>/decisions.json`.
- [ ] **Step 2:** Remove the single-vs-multi-product mode question unless the user volunteers multiple products (default flat). Remove date-round language.
- [ ] **Step 3: Path-trace check.** Run: `grep -n 'product-context\|_product-context\|decisions.json\|OST-discovery' product-discovery/skills/00b-*/SKILL.md` — expect `product-context/` (no leading underscore), no `_product-context`.
- [ ] **Step 4: Commit.** `git add product-discovery/skills/00b-*/SKILL.md && git commit -m "feat: 00b writes context to product-context/ + flat scope (SCI-53)"`

---

## Phase 4 — Viewer

### Task 12: Point the viewer at `_working/` for view JSON

**Files:**
- Modify: `product-discovery/templates/viewer/index.html`

Current `switchView` (≈ lines 1065–1086) fetches every view from `roundData.basePath + '/' + filename`, and `decisions.json` is rendered from already-loaded `roundData.decisions`. All non-decisions JSON now lives in `_working/`.

- [ ] **Step 1: Write the failing smoke check first.** Create a throwaway fixture dir `templates/viewer/_smoke/` mirroring the NEW layout: `decisions.json` at root and `_working/comparison-matrix.json` etc. Launch `python3 templates/serve.py --templates templates/viewer --data templates/viewer/_smoke`, open `/_viewer`, click the "Comparison Matrix" tab.
Expected BEFORE fix: "Could not load comparison-matrix.json" (it's fetching from root, not `_working/`).

- [ ] **Step 2: Fix the fetch path.** In `switchView`, change the non-decisions fetch from:

```javascript
  var json = await loadJSON(roundData.basePath + '/' + filename);
```
to:
```javascript
  var json = await loadJSON(roundData.basePath + '/_working/' + filename);
```
Leave the `decisions.json` early-return branch (renders from `roundData.decisions`) untouched.

- [ ] **Step 3:** Check the round-loading code that builds `roundData` / lists JSON (the directory-listing fetch). If it lists JSON from `basePath` to discover available views, point that listing at `basePath + '/_working/'` as well; keep `decisions.json` loaded from `basePath` root.

- [ ] **Step 4: Run the smoke check again.** Expected AFTER fix: the Comparison Matrix, Solutions, Journey Map, Experience Map, Riskiest, Experiments tabs all render from `_working/`; the Decisions tab renders from root `decisions.json`.

- [ ] **Step 5: Remove the smoke fixture** and commit.

```bash
rm -rf product-discovery/templates/viewer/_smoke
git add product-discovery/templates/viewer/index.html
git commit -m "feat: viewer reads view JSON from _working/ (SCI-53)"
```

### Task 13: Update viewer-launch + schema docs

**Files:**
- Modify: `product-discovery/knowledge/discovery/viewer-launch.md`
- Modify: `product-discovery/knowledge/discovery/decisions-json-schema.md`

- [ ] **Step 1:** In `viewer-launch.md`, change the `--data` argument example to point at `OST-discovery/` (or the active scope folder) instead of `discovery/`.
- [ ] **Step 2:** In `decisions-json-schema.md`, change the Location line `discovery/<round-folder>/decisions.json` → `OST-discovery/[<product>/][rounds/<date>/]decisions.json` and confirm the existing rule line already says working artifacts live in `_working/` (it does — keep it).
- [ ] **Step 3: Commit.** `git add product-discovery/knowledge/discovery/viewer-launch.md product-discovery/knowledge/discovery/decisions-json-schema.md && git commit -m "docs: update viewer-launch + schema location for OST-discovery/_working (SCI-53)"`

---

## Phase 5 — Migration & Docs

### Task 14: Migration helper for existing workspaces

**Files:**
- Create: `product-discovery/skills/00a-OST-init-workspace/references/MIGRATION.md`

- [ ] **Step 1:** Write a plain-language migration note that a user (or Claude) can follow to convert an existing `discovery/` tree to the new layout:

```markdown
# Migrating an existing discovery/ workspace to OST-discovery/

1. Rename the top folder: `discovery/` → `OST-discovery/`.
2. Rename `_product-context/` → `product-context/`.
3. For each round folder, create `_working/` and MOVE into it every file EXCEPT
   `decisions.json` and any `1-`..`4-*.md` milestone docs.
4. Rename the gate proposal files to milestones if present:
   `chosen-opportunity-proposal.md` → `1-opportunity.md`,
   `top-three-solutions.md` → `2-solutions.md`,
   `riskiest-assumptions.md` → `3-riskiest-assumptions.md`,
   `validation-experiments.md` → `4-experiments.md`.
   (If the old run predates self-contained milestones, re-run the gate skill to regenerate them.)
5. If only one product/round, flatten: the round folder's contents become OST-discovery/ root;
   product-context/ moves to OST-discovery/product-context/.
6. Update `.current-scope` if present, or delete it for the flat default.
```

- [ ] **Step 2: Commit.** `git add product-discovery/skills/00a-OST-init-workspace/references/MIGRATION.md && git commit -m "docs: add OST workspace migration helper (SCI-53)"`

### Task 15: Update plugin docs

**Files:**
- Modify: `product-discovery/CLAUDE.md` and `product-discovery/README.md` (whichever reference `discovery/`)

- [ ] **Step 1:** Find references. Run: `grep -rn 'discovery/\|_product-context\|opportunity-selection/<' product-discovery/CLAUDE.md product-discovery/README.md 2>/dev/null`
- [ ] **Step 2:** Update any layout descriptions to the new flat `OST-discovery/` model with `_working/` and the 4 milestone docs. Remove two-mode descriptions.
- [ ] **Step 3: Commit.** `git add product-discovery/CLAUDE.md product-discovery/README.md && git commit -m "docs: update product-discovery docs for new OST layout (SCI-53)"`

---

## Phase 6 — Golden Regression Check

### Task 16: Re-run the pipeline and compare against baseline

**Files:**
- Create: `docs/superpowers/fixtures/ost-golden/after-track-a/` (new run outputs)

- [ ] **Step 1:** Sync the edited skills into the plugin cache (per repo CLAUDE.md iteration workflow): `cp -R product-discovery/skills/. ~/.claude/plugins/cache/scilla-studio/product-discovery/1.0.0/skills/` and restart the session so metadata reloads. (If running source-direct, skip.)
- [ ] **Step 2:** Run the full pipeline (00b→13) on the SAME frozen `INPUT.md` from Task 0. Copy the resulting `OST-discovery/` tree into `docs/superpowers/fixtures/ost-golden/after-track-a/`.
- [ ] **Step 3: File-count check (finding #2).** Run: `find docs/superpowers/fixtures/ost-golden/after-track-a/OST-discovery -maxdepth 1 -type f | grep -v _working` — expect exactly `decisions.json` + `1-opportunity.md` + `2-solutions.md` + `3-riskiest-assumptions.md` + `4-experiments.md` (5 files at root; everything else under `_working/` and `product-context/`).
- [ ] **Step 4: Quality check (finding #3).** Walk `RUBRIC.md` axis by axis comparing `after-track-a/` to `baseline/`. Every axis must hold (esp. axis 1: still 18 solution candidates; axis 4: milestone docs self-contained). If any axis fails, STOP — a path edit broke divergence/grounding; fix before proceeding.
- [ ] **Step 5: Viewer check.** Launch the viewer against `after-track-a/OST-discovery/` and confirm every tab renders.
- [ ] **Step 6: Commit.** `git add docs/superpowers/fixtures/ost-golden/after-track-a/ && git commit -m "test: golden regression after Track A — quality preserved (SCI-53)"`

---

## Self-Review (completed during authoring)

- **Spec coverage:** finding #1 (folders) → Tasks 1–3, 11, 15; finding #2 (files) → Tasks 4–10, verified Task 16 Step 3; finding #3 (quality guardrail) → Tasks 0, 5/6/10 divergence guards, Task 16 Step 4; folder rename (`OST-discovery/`) → Task 2; viewer consumption surface → Tasks 12–13; migration risk → Task 14; viewer data-path risk → Task 12; golden-run rubric risk → Task 0. Track B is out of scope per spec (own plan later).
- **Placeholder scan:** no TBD/TODO; every edit has exact paths, transformation rule, and a path-trace or smoke verification.
- **Consistency:** milestone filenames (`1-opportunity.md`…`4-experiments.md`), `_working/` plumbing location, and `decisions.json`-stays-at-root are used identically across Tasks 1, 4–13, 16.
```

> **Sequencing caution:** Phase 0 (golden baseline) MUST run on un-modified `master` before any Phase 1 edit, or there is nothing to regress against.
