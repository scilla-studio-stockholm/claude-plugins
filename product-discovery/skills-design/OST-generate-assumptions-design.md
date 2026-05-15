---
title: "OST-generate-assumptions: design spec"
date: 2026-05-11
purpose: Locked design for assist 9 in opportunity-solution-tree-agents.md - takes the trio-ratified top-three-solutions v0.2 JSON (located via the ratification-flag pattern in workspace/context/ratifications.md), the chosen-opportunity, the product outcome, and the extracted experience map; spawns 9 method-pass sub-agents (3 methods x 3 solutions) in parallel via the Agent tool, then runs 3 per-solution LLM dedup-passes that merge similar assumptions across methods with source-method attribution preserved as an array; produces paired JSON + markdown per a new schema v0.1 in knowledge/discovery/assumption-generation.md. Input to the implementation plan.
tags: [skill-design, workshop-3, ost, assumption-generation, schema-v0.1, agent-orchestration]

---

# OST-generate-assumptions: design spec

This is the locked design for **assist 9** in `opportunity-solution-tree-agents.md`. It is the ninth skill built in the workshop 3 series and the first assist in **phase 3 (assumption testing)**. All prior assists were phase 1 (opportunity space) or phase 2 (solution space). The HITL pattern shifts again here: phase 3 assists generate intermediate artifacts in sequence (generate -> categorize -> riskiest-map), and the trio's gate is at the end of the phase (assist 11), not inside this skill. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when generating the assumptions that must hold for the top 3 solutions to move the product outcome, output a paired JSON + markdown rendering with three method-passes (storymap, pre-mortem, outcome-impact) per solution, deduped across methods with source-method attribution preserved as an array. Input to assist 10 (OST-assumption-categorizer).

Input is the trio-ratified `top-three-solutions-*.json` (located via the ratification-flag pattern in `workspace/context/ratifications.md`), the `chosen-opportunity.md`, the `product-outcome.md`, and the latest `experience-map-extracted-*.json`. Output is two files in `workspace/7-assumptions/` with the same root name: an assumptions JSON conforming to schema v0.1 in a new knowledge anchor `knowledge/discovery/assumption-generation.md`, and a markdown rendering generated deterministically from the JSON.

The orchestration uses the **Agent tool** to spawn 9 sub-agents in parallel (3 methods x 3 solutions). Within the 9-call block the sub-agents are blind to each other; each sees only its assigned solution, the chosen opportunity, the product outcome, and its method's framing. Storymap sub-agents additionally receive the extracted experience map as anchoring context. After collection, the orchestrator runs **3 per-solution LLM dedup-passes** (one per solution) that merge similar assumptions across the 3 methods and tag each surviving entry with a `source_methods` array. Each sub-agent produces exactly **6 assumptions**. There is no cross-solution dedup. There is no in-skill HITL banner - the trio's gate for phase 3 is downstream at assist 11 (OST-riskiest-assumptions).

## Scope decisions (locked 2026-05-11)

The brainstorm narrowed the six open questions in `opportunity-solution-tree-agents.md` (lines 608-615) and added several mechanical decisions. Each decision below resolves an open question.

| Question | Decision |
|---|---|
| Skill vs agent | **Skill that spawns 9 sub-agents.** Single SKILL.md prompt at `.claude/skills/OST-generate-assumptions/SKILL.md`. Body instructs Claude to use the Agent tool to spawn 9 method-pass sub-agents in parallel; orchestrator runs 3 dedup-passes after collection. Mirrors the existing skill pattern (OST-brainstorm-solutions). The Agent tool is the parallelism primitive; "agent" in the spec section 9's "Föreslagen typ" is a category label, not a separate construct. |
| Method orchestration | **Parallel, blind to each other.** Spawn 9 sub-agents (storymap x 3, pre-mortem x 3, outcome-impact x 3) simultaneously in one Agent tool-use block. Each sub-agent sees only its assigned solution + chosen opp + product outcome + its method's framing. Storymap sub-agents additionally receive the extracted experience map. Maximum diversification. |
| Count per method-pass | **Fixed 6 assumptions per sub-agent.** 6 x 3 methods x 3 solutions = 54 raw. After per-solution dedup approximately 10-14 per solution = approximately 30-42 deduped. Locked at v1; configurable counts are a v0.2 follow-up. |
| Cross-method dedup | **Per-solution LLM dedup-pass with `source_methods` array.** After the 9 sub-agent calls, three dedup-passes (one per solution) merge similar assumptions across the 3 methods. Each surviving entry carries a `source_methods` array of length 1-3 with values from `{storymap, pre-mortem, outcome-impact}`. Array length is the triangulation signal: a 3-source entry was surfaced by all three methods independently. |
| Cross-solution dedup | **None.** Each solution gets its own independent deduped list. No `shared_with` marking. Per-solution structure mirrors the workshop wall and matches the downstream categorizer contract. Cross-solution patterns are a future concern, not this skill's job. |
| Source-method attribution | **Visible in JSON as `source_methods` array; rendered in markdown as inline tag.** Not a hidden internal field. Preserves traceability and surfaces triangulation strength. |
| Experience map for storymap | **Yes, passed to storymap sub-agents only.** Provides anchoring context for inferring the future user-flow the solution implies. Prompt instructs sub-agent that the map is today's flow and to reason about the future. Hard-exit if missing (the workshop-3 pipeline assumes it exists from assist 3). |
| Input source for top-3 | **Ratification-flag pattern.** Read `workspace/context/ratifications.md`, find the latest entry whose artifact filename matches `top-three-solutions-*.json`, read that JSON from `workspace/6-top-three/`. Hard-exit if no matching ratification entry. Pattern defined in `knowledge/discovery/top-three-selection.md` (v2 introduced; this skill is the first consumer). |
| HITL flavor | **No in-skill HITL banner.** Trio gate for phase 3 is downstream at assist 11 (OST-riskiest-assumptions output). Matches the OST-brainstorm-solutions precedent (trio gate downstream at top-3 selector). |
| Output location | `workspace/7-assumptions/`. Stage-numbered convention continuing `1-opportunity-val/`, `2-opportunity-compare/`, `3-opportunity-select/`, `4-solution-brainstorm/`, `5-solution-cluster/`, `6-top-three/`. |
| Output filename | `assumptions-<YYYY-MM-DD>.{json,md}` per cross-cutting datakontrakt. |
| Output format | Paired JSON + markdown. JSON is the contract for assist 10; markdown is for human eyeballing if a trio wants to peek before categorization. |
| Schema location | New knowledge anchor `knowledge/discovery/assumption-generation.md`. Schema is v0.1. |
| Slug name | `OST-generate-assumptions`. Verb-first matches `OST-validate-opportunities`, `OST-cluster-opportunities`, `OST-compare-opportunities`, `OST-select-opportunity`, `OST-extract-experience-map`, `OST-brainstorm-solutions`, `OST-select-top-three-solutions`. Plural noun reflects multiple output. |
| Body language | English, matching precedent. Inputs and output prose may be Swedish (the trio's working language); the skill body and the new knowledge anchor are English so the skill is reusable across teams. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-generate-assumptions/SKILL.md` |
| Skill name | `OST-generate-assumptions` |
| Slash-command (optional) | `/OST-generate-assumptions` if frequency justifies it |
| Body language | English |
| Tools | `Read` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when generating the assumptions that must hold for the top 3 solutions to move the product outcome, output a paired JSON + markdown rendering with three method-passes (storymap, pre-mortem, outcome-impact) per solution, deduped across methods with source-method attribution. Input to assist 10 (OST-assumption-categorizer).

This follows the "for X, when Y, output Z" pattern. Generic and company-agnostic. Distinct from `OST-brainstorm-solutions` (generates 18 solutions; doesn't generate assumptions), `OST-select-top-three-solutions` (picks 3 from 18; no assumption work), and `OST-assumption-categorizer` (assist 10; classifies into the 5-category taxonomy but does not generate).

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/context/ratifications.md` | Trio-appended, fixed path | Find the latest ratified `top-three-solutions-*.json` filename |
| `workspace/6-top-three/<filename-from-ratifications>.json` | `OST-select-top-three-solutions` (assist 8) v0.2 | The 3 specific solutions (id, title, role, round, description, rationale) to decompose |
| `workspace/context/chosen-opportunity.md` | Trio-ratified, fixed path | Cross-check `chosen_opportunity.id` against source JSON; quote and source available as grounding context |
| `workspace/context/product-outcome.md` | Trio-authored, fixed path | Outcome formulation that grounds the outcome-impact method |
| `workspace/1-opportunity-val/experience-map-extracted-<date>.json` | `OST-extract-experience-map` (assist 3), latest by date | Anchoring context for the storymap sub-agents (today's user-flow structure) |

**File-resolution rules:** `ratifications.md`, `chosen-opportunity.md`, `product-outcome.md` at fixed paths. Top-three JSON filename comes from the ratifications line (latest matching line). Experience map: latest `experience-map-extracted-*.json` in `workspace/1-opportunity-val/` by date in filename, descending.

**Knowledge anchors read at runtime:**

- **`knowledge/discovery/assumption-generation.md`** (NEW, created as part of this build) - owns the schema, the three-method definitions, the parallel-blind orchestration, the dedup-pass convention, the source-method attribution rule, the count-per-pass rule.
- `knowledge/discovery/assumption-types.md` - the 5-category taxonomy. Read for reference only; this skill does NOT classify (that is assist 10). Sub-agents read the "Definition" and "Application notes" sections to know what counts as an assumption.
- `knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - the decompose-into-assumptions framing (CDH ch 8).
- `knowledge/discovery/top-three-selection.md` - the source schema (v0.2) and the ratification-flag pattern so the skill can parse the upstream output and find the ratified version.

Per the cross-cutting datakontrakt decision, anchors are read at runtime rather than hard-coded into the prompt.

**What the skill does NOT consume:**

- Interview transcripts.
- The OST-brainstorm-solutions output (`solution-candidates-*.json`); only the picked top-3 from the selector flows into this layer.
- Cluster-solutions output (off-pipeline anyway).
- The comparison matrix, validated opportunities, or the clustered experience map (the storymap method wants today's raw journey, not the opportunity overlay).
- Role anchors (`role-product-manager.md`, `role-ux-designer.md`, `role-tech-lead.md`). The role abbreviation is carried as data only; this skill does not apply a role lens to assumption generation.

## The new knowledge anchor: `knowledge/discovery/assumption-generation.md`

This anchor carries the same role for the generator that `solution-brainstorm.md` carries for the brainstormer and `top-three-selection.md` carries for the selector: it owns the schema, the three-method definitions, the parallel-blind orchestration, the dedup-pass convention, the source-method attribution rule, and the count-per-pass rule. Created as a one-time write during this skill's build; not modified at runtime.

**Sections in the anchor:**

1. **What the generator does** - short framework prose tying it to Torres CDH ch 8 ("Decompose into assumptions") and the workshop screenshot. Notes that the generator consumes a trio-ratified top-3 and produces a per-solution deduped assumption list with method attribution; categorization and risk-mapping are downstream.
2. **The three methods.**
   - **Storymap method:** infer the user-flow for the solution (user types -> steps); for each step, surface what must be true for that step to work. Today's experience map is anchoring context; the sub-agent reasons about the future flow the solution implies.
   - **Pre-mortem method:** imagine 6 months out, the solution failed. Walk the failure modes; for each mode, name the underlying assumption that turned out false.
   - **Outcome-impact method:** state why this solution would move the product outcome; for each reason, name the underlying assumption that has to hold.
3. **Per-method count rule** - exactly 6 assumptions per method per solution. Locked at v0.1.
4. **The parallel-blind orchestration** - 9 sub-agents fired in one Agent tool-use block, no sub-agent sees another's output.
5. **The dedup-pass convention** - one LLM dedup-pass per solution merges similar assumptions across the 3 methods; output entries carry a `source_methods` array (1-3 entries). Length is triangulation signal. Dedup-pass may not invent new assumptions.
6. **Definition of "assumption"** - drawn from `assumption-types.md`: "something the trio takes for granted but does not know to be true; if false, would sink the solution." The 5 categories from `assumption-types.md` are NOT applied here (that is assist 10).
7. **No in-skill HITL** - trio gate is downstream at OST-riskiest-assumptions (assist 11).
8. **JSON schema (v0.1)** - the contract.
9. **Field notes** - per-field commentary including the missing-optional convention and id-encoding scheme.
10. **Open questions** - what is punted to v0.2.
11. **Evolution** - version history.

**Schema v0.1:**

```json
{
  "schema_version": "0.1",
  "team": "string (carried from upstream top-three JSON)",
  "title": "string (e.g., 'Assumptions: <chosen_opportunity.id> - <first 5-10 words of quote>')",
  "product_outcome": "string (carried)",
  "chosen_opportunity": {
    "id": "string (carried; matches the bold-id row in workspace/context/chosen-opportunity.md)",
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

**Schema design notes:**

- `assumptions_per_solution[]` is a fixed-length-3 array, ordered by `pick_position` from the upstream `picks[]` order (which mirrors the selector's confidence ordering).
- `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number` are carried byte-identical from the upstream top-three JSON. No re-interpretation.
- `assumptions[].id` is deterministic: `asm-<solution_id>-<NNN>` where `NNN` is zero-padded 001..NNN within a solution. Order is the dedup-pass output order (the LLM may order by triangulation strength; not enforced).
- `assumptions[].source_methods` is an array of length 1-3. Values from the fixed enum `{storymap, pre-mortem, outcome-impact}`. Order is canonicalized to `["storymap", "pre-mortem", "outcome-impact"]` (deterministic regardless of method ordering in the upstream raw lists).
- `assumptions[].text` is 1-2 sentences in the language the upstream solution-description uses (typically Swedish for this trio's work).
- No `category` field. Categorization is assist 10's job. Pre-categorizing here would couple the two skills and force this skill to read `assumption-types.md` as more than reference.
- No `risk_level`, `importance`, or `evidence` fields. Those are assist 11's territory.
- No `shared_with` array. Per-solution structure only.
- `generation_summary` is a fixed-shape sanity block. v0.1 values are locked.

**Schema invariants** (skill enforces; hard-exit on violation, no partial writes):

- `assumptions_per_solution.length == 3`.
- Each `assumptions_per_solution[].solution_id` is in upstream `top-three-solutions.picks[].id`. No inventions.
- No duplicate `solution_id` across the 3 entries.
- For each per-solution entry, `6 <= assumptions.length <= 18`. Floor 6 prevents catastrophic over-dedup; ceiling 18 prevents sub-agent over-production.
- Each `assumption.id` matches `^asm-sol-r[123]-(pm|ux|tl)-[1-9][0-9]*-\d{3}$`.
- `assumption.id` values are unique across the entire output.
- `assumption.source_methods.length` is in `{1, 2, 3}`.
- `assumption.source_methods` values are a subset of `{storymap, pre-mortem, outcome-impact}`; no duplicates within an array.
- `chosen_opportunity.id` matches upstream JSON AND the bold-id row in `workspace/context/chosen-opportunity.md`.
- All carried fields (`solution_title`, `solution_description`, `generating_role`, `round_number`) byte-identical to upstream.
- `generation_summary` is the fixed v0.1 block.

## Steps

The skill follows the same numbered-step pattern as `OST-brainstorm-solutions` and `OST-select-top-three-solutions`. Single orchestrator pass; sub-agent and dedup-pass calls are nested but the skill itself does not iterate or retry.

1. **Read knowledge anchors:** `assumption-generation.md` (new), `assumption-types.md` (reference), `opportunity-solution-tree-teresa-torres.md`, `top-three-selection.md`.

2. **Locate inputs:**
   - `workspace/context/ratifications.md` (fixed path).
   - Parse ratifications: find the latest line matching `top-three-solutions-*.json`. Extract filename.
   - `workspace/6-top-three/<filename-from-ratifications>` (the ratified JSON).
   - `workspace/context/chosen-opportunity.md` (fixed path).
   - `workspace/context/product-outcome.md` (fixed path).
   - Latest `workspace/1-opportunity-val/experience-map-extracted-*.json` by date in filename.

3. **Hard-exit checks** (see Error handling). Do not write any output files when these fire.

4. **Parse inputs.**
   - Top-3 JSON: extract `picks[]`. Index by `id`.
   - `chosen-opportunity.md`: extract bold-id row (`id`, `phase_id`, `quote`, `source`), score profile, rationale.
   - `product-outcome.md`: extract `## Outcome` formulation and `## Team` name.
   - Experience map JSON: load as-is for storymap sub-agent prompts.

5. **Cross-check chosen-opp id.** Source top-3 JSON's `chosen_opportunity.id` must match the chosen-opportunity.md bold-id row. Mismatch -> hard-exit.

6. **Spawn 9 sub-agents in parallel.** The orchestrator issues a single Agent tool-use block containing 9 invocations (storymap x 3 solutions, pre-mortem x 3 solutions, outcome-impact x 3 solutions), each with `subagent_type: general-purpose`. Each sub-agent prompt is constructed from:

   - **Common context** (all 9): chosen opportunity (id, phase, quote, source), product outcome (verbatim), the one specific solution this sub-agent is reasoning about (id, title, description, generating_role, round_number, rationale from the upstream picks entry).
   - **Method-specific framing** (varies per method): 1-2 paragraphs from `assumption-generation.md` describing how that method surfaces assumptions, drawn from the workshop screenshot wall.
   - **Storymap sub-agents only:** additionally receive the `experience-map-extracted-*.json` content with explicit prompt instruction: "This is today's user journey. The solution may propose a new flow. Use this as anchoring but reason about the future flow the solution implies."
   - **Definition of "assumption"** (verbatim from `assumption-generation.md`).
   - **Per-method task:** "Produce exactly 6 assumptions for this solution using the <method-name> method. Each assumption is 1-2 sentences max. Return a JSON array of 6 objects with shape `{text: string}`. No other fields."

   Collect the 9 sub-agent responses; parse each as a JSON array of 6 entries. Total raw: 54.

7. **Per-solution dedup pass.** Three LLM calls in parallel (one per solution). Each receives:
   - The solution context (id, title, description).
   - The 3 method-lists for THIS solution (18 raw entries), each entry tagged with its source method.
   - The dedup task: "Merge assumptions that express the same underlying belief in different words. Preserve the source method of each merged entry as an array. Return a JSON array of deduped objects with shape `{text, source_methods}`. Do not invent new assumptions. Do not drop assumptions that are genuinely distinct."

   Collect 3 deduped lists. Each list length should be in `6..18`.

8. **Assign deterministic ids** to each surviving assumption: `asm-<solution_id>-<NNN>` (zero-padded 3-digit). Canonicalize `source_methods` array order to `["storymap", "pre-mortem", "outcome-impact"]`.

9. **Compose the v0.1 JSON.** Top-level fields per the schema. `assumptions_per_solution[]` ordered by upstream `pick_position` (1, 2, 3). Within each per-solution entry, `assumptions[]` in dedup-pass output order. Always write `generation_summary` as the fixed v0.1 block.

10. **Render the markdown deterministically** from the JSON via the embedded template (Output composition).

11. **Write paired output** to:
    - `workspace/7-assumptions/assumptions-<YYYY-MM-DD>.json`
    - `workspace/7-assumptions/assumptions-<YYYY-MM-DD>.md`

    Use today's date in `YYYY-MM-DD`. Same root name on both files. Create `workspace/7-assumptions/` if it does not exist. The skill does NOT modify any input files; the top-3 JSON, chosen-opportunity, product-outcome, experience map, and ratifications.md all stay immutable.

One pass through 9 sub-agents plus 3 dedup-passes. No retries beyond what individual Agent calls inherently do; if a sub-agent returns malformed JSON or wrong count, or a dedup-pass violates an invariant, the skill hard-exits rather than re-running.

## Output composition

Two files with the same root name:

```text
workspace/7-assumptions/assumptions-<YYYY-MM-DD>.json
workspace/7-assumptions/assumptions-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.1 from `knowledge/discovery/assumption-generation.md`. No extra fields beyond the schema.

**The markdown** is generated deterministically from the JSON via an embedded template in the prompt:

````markdown
---
title: "Assumptions: <chosen_opportunity.id> - <first 5-10 words of quote>"
date: <YYYY-MM-DD>
purpose: Per-solution deduped assumption lists with source-method attribution. Paired with assumptions-<date>.json. Input to assist 10 (OST-assumption-categorizer); trio gate downstream at assist 11 (OST-riskiest-assumptions).
tags: [assumption-generation, ost, schema-v0.1]

---

# Assumptions: <chosen_opportunity.id>

Source top 3 solutions: `<source_top_three_solutions>`
Source chosen opportunity: `workspace/context/chosen-opportunity.md`
Source product outcome: `workspace/context/product-outcome.md`
Source experience map: `<source_experience_map>`
Schema version: 0.1
Paired JSON: `assumptions-<YYYY-MM-DD>.json`

Generation summary: 3 methods (storymap, pre-mortem, outcome-impact) x 3 solutions x 6 assumptions = 54 raw, then per-solution dedup with source-method attribution.

## Chosen opportunity

**<chosen.id>** (Phase: <phase_id>) - "<quote>" - *<source>*

## Product outcome

> <outcome formulation>

## Solution 1: <solution_title>

**<solution_id>** [<role-abbrev>, R<round_number>]

<solution_description>

### Assumptions (<count>)

- **<asm-id>** [<methods-tag>] <text>
- **<asm-id>** [<methods-tag>] <text>
- ...

## Solution 2: <solution_title>

(same shape)

## Solution 3: <solution_title>

(same shape)
````

**Rendering rules:**

- **Role abbreviation mapping:** `product-manager` -> `PM`, `ux-designer` -> `UX`, `tech-lead` -> `TL`. Rendered in the solution header line as `[<role-abbrev>, R<round_number>]`.
- **Method tag mapping for assumptions:** `storymap` -> `SM`, `pre-mortem` -> `PrM`, `outcome-impact` -> `OI`. `PrM` is chosen over `PM` to avoid collision with the product-manager role abbreviation.
- **Multi-source method tags:** components combined alphabetically with `+` inside brackets. Examples: `[OI+SM]`, `[PrM+SM]`, `[OI+PrM+SM]`.
- **Source attribution** in the chosen-opportunity line carried verbatim. Separated from the quote by ` - ` (regular dash).
- **No em-dash** anywhere; uniform across Swedish and English prose.
- **Frontmatter** complies with the project rule (blank line before closing `---`).
- **No HITL banner.** Phase 3 trio gate is at assist 11 (OST-riskiest-assumptions); this skill's output goes to the categorizer (assist 10).
- **Output language for prose** (assumption text) follows the language of the upstream solution descriptions (typically Swedish for this trio). Schema field names, JSON key strings, method enum values, role enum values, and id strings stay as defined in English.
- **Section order is fixed** and the AI does not insert ad-hoc sections.
- **No `Cites:` line.** Assumptions are generative, not evidence-traced.
- **Pick ordering** in the markdown mirrors the upstream `picks[]` array order (which mirrors the selector's confidence ordering).

## Knowledge-doc updates required before ship

As part of building this skill:

- **Create `knowledge/discovery/assumption-generation.md`** (the new anchor). Sections per "The new knowledge anchor" above. This is the canonical source for the schema, the three-method definitions, the parallel-blind orchestration, the dedup-pass convention, the source-method attribution rule, and the count-per-pass rule.
- **Update `skills-design/skill-template.md` Bygg-status** - mark `OST-generate-assumptions` as built. Final task in the implementation plan, not in this design. Counting subject to confirmation against current template state when implementing.
- **Update `skills-design/opportunity-solution-tree-agents.md`** - replace the six open design questions in section 9 (lines 608-615) with a reference to the locked decisions in `skills-design/OST-generate-assumptions-design.md`. Update the "Föreslagen typ: agent" line to "skill that spawns 9 sub-agents" to match the actual decision.

What is NOT updated:

- `knowledge/discovery/assumption-types.md` - read as reference; the taxonomy stays for assist 10. Untouched.
- `knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - referenced but not extended.
- `knowledge/discovery/top-three-selection.md` - read for schema and ratification-flag pattern; no changes.
- `workspace/README.md` - the staging-dir-documentation follow-up is the same TODO already opened by `OST-compare-opportunities` and others; `workspace/7-assumptions/` adds another data point but is not a separate update here.

## Error handling

**Hard-exit triggers** (no output files written when these fire):

| Trigger | Looked for | Remedy |
|---|---|---|
| `workspace/context/ratifications.md` missing | The ratification log file | Create the file with `# Ratifications` heading + intro, append a line for the latest `top-three-solutions-*.json` per the format in `knowledge/discovery/top-three-selection.md` |
| No matching `top-three-solutions-*.json` line in ratifications | An append-only line of the form `- <date> top-three-solutions-*.json ratified by <approver> (<note>)` | Review the proposal in `workspace/6-top-three/`, append a ratification line |
| The referenced `top-three-solutions-*.json` missing in `workspace/6-top-three/` | The JSON file named in the ratification line | Run `OST-select-top-three-solutions`, or correct the filename in ratifications |
| Source JSON does not parse | Valid JSON conforming to `top-three-selection.md` v0.2 | Re-run `OST-select-top-three-solutions` |
| Source JSON `schema_version` is not `"0.2"` | The exact string `"0.2"` | Re-run `OST-select-top-three-solutions` against v0.2 |
| Source `picks[]` length != 3 | 3 picks (Torres canon) | Re-run `OST-select-top-three-solutions` |
| `workspace/context/chosen-opportunity.md` missing | Trio-ratified chosen-opportunity file | Restore from git or re-ratify per `knowledge/discovery/opportunity-selection.md` |
| `chosen-opportunity.md` missing parseable bold-id row under `## Chosen opportunity` | `**<opp-id>** (Phase: <phase-id>) - "<quote>" - *<source>*` | Re-ratify using the format in `opportunity-selection.md` |
| `workspace/context/product-outcome.md` missing or no `## Outcome` section | Heading `## Outcome` followed by content | Re-author per template |
| No `experience-map-extracted-*.json` in `workspace/1-opportunity-val/` | At least one extracted experience map | Run `OST-extract-experience-map` (assist 3) |
| `chosen_opportunity.id` mismatch (source top-3 JSON vs `chosen-opportunity.md` bold-id row) | Byte-identical id strings | Decide which version is authoritative; reconcile manually |
| Any knowledge anchor missing (`assumption-generation.md`, `assumption-types.md`, `opportunity-solution-tree-teresa-torres.md`, `top-three-selection.md`) | All four files at fixed paths | Restore from git |
| A sub-agent returned malformed JSON | A JSON array of 6 `{text}` objects | Re-run; if persistent, the method-prompt JSON instruction needs tightening |
| A sub-agent returned count != 6 | Exactly 6 entries | Re-run; if persistent, the per-method count rule needs tightening |
| A dedup-pass returned malformed JSON | A JSON array of `{text, source_methods}` objects | Re-run; if persistent, the dedup prompt needs tightening |
| A dedup-pass returned count outside `6..18` | Length floor 6 (catastrophic over-merge), ceiling 18 (no merge at all) | Re-run; if persistent, the dedup prompt is mis-calibrated |
| Dedup-pass output references a `source_methods` value outside `{storymap, pre-mortem, outcome-impact}` | Enum membership | Re-run |
| Final-JSON invariant violation (id collision, missing carried field, etc.) | Schema invariants above | Re-run |

**Hard-exit message format** (same shape as `OST-brainstorm-solutions` and `OST-select-top-three-solutions`):

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

Three pieces in order: what failed, what the skill saw, what to do about it. No silent degradation. No retries beyond the implicit retry inside any single Agent tool call.

**Soft warnings:** None for v1. The categorizer (assist 10) surfaces any taxonomy-related issues downstream; the OST-riskiest-assumptions agent (assist 11) surfaces evidence-quality issues. The generator does not second-guess sub-agent or dedup-pass output beyond the count/format invariants.

**Convention for missing optional fields in JSON:** v0.1 has no optional fields. `null` is never written.

**No JSON self-validation pass.** Trust the prompt and the invariant check; downstream skills surface any malformed JSON. Mirrors the precedent set by `OST-extract-experience-map`, `OST-cluster-opportunities`, `OST-compare-opportunities`, `OST-select-opportunity`, `OST-brainstorm-solutions`, and `OST-select-top-three-solutions`.

## What this skill does NOT do

- **Read interview transcripts.** Assumptions are generative, not evidence-traced.
- **Read the OST-brainstorm-solutions output, comparison matrix, validated opportunities, OST-cluster-solutions output, or clustered experience map.** Only the upstream contracts listed in Inputs.
- **Read the role anchors (`role-product-manager.md` etc.).** Role information is carried as the role abbreviation only; no role-lens shaping of assumptions.
- **Categorize assumptions into desirability / usability / feasibility / viability / other.** That is assist 10.
- **Score, rank, or flag assumptions as riskiest.** That is assist 11.
- **Generate test cards, validation plans, or experiment designs.** Out of scope; future phase 4.
- **Apply cross-solution dedup or mark `shared_with` assumptions.** Per-solution structure only.
- **Modify upstream files.** `ratifications.md`, top-three JSON, `chosen-opportunity.md`, `product-outcome.md`, experience map all stay immutable.
- **Write to `workspace/context/`.** Output lives in `workspace/7-assumptions/`.
- **Append to `ratifications.md`.** The trio ratifies downstream artifacts manually; this skill is upstream of the OST-riskiest-assumptions gate.
- **Add an in-skill HITL banner.** Trio gate is downstream at assist 11.
- **Run a JSON self-validation pass.**
- **Retry sub-agents on partial failures.** Hard-exit; operator re-runs end-to-end.
- **Use a `category`, `risk_level`, `importance`, `evidence`, or `shared_with` schema field.** All downstream territory.
- **Allow sub-agents to read each other's output.** Within-pass blindness across the 9 sub-agents is intentional.
- **Allow the dedup-pass to invent new assumptions.** The dedup-pass prompt explicitly forbids new assumptions; it merges or keeps, never adds.
- **Configure the method set, count per method, solution count, or per-team overrides.** All locked at v1.
- **Pre-cluster, theme-tag, or pre-categorize the output.** Pure-divergent post-dedup; downstream skills handle structure.
- **Use emoji or numeric encoding for method tags.** Plain bracketed text (`[SM]`, `[PrM]`, `[OI]`, multi-source combos like `[OI+PrM+SM]`).
- **Write to Miro or any external surface.** JSON + markdown only.

## Testing

Smoke test only for v1, no formal regression harness. Reuses the Norrsken top-three from `OST-select-top-three-solutions` v2's smoke test.

```text
Pre-step (one-time fixture creation):
  Create workspace/context/ratifications.md with:
    - # Ratifications heading
    - One-paragraph intro
    - One ratification line for top-three-solutions-2026-05-11.json per the
      format in knowledge/discovery/top-three-selection.md (e.g.,
      "- 2026-05-11 top-three-solutions-2026-05-11.json ratified by Norrsken
      trio (no overrides)")
  Save and commit.

Inputs:
  workspace/context/ratifications.md
  workspace/6-top-three/top-three-solutions-2026-05-11.json
    (Norrsken; picks sol-r1-pm-1, sol-r3-pm-3, sol-r3-tl-4)
  workspace/context/chosen-opportunity.md
    (opp-5-1, licenstilldelning)
  workspace/context/product-outcome.md
  workspace/1-opportunity-val/experience-map-extracted-2026-05-09.json

Expect:
  - schema_version "0.1" in the output JSON
  - assumptions_per_solution.length == 3
  - Each entry's solution_id is in upstream picks[].id
    (sol-r1-pm-1, sol-r3-pm-3, sol-r3-tl-4)
  - No duplicate solution_id across the 3 entries
  - For each per-solution entry, 6 <= assumptions.length <= 18
  - All assumption.id values unique, match
    ^asm-sol-r[123]-(pm|ux|tl)-[1-9][0-9]*-\d{3}$
  - All source_methods arrays length 1-3, values from
    {storymap, pre-mortem, outcome-impact}, no duplicates within array
  - chosen_opportunity.id == "opp-5-1", phase_id == "fas-5", quote and source
    verbatim from chosen-opportunity.md
  - All carried fields (solution_title, solution_description, generating_role,
    round_number) byte-identical to upstream
  - generation_summary is the fixed v0.1 block
  - Markdown frontmatter present with blank line before closing ---
  - Three "## Solution N: <title>" sections
  - Each assumption in markdown shows [<methods-tag>] between id and text
  - No em-dash anywhere
  - No "Cites:" line, no "Trio HITL" banner

Eyeball checks (manual):
  - Each method (storymap, pre-mortem, outcome-impact) appears at least once
    as a single-source method in the deduped output (signals that the 3
    methods are surfacing different content, not all collapsing)
  - Multi-source entries appear (signals that some assumptions are genuinely
    triangulated across methods)
  - Assumptions are 1-2 sentences and falsifiable in principle
  - Storymap-tagged assumptions reference user-flow elements (steps,
    transitions, decisions); pre-mortem-tagged reference failure modes;
    outcome-impact-tagged reference the outcome metric
  - Output language matches the upstream solution-description language
    (typically Swedish for this trio)
  - No category vocabulary in assumption text (desirability, usability,
    feasibility, viability, risk, risky - those are assist 10/11 territory)
  - No effort vocabulary in assumption text (complex, expensive, feasible,
    quick win - carried from the Torres no-effort rule)
```

If `assumptions_per_solution.length` is not 3, any per-solution count is outside `6..18`, ids drift from the regex, `source_methods` values are out of enum, or the markdown is malformed in any other way, the prompt is wrong. A formal regression harness is overkill for v1.

What the smoke test does NOT exercise (parked as open follow-ups):

- Configurable count per method-pass.
- Configurable method set or solution count.
- Per-team experience-map override (the smoke test uses the latest by date).
- Edge case where a sub-agent returns 0 assumptions (hard-exit fires).
- Edge case where the dedup-pass collapses all 18 to 6 or leaves all 18 untouched (hard floor/ceiling fires).
- Trio re-ratifying after editing the top-three proposal (the ratification line format is unchanged; the smoke test uses the AI's untouched picks).
- Multi-ratification scenarios where `ratifications.md` has multiple `top-three-solutions-*.json` entries (skill takes the latest per the reading rule).

These gaps in test coverage are accepted for v1; they go on the open-follow-ups list.

## Open follow-ups

These are added to `TODO.md` rather than blocking v1.

1. **Configurable count per method-pass.** v1 locks 6. If trios consistently want different sizing (4 to reduce noise, 8 to widen the net), surface via config.
2. **Configurable method set.** v1 fixes storymap / pre-mortem / outcome-impact. Future workshops may add methods (e.g., "5 whys", "competitor-flow walkthrough"). Make extensible.
3. **Configurable solution count.** v1 fixes 3 (mirrors upstream selector). If the selector becomes configurable in v0.3 (its own open follow-up), this skill should match.
4. **Cross-solution `shared_with` marking.** Deliberately deferred. Re-open if trios report that shared bets across solutions are valuable to surface here rather than in risk-mapping.
5. **Per-team experience-map source override.** v1 reads the latest extracted by date. If a trio runs multiple extractions and wants a specific version, surface via config.
6. **Dedup-pass quality bar.** If smoke-test trios report that dedup over-merges (collapses distinct assumptions) or under-merges (preserves obvious dups), tune the prompt or add a count-distribution sanity check.
7. **Effort-vocabulary blocklist post-pass.** Eyeball-only at smoke test. Carried as a candidate from `OST-select-top-three-solutions`' open follow-ups.
8. **Category-vocabulary blocklist post-pass.** Same shape. If sub-agents start writing "this is a feasibility assumption" instead of stating the assumption, that creeps into assist 10's territory.
9. **Method-grouped rendering option.** v1 renders flat with method tags. If trios prefer separate sections per method (closer to the workshop wall layout), surface as a flavor.
10. **Optional `category` pre-tag from sub-agents.** v1 keeps categorization in assist 10. If pipeline timing suggests pre-tagging here is cheaper, evaluate the coupling cost.
11. **Schema evolution beyond v0.1.** Procedure same as `solution-brainstorm`: add an Evolution entry to `assumption-generation.md` and bump `schema_version` in the skill prompt.
12. **Storymap experience-map over-anchoring.** v1 passes the experience map with a "future flow, not today" instruction. If smoke test shows sub-agents drifting back to today's flow, tighten the prompt or drop the input entirely.

## What this skill establishes for the workshop-3 series

- **Multi-method sub-agent orchestration precedent.** First skill in the series that spawns sub-agents grouped by method x target rather than role-only. Pattern transfers to any future skill that triangulates a single artifact through multiple lenses.
- **Per-solution LLM dedup-pass precedent.** First skill that runs an LLM dedup-pass as a structural orchestration step (not just prompt-only anti-dup). Pattern transfers to any future skill where multiple blind passes produce overlapping output.
- **Source-method attribution as triangulation signal.** First skill where the number of sources surfacing an item is exposed as data (`source_methods` array length). Future "evidence aggregation" skills can follow the same shape.
- **Ratification-flag pattern as consumer.** First skill that READS from `workspace/context/ratifications.md` to locate its upstream artifact (rather than reading a fixed path). Establishes the consumer side of the pattern that `OST-select-top-three-solutions` v2 introduced on the producer side.
