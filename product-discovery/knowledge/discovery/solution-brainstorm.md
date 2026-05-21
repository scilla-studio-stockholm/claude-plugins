---
title: Solution brainstorm - schema and conventions
date: 2026-05-10
purpose: Owns the solution-candidates schema (v0.1), the three-round structure, the role-diversification framing, the prompt-only anti-duplication convention, and the broad-solution-scope definition. Read at runtime by the OST-brainstorm-solutions skill (assist 6); consumed by the solution-clusterer (assist 7).
tags: [discovery, ost, solution-brainstorm, schema-v0.1, torres]

---

# Solution brainstorm

The structured brainstorm artifact between a trio-ratified chosen opportunity and a downstream solution-clusterer. Produced by `OST-brainstorm-solutions` (assist 6) and consumed by assist 7 (solution clusterer).

This anchor owns the schema, the three-round structure, the role-diversification framing, the anti-duplication convention, and the broad-solution-scope definition. It corresponds loosely to Torres "Continuous Discovery Habits" chapter 8 ("Solutions") and the OST principle "explore multiple solutions for one opportunity".

## What the brainstormer does

The brainstormer reads a trio-ratified chosen opportunity and a product outcome, then spawns three role sub-agents (Product Manager, UX Designer, Tech Lead) in parallel for each of three rounds. Each sub-agent produces 2 solution candidates per round, totaling 18. The output is a divergent candidate set: clustering, scoring, and selection happen downstream.

The brainstormer does not curate, rank, or pre-cluster the 18 candidates. The trio's HITL gate for phase 2 is at the top-3 selector (assist 8), not in this skill.

## The three-round structure

Iterative-brainstorm research shows that the most obvious ideas come first. Round 1 captures these. Rounds 2 and 3 force divergence past the obvious by making each sub-agent see the prior pool with a "no paraphrases" rule.

- **Round 1:** Each sub-agent sees the chosen opportunity, the outcome, and its own role anchor. It produces 2 ideas from its frame. Three sub-agents in parallel: 6 ideas.
- **Round 2:** Each sub-agent sees the 6 round-1 ideas as a "do not duplicate" pool, plus the same context as round 1. It produces 2 more ideas. 6 more ideas.
- **Round 3:** Same as round 2 but the pool is 12. 6 more ideas. Total: 18.

Three rounds is enough divergence. More rounds risk diminishing returns; fewer rounds capture only the intuitive.

## Role diversification

The three roles in a product trio (Product Manager, UX Designer, Tech Lead) are the structural diversity unit of the team. Using them as generation anchors maps that diversity into the candidate set. Each role's anchor file describes the role's lens; the orchestrator includes the role anchor verbatim in each role-specific sub-agent's prompt.

Within a round, the three sub-agents are blind to each other. This is deliberate: if they saw each other's ideas mid-round, the late-running ones would gravitate toward the early-running ones, defeating diversification.

Across rounds, sub-agents see all roles' prior output. Cross-role build-on is the design intent for rounds 2 and 3.

## The anti-duplication rule

Anti-duplication is prompt-only. The round-2 and round-3 prompts include this rule verbatim:

> Each idea must be either NEW (different core mechanism / target / surface from any prior idea in the pool) OR an explicit build-on of a specific prior idea (cite the prior idea by id or title in your description, e.g., "Builds on sol-r1-pm-2 by ..."). Paraphrases or rewordings of prior ideas are not allowed.

Sub-agents self-classify their ideas as new or build-on in the description prose. The schema does not have a `build_on` field; structural enforcement would be inconsistent with the prompt-only philosophy.

The downstream solution-clusterer (assist 7) is the dedup layer. If the brainstormer's anti-dup rule produces a clean enough set, the clusterer's job is grouping by theme; if it produces some near-duplicates, the clusterer collapses them. Doing dedup in the brainstormer would duplicate work and introduce a second judgment surface where one is enough.

## Definition of "solution"

A solution is anything a product trio could ship or change that plausibly moves the product outcome on the chosen opportunity. This includes:

- User-facing features (new capabilities, redesigned flows, removed surfaces)
- Process redesigns (changes to who does what, in what order, with what handoff)
- Policy changes (changes to rules, defaults, guardrails)
- Integration changes (connecting systems, removing manual transcription)
- Automation (replacing a manual step with code)
- Internal tooling (changes that affect the team but not the user)
- Removed steps (eliminating a check, approval, or workflow node)
- Org-level changes (team boundaries, ownership shifts)

Each role's anchor steers the role's framing (PM toward outcome moves, UX toward experience moves, Tech Lead toward system moves), but no role is restricted to a single surface. A strong PM hypothesis can be "remove this step from the process", not a feature; a strong Tech Lead idea can be "change the policy default", not a script.

## Pure-divergent output

The brainstormer's output is 18 raw candidates. There is no AI curation, no "top picks", no theme-tagging, no pre-clustering. The trio's HITL gate is at assist 8 (top-3 selector), after the clusterer (assist 7) has done its work.

This is a deliberate separation of concerns: generation and clustering are different problems and benefit from different prompts. Combining them in one skill would either weaken generation (the clustering prompt would constrain divergence) or weaken clustering (the generation prompt's biases would carry into clusters).

## JSON schema (v0.1)

This is the contract that `OST-brainstorm-solutions` produces. Downstream consumers (assist 7) read it.

```json
{
  "schema_version": "0.1",
  "team": "string (carried from product-outcome.md ## Team)",
  "title": "string (carried from chosen-opportunity.md frontmatter title)",
  "product_outcome": "string (carried from product-outcome.md ## Outcome)",
  "chosen_opportunity": {
    "id": "string (carried from chosen-opportunity.md ## Chosen opportunity)",
    "phase_id": "string",
    "quote": "string",
    "source": "string"
  },
  "source_chosen_opportunity_file": "string (repo-root-relative resolved path of the ratified chosen-opportunity, e.g. workspace/fast/fsok/opportunities/brist-pa-oversikt/chosen-opportunity.md; resolved from <scope>/../chosen-opportunity.md at runtime)",
  "generation_summary": {
    "rounds": 3,
    "roles": ["product-manager", "ux-designer", "tech-lead"],
    "ideas_per_role_per_round": 2,
    "total_solutions": 18
  },
  "solutions": [
    {
      "id": "string (deterministic, e.g., 'sol-r1-pm-3' = round 1, PM, idea 3)",
      "round_number": 1,
      "generating_role": "product-manager | ux-designer | tech-lead",
      "title": "string (short, 5-12 words)",
      "description": "string (1-3 sentences; build-on entries name the prior idea by id or title inline)"
    }
  ]
}
```

### Field notes

- **`chosen_opportunity`** is denormalized at the top level so assist 7 can read the chosen opp without reloading the opportunity-folder root (`<scope>/../`).
- **`generation_summary`** is a fixed-shape sanity block. v0.1 always reads `{rounds: 3, roles: [...], ideas_per_role_per_round: 2, total_solutions: 18}`. Configurable counts is a v0.2 follow-up.
- **`solutions[]`** is one flat array of 18 entries, not nested by round/role. Round and role are properties of each entry. Trivial to group/filter in either dimension.
- **`solutions[].id`** is deterministic: `sol-r<round>-<role-prefix>-<index>` where role-prefix is `pm` (product-manager) / `ux` (ux-designer) / `tl` (tech-lead) and index is 1..2 within (round, role). Predictable, sortable, easy to cite in build-on prose.
- **No `build_on` schema field.** Anti-duplication is prompt-only; build-on linkage in round 2/3 lives in the `description` prose.
- **No `assumptions` or `risk_level` field.** Those live in assists 9-12.

### Schema invariants

- `solutions[]` length is exactly 18.
- For each `(round_number, generating_role)` pair, exactly 2 entries.
- `solutions[].id` values are unique.
- `solutions[].id` matches the regex `^sol-r[123]-(pm|ux|tl)-[12]$`.
- `solutions[].round_number` ∈ {1, 2, 3}.
- `solutions[].generating_role` ∈ {`product-manager`, `ux-designer`, `tech-lead`}.
- `chosen_opportunity.id` matches the id parsed from `<scope>/../chosen-opportunity.md` (the ratified chosen-opportunity at the opportunity-folder root).
- `generation_summary` is the fixed v0.1 block.
- No `build_on`, `assumptions`, `risk_level`, or other extension fields anywhere.

## Open questions

- Configurable idea / round / role counts: v0.1 locks 3×3×2=18. v0.2 if trios consistently want different sizing.
- Per-team role-anchor overrides: v0.1 reads generic anchors from `knowledge/foundations/`. v0.2 may let trios shadow defaults from the opportunity-folder root (e.g., `<scope>/../role-*.md`).
- Configurable role set: v0.1 fixes PM/UX/Tech Lead. v0.2 if teams have different trios (e.g., engineering manager + designer + researcher).
- Optional `build_on` schema field for structural cross-round linkage: parked. Add if the clusterer benefits.
- HITL flavor variants (curated top-N, themed-prep): parked. Add if trios push back on pure-divergent.

## Evolution

This document evolves as more trios run the brainstormer. When a new pattern emerges that doesn't fit the current version, the schema bumps with a note in this section.

**v0.1 (2026-05-10, revised 2026-05-11):** Initial schema. Three rounds × three roles × two ideas per role per round = 18 solutions. Role-diversified parallel sub-agents within rounds, cross-round full-pool anti-duplication via prompt-only "new or build-on, no paraphrases" rule. Broad solution scope. Pure-divergent output (no AI curation, no pre-clustering). Designed to support `OST-brainstorm-solutions` (assist 6 in `opportunity-solution-tree-agents.md`).

Revision note (2026-05-11): per-round count dropped from 5 to 2 (total 45 → 18). Joni's call: pure-divergent set is enough at 18 to give OST-cluster-solutions + select-top-three useful spread without the long-tail noise of 5/round/role. Same three-round structure preserved; round 3 pool size shifts from 30 to 12, anti-duplication rule unchanged.
