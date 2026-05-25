---
name: OST-select-top-three-solutions
description: For product trios and researchers, when picking the top 3 solutions to carry into assumption testing from a divergent brainstorm output, output a paired JSON + markdown proposal with 3 specific solutions ranked by outcome-impact probability, each with an outcome-mapping rationale. Input to assist 9 (assumption generator).
---

# Select top three solutions

You help a product trio pick the 3 specific solutions with the strongest probability of moving the product outcome within the chosen opportunity. You read the divergent brainstorm output (18 specific solution candidates) and rank them by outcome-impact probability. The top 3 carry forward; each gets a 2-3 sentence rationale that names the causal path from the solution to the outcome. Output is paired JSON (per the top-three-selection schema v0.2) plus a markdown rendering generated deterministically from the JSON.

This skill is assist 8 in the OST discovery workflow.

The output is a **proposal** that assist 9 (assumption generator) consumes after trio ratification. The trio reviews the markdown output. If approved, `decided.solutions` in `decisions.json` is the ratified record. The trio may edit `decisions.json` to swap picks or adjust rationale. This skill does NOT write outside `<scope>/`.

**Out of scope:** clustering or grouping solutions (`OST-cluster-solutions` is a separate optional skill, not consumed here), generating assumptions per pick (assist 9), re-brainstorming (assist 6), reading interview transcripts or the comparison matrix (everything needed is in the brainstormer JSON + `decisions.json`), surfacing alternatives or runners-up as a structured field (trio reads brainstormer markdown directly), scoring or ranking numerically, weighing effort or feasibility (Torres principle, carried), applying mechanism diversification as a constraint.

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`. Discovery scope only.

2. **Load context via parent walk-up:**
   - `<scope>/decisions.json`
   - Same-round predecessor: `<scope>/solution-candidates.json` (with sibling-round fallback)

3. **Read the knowledge anchors:**
   - `references/top-three-selection.md` - the v0.2 schema, the four v2 locked decisions, the no-effort rule, the ratification-flag pattern, the field-notes section.
   - `references/solution-brainstorm.md` - the source schema (v0.1) so you can parse what `OST-brainstorm-solutions` produced.
   - `references/opportunity-solution-tree-teresa-torres.md` - Torres principles. The canonical anchor is "Choose three solutions to explore in parallel" (CDH ch 7 step 6). The "Don't assess effort during opportunity selection" rule is carried to solution selection prose.

4. **Locate inputs:**
   - Latest `solution-candidates.json` in `<scope>/` (with sibling-round fallback).
   - `<scope>/decisions.json` (parent walk-up).

5. **Hard-exit checks** (see Hard-exit format below). Do not write any output files when these fire:
   - Missing knowledge anchor `top-three-selection.md`, `solution-brainstorm.md`, or `opportunity-solution-tree-teresa-torres.md` (expected under `knowledge/discovery/`).
   - Zero files match `solution-candidates.json` in `<scope>/`.
   - `<scope>/decisions.json` missing.
   - `decisions.json` has no `decided.opportunity` key.
   - Source JSON does not parse.
   - Source JSON `schema_version` is not `"0.1"`.
   - Source `solutions[]` does not contain exactly 18 entries.
   - Chosen-opp id in source JSON does not match `decided.opportunity.id` in `decisions.json`.

6. **Parse inputs.**
   - Parse the source brainstormer JSON. Carry `team`, `product_outcome`, `chosen_opportunity` (full sub-object) verbatim. Index `solutions[]` by `id`. Confirm count == 18.
   - Read `<scope>/decisions.json`. Extract `decided.opportunity.id` and `decided.opportunity.quote` for grounding context.
   - Cross-check: source-JSON `chosen_opportunity.id` must equal `decided.opportunity.id` in `decisions.json`. Mismatch → hard-exit.
   - The `product_outcome` field in output is carried verbatim from source-JSON (which is the authoritative copy at brainstorm-time); `decisions.json` is used only as grounding context in the LLM prompt.

7. **Compose the picking prompt.** Build a single LLM prompt with these sections, in this order:

   **a. Role frame:**
   > You are picking the 3 specific solutions with the strongest probability of moving the product outcome within the chosen opportunity. Rank the 18 candidates by outcome-impact probability and return the top 3 as specific solutions (not clusters, not themes - the specific solution with its verbatim id, title, role, round, and description). Order picks from highest to lowest probability.

   **b. Grounding context:**
   > Chosen opportunity: `<chosen_opportunity.id>` (Phase: `<phase_id>`) - "`<quote>`" - *`<source>`*
   >
   > Product outcome: `<product_outcome verbatim>`

   **c. The 18 candidates** rendered as a flat list, one per line:
   ```
   - sol-r1-pm-1 [product-manager, R1] "Title here" - Description here.
   - sol-r1-pm-2 [product-manager, R1] "Title here" - Description here.
   ...
   ```

   **d. The four v2 locked decisions** (verbatim from `top-three-selection.md`):
   1. Pick unit: always specific member solution. No clusters, no theme-grouping. Each pick is one of the 18 with verbatim id, title, generating_role, round_number, description.
   2. Pick count: strict 3. Exactly 3 picks. No flexibility.
   3. Rationale prose: outcome-mapping only. 2-3 sentences. Name the causal path from this specific solution's mechanism to the product outcome's metric. No customer-evidence anchor required (the chosen-opp quote is in the file header for context, but the rationale doesn't need to repeat it). No cluster-context. No assumption-reasoning - stay assertive ("this moves the outcome by X"), not conditional ("this would move the outcome IF X").
   4. No alternatives section. The output schema has no `alternatives_considered[]`. Trio reads the brainstormer markdown directly if they want to see the other 15 specific solutions.

   **e. The no-effort rule:**
   > Do not use effort vocabulary in `rationale`. Forbidden words: complex, easy, simple, expensive, cheap, feasible, infeasible, scalable, quick win, low-hanging fruit, ambitious, risky-to-build, effort, implementation cost, build time. Torres principle: opportunity prioritization doesn't weigh effort, and we extend the rule to solution selection.

   **f. Pick ordering convention (soft):**
   > Present picks in descending outcome-impact probability (strongest first). The trio reads top-to-bottom and infers descending confidence.

   **g. Schema skeleton** (the v0.2 JSON shape from `top-three-selection.md`):
   ```json
   {
     "schema_version": "0.2",
     "team": "...",
     "title": "Top solutions: <first clause of chosen opportunity quote>",
     "product_outcome": "...",
     "chosen_opportunity": { "id": "...", "phase_id": "...", "quote": "...", "source": "..." },
     "source_solution_candidates": "<source filename>",
     "picks": [
       {
         "id": "sol-...",
         "title": "...",
         "generating_role": "...",
         "round_number": <int>,
         "description": "...",
         "rationale": "2-3 sentences; outcome-mapping only"
       }
     ],
     "extensions": {}
   }
   ```

   The picks array has exactly 3 entries. Each entry's `id`, `title`, `generating_role`, `round_number`, `description` are carried verbatim from the source brainstormer `solutions[]` entry with matching `id`. The `rationale` is your own composition.

   **h. Output instruction:**
   > Return only a single JSON object matching the schema. No prose preamble. No markdown code fences in the output.

8. **Make the LLM call.** Pass the composed prompt to the model. Receive the JSON response.

9. **Parse and validate the response.**
   - Parse JSON. Malformed JSON → hard-exit.
   - Validate invariants:
     - `picks.length == 3`.
     - Each `pick.id` exists in source `solutions[]`.
     - No duplicate pick ids.
     - For each pick: `title`, `generating_role`, `round_number`, `description` byte-identical to source entry with matching id.
     - `chosen_opportunity.{id, phase_id, quote, source}` byte-identical to source brainstormer JSON.
   - Invariant violation → hard-exit (see triggers) with the specific violation named.

10. **Set top-level `title`** to `"Top solutions: <first 5-10 words of chosen_opportunity.quote, trailing punctuation stripped>"`. Set `source_solution_candidates` to the basename of the source brainstormer JSON file (no directory prefix).

11. **Write JSON output** to `<scope>/top-three-solutions.json`. Create the directory if it doesn't exist.

12. **Render the markdown deterministically from the JSON** using the template in the "Markdown template" section below. Write to `<scope>/top-three-solutions.md`.

    Use today's date in `YYYY-MM-DD` format. The two files share the same root name. Upstream files (`solution-candidates.json`, `decisions.json`) are not modified after this step.

13. **Write to decisions.json:** Read `<scope>/decisions.json`. Set `decided.solutions`:

    ```json
    {
      "ratified": "<today YYYY-MM-DD>",
      "picks": [
        {
          "id": "<sol-id>",
          "title": "<title>",
          "description": "<description>",
          "rationale": "<rationale>"
        }
      ]
    }
    ```

    Exactly 3 picks. Do not include `generating_role` or `round_number`.

## Hard-exit format

When a hard-exit condition fires, respond with this exact pattern (substitute actual values) and stop. Do not write any output files.

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

The hard-exit triggers:

| Trigger | Looked for | Remedy |
|---|---|---|
| Missing knowledge anchor (`top-three-selection.md`, `solution-brainstorm.md`, or `opportunity-solution-tree-teresa-torres.md`) | The anchor file at the expected path under `knowledge/discovery/` | Restore from git, or re-run Task 1 of the OST-select-top-three-solutions v2 build |
| Zero `solution-candidates.json` in `<scope>/` | A source brainstormer file | Run `OST-brainstorm-solutions` |
| `<scope>/decisions.json` missing | Round-level `decisions.json` | Re-run `OST-init-workspace` to scaffold the file |
| `decisions.json` has no `decided.opportunity` key | `decided.opportunity` object in `decisions.json` | Run `OST-select-opportunity` to ratify the chosen opportunity |
| Source JSON does not parse | Schema-conformant v0.1 JSON | Re-run `OST-brainstorm-solutions` |
| Source JSON `schema_version` is not `"0.1"` | `"schema_version": "0.1"` | Re-run `OST-brainstorm-solutions` |
| Source `solutions[]` count is not 18 | Exactly 18 source candidates | Re-run `OST-brainstorm-solutions` (3 sub-agents × 3 rounds × 2 ideas = 18) |
| Chosen-opp id mismatch (source-JSON vs. `decided.opportunity.id`) | Same opp-id in both files | Inspect `decisions.json` and source brainstormer JSON; re-ratify or re-run the upstream |
| LLM output not valid JSON | A single JSON object | Re-run the skill; if persistent, inspect the prompt for ambiguity |
| Invariant: `picks.length != 3` | Exactly 3 picks | Re-run the skill; if persistent, tighten the prompt's pick-count rule |
| Invariant: pick id not in source `solutions[]` | All pick ids in source | Re-run the skill |
| Invariant: duplicate pick ids | Each pick id appears at most once | Re-run the skill |
| Invariant: carried member field not verbatim from source | `title`, `generating_role`, `round_number`, `description` byte-identical to source | Re-run the skill |
| Invariant: `chosen_opportunity` not verbatim from source | `chosen_opportunity.{id, phase_id, quote, source}` byte-identical | Re-run the skill |

## Markdown template

The markdown output is rendered deterministically from the composed JSON using this template:

```markdown
---
title: "Top solutions: <chosen_opportunity.id> - <first 5-10 words of chosen_opportunity.quote>"
date: <YYYY-MM-DD>
purpose: Selector proposal for OST step 6 (top solutions to explore in parallel). Paired with top-three-solutions-<date>.json. Trio reviews; decided.solutions in decisions.json is the ratified record. Input to assist 9 (assumption generator).
tags: [top-three-selection, ost, schema-v0.2]

---

# Top solutions: <chosen_opportunity.id>

Source solution candidates: `<source_solution_candidates>`
Source context: `<scope>/decisions.json`
Schema version: 0.2
Paired JSON: `top-three-solutions-<YYYY-MM-DD>.json`

> **Trio HITL:** This is the AI's proposal. Review the rationales, override if you disagree. When approved, `decided.solutions` in `decisions.json` is the ratified record. The trio may edit `decisions.json` directly to swap picks or adjust rationale.

## Chosen opportunity

**<chosen_opportunity.id>** (Phase: <phase_id>) - "<chosen_opportunity.quote>" - *<chosen_opportunity.source>*

## Product outcome

> <product_outcome>

## Picks (3)

### Pick 1: <picks[0].title>

**<picks[0].id>** [<role-abbrev>, R<picks[0].round_number>]

<picks[0].description>

*Rationale:* <picks[0].rationale>

### Pick 2: <picks[1].title>

**<picks[1].id>** [<role-abbrev>, R<picks[1].round_number>]

<picks[1].description>

*Rationale:* <picks[1].rationale>

### Pick 3: <picks[2].title>

**<picks[2].id>** [<role-abbrev>, R<picks[2].round_number>]

<picks[2].description>

*Rationale:* <picks[2].rationale>
```

**Role abbreviation mapping** (used in the markdown bullet, not in JSON):

- `product-manager` → `PM`
- `ux-designer` → `UX`
- `tech-lead` → `TL`

## Output principles

- **Picks are presented in confidence order** (strongest outcome-impact probability first). Soft convention in the prompt only; not enforced post-hoc.
- **Verbatim carry-over** of all member fields and chosen-opp fields from source.
- **Title field at top level is derived** from `chosen_opportunity.quote` first clause (5-10 words, trailing punctuation stripped).
- **Source attribution** carried verbatim from the chosen-opportunity record. Separated from the quote by ` - ` (regular dash).
- **No em-dash** anywhere, applied uniformly to Swedish and English prose.
- **Role abbreviations in markdown** map `product-manager` → `PM`, `ux-designer` → `UX`, `tech-lead` → `TL`. The JSON field `generating_role` keeps the full slug.
- **Output language for prose** (`rationale`) matches the source language detected in the chosen-opportunity quote and brainstormer descriptions.
- **Frontmatter on the markdown output** complies with the project rule (blank line before closing `---`).
- **HITL banner** rendered verbatim every run.
- **No `Cites:` line.** No alternatives section. No notes section.
- **No silent degradation.** Hard exit on the conditions in the Hard-exit format table; never write partial output.
- **No JSON self-validation pass after composition.** Trust the invariant check.
- **Upstream files are immutable.** Never modify `solution-candidates.json`. The skill writes the two `top-three-solutions.*` files under `<scope>/` and updates `decided.solutions` in `<scope>/decisions.json`.
- **Creating `ratifications.md` entries is no longer required.** `decided.solutions` in `decisions.json` is the ratified record.
- **Single pass.** No retries, no iteration.

## What this skill does NOT do

- **Read `OST-cluster-solutions` output.** v0.2 dropped the clusterer from the required pipeline. The trio may invoke OST-cluster-solutions separately for their own clustered review, but the picker doesn't consume it.
- **Cluster, group, or theme-categorize the 18 source solutions.**
- **Generate assumptions per pick.** Assist 9's job, via three parallel methods (storymap, pre-mortem, outcome-impact).
- **Surface alternatives, near-misses, or runners-up as a structured field.** Trio reads brainstormer markdown directly.
- **Pick more than 3 or fewer than 3.** Hard invariant.
- **Pick the same identity twice.** Hard invariant.
- **Filter, dedupe, or modify source solutions.** Read-only against input.
- **Re-brainstorm.** Upstream skill (assist 6).
- **Append to `ratifications.md`.** That pattern is retired; `decided.solutions` in `decisions.json` is the ratified record.
- **Read interview transcripts, comparison matrix, validated opportunities, experience map.** Everything needed is in the brainstormer JSON + `decisions.json`.
- **Score, matrix, or rank numerically before picking.** Single-pass qualitative judgement; ranking is internal to the LLM call and surfaces only as `picks[]` order.
- **Apply effort or feasibility weighing.** Torres principle, carried.
- **Apply mechanism diversification as a constraint.** Picker ranks by outcome-impact probability; if top 3 share a mechanism family, that's a coherent comparative bet.
- **Reason about assumptions or risks in the rationale.** Assist 9's territory. Rationale prose stays assertive about outcome-mapping.
- **Run a no-effort or no-assumption post-pass.** Eyeball-only at smoke test.
- **Ask the trio interactively.** Force a pick.
- **Sub-agent orchestration.** Single LLM call.
- **Iterate, retry, or run multiple passes.**
- **Write to Miro, Notion, or any external surface.** JSON + markdown only.
