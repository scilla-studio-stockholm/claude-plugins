---
name: OST-validation-experiment-designer
description: For product trios and researchers, when designing validation experiments for the riskiest assumptions surfaced in phase 4, output a paired JSON + markdown rendering with one Bland Test Card per riskiest assumption (hypothesis, test, metric, success criteria with required numeric anchor) plus 2 alternative tests. Terminal assist; trio reads, picks execution order, and runs.
---

# OST-validation-experiment-designer

You help a product trio design validation experiments for the riskiest assumptions surfaced by `OST-riskiest-assumptions` (assist 11), using David Bland's Test Card method and the cheapest-viable principle. This skill is assist 12 in the OST discovery workflow and the only assist in phase 5 (assumption validation experiments). It is the terminal assist in the discovery critical path.

The skill is a filtered identity map over upstream assumptions plus 2 new per-assumption fields (`recommended_test`, `alternative_tests`). Filter: `is_riskiest=true` only. Non-riskiest assumptions are dropped. Every upstream field for retained assumptions carries through byte-identical.

This skill is terminal. There is no downstream skill. The markdown output opens with a `Trio run-list handoff.` banner directing the trio to read the Test Cards, pick execution order based on resources/dependencies/capacity, and run the cheapest viable test first per Bland's principle.

## Prerequisites

- `OST-riskiest-assumptions` (assist 11) has run; `riskiest-assumptions.json` exists in `<scope>/` (or a sibling round).
- At least one assumption in the upstream input has `is_riskiest=true`.

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`. Discovery scope only.

2. **Load context:**
   - `<scope>/decisions.json` (for `chosen_opportunity` and `product_outcome`)
   - Same-round predecessor: `<scope>/riskiest-assumptions.json` (with sibling-round fallback)

3. **Read the knowledge anchors:**
   - `references/assumption-validation.md` (v0.2; Test Card structure, 12-test-type catalog, 5 selection principles, category-default mapping, success_criteria regex rule, filter + identity-mapping invariants, schema v0.2, renderer template).
   - `references/assumption-risk-mapping.md` (v0.2; upstream schema and semantics).
   - `references/assumption-types.md` (5-category taxonomy; reference for category-default mapping).
   - `references/opportunity-solution-tree-teresa-torres.md` (Torres "test the riskiest assumptions" framing, CDH ch 9).

4. **Locate input.** List `<scope>/riskiest-assumptions.json` (with sibling-round fallback), take the latest. Hard-exit if zero matches.

5. **Hard-exit checks.** Apply the triggers below. If any fire, write no output files. Emit a three-line error in this exact shape:

   ```text
   ERROR: <one-line failure>
   - Looked for: <pattern or field name and where>
   - Found: <what was actually present>
   - Remedy: <concrete next step the operator should take>
   ```

   Triggers:

   - No `riskiest-assumptions.json` in `<scope>/` (with sibling-round fallback). Remedy: run `OST-riskiest-assumptions` (assist 11) first.
   - Source JSON does not parse. Remedy: re-run assist 11.
   - Source JSON `schema_version` is not `"0.2"`. Remedy: re-run assist 11 against v0.2.
   - Source `assumptions_per_solution.length` != 3. Remedy: re-run assist 11.
   - Zero assumptions with `is_riskiest == true` across all solutions. Remedy: "No riskiest assumptions to validate. Either re-run assist 11 with stricter scoring, or accept that this opportunity has no leap-of-faith assumptions to test."
   - Any of the four knowledge anchors missing. Remedy: restore from git.

6. **Parse and filter.** Extract:
   - Top-level carried fields: `team`, `title`, `product_outcome`, `chosen_opportunity` (object), `source_assumptions_categorized`, `source_assumptions`, `source_top_three_solutions`, `source_experience_map`, `categorization_summary`, `risk_summary`.
   - `assumptions_per_solution[]` (3 entries with `pick_position`, `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number`, `assumptions[]`).
   - Filter each per-solution `assumptions[]` to entries where `is_riskiest == true`.
   - Build an index of retained assumptions keyed by `assumption.id`.
   - Compute `total_riskiest` from the filter (sum across solutions).
   - If `total_riskiest == 0`, hard-exit per Step 3.

7. **Build the Test Card design input.** Flatten retained assumptions across the 3 solutions into a single ordered list. For each retained assumption, format one line as:

   ```text
   <solution_id> :: <assumption.id> :: [<category>] :: [<importance>/<evidence>] :: <assumption.text> :: <assumption.rationale>
   ```

   Including importance/evidence/upstream-rationale grounds the Test Card framing. Preserve order: solution 1 retained in upstream order, then solution 2 retained, then solution 3 retained.

8. **Run one LLM Test Card design pass.** Issue a single LLM call. The prompt contains, in order:

   - **Role frame:** "You design Bland Test Cards for product-discovery assumptions that the trio has flagged as riskiest. Apply the cheapest-viable principle. Each Test Card has 4 fields (hypothesis, test, metric, success_criteria) plus 2 alternative tests."

   - **Test Card structure** verbatim from anchor v0.1: Hypothesis ("We believe that ..."), Test ("To verify that, we will ..."), Metric ("And measure ..."), Success criteria ("We are right if ...").

   - **Selection principles** verbatim from anchor v0.1: (1) Cheapest viable test first; (2) Match the test to the assumption type; (3) Prefer revealed preferences over stated ones; (4) Time-box the test; (5) Plan for both outcomes.

   - **Test type catalog** verbatim from anchor v0.1 (12-row table with `Best for / Cost / Time / Evidence` ratings).

   - **Category-default mapping** verbatim from anchor v0.2 (5-row table with defaults: desirability -> Customer interview; usability -> Paper or click-through prototype; feasibility -> Technical spike or proof-of-concept; viability -> Landing page with sign-up; other -> Customer interview fallback).

   - **Override rule + rationale format** verbatim from anchor v0.2:

     > For each assumption, start from the category default. If the specific assumption text suggests a better cheapest-viable, override and name the override in `recommended_test.rationale` using one of these verbatim formats: `Default for <category> is <default-test> (used as-is).` or `Default for <category> is <default-test>, but <chosen-test> fits because <reason>.`

   - **success_criteria regex rule** verbatim from anchor v0.2 with acceptable and rejected examples. The effective rule: success_criteria MUST contain at least one digit.

   - **Solution context block:** for each of the 3 solutions, `solution_id`, `title`, `description`, `generating_role`, `round_number`. Used to ground Test Card framing.

   - **Carried context:** chosen opportunity (id, phase, quote, source) and product outcome (verbatim). Used to ground Test Card outcomes.

   - **The full flat list of retained assumptions** (one per line, in the format from step 5).

   - **Task:** "For each assumption in the list, return a JSON object `{id, recommended_test, alternative_tests}`. `recommended_test` includes all 9 sub-fields: test_type, hypothesis, test_description, metric, success_criteria, estimated_cost, estimated_time, evidence_strength, rationale. `alternative_tests` is exactly 2 objects, each with `test_type` and `rationale`. Apply category-default with named override in `recommended_test.rationale` using the verbatim format. `success_criteria` MUST include at least one digit. Test Card prose (hypothesis, test_description, metric, success_criteria) in the language of the assumption text (typically Swedish). Return only a JSON array, one per retained assumption, in the same order as the input. No other fields, no prose preamble."

   Collect the response. Parse as a JSON array. If parsing fails, hard-exit:

   ```text
   ERROR: design LLM pass returned malformed JSON
   - Looked for: a JSON array of {id, recommended_test, alternative_tests} objects
   - Found: <first 200 chars of response>
   - Remedy: re-run; if persistent, the prompt's JSON instruction needs tightening
   ```

9. **Validate the design response.** Verify:

   - Length equals retained count.
   - Every entry has `id` (string), `recommended_test` (object), `alternative_tests` (array of length 2).
   - Every `recommended_test` has all 9 sub-fields with correct types.
   - Every `recommended_test.success_criteria` contains at least one digit (regex match).
   - Every `recommended_test.rationale` matches the Default-or-override regex: `^Default for (desirability|usability|feasibility|viability|other) is .+ \(used as-is\.\)$|^Default for (desirability|usability|feasibility|viability|other) is .+, but .+ fits because .+\.$`.
   - Every `recommended_test.estimated_cost` in `{low, medium, high}`.
   - Every `recommended_test.estimated_time` in `{hours, days, weeks}`.
   - Every `recommended_test.evidence_strength` in `{weak, moderate, strong}`.
   - Every `recommended_test.test_type` is a non-empty string. Soft warning (not hard-exit) if outside the 12-test catalog from v0.1 anchor.
   - Every `alternative_tests` entry has non-empty `test_type` and `rationale` strings.
   - The set of ids in the response equals the retained set (no missing, no unknown, no duplicates).

   Any failure → hard-exit naming the specific failure.

10. **Merge designs back into the filtered upstream structure.** Build a lookup map `designs_by_id[id] = {recommended_test, alternative_tests}`. For each retained upstream assumption, build the output assumption object as a copy of the upstream object plus the two new fields. Every other field carries byte-identical. Preserve upstream order (identity-mapping).

11. **Compose the v0.2 JSON.**

   Top-level fields:
   - `schema_version`: `"0.2"`.
   - `method`: `"assumption-validation-bland"`.
   - `method_source`: `"David Bland, Testing Business Ideas (2019)"`.
   - `team`, `title`, `product_outcome`, `chosen_opportunity`, `source_assumptions_categorized`, `source_assumptions`, `source_top_three_solutions`, `source_experience_map`, `categorization_summary`, `risk_summary`: carried byte-identical from upstream.
   - `source_riskiest_assumptions`: basename of the source `riskiest-assumptions-*.json` file.
   - `validation_summary`: the fixed v0.2 block:
     ```json
     {
       "framework": "Bland Test Card with cheapest-viable selection (David Bland)",
       "selection_rule": "category-default with named override; alternative_tests fixed at 2",
       "success_criteria_rule": "regex-anchored numeric threshold required",
       "total_riskiest": <integer; from upstream risk_summary.total_riskiest>,
       "total_test_cards": <integer; count of Test Cards produced; equals total_riskiest>
     }
     ```
   - `assumptions_per_solution`: array of 3 entries in upstream order. Each entry has the per-solution carried fields plus `assumptions[]` filtered to retained set with 2 new fields per assumption merged in.

12. **Validate invariants.** Before writing output:

    - `schema_version == "0.2"`, `method`/`method_source` exact.
    - `assumptions_per_solution.length == 3`.
    - Per-solution `assumptions.length` equals upstream `is_riskiest=true` count for that solution.
    - Every retained assumption has `is_riskiest == true`.
    - Per-solution ids in retained set in same order as upstream.
    - Every retained assumption's `id`, `text`, `source_methods`, `category`, `importance`, `evidence`, `is_riskiest`, `rationale` byte-identical to upstream.
    - Every retained assumption has `recommended_test` (all 9 sub-fields) and `alternative_tests` (length=2).
    - Every `success_criteria` contains at least one digit.
    - Every `recommended_test.rationale` matches the Default-or-override regex.
    - Every enum value in scope.
    - All carried top-level fields byte-identical (including `categorization_summary` and `risk_summary`).
    - `source_riskiest_assumptions` is the source filename basename.
    - `validation_summary.total_test_cards == validation_summary.total_riskiest` and matches actual count.
    - `validation_summary` fixed strings match.

    Any violation → hard-exit, no write.

13. **Write paired output:**
    - `<scope>/_working/validation-experiments.json` (machine JSON; plumbing)
    - `<scope>/4-experiments.md` (self-contained MILESTONE doc at scope ROOT)
    Create the `_working/` directory if absent.

    `4-experiments.md` must stand alone — the reader (trio) should not need to open `_working/`. The milestone doc carries, per riskiest assumption, one full Bland Test Card (hypothesis, test, metric, success criteria with the required numeric anchor) plus the 2 alternative tests, so the trio can pick execution order and run experiments without touching the machine JSON.

14. **Write to decisions.json:** Read the round's `<scope>/decisions.json` (scope ROOT, not `_working/`). Set `decided.experiments`:

    ```json
    {
      "ratified": "<today YYYY-MM-DD>",
      "test_cards": [
        {
          "assumption_id": "<asm-id>",
          "solution_id": "<sol-id>",
          "test_type": "<test type>",
          "hypothesis": "We believe that ...",
          "metric": "And measure ...",
          "success_criteria": "We are right if ... (<numeric anchor>)",
          "estimated_cost": "<low|medium|high>",
          "estimated_time": "<hours|days|weeks>"
        }
      ]
    }
    ```

    One test card per riskiest assumption. Do not include `alternative_tests`.

15. **Render the markdown deterministically from the JSON.** Use this exact template:

    ````markdown
    ---
    title: "Validation experiments: <chosen_opportunity.id> - <first 5-10 words of quote>"
    date: <YYYY-MM-DD>
    purpose: Self-contained MILESTONE doc. Bland Test Cards for the riskiest assumptions surfaced in phase 4. Terminal run-list for the trio. Machine JSON at _working/validation-experiments.json (plumbing; not required to run experiments).
    tags: [assumption-validation, ost, bland, test-card, schema-v0.2]

    ---

    # Validation experiments: <chosen_opportunity.id>

    > **Trio run-list handoff.** This is the terminal artifact for the discovery critical path. Read the Test Cards; pick execution order based on resource availability, dependencies, and team capacity; run the cheapest viable test first per Bland's principle. The skill does NOT pick sequence. Capture results separately (a future Learning-Card skill is parked). If a recommended test does not fit your context, swap to one of the 2 alternatives.

    Source chosen opportunity: `<scope>/decisions.json`
    Source product outcome: `<scope>/decisions.json`
    Source OST-riskiest-assumptions: `<source_riskiest_assumptions>`
    Source assumptions-categorized: `<source_assumptions_categorized>`
    Source top 3 solutions: `<source_top_three_solutions>`
    Schema version: 0.2
    Machine JSON (plumbing, not required to run): `_working/validation-experiments.json`

    Framework: Bland Test Card with cheapest-viable selection. Category-default + named override. alternative_tests fixed at 2. success_criteria regex-anchored.

    Total riskiest: <N>. Total Test Cards: <N>.

    ## Chosen opportunity

    **<chosen.id>** (Phase: <phase_id>) - "<quote>" - *<source>*

    ## Product outcome

    > <outcome formulation>

    ## Solution 1: <solution_title>

    **<solution_id>** [<role-abbrev>, R<round_number>]

    <solution_description>

    **Test Cards in this solution (<count>):**

    ### <asm-id> [<methods-tag>] [<category>] [<importance>/<evidence>]

    **Assumption:** <text>

    **Upstream rationale:** <assumption.rationale carried verbatim from assist 11>

    **Recommended test: <test_type>**

    > **Hypothesis:** We believe that <...>.
    > **Test:** To verify that, we will <...>.
    > **Metric:** And measure <...>.
    > **Success criteria:** We are right if <... numeric anchor>.

    **Cost:** <low|medium|high> | **Time:** <hours|days|weeks> | **Evidence:** <weak|moderate|strong>

    **Why this test:** <recommended_test.rationale>

    **Alternatives:**

    - **<alt1.test_type>:** <alt1.rationale>
    - **<alt2.test_type>:** <alt2.rationale>

    ---

    ### <asm-id> [<methods-tag>] [<category>] [<importance>/<evidence>]

    (same Test Card shape)

    ---

    ## Solution 2: <solution_title>

    (same shape)

    ## Solution 3: <solution_title>

    (same shape)
    ````

    **Rendering rules:**

    - Carried tags: method-tag (`SM`/`PrM`/`OI`), category (`[desirability]` etc.), score (`[high/weak]` etc.; always `[high/weak]` for retained set), role-abbrev (`PM`/`UX`/`TL`).
    - Per-Test-Card heading: `### <asm-id> [<methods>] [<category>] [<imp>/<ev>]`. Tag order fixed.
    - Test Card prose: Bland 4-field block as `>` blockquote (each field on its own line, bold-prefixed).
    - Cost/time/evidence triple on one line, separated by ` | `.
    - "Why this test" line carries `recommended_test.rationale` verbatim.
    - "Upstream rationale" line carries `assumption.rationale` (from assist 11) verbatim.
    - Alternatives: 2 bullets, bold test_type + rationale.
    - Horizontal rule `---` between Test Cards within a solution. No trailing `---` after the last Test Card before the next `##`.
    - "Test Cards in this solution (count)" line between solution-description and first Test Card. If count is 0, render `**Test Cards in this solution (0):** _none - no riskiest assumptions to validate._` and skip the Test Card section.
    - Run-list HITL banner at top of body.
    - Total summary line under framework paragraph.
    - No em-dash anywhere. Frontmatter blank line before closing `---`. No `Cites:` line.
    - Pick ordering mirrors upstream `picks[]` order.
    - Row ordering within each solution preserves upstream order (among retained).
    - Output language: Test Card prose follows upstream language (typically Swedish). Schema field names, test_type names, enums, abbreviations stay English.

16. **Launch the viewer.** Follow `knowledge/discovery/viewer-launch.md` to resolve the viewer path, start the server, and open the browser.

## Output principles

- The output is the terminal artifact for the discovery critical path. Markdown opens with a run-list handoff banner; the trio reads, picks execution order, runs the cheapest viable first.
- Filtered identity-mapping is the load-bearing invariant. Every retained upstream field byte-identical; only 2 new fields added per assumption. Non-riskiest dropped.
- Apply category-default first, override only when assumption text justifies. Name the override in rationale.
- `success_criteria` is falsifiable: at least one digit required. Vague thresholds rejected.
- Cheapest viable: prefer low-cost tests; high cost should be rare and justified.
- Alternatives must be genuinely different from the recommended (not just cosmetic variants).
- Test Card prose grounded in the specific assumption and solution context, not boilerplate.
- The trio picks execution sequence based on resources, dependencies, and capacity. The skill does not propose sequence.

## Vad skill INTE gör

- Reads interview transcripts, OST-brainstorm-solutions output, comparison matrix, validated opportunities, OST-cluster-solutions output, top-three-solutions JSON directly, the assumptions JSON, the categorized JSON, or the experience map. Only the upstream `riskiest-assumptions-*.json` contract.
- Reads `chosen-opportunity.md`, `product-outcome.md`, or `ratifications.md` directly. Identifying context flows through `decisions.json`.
- Appends to `ratifications.md`. Writes `decided.experiments` to `decisions.json` only.
- Reads role anchors. Role info is data only.
- Includes non-riskiest assumptions in output. Filter is mandatory.
- Re-orders assumptions. Order preserved from upstream within retained set.
- Scores or re-flags riskiness. `is_riskiest` is carried byte-identical.
- Modifies upstream files. The `riskiest-assumptions.json` and all context files stay immutable.
- Writes outside `<scope>/`. Output lives in `<scope>/`.
- Adds an in-skill ratification mechanism.
- Picks execution sequence. Trio picks.
- Flags customer-access requirements as a structured field. Trio infers at HITL.
- Includes a Learning Card scaffold. Deferred.
- Runs experiments. Designs only.
- Provides more than 2 alternative tests. Fixed at 2.
- Provides finer-grained cost/time/evidence ratings than 3 buckets each.
- Runs a JSON self-validation pass beyond invariants.
- Retries the design pass on partial failures. Hard-exit; operator re-runs.
- Uses a `priority`, `sequence`, `requires_customer_access`, `learning_card`, or `confidence` schema field.
- Spawns sub-agents. Single-pass design is the architecture.
- Defaults to vague success_criteria. Numeric anchor required.
- Re-renders markdown when the trio edits JSON. Markdown is generated once.
- Writes to Miro or any external surface. JSON + markdown only.
