---
name: OST-riskiest-assumptions
description: For product trios and researchers, when identifying the riskiest assumptions among the categorized assumptions for the top 3 solutions, output a paired JSON + markdown rendering with each assumption scored on importance (high/low) and evidence (strong/weak), and flagged as riskiest when importance=high AND evidence=weak. Phase-3 trio review gate; input to assist 12 (OST-validation-experiment-designer).
---

# OST-riskiest-assumptions

You help a product trio identify the riskiest assumptions among the categorized per-solution assumption lists produced by `OST-assumption-categorizer` (assist 10), using David Bland's 2x2 importance × evidence framework. This skill is assist 11 in the OST discovery workflow and the only assist in phase 4 (assumption risk mapping).

The skill is an identity map over upstream assumptions plus four new per-assumption fields (`importance`, `evidence`, `is_riskiest`, `rationale`). Every other upstream field carries through byte-identical: no re-ordering, no re-wording, no merging, no dropping. `is_riskiest` is computed by the skill from `importance` and `evidence`; the LLM is forbidden from returning it.

This skill IS the phase-3 trio HITL gate. The markdown output opens with a `Trio HITL gate.` banner directing the trio to review the importance/evidence calls and edit `decisions.json` if they disagree. `decided.assumptions` in `decisions.json` is the ratified record read by assist 12.

## Prerequisites

- `OST-assumption-categorizer` (assist 10) has run; `assumptions-categorized.json` exists in `<scope>/` (or a sibling round folder).

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`. Discovery scope only.

2. **Load context via parent walk-up:**
   - `<scope>/decisions.json` (chosen opportunity, product outcome)
   - Same-round predecessor: `<scope>/assumptions-categorized.json` (with sibling-round fallback)

3. **Read the knowledge anchors:**
   - `references/assumption-risk-mapping.md` (v0.2; the 2x2 framework, the Swedish scoring questions, the soft-evidence rule, the rationale format rule, the carry-forward rules, the schema v0.2, the renderer template; this is the canonical source for everything below).
   - `references/assumption-types.md` (reference only; categorization is upstream).
   - `references/opportunity-solution-tree-teresa-torres.md` (the "test the riskiest assumptions" framing, CDH ch 9).
   - `references/assumption-categorization.md` (the upstream schema v0.1; parse the input JSON against this).

4. **Locate input.** List `<scope>/assumptions-categorized.json` (with sibling-round fallback), sort by the date in the filename descending, take the latest. Hard-exit if zero matches.

5. **Hard-exit checks.** Apply the triggers below. If any fire, write no output files. Emit a three-line error in this exact shape:

   ```text
   ERROR: <one-line failure>
   - Looked for: <pattern or field name and where>
   - Found: <what was actually present>
   - Remedy: <concrete next step the operator should take>
   ```

   Triggers:

   - No `assumptions-categorized.json` in `<scope>/` (with sibling-round fallback). Remedy: run `OST-assumption-categorizer` (assist 10) first.
   - Source JSON does not parse. Remedy: re-run `OST-assumption-categorizer`.
   - Source JSON `schema_version` is not `"0.1"`. Remedy: re-run `OST-assumption-categorizer` against v0.1.
   - Source `assumptions_per_solution.length` != 3. Remedy: re-run `OST-assumption-categorizer`.
   - Any per-solution `assumptions.length` outside `6..18`. Remedy: re-run upstream `OST-generate-assumptions`.
   - Any of the four knowledge anchors missing. Remedy: restore from git.

6. **Parse input.** Extract:
   - Top-level carried fields: `team`, `title`, `product_outcome`, `chosen_opportunity` (object), `source_assumptions`, `source_top_three_solutions`, `source_experience_map`, `categorization_summary`.
   - `assumptions_per_solution[]` (array of 3 entries with `pick_position`, `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number`, `assumptions[]`).
   - Build an index of all upstream `assumption` objects keyed by `assumption.id` for the later merge.

7. **Build the scoring input.** Flatten all assumptions across the 3 solutions into a single ordered list. For each assumption, format one line as:

   ```text
   <solution_id> :: <assumption.id> :: [<category>] :: <assumption.text>
   ```

   Including `category` grounds the importance call. Preserve the order: solution 1 in upstream order, then solution 2, then solution 3.

8. **Run one LLM scoring pass.** Issue a single LLM call. The prompt contains, in order:

   - **Role frame:** "You are scoring product-discovery assumptions on Bland's 2x2: importance (high/low) and evidence (strong/weak). Riskiest = high importance + weak evidence."

   - **The two scoring questions** verbatim from `assumption-risk-mapping.md` v0.1 (Swedish-language original preserved verbatim):
     - **Q1 (evidence):** *Har vi redan bevis för att det här antagandet är sant?* Yes → `strong`. No → `weak`.
     - **Q2 (importance):** *Om vi har fel i det här antagandet, skiter det sig då?* Yes → `high`. No → `low`.

   - **The soft-evidence rule** verbatim from v0.2:

     > Evidence includes empirical observation from the inputs AND domain norms, industry conventions, and general engineering practice. Mark `strong` if the assumption seems well-grounded; mark `weak` if genuinely speculative.

   - **The "skiter det sig" semantics** verbatim from v0.1:

     > The solution materially fails to deliver its impact on the product outcome. Edge-case wobbles do not qualify. The bar is whether the solution as a whole stops working.

   - **The rationale format rule** verbatim from v0.2:

     > Write rationale as one sentence in the form `Importance=<level> (<reason>); evidence=<level> (<reason>).` Each parenthetical reason is one short clause.

   - **Solution context block:** for each of the 3 solutions, list `solution_id`, `title`, `description`, `generating_role`, `round_number`.

   - **Carried context:** chosen opportunity (id, phase, quote, source) and product outcome (verbatim).

   - **The full flattened list of assumptions** (one per line, in the format from step 7).

   - **Task:** "For each assumption, return a JSON object `{id, importance, evidence, rationale}`. Use exactly one value from `{high, low}` for importance and `{strong, weak}` for evidence. Write rationale in the structured format. Return only a JSON array, one per assumption, in the same order as the input. No other fields, no prose preamble. Do NOT return `is_riskiest`; the skill computes that."

   Collect the response. Parse as a JSON array. If parsing fails, hard-exit:

   ```text
   ERROR: scoring LLM pass returned malformed JSON
   - Looked for: a JSON array of {id, importance, evidence, rationale} objects
   - Found: <first 200 chars of response>
   - Remedy: re-run; if persistent, the prompt's JSON instruction needs tightening
   ```

9. **Validate the scoring response.** Verify:
   - Length equals the total upstream assumption count.
   - Every entry has `id`, `importance`, `evidence`, `rationale` strings.
   - Every `importance` in `{high, low}`.
   - Every `evidence` in `{strong, weak}`.
   - Every `rationale` matches the regex `^Importance=(high|low) \(.+\); evidence=(strong|weak) \(.+\)\.$`.
   - The set of ids equals the upstream id set (no missing, no unknown).
   - No duplicate ids.
   - No entry contains `is_riskiest` (forbidden).

   Any failure → hard-exit naming the specific failure.

10. **Compute `is_riskiest` deterministically.** For each scored entry: `is_riskiest = (importance == "high" AND evidence == "weak")`.

11. **Merge scores back into the upstream structure.** Build a lookup map `scores_by_id[id] = {importance, evidence, is_riskiest, rationale}`. For each upstream assumption, build the output object as a copy of upstream plus the four new fields. Every other field carries byte-identical. Preserve upstream `assumptions[]` order (identity-mapping).

12. **Compose the v0.2 JSON.**

    Top-level fields:
    - `schema_version`: `"0.2"`.
    - `method`: `"assumption-risk-mapping"`.
    - `method_source`: `"David Bland, Testing Business Ideas (2019)"`.
    - `team`, `title`, `product_outcome`, `chosen_opportunity`, `source_assumptions`, `source_top_three_solutions`, `source_experience_map`, `categorization_summary`: carried byte-identical.
    - `source_assumptions_categorized`: basename of the source `assumptions-categorized.json` file.
    - `risk_summary`: the fixed v0.2 block:
      ```json
      {
        "framework": "2x2 importance x evidence (David Bland)",
        "evidence_rule": "soft: domain norms and industry conventions count",
        "rationale_format": "single sentence; importance-then-evidence",
        "total_assumptions": <integer; sum across all 3 solutions>,
        "total_riskiest": <integer; count where is_riskiest=true>
      }
      ```
    - `assumptions_per_solution`: array of 3 entries in upstream order, each carrying upstream fields plus the four new fields per assumption.

13. **Validate invariants.** Before writing output:
    - `schema_version == "0.2"`, `method`/`method_source` exact.
    - `assumptions_per_solution.length == 3`.
    - Per-solution `assumptions.length` equals upstream; ids in same order at each index.
    - Every `importance` in `{high, low}`; every `evidence` in `{strong, weak}`.
    - Every `rationale` matches the regex.
    - For each assumption: `is_riskiest == (importance == "high" AND evidence == "weak")`.
    - Every `id`, `text`, `source_methods`, `category` byte-identical to upstream.
    - All carried top-level and per-solution fields byte-identical.
    - `risk_summary.total_assumptions` and `total_riskiest` match actual counts.
    - `risk_summary` strings match the fixed v0.2 values.

    Any violation → hard-exit, no write.

14. **Write paired output:**
    - `<scope>/riskiest-assumptions.json`
    - `<scope>/riskiest-assumptions.md`
    Create the directory if absent.

15. **Write to decisions.json.** Read `<scope>/decisions.json`. Set `decided.assumptions`:

    ```json
    {
      "ratified": "<today YYYY-MM-DD>",
      "riskiest": [
        {
          "id": "<asm-id>",
          "solution_id": "<sol-id>",
          "text": "<assumption text>",
          "category": "<category>",
          "importance": "high",
          "evidence": "weak",
          "rationale": "<rationale>"
        }
      ]
    }
    ```

    Include only assumptions where `is_riskiest == true`.

16. **Render the markdown deterministically from the JSON.** Use this exact template:

    ````markdown
    ---
    title: "Riskiest assumptions: <chosen_opportunity.id> - <first 5-10 words of quote>"
    date: <YYYY-MM-DD>
    purpose: Per-solution assumptions scored on importance x evidence (Bland 2x2), with the riskiest flagged. Phase-3 trio review-and-approve gate. Paired with riskiest-assumptions.json. Input to assist 12 (OST-validation-experiment-designer).
    tags: [assumption-risk-mapping, ost, bland, schema-v0.2]

    ---

    # Riskiest assumptions: <chosen_opportunity.id>

    > **Trio HITL gate.** Review the importance/evidence calls per assumption. If you disagree with any importance/evidence scoring, edit `decided.assumptions.riskiest[]` in `decisions.json` directly (add or remove entries). The `decided.assumptions` section is the ratified record. Riskiest rows are flagged `[RISKIEST]` inline; each solution opens with a `Riskiest:` summary line of the flagged ids.

    Source assumptions-categorized: `<source_assumptions_categorized>`
    Source assumptions: `<source_assumptions>`
    Source top 3 solutions: `<source_top_three_solutions>`
    Source chosen opportunity: `<scope>/decisions.json`
    Source product outcome: `<scope>/decisions.json`
    Schema version: 0.2
    Paired JSON: `riskiest-assumptions.json`

    Framework: 2x2 importance x evidence (David Bland, *Testing Business Ideas* 2019). Riskiest = high importance + weak evidence. Evidence rule: soft (domain norms and industry conventions count). Rationale format: single sentence, importance-then-evidence.

    Total assumptions: <N>. Total riskiest: <M>.

    ## Chosen opportunity

    **<chosen.id>** (Phase: <phase_id>) - "<quote>" - *<source>*

    ## Product outcome

    > <outcome formulation>

    ## Solution 1: <solution_title>

    **<solution_id>** [<role-abbrev>, R<round_number>]

    <solution_description>

    **Riskiest:** <comma-separated ids of riskiest in this solution, or "(none)">

    ### Assumptions (<count>)

    - **<asm-id>** [<methods-tag>] [<category>] [<importance>/<evidence>] [optional **[RISKIEST]**] <text>
      - <rationale>
    - **<asm-id>** [<methods-tag>] [<category>] [<importance>/<evidence>] <text>
      - <rationale>
    - ...

    ## Solution 2: <solution_title>

    (same shape)

    ## Solution 3: <solution_title>

    (same shape)
    ````

    **Rendering rules:**

    - Role abbreviation: `product-manager` -> `PM`, `ux-designer` -> `UX`, `tech-lead` -> `TL`. Render in the solution header as `[<role-abbrev>, R<round_number>]`.
    - Method tag: `storymap` -> `SM`, `pre-mortem` -> `PrM`, `outcome-impact` -> `OI`. Multi-source combined alphabetically with `+`. Examples: `[OI+SM]`, `[PrM+SM]`, `[OI+PrM+SM]`.
    - Category tag: lowercase verbatim in brackets, no abbreviation: `[desirability]`, `[usability]`, `[feasibility]`, `[viability]`, `[other]`.
    - Score tag: `[<importance>/<evidence>]` with values lowercase verbatim. Four possible values: `[high/strong]`, `[high/weak]`, `[low/strong]`, `[low/weak]`.
    - `[RISKIEST]` marker: appears only when `is_riskiest=true`. Bold all-caps in brackets, placed AFTER the score tag and BEFORE the text. Format: `**[RISKIEST]**`.
    - Tag order per row is fixed: `[<methods>] [<category>] [<importance>/<evidence>] [optional RISKIEST]`. Methods -> category -> score -> optional riskiest marker -> text.
    - Rationale rendered as a nested sub-bullet under each assumption row, indented 2 spaces, single line, verbatim from JSON.
    - Per-solution `Riskiest:` summary line. Placed between the solution-description and the `### Assumptions` heading. Format: `**Riskiest:** <comma-separated ids>` or `**Riskiest:** (none)`.
    - Trio HITL banner: top-of-body blockquote (`>` prefix), after the H1 and before the source-metadata lines.
    - Total summary line: `Total assumptions: <N>. Total riskiest: <M>.` after the framework-summary paragraph.
    - Chosen-opportunity source attribution carried verbatim. Separated from the quote with ` - ` (regular dash).
    - No em-dash anywhere. Use regular dashes only.
    - Frontmatter must have a blank line before the closing `---`.
    - No `Cites:` line.
    - Pick ordering in the markdown mirrors the upstream `picks[]` array order.
    - Row ordering within each solution preserves the upstream `assumptions[]` order. No re-sort by score or risk.
    - Output language for assumption text and rationale matches the upstream (typically Swedish for this trio).

## Output principles

- The output is the phase-3 trio HITL gate. Markdown opens with a `Trio HITL gate.` banner; the trio reviews the calls and edits the paired JSON to override; assist 12 picks up the latest by date.
- Identity-mapping is the load-bearing invariant. Every upstream field byte-identical; only 4 new fields added per assumption.
- `is_riskiest` is computed by the skill, not returned by the LLM. Prevents LLM drift on the riskiest definition.
- The soft-evidence rule means the LLM may use domain norms as evidence. The trio overrides at HITL.
- Rationale format is structurally constrained: `Importance=<level> (<reason>); evidence=<level> (<reason>).` Regex-checked.
- No graded scoring. Binary axes only.
- Stay consistent across the three solutions: similar assumption text should score similarly.

## Vad skill INTE gör

- Reads interview transcripts, OST-brainstorm-solutions output, comparison matrix, validated opportunities, OST-cluster-solutions output, top-three-solutions JSON directly, the assumptions JSON, or the experience map. Only the upstream `assumptions-categorized.json` contract.
- Reads `<scope>/../chosen-opportunity.md`, `<scope>/../../../_product-context/product-outcome.md`, or `ratifications.md` beyond what scope-resolution provides. Identifying context flows through the upstream JSON.
- Appends to `ratifications.md`. The phase-3 HITL gate is markdown-banner-only.
- Reads role anchors. Role info is data only.
- Generates, modifies, merges, or drops assumptions. Identity-mapping is the contract.
- Re-orders assumptions. Row order preserves upstream.
- Returns `is_riskiest` from the LLM. The skill computes it.
- Uses graded scoring on importance or evidence. Binary axes only.
- Designs Test Cards or validation experiments. (Assist 12.)
- Scores riskiness across solutions (cross-solution comparison). Per-solution scoring only.
- Modifies upstream files. The `assumptions-categorized-*.json` and all context files stay immutable.
- Writes outside `<scope>/`. Output lives at `<scope>/riskiest-assumptions.{json,md}`.
- Adds an in-skill ratification mechanism. Trio gate is markdown-banner-only.
- Runs a JSON self-validation pass beyond the invariant check.
- Retries the scoring pass on partial failures. Hard-exit; operator re-runs end-to-end.
- Uses a `confidence`, `alt_importance`, `alt_evidence`, `risk_level`, or `shared_with` schema field.
- Spawns sub-agents. Single-pass scoring is the architecture.
- Defaults to a single axis value when uncertain. Force one binary value on each axis.
- Groups assumptions by risk in markdown. Flat row order preserves upstream; risk surfaces as a per-row marker and a per-solution summary line.
- Writes to Miro or any external surface. JSON + markdown only.
