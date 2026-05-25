---
title: Assumption generation - schema and conventions
date: 2026-05-11
purpose: Owns the assumptions schema (v0.1), the three-method definitions (storymap, pre-mortem, outcome-impact), the parallel-blind orchestration, the per-solution dedup-pass convention, the source-method attribution rule, and the count-per-pass rule. Read at runtime by the OST-generate-assumptions skill (assist 9); consumed by assist 10 (OST-assumption-categorizer).
tags: [discovery, ost, assumption-generation, schema-v0.1, torres]

---

# Assumption generation

The structured artifact between top-three selection and assumption categorization. Produced by `OST-generate-assumptions` (assist 9) and consumed by `OST-assumption-categorizer` (assist 10).

This anchor owns the schema, the three-method definitions, the parallel-blind orchestration, the dedup-pass convention, the source-method attribution rule, and the count-per-pass rule. It corresponds to Torres "Continuous Discovery Habits" chapter 8 ("Decompose into assumptions").

## What the generator does

The generator reads a trio-ratified `top-three-solutions.json` (the 3 specific solutions, located via the ratification-flag pattern in `<scope>/../ratifications.md`) plus the chosen-opportunity, the product outcome, and the latest extracted experience map.

> **Note:** As of schema v1.0, skill 10 reads `decisions.json` → `decided.solutions` directly. The `ratifications.md` lookup described above is deprecated.

It spawns 9 method-pass sub-agents in parallel via the Agent tool (3 methods x 3 solutions), then runs 3 per-solution LLM dedup-passes that merge similar assumptions across methods and tag each surviving entry with a `source_methods` array.

Output is a paired JSON + markdown rendering with one deduped assumption list per solution. The trio does NOT review this output directly; downstream the categorizer (assist 10) classifies each assumption into the 5-category taxonomy and the OST-riskiest-assumptions agent (assist 11) flags the most risky. The trio's gate for phase 3 is at assist 11's output.

## The three methods

The three methods are drawn from `plans/Session 3_ Opportunities, Solutions & Assumptions - Identifiera antaganden 60 min.jpg`. Each method surfaces assumptions through a different lens; together they triangulate the assumption space for one solution.

### Storymap method

Infer the user-flow for the solution (user types -> steps in time order). For each step, surface what must be true for that step to work for the user. Today's experience map is provided as anchoring context, but the sub-agent reasons about the FUTURE flow the solution implies, not today's flow.

Typical assumptions surfaced: "users understand step X", "the system has the data needed at step Y", "users will choose path A over path B at decision Z".

### Pre-mortem method

Imagine 6 months out: the solution shipped, then failed. Walk the failure modes one by one. For each failure mode, name the underlying assumption that turned out false.

Typical assumptions surfaced: failure-mode mirrors (e.g., "the integration is stable enough to run unattended", "the policy change does not trigger churn", "the team's capacity holds through the rollout").

### Outcome-impact method

State why this solution would move the product outcome. For each reason in that argument, name the underlying assumption that must hold for the reason to be valid.

Typical assumptions surfaced: causal-chain mirrors (e.g., "removing this manual step shifts the bottleneck rather than reproducing it elsewhere", "the outcome metric is sensitive to changes at this point in the flow").

## Per-method count rule

Each method sub-agent produces exactly 6 assumptions per solution. Locked at v0.1. The 6 figure balances "wide enough to surface non-obvious assumptions" against "narrow enough to avoid brus that the dedup-pass then has to filter".

Total raw: 6 x 3 methods x 3 solutions = 54. After per-solution dedup approximately 10-14 per solution = approximately 30-42 deduped total.

Configurable counts are a v0.2 follow-up.

## The parallel-blind orchestration

All 9 sub-agents fire in one Agent tool-use block. Within that block, no sub-agent sees another sub-agent's output. This is intentional: methods are designed to triangulate independently. If a sub-agent saw a sibling's output, the triangulation collapses (the second sub-agent would converge toward the first).

The orchestrator collects all 9 responses, then runs the dedup-pass.

## The dedup-pass convention

After the 9 sub-agent calls return, the orchestrator runs three LLM dedup-passes, one per solution. Each pass receives:

- The solution context (id, title, description).
- The 3 method-lists for that solution (18 raw entries), each entry pre-tagged with its source method.

The dedup-pass merges assumptions that express the same underlying belief in different words. Output entries carry a `source_methods` array of length 1-3 with values from `{storymap, pre-mortem, outcome-impact}`. Array length is the triangulation signal: a 3-source entry was surfaced by all three methods independently.

**Hard rule for the dedup-pass:** must not invent new assumptions. It merges or keeps; never adds.

**Hard count rule for the dedup-pass output:** `6 <= count <= 18`. Floor 6 prevents catastrophic over-merging (collapsing distinct assumptions into one); ceiling 18 prevents zero-merging (which means the dedup-pass did no work).

## Definition of "assumption"

An assumption is something the trio takes for granted but does not know to be true; if the assumption is false, the solution will not deliver its intended impact.

The 5-category taxonomy (desirability, usability, feasibility, viability, other) in `knowledge/discovery/assumption-types.md` is NOT applied at this generation step. That is assist 10's (categorizer's) job. Assumptions at this layer are stated as beliefs, not as members of a category.

## No in-skill HITL

The skill does not produce a "proposal" requiring trio ratification. It writes intermediate artifacts that flow into the categorizer (assist 10) and then to the OST-riskiest-assumptions agent (assist 11). The trio's review and approval gate for phase 3 is at assist 11's output, not here.

This mirrors the pattern from `OST-brainstorm-solutions`: that skill also produces intermediate divergent output without an in-skill HITL banner; the trio's gate is downstream at the selector (assist 8).

## JSON schema (v0.1)

This is the v0.1 contract that `OST-generate-assumptions` produces. Downstream consumer (assist 10) reads it.

```json
{
  "schema_version": "0.1",
  "team": "string (carried from upstream top-three JSON)",
  "title": "string (e.g., 'Assumptions: <chosen_opportunity.id> - <first 5-10 words of quote>')",
  "product_outcome": "string (carried)",
  "chosen_opportunity": {
    "id": "string (carried; matches the bold-id row in <scope>/../chosen-opportunity.md)",
    "phase_id": "string (carried)",
    "quote": "string (carried verbatim)",
    "source": "string (carried verbatim)"
  },
  "source_top_three_solutions": "string (filename of source top-three-solutions-*.json)",
  "source_experience_map": "string (filename of source experience-map-extracted-*.json)",
  "generation_summary": {
    "methods": ["storymap", "pre-mortem", "outcome-impact"],
    "assumptions_per_method_per_solution": 6,
    "raw_total_before_dedup": 54,
    "solutions": 3
  },
  "assumptions_per_solution": [
    {
      "pick_position": 1,
      "solution_id": "string (verbatim from upstream, e.g., 'sol-r1-pm-1')",
      "solution_title": "string (verbatim)",
      "solution_description": "string (verbatim)",
      "generating_role": "product-manager | ux-designer | tech-lead (verbatim)",
      "round_number": "integer (verbatim)",
      "assumptions": [
        {
          "id": "string (deterministic, e.g., 'asm-sol-r1-pm-1-001')",
          "text": "string (1-2 sentences)",
          "source_methods": ["storymap" | "pre-mortem" | "outcome-impact"]
        }
      ]
    }
  ]
}
```

## Field notes

- `assumptions_per_solution[]` is a fixed-length-3 array, ordered by `pick_position` from the upstream `picks[]` order (which mirrors the selector's confidence ordering).
- `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number` are carried byte-identical from the upstream top-three JSON. No re-interpretation.
- `assumptions[].id` is deterministic: `asm-<solution_id>-<NNN>` where `NNN` is zero-padded 001..NNN within a solution.
- `assumptions[].source_methods` is an array of length 1-3. Values from the fixed enum. Order canonicalized to `["storymap", "pre-mortem", "outcome-impact"]`.
- `assumptions[].text` is 1-2 sentences in the language of the upstream solution descriptions (typically Swedish for this trio).
- `generation_summary` is a fixed-shape sanity block. v0.1 values are locked.
- Missing-optional convention: v0.1 has no optional fields. `null` is never written.

## Invariants

The skill enforces these as hard-exit-on-violation, no partial writes:

- `assumptions_per_solution.length == 3`.
- Each `assumptions_per_solution[].solution_id` is in upstream `top-three-solutions.picks[].id`. No inventions.
- No duplicate `solution_id` across the 3 entries.
- For each per-solution entry, `6 <= assumptions.length <= 18`.
- Each `assumption.id` matches `^asm-sol-r[123]-(pm|ux|tl)-[1-9][0-9]*-\d{3}$`.
- `assumption.id` values are unique across the entire output.
- `assumption.source_methods.length` is in `{1, 2, 3}`.
- `assumption.source_methods` values are a subset of `{storymap, pre-mortem, outcome-impact}`; no duplicates within an array.
- `chosen_opportunity.id` matches upstream JSON AND the bold-id row in `<scope>/../chosen-opportunity.md`.
- All carried fields (`solution_title`, `solution_description`, `generating_role`, `round_number`) byte-identical to upstream.
- `generation_summary` is the fixed v0.1 block.

## Open questions (v0.2 candidates)

1. Configurable count per method-pass (v1 locks 6).
2. Configurable method set (v1 fixes storymap, pre-mortem, outcome-impact).
3. Configurable solution count (v1 fixes 3; mirrors selector).
4. Cross-solution `shared_with` marking (deliberately deferred).
5. Per-team experience-map source override.
6. Dedup-pass quality bar.
7. Effort-vocabulary blocklist post-pass.
8. Category-vocabulary blocklist post-pass.
9. Method-grouped rendering option (separate sections per method).
10. Optional `category` pre-tag from sub-agents (couples with assist 10).
11. Storymap experience-map over-anchoring (drop the input if drift observed).

## Evolution

| Version | Date | Change |
|---|---|---|
| v0.1 | 2026-05-11 | Initial schema. 9 method-pass sub-agents + 3 per-solution dedup-passes. source_methods as array. Per-solution structure only (no cross-solution marking). |
