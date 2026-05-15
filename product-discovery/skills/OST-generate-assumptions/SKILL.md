---
name: OST-generate-assumptions
description: For product trios and researchers, when generating the assumptions that must hold for the top 3 solutions to move the product outcome, output a paired JSON + markdown rendering with three method-passes (storymap, pre-mortem, outcome-impact) per solution, deduped across methods with source-method attribution. Input to assist 10 (OST-assumption-categorizer).
---

# OST-generate-assumptions

You help a product trio decompose their 3 chosen solutions into the assumptions that must hold for each solution to deliver its intended impact on the product outcome. This skill is assist 9 in `skills-design/opportunity-solution-tree-agents.md` and the first assist in phase 3 (assumption testing).

## Prerequisites

- The trio has ratified a top-three-solutions proposal by appending a line to `<scope>/../ratifications.md` per the format in `../../knowledge/discovery/top-three-selection.md`.
- `<scope>/../chosen-opportunity.md` exists with a parseable bold-id row.
- `<scope>/../../../_product-context/product-outcome.md` exists with a `## Outcome` section.
- `<scope>/../../../_product-context/experience-map.json` (or `.md`) exists.
- `<scope>/top-three-solutions.json` exists in the current scope or in the ratified sibling round.

## Steps

1. **Resolve scope.** Follow `../../knowledge/discovery/workspace-scope.md`. Discovery scope only.

2. **Load context via parent walk-up:**
   - `<scope>/../chosen-opportunity.md`
   - `<scope>/../../../_product-context/product-outcome.md`
   - `<scope>/../ratifications.md` (required)
   - Same-round predecessor: `<scope>/top-three-solutions.json` (with sibling-round fallback)
   - `<scope>/../../../_product-context/experience-map.json` (or `.md`) — the experience map for context

3. **Read the knowledge anchors:**
   - `../../knowledge/discovery/assumption-generation.md` (the schema and the three-method definitions; this is the canonical source for everything below).
   - `../../knowledge/discovery/assumption-types.md` (read the "Definition" and "Application notes" sections for the meaning of "assumption". Do NOT apply the 5-category taxonomy here; that is assist 10's job).
   - `../../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` (the decompose-into-assumptions framing, CDH ch 8).
   - `../../knowledge/discovery/top-three-selection.md` (the source schema v0.2 and the ratification-flag pattern).

4. **Locate inputs:**

   - Read `<scope>/../ratifications.md`. Scan for lines matching the pattern `- <round-folder-date> top-three-solutions ratified by <approver> (<note>)` where round-folder-date is the round directly under the opportunity slug that contains the ratified top-three-solutions.json. The latest matching line (last in file order, append-only) gives the ratified round date. If `ratifications.md` does not exist or has no matching line, hard-exit per the format below.
   - Read `<scope>/top-three-solutions.json`. If it does not exist, fall back to the sibling round identified by the ratified round date in the ratifications entry. If neither exists, hard-exit.
   - Read `<scope>/../chosen-opportunity.md`. Hard-exit if missing.
   - Read `<scope>/../../../_product-context/product-outcome.md`. Hard-exit if missing or no `## Outcome` section.
   - Read `<scope>/../../../_product-context/experience-map.json` (fall back to `.md` if JSON is absent). Hard-exit if neither exists.

5. **Hard-exit checks.** Apply the triggers below. If any fire, write no output files. Emit a three-line error in this exact shape:

   ```text
   ERROR: <one-line failure>
   - Looked for: <pattern or field name and where>
   - Found: <what was actually present>
   - Remedy: <concrete next step the operator should take>
   ```

   Triggers:

   - `<scope>/../ratifications.md` missing.
   - No matching `top-three-solutions` ratification line in `<scope>/../ratifications.md`.
   - The referenced `top-three-solutions.json` missing in both current scope and the ratified sibling round.
   - Source JSON does not parse.
   - Source JSON `schema_version` is not `"0.2"`.
   - Source `picks[]` length != 3.
   - `<scope>/../chosen-opportunity.md` missing.
   - `chosen-opportunity.md` missing parseable bold-id row under `## Chosen opportunity` (format: `**<opp-id>** (Phase: <phase-id>) - "<quote>" - *<source>*`).
   - `<scope>/../../../_product-context/product-outcome.md` missing or no `## Outcome` section.
   - Neither `<scope>/../../../_product-context/experience-map.json` nor `experience-map.md` exists.
   - Any of the four knowledge anchors missing.

7. **Parse inputs.**

   - From the top-three JSON: extract `team`, `product_outcome`, `chosen_opportunity` (object with `id`, `phase_id`, `quote`, `source`), and `picks[]` (array of 3 objects with `id`, `title`, `generating_role`, `round_number`, `description`, `rationale`). Index `picks[]` by `id`.
   - From `chosen-opportunity.md`: extract the bold-id row's `id`, `phase_id`, `quote`, `source`.
   - From `product-outcome.md`: extract the `## Outcome` formulation (the prose under that heading).
   - Load the experience map JSON content for storymap sub-agent prompts. Keep as-is.

8. **Cross-check chosen-opp id.** The source top-three JSON's `chosen_opportunity.id` MUST match the chosen-opportunity.md bold-id row's `id`. If not, hard-exit with:

   ```text
   ERROR: chosen-opportunity id mismatch between source JSON and context.md
   - Looked for: identical id strings
   - Found: source JSON id "<x>" vs context.md bold-id "<y>"
   - Remedy: decide which version is authoritative; reconcile manually
   ```

9. **Spawn 9 method-pass sub-agents in parallel.** Issue a single tool-use block containing 9 Agent invocations, each with `subagent_type: general-purpose`. The 9 invocations are: (storymap, pick 1), (storymap, pick 2), (storymap, pick 3), (pre-mortem, pick 1), (pre-mortem, pick 2), (pre-mortem, pick 3), (outcome-impact, pick 1), (outcome-impact, pick 2), (outcome-impact, pick 3).

   Each sub-agent prompt is constructed from these parts in this order:

   - **Role frame:** "You are surfacing the assumptions that must hold for a specific product solution to move the product outcome, using the <method-name> method."
   - **Chosen opportunity grounding:** id, phase, quote, source.
   - **Product outcome:** the verbatim outcome formulation.
   - **The specific solution this sub-agent reasons about:** id, title, description, generating_role, round_number, rationale. Carried from the upstream picks entry.
   - **Method-specific framing** (drawn from `assumption-generation.md`, "The three methods" section). Use the verbatim definition for the assigned method:
     - **Storymap:** "Infer the user-flow for this solution (user types -> steps in time order). For each step, surface what must be true for that step to work for the user."
     - **Pre-mortem:** "Imagine 6 months out: this solution shipped, then failed. Walk the failure modes one by one. For each failure mode, name the underlying assumption that turned out false."
     - **Outcome-impact:** "State why this solution would move the product outcome. For each reason in that argument, name the underlying assumption that must hold for the reason to be valid."
   - **Storymap sub-agents only:** include the experience map JSON content with this instruction: "This is today's user journey. The solution may propose a new flow. Use this as anchoring but reason about the future flow the solution implies, not today's."
   - **Definition of assumption** (verbatim from `assumption-generation.md`): "An assumption is something the trio takes for granted but does not know to be true; if the assumption is false, the solution will not deliver its intended impact."
   - **Output language guidance:** "Write each assumption in the language used in the solution description (typically Swedish)."
   - **Task:** "Produce exactly 6 assumptions for this solution using the <method-name> method. Each assumption is 1-2 sentences max. Do not categorize assumptions (no 'this is a feasibility assumption' framing). Do not introduce effort vocabulary (complex, expensive, feasible, quick win). Return only a JSON array of 6 objects with shape `{text: string}`. No other fields, no prose preamble."

   Collect the 9 sub-agent responses. Parse each as a JSON array. If any returns malformed JSON or count != 6, hard-exit per format.

10. **Run 3 per-solution LLM dedup-passes in parallel.** Issue one LLM call per solution. Each receives:

   - The solution context: id, title, description.
   - The 3 method-lists for THIS solution (18 raw entries total), each entry pre-tagged with its source method like `{text, source_method}` where `source_method` is one of `"storymap"`, `"pre-mortem"`, `"outcome-impact"`.
   - The dedup task: "Merge assumptions that express the same underlying belief in different words. Preserve the source method of each merged entry as an array (a 3-source merge means all three methods surfaced the same belief independently; a 1-source entry was unique to one method). Do not invent new assumptions. Do not drop assumptions that are genuinely distinct. Return only a JSON array of deduped objects with shape `{text: string, source_methods: [<one or more of 'storymap', 'pre-mortem', 'outcome-impact'>]}`. No other fields, no prose preamble."

   Collect 3 deduped lists. Verify each list:
   - Parses as JSON.
   - Length is in `6..18`.
   - Each entry has a `text` string and a `source_methods` array.
   - Each `source_methods` array has length 1-3 with values from `{storymap, pre-mortem, outcome-impact}` and no duplicates within the array.

   If any check fails, hard-exit per format.

11. **Assign deterministic ids and canonicalize.** For each surviving assumption in each per-solution list:

   - Set `id` = `asm-<solution_id>-<NNN>` with `NNN` zero-padded 3 digits, numbered 001..NNN in the dedup-pass output order.
   - Canonicalize `source_methods` array order to `["storymap", "pre-mortem", "outcome-impact"]` (filter out methods not present; order the remaining ones per this canonical sequence).

12. **Compose the v0.1 JSON.**

   Top-level fields:
   - `schema_version`: `"0.1"`.
   - `team`: carried from upstream top-three JSON.
   - `title`: `"Assumptions: <chosen_opportunity.id> - <first 5-10 words of chosen_opportunity.quote, trailing punctuation stripped>"`.
   - `product_outcome`: the verbatim outcome formulation.
   - `chosen_opportunity`: the object with `id`, `phase_id`, `quote`, `source` (carried from upstream).
   - `source_top_three_solutions`: relative path to the source top-three JSON from the repo root (e.g., `"workspace/fast/fsok/opportunities/sok-pa-karta/2026-05-11/top-three-solutions.json"`).
   - `source_experience_map`: basename of the source experience-map JSON.
   - `generation_summary`: the fixed v0.1 block:
     ```json
     {
       "methods": ["storymap", "pre-mortem", "outcome-impact"],
       "assumptions_per_method_per_solution": 6,
       "raw_total_before_dedup": 54,
       "solutions": 3
     }
     ```
   - `assumptions_per_solution`: array of 3 entries, ordered by upstream `picks[]` order. Each entry has:
     - `pick_position`: 1, 2, or 3 (matches the upstream picks array index + 1).
     - `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number`: carried byte-identical from the upstream picks entry.
     - `assumptions`: the deduped, id-assigned, canonicalized list for this solution.

13. **Validate invariants.** Before writing output, verify:

    - `assumptions_per_solution.length == 3`.
    - Each `solution_id` is in upstream `picks[].id`.
    - No duplicate `solution_id` across the 3 entries.
    - For each per-solution entry, `6 <= assumptions.length <= 18`.
    - Each `assumption.id` matches `^asm-sol-r[123]-(pm|ux|tl)-[1-9][0-9]*-\d{3}$`.
    - All `assumption.id` values unique across the entire output.
    - All carried fields byte-identical to upstream picks entry.

    If any invariant fails, hard-exit naming the specific invariant. Write no output.

14. **Write paired output.**

    - `<scope>/assumptions.json`
    - `<scope>/assumptions.md`

    Create `<scope>/` if it does not exist. Same root name on both files.

15. **Render the markdown deterministically from the JSON.** Use this exact template:

    ````markdown
    ---
    title: "Assumptions: <chosen_opportunity.id> - <first 5-10 words of quote>"
    date: <YYYY-MM-DD>
    purpose: Per-solution deduped assumption lists with source-method attribution. Paired with assumptions-<date>.json. Input to assist 10 (OST-assumption-categorizer); trio gate downstream at assist 11 (OST-riskiest-assumptions).
    tags: [assumption-generation, ost, schema-v0.1]

    ---

    # Assumptions: <chosen_opportunity.id>

    Source top 3 solutions: `<source_top_three_solutions>`
    Source chosen opportunity: `<scope>/../chosen-opportunity.md`
    Source product outcome: `<scope>/../../../_product-context/product-outcome.md`
    Source experience map: `<source_experience_map>`
    Schema version: 0.1
    Paired JSON: `assumptions-<YYYY-MM-DD>.json`

    Generation summary: 3 methods (storymap, pre-mortem, outcome-impact) x 3 solutions x 6 assumptions = 54 raw, then per-solution dedup with source-method attribution.

    ## Chosen opportunity

    **<chosen.id>** (Phase: <phase_id>) - "<quote>" - *<source>*

    ## Product outcome

    > <outcome formulation>

    ## Solution 1: <solution_title>

    **<solution_id>** [<role-abbrev>, R<round_number>]

    <solution_description>

    ### Assumptions (<count>)

    - **<asm-id>** [<methods-tag>] <text>
    - **<asm-id>** [<methods-tag>] <text>
    - ...

    ## Solution 2: <solution_title>

    (same shape)

    ## Solution 3: <solution_title>

    (same shape)
    ````

    **Rendering rules:**

    - Role abbreviation: `product-manager` -> `PM`, `ux-designer` -> `UX`, `tech-lead` -> `TL`. Render in the solution header line as `[<role-abbrev>, R<round_number>]`.
    - Method tag for assumptions: `storymap` -> `SM`, `pre-mortem` -> `PrM`, `outcome-impact` -> `OI`. `PrM` is chosen over `PM` to avoid collision with the product-manager role abbreviation.
    - Multi-source method tags: components combined alphabetically with `+` inside brackets. Examples: `[OI+SM]`, `[PrM+SM]`, `[OI+PrM+SM]`.
    - Chosen-opportunity source attribution carried verbatim. Separate the quote from the source with ` - ` (regular dash).
    - No em-dash anywhere. Use regular dashes only.
    - Frontmatter must have a blank line before the closing `---`.
    - No `Cites:` line. No `Trio HITL` banner.
    - Pick ordering in the markdown mirrors the upstream `picks[]` array order.
    - Output language for assumption text matches the upstream solution-description language (typically Swedish for this trio).

## Output principles

- The output is intermediate: it feeds assist 10 (categorizer) and assist 11 (OST-riskiest-assumptions). No in-skill HITL banner; the trio's review gate is at assist 11's output.
- Sub-agents are blind to each other. The three methods are designed to triangulate independently.
- The dedup-pass merges or keeps; never invents.
- Source-method attribution is data, not decoration. The array length is the triangulation signal.
- Per-solution structure only. No cross-solution `shared_with` marking.
- Stay assertive in assumption text ("users understand the new flow") rather than hedging ("users will likely understand"). Hedging is for risk-mapping (assist 11), not for assumption statement.
- No category vocabulary in assumption text (no "desirability", "usability", "feasibility", "viability", "risky"). That is assist 10/11 territory.
- No effort vocabulary in assumption text (no "complex", "expensive", "feasible", "quick win"). Carried from the Torres no-effort rule.

## Vad skill INTE gör

- Reads interview transcripts, OST-brainstorm-solutions output, comparison matrix, validated opportunities, OST-cluster-solutions output, or the clustered experience map.
- Reads role anchors (`role-product-manager.md` etc.). Role info is data only.
- Categorizes assumptions into desirability / usability / feasibility / viability / other. (Assist 10.)
- Scores, ranks, or flags assumptions as riskiest. (Assist 11.)
- Generates test cards, validation plans, or experiment designs. (Future phase 4.)
- Applies cross-solution dedup or marks shared assumptions across solutions.
- Modifies upstream files (ratifications.md, top-three JSON, chosen-opportunity.md, product-outcome.md, experience map).
- Writes outside the resolved scope. Output lives in `<scope>/`.
- Appends to `<scope>/../ratifications.md`. Ratification is the trio's manual step downstream.
- Adds an in-skill HITL banner. Trio gate is at assist 11.
- Runs a JSON self-validation pass. Trust the invariant check.
- Retries sub-agents on partial failures. Hard-exit; operator re-runs end-to-end.
- Uses a `category`, `risk_level`, `importance`, `evidence`, or `shared_with` schema field.
- Allows sub-agents to read each other's output.
- Allows the dedup-pass to invent new assumptions.
- Configures method set, count per method, solution count, or per-team overrides. (All locked at v1.)
- Pre-clusters, theme-tags, or pre-categorizes the output.
- Uses emoji or numeric encoding for method tags. Plain bracketed text only.
- Writes to Miro or any external surface. JSON + markdown only.
