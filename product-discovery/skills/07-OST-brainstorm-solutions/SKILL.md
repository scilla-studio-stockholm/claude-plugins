---
name: OST-brainstorm-solutions
description: For product trios and researchers, when generating a divergent set of solution candidates for one chosen opportunity, output 18 paired JSON + markdown solution candidates produced by three role-diversified sub-agents (PM, UX, Tech Lead) over three rounds with cross-round anti-duplication.
---

# Brainstorm solutions

You help a product trio generate a divergent set of 18 solution candidates for one chosen opportunity. You spawn three role-diversified sub-agents (Product Manager, UX Designer, Tech Lead) in parallel for each of three rounds. Within a round the three sub-agents are blind to each other; across rounds they see the full prior pool with an explicit "new or build-on, no paraphrases" rule. The output is paired JSON (per the solution-brainstorm schema v0.1) plus a markdown rendering. Clustering, scoring, and selection happen downstream.

This skill is assist 6 in the OST discovery workflow.

The output is a **divergent candidate set**, not a recommendation. There is no curation, no top-picks highlighting, no theme-tagging. The trio's HITL gate for phase 2 is at the top-3 selector (assist 8), after the clusterer (assist 7).

**Out of scope:** clustering or grouping solutions (assist 7), scoring or ranking solutions (assist 8), generating assumptions or risk maps (assists 9-12), reading interview transcripts, comparison matrix, or experience map (everything needed is in the scope context files), modifying upstream files, weighing effort or feasibility (Torres principle).

## Steps

1. **Resolve scope.** Follow the scope-resolution protocol in `references/workspace-scope.md`. The resolved scope is a discovery scope of the form `OST-discovery/<team>/<product>/opportunities/<opp>/<YYYY-MM-DD>/`. Hard-exit if the resolved scope contains `/opportunity-selection/` (this skill runs in phase B only).

2. **Load context from the round folder.** Per `references/workspace-scope.md`:
   - `<scope>/decisions.json` — the ratified opportunity context (`decided.opportunity`) and product outcome (`product_outcome`)

3. **Read the knowledge anchors:**
   - `references/solution-brainstorm.md` - the schema (v0.1), the three-round structure, the role-diversification framing, the anti-duplication rule, the broad-solution-scope definition.
   - `references/tech-product-trio-responsibility-split.md` - cross-role framing baseline.
   - `references/product-trio-operational-practices.md` - cross-role framing baseline.
   - `references/opportunity-solution-tree-teresa-torres.md` - Torres principle "explore multiple solutions for one opportunity".

4. **Locate inputs:**
   - `<scope>/decisions.json`
   - `references/role-product-manager.md`
   - `references/role-ux-designer.md`
   - `references/role-tech-lead.md`

5. **Hard-exit checks** (see Hard-exit format below). Do not write any output files when these fire:
   - `<scope>/decisions.json` missing.
   - `decided.opportunity` key absent from `decisions.json`.
   - Any of the three role anchors missing.

6. **Extract chosen-opportunity context from `decisions.json`.**
   - Read `decided.opportunity.id`, `decided.opportunity.phase_id`, `decided.opportunity.quote`, `decided.opportunity.source` directly from the structured JSON — no parsing needed.
   - Read `decided.opportunity.scores` for score profile context (used to frame the sub-agent prompt; not carried into the output schema).
   - Read `decided.opportunity.rationale` for rationale prose (used to frame the sub-agent prompt; not carried into the output schema).

7. **Extract product outcome and team from `decisions.json`.**
   - Read `product_outcome` for the outcome formulation.
   - Read top-level `team` for the team slug.

8. **Read the three role anchors** verbatim. Hold their full content in context for sub-agent prompt construction.

9. **Round 1: spawn three role sub-agents in parallel via the Agent tool.** Issue a single tool-use block containing three Agent invocations (one per role), each with `subagent_type: general-purpose`. Each sub-agent's prompt contains:

   - The chosen-opportunity context (id, phase, quote, source, rationale, score profile).
   - The product outcome.
   - The Torres "explore multiple solutions" framing.
   - The role anchor (full content of the role's `knowledge/foundations/role-*.md` file).
   - The cross-role framing baselines.
   - The broad solution-scope definition (verbatim from `references/solution-brainstorm.md`).
   - Round-1 task: "Produce 2 solution candidates from your role's frame. Each candidate has a short title (5-12 words) and a 1-3 sentence description. Range freely across user-facing features, process redesigns, policy changes, integration changes, automation, internal tooling, removed steps, or org-level changes - whatever your role's lens suggests would plausibly move the product outcome on this opportunity. Return a JSON array of 2 objects with shape `{title, description}` and nothing else."

   Collect the three sub-agent responses; parse each as a JSON array of 2 candidates; assign deterministic ids (`sol-r1-pm-1..2`, `sol-r1-ux-1..2`, `sol-r1-tl-1..2`); attach `round_number: 1` and `generating_role` to each. Total: 6 ideas.

10. **Round 2: same orchestration as round 1, with these additions:**
   - The full pool of 6 round-1 ideas (id, role, title, description) provided as the "do not duplicate" context.
   - The anti-duplication rule (from `references/solution-brainstorm.md`, with inner quotes single-escaped): "Each idea must be either NEW (different core mechanism / target / surface from any prior idea in the pool) OR an explicit build-on of a specific prior idea (cite the prior idea by id or title in your description, e.g., 'Builds on sol-r1-pm-2 by ...'). Paraphrases or rewordings of prior ideas are not allowed."
   - Round-2 task: same JSON-array-of-2 instruction as round 1.

   Collect, parse, assign ids `sol-r2-{role-prefix}-1..2`, attach `round_number: 2`. Total: 6 more (running total: 12).

11. **Round 3: same orchestration as round 2, with the pool now 12 ideas (round 1 + round 2).**
   Collect, parse, assign ids `sol-r3-{role-prefix}-1..2`, attach `round_number: 3`. Total: 6 more (running total: 18).

12. **Compose the v0.1 JSON.** Top-level fields per the schema in `references/solution-brainstorm.md`. Specifically: `schema_version` is the literal `"0.1"`; `team` carries from Step 7 (top-level `team` in `decisions.json`); `title` is derived from the opportunity id (e.g. `opp-42`); `product_outcome` carries from Step 7 (`product_outcome` in `decisions.json`); `chosen_opportunity` carries the four fields from Step 6 (id, phase_id, quote, source); `source_chosen_opportunity_file` is the repo-root-relative path to `<scope>/decisions.json` (resolve to a literal path before writing). `solutions[]` is the concatenation of the three rounds in order (rounds 1, 2, 3). Within each round the order is PM ideas (1..2), then UX (1..2), then TL (1..2). Always write `generation_summary` as the fixed v0.1 block: `{"rounds": 3, "roles": ["product-manager", "ux-designer", "tech-lead"], "ideas_per_role_per_round": 2, "total_solutions": 18}`.

13. **Note on chosen-opp consistency.** Since both the composed JSON and the sub-agent prompts pull `chosen_opportunity` directly from `decisions.json` structured fields (Step 6), there is no parse ambiguity. No separate consistency check is needed.

14. **Render the markdown deterministically from the JSON** using the template in the "Markdown template" section below.

15. **Write paired output** to:
    - `<scope>/_working/solution-candidates.json`
    - `<scope>/_working/solution-candidates.md`

    Use today's date in `YYYY-MM-DD` format for the round folder name (already part of `<scope>`). The two files share the same root name. Create the `<scope>/_working/` directory if it doesn't exist. Upstream files (`decisions.json`, role anchors) are not modified.

16. **Launch the viewer.** Follow `knowledge/discovery/viewer-launch.md` to resolve the viewer path, start the server, and open the browser.

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
| `decisions.json` not found in the round folder at `<scope>/decisions.json` | Trio's ratified decisions file in the round folder | Run `OST-select-opportunity` to produce `decisions.json`, or restore from git |
| `decided.opportunity` missing from `decisions.json` | `decided.opportunity` key with `id`, `phase_id`, `quote`, `source` fields | Re-run `OST-select-opportunity` to ratify an opportunity into `decisions.json` |
| Any of the three role anchors missing | All three at `knowledge/foundations/role-{product-manager,ux-designer,tech-lead}.md` | Restore from git |
| A round produced ≠ 6 ideas after sub-agent collection | 2 ideas × 3 roles per round (6 per round) | Re-run; if persistent, the role prompts need tuning |
| A sub-agent returned malformed JSON | A JSON array of 2 `{title, description}` objects | Re-run; if persistent, the role-prompt JSON instruction needs tightening |

## Markdown template

The markdown output is rendered deterministically from the composed JSON using this template:

```markdown
---
title: Solution candidates - <title> (<team>)
date: <YYYY-MM-DD>
purpose: Divergent solution-candidate set for the chosen opportunity, paired with solution-candidates-<date>.json. Consumed by assist 7 (OST-cluster-solutions). Trio review at assist 8 (top-3 selector).
tags: [solution-brainstorm, ost, schema-v0.1]

---

# Solution candidates: <title> (<team>)

Source: `<scope>/decisions.json`
Schema version: 0.1
Paired JSON: `_working/solution-candidates-<YYYY-MM-DD>.json`

Generation summary: 3 rounds × 3 roles × 2 ideas = 18 total. Roles: Product Manager (PM), UX Designer (UX), Tech Lead (TL).

## Chosen opportunity

**<chosen.id>** (Phase: <phase_id>) - "<chosen.quote>" - *<chosen.source>*

## Product outcome

> <full outcome formulation>

## Round 1 (6)

- **[PM]** *<title>* - <description>
(repeat: 2 PM, then 2 UX, then 2 TL, in id order within each role)

## Round 2 (6)

- **[PM]** *<title>* - <description>
(repeat: 2 PM, then 2 UX, then 2 TL; build-on entries name the prior idea by id or title in the description)

## Round 3 (6)

- **[PM]** *<title>* - <description>
(repeat: 2 PM, then 2 UX, then 2 TL; build-on entries name the prior idea by id or title in the description)
```

## Output principles

- **Within each round, ideas are listed in deterministic order**: PM 1..2, UX 1..2, TL 1..2 (matching the JSON `solutions[]` order).
- **Title is italicized** with single-asterisk wrapping (`*<title>*`); **role tag is bracketed and bolded** (`**[PM]**` / `**[UX]**` / `**[TL]**`); description follows after a regular dash separator (` - `).
- **No em-dash** anywhere, applied uniformly across languages.
- **Frontmatter on the markdown output** follows the project convention that every `.md` file has YAML frontmatter (title, date, purpose, tags), with a blank line before the closing `---`.
- **Output language for prose** (the solution titles and descriptions) follows the language the sub-agent generates, which tends to match the language of the chosen opportunity quote and the role anchors. Schema field names, JSON keys, role enum values, and id strings stay in English as defined.
- **Section order is fixed** and the AI does not insert ad-hoc sections.
- **No HITL banner.** Phase 2's HITL is at assist 8 (top-3 selector), not here.
- **No `Cites:` line.** Solutions are generative; no per-idea evidence trace.
- **Build-on entries** in rounds 2 and 3 reference the prior idea inline in the description (e.g., "Builds on sol-r1-pm-2 by adding ..." or "Builds on the 'auto-renewal nudge' idea by ..."). No structural reference field.
- **No silent degradation.** Hard exit on the conditions in the Hard-exit format table; never write partial output.
- **No JSON self-validation pass.** Trust the prompt; downstream skills surface any malformed JSON.
- **Upstream files are immutable.** Never modify `decisions.json` or the role anchors. The skill writes only the two `solution-candidates.*` files inside `<scope>/_working/`.
- **Single orchestrator pass.** Three rounds executed in sequence; sub-agent calls happen via the Agent tool but the skill itself doesn't iterate or retry beyond the structured rounds.

## What this skill does NOT do

- **Read interview transcripts.** Solutions are generative, not evidence-traced.
- **Read the comparison matrix, validated table, clustered experience map, or extracted opportunities.** All chosen-opportunity context is in `<scope>/decisions.json`.
- **Read the selector's proposal in `<scope>/../../opportunity-selection/<round>/`.** The skill reads only the trio-ratified data in `<scope>/decisions.json`.
- **Modify upstream files.** `decisions.json` and the role anchors stay immutable.
- **Cluster, score, rank, or select solutions.** Those are downstream (assist 7 clusterer, assist 8 top-3 selector).
- **Generate assumptions, risk maps, or test cards.** Those are downstream (assists 9-12).
- **Pre-cluster or theme-tag the 18 candidates.** Pure-divergent output.
- **Curate AI "top picks" in the output.** All 18 are presented flat.
- **Run a JSON self-validation pass after composition.**
- **Write to Miro or any external surface.** JSON + markdown only.
- **Iterate beyond three rounds.** 3 rounds is locked for v1.
- **Configure idea counts, round counts, or role counts.** All locked at 3×3×2=18 for v1.
- **Use a `build_on` schema field.** Build-on linkage is prose-only in `description`.
- **Use `assumptions`, `risk_level`, or any phase-2-output field.**
- **Restrict solutions to user-facing features.** Solution scope is broad.
- **Constrain roles to specific surfaces.** Role anchors steer framing; no role is locked to a single surface.
- **Hide role attribution from the markdown.** `[PM]`, `[UX]`, `[TL]` tags are visible inline.
- **Group solutions by role within a round.** Flat-list rendering with role tags.
- **Read each other's output mid-round.** Within-round sub-agents are blind to peers.
- **Self-validate or re-rank ideas.** No post-pass scoring.
- **Write outside the resolved scope.** The skill writes only to `<scope>/_working/solution-candidates.{md,json}`.
- **Re-run sub-agents on partial failures.** Any sub-agent failure (malformed JSON, wrong count) hard-exits the orchestrator.
- **Use a `Cites:` line in the markdown.**
- **Use emoji or numeric encoding for role tags.**
