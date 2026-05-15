---
title: Solution cluster - schema and conventions
date: 2026-05-11
purpose: Owns the clustered-solutions schema (v0.1), the four locked clustering decisions, the clustering-axis convention, the chosen-opportunity cross-check rule, and the field-notes section. Read at runtime by the OST-cluster-solutions skill (assist 7); consumed by assist 8 (top-3 selector).
tags: [discovery, ost, solution-cluster, schema-v0.1, torres]

---

# Solution cluster

The structured clustering artifact between a divergent brainstorm and a top-3 selection. Produced by `OST-cluster-solutions` (assist 7) and consumed by assist 8 (top-3 selector).

This anchor owns the schema, the four locked decisions, and the clustering-axis convention. It corresponds to Torres "Continuous Discovery Habits" chapter 9 preparatory step "Identify hidden assumptions" - you group candidate solutions before identifying assumptions per representative idea.

## What the clusterer does

The clusterer reads 18 paired-JSON solution candidates (3 sub-agents × 3 rounds × 2 ideas) plus the trio-ratified chosen-opportunity and product-outcome context, then runs one LLM call to group the 18 candidates into 3-5 thematic clusters. Each cluster has a 3-7 word title, a 2-4 sentence summary, and a full embed of its member solutions. Output is a proposal that assist 8 consumes; the trio reviews assist 8's top-3 proposal, not this intermediate cluster map.

## The four locked decisions

These decisions are locked for v0.1 and the clusterer's prompt enforces them as rules.

1. **Cluster count target 3-5, material-driven.** The skill targets 3-5 clusters; if the 18 candidates genuinely split into 2 or 6-7 themes, the skill allows it and populates the top-level `notes` field naming the reason. The target bounds output for assist 8 while letting real structure drive shape.

2. **Full member embed.** Each cluster's `members[]` carries the full source record per member: `id`, `title`, `generating_role`, `round_number`, `description`. Cluster file is self-contained; assist 8 needs no join against the source candidates file.

3. **No `build_on` field in v0.1.** Sol-r2-pm-2's build-on prose (e.g., in Swedish output: "Bygger på sol-r1-pm-5") stays in the description verbatim. No structural `build_on` field on member objects. Reverses to a v0.2 candidate if assist 8 reports needing structured chains. Preserves the brainstormer's prompt-only anti-duplication decision.

4. **Single-member clusters allowed.** A genuinely unique solution gets its own cluster of one member. No separate `cluster-0-outliers` bucket. The asymmetry of the brainstormer's `fas-0-unphased` (where phases are pre-given) does not apply: clusters are discovered from data, not measured against a fixed taxonomy.

## The clustering-axis convention

The prompt says "group by theme/similarity"; the LLM picks dimensions that the material carries. No fixed primary axis.

Dimensions that recur across solution sets (informational, not prescriptive):

- **Mechanism** - API integration, UI flow, process/policy change, instrumentation, removed step.
- **Target user** - end customer, internal operator, integrator, automation.
- **System surface** - product-internal, external system (third-party API, payment provider, etc.), data layer, both.
- **Intervention type** - add new capability, remove existing friction, redesign existing flow, measure-before-act.

The LLM may use one of these dimensions, combine several, or invent a fitting one. The clusterer's job is to find the dimensions the material expresses, not to apply a checklist.

## The chosen-opportunity cross-check rule

The source candidates JSON carries a top-level `chosen_opportunity.id` (set by the brainstormer at build time). `<scope>/../chosen-opportunity.md` carries the trio-ratified chosen opportunity, with the id in a bold-id row (e.g., `**opp-5-1** (Phase: fas-5) - "..." - *...*`).

The clusterer parses both and compares. Mismatch → hard-exit. This catches a mismatch downstream of the brainstormer; the same check should also be added to `OST-brainstorm-solutions` to fail earlier (separate TODO item).

## JSON schema (v0.1)

This is the contract that `OST-cluster-solutions` produces. Downstream consumers (assist 8) read it.

```json
{
  "schema_version": "0.1",
  "team": "string (carried from source candidates JSON)",
  "title": "string (e.g., 'Clustered solutions: <first clause of chosen opportunity quote>')",
  "product_outcome": "string (carried from source)",
  "chosen_opportunity": {
    "id": "string (carried; e.g., 'opp-5-1'; matches the bold-id row in <scope>/../chosen-opportunity.md)",
    "phase_id": "string (carried)",
    "quote": "string (carried verbatim)",
    "source": "string (carried verbatim)"
  },
  "source_solution_candidates": "string (filename of source solution-candidates-*.json)",
  "cluster_count": "integer (3-5 target; may fall outside when material requires - see notes field)",
  "clusters": [
    {
      "cluster_id": "string (c1, c2, ...; sequential after post-sort)",
      "title": "string (3-7 words; theme name)",
      "summary": "string (2-4 sentences; what unifies the members and what mechanism/surface/intervention type the cluster represents)",
      "members": [
        {
          "id": "string (carried verbatim; e.g., 'sol-r1-pm-1')",
          "title": "string (carried verbatim)",
          "generating_role": "product-manager | ux-designer | tech-lead (carried verbatim from source)",
          "round_number": "integer (1, 2, or 3)",
          "description": "string (carried verbatim)"
        }
      ]
    }
  ],
  "notes": "string (optional; only present when something non-standard happened, e.g., 'cluster count fell to 2 because the 18 candidates split cleanly into 2 themes')",
  "extensions": {}
}
```

### Field notes

- **`team`, `title` (top level), `product_outcome`** are carried verbatim from the source candidates JSON, except `title` is rewritten to the form `"Clustered solutions: <first clause of chosen opportunity quote>"` for downstream readability.
- **`chosen_opportunity`** is carried verbatim from the source candidates JSON. Cross-check against the bold-id row in `<scope>/../chosen-opportunity.md` is mandatory (see The chosen-opportunity cross-check rule above).
- **`source_solution_candidates`** is the filename (no directory prefix) of the source JSON. The clusterer found it under `<scope>/` (the active discovery round folder).
- **`cluster_count`** equals `clusters.length`. Hard invariant.
- **`clusters[]`** is ordered by member count descending; ties broken by first-appearing member id. `cluster_id` values are assigned post-sort as `c1, c2, ...`.
- **`clusters[].title`** is 3-7 words, theme name; no period at the end.
- **`clusters[].summary`** is 2-4 sentences. Names what unifies the members and what mechanism/surface/intervention the cluster represents.
- **`clusters[].members[]`** is the full embed; carries `id`, `title`, `generating_role`, `round_number`, `description` verbatim from source. Soft member-ordering convention: lead-idea first (the member whose description most centrally expresses the cluster theme), then by round ascending, then by role. Not a hard invariant - LLM choice is preserved verbatim.
- **`notes`** is optional. Omit the key entirely when nothing non-standard happened; never write `null`. Only present when cluster_count falls outside 3-5 or another structural anomaly occurred.
- **`extensions`** is an empty object reserved for v0.2 fields.

### Schema invariants

The skill enforces these hard invariants on its output JSON. Violation results in a hard-exit with no partial writes.

- **Total member count == 18.** Sum of `members[]` across all clusters equals exactly 18 (every source candidate appears in exactly one cluster).
- **Every member id matches a source candidate id verbatim.** No inventions, no paraphrases, no typos.
- **No duplicate member id across clusters.** Every source id appears in exactly one cluster's members list.
- **`cluster_count` equals `clusters.length`.** The top-level integer matches the array length.
- **Cluster ordering is member-count descending.** Ties broken by first-appearing member id. `cluster_id` values `c1, c2, ...` are assigned post-sort.

### Missing optional fields convention

When an optional field's value isn't set, the skill omits the key from the JSON entirely rather than writing `null`. Downstream skills treat key absence as the missing-value signal. Optional fields in v0.1: `notes`.

## Open questions

- **Parse `build_on` from description prose.** Deferred from the brainstorming Q3 (decided 2026-05-11). If assist 8 reports needing structured chain data, add a member-level `build_on: ["sol-r1-pm-5"]` field populated by regex against description prose, cross-checked against member ids. Captures the brainstormer's prose anti-duplication signal as structural data without changing the brainstormer.
- **Cluster-axis disclosure.** Optional `cluster_axis_summary` field that names what dimensions the LLM used (e.g., "mechanism (API vs. UI vs. process) + intervention type (add vs. remove)"). Helps trio sanity-check the clustering logic. Currently parked.
- **Weak-fit flag on members.** Optional `fit_confidence: strong | weak` on member objects, for solutions the LLM placed but with low confidence. Surfaces ambiguity for trio review without forcing single-member clusters. Currently parked.
- **Configurable target range.** v1 locks 3-5 (calibrated for 18-candidate input from OST-brainstorm-solutions). If trios find 2-4 or 4-6 fits better for specific material profiles, expose as config in the anchor.
- **Re-cluster on disagreement.** If trio review surfaces "this cluster should split", let the skill take a subset of members + a split instruction and produce a re-clustered output. Avoids full re-runs.
- **Cluster ordering by outcome-relevance.** v1 orders by member count. Could order by LLM-judged outcome-impact if assist 8 finds that more useful (but likely assist 8's job).
- **Cluster rationale field.** A short *why* per cluster (why these members go together, beyond the `summary`). Likely subsumed by assist 8's downstream rationale.

## Evolution

This document evolves as more trios run the clusterer. When a new pattern emerges that doesn't fit the current version, the schema bumps with a note in this section.

**v0.1 (2026-05-11):** Initial schema. Four locked decisions (target 3-5 clusters material-driven, full member embed, no build_on field, single-member clusters allowed), free-form clustering axis, chosen-opportunity cross-check rule, single-pass single-LLM-call architecture. Designed to support `OST-cluster-solutions` (assist 7 in `opportunity-solution-tree-agents.md`).

Revision note (2026-05-11): cluster-count target recalibrated from 5-9 to 3-5 after OST-brainstorm-solutions per-round count dropped from 5 to 2 (input pool 45 → 18). Same density (avg 3.6-6 ideas per cluster). All other locked decisions unchanged.
