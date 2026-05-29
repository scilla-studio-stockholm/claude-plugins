---
title: Top-three selection - schema and conventions
date: 2026-05-11
purpose: Owns the top-three-solutions schema (v0.2 current; v0.1 in Evolution), the four v2 locked decisions, the no-effort rule, and the ratification pattern. Read at runtime by the OST-select-top-three-solutions skill (assist 8); consumed by assist 9 (assumption generator).
tags: [discovery, ost, top-three-selection, schema-v0.2, torres]

---

# Top-three selection

The structured selection artifact between a divergent brainstorm and assumption decomposition. Produced by `OST-select-top-three-solutions` (assist 8) and consumed by assist 9 (assumption generator) after trio ratification.

This anchor owns the schema, the four v2 locked decisions, the no-effort rule, and the ratification pattern. It corresponds to Torres "Continuous Discovery Habits" chapter 7 step 6 ("Choose three solutions to explore in parallel").

## What the selector does

The selector reads the v0.1 solution-candidates JSON from `OST-brainstorm-solutions` (the 18 specific solutions) plus the trio-ratified chosen-opportunity and product-outcome context, then runs one LLM call to pick 3 specific solutions ranked by outcome-impact probability. Each pick is one of the 18 specific solutions (no clustering, no theme-grouping); each has a 2-3 sentence outcome-mapping rationale.

Output is a proposal that assist 9 consumes after trio ratification. The trio reviews the markdown, edits if needed, then the ratified top-3 is recorded in `<scope>/decisions.json` → `decided.solutions`. The selector itself does not write the ratified decision; it writes only its proposal.

The selector does NOT consume OST-cluster-solutions output. `OST-cluster-solutions` is a separate optional skill the trio may invoke for their own clustered review of the brainstorm; it is off the critical path as of v0.2.

## The four v2 locked decisions

These decisions are locked for v0.2 and the selector's prompt enforces them as rules.

1. **Pick unit: always specific member solution.** Each pick is one of the 18 specific solutions from the brainstormer (carries `id`, `title`, `generating_role`, `round_number`, `description`). No discriminator. No cluster-picks. v0.1's discriminator-variant schema collapsed to specific-only after smoke test showed cluster-bias in picker behavior.

2. **Pick count: strict 3.** Always exactly 3 picks (Torres canon). With 18 specific solutions, the top 3 by outcome-impact probability always exists. v0.1's flexible 2-4 was tied to cluster-collapsing scenarios that no longer apply.

3. **Rationale prose: outcome-mapping only.** 2-3 sentences per pick. Names the causal path from this specific solution to moving the product outcome's metric (e.g., "manuella steg" reduction, "antalet aktörer" reduction - depends on the trio's outcome formulation). No customer-evidence anchor required (the chosen-opp quote is in the file header). No cluster-context (no clusters). No assumption-reasoning (that's assist 9's job; rationale prose stays assertive - "this moves the outcome by X" not "this would move the outcome IF X").

4. **No alternatives section.** v0.2 omits `alternatives_considered[]` entirely. Trio reads the brainstormer markdown (`<scope>/solution-candidates.md`) directly to see the other 15 specific solutions if they want to override.

## The no-effort rule

Carried from `knowledge/discovery/opportunity-solution-tree-teresa-torres.md`. Torres' principle is "Don't assess effort during opportunity selection." We extend the rule to solution selection: the `rationale` prose must not introduce effort thinking. Eyeballed at smoke test, not invariant-enforced.

Forbidden vocabulary (eyeball list):

- `complex`, `easy`, `simple`, `expensive`, `cheap`
- `feasible`, `infeasible`, `scalable`
- `quick win`, `low-hanging fruit`, `ambitious`, `risky-to-build`
- `effort`, `implementation cost`, `build time`

## The ratification pattern

Trio ratification of the top-3 is recorded in `<scope>/decisions.json` → `decided.solutions` (schema in `knowledge/discovery/decisions-json-schema.md`). The block carries the date the trio signed off (`ratified`) plus exactly 3 `picks`, each with `id`, `title`, `description`, and `rationale`.

The selector itself does not write `decided.solutions`. It writes only its proposal (`top-three-solutions.json` + the `2-solutions.md` milestone). The trio reviews the proposal, edits if needed, and the ratified top-3 is committed to `decided.solutions`.

**Reading rule for assist 9** (and any future consumer): read `decided.solutions` from `<scope>/decisions.json`. Key presence signals the upstream gate is ratified; absence means it is not yet ready.

> **Historical note:** v0.1/v0.2 recorded ratifications in an append-only `ratifications.md` log at the opportunity-folder root. As of schema v1.0 that file is no longer written or read — `decisions.json` → `decided.solutions` is the single source of truth.

## JSON schema (v0.2)

This is the v0.2 contract that `OST-select-top-three-solutions` produces. Downstream consumer (assist 9) reads it.

```json
{
  "schema_version": "0.2",
  "team": "string (carried from source brainstormer JSON)",
  "title": "string (e.g., 'Top solutions: <first clause of chosen opportunity quote>')",
  "product_outcome": "string (carried)",
  "chosen_opportunity": {
    "id": "string (carried; e.g., 'opp-5-1'; matches decided.opportunity.id in <scope>/decisions.json)",
    "phase_id": "string (carried)",
    "quote": "string (carried verbatim)",
    "source": "string (carried verbatim)"
  },
  "source_solution_candidates": "string (filename of source solution-candidates.json in the active discovery round folder)",
  "picks": [
    {
      "id": "string (verbatim member id from source, e.g., 'sol-r1-pm-1')",
      "title": "string (verbatim from source)",
      "generating_role": "product-manager | ux-designer | tech-lead (verbatim)",
      "round_number": "integer (verbatim)",
      "description": "string (verbatim from source)",
      "rationale": "string (2-3 sentences; outcome-mapping only - names the causal path from this specific solution to moving the product outcome)"
    }
  ],
  "extensions": {}
}
```

### Field notes

- **`team`, `title` (top level), `product_outcome`** are carried from the source brainstormer JSON. Top-level `title` is rewritten to `"Top solutions: <first 5-10 words of chosen_opportunity.quote, trailing punctuation stripped>"` for downstream readability.
- **`chosen_opportunity`** is carried verbatim from the source brainstormer JSON. Cross-check against `decided.opportunity.id` in `<scope>/decisions.json` is mandatory.
- **`source_solution_candidates`** is the filename (no directory prefix) of the source brainstormer JSON (located at `<scope>/solution-candidates.json`).
- **`picks[]`** is exactly 3 entries. Order is descending outcome-impact probability (strongest first). Soft convention in prompt; not invariant-enforced post-hoc.
- **`picks[].{id, title, generating_role, round_number, description}`** are carried verbatim from the source brainstormer's `solutions[]` entry with matching `id`.
- **`picks[].rationale`** is 2-3 sentences. Names a causal path from the pick's mechanism to the product outcome's metric. No effort vocabulary, no assumption vocabulary, no customer-evidence anchor required.
- **`extensions`** is an empty object reserved for v0.3 fields.

### Schema invariants

The skill enforces these hard invariants on its output JSON. Violation results in a hard-exit with no partial writes.

- **`picks.length == 3`.** Exactly 3 picks. No flexibility.
- **Each `pick.id` is in source `solutions[]`.** No inventions, no typos.
- **No duplicate pick ids.** Every picked id appears exactly once.
- **Verbatim carry of member fields.** `picks[].{title, generating_role, round_number, description}` byte-identical to source.
- **Verbatim carry of chosen-opp fields.** `chosen_opportunity.{id, phase_id, quote, source}` byte-identical to source brainstormer JSON.
- **Chosen-opp consistency.** `chosen_opportunity.id` matches source JSON's `chosen_opportunity.id` AND `decided.opportunity.id` in `<scope>/decisions.json`.

### Missing optional fields convention

Optional keys: `extensions` content. When empty, write `"extensions": {}` (the object key is required at the schema level, but the contents may be empty). Never write `null`.

## Open questions

v0.3 candidates parked here:

- **Near-miss inline callout.** v0.2 says hedging is "only when warranted" but doesn't enforce a structural convention. If trios report wanting clearer signals about close calls, add an optional `near_miss_inline` field or a prompt convention for surfacing closeness.
- **Configurable pick count.** v0.2 locks 3. If trios consistently want 2 (assumption-budget concerns) or 4 (extra exploration), expose as configurable.
- **Optional cluster-context provenance.** If trios who invoke `OST-cluster-solutions` separately want the picker to label each pick with its cluster origin, add an optional `cluster_id_if_clustered` field. Only relevant if the trio runs OST-cluster-solutions out-of-band.
- **Effort-vocabulary blocklist post-pass.** Eyeball-only at smoke test. If creeping shows up, add forbidden-vocabulary regex or post-composition validation pass.
- **Assumption-vocabulary blocklist post-pass.** Same shape. If rationale prose starts naming assumptions ("this works IF Delfi API permits writes"), that's assist 9's territory. Promote to enforced if observed.
- **`OST-cluster-solutions` full retirement.** v0.2 leaves OST-cluster-solutions built but off-pipeline. Decide later whether to deprecate fully (delete the skill, document as obsolete) or keep as supported standalone tool.

## Evolution

**v0.1 (2026-05-11):** Initial schema. Eight locked decisions (either pick unit cluster/member, flexible 2-4 picks, no diversification constraint, three-ingredient rationale outcome-mapping+cluster-context+customer-evidence anchor, no assumption field, hedging tone, every-non-picked-cluster as alternative, ratification-flag pattern). Discriminator-variant schema with `cluster`/`member` exclusivity. Read OST-cluster-solutions output as input. Designed to support `OST-select-top-three-solutions` (assist 8). Built at commit `9693096`; the v0.1 design doc lives at commit `36a2826`.

**v0.2 (2026-05-11):** Architectural simplification after v0.1 smoke test surfaced three problems:

1. Cluster-bias in picker behavior (3-of-3 cluster-picks; discriminator hid a strong default).
2. "Explore in parallel" misread as mechanism-diversification (Torres principle is about comparative learning speed, not hedging across mechanisms).
3. Premature assumption-reasoning leaked into rationale prose (assist 9's domain).

v0.2 changes:

- Schema collapses discriminator to specific-member-only picks.
- Input switches from OST-cluster-solutions output to OST-brainstorm-solutions output direct.
- Pick count locks to strict 3 (Torres canon).
- Rationale ingredients collapse to outcome-mapping only (no cluster-context, no customer-evidence anchor).
- `alternatives_considered[]` removed entirely; trio reads brainstormer markdown to override.
- `pick_count` and `notes` fields removed (redundant with always-3 invariant).
- `OST-cluster-solutions` removed from required pipeline; stays available as standalone skill.

Pipeline shrinks from 13 to 12 required assists.
