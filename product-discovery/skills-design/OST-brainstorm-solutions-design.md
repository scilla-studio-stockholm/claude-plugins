---
title: "OST-brainstorm-solutions: design spec"
date: 2026-05-10
purpose: Locked design for assist 6 in opportunity-solution-tree-agents.md - takes the trio-ratified chosen-opportunity from workspace/context/chosen-opportunity.md and the product outcome, spawns three role sub-agents (PM, UX, Tech Lead) in parallel per round across three rounds via the Agent tool with a prompt-only "new or build-on, no paraphrases" anti-duplication rule, and produces 18 paired JSON + markdown solution candidates conforming to a new schema v0.1 in ../knowledge/discovery/solution-brainstorm.md. Input to the implementation plan.
tags: [skill-design, workshop-3, ost, solution-brainstorm, schema-v0.1, agent-orchestration]

---

# OST-brainstorm-solutions: design spec

This is the locked design for **assist 6** in `opportunity-solution-tree-agents.md`. It is the seventh skill built in the workshop 3 series, after `OST-opportunity-extractor`, `OST-validate-opportunities`, `OST-extract-experience-map`, `OST-cluster-opportunities`, `OST-compare-opportunities`, and `OST-select-opportunity`. The implementation plan derives from this document.

This is the first assist in **phase 2 (solution space)**. All prior assists were phase 1 (opportunity space). The HITL pattern shifts here: phase 1 was trio-driven discovery with AI summarization; phase 2 starts with AI-driven generation, and the trio comes in at the end of the phase (assist 8) to approve top 3. There is no in-skill HITL banner in this skill's output; the trio's gate is downstream.

## What the skill does

For product trios and researchers, when generating a divergent set of solution candidates for one chosen opportunity, output 18 paired JSON + markdown solution candidates produced by three role-diversified sub-agents (PM, UX, Tech Lead) over three rounds with cross-round anti-duplication.

Input is the trio-ratified `workspace/context/chosen-opportunity.md`, the trio's `workspace/context/product-outcome.md`, three role anchors, and three knowledge anchors. Output is two files in `workspace/4-solution-brainstorm/` with the same root name: a solution-candidates JSON conforming to schema v0.1 in a new knowledge anchor `../knowledge/discovery/solution-brainstorm.md`, and a markdown rendering generated deterministically from the JSON.

The orchestration uses the **Agent tool** to spawn three role sub-agents in parallel per round. Within a round the sub-agents are blind to each other (each only sees the chosen opp, outcome, and its own role anchor); in rounds 2 and 3 they all see the full prior pool of ideas and follow a "new or build-on, no paraphrases" rule. Anti-duplication is prompt-only; assist 7 (clusterer) is the dedup layer.

The skill produces 18 raw candidates. There is no AI curation, theme-tagging, or pre-clustering at this stage. Pure-divergent output is the design intent: keep generation and clustering as separate concerns.

## Scope decisions (locked 2026-05-10)

The brainstorm narrowed the open questions in `opportunity-solution-tree-agents.md` (lines 487-493) and added several mechanical decisions. Each decision below resolves an open question.

| Question | Decision |
|---|---|
| Skill vs agent | **Skill that spawns sub-agents.** Single SKILL.md prompt at `.claude/skills/OST-brainstorm-solutions/SKILL.md`. Body instructs Claude to use the Agent tool to spawn 3 role sub-agents per round in parallel; orchestrator carries cross-round context. Matches the existing skill conventions (file location, frontmatter, NL trigger). The Agent tool is the parallelism primitive, not a separate "agent" construct. |
| Within-round orchestration | **Parallel, blind to each other.** Spawn PM, UX, Tech Lead sub-agents simultaneously in one Agent tool call (multiple invocations in one block). Each role sees the chosen opp, outcome, and its own role anchor; NOT the other roles' output for the same round. Maximum diversification. |
| Cross-round inheritance | **All roles' prior ideas in full.** PM in round 2 sees all 15 round-1 ideas (PM + UX + Tech Lead). Same for UX and Tech Lead. Round 3 sees the full 30-idea round-1+2 pool. The role anchor still keeps each sub-agent in its own frame; the prior pool defines what's already covered. |
| Anti-duplication mechanics | **Prompt-only, no enforcement.** Round 2/3 prompts include the prior pool plus an explicit rule: "Each idea must be either NEW (different core mechanism / target / surface from any prior idea) OR an explicit build-on of a specific prior idea (cite the prior idea by its title in your description)." Sub-agents self-classify in prose; no schema field, no post-pass dedup. assist 7 (clusterer) is the dedup layer. |
| Input source | **Ratified `workspace/context/chosen-opportunity.md`.** Hard-require the trio's ratified file. Hard-exit if missing with a remedy pointing the operator to the proposal in `workspace/3-opportunity-select/`. Honors the contract `OST-select-opportunity` locked: phase 2 starts with a trio-owned decision, not an AI proposal. |
| Ratified file shape | **Mirror selector proposal markdown, minus alternatives + HITL banner.** Required sections: frontmatter (title/date/purpose/tags), `## Product outcome`, `## Chosen opportunity` (id-quote-source line in the same bold-id-then-quote format the selector renders), `### Score profile` table, `### Rationale` prose, optional `## Evidence gaps carried into phase 2`. The trio's ratification action is concrete: copy proposal md, trim alternatives + HITL banner, edit chosen opp / rationale if overriding, save to `workspace/context/`. |
| Per-solution schema fields | **Minimal five: id, title, description, generating_role, round_number.** Flat schema. No `build_on` field (anti-dup is prompt-only). No `assumptions` or `risk_level` (those are assist 9+ territory). |
| Role attribution rendering | **Visible, flat list per round.** JSON has `generating_role` for every solution. Markdown renders three `## Round N (6)` sections, each a flat list of 6 entries with `[PM] / [UX] / [TL]` inline tags before the title. No grouping by role within round. |
| Solution scope | **Anything that affects outcome.** "A solution is anything a product trio could ship or change that plausibly moves the product outcome on the chosen opportunity. This includes user-facing features, process redesigns, policy changes, integration changes, automation, internal tooling, removed steps, or org-level changes." Each role's anchor steers framing but no role is forced to stay only inside one surface. |
| Idea count | **3 rounds × 3 roles × 2 ideas = 18, locked for v1.** Configurable counts is a v0.2 follow-up. |
| HITL flavor | **Pure-divergent.** 18 raw candidates, no AI curation, no pre-clustering, no themed-prep. The trio's HITL gate for phase 2 is at assist 8 (top-3 selector), not in this skill. |
| Output location | `workspace/4-solution-brainstorm/`. Stage-numbered convention continuing `1-opportunity-val/`, `2-opportunity-compare/`, `3-opportunity-select/`. |
| Output filename | `solution-candidates-<YYYY-MM-DD>.{json,md}` per cross-cutting datakontrakt. |
| Output format | Paired JSON + markdown. JSON is the contract for assist 7; markdown is for human eyeballing if a trio wants to peek before clustering. |
| Schema location | New knowledge anchor `../knowledge/discovery/solution-brainstorm.md` (mirrors the comparator, selector, and experience-map precedents). Schema is v0.1. |
| Slug name | `OST-brainstorm-solutions`. Verb-first matches `OST-validate-opportunities`, `OST-cluster-opportunities`, `OST-compare-opportunities`, `OST-select-opportunity`, `OST-extract-experience-map`. Plural noun reflects that the output is multiple solutions. |
| Role-anchor paths | **Generic role anchors in `knowledge/foundations/`.** Three new files created during this build: `role-product-manager.md`, `role-ux-designer.md`, `role-tech-lead.md`. English, generic, applicable to any product trio practicing this method. The skill has zero coupling to any specific company, product, or tech stack. Per-team overrides are a v0.2 follow-up (e.g., `workspace/context/role-*.md` shadowing the foundations defaults). |
| Body language | English, matching precedent. Ratified files may be Swedish (the trio's working language); the skill body, new knowledge anchor, and role anchors are English so the skill is reusable across teams. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-brainstorm-solutions/SKILL.md` |
| Skill name | `OST-brainstorm-solutions` |
| Slash-command (optional) | `/OST-brainstorm-solutions` if frequency justifies it |
| Body language | English, matching the precedent set by `OST-validate-opportunities`, `OST-extract-experience-map`, `OST-cluster-opportunities`, `OST-compare-opportunities`, and `OST-select-opportunity` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when generating a divergent set of solution candidates for one chosen opportunity, output 18 paired JSON + markdown solution candidates produced by three role-diversified sub-agents (PM, UX, Tech Lead) over three rounds with cross-round anti-duplication.

This follows the "for X, when Y, output Z" pattern. It is generic and company-agnostic. It is distinct from `OST-select-opportunity` (picks one opp; doesn't generate solutions), `OST-compare-opportunities` (scores opps against criteria), and `OST-cluster-opportunities` (groups opps against an experience map). The `brainstorm-` verb signals divergence; downstream `cluster-` and a future `select-solutions` skill follow the same naming pattern as the opportunity-side trio.

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/context/chosen-opportunity.md` | Trio-ratified, fixed path | Chosen opp's id, phase, quote, source, rationale, score profile |
| `workspace/context/product-outcome.md` | Trio-authored, fixed path | Outcome formulation; team name |
| `../knowledge/foundations/role-product-manager.md` | Generic role anchor (created during this build) | PM sub-agent's lens |
| `../knowledge/foundations/role-ux-designer.md` | Generic role anchor (created during this build) | UX sub-agent's lens |
| `../knowledge/foundations/role-tech-lead.md` | Generic role anchor (created during this build) | Tech Lead sub-agent's lens |

**File-resolution rules:** Both input files are at fixed paths with no date suffix. The role anchors are at fixed paths.

**Knowledge anchors read at runtime:**

- `../knowledge/discovery/solution-brainstorm.md` (NEW, created as part of this build) - the JSON schema, the three-round structure, the role-diversification framing, the anti-duplication convention, the broad-solution-scope definition.
- `../knowledge/foundations/tech-product-trio-responsibility-split.md` - cross-role framing baseline; reinforces the role lenses.
- `../knowledge/foundations/product-trio-operational-practices.md` - cross-role framing baseline.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - solution-space principles, especially "Choose three solutions to explore in parallel" (which motivates the divergent generation here) and the cautious framing on idea quality vs. quantity.

Per the cross-cutting datakontrakt decision, anchors are read at runtime rather than hard-coded into the prompt.

**What the skill does NOT consume:**

- Interview transcripts.
- The original `opportunities-extracted-*` or `opportunities-validated-*` files.
- The clustered experience-map JSON.
- The comparison matrix JSON.
- The selector's proposal in `workspace/3-opportunity-select/`. The skill reads only the ratified `workspace/context/chosen-opportunity.md`.

**Role anchors are generic by default.** Three new role-anchor files are created in `knowledge/foundations/` as part of this build (see "Knowledge-doc updates required before ship"). They describe the PM, UX, and Tech Lead lenses in company-agnostic terms, drawing on the same discipline knowledge that already lives in `knowledge/foundations/` (product-trio-operational-practices, tech-product-trio-responsibility-split, Cagan's empowered-team writing). The skill body, the new `solution-brainstorm.md` anchor, and the role anchors contain zero references to any specific company, product, tooling, or domain. Per-team override of role anchors (a future v0.2 follow-up) would let trios shadow these defaults from `workspace/context/role-*.md` if they want a tighter local frame.

## The new knowledge anchor: `../knowledge/discovery/solution-brainstorm.md`

This anchor carries the same role for the brainstormer that `opportunity-comparison.md` carries for the comparator and `opportunity-selection.md` carries for the selector: it owns the schema, the three-round structure, the role-diversification framing, the anti-duplication convention, and the broad solution-scope definition. Created as a one-time write during this skill's build; not modified at runtime.

Sections in the anchor:

1. **What the brainstormer does** - short framework prose tying it to Torres CDH ch 8 ("Generate solutions"). Notes that the brainstormer consumes a ratified chosen opportunity and produces a divergent candidate set; clustering and selection are downstream.
2. **The three-round structure** - why three rounds: round 1 catches the intuitive, rounds 2 and 3 force divergence past the obvious. From workshop-loops literature.
3. **Role diversification** - why PM, UX, Tech Lead specifically. Each role's lens biases what surface area they explore. Three roles is the trio's structural diversity; using them as generation anchors maps the diversity into the candidate set.
4. **The anti-duplication rule** - prompt-only, "new or build-on, no paraphrases", build-on entries cite the prior idea by title in their description. assist 7 (clusterer) is the dedup layer.
5. **Definition of "solution"** - "A solution is anything a product trio could ship or change that plausibly moves the product outcome on the chosen opportunity. This includes user-facing features, process redesigns, policy changes, integration changes, automation, internal tooling, removed steps, or org-level changes." Each role steers framing; no role is restricted to a single surface.
6. **Pure-divergent output convention** - 18 raw candidates with no curation, no clustering, no themed-prep at this stage. The trio's HITL gate is downstream at assist 8.
7. **JSON schema (v0.1)** - the contract.
8. **Field notes** - per-field commentary including the missing-optional convention and id-encoding scheme.
9. **Open questions** - what's punted to v0.2.
10. **Evolution** - version history.

**Schema v0.1:**

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
  "source_chosen_opportunity_file": "workspace/context/chosen-opportunity.md",
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
      "description": "string (1-3 sentences; build-on entries name the prior idea by title inline)"
    }
  ]
}
```

**Schema design notes:**

- `chosen_opportunity` is a singular object, denormalized at the top level so assist 7 can read the chosen opp without reloading `workspace/context/`.
- `generation_summary` is a fixed-shape sanity block. v0.1 always reads `{rounds: 3, roles: [...], ideas_per_role_per_round: 2, total_solutions: 18}`. If a trio overrides counts in a future v0.2, this block reflects the override; v0.1 is locked.
- `solutions[]` is one flat array, not nested by round/role. Length is exactly 18. Round and role are properties of each entry, not array structure. Easier for assist 7 to consume; trivial to group/filter in either dimension.
- `solutions[].id` is deterministic: `sol-r<round>-<role-prefix>-<index>` where role-prefix is `pm` (product-manager) / `ux` (ux-designer) / `tl` (tech-lead) and index is 1..2 within (round, role). Example: `sol-r2-tl-1` = round 2, Tech Lead, idea 1. Predictable, sortable, easy to reference in build-on prose.
- No `build_on` schema field. Anti-duplication is prompt-only; build-on linkage in round 2/3 lives in the `description` prose ("Builds on sol-r1-pm-2 by ..." or "Builds on the 'auto-renewal nudge' idea by ..."). Adding a structural field would be inconsistent with the prompt-only anti-dup decision and would duplicate work the clusterer does.
- No `assumptions` or `risk_level` field. Those live in assists 9-12 (assumption identification, risk mapping). Brainstorm output stays minimal so the trio's review surface stays manageable.

**Schema invariants:**

- `solutions[]` length is exactly 18.
- For each `(round_number, generating_role)` pair, exactly 2 entries.
- `solutions[].id` values are unique.
- `solutions[].id` matches the regex `^sol-r[123]-(pm|ux|tl)-[12]$`.
- `solutions[].round_number` ∈ {1, 2, 3}.
- `solutions[].generating_role` ∈ {`product-manager`, `ux-designer`, `tech-lead`}.
- `chosen_opportunity.id` matches the id parsed from `workspace/context/chosen-opportunity.md`.
- `generation_summary` is the fixed v0.1 block.
- No `build_on`, `assumptions`, `risk_level`, or other extension fields anywhere.

## Companion knowledge-anchor update: `../knowledge/discovery/opportunity-selection.md`

This skill is the first to consume `workspace/context/chosen-opportunity.md`. The selector explicitly does NOT write that file; the trio ratifies into it manually. The shape of that ratified file was not previously documented anywhere. As part of this build, add a **"Ratification format"** section to `opportunity-selection.md` documenting the contract the brainstormer hard-requires.

Required content of `workspace/context/chosen-opportunity.md` (mirrors the selector's proposal markdown, minus alternatives and HITL banner):

- YAML frontmatter (title, date, purpose, tags) with blank line before closing `---`.
- `## Product outcome` section, with the outcome formulation as a blockquote.
- `## Chosen opportunity` section, with a single bold-id line of the form: `**<opp-id>** (Phase: <phase-id>) - "<quote>" - *<source>*`.
- `### Score profile` subsection with a 5-row markdown table (one row per criterion: outcome-alignment, customer-importance, market-size, strategic-fit, competitive-landscape) and a `Profile summary:` line.
- `### Rationale` subsection with 2-4 sentences of prose. Trio may rewrite or expand from the selector's draft.
- Optional `## Evidence gaps carried into phase 2` section with bullet entries (omitted entirely if the trio has none).

Trio's ratification action: copy `workspace/3-opportunity-select/chosen-opportunity-<date>.md` to `workspace/context/chosen-opportunity.md`, delete the `> **Trio HITL:**` blockquote and the `## Alternatives considered` section, edit the chosen opportunity / rationale if overriding the AI's pick, update the frontmatter `purpose` line to reflect that this is the ratified decision-of-record (not a proposal), commit. The brainstormer reads this file unchanged.

This format documentation does not bump the `opportunity-selection.md` schema version (v0.1 stays). It's an addition to the prose sections, not a schema change.

## Steps

The skill follows the same numbered-step pattern as `OST-select-opportunity` and `OST-compare-opportunities`. Single orchestrator pass; sub-agent calls are nested but the skill itself doesn't iterate or retry beyond the three rounds.

1. **Read knowledge anchors:** the four files listed above (`solution-brainstorm.md`, the two foundations, the OST anchor).

2. **Locate inputs:**
   - `workspace/context/chosen-opportunity.md` (fixed path).
   - `workspace/context/product-outcome.md` (fixed path).
   - `../knowledge/foundations/role-product-manager.md` (fixed path).
   - `../knowledge/foundations/role-ux-designer.md` (fixed path).
   - `../knowledge/foundations/role-tech-lead.md` (fixed path).

3. **Hard-exit checks** (see Error handling). Do not write any output files when these fire.

4. **Parse `workspace/context/chosen-opportunity.md`.**
   - Extract chosen-opp `id`, `phase_id`, `quote`, `source` from the bold-id line under `## Chosen opportunity`.
   - Extract score profile from the `### Score profile` table (5 rows, criterion -> score).
   - Extract rationale prose from the `### Rationale` subsection.
   - Extract title from the frontmatter `title:` field. The selector renders this as `"Chosen opportunity - <opp-title> (<team>)"` (with a regular dash); the brainstormer derives `<opp-title>` by stripping the `"Chosen opportunity - "` prefix and the trailing ` (<team>)`.

5. **Parse `workspace/context/product-outcome.md`.**
   - Extract the outcome formulation under `## Outcome`.
   - Extract team name from `## Team`.

6. **Read the three role anchors.** Hold their full content in context for the orchestrator's sub-agent prompt construction.

7. **Round 1.** Spawn three role sub-agents in parallel via the Agent tool. The orchestrator issues a single tool-use block containing three Agent invocations (PM, UX, Tech Lead), each with `subagent_type: general-purpose`. Each sub-agent prompt is constructed from these parts:

   - The chosen-opportunity context (id, phase, quote, source, rationale, score profile).
   - The product outcome.
   - The Torres "explore multiple solutions" framing (1-2 sentences from the OST anchor).
   - The role's anchor (full content of the role-doc).
   - The cross-role framing baselines (1-2 paragraphs from `tech-product-trio-responsibility-split.md`).
   - The broad solution-scope definition (verbatim from the new knowledge anchor).
   - Round-1 task: "Produce 2 solution candidates from your role's frame. Each candidate has a short title (5-12 words) and a 1-3 sentence description. Range freely across user-facing features, process redesigns, policy changes, integration changes, automation, internal tooling, removed steps, or org-level changes - whatever your role's lens suggests would plausibly move the product outcome on this opportunity. Return a JSON array of 2 objects with shape `{title, description}`."

   Collect the three sub-agent responses; parse each as a JSON array of 2 candidates; assign deterministic ids (`sol-r1-pm-1..2`, `sol-r1-ux-1..2`, `sol-r1-tl-1..2`); attach `round_number: 1` and `generating_role` to each. Total: 6 ideas.

8. **Round 2.** Same orchestration as round 1, with these prompt additions:

   - The full pool of 6 round-1 ideas (id, role, title, description) provided as the "do not duplicate" context.
   - The anti-duplication rule (verbatim from the new knowledge anchor): "Each idea must be either NEW (different core mechanism / target / surface from any prior idea in the pool) OR an explicit build-on of a specific prior idea (cite the prior idea by id or title in your description, e.g., 'Builds on sol-r1-pm-2 by ...'). Paraphrases or rewordings of prior ideas are not allowed."
   - Round-2 task: same as round 1 plus the rule above.

   Collect, parse, assign ids `sol-r2-{role-prefix}-1..2`, attach `round_number: 2`. Total: 6 more ideas (running total: 12).

9. **Round 3.** Same as round 2, with the pool now being 12 ideas (round 1 + round 2). Round-3 task is the same as round 2; the rule applies against the larger pool.

   Collect, parse, assign ids `sol-r3-{role-prefix}-1..2`, attach `round_number: 3`. Total: 6 more (running total: 18).

10. **Compose the v0.1 JSON.** Top-level fields per the schema. `solutions[]` is the concatenation of the three rounds in order (rounds 1, 2, 3). Within each round the order is PM ideas (1..2), then UX (1..2), then TL (1..2). Always write `generation_summary` as the fixed v0.1 block.

11. **Render the markdown deterministically from the JSON** via the embedded template (Output composition).

12. **Write paired output** to:
    - `workspace/4-solution-brainstorm/solution-candidates-<YYYY-MM-DD>.json`
    - `workspace/4-solution-brainstorm/solution-candidates-<YYYY-MM-DD>.md`

    Use today's date in `YYYY-MM-DD`. Same root name on both files. Create `workspace/4-solution-brainstorm/` if it doesn't exist. The skill does NOT modify any input files; the chosen-opportunity, product-outcome, and role anchors stay immutable.

The orchestration is a single pass through three rounds. No retries beyond what individual sub-agent calls inherently do; if a sub-agent returns malformed JSON or a count off from 2, the skill hard-exits (see Error handling) rather than re-running.

## Output composition

Two files with the same root name:

```text
workspace/4-solution-brainstorm/solution-candidates-<YYYY-MM-DD>.json
workspace/4-solution-brainstorm/solution-candidates-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.1 from `../knowledge/discovery/solution-brainstorm.md`. No extra fields beyond the schema.

**The markdown** is generated deterministically from the JSON via an embedded template in the prompt:

````markdown
---
title: Solution candidates - <title> (<team>)
date: <YYYY-MM-DD>
purpose: Divergent solution-candidate set for the chosen opportunity, paired with solution-candidates-<date>.json. Consumed by assist 7 (OST-cluster-solutions). Trio review at assist 8 (top-3 selector).
tags: [solution-brainstorm, ost, schema-v0.1]

---

# Solution candidates: <title> (<team>)

Source chosen opportunity: `workspace/context/chosen-opportunity.md`
Source product outcome: `workspace/context/product-outcome.md`
Schema version: 0.1
Paired JSON: `solution-candidates-<YYYY-MM-DD>.json`

Generation summary: 3 rounds × 3 roles × 2 ideas = 18 total. Roles: Product Manager (PM), UX Designer (UX), Tech Lead (TL).

## Chosen opportunity

**<chosen.id>** (Phase: <phase_id>) - "<chosen.quote>" - *<chosen.source>*

## Product outcome

> <full outcome formulation>

## Round 1 (6)

- **[PM]** *<title>* - <description>
- **[PM]** *<title>* - <description>
- **[UX]** *<title>* - <description>
- **[UX]** *<title>* - <description>
- **[TL]** *<title>* - <description>
- **[TL]** *<title>* - <description>

## Round 2 (6)

(same shape as Round 1; build-on entries name the prior idea by id or title inline in the description)

## Round 3 (6)

(same shape as Round 2; pool is now 12 ideas)
````

**Rendering rules:**

- **Within each round, ideas are listed in deterministic order**: PM 1..2, UX 1..2, TL 1..2. The flat-list rendering uses tag prefixes (`[PM]`, `[UX]`, `[TL]`) instead of role subheadings.
- **Title is italicized**, role is bracketed and bolded, description follows after a regular dash separator.
- **No em-dash** anywhere, applied uniformly to Swedish and English prose.
- **Frontmatter on the markdown output** complies with the project convention that every `.md` file has YAML frontmatter (title, date, purpose, tags), with a blank line before the closing `---`.
- **No HITL banner.** Phase 2's HITL is at assist 8 (top-3 selector); this skill's output goes to the clusterer (assist 7), not directly to the trio for review.
- **Output language for prose** (the solution titles and descriptions) follows the language the sub-agent generates. The role anchors are Swedish, the chosen-opportunity quote may be Swedish, the product outcome may be Swedish; sub-agents will tend to produce Swedish output. Schema field names, JSON key strings, role enum values, and id strings stay as defined in English.
- **Section order is fixed** and the AI does not insert ad-hoc sections.
- **No `Cites:` line.** The brainstormer doesn't cite interview material; ideas are generative, not evidence-traced.
- **Build-on entries** in rounds 2 and 3 reference the prior idea inline in the description (e.g., "Builds on sol-r1-pm-2 by adding ..."). No structural reference field; the prose is the contract.

## Knowledge-doc updates required before ship

As part of building this skill:

- **Create `../knowledge/discovery/solution-brainstorm.md`** (the new anchor). Sections per "The new knowledge anchor" above. This is the canonical source for the schema, the three-round structure, the role-diversification framing, the anti-duplication rule, and the broad-solution-scope definition.
- **Create `../knowledge/foundations/role-product-manager.md`**, **`role-ux-designer.md`**, and **`role-tech-lead.md`**. Three new generic role anchors that describe each role's lens for solution brainstorming. Written in English and applicable to any product trio practicing this method. Each file follows the same shape: frontmatter (title, date, purpose, tags), a short framing paragraph on the role within a product trio, a "Lens for solution brainstorming" section describing how this role frames the solution space, a "Solution surfaces this role naturally explores" bullet list with concrete examples (features, flows, integrations, automation, processes, policies, removed steps - whichever fit the role), and an "Anti-patterns" bullet list. The files draw on discipline knowledge already represented in `knowledge/foundations/` (Cagan's empowered-team writing, product-trio-operational-practices, tech-product-trio-responsibility-split) but contain zero references to any specific company, product, tooling, or domain.
- **Update `../knowledge/discovery/opportunity-selection.md`** with a new "Ratification format" section documenting the structure of `workspace/context/chosen-opportunity.md`. Schema version stays at v0.1; this is a prose addition.

What is NOT updated:

- `workspace/README.md` - the staging-subdirectory documentation update is the same follow-up TODO already opened by `OST-compare-opportunities` and `OST-select-opportunity`. The brainstormer's `workspace/4-solution-brainstorm/` is another data point that the README's staging-dir documentation needs to catch up.
- `../knowledge/foundations/tech-product-trio-responsibility-split.md` and `product-trio-operational-practices.md` - the brainstormer reads them at runtime; they aren't extended.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - referenced but not extended.
- `skills-design/skill-template.md` Bygg-status - that gets updated in the implementation plan as a final task (mark `OST-brainstorm-solutions` built, "7 of 13"), not in this design.

## Error handling

**Hard-exit triggers** (no output files written when these fire):

| Trigger | Looked for | Remedy |
|---|---|---|
| `workspace/context/chosen-opportunity.md` missing | Trio's ratified chosen-opportunity file | Review the proposal in `workspace/3-opportunity-select/`, ratify into `workspace/context/chosen-opportunity.md` per the format in `../knowledge/discovery/opportunity-selection.md` |
| `workspace/context/product-outcome.md` missing | Trio's product outcome file | Restore from git or re-author using the template structure |
| chosen-opportunity.md missing `## Chosen opportunity` section with parseable id/quote/source line | The bold-id line: `**<opp-id>** (Phase: <phase-id>) - "<quote>" - *<source>*` | Re-ratify using the format in `../knowledge/discovery/opportunity-selection.md` |
| chosen-opportunity.md missing `## Product outcome` blockquote | An outcome formulation in the ratified file | Re-ratify; copy outcome from `workspace/context/product-outcome.md` |
| Product outcome file has no extractable `## Outcome` or `## Team` section | Headings `## Outcome` and `## Team` followed by content | Re-author `workspace/context/product-outcome.md` using the template structure |
| Any of the three role anchors missing | All three role anchors at `knowledge/foundations/role-{product-manager,ux-designer,tech-lead}.md` | Restore from git |
| A round produced ≠ 6 ideas after sub-agent collection (some sub-agent over- or under-delivered) | 2 ideas × 3 roles per round | Re-run; if persistent, the role prompts need tuning. Hard-exit prevents partial output. |
| A sub-agent returned malformed JSON | A JSON array of 2 `{title, description}` objects | Re-run; if persistent, the role-prompt JSON instruction needs tightening |

**Hard-exit message format** (same shape as `OST-compare-opportunities` and `OST-select-opportunity`):

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

Three pieces in order: what failed, what the skill saw, what to do about it. No silent degradation. No retries beyond the implicit retry inside any single Agent tool call.

**Soft warnings:** None for v1. The clusterer (assist 7) is the layer that surfaces near-duplicates; the brainstormer doesn't second-guess sub-agent output.

**Convention for missing optional fields in JSON:** the skill writes the v0.1 schema as fully populated. There are no optional fields in v0.1 (every field is required by the schema invariants). `null` is never written.

**No JSON self-validation pass.** Trust the prompt; downstream skills surface any malformed JSON. Mirrors the precedent set by `OST-extract-experience-map`, `OST-cluster-opportunities`, `OST-compare-opportunities`, and `OST-select-opportunity`.

## What this skill does NOT do

- **Read interview transcripts.** Solutions are generative, not evidence-traced.
- **Read the comparison matrix, validated table, clustered experience map, or extracted opportunities.** All chosen-opportunity context is in `workspace/context/chosen-opportunity.md`.
- **Read the selector's proposal in `workspace/3-opportunity-select/`.** The skill reads only the trio-ratified file in `workspace/context/`.
- **Modify upstream files.** `chosen-opportunity.md`, `product-outcome.md`, and the role anchors stay immutable.
- **Cluster, score, rank, or select solutions.** Those are downstream (assist 7 clusterer, assist 8 top-3 selector).
- **Generate assumptions, risk maps, or test cards.** Those are downstream (assists 9-12).
- **Pre-cluster or theme-tag the 18 candidates.** Pure-divergent output; the trio's HITL gate is at assist 8.
- **Curate AI "top picks" in the output.** No favoritism; all 18 are presented flat.
- **Run a JSON self-validation pass after composition.**
- **Write to Miro or any external surface.** JSON + markdown only.
- **Iterate beyond three rounds.** 3 rounds is locked for v1.
- **Configure idea counts, round counts, or role counts.** All locked at 3×3×2=18 for v1; v0.2 follow-up.
- **Use a `build_on` schema field.** Build-on linkage is prose-only in `description`.
- **Use `assumptions`, `risk_level`, or any phase-2-output field.** Those live downstream.
- **Restrict solutions to user-facing features.** Solution scope is broad (process, policy, automation, integration, removed steps, org-level).
- **Constrain roles to specific surfaces.** PM/UX/TL anchors steer framing; no role is locked to a single solution surface.
- **Hide role attribution from the markdown.** `[PM]`, `[UX]`, `[TL]` tags are visible inline.
- **Group solutions by role within a round.** Flat-list rendering with role tags.
- **Read each other's output mid-round.** Within-round sub-agents are blind to peers; cross-round sub-agents see the full prior pool.
- **Self-validate or re-rank ideas.** No post-pass scoring or ranking; output is in generation order.
- **Write to `workspace/context/`.** The skill writes only to `workspace/4-solution-brainstorm/`.
- **Re-run sub-agents on partial failures.** Any sub-agent failure (malformed JSON, wrong count) hard-exits the orchestrator; the operator re-runs the skill end-to-end.
- **Use a `Cites:` line in the markdown.** No evidence-trace surface; ideas are generative.
- **Use emoji or numeric encoding for role tags.** Plain bracketed text (`[PM]`, `[UX]`, `[TL]`).

## Testing

Smoke test only for v1, no formal regression harness. Reuses the Norrsken chosen-opportunity from `OST-select-opportunity`'s smoke test (after manual ratification into `workspace/context/`) and the existing product-outcome.md.

```text
Pre-step (one-time fixture creation):
  Create workspace/context/chosen-opportunity.md by copying
    workspace/3-opportunity-select/chosen-opportunity-2026-05-10.md
  and removing:
    - The "> **Trio HITL:** ..." blockquote
    - The "## Alternatives considered (5)" section and its 5 bullet entries
  Update frontmatter:
    - title stays
    - date stays
    - purpose: rewrite to "Trio-ratified chosen opportunity for OST opportunity
      selection. Decision-of-record consumed by assist 6 (OST-brainstorm-solutions)
      and assist 8 (top-3 selector)."
    - tags: drop "schema-v0.1" if present (this is a markdown contract, not a
      JSON schema artifact)
  Save and commit.

Inputs:
  workspace/context/chosen-opportunity.md
    (Norrsken Licenstilldelning, opp-5-1 Delfi licens-upplägg)
  workspace/context/product-outcome.md
    (Norrsken licens-tilldelning outcome)
  ../knowledge/foundations/role-product-manager.md
  ../knowledge/foundations/role-ux-designer.md
  ../knowledge/foundations/role-tech-lead.md

Expect:
  - schema_version "0.1" in the output JSON
  - solutions[] length is 18
  - For each (round, role) pair, exactly 2 entries:
      (1, product-manager): 2; (1, ux-designer): 2; (1, tech-lead): 2
      (2, product-manager): 2; (2, ux-designer): 2; (2, tech-lead): 2
      (3, product-manager): 2; (3, ux-designer): 2; (3, tech-lead): 2
  - All solution ids unique and matching ^sol-r[123]-(pm|ux|tl)-[12]$
  - generation_summary == {rounds: 3, roles: [...], ideas_per_role_per_round: 2,
    total_solutions: 18}
  - chosen_opportunity.id == "opp-5-1"
  - chosen_opportunity.quote and source carried verbatim from
    workspace/context/chosen-opportunity.md
  - title and team carried correctly from inputs
  - Markdown frontmatter present with blank line before closing ---
  - Markdown has three "## Round N (6)" sections
  - Each round renders 6 entries in PM-then-UX-then-TL order with [PM]/[UX]/[TL]
    inline tags
  - Round 2 and 3 entries that are "build-on" cite a prior idea by id or title
    in their description
  - No em-dash anywhere in markdown body
  - No "Cites:" line, no "Trio HITL" banner

Eyeball checks (manual):
  - Each round's 6 ideas show clear role-lens diversity (PM tends toward
    product moves, UX toward experience moves, TL toward technical moves), even
    though scope is broad
  - Round 2 and 3 ideas are not lexical paraphrases of round 1 (no "automate the
    manual step" three times in different words)
  - Broad solution scope shows up: at least some entries are process redesigns,
    policy changes, or integration changes - not only UI features
  - Build-on entries in round 2/3 actually extend the cited prior idea rather
    than restating it
  - At least one entry per role per round is in Swedish (or the language of the
    Norrsken chosen-opportunity context); language-detection isn't a hard
    invariant but eyeball that the sub-agents aren't switching to English
    arbitrarily
```

If `solutions[]` length isn't 18, any (round, role) pair has the wrong count, ids drift from the regex, or the markdown is malformed in any other way, the prompt is wrong. A formal regression harness is overkill for v1.

What the smoke test does NOT exercise (parked as open follow-ups):

- Configurable idea / round / role counts.
- Trios that override the AI's chosen opportunity in the ratified file (the smoke test uses the AI's opp-5-1 directly).
- Per-team role-anchor overrides (the smoke test uses the generic anchors at the fixed paths; trios overriding role framing per-team is a v0.2 follow-up).
- Edge case where a sub-agent returns 0 ideas (hard-exit fires; smoke test doesn't construct this).
- Edge case where rounds 2 and 3 still produce near-duplicates despite the prompt rule (assist 7 surfaces this).

These gaps in test coverage are accepted for v1; they go on the open-follow-ups list.

## Open follow-ups

These are added to `TODO.md` rather than blocking v1.

1. **Workspace README staging-convention update.** Already on the follow-up list from `OST-compare-opportunities` and `OST-select-opportunity`. The brainstormer's `workspace/4-solution-brainstorm/` is another data point that the README's staging-dir documentation needs to catch up.
2. **Per-team role-anchor overrides.** v1 reads generic role anchors from `knowledge/foundations/role-{product-manager,ux-designer,tech-lead}.md`. If a trio wants a tighter local frame (e.g., team-specific phrasing, additional surfaces, narrower scope), v0.2 should let them shadow the defaults from `workspace/context/role-{product-manager,ux-designer,tech-lead}.md`. The skill would prefer the workspace shadow when present, fall back to the foundations default when not.
3. **Configurable idea / round / role counts.** v1 locks 3×3×2=18. If trios consistently want different sizing (e.g., 2 rounds, 4 roles, 6 ideas), surface this through a config in the knowledge anchor or an in-skill argument.
4. **Configurable role set.** v1 fixes PM/UX/Tech Lead. Some teams have different trios (e.g., engineering manager + designer + researcher). Make the role set extensible.
5. **Optional `build_on` schema field.** If the clusterer benefits from structured cross-round linkage instead of prose-only, add `build_on: ["sol-r1-pm-2"]` as an optional array field.
6. **Optional `target_user` or `target_phase` field.** If the clusterer's grouping by user-facing-vs-internal or by journey-phase is useful, add these as optional metadata.
7. **HITL flavor variants.** v1 is pure-divergent. If trios consistently want curated top-N or themed-prep, surface as configurable HITL flavor.
8. **Role lens leakage.** If sub-agents drift into other roles' surfaces (PM proposing pure UI changes, UX proposing API integrations) more than they should, tighten role-anchor sections in the prompt or split into more roles.
9. **Build-on quality.** If trios report that round 2/3 build-on entries actually restate the prior idea, add a post-composition pass that flags suspicious build-ons (e.g., high lexical overlap with the cited prior idea).
10. **Schema evolution beyond v0.1.** Bumps when downstream skills request new fields or trios produce structures v0.1 cannot represent. Procedure same as `opportunity-selection`: add an "Evolution" entry to `solution-brainstorm.md` and bump `schema_version` in the skill prompt.
11. **Anti-duplication enforcement layer.** v1 is prompt-only. If trios report that the 18-set has too many near-dups across rounds even with the prompt rule, add an optional post-pass dedup or a structural `build_on` field that the round-2/3 prompts must populate.
    - **Within-round near-duplicates: explicitly accepted as a designed property (decided 2026-05-11).** Round 1 PM and TL sometimes converge on the same obvious idea (e.g., in the Norrsken smoke fixture both proposed "automate Delfi API"). Within-round blindness is intentional - we want PM/UX/TL to think independently before seeing each other. The Norrsken fixture showed ~4% within-round near-dup rate; not a quality problem motivating extra LLM-call + test surface in the brainstormer. assist 7 (clusterer) is the single dedup station. Re-open only if the rate climbs significantly in production or if clusterer output is materially distorted by within-round duplicates.
12. **Solution-scope drift.** If trios report that the 18-set is dominated by user-facing features despite the broad-scope rule, tighten the prompt with explicit "at least N ideas per round must be process / policy / integration / removed-step" guidance.
