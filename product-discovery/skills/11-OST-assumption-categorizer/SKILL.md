---
name: OST-assumption-categorizer
description: For product trios and researchers, when categorizing the deduped assumptions for the top 3 solutions into Cagan's five product-risk categories, output a paired JSON + markdown rendering with each assumption tagged in exactly one category. Input to assist 11 (OST-riskiest-assumptions).
---

# OST-assumption-categorizer

You help a product trio classify the deduped per-solution assumptions produced by `OST-generate-assumptions` (assist 9) into Marty Cagan's five product-risk categories. This skill is assist 10 in the OST discovery workflow and the second assist in phase 3 (assumption testing).

The skill is an identity map over upstream assumptions plus one new `category` field per assumption. Every other upstream field carries through byte-identical: no re-ordering, no re-wording, no merging, no dropping.

## Prerequisites

- `OST-generate-assumptions` (assist 9) has run; `assumptions.json` exists in the resolved `<scope>/_working/` (or a sibling-round fallback).

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`. Discovery scope only.

2. **Load context via parent walk-up:**
   - `<scope>/../chosen-opportunity.md`
   - `<scope>/../../../product-context/product-outcome.md`
   - Same-round predecessor: `<scope>/_working/assumptions.json` (with sibling-round fallback)

3. **Read the knowledge anchors:**
   - `references/assumption-categorization.md` (the schema, the category enum, the risk-falls tiebreaker rule, the 'other'-reservation rule, the carry-forward rules, the renderer template; this is the canonical source for everything below).
   - `references/assumption-types.md` (read the full "Definition" and "Application notes" sections per category; this is the authoritative taxonomy source the classification pass applies).
   - `references/product-operating-model-marty-cagan.md` (the Cagan-five framing that anchors the taxonomy).
   - `references/assumption-generation.md` (the upstream schema v0.1; parse the input JSON against this).

4. **Locate input.** List `<scope>/_working/assumptions.json` (with sibling-round fallback), take the latest. Hard-exit if zero matches.

5. **Hard-exit checks.** Apply the triggers below. If any fire, write no output files. Emit a three-line error in this exact shape:

   ```text
   ERROR: <one-line failure>
   - Looked for: <pattern or field name and where>
   - Found: <what was actually present>
   - Remedy: <concrete next step the operator should take>
   ```

   Triggers:

   - No `assumptions.json` in `<scope>/_working/` (or sibling-round fallback). Remedy: run `OST-generate-assumptions` (assist 9) first.
   - Source JSON does not parse. Remedy: re-run `OST-generate-assumptions`.
   - Source JSON `schema_version` is not `"0.1"`. Remedy: re-run `OST-generate-assumptions` against v0.1.
   - Source `assumptions_per_solution.length` != 3. Remedy: re-run `OST-generate-assumptions`.
   - Any per-solution `assumptions.length` outside `6..18`. Remedy: re-run `OST-generate-assumptions`.
   - Any of the four knowledge anchors missing (`assumption-categorization.md`, `assumption-types.md`, `product-operating-model-marty-cagan.md`, `assumption-generation.md`). Remedy: restore from git.

6. **Parse input.** Extract:

   - Top-level carried fields: `team`, `title`, `product_outcome`, `chosen_opportunity` (object), `source_top_three_solutions`, `source_experience_map`.
   - `assumptions_per_solution[]` (array of 3 entries with `pick_position`, `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number`, `assumptions[]`).
   - Build an index of all upstream `assumption` objects keyed by `assumption.id` for the later merge.

7. **Build the classification input.** Flatten all assumptions across the 3 solutions into a single ordered list. For each assumption, format one line as:

   ```text
   <solution_id> :: <assumption.id> :: <assumption.text>
   ```

   Preserve the order: solution 1's assumptions in upstream order, then solution 2's, then solution 3's. This is the prompt-input ordering, NOT the output ordering (output preserves per-solution upstream order via the merge step).

8. **Run one LLM classification pass.** Issue a single LLM call. The prompt contains, in order:

   - **Role frame:** "You are classifying product-discovery assumptions into Marty Cagan's five product-risk categories. Each assumption gets exactly one category. Apply the risk-falls rule: pick the category that describes the risk if the assumption turns out false."
   - **The five-category taxonomy** verbatim from `assumption-types.md` (the "Definition" and "Application notes" sections per category).
   - **The risk-falls tiebreaker rule** verbatim from `assumption-categorization.md`:

     > Assumptions often touch more than one category at the surface. Pick the category that describes the risk if the assumption turns out false. The rule is mechanical, not opinion-based: it asks what kind of risk the assumption carries, and points to the category that owns that risk.

   - **The 'other'-reservation rule** verbatim from `assumption-categorization.md`:

     > Force one of `{desirability, usability, feasibility, viability}` whenever an assumption fits even marginally. 'Other' is reserved for assumptions genuinely orthogonal to Cagan's four product risks: legal, ethical, regulatory, market-timing, organizational. If an assumption could reasonably fit `feasibility` (e.g., "we have the team capacity to ship in Q3"), it goes there, not in `other`. 'Other' is the narrow bucket, not the default fallback.

   - **Two worked examples** from `assumption-categorization.md` (chosen to disambiguate the two most common confusion zones):

     > "Users will tolerate a 2-second loading state at step X." -> **usability** (risk if false: users abandon the flow).
     >
     > "The Delfi API permits writes to the licens-table." -> **feasibility** (risk if false: the solution cannot be built).

   - **The full flattened list of assumptions** (one per line, in the format from step 7).
   - **Task:** "For each assumption, return a JSON object `{id, category}`. Use exactly one category from the enum `{desirability, usability, feasibility, viability, other}`. Apply the risk-falls rule for ambiguous cases. Reserve 'other' for assumptions outside Cagan's four risks (legal, ethical, regulatory, market-timing, organizational). Return only a JSON array of objects, one per assumption, in the same order as the input. No other fields, no prose preamble, no per-assumption rationale."

   Collect the response. Parse as a JSON array. If parsing fails, hard-exit:

   ```text
   ERROR: classification LLM pass returned malformed JSON
   - Looked for: a JSON array of {id, category} objects
   - Found: <first 200 chars of response>
   - Remedy: re-run; if persistent, the prompt's JSON instruction needs tightening
   ```

9. **Validate the classification response.** Verify:

   - Length equals the total upstream assumption count (sum of `assumptions[].length` across the 3 solutions).
   - Every entry has an `id` string and a `category` string.
   - Every `category` value is in `{desirability, usability, feasibility, viability, other}`.
   - The set of ids in the response equals the set of upstream `assumption.id` values (no missing ids, no unknown ids).
   - No duplicate ids in the response.

   If any check fails, hard-exit naming the specific failure.

10. **Merge classification back into the upstream structure.** Build a lookup map: `classification_by_id[id] = category`. For each upstream `assumption`, build the output assumption object as a copy of the upstream object plus `"category": classification_by_id[id]`. Every other field is carried byte-identical. Preserve upstream `assumptions[]` order within each per-solution entry (identity-mapping).

11. **Compose the v0.1 JSON.**

   Top-level fields:
   - `schema_version`: `"0.1"`.
   - `team`, `title`, `product_outcome`, `chosen_opportunity`, `source_top_three_solutions`, `source_experience_map`: carried byte-identical from upstream.
   - `source_assumptions`: basename of the source `assumptions-*.json` file (e.g., `"assumptions-2026-05-11.json"`).
   - `categorization_summary`: the fixed v0.1 block:
     ```json
     {
       "categories": ["desirability", "usability", "feasibility", "viability", "other"],
       "rule": "single-category per assumption, risk-falls tiebreaker",
       "total_assumptions": <integer; sum across all 3 solutions>
     }
     ```
   - `assumptions_per_solution`: array of 3 entries, in upstream order. Each entry has `pick_position`, `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number` carried byte-identical, and `assumptions[]` with the new `category` field merged per item.

12. **Validate invariants.** Before writing output, verify:

    - `schema_version == "0.1"`.
    - `assumptions_per_solution.length == 3`.
    - For each per-solution entry, `assumptions.length` equals the corresponding upstream per-solution entry's `assumptions.length`.
    - For each per-solution entry, the output `assumptions[]` ids appear in the same order as upstream at each index.
    - Every output `assumption.category` is in `{desirability, usability, feasibility, viability, other}`.
    - Every output `assumption.id`, `assumption.text`, `assumption.source_methods` is byte-identical to the upstream.
    - All carried top-level fields byte-identical to upstream.
    - All carried per-solution fields byte-identical to upstream.
    - `categorization_summary.total_assumptions` equals the summed assumption count.
    - `categorization_summary` matches the fixed v0.1 block (other than `total_assumptions`).

    If any invariant fails, hard-exit naming the specific invariant. Write no output.

13. **Write paired output.**

    - `<scope>/_working/assumptions-categorized.json`.
    - `<scope>/_working/assumptions-categorized.md`.

    Create `<scope>/_working/` if it does not exist. Same root name on both files.

14. **Render the markdown deterministically from the JSON.** Use this exact template:

    ````markdown
    ---
    title: "Categorized assumptions: <chosen_opportunity.id> - <first 5-10 words of quote>"
    date: <YYYY-MM-DD>
    purpose: Per-solution deduped assumption lists with Cagan-category tags. Paired with assumptions-categorized.json. Input to assist 11 (OST-riskiest-assumptions); trio gate downstream at assist 11.
    tags: [assumption-categorization, ost, schema-v0.1]

    ---

    # Categorized assumptions: <chosen_opportunity.id>

    Source assumptions: `<source_assumptions>`
    Source top 3 solutions: `<source_top_three_solutions>`
    Source chosen opportunity: `<scope>/../chosen-opportunity.md`
    Source product outcome: `<scope>/../../../product-context/product-outcome.md`
    Schema version: 0.1
    Paired JSON: `assumptions-categorized.json`

    Categorization rule: single category per assumption, risk-falls tiebreaker. 'Other' reserved for non-Cagan assumptions (legal, ethical, regulatory, market-timing, organizational).

    ## Chosen opportunity

    **<chosen.id>** (Phase: <phase_id>) - "<quote>" - *<source>*

    ## Product outcome

    > <outcome formulation>

    ## Solution 1: <solution_title>

    **<solution_id>** [<role-abbrev>, R<round_number>]

    <solution_description>

    ### Assumptions (<count>)

    - **<asm-id>** [<methods-tag>] [<category>] <text>
    - **<asm-id>** [<methods-tag>] [<category>] <text>
    - ...

    ## Solution 2: <solution_title>

    (same shape)

    ## Solution 3: <solution_title>

    (same shape)
    ````

    **Rendering rules:**

    - Role abbreviation: `product-manager` -> `PM`, `ux-designer` -> `UX`, `tech-lead` -> `TL`. Render in the solution header line as `[<role-abbrev>, R<round_number>]`.
    - Method tag: `storymap` -> `SM`, `pre-mortem` -> `PrM`, `outcome-impact` -> `OI`. Multi-source combined alphabetically with `+`. Examples: `[OI+SM]`, `[PrM+SM]`, `[OI+PrM+SM]`.
    - Category tag: lowercase verbatim in brackets, no abbreviation: `[desirability]`, `[usability]`, `[feasibility]`, `[viability]`, `[other]`.
    - Tag order per row is fixed: `[<methods-tag>] [<category>]`, in that order. The asm-id is bold-prefixed; tags follow; text follows.
    - Chosen-opportunity source attribution carried verbatim. Separate the quote from the source with ` - ` (regular dash).
    - No em-dash anywhere. Use regular dashes only.
    - Frontmatter must have a blank line before the closing `---`.
    - No `Cites:` line. No `Trio HITL` banner.
    - Pick ordering in the markdown mirrors the upstream `picks[]` array order.
    - Row ordering within each solution preserves the upstream `assumptions[]` order. No re-sort by category or triangulation.
    - Output language for assumption text matches the upstream (typically Swedish for this trio).

## Output principles

- The output is intermediate: it feeds assist 11 (OST-riskiest-assumptions). No in-skill HITL banner; the trio's review gate is at assist 11's output.
- Identity-mapping is the load-bearing invariant. Every upstream field byte-identical; one `category` added per assumption.
- The risk-falls rule is mechanical: ask what kind of risk the assumption carries, point to the category that owns that risk.
- 'Other' is the narrow bucket. Reserve it for genuinely non-Cagan assumptions (legal, ethical, regulatory, market-timing, organizational); never as an uncertainty fallback.
- No category-rationale in the schema or markdown. The choice is mechanical via the risk-falls rule; the trio can override at review by editing the JSON.
- Stay consistent across the three solutions. Similar assumption text in two different solutions should map to the same category.

## Vad skill INTE gör

- Reads interview transcripts, OST-brainstorm-solutions output, comparison matrix, validated opportunities, OST-cluster-solutions output, top-three-solutions JSON directly, or the experience map. Only the upstream `assumptions-*.json` contract.
- Reads `chosen-opportunity.md`, `product-outcome.md`, or `ratifications.md`. Identifying context flows through the upstream JSON; no ratification gate between assists 9 and 10.
- Reads role anchors (`role-product-manager.md` etc.). Role info is data only.
- Generates, modifies, merges, or drops assumptions. Identity-mapping is the contract.
- Re-orders assumptions. Row order preserves upstream.
- Scores, ranks, or flags assumptions as riskiest. (Assist 11.)
- Applies importance, evidence, or risk-level scoring. (Assist 11.)
- Generates test cards, validation plans, or experiment designs. (Future phase 4.)
- Applies cross-solution analysis or marks shared assumptions across solutions.
- Modifies upstream files. The `assumptions-*.json` and all context files stay immutable.
- Writes outside `<scope>/_working/`. Output lives in `<scope>/_working/`.
- Appends to `ratifications.md`.
- Adds an in-skill HITL banner. Trio gate is downstream at assist 11.
- Runs a JSON self-validation pass beyond the invariant check.
- Retries the classification pass on partial failures. Hard-exit; operator re-runs end-to-end.
- Uses a `rationale`, `confidence`, `alt_categories`, `risk_level`, `importance`, `evidence`, or `shared_with` schema field. All either downstream territory or v0.2 follow-ups.
- Spawns sub-agents. Single-pass classification is the architecture.
- Uses emoji or numeric encoding for category tags. Plain bracketed lowercase words only.
- Defaults to 'other' when uncertain. Force one of the four Cagan categories whenever an assumption fits even marginally.
- Groups assumptions by category in markdown. Flat row order preserves upstream; category surfaces as a per-row bracketed tag.
- Writes to Miro or any external surface. JSON + markdown only.
