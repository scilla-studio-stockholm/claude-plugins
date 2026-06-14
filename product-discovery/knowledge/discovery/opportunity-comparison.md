---
title: Opportunity comparison - schema and conventions
date: 2026-05-09
purpose: Owns the comparison-matrix schema (v0.1) and its conventions. Read at runtime by the OST-compare-opportunities skill (assist 4); consumed by the selector skill (assist 5).
tags: [discovery, ost, opportunity-comparison, schema-v0.1, torres]

---

# Opportunity comparison

The structured comparison artifact between a clustered set of approved opportunities and a trio's product outcome. Produced by `OST-compare-opportunities` (assist 4) and consumed by the selector (assist 5).

This anchor owns the schema, criteria definitions, and conventions. It corresponds to Torres "Continuous Discovery Habits" chapter 7 ("Prioritizing Opportunities, Not Solutions").

## What the comparator does

For each approved opportunity in the cluster, the comparator scores five criteria (rows in a matrix), grounding each cell's rationale in opportunity quotes from the cluster. Cells where evidence is thin score `unknown` and feed an evidence-gap list; cells where the criterion structurally doesn't apply score `n/a`.

The matrix is for compare-and-contrast reasoning, not for ranking by a sum. Scores are non-numeric specifically to prevent summing.

## The five criteria

Four criteria derive from Torres's prioritization principles in CDH ch 7: `customer-importance`, `market-size`, `competitive-landscape`, and `strategic-fit` (Torres's "alignment with vision", renamed for trio readability). One criterion is comparator-specific: `outcome-alignment`.

| ID | Display name | What the criterion asks |
|---|---|---|
| `outcome-alignment` | Outcome alignment | Does solving this opportunity move the trio's product outcome? How directly would the opportunity's pain, when relieved, shift the outcome's metric or behavior? |
| `customer-importance` | Customer importance | How strongly do the customers in the cluster feel this pain? Intensity, recurrence, and cross-customer signal in the source quotes. |
| `market-size` | Market size / frequency | How many customers experience this pain, and how often? Frequency multiplies importance: a moderately painful experience that happens daily can outweigh a sharp pain that happens once a year. |
| `strategic-fit` | Strategic fit | Does solving this opportunity align with the team's vision and the product's positioning? Fit with the team's domain, the product's core promise, and the trio's stated direction. |
| `competitive-landscape` | Competitive landscape | Does solving this opportunity differentiate against alternatives the customer could choose? For internal products with no external competition this often scores `n/a`. |

The criteria list is fixed in v0.1. Configurable criteria per trio is parked for v0.2.

## Score vocabulary

| Value | Semantics |
|---|---|
| `strong` | Evidence in the cluster directly supports a high score on this criterion. Multiple `opp_refs` may reinforce; a single `opp_ref` with a clear quote is sufficient. |
| `medium` | Evidence supports the criterion partially or with caveats. A reasoned chain from quote to score is fine if it remains within the cluster's evidence. |
| `weak` | Evidence in the cluster suggests the opportunity scores low on this criterion, but the opportunity is still a real candidate (otherwise `OST-validate-opportunities` would have flagged it). |
| `unknown` | Evidence is genuinely thin and an honest non-`unknown` score is not defensible. The cell goes on the evidence-gap list with a one-sentence `what_is_missing`. |
| `n/a` | The criterion structurally doesn't apply to the trio's context (e.g., "market size" for an internal tool with a fixed user base, "competitive landscape" for an internal tool with no external competitors). Different from `unknown`: not an evidence gap. |

The vocabulary is non-numeric on purpose. Numeric scoring invites summing, which collapses Torres-style nuance.

## The trace-back rule

For scores `strong` / `medium` / `weak`, the rationale must reference at least one `opp-id` from `opportunities_compared[]`. The rationale's structure conveys the "grounded vs reasoned" signal: a `strong` / `medium` / `weak` rationale without an `opp-id` reference is structurally invalid.

If the AI cannot honestly cite an `opp-id`, score `unknown` and the cell goes on the gap list with a `what_is_missing` sentence.

`unknown` and `n/a` cells skip the trace-back rule.

`opp_refs[]` only references IDs in `opportunities_compared[]`. Excluded opportunities (`needs_tweak`, `solution_in_disguise`) are filtered before scoring and cannot be cited.

## The no-effort rule

Per Torres's principle ("Don't assess effort during opportunity selection") in `knowledge/discovery/opportunity-solution-tree-teresa-torres.md`, score every cell as if implementation were free.

Do not consider build complexity, cost, scalability, integration risk, or any feasibility dimension when grounding a score. If your reasoning chain ever reaches "but it would be hard/easy to build", remove that step and re-score on the criterion's dimension only. Effort is decided downstream in assumption testing (step 4 of the OST process), not here.

## JSON schema (v0.1)

This is the contract that `OST-compare-opportunities` produces. Downstream skills (assist 5, the selector) consume it.

```json
{
  "schema_version": "0.1",
  "team": "string (carried from clustered map)",
  "title": "string (carried from clustered map)",
  "product_outcome": "string (full outcome from <scope>/product-context/product-outcome.md)",
  "source_clustered_map": "string (filename of source experience-map-clustered-*.json)",
  "journey_phases": [
    {
      "id": "string (phase id, e.g. 'fas-5'; snapshot from clustered map phases[] in upstream order)",
      "name": "string (phase display name, carried verbatim from the clustered map)"
    }
  ],
  "criteria": [
    {
      "id": "string (e.g., 'outcome-alignment')",
      "name": "string (display name, e.g., 'Outcome alignment')",
      "description": "string (what the criterion asks)"
    }
  ],
  "opportunities_compared": [
    {
      "id": "string (carried verbatim from cluster JSON, e.g., 'opp-4-1')",
      "phase_id": "string (carried)",
      "quote": "string (carried)",
      "source": "string (carried)",
      "summary_title": "string (AI-generated 3-6 word noun phrase naming the pain; source language of the quote)",
      "score_counts": { "strong": 0, "medium": 0, "weak": 0, "unknown": 0, "na": 0 }
    }
  ],
  "opportunities_excluded": [
    {
      "id": "string",
      "phase_id": "string",
      "verdict": "needs_tweak | solution_in_disguise",
      "reason": "string (one-line note, e.g., 'verdict needs_tweak: vag deskriptor')"
    }
  ],
  "cells": [
    {
      "criterion_id": "string",
      "opportunity_id": "string",
      "score": "strong | medium | weak | unknown | n/a",
      "rationale": "string (1-2 sentences)",
      "opp_refs": ["string (opportunity IDs cited in the rationale; non-empty for strong/medium/weak; empty for unknown and n/a)"]
    }
  ],
  "evidence_gaps": [
    {
      "criterion_id": "string",
      "opportunity_id": "string",
      "what_is_missing": "string (one sentence describing what evidence would unlock a score)"
    }
  ]
}
```

### Field notes

- **`journey_phases[]`** is snapshotted from the clustered map's `phases[]` in upstream array order, `{ id, name }` verbatim, including phases with zero approved opportunities. Always non-empty (any valid clustered map has ≥1 phase). The OST Viewer's Prioritise lens builds its phase columns from this; without it the swim-grid renders zero columns and silently drops every opportunity (the viewer carries a fallback that re-derives phases from the clustered map, but the producer must emit this field).
- **`summary_title`** (per `opportunities_compared[]` entry) is an AI-generated 3-6 word noun phrase naming the underlying pain, in the source language of the `quote`. Cached across re-runs. The viewer falls back to the opportunity `id` when absent.
- **`score_counts`** (per `opportunities_compared[]` entry) is the integer tally `{ strong, medium, weak, unknown, na }` over that opportunity's five cells. Deterministically derivable from `cells[]`; emitted so the viewer can sort/filter cards without recomputing.
- **`criteria[]`** is denormalized into the JSON output (full definitions, not just IDs). Self-documenting; the selector doesn't need to load this anchor to interpret the matrix.
- **`opportunities_compared[]`** carries `id`, `phase_id`, `quote`, `source` verbatim from the cluster JSON. The comparator does not modify quotes or sources.
- **`opportunities_excluded[]`** captures the verdict-filter step's output. Empty array if no opportunities were excluded.
- **`cells[]`** is flat (one entry per criterion × opportunity), not 2D-nested. Easier to validate and write; renderer groups by `criterion_id` on output.
- **`opp_refs[]`** is the structural enforcement of the trace-back rule. Schema invariant: if `score ∈ {strong, medium, weak}` then `opp_refs[]` is non-empty; if `score ∈ {unknown, n/a}` then `opp_refs[]` is empty.
- **`evidence_gaps[]`** is technically derivable from `cells[]` (any cell with `score: "unknown"`), but written explicitly so the AI can add a `what_is_missing` sentence per gap. `n/a` cells do not appear here.
- **No effort/feasibility field** anywhere in the schema. Structural enforcement of the no-effort rule.
- **Missing optional fields.** The skill omits any optional key whose value isn't set; never writes `null`. For v0.1, all cell-level fields are required; the only optional document-level fields are `opportunities_excluded[]` and `evidence_gaps[]` (written as empty arrays when applicable, never `null`).

## Open questions

- ~~Configurable criteria per trio?~~ Not in v0.1. The five Torres-derived criteria are hardcoded. Revisit in v0.2 if 2-3 trios consistently want to swap, drop, or extend criteria for their context.
- Effort-creep self-policing: if trios catch the comparator weighing effort despite the no-effort rule, add either a forbidden-vocabulary blocklist or a post-composition validation pass. Currently parked.
- Pairwise comparison output: the selector (assist 5) reads this matrix and picks. If it needs explicit pairwise rankings (opp-A vs opp-B on each criterion) rather than per-cell scores, that's a comparator-output extension or a selector-internal computation. Decide during selector design.

## Evolution

This document evolves as more trios run the comparator. When a new pattern emerges that doesn't fit the current version, the schema bumps with a note in this section.

**v0.1 (2026-05-09):** Initial schema. Five hardcoded Torres-derived criteria (outcome-alignment, customer-importance, market-size, strategic-fit, competitive-landscape), qualitative score vocabulary (`strong` / `medium` / `weak` / `unknown` / `n/a`), trace-back rule via `opp_refs[]`, evidence_gaps[] derived from unknown cells. Designed to support `OST-compare-opportunities` (assist 4 in `opportunity-solution-tree-agents.md`).
