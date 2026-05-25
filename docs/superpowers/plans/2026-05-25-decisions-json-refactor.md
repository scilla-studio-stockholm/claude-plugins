# decisions.json Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace per-skill JSON files with a single `decisions.json` per discovery round as the durable record of trio-ratified decisions. Intermediate JSON files continue to exist for within-phase data passing but are no longer the source of truth for cross-phase reads.

**Architecture:** Skills at HITL gates (06, 09, 12, 13) append their section to `decisions.json`. Skills that need upstream ratified context (07, 08, 09, 10) read from `decisions.json` instead of `chosen-opportunity.md`, `ratifications.md`, or upstream JSON files. Intermediate artifacts stay where they are — no file moves in this phase.

**Schema spec:** `product-discovery/knowledge/discovery/decisions-json-schema.md`

**Scope boundary:** This plan covers `decisions.json` integration only. Two related refactors are explicitly out of scope:
- Moving intermediate files to `_working/` — future task
- Building the Opportunity Solution Tree (living artifact) — future task

---

### Task 1: Scaffold decisions.json in init_workspace.sh

**Files:**
- Modify: `product-discovery/skills/00a-OST-init-workspace/scripts/init_workspace.sh:413-428`

- [ ] **Step 1: Add decisions.json template function**

Add a shell function that generates the initial `decisions.json` envelope. Place it near the other template functions (after `chosen_opportunity_template`):

```bash
decisions_json_template() {
  local product="$1"
  local team="$2"
  local round="$3"
  cat <<ENDJSON
{
  "schema_version": "1.0",
  "product": "$product",
  "team": ${team:+"\"$team\""}${team:-"null"},
  "round": "$round",
  "product_outcome": "",
  "decided": {}
}
ENDJSON
}
```

- [ ] **Step 2: Create decisions.json when scaffolding a round folder**

In the `--opportunity` block (around line 418), after `mk_dir "$ROUND_DIR"`, add:

```bash
mk_file "$ROUND_DIR/decisions.json" "$(decisions_json_template "$PRODUCT" "$TEAM" "$ROUND_DIR")"
```

In the `--selection` block (around line 425), after `mk_dir "$ROUND_DIR"`, add:

```bash
mk_file "$ROUND_DIR/decisions.json" "$(decisions_json_template "$PRODUCT" "$TEAM" "$ROUND_DIR")"
```

- [ ] **Step 3: Verify idempotency**

Run: `bash product-discovery/skills/00a-OST-init-workspace/scripts/init_workspace.sh --single-product --product test-product --selection --date 2026-01-01`
Expected: `CREATED: .../decisions.json`

Run again:
Expected: `SKIPPED (exists): .../decisions.json`

Clean up: `rm -rf discovery/`

- [ ] **Step 4: Commit**

```bash
git add product-discovery/skills/00a-OST-init-workspace/scripts/init_workspace.sh
git commit -m "init-workspace: scaffold decisions.json in round folders"
```

---

### Task 2: Update setup-product to write product_outcome to decisions.json

**Files:**
- Modify: `product-discovery/skills/00b-OST-setup-product/SKILL.md`

- [ ] **Step 1: Add decisions.json write instruction**

Find the section where the skill writes `product-outcome.md` to `_product-context/`. After that instruction, add a step:

> After writing `product-outcome.md`, also update `decisions.json` in the active round folder: set `product_outcome` to the full outcome formulation string. Read the existing `decisions.json`, update the field, write it back. If `decisions.json` does not exist yet (round not scaffolded), skip this step.

- [ ] **Step 2: Commit**

```bash
git add product-discovery/skills/00b-OST-setup-product/SKILL.md
git commit -m "setup-product: write product_outcome to decisions.json"
```

---

### Task 3: Update select-opportunity to write decided.opportunity

**Files:**
- Modify: `product-discovery/skills/06-OST-select-opportunity/SKILL.md`

- [ ] **Step 1: Locate the output section**

Find where the skill writes `chosen-opportunity-proposal.json` and `chosen-opportunity-proposal.md`.

- [ ] **Step 2: Add decisions.json write**

After writing the proposal files, add this instruction:

> **Write to decisions.json:** Read the round's `decisions.json`. Set `decided.opportunity` with these fields extracted from the proposal:
>
> ```json
> {
>   "ratified": "<today YYYY-MM-DD>",
>   "id": "<chosen_opportunity.id>",
>   "phase_id": "<chosen_opportunity.phase_id>",
>   "quote": "<chosen_opportunity.quote>",
>   "source": "<chosen_opportunity.source>",
>   "scores": {
>     "outcome_alignment": "<score>",
>     "customer_importance": "<score>",
>     "market_size_frequency": "<score>",
>     "strategic_fit": "<score>",
>     "competitive_landscape": "<score>"
>   },
>   "rationale": "<rationale>",
>   "evidence_gaps": [<evidence_gaps_carried items>]
> }
> ```
>
> Write the updated `decisions.json` back.

- [ ] **Step 3: Update the HITL gate instructions**

Find the trio ratification instructions (where it tells the trio to create `chosen-opportunity.md`). Update to:

> The trio reviews the proposal markdown. If approved, `decided.opportunity` in `decisions.json` is the ratified record. The trio may edit `decisions.json` directly to adjust scores or rationale before approving. Creating `chosen-opportunity.md` at the opportunity-folder root is optional (human reference only — downstream skills read from `decisions.json`).

- [ ] **Step 4: Commit**

```bash
git add product-discovery/skills/06-OST-select-opportunity/SKILL.md
git commit -m "select-opportunity: write decided.opportunity to decisions.json"
```

---

### Task 4: Update brainstorm-solutions to read from decisions.json

**Files:**
- Modify: `product-discovery/skills/07-OST-brainstorm-solutions/SKILL.md`

- [ ] **Step 1: Replace chosen-opportunity.md read**

Find the input section that reads `chosen-opportunity.md` from `<scope>/..`. Replace with:

> Read `decisions.json` from the round folder. Extract `decided.opportunity` for the chosen opportunity context (id, phase_id, quote, source). Extract `product_outcome` for the product outcome. Hard-exit if `decided.opportunity` is missing from `decisions.json`.

- [ ] **Step 2: Remove product-outcome.md read (if separate)**

If the skill also reads `product-outcome.md` separately from `_product-context/`, replace that with: "Read `product_outcome` from `decisions.json`." This avoids the walk-up path resolution.

- [ ] **Step 3: Update the hard-exit conditions**

Replace any hard-exit that checks for missing `chosen-opportunity.md` with: hard-exit if `decisions.json` is missing or `decided.opportunity` key is absent.

- [ ] **Step 4: Commit**

```bash
git add product-discovery/skills/07-OST-brainstorm-solutions/SKILL.md
git commit -m "brainstorm-solutions: read from decisions.json instead of chosen-opportunity.md"
```

---

### Task 5: Update cluster-solutions to read from decisions.json

**Files:**
- Modify: `product-discovery/skills/08-OST-cluster-solutions/SKILL.md`

- [ ] **Step 1: Replace chosen-opportunity.md and product-outcome.md reads**

Same pattern as Task 4. Find references to `chosen-opportunity.md` and `product-outcome.md`. Replace with reads from `decisions.json` → `decided.opportunity` and `product_outcome`.

- [ ] **Step 2: Update hard-exit conditions**

Replace missing-file hard-exits with `decisions.json` key-presence checks.

- [ ] **Step 3: Commit**

```bash
git add product-discovery/skills/08-OST-cluster-solutions/SKILL.md
git commit -m "cluster-solutions: read from decisions.json instead of chosen-opportunity.md"
```

---

### Task 6: Update select-top-three to write decided.solutions

**Files:**
- Modify: `product-discovery/skills/09-OST-select-top-three-solutions/SKILL.md`

- [ ] **Step 1: Replace chosen-opportunity.md and product-outcome.md reads**

Same pattern as Tasks 4-5. Read from `decisions.json`.

- [ ] **Step 2: Add decisions.json write**

After writing `top-three-solutions.json` and `top-three-solutions.md`, add:

> **Write to decisions.json:** Read the round's `decisions.json`. Set `decided.solutions`:
>
> ```json
> {
>   "ratified": "<today YYYY-MM-DD>",
>   "picks": [
>     {
>       "id": "<sol-id>",
>       "title": "<title>",
>       "description": "<description>",
>       "rationale": "<rationale>"
>     }
>   ]
> }
> ```
>
> Exactly 3 picks. Do not include `generating_role` or `round_number`.

- [ ] **Step 3: Update ratification instructions**

Find the section about appending to `ratifications.md`. Replace with:

> The trio reviews the markdown output. If approved, `decided.solutions` in `decisions.json` is the ratified record. The trio may edit `decisions.json` to swap picks or adjust rationale. Appending to `ratifications.md` is no longer required.

- [ ] **Step 4: Commit**

```bash
git add product-discovery/skills/09-OST-select-top-three-solutions/SKILL.md
git commit -m "select-top-three: write decided.solutions to decisions.json"
```

---

### Task 7: Update generate-assumptions to read from decisions.json

**Files:**
- Modify: `product-discovery/skills/10-OST-generate-assumptions/SKILL.md`

This is the biggest single change. Skill 10 currently reads `ratifications.md` to verify the trio ratified the top-3, then reads `top-three-solutions.json` for solution data. Both reads get replaced.

- [ ] **Step 1: Replace ratifications.md check**

Find the hard-exit that checks `ratifications.md` for a `top-three-solutions` ratification line. Replace with:

> Read `decisions.json` from the round folder. Hard-exit if `decided.solutions` is missing — this means the trio has not yet ratified the top 3.

- [ ] **Step 2: Replace top-three-solutions.json read**

Find where the skill reads `top-three-solutions.json` (with sibling-round fallback). Replace with:

> Read solution data from `decisions.json` → `decided.solutions.picks[]`. Each pick has `id`, `title`, `description`, `rationale`. Use these as the solution context for assumption generation sub-agents.

- [ ] **Step 3: Replace chosen-opportunity.md and product-outcome.md reads**

Same pattern as Tasks 4-5. Read from `decisions.json`.

- [ ] **Step 4: Update hard-exit conditions**

Remove hard-exits for:
- Missing `ratifications.md`
- Missing ratification line pattern
- Missing `top-three-solutions.json`

Replace with: hard-exit if `decisions.json` is missing or lacks `decided.solutions`.

- [ ] **Step 5: Remove sibling-round fallback for top-three-solutions.json**

The sibling-round fallback logic is no longer needed since `decisions.json` is authoritative. Remove it.

- [ ] **Step 6: Commit**

```bash
git add product-discovery/skills/10-OST-generate-assumptions/SKILL.md
git commit -m "generate-assumptions: read from decisions.json, drop ratifications.md dependency"
```

---

### Task 8: Update riskiest-assumptions to write decided.assumptions

**Files:**
- Modify: `product-discovery/skills/12-OST-riskiest-assumptions/SKILL.md`

- [ ] **Step 1: Add decisions.json write**

After writing `riskiest-assumptions.json` and `riskiest-assumptions.md`, add:

> **Write to decisions.json:** Read the round's `decisions.json`. Set `decided.assumptions`:
>
> ```json
> {
>   "ratified": "<today YYYY-MM-DD>",
>   "riskiest": [
>     {
>       "id": "<asm-id>",
>       "solution_id": "<sol-id>",
>       "text": "<assumption text>",
>       "category": "<category>",
>       "importance": "high",
>       "evidence": "weak",
>       "rationale": "<rationale>"
>     }
>   ]
> }
> ```
>
> Include only assumptions where `is_riskiest == true`.

- [ ] **Step 2: Update HITL gate instructions**

Update the trio review section to reference `decisions.json`:

> The trio reviews the riskiest assumptions in the markdown output. If they disagree with any importance/evidence scoring, they edit `decided.assumptions.riskiest[]` in `decisions.json` directly (add or remove entries). The `decided.assumptions` section is the ratified record.

- [ ] **Step 3: Commit**

```bash
git add product-discovery/skills/12-OST-riskiest-assumptions/SKILL.md
git commit -m "riskiest-assumptions: write decided.assumptions to decisions.json"
```

---

### Task 9: Update validation-experiment-designer to write decided.experiments

**Files:**
- Modify: `product-discovery/skills/13-OST-validation-experiment-designer/SKILL.md`

- [ ] **Step 1: Add decisions.json write**

After writing `validation-experiments.json` and `validation-experiments.md`, add:

> **Write to decisions.json:** Read the round's `decisions.json`. Set `decided.experiments`:
>
> ```json
> {
>   "ratified": "<today YYYY-MM-DD>",
>   "test_cards": [
>     {
>       "assumption_id": "<asm-id>",
>       "solution_id": "<sol-id>",
>       "test_type": "<test type>",
>       "hypothesis": "We believe that ...",
>       "metric": "And measure ...",
>       "success_criteria": "We are right if ... (<numeric anchor>)",
>       "estimated_cost": "<low|medium|high>",
>       "estimated_time": "<hours|days|weeks>"
>     }
>   ]
> }
> ```
>
> One test card per riskiest assumption. Do not include `alternative_tests`.

- [ ] **Step 2: Commit**

```bash
git add product-discovery/skills/13-OST-validation-experiment-designer/SKILL.md
git commit -m "validation-experiment-designer: write decided.experiments to decisions.json"
```

---

### Task 10: Update workspace-scope.md canonical reference

**Files:**
- Modify: `product-discovery/knowledge/discovery/workspace-scope.md:64-94`

- [ ] **Step 1: Add decisions.json to the canonical filenames table**

Add at the top of the table (line 78):

```markdown
| Decision record | `decisions.json` |
```

- [ ] **Step 2: Update context walk-up section**

In the context walk-up section (lines 60-74), add:

> - `decisions.json` → `<scope>/decisions.json` (same round folder; no walk-up needed)

- [ ] **Step 3: Add deprecation note for chosen-opportunity.md and ratifications.md as skill inputs**

After the canonical filenames table, add:

> **Deprecated as skill inputs (read from `decisions.json` instead):**
> - `chosen-opportunity.md` — skills 07, 08, 09 previously read this; now read `decided.opportunity` from `decisions.json`. The file may still exist as a human-readable reference.
> - `ratifications.md` — skill 10 previously checked this for top-3 ratification; now checks `decided.solutions` in `decisions.json`. The file is no longer maintained.

- [ ] **Step 4: Commit**

```bash
git add product-discovery/knowledge/discovery/workspace-scope.md
git commit -m "workspace-scope: add decisions.json, deprecate chosen-opportunity.md and ratifications.md as skill inputs"
```

---

### Task 11: Update knowledge reference files

**Files:**
- Modify: `product-discovery/knowledge/discovery/top-three-selection.md` (lines 19, 55-56, 67 — ratifications.md references)
- Modify: `product-discovery/knowledge/discovery/assumption-generation.md` (line 17 — ratifications.md reference)
- Modify: `product-discovery/knowledge/discovery/opportunity-selection.md` (line 81 — chosen-opportunity.md copy instruction)

- [ ] **Step 1: Update top-three-selection.md**

Find references to `ratifications.md` (the append-only ratification pattern). Add a note:

> **Note:** As of schema v1.0, trio ratification is recorded in `decisions.json` → `decided.solutions`. The `ratifications.md` append pattern described below is deprecated. Skills read `decisions.json` for ratification status.

- [ ] **Step 2: Update assumption-generation.md**

Find the section describing how skill 10 reads `ratifications.md` to locate the ratified top-three. Add:

> **Note:** As of schema v1.0, skill 10 reads `decisions.json` → `decided.solutions` directly. The `ratifications.md` lookup described below is deprecated.

- [ ] **Step 3: Update opportunity-selection.md**

Find the instruction about copying `chosen-opportunity-proposal.md` to `chosen-opportunity.md`. Add:

> **Note:** As of schema v1.0, the ratified opportunity is recorded in `decisions.json` → `decided.opportunity`. Creating `chosen-opportunity.md` is optional (human reference only).

- [ ] **Step 4: Commit**

```bash
git add product-discovery/knowledge/discovery/top-three-selection.md \
        product-discovery/knowledge/discovery/assumption-generation.md \
        product-discovery/knowledge/discovery/opportunity-selection.md
git commit -m "knowledge: add decisions.json deprecation notes to reference files"
```

---

### Task 12: Update CLAUDE.md and README.md

**Files:**
- Modify: `CLAUDE.md` — update Current State section
- Modify: `product-discovery/README.md` — mention decisions.json in skill descriptions

- [ ] **Step 1: Update README.md**

In the "Skill flow" section preamble, add after the HITL explanation:

> Each round produces a single `decisions.json` that accumulates the trio's ratified decisions at each gate. Intermediate artifacts (comparison matrices, brainstorm outputs, assumption inventories) are working documents consumed within their phase. See `knowledge/discovery/decisions-json-schema.md` for the schema.

- [ ] **Step 2: Update CLAUDE.md current state**

Update the "Current State" and "Next steps" sections to reflect the decisions.json refactor work.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md product-discovery/README.md
git commit -m "docs: document decisions.json in README and update CLAUDE.md"
```

---

## Skills that need NO changes

| Skill | Why |
|---|---|
| 02 opportunity-extractor | Markdown-only output, no JSON reads |
| 03 validate-opportunities | Markdown-only output, no JSON reads |
| 04 cluster-opportunities | Reads/writes intermediate JSON within phase 1 only; no cross-phase dependency |
| 05 compare-opportunities | Reads/writes intermediate JSON within phase 1 only; no cross-phase dependency |
| 11 assumption-categorizer | Reads/writes intermediate JSON within phase 3 only; no cross-phase dependency |

These skills operate entirely within their phase using intermediate files. They don't read ratified upstream decisions and don't produce HITL gate outputs. They'll be updated later when intermediate files move to `_working/`.

## Future work (out of scope)

1. **`_working/` folder** — Move all intermediate JSON/MD to `_working/` subfolder. Update within-phase read paths. Add `_working/` to init-workspace scaffolding.
2. **Opportunity Solution Tree** — Living artifact accumulating validated opportunities across rounds. Separate design needed.
3. **SCI-27** — Rename `ratifications.md` → `trio-decisions.md`. Lower priority now that `ratifications.md` is deprecated as a skill input; consider closing as won't-fix.
4. **Move extract-experience-map to Phase 0** — Renumber to `00c`. One-time setup step, not a recurring phase 1 activity.
