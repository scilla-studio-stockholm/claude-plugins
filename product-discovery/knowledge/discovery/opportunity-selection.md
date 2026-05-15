---
title: Opportunity selection - schema and conventions
date: 2026-05-10
purpose: Owns the chosen-opportunity schema (v0.1), the locked three-step decision rule, the tie-handling convention, the evidence-gap-filter convention, and the no-effort reminder. Read at runtime by the OST-select-opportunity skill (assist 5); consumed by assist 6 (synthetic trio solution brainstormer).
tags: [discovery, ost, opportunity-selection, schema-v0.1, torres]

---

# Opportunity selection

The structured selection artifact between a comparison matrix and a trio's downstream solution work. Produced by `OST-select-opportunity` (assist 5) and consumed by assist 6 (synthetic trio solution brainstormer).

This anchor owns the schema, the decision rule, and the conventions. It corresponds to Torres "Continuous Discovery Habits" chapter 7 step 4 of the OST process ("Select one target opportunity").

## What the selector does

The selector reads a comparison matrix (5 criteria × N approved opportunities, qualitatively scored) and applies a locked three-step decision rule to propose one chosen opportunity. The output is a proposal: the trio reviews it, overrides if it disagrees, and ratifies the final pick into the opportunity folder's `chosen-opportunity.md` (which assist 6 reads).

The selector does not pick more than one opportunity. Even on tied picks it commits to one and names the tie inline so the trio sees the closeness.

## The decision rule

The selector applies these three steps in order:

**Step 1 (filter).** Deprioritize any opportunity scoring `weak` or `unknown` on `outcome-alignment`. The outcome is the trio's north star; an opportunity that doesn't move the outcome is not a candidate.

**Edge case:** if step 1 empties the candidate set (every approved opportunity scored `weak` or `unknown` on outcome-alignment), fall back to "best of the rest" using the highest outcome-alignment score available (e.g., if no `strong`/`medium` exists, include all `weak`s; if no `weak`s, include `unknown`s). The `rationale` must explicitly name the fallback ("No opportunity scored strong/medium on outcome-alignment; falling back to ...").

**Step 2 (rank).** Among the remaining candidates, pick the one with the strongest aggregate profile across the other four criteria. Use this ordering:

1. More `strong` is better.
2. Among equal `strong` counts, fewer `weak` is better.
3. Among equal `weak` counts, fewer `unknown` is better.

`n/a` is neutral (does not count as positive or negative).

**Step 3 (tiebreak).** If two or more opportunities tie under step 2, prefer the one with fewer `unknown` cells across all five criteria (including outcome-alignment). If still tied, prefer the one with the better outcome-alignment score (`strong` > `medium` > `weak` > `unknown`). If still tied, force a pick (any of the tied opps, AI's choice) and populate `decision_signals.tie_with[]` with the tied opp-ids.

The decision rule is fixed in v0.1. Configurable rules per trio is parked for v0.2.

## Tie handling

See Step 3 of the decision rule for the cascade (fewer unknowns, then better outcome-alignment, then force-pick) that resolves most ties before reaching the inline-naming behavior described here. Force a pick. Name the tied opp(s) explicitly in the `rationale` prose so the trio sees the closeness. Populate `decision_signals.tie_with[]` with the tied opp-ids.

No separate "tie note" or "coin-flip" header. Inline naming in the rationale is the trio's signal.

## The evidence-gap filter

The chosen opportunity may have one or more `unknown` cells in the matrix. The selector judges which of those gaps would affect phase-2 solution evaluation:

- **Carried** to phase 2: the gap describes evidence that would change which solutions are reasonable, how to prioritize them, or how to test them. Add to `evidence_gaps_carried[]` with a 1-sentence `why_relevant_to_phase_2`.
- **Excluded** from carry-forward: the gap is real but doesn't affect solution work (e.g., political/governance unknowns, market-size unknowns when the chosen opp is internal-only). Add to `evidence_gaps_excluded[]` with a 1-sentence `why_excluded`.

Both lists appear in the output for transparency. Their union (by `criterion_id`) equals the chosen opportunity's full `unknown`-cell set in the matrix. Their intersection is empty.

`n/a` cells are structural, not gaps; they appear in neither list.

The carry-forward is chosen-only. Gaps from non-chosen opportunities live in the matrix and are not pulled forward.

## The no-effort rule

Per Torres's principle ("Don't assess effort during opportunity selection") in `knowledge/discovery/opportunity-solution-tree-teresa-torres.md`, the matrix already enforced no-effort scoring. The selector inherits this discipline.

Do not introduce effort thinking in `rationale`, `reason_not_picked`, `why_relevant_to_phase_2`, or `why_excluded` prose. If the reasoning chain ever reaches "but it would be hard/easy to build / requires X integration / would scale poorly", remove that step. Effort is decided downstream in assumption testing (step 4 of the OST process), not here.

## Ratification format

The selector produces a proposal at `<scope>/chosen-opportunity-proposal.{json,md}`. The trio reviews the proposal, overrides if it disagrees, and ratifies the final pick into the opportunity folder. This file is the decision-of-record consumed by downstream phase-2 skills (the solution brainstormer at assist 6 and the top-3 selector at assist 8).

The ratified file mirrors the selector's proposal markdown structure, minus the alternatives section and the HITL banner. Required structure:

- YAML frontmatter (title, date, purpose, tags) with a blank line before the closing `---`.
- `## Product outcome` section, with the outcome formulation as a blockquote (carried verbatim from `<scope>/../../_product-context/product-outcome.md`).
- `## Chosen opportunity` section, with a single bold-id line of the form: `**<opp-id>** (Phase: <phase-id>) - "<quote>" - *<source>*`.
- `### Score profile` subsection with a 5-row markdown table (one row per criterion: outcome-alignment, customer-importance, market-size, strategic-fit, competitive-landscape) and a `Profile summary:` line.
- `### Rationale` subsection with prose explaining the pick. The trio may carry the selector's rationale as-is, edit it, or rewrite it.
- Optional `## Evidence gaps carried into phase 2` section with bullet entries (omitted entirely if there are none).

The trio's ratification action is concrete:

1. Create a new opportunity folder at `workspace/<team>/<product>/opportunities/<opp-slug>/` (slug from the chosen opportunity's title per `knowledge/discovery/workspace-scope.md`) and copy `<scope>/chosen-opportunity-proposal.md` into it as `chosen-opportunity.md`.
2. Delete the `> **Trio HITL:** ...` blockquote.
3. Delete the entire `## Alternatives considered` section and its bullet entries.
4. Edit the chosen opportunity / rationale / score profile if overriding the selector's pick (otherwise leave as-is).
5. Update the frontmatter `purpose:` line to reflect that this is the ratified decision-of-record (not a proposal).
6. Commit.

Downstream skills (`OST-brainstorm-solutions`, the future top-3 solution selector) read `chosen-opportunity.md` at the opportunity-folder root (`<scope>/../chosen-opportunity.md` from a discovery scope). They hard-exit if the file is missing or malformed.

This format is locked at the same v0.1 schema version as the selector's JSON output. Format changes require a schema bump and a coordinated update across the selector, the brainstormer, and the top-3 selector.

## JSON schema (v0.1)

This is the contract that `OST-select-opportunity` produces. Downstream consumers (assist 6) read it.

```json
{
  "schema_version": "0.1",
  "team": "string (carried from comparison matrix)",
  "title": "string (carried from comparison matrix)",
  "product_outcome": "string (carried from comparison matrix)",
  "source_comparison_matrix": "string (filename of source comparison-matrix.json in the portfolio round folder)",
  "chosen_opportunity": {
    "id": "string (e.g., 'opp-5-1'; matches an id in the matrix's opportunities_compared[])",
    "phase_id": "string (carried from comparison matrix)",
    "quote": "string (carried verbatim)",
    "source": "string (carried verbatim)"
  },
  "chosen_opportunity_scores": [
    {
      "criterion_id": "string (e.g., 'outcome-alignment')",
      "score": "strong | medium | weak | unknown | n/a"
    }
  ],
  "rationale": "string (2-4 sentences using the locked decision rule: outcome-alignment first, strongest-aggregate-profile rank, fewer-unknowns tiebreak; mentions opp-ids and criterion names; on tied picks, names the tied opp(s) explicitly)",
  "decision_signals": {
    "outcome_alignment_score_for_chosen": "strong | medium | weak | unknown | n/a",
    "profile_summary": "string (one-line tally, e.g., '4 strong, 0 medium, 0 weak, 0 unknown, 1 n/a')",
    "tie_with": ["string (opp-ids the chosen was tied with at any decision step; empty array if unambiguous)"]
  },
  "alternatives_considered": [
    {
      "id": "string (carried verbatim from matrix opportunities_compared[])",
      "phase_id": "string",
      "quote": "string (carried verbatim)",
      "source": "string (carried verbatim)",
      "reason_not_picked": "string (1-2 sentences anchored in matrix scores)"
    }
  ],
  "evidence_gaps_carried": [
    {
      "criterion_id": "string (carried from matrix evidence_gaps[])",
      "what_is_missing": "string (carried verbatim from matrix evidence_gaps[], or lightly rephrased)",
      "why_relevant_to_phase_2": "string (1 sentence on why this gap affects solution evaluation)"
    }
  ],
  "evidence_gaps_excluded": [
    {
      "criterion_id": "string",
      "what_is_missing": "string",
      "why_excluded": "string (1 sentence on why this gap doesn't affect solution work)"
    }
  ]
}
```

### Field notes

- **`chosen_opportunity`** is a singular object. We picked one; not forward-designing for multi-pick which we explicitly rejected.
- **`chosen_opportunity_scores[]`** is denormalized at the top level so assist 6 can read the chosen opp's profile without reloading the matrix. Always exactly five entries in v0.1, one per criterion ID from the matrix's `criteria[]`, in the matrix's declared order.
- **`decision_signals.tie_with[]`** is the structured signal for tied picks. Empty when the pick is unambiguous. The rationale prose still names the tie inline; this field is the parseable counterpart.
- **`alternatives_considered[]`** contains every other approved opportunity from the matrix (count = `|opportunities_compared| - 1`). Carries the same `id`, `phase_id`, `quote`, `source` fields as the chosen, plus a `reason_not_picked`. Self-contained.
- **`evidence_gaps_carried[]`** and **`evidence_gaps_excluded[]`** are a symmetric pair so the AI's filter judgement is auditable. Their union equals the chosen opp's `unknown`-cell set in the matrix; intersection is empty. `n/a` cells appear in neither.
- **No effort/feasibility field** anywhere in the schema. Structural enforcement of the no-effort rule.
- **Missing optional fields.** The skill omits any optional key whose value isn't set; never writes `null`. The exception is the three optional array fields in v0.1 (`decision_signals.tie_with[]`, `evidence_gaps_carried[]`, and `evidence_gaps_excluded[]`), which are always written as empty arrays when applicable, never `null` and never omitted.

## Open questions

- ~~Configurable decision rule per trio?~~ Not in v0.1. The three-step rule is hardcoded. Revisit in v0.2 if 2-3 trios consistently want different weighting.
- Multi-pick / shortlist mode: if trios consistently want a 2-3 opp shortlist instead of a single pick + alternatives, add a configurable HITL flavor. Currently parked.
- Selector self-doubt signaling beyond the tie note: if trios report that low-confidence non-tied picks land as too confident, add an explicit per-pick confidence signal (e.g., `decision_signals.confidence: "high" | "medium" | "low"`). Currently parked.
- Inherited evidence-overstatement from matrix rationales: the comparator's v2 follow-ups (commit `018e176`) flagged that matrix rationales can over-state cross-customer "independence" or pull from the cluster's `narrativ` extension surface as evidence. The selector inherits these rationales by reference; if selector outputs over-state evidence as a result, address as a v2 follow-up.

## Evolution

This document evolves as more trios run the selector. When a new pattern emerges that doesn't fit the current version, the schema bumps with a note in this section.

**v0.1 (2026-05-10):** Initial schema. Three-step decision rule (outcome-alignment filter, strongest-aggregate-profile rank, fewer-unknowns tiebreak), tie handling via inline rationale + `decision_signals.tie_with[]`, AI-judged evidence-gap carry-forward with symmetric `carried`/`excluded` lists, no-effort rule carried from Torres OST + `OST-compare-opportunities`. Designed to support `OST-select-opportunity` (assist 5 in `opportunity-solution-tree-agents.md`).
