---
title: Assumption categorization - schema and conventions
date: 2026-05-12
purpose: Owns the assumption-categorization schema (v0.1), the category enum (Cagan five product risks), the risk-falls tiebreaker rule, the 'other'-reservation rule, the carry-forward rules, the identity-mapping invariants, and the renderer template. Read at runtime by the OST-assumption-categorizer skill (assist 10); consumed by assist 11 (OST-riskiest-assumptions).
tags: [discovery, ost, assumption-categorization, schema-v0.1, cagan]

---

# Assumption categorization

The structured artifact between assumption generation and risk mapping. Produced by `OST-assumption-categorizer` (assist 10) and consumed by `OST-riskiest-assumptions` (assist 11).

This anchor owns the schema, the category enum, the risk-falls tiebreaker rule, the 'other'-reservation rule, the carry-forward rules, the identity-mapping invariants, and the renderer template. It applies Marty Cagan's five product risks (from `knowledge/foundations/product-operating-model-marty-cagan.md`) as the classification taxonomy, with the definitions in `knowledge/discovery/assumption-types.md`.

## What the categorizer does

The categorizer reads `assumptions.json` from `<scope>/` (the deduped per-solution assumption list with source-method attribution produced by assist 9) and runs a single LLM classification pass over the full flat list of all assumptions across the three solutions. Each assumption is tagged with exactly one category from the enum `{desirability, usability, feasibility, viability, other}` using the risk-falls tiebreaker rule.

Output is a paired JSON + markdown rendering with one `category` field added per assumption. Every other upstream field carries through byte-identical; the skill is an identity map plus one new field per item. The trio does NOT review this output directly; downstream the OST-riskiest-assumptions agent (assist 11) scores importance and evidence on the categorized list, and the trio's gate for phase 3 is at assist 11's output.

## The category enum

The five values map to Marty Cagan's five product risks plus an 'other' bucket for genuinely-orthogonal assumptions:

| Category | Risk if assumption is false |
|---|---|
| `desirability` | Users do not want the solution (the value proposition does not resonate). |
| `usability` | Users cannot figure out how to use the solution (the interaction does not work). |
| `feasibility` | The team cannot build the solution (technical, data, or integration constraint). |
| `viability` | The solution does not work for the business (margin, compliance, brand, scale, sustainability). |
| `other` | The assumption is outside Cagan's four product risks: legal, ethical, regulatory, market-timing, organizational. |

Full per-category definitions and worked examples live in `knowledge/discovery/assumption-types.md`. The categorizer reads that file at runtime as the authoritative taxonomy source.

## The risk-falls tiebreaker rule

Assumptions often touch more than one category at the surface (e.g., a step in the user flow is part-usability part-feasibility). The categorizer applies a single rule to break ties: **pick the category that describes the risk if the assumption turns out false.**

Worked examples:

- "Users will tolerate a 2-second loading state at step X." Surface: usability + viability. Risk if false: users abandon the flow -> desirability/usability concern, not viability (viability is about business model). Pick **usability**.
- "The Delfi API permits writes to the licens-table." Surface: feasibility only. Risk if false: the solution cannot be built. Pick **feasibility**.
- "Removing the manual approval step does not violate the procurement policy." Surface: viability + other. Risk if false: the company cannot ship the solution despite it being technically viable. Pick **viability** (it is a business-rule constraint that blocks operating, not an external legal/ethical issue).
- "GDPR allows the new data flow without explicit consent." Surface: other. Risk if false: regulatory enforcement. Pick **other** (genuinely outside Cagan's four).

The rule is mechanical, not opinion-based: it asks what kind of risk the assumption carries, and points to the category that owns that risk.

## The 'other'-reservation rule

**Force one of `{desirability, usability, feasibility, viability}` whenever an assumption fits even marginally.** 'Other' is reserved for assumptions that are genuinely orthogonal to Cagan's four product risks. Concretely, 'other' is the right category for:

- Legal: regulatory permission, license boundaries, contract terms.
- Ethical: harm to specific user groups, dual-use risk, consent.
- Regulatory: standards compliance, audit obligations, certification.
- Market-timing: external readiness, competitor moves, macro conditions.
- Organizational: cross-team dependencies, leadership commitment, hiring capacity.

If an assumption could reasonably fit `feasibility` (e.g., "we have the team capacity to ship in Q3"), it goes there, not in `other`. 'Other' is the narrow bucket, not the default fallback.

## Carry-forward rules

Every upstream field carries through byte-identical. The categorizer adds exactly one `category` field per assumption and nothing else. Specifically:

- Top-level: `team`, `title`, `product_outcome`, `chosen_opportunity.*`, `source_top_three_solutions`, `source_experience_map` carried verbatim.
- Per-solution: `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number` carried byte-identical.
- Per-assumption: `id`, `text`, `source_methods` carried byte-identical; `category` is added.

No re-ordering, no re-wording, no merging, no dropping, no enrichment beyond the `category` field.

## Identity-mapping invariants

The skill enforces these as hard-exit-on-violation, no partial writes:

- `assumptions_per_solution.length == 3`.
- For each per-solution entry, `assumptions.length` equals the corresponding upstream per-solution entry's `assumptions.length`.
- For each per-solution entry, the upstream `assumptions[]` ids appear in the output in the same order at each index.
- Every `assumption.category` is in `{desirability, usability, feasibility, viability, other}`; exactly one value; never null; never an array.
- Every upstream field is byte-identical to the source JSON.
- `categorization_summary.total_assumptions` equals the sum of `assumptions[].length` across the three solutions.
- `categorization_summary` is the fixed v0.1 block.

## No in-skill HITL

The skill does not produce a "proposal" requiring trio ratification. It writes intermediate artifacts that flow into the OST-riskiest-assumptions agent (assist 11). The trio's review and approval gate for phase 3 is at assist 11's output, not here.

This mirrors the pattern from `OST-generate-assumptions`: that skill also produces intermediate artifacts without an in-skill HITL banner; the phase-3 gate is downstream.

## JSON schema (v0.1)

This is the v0.1 contract that `OST-assumption-categorizer` produces. Downstream consumer (assist 11) reads it.

```json
{
  "schema_version": "0.1",
  "team": "string (carried byte-identical from upstream assumptions-*.json)",
  "title": "string (carried byte-identical)",
  "product_outcome": "string (carried byte-identical)",
  "chosen_opportunity": {
    "id": "string (carried byte-identical)",
    "phase_id": "string (carried byte-identical)",
    "quote": "string (carried byte-identical)",
    "source": "string (carried byte-identical)"
  },
  "source_assumptions": "string (filename of source assumptions-*.json)",
  "source_top_three_solutions": "string (carried byte-identical)",
  "source_experience_map": "string (carried byte-identical)",
  "categorization_summary": {
    "categories": ["desirability", "usability", "feasibility", "viability", "other"],
    "rule": "single-category per assumption, risk-falls tiebreaker",
    "total_assumptions": "integer (sum across all 3 solutions)"
  },
  "assumptions_per_solution": [
    {
      "pick_position": 1,
      "solution_id": "string (carried byte-identical)",
      "solution_title": "string (carried byte-identical)",
      "solution_description": "string (carried byte-identical)",
      "generating_role": "product-manager | ux-designer | tech-lead (carried byte-identical)",
      "round_number": "integer (carried byte-identical)",
      "assumptions": [
        {
          "id": "string (carried byte-identical, e.g., 'asm-sol-r1-pm-1-001')",
          "text": "string (carried byte-identical)",
          "source_methods": ["array carried byte-identical"],
          "category": "desirability | usability | feasibility | viability | other"
        }
      ]
    }
  ]
}
```

## Field notes

- `assumptions_per_solution[]` is a fixed-length-3 array, ordered by `pick_position` from the upstream.
- Every upstream field is carried byte-identical. The skill is an identity map on upstream data plus one new `category` field per assumption.
- `assumption.category` is exactly one value from the fixed enum. Never an array. Never null.
- `categorization_summary` is a fixed-shape sanity block. v0.1 values are locked.
- `categorization_summary.total_assumptions` is the only summary value that varies with input.
- Missing-optional convention: v0.1 has no optional fields. `null` is never written.

## Renderer template

The markdown is generated deterministically from the JSON via this template:

````markdown
---
title: "Categorized assumptions: <chosen_opportunity.id> - <first 5-10 words of quote>"
date: <YYYY-MM-DD>
purpose: Per-solution deduped assumption lists with Cagan-category tags. Paired with assumptions-categorized-<date>.json. Input to assist 11 (OST-riskiest-assumptions); trio gate downstream at assist 11.
tags: [assumption-categorization, ost, schema-v0.1]

---

# Categorized assumptions: <chosen_opportunity.id>

Source assumptions: `<source_assumptions>`
Source top 3 solutions: `<source_top_three_solutions>`
Source chosen opportunity: `<scope>/decisions.json` → `decided.opportunity`
Source product outcome: `<scope>/product-context/product-outcome.md`
Schema version: 0.1
Paired JSON: `assumptions-categorized-<YYYY-MM-DD>.json`

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

Rendering rules:

- Role abbreviation: `product-manager` -> `PM`, `ux-designer` -> `UX`, `tech-lead` -> `TL`.
- Method tag: `storymap` -> `SM`, `pre-mortem` -> `PrM`, `outcome-impact` -> `OI`. Multi-source combined alphabetically with `+`.
- Category tag: lowercase verbatim in brackets after the method tag: `[desirability]`, `[usability]`, `[feasibility]`, `[viability]`, `[other]`. No abbreviations.
- Tag order per row: `[<methods-tag>] [<category>]`, in that order.
- Row ordering within each solution preserves the upstream `assumptions[]` order. No re-sort by category or triangulation.
- No em-dash anywhere. Frontmatter has blank line before closing `---`.
- No `Cites:` line, no HITL banner.
- Pick ordering in the markdown mirrors the upstream `picks[]` array order.
- Output language for assumption text carries through from upstream verbatim (typically Swedish).

## Open questions (v0.2 candidates)

1. Per-category count sanity check (warn if >70% in one category or >20% in 'other').
2. Per-solution classification consistency check (similar text -> same category across solutions).
3. Optional `confidence` field for close-call classifications.
4. Optional `alt_categories` array for ambiguity-as-data.
5. Configurable category enum (Cagan-five locked at v1).
6. Explicit-filename input mode (latest-by-date is v1 default).
7. Schema evolution beyond v0.1.
8. Category-grouped rendering option (per-category headers within each solution).
9. Effort-vocabulary blocklist post-pass.
10. Risk-vocabulary blocklist post-pass.

## Evolution

| Version | Date | Change |
|---|---|---|
| v0.1 | 2026-05-12 | Initial schema. Single-pass classification against Cagan-five taxonomy. Identity-mapping over upstream assumptions; `category` is the only new per-assumption field. |
