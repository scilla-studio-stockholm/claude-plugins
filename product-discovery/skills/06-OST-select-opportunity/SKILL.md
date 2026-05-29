---
name: OST-select-opportunity
description: For product trios and researchers, when selecting one opportunity from an approved set already compared against a product outcome and Torres criteria, output a paired JSON + markdown proposal with the chosen opportunity, rationale, every other approved opportunity as an alternative considered, and an AI-judged subset of evidence gaps to carry into phase 2.
---

# Select opportunity

You help a product trio select one opportunity from an approved set already compared against a product outcome and Torres criteria, producing paired JSON (per the opportunity-selection schema v0.1) plus a markdown rendering. The output is a proposal: the chosen opportunity with rationale, every other approved opportunity as an alternative-considered with a reason not picked, the chosen opp's score profile, and an AI-judged subset of the chosen opportunity's evidence gaps to carry into phase 2.

This skill is assist 5 in the OST discovery workflow.

The selector applies a locked three-step decision rule:

1. **Filter** opportunities scoring `weak` or `unknown` on `outcome-alignment` (deprioritize).
2. **Rank** the remaining by strongest aggregate profile across the other four criteria.
3. **Tiebreak** on fewer evidence gaps.

The output is a **proposal**, not a decision-of-record. The trio reviews the proposal markdown. If approved, `decided.opportunity` in `decisions.json` is the ratified record. The trio may edit `decisions.json` directly to adjust scores or rationale before approving. Creating `chosen-opportunity.md` at the opportunity-folder root is optional (human reference only — downstream skills read from `decisions.json`).

**Out of scope:** transcript reading, citation validation (`OST-validate-opportunities` upstream), re-clustering (`OST-cluster-opportunities` upstream), re-comparing (`OST-compare-opportunities` upstream), summing scores, picking more than one opportunity, generating solutions (assist 6 onward), and weighing effort or feasibility (Torres principle).

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`. Opportunity-selection scope only.

2. **Load context via parent walk-up:**
   - `<scope>/../../_product-context/product-outcome.md`
   - Same-round predecessor: `<scope>/comparison-matrix.json`

3. **Read the knowledge anchors:**
   - `references/opportunity-selection.md` - the chosen-opportunity schema (v0.1), the three-step decision rule, the tie-handling convention, the evidence-gap-filter convention, the no-effort reminder.
   - `references/opportunity-comparison.md` - the matrix schema (v0.1), the criteria definitions, the score vocabulary.
   - `references/opportunity-solution-tree-teresa-torres.md` - Torres principles, especially "Don't assess effort during opportunity selection".

4. **Locate inputs:**
   - `<scope>/comparison-matrix.json` (same-round predecessor).
   - `<scope>/../../_product-context/product-outcome.md`.

5. **Hard-exit checks** (see Hard-exit format below). Do not write any output files when these fire:
   - `<scope>/comparison-matrix.json` not found.
   - `<scope>/../../_product-context/product-outcome.md` missing.
   - Matrix JSON does not parse.
   - Matrix JSON `schema_version` is not `"0.1"`.
   - Zero items in matrix `opportunities_compared[]`.
   - Product outcome file has no extractable `## Outcome` section.

6. **Parse inputs.**
   - Parse the matrix JSON. Index `opportunities_compared[]` by `id`. Build a per-opportunity score map from `cells[]` (key: `(criterion_id, opportunity_id)`, value: `score`).
   - Parse the product outcome from `<scope>/../../_product-context/product-outcome.md`. Extract the outcome formulation under the `## Outcome` heading. Carry the team name from `## Team`.

7. **Step 1 (filter).** Identify opportunities where `outcome-alignment` score is `weak` or `unknown`. These are deprioritized. The remaining set is the candidate pool.

   **Edge case:** if the candidate pool is empty (every approved opp scored `weak` or `unknown` on outcome-alignment), fall back to "best of the rest": include opportunities with the highest available outcome-alignment score (e.g., if no `strong`/`medium` exists, include all `weak`s; if no `weak`s, include `unknown`s). The `rationale` must explicitly name the fallback ("No opportunity scored strong/medium on outcome-alignment; falling back to ...").

8. **Step 2 (rank).** Among the candidate pool, score each opportunity's profile across the other four criteria: count `strong`, `medium`, `weak`, `unknown`. `n/a` is neutral (does not count as positive or negative). Pick the opportunity with the strongest profile by this ordering:

   1. More `strong` is better.
   2. Among equal `strong` counts, fewer `weak` is better.
   3. Among equal `weak` counts, fewer `unknown` is better.

9. **Step 3 (tiebreak).** If two or more opportunities tie under step 2, prefer the one with fewer `unknown` cells across all five criteria (including outcome-alignment). If still tied, prefer the one with the better outcome-alignment score (`strong` > `medium` > `weak` > `unknown`). If still tied, force a pick (any of the tied opps, AI's choice) and populate `decision_signals.tie_with[]` with the tied opp-ids. The rationale must name the tie inline.

10. **Compose `chosen_opportunity`, `chosen_opportunity_scores`, `decision_signals`.**
   - `chosen_opportunity`: carry `id`, `phase_id`, `quote`, `source` verbatim from the matrix.
   - `chosen_opportunity_scores`: one entry per criterion, with the score from the matrix's cells.
   - `decision_signals.outcome_alignment_score_for_chosen`: pulled from the matrix.
   - `decision_signals.profile_summary`: one-line tally (e.g., `"4 strong, 0 medium, 0 weak, 0 unknown, 1 n/a"`).
   - `decision_signals.tie_with`: opp-ids tied with the chosen at any decision step (empty array if unambiguous).

11. **Compose `rationale`.** 2-4 sentences explaining the pick using the locked decision rule. Mentions opp-ids and criterion names by their canonical English form. On tied picks, names the tied opp(s) explicitly. On the empty-candidate-set fallback, names the fallback explicitly. No effort vocabulary.

12. **Compose `alternatives_considered`.** One entry for every other opp in `opportunities_compared[]` (matrix - chosen). For each: carry `id`, `phase_id`, `quote`, `source`. Write a 1-2 sentence `reason_not_picked` anchored in matrix scores (e.g., "Profile is weaker than chosen on customer-importance and market-size") or in the decision-rule step that filtered it (e.g., "Deprioritized at step 1: scored weak on outcome-alignment"). No effort vocabulary.

13. **Compose `evidence_gaps_carried` and `evidence_gaps_excluded`.**
    - Walk matrix `evidence_gaps[]` for entries where `opportunity_id == chosen_opportunity.id`. Do NOT pull gaps from other opportunities; the carry-forward is chosen-only.
    - For each gap, judge whether it would affect phase-2 solution evaluation:
      - **Carried:** the gap describes evidence that would change which solutions are reasonable, how to prioritize them, or how to test them. Add to `evidence_gaps_carried[]` with a 1-sentence `why_relevant_to_phase_2`.
      - **Excluded:** the gap is real but doesn't affect solution work (e.g., political/governance unknowns, market-size unknowns when the chosen opp is internal-only). Add to `evidence_gaps_excluded[]` with a 1-sentence `why_excluded`.
    - The two lists together cover every chosen-opp `unknown` cell. `n/a` cells are not gaps and appear in neither list.

14. **Compose the v0.1 JSON.** All fields per the schema in `references/opportunity-selection.md`. Top-level scalar fields are carried, not invented:
    - `schema_version`: literal `"0.1"`.
    - `team`: carry from the comparison matrix's top-level `team` field.
    - `title`: carry from the comparison matrix's top-level `title` field. Do NOT derive from the chosen opportunity's quote.
    - `product_outcome`: carry from the comparison matrix's top-level `product_outcome` field.
    - `source_comparison_matrix`: filename of the matrix JSON resolved in Step 2 (e.g., `"comparison-matrix-2026-05-10.json"`).

    Per the missing-optional convention, omit any optional key whose value isn't set; never write `null`. `decision_signals.tie_with[]`, `evidence_gaps_carried[]`, and `evidence_gaps_excluded[]` are written as empty arrays when applicable, never as `null` and never omitted.

15. **Render the markdown deterministically from the JSON** using the template in the "Markdown template" section below.

16. **Write paired output** to:
    - `<scope>/chosen-opportunity-proposal.json`
    - `<scope>/chosen-opportunity-proposal.md`

    Upstream `comparison-matrix.json` and `product-outcome.md` are not modified. Create `<scope>/` if it doesn't exist. Do NOT write to any `chosen-opportunity.md` under `opportunities/` - that is the trio's ratification step.

17. **Write to decisions.json:** Read the round's `decisions.json`. Set `decided.opportunity` with these fields extracted from the proposal:

    ```json
    {
      "ratified": "<today YYYY-MM-DD>",
      "id": "<chosen_opportunity.id>",
      "phase_id": "<chosen_opportunity.phase_id>",
      "quote": "<chosen_opportunity.quote>",
      "source": "<chosen_opportunity.source>",
      "scores": {
        "outcome_alignment": "<score>",
        "customer_importance": "<score>",
        "market_size_frequency": "<score>",
        "strategic_fit": "<score>",
        "competitive_landscape": "<score>"
      },
      "rationale": "<rationale>",
      "evidence_gaps": [<evidence_gaps_carried items>]
    }
    ```

    Write the updated `decisions.json` back.

## Hard-exit format

When a hard-exit condition fires, respond with this exact pattern (substitute actual values) and stop. Do not write any output files.

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

The six hard-exit triggers:

| Trigger | Looked for | Remedy |
|---|---|---|
| `<scope>/comparison-matrix.json` not found | A comparison matrix at the resolved scope path | Run `OST-compare-opportunities` for this scope round |
| `<scope>/../../_product-context/product-outcome.md` missing | Trio's product outcome file via parent walk-up | Restore from git or re-author using the template structure in `_product-context/` |
| Matrix JSON does not parse | Schema-conformant v0.1 JSON | Re-run `OST-compare-opportunities` |
| Matrix JSON `schema_version` is not `"0.1"` | `"schema_version": "0.1"` | Re-run `OST-compare-opportunities` against the latest clustered map |
| Zero items in matrix `opportunities_compared[]` | At least one approved opportunity in the matrix | Re-run `OST-validate-opportunities` and review verdicts; the selector cannot select from an empty set |
| Product outcome file has no extractable `## Outcome` section | A heading `## Outcome` followed by the outcome formulation | Re-author `_product-context/product-outcome.md` using the template structure |

## Markdown template

The markdown output is rendered deterministically from the composed JSON using this template:

```markdown
---
title: Chosen opportunity - <title> (<team>)
date: <YYYY-MM-DD>
purpose: Selector proposal for OST opportunity selection, paired with chosen-opportunity-proposal.json. Trio reviews and ratifies into OST-discovery/<team>/<product>/opportunities/<opp-slug>/chosen-opportunity.md.
tags: [opportunity-selection, ost, schema-v0.1]

---

# Chosen opportunity: <title> (<team>)

Source comparison matrix: `comparison-matrix.json`
Source product outcome: `<scope>/../../_product-context/product-outcome.md`
Schema version: 0.1
Paired JSON: `chosen-opportunity-proposal.json`

> **Trio HITL:** This is the AI's proposal. Review the rationale and override if you disagree. If approved, `decided.opportunity` in `decisions.json` is the ratified record — you may edit it directly to adjust scores or rationale before approving. Creating `chosen-opportunity.md` in an opportunity folder is optional (human reference only — downstream skills read from `decisions.json`).

## Product outcome

> <full outcome formulation>

## Chosen opportunity

**<chosen.id>** (Phase: <phase name>) - "<chosen.quote>" - *<chosen.source>*

### Score profile

| Criterion               | Score   |
|-------------------------|---------|
| Outcome alignment       | <score> |
| Customer importance     | <score> |
| Market size / frequency | <score> |
| Strategic fit           | <score> |
| Competitive landscape   | <score> |

Profile summary: <decision_signals.profile_summary>.

### Rationale

<rationale prose, 2-4 sentences. Mentions opp-ids and criterion names; on tied picks, names the tied opp(s) explicitly so the trio sees the closeness.>

## Alternatives considered (<N>)

- **opp-X-Y** (Phase: <phase>) - "<quote>" - *<source>*
  Reason not picked: <1-2 sentences anchored in matrix scores>
- **opp-A-B** (Phase: <phase>) - "<quote>" - *<source>*
  Reason not picked: <...>

(repeat one entry per opp in alternatives_considered[])

## Evidence gaps carried into phase 2 (<N>)

(only if non-empty; otherwise omit this whole section)

These gaps from the chosen opportunity affect how phase-2 solutions are evaluated.

- **<criterion display name>**: <what_is_missing>
  *Why relevant: <why_relevant_to_phase_2>*

(repeat one entry per evidence_gaps_carried[])

## Evidence gaps not carried (<N>)

(only if non-empty; otherwise omit this whole section)

These gaps from the chosen opportunity were judged not to affect phase-2 solution work. Listed for transparency; trio may decide to investigate them anyway.

- **<criterion display name>**: <what_is_missing>
  *Why excluded: <why_excluded>*

(repeat one entry per evidence_gaps_excluded[])
```

## Output principles

- **Score values use full words** in the score-profile table and in any inline reference: `strong` / `medium` / `weak` / `unknown` / `n/a`. No emoji, no numeric encoding.
- **Source attribution** carried verbatim from the matrix JSON. Separated from the quote by ` - ` (regular dash, not em-dash).
- **No em-dash** anywhere, applied uniformly to Swedish and English prose.
- **Criterion display names stay in English** even when quotes and rationales are Swedish.
- **Output language for prose** (`rationale`, `reason_not_picked`, `why_relevant_to_phase_2`, `why_excluded`) matches the source language detected in the matrix's `quote` text and `phase` placement. Schema field names, JSON keys, criterion IDs, criterion display names, and score vocabulary stay as defined.
- **Frontmatter on the markdown output** complies with the project convention that every `.md` file has YAML frontmatter, with a blank line before the closing `---`.
- **Empty optional sections are omitted entirely.** "Evidence gaps carried into phase 2" and "Evidence gaps not carried" each omit when their underlying list is empty.
- **Tie callouts live inline in the rationale prose.** No separate "tie note" or "coin-flip" section.
- **No `Cites:` line** anywhere. The selector's rationale references opp-ids inline; there is no per-cell trace-back invariant.
- **Section order is fixed** and the AI does not insert ad-hoc sections.
- **The HITL banner** (`> **Trio HITL:** ...`) is rendered verbatim every run.
- **No silent degradation.** Hard exit on the conditions in the Hard-exit format table; never write partial output.
- **No JSON self-validation pass.** Trust the prompt; downstream skills surface any malformed JSON.
- **Upstream files are immutable.** Never modify `comparison-matrix-*.json` or `product-outcome.md`. The skill writes the two `chosen-opportunity-proposal.*` files and `decisions.json`.
- **Never write to any `chosen-opportunity.md` under `opportunities/`.** The skill writes only `chosen-opportunity-proposal.*` into `<scope>/` and updates `decided.opportunity` in `decisions.json`. Creating `chosen-opportunity.md` in an opportunity folder is the trio's optional manual step.
- **Single pass.** No retries, no iteration over the inputs.

## What this skill does NOT do

- **Read interview transcripts.** Quotes come from the comparison matrix.
- **Read the clustered experience-map JSON, validated table, or extracted opportunities.** All quotes, sources, scores, and rationales the selector needs are already in the matrix.
- **Re-validate, re-cluster, or re-compare.** Those are upstream skills.
- **Modify upstream files.** `comparison-matrix-*.json` and `product-outcome.md` stay immutable.
- **Write to `OST-discovery/<team>/<product>/opportunities/<opp-slug>/chosen-opportunity.md`.** That is the trio's optional manual step; downstream skills read from `decisions.json`.
- **Pick more than one opportunity.** HITL flavor is locked as picks-one + alternatives.
- **Produce a shortlist.** Even on tied picks, the AI commits to one and names the tie in the rationale.
- **Produce a free-form recommendation without alternatives.** Every other approved opportunity from the matrix appears in `alternatives_considered[]`.
- **Sum, average, or otherwise aggregate matrix scores into a numeric ranking.** Pattern-matching, not arithmetic.
- **Weigh effort, feasibility, integration cost, or implementation complexity.** Per Torres.
- **Generate solutions for the chosen opportunity.** Downstream (assist 6).
- **Re-introduce excluded opportunities** (verdict `needs_tweak` or `solution_in_disguise`) into the candidate set. The matrix already filtered them.
- **Iterate, retry, or run multiple passes.** One pass over the inputs, one pair of output files.
- **Run a JSON self-validation pass after composition.**
- **Write to Miro or any external surface.** JSON + markdown only.
- **Audit the matrix JSON for invariant violations** beyond what's needed to apply the decision rule. The selector trusts the comparator's output.
- **Ask the trio for a pick interactively.** If the matrix is genuinely ambiguous, force a pick and populate `decision_signals.tie_with[]`.
- **Carry evidence gaps from non-chosen opportunities.** The carry-forward is chosen-only.
- **Use a `Cites:` line in the markdown.** No per-cell trace-back invariant.
- **Use emoji or numeric encoding for scores or in tie callouts.** Words and prose only.
