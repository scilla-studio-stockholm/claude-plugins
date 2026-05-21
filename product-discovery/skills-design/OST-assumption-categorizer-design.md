---
title: "OST-assumption-categorizer: design spec"
date: 2026-05-12
purpose: Locked design for assist 10 in opportunity-solution-tree-agents.md - takes the deduped per-solution assumption list from OST-generate-assumptions (assist 9), runs a single classification LLM pass against the 5-category Cagan taxonomy in ../knowledge/discovery/assumption-types.md, and writes paired JSON + markdown with each assumption tagged with exactly one category. Identity-mapping over upstream assumptions (no reorder, no add, no drop, no re-wording). Input to assist 11 (OST-riskiest-assumptions). Input to the implementation plan.
tags: [skill-design, ost, assumption-categorization, schema-v0.1]

---

# OST-assumption-categorizer: design spec

This is the locked design for **assist 10** in `opportunity-solution-tree-agents.md`. It is the tenth skill built and the second assist in **phase 3 (assumption testing)**. Upstream is assist 9 (`OST-generate-assumptions`), which produces the deduped per-solution assumption lists with source-method attribution. Downstream is assist 11 (`OST-riskiest-assumptions`), where the phase-3 trio gate sits. There is no ratification step between assists 9 and 10. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when categorizing the deduped assumptions for the top 3 solutions into Cagan's five product-risk categories, output a paired JSON + markdown rendering with each assumption tagged in exactly one category. Input to assist 11 (OST-riskiest-assumptions).

Input is the latest `assumptions-*.json` in `workspace/7-assumptions/` by date in filename (assist 9's output). Output is two files in `workspace/8-assumptions-categorized/` with the same root name: a categorized JSON conforming to schema v0.1 in a new knowledge anchor `../knowledge/discovery/assumption-categorization.md`, and a markdown rendering generated deterministically from the JSON.

The orchestration is a **single LLM classification pass** over the full flat list of assumptions (all three solutions concatenated). Per-assumption classification against a locked 5-category taxonomy is a bounded transformation that does not benefit from sub-agent diversification - the taxonomy is the same lens for every assumption, and a single pass keeps classification consistent across solutions. The skill enforces strict **identity-mapping** over the upstream assumptions: every upstream assumption.id, text, and source_methods array carries through byte-identical; the skill adds exactly one `category` field per assumption and nothing else.

## Scope decisions (locked 2026-05-12)

The four open questions in `opportunity-solution-tree-agents.md` (lines 639-644) are narrowed below, plus several mechanical decisions. Each decision resolves an open question.

| Question | Decision |
|---|---|
| Skill vs agent | **Single-pass skill, no sub-agents.** Single SKILL.md prompt at `.claude/skills/OST-assumption-categorizer/SKILL.md`. Body instructs Claude to run one LLM classification pass over the full flat list of assumptions. Mirrors the precedent set by `OST-validate-opportunities` and `OST-select-top-three-solutions` v2 - bounded transformations over a locked taxonomy. Per-assumption classification does not benefit from method-diversification (the taxonomy is one lens, not three). |
| Output shape | **Flat per-assumption rows with `[category]` tag.** Keeps row shape identical to `OST-generate-assumptions` output; adds one bracketed tag between the methods-tag and the assumption text. Smallest schema delta from assist 9 - one new field per assumption (`category`). Trio reads the same row order they reviewed upstream, just with a `[category]` tag added per row. Categories-as-containers (per-category headers per solution) was considered and rejected: explicit headers force the reader into a category-first cognitive frame that does not match how the OST-riskiest-assumptions agent (assist 11) consumes the artefact. |
| Ambiguity rule | **Single category, risk-falls rule, no rationale field.** Apply the rule from `assumption-types.md`: pick the category that describes the risk if the assumption turns out false. No `rationale` or `confidence` field in the schema. Trio can override at review by editing the JSON. Cleanest contract; matches the precedent set by `OST-generate-assumptions` (no per-item rationale). The risk-falls rule is the load-bearing decision rule that the prompt must apply mechanically. |
| 'Other'-semantics | **Reserved for non-Cagan assumptions only.** Force one of `{desirability, usability, feasibility, viability}` whenever an assumption fits even marginally. 'Other' is for assumptions that are genuinely orthogonal to Cagan's four product risks: legal, ethical, regulatory, market-timing, organizational. Keeps the four primary buckets meaningful for downstream risk-mapping. |
| Row ordering | **Preserve upstream order.** Identity-mapping over upstream `assumptions[]`. No re-ordering by category, no triangulation-strength-desc sort. Trio sees the same order assist 9 produced. Easiest invariant to enforce (length-equality plus id-equality at each index). |
| Input source pattern | **Latest-by-date, no ratification gate.** Read latest `assumptions-*.json` from `workspace/7-assumptions/` by date in filename. Per the locked phase-3 HITL design in `OST-generate-assumptions-design.md`, the trio gate for phase 3 is downstream at assist 11; no ratification between 9 and 10. |
| Schema home | **New `../knowledge/discovery/assumption-categorization.md`.** Per the per-assist precedent (every prior assist got its own anchor: `solution-brainstorm.md`, `solution-cluster.md`, `top-three-selection.md`, `assumption-generation.md`). Schema v0.1 owns the category enum, the risk-falls tiebreaker rule, the 'other'-reservation rule, the carry-forward rules, and the renderer template. |
| HITL flavor | **No in-skill HITL banner.** Phase 3 trio gate is at assist 11. Matches `OST-generate-assumptions` precedent. |
| Output location | `workspace/8-assumptions-categorized/`. Stage-numbered convention continuing the `1-` through `7-` subdirs. |
| Output filename | `assumptions-categorized-<YYYY-MM-DD>.{json,md}` per cross-cutting datakontrakt. |
| Output format | Paired JSON + markdown. JSON is the contract for assist 11; markdown is for trio eyeballing if they want to peek before risk-mapping. |
| Slug name | `OST-assumption-categorizer`. Noun-form matches the spec section title ("Assumption categorizer"); deviates from the verb-first pattern used by `OST-generate-assumptions`, `OST-validate-opportunities`, etc. Justification: the spec name is well-known to the trio and noun-form reads naturally with the slash-command pattern (`/OST-assumption-categorizer`). |
| Body language | English, matching all skill-body precedent (per the `project_skill_bodies_english` memory). Input and output prose may be Swedish (the trio's working language); the skill body and the new knowledge anchor are English so the skill is reusable across teams. |
| Tools | `Read`. No sub-agents, no Write tool needed beyond the orchestrator's normal output-file writes. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-assumption-categorizer/SKILL.md` |
| Skill name | `OST-assumption-categorizer` |
| Slash-command (optional) | `/OST-assumption-categorizer` if frequency justifies it |
| Body language | English |
| Tools | `Read` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when categorizing the deduped assumptions for the top 3 solutions into Cagan's five product-risk categories, output a paired JSON + markdown rendering with each assumption tagged in exactly one category. Input to assist 11 (OST-riskiest-assumptions).

This follows the "for X, when Y, output Z" pattern. Generic and company-agnostic. Distinct from `OST-generate-assumptions` (produces the deduped list but does not classify), from `OST-riskiest-assumptions` (scores importance and evidence on the categorized list, but does not categorize), and from `OST-validate-opportunities` (different domain: opportunity citation format, not assumption taxonomy).

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/7-assumptions/assumptions-<latest-date>.json` | `OST-generate-assumptions` (assist 9) v0.1 | The deduped per-solution assumption lists to classify, plus all carried top-level fields |

**File-resolution rule:** latest `assumptions-*.json` in `workspace/7-assumptions/` by date in filename, descending. If a trio wants to categorize an older version, they pass the filename explicitly at invocation time (v0.2 follow-up; v1 reads latest only).

That is the only input. The skill does NOT read:

- `workspace/context/ratifications.md` - no ratification gate between assists 9 and 10.
- `workspace/context/chosen-opportunity.md` or `product-outcome.md` - categorization is per-assumption against the locked taxonomy; chosen-opp and outcome are not needed for the risk-falls rule. Identifying context carries through byte-identical from the upstream JSON.
- The experience map - categorization is structural, not journey-anchored.
- Interview transcripts, OST-brainstorm-solutions output, top-three-solutions output, or comparison matrix.
- Role anchors (`role-product-manager.md` etc.). Role information carries as the role abbreviation only; no role-lens shaping of categorization.

**Knowledge anchors read at runtime:**

- **`../knowledge/discovery/assumption-categorization.md`** (NEW, created as part of this build) - owns the schema, the category enum, the risk-falls tiebreaker rule, the 'other'-reservation rule, the carry-forward rules, and the renderer template.
- **`../knowledge/discovery/assumption-types.md`** - the 5-category taxonomy with definitions and examples. Read in full; the prompt instructs the LLM to apply the "Definition" and "Application notes" sections per category to every assumption.
- **`../knowledge/foundations/product-operating-model-marty-cagan.md`** - Cagan five-product-risks framing that anchors the taxonomy. Read as reference for the conceptual grounding.
- **`../knowledge/discovery/assumption-generation.md`** - the upstream schema (v0.1) so the skill can parse the input JSON cleanly without ambiguity.

Per the cross-cutting datakontrakt, anchors are read at runtime rather than hard-coded into the prompt.

## The new knowledge anchor: `../knowledge/discovery/assumption-categorization.md`

This anchor carries the same role for the categorizer that `assumption-generation.md` carries for the generator: it owns the schema, the category enum, the risk-falls tiebreaker rule, the 'other'-reservation rule, the carry-forward rules, and the renderer template. Created as a one-time write during this skill's build; not modified at runtime.

**Sections in the anchor:**

1. **What the categorizer does** - short framework prose tying it to Cagan's five product risks and Torres' assumption-testing arc. Notes that the categorizer consumes a deduped per-solution assumption list with source-method attribution and produces the same list with one category tag added per assumption; risk-mapping is downstream.
2. **The category enum** - the five values (`desirability`, `usability`, `feasibility`, `viability`, `other`) with one-line definitions cross-linking to the full definitions in `assumption-types.md`.
3. **The risk-falls rule** - pick the category that describes the risk if the assumption turns out false. Verbatim wording for the prompt to apply mechanically.
4. **The 'other'-reservation rule** - force one of the four Cagan categories whenever an assumption fits even marginally; reserve 'other' for legal, ethical, regulatory, market-timing, organizational, or otherwise orthogonal assumptions.
5. **Carry-forward rules** - every upstream field stays byte-identical; the skill adds exactly one `category` field per assumption and nothing else.
6. **Identity-mapping invariants** - assumption count, ordering, and id-equality at each index.
7. **JSON schema (v0.1)** - the contract.
8. **Field notes** - per-field commentary including the missing-optional convention and the enum semantics.
9. **Renderer template** - the deterministic markdown template.
10. **Open questions** - what is punted to v0.2.
11. **Evolution** - version history.

**Schema v0.1:**

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

**Schema design notes:**

- `assumptions_per_solution[]` is fixed-length-3, in the same order as upstream `pick_position` (1, 2, 3).
- Every upstream field (`solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number`, `assumption.id`, `assumption.text`, `assumption.source_methods`) carries through byte-identical. The skill is an identity map on upstream data plus a single new `category` field per assumption.
- `assumption.category` is exactly one value from the fixed enum. Never an array. Never null.
- No `rationale`, `confidence`, or `alt_categories` field. Locked at v0.1; surfacing ambiguity as data is a v0.2 follow-up if trios report mis-classifications.
- No `risk_level`, `importance`, or `evidence` field. Those are assist 11's territory.
- No `shared_with` field. Per-solution structure only, mirrors upstream.
- `categorization_summary` is a fixed-shape sanity block. v0.1 values are locked.

**Schema invariants** (skill enforces; hard-exit on violation, no partial writes):

- `schema_version == "0.1"`.
- `assumptions_per_solution.length == 3`.
- For each per-solution entry, `assumptions.length` equals the corresponding upstream per-solution entry's `assumptions.length`.
- For each per-solution entry, the upstream `assumptions[]` ids appear in the output in the same order (identity-mapping at each index).
- Every `assumption.category` is in `{desirability, usability, feasibility, viability, other}`.
- Every upstream field is byte-identical to the source JSON (`team`, `title`, `product_outcome`, `chosen_opportunity.*`, `source_top_three_solutions`, `source_experience_map`, plus all per-solution and per-assumption carried fields).
- `categorization_summary.total_assumptions` equals the sum of `assumptions[].length` across the three solutions.
- `categorization_summary` is the fixed v0.1 block.

## Steps

The skill follows the same numbered-step pattern as `OST-validate-opportunities` and `OST-generate-assumptions`. Single orchestrator pass; one LLM classification call nested inside step 5.

1. **Read knowledge anchors:** `assumption-categorization.md` (new), `assumption-types.md` (full taxonomy), `product-operating-model-marty-cagan.md` (Cagan framing), `assumption-generation.md` (upstream schema).

2. **Locate input:** latest `workspace/7-assumptions/assumptions-*.json` by date in filename, descending.

3. **Hard-exit checks** (see Error handling). Do not write any output files when these fire.

4. **Parse input.** Extract `assumptions_per_solution[]` plus all top-level carried fields. Build an index of all upstream assumptions keyed by `assumption.id` for later merge.

5. **Classification LLM pass.** One single LLM call. Prompt includes:

   - The full 5-category taxonomy from `assumption-types.md` (verbatim "Definition" and "Application notes" sections per category).
   - The risk-falls rule from `assumption-categorization.md` (verbatim).
   - The 'other'-reservation rule (verbatim).
   - The full flat list of all assumptions, concatenated across all three solutions. Each assumption rendered as `<solution_id> :: <assumption.id> :: <text>` so the response can re-associate by id alone.
   - Task: "For each assumption, return a JSON object `{id, category}`. Use exactly one category from the enum `{desirability, usability, feasibility, viability, other}`. Apply the risk-falls rule for ambiguous cases: pick the category describing the risk if the assumption turns out false. Reserve 'other' for assumptions outside Cagan's four risks (legal, ethical, regulatory, market-timing, organizational). Return a JSON array of objects in the same order as the input."

   Single pass over all assumptions (typically 30-42 total post-dedup). No per-solution split - one LLM call sees the full set so the taxonomy is applied consistently across solutions.

6. **Merge classification back into the upstream structure.** Index the classification response by `id`. For each upstream assumption, look up the corresponding classification entry and add the `category` field to a copy of the upstream object. Every other field is carried byte-identical. If any upstream assumption id is missing from the classification response, hard-exit. If the classification response contains an id not in the upstream input, hard-exit. If the classification response contains a duplicate id, hard-exit.

7. **Compose the v0.1 JSON.** Top-level fields per the schema. `assumptions_per_solution[]` ordered by upstream `pick_position` (1, 2, 3). Within each per-solution entry, `assumptions[]` in upstream order. Compute `categorization_summary.total_assumptions` as the summed length. Always write `categorization_summary` as the fixed v0.1 block.

8. **Validate invariants.** Hard-exit on any violation.

9. **Render the markdown deterministically** from the JSON via the embedded template (Output composition).

10. **Write paired output** to:
    - `workspace/8-assumptions-categorized/assumptions-categorized-<YYYY-MM-DD>.json`
    - `workspace/8-assumptions-categorized/assumptions-categorized-<YYYY-MM-DD>.md`

    Use today's date in `YYYY-MM-DD`. Same root name on both files. Create `workspace/8-assumptions-categorized/` if it does not exist. The skill does NOT modify any input files; the upstream `assumptions-*.json` stays immutable.

One pass through one LLM classification call plus a deterministic merge. No retries beyond what the single Agent call inherently does; if classification output is malformed or violates an invariant, the skill hard-exits rather than re-running.

## Output composition

Two files with the same root name:

```text
workspace/8-assumptions-categorized/assumptions-categorized-<YYYY-MM-DD>.json
workspace/8-assumptions-categorized/assumptions-categorized-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.1 from `../knowledge/discovery/assumption-categorization.md`. No extra fields beyond the schema.

**The markdown** is generated deterministically from the JSON via an embedded template in the prompt:

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
Source chosen opportunity: `workspace/context/chosen-opportunity.md`
Source product outcome: `workspace/context/product-outcome.md`
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

**Rendering rules:**

- **Role-abbreviation mapping** (carried from assist 9): `product-manager` -> `PM`, `ux-designer` -> `UX`, `tech-lead` -> `TL`. Rendered in the solution header line as `[<role-abbrev>, R<round_number>]`.
- **Method-tag mapping** (carried from assist 9): `storymap` -> `SM`, `pre-mortem` -> `PrM`, `outcome-impact` -> `OI`. Multi-source combined alphabetically with `+`. Examples: `[OI+SM]`, `[PrM+SM]`, `[OI+PrM+SM]`.
- **Category-tag** rendered lowercase verbatim in brackets after the method tag: `[desirability]`, `[usability]`, `[feasibility]`, `[viability]`, `[other]`. No abbreviations - full words read more clearly when the trio scans the markdown.
- **Tag order per row** is fixed: `[<methods-tag>] [<category>]`, in that order. The asm-id is bold-prefixed; tags follow; text follows.
- **Source attribution** in the chosen-opportunity line carried verbatim. Separated from the quote by ` - ` (regular dash).
- **No em-dash** anywhere; uniform across Swedish and English prose.
- **Frontmatter** complies with the project rule (blank line before closing `---`).
- **No HITL banner.** Phase 3 trio gate is at assist 11 (OST-riskiest-assumptions); this skill's output goes to the risk-mapping agent.
- **Output language for prose** (`assumption.text`) carries through from upstream verbatim (typically Swedish for this trio's work). Schema field names, JSON key strings, category enum values, method enum values, role enum values, and id strings stay as defined in English.
- **Section order is fixed** and the AI does not insert ad-hoc sections.
- **No `Cites:` line.** Categorization is a classification operation, not an evidence-traced one.
- **Pick ordering** in the markdown mirrors the upstream `picks[]` array order (which mirrors the selector's confidence ordering).
- **Row ordering within each solution** preserves the upstream `assumptions[]` order. No re-sort by category or triangulation.

## Knowledge-doc updates required before ship

As part of building this skill:

- **Create `../knowledge/discovery/assumption-categorization.md`** (the new anchor). Sections per "The new knowledge anchor" above. This is the canonical source for the schema, the category enum, the risk-falls rule, the 'other'-reservation rule, the carry-forward rules, and the renderer template.
- **Update `skills-design/skill-template.md` Bygg-status** - mark `OST-assumption-categorizer` as built. Final task in the implementation plan, not in this design.
- **Update `skills-design/opportunity-solution-tree-agents.md`** - replace the four open design questions in section 10 (lines 639-644) with a reference to the locked decisions in `skills-design/OST-assumption-categorizer-design.md`. Update the "Föreslagen typ: Skill" line is already correct - no change needed there.

What is NOT updated:

- `../knowledge/discovery/assumption-types.md` - read as reference; the taxonomy stays as the canonical source. Untouched.
- `../knowledge/foundations/product-operating-model-marty-cagan.md` - referenced but not extended.
- `../knowledge/discovery/assumption-generation.md` - read for upstream schema; no changes.
- `workspace/README.md` - the staging-dir-documentation follow-up is the same TODO already opened by upstream skills; `workspace/8-assumptions-categorized/` adds another data point but is not a separate update here.

## Error handling

**Hard-exit triggers** (no output files written when these fire):

| Trigger | Looked for | Remedy |
|---|---|---|
| No `assumptions-*.json` in `workspace/7-assumptions/` | At least one `assumptions-<YYYY-MM-DD>.json` file | Run `OST-generate-assumptions` (assist 9) first |
| Source JSON does not parse | Valid JSON conforming to `assumption-generation.md` v0.1 | Re-run `OST-generate-assumptions` |
| Source JSON `schema_version` is not `"0.1"` | The exact string `"0.1"` | Re-run `OST-generate-assumptions` against v0.1 |
| Source `assumptions_per_solution.length != 3` | 3 entries (one per pick) | Re-run `OST-generate-assumptions` |
| Any per-solution `assumptions[]` length outside `6..18` | Per-solution count within the v0.1 invariant range | Re-run `OST-generate-assumptions` |
| Any knowledge anchor missing (`assumption-categorization.md`, `assumption-types.md`, `product-operating-model-marty-cagan.md`, `assumption-generation.md`) | All four files at fixed paths | Restore from git |
| Classification LLM pass returned malformed JSON | A JSON array of `{id, category}` objects | Re-run; if persistent, the prompt's JSON instruction needs tightening |
| Classification omits an upstream `assumption.id` | Every upstream id in the response | Re-run; if persistent, the prompt needs to emphasize exhaustive coverage |
| Classification contains an `id` not in the upstream input | Every response id is in the upstream input | Re-run |
| Classification contains a duplicate `id` | No duplicate ids | Re-run |
| Classification `category` value outside the enum | One of `{desirability, usability, feasibility, viability, other}` | Re-run; if persistent, the enum constraint in the prompt needs tightening |
| Identity-mapping violation (any upstream field changed in the output) | All upstream fields byte-identical | Re-run; if persistent, the merge logic has drifted |
| `categorization_summary.total_assumptions` does not match summed counts | Sum equals total | Re-run |
| Final-JSON invariant violation (any of the schema invariants above) | Schema invariants | Re-run |

**Hard-exit message format** (same shape as `OST-generate-assumptions` and upstream skills):

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

Three pieces in order: what failed, what the skill saw, what to do about it. No silent degradation. No retries beyond the implicit retry inside any single Agent tool call.

**Soft warnings:** None for v1. The OST-riskiest-assumptions agent (assist 11) is the next gate; any distribution oddities (e.g., 100% feasibility, high 'other') are eyeball-only at v1 smoke test and parked as v0.2 follow-ups.

**Convention for missing optional fields in JSON:** v0.1 has no optional fields. `null` is never written.

**No JSON self-validation pass.** Trust the prompt and the invariant check; downstream skills surface any malformed JSON. Mirrors the precedent set by `OST-extract-experience-map`, `OST-cluster-opportunities`, `OST-compare-opportunities`, `OST-select-opportunity`, `OST-brainstorm-solutions`, `OST-select-top-three-solutions`, and `OST-generate-assumptions`.

## What this skill does NOT do

- **Read interview transcripts.** Categorization is structural, not evidence-traced.
- **Read the OST-brainstorm-solutions output, comparison matrix, validated opportunities, OST-cluster-solutions output, top-three-solutions output directly, or the clustered experience map.** Only the upstream `assumptions-*.json` contract listed in Inputs.
- **Read `chosen-opportunity.md`, `product-outcome.md`, or the experience map.** Identifying context carries through byte-identical from the upstream JSON.
- **Read `ratifications.md`.** No ratification gate between assists 9 and 10.
- **Read the role anchors (`role-product-manager.md` etc.).** Role information is carried as the role abbreviation only; no role-lens shaping of categorization.
- **Generate, modify, merge, or drop assumptions.** Identity-mapping over upstream `assumptions[]` is the core invariant; every upstream assumption appears exactly once in the output with one `category` added.
- **Re-order assumptions.** Row order preserves upstream.
- **Score, rank, or flag assumptions as riskiest.** That is assist 11.
- **Apply importance, evidence, or risk-level scoring.** That is assist 11.
- **Generate test cards, validation plans, or experiment designs.** Out of scope; future assist 12.
- **Apply cross-solution analysis or mark shared assumptions.** Per-solution structure only.
- **Modify upstream files.** The `assumptions-*.json`, `chosen-opportunity.md`, `product-outcome.md`, and experience map all stay immutable.
- **Write to `workspace/context/`.** Output lives in `workspace/8-assumptions-categorized/`.
- **Append to `ratifications.md`.** The trio ratifies downstream artifacts manually; this skill is upstream of the OST-riskiest-assumptions gate.
- **Add an in-skill HITL banner.** Trio gate is downstream at assist 11.
- **Run a JSON self-validation pass.**
- **Retry the classification pass on partial failures.** Hard-exit; operator re-runs end-to-end.
- **Use a `rationale`, `confidence`, `alt_categories`, `risk_level`, `importance`, `evidence`, or `shared_with` schema field.** All either downstream territory or v0.2 follow-ups.
- **Spawn sub-agents.** Single-pass classification is the architecture.
- **Use emoji or numeric encoding for category tags.** Plain bracketed lowercase words (`[desirability]`, `[usability]`, `[feasibility]`, `[viability]`, `[other]`).
- **Default to 'other' when uncertain.** Force one of the four Cagan categories whenever an assumption fits even marginally.
- **Configure the category enum, the input source, the output location, or per-team overrides.** All locked at v1.
- **Group assumptions by category in markdown.** Flat row order preserves upstream; category surfaces as a per-row bracketed tag.
- **Write to Miro or any external surface.** JSON + markdown only.

## Testing

Smoke test only for v1, no formal regression harness. Reuses the Norrsken assumptions output from `OST-generate-assumptions`' smoke test.

```text
Inputs:
  workspace/7-assumptions/assumptions-<latest-date>.json
    (Norrsken; ~30-42 deduped assumptions across 3 picks)

Expect:
  - schema_version "0.1" in the output JSON
  - assumptions_per_solution.length == 3
  - Identity-mapping: every assumption.id, text, source_methods byte-identical
    to upstream
  - For each per-solution entry, assumptions[].length equals upstream length
    AND ids appear in the same order at each index
  - Every assumption.category in {desirability, usability, feasibility,
    viability, other}; exactly one value; never null
  - chosen_opportunity carried byte-identical (id, phase_id, quote, source)
  - All other carried top-level fields byte-identical (team, title,
    product_outcome, source_top_three_solutions, source_experience_map)
  - categorization_summary is the fixed v0.1 block with total_assumptions
    matching the summed counts
  - Markdown frontmatter present with blank line before closing ---
  - Three "## Solution N: <title>" sections
  - Each assumption row shows [<methods-tag>] [<category>] in that order
  - Categories rendered lowercase verbatim (desirability, usability, etc.)
  - No em-dash anywhere
  - No "Cites:" line, no HITL banner

Eyeball checks (manual):
  - Distribution across the five categories is plausible (not 100% in one
    category, not heavily skewed to 'other')
  - 'Other' bucket contains only genuinely-non-Cagan assumptions (legal,
    ethical, regulatory, market-timing, organizational) if anything;
    empty is acceptable
  - Categorization is consistent across similar assumptions across the three
    solutions (e.g., two assumptions about a UI control both map to
    usability, not one to usability and one to feasibility)
  - Risk-falls rule visibly applied: assumptions whose failure would cause
    user rejection map to desirability; whose failure would cause inability
    to deliver map to feasibility; etc.
  - No category drift in markdown: every row in the markdown matches the
    JSON's category for the same id
```

If `assumptions_per_solution.length` is not 3, identity-mapping is violated, category values drift from the enum, the markdown is malformed in any other way, or the response misses upstream ids, the prompt is wrong. A formal regression harness is overkill for v1.

What the smoke test does NOT exercise (parked as open follow-ups):

- Edge case: all assumptions classified into a single category (signals taxonomy mis-calibration or trivial input).
- Edge case: high 'other' count (>20%, signals risk-falls rule needs tightening or the 'other'-reservation prompt instruction needs reinforcement).
- Edge case: classification pass returning a partial response (less than the upstream assumption count) - hard-exit fires, but the operator experience hasn't been smoke-tested.
- Multi-pass classification for consistency (single pass is v1).
- Configurable category enum (locked to Cagan-five for v1).
- Per-team taxonomy overrides.
- Explicit-filename input mode (v1 reads latest by date; passing an older filename is a v0.2 follow-up).

These gaps in test coverage are accepted for v1; they go on the open-follow-ups list.

## Open follow-ups

These are added to `TODO.md` rather than blocking v1.

1. **Per-category count sanity check.** If smoke-test trios report distributions that look off (one category dominates >70%, or 'other' exceeds 20%), add a soft-warning pass that surfaces the distribution to the operator. v1 is eyeball-only.
2. **Per-solution classification consistency check.** Surface cases where similar assumption text in two different solutions maps to two different categories. Helps trio sanity-check the LLM. v1 is eyeball-only.
3. **Optional `confidence` field.** If trios report that the binary "this category, no ambiguity" framing loses signal on close calls, surface a per-assumption confidence indicator. Parked.
4. **Optional `alt_categories` array.** Same shape as the rejected option in the brainstorm. Re-open if trios consistently report that the single-category-with-no-rationale contract is too thin. Parked.
5. **Configurable category enum.** v1 locks Cagan-five. If a trio wants to use a different taxonomy (e.g., Test Card-derived risk categories from Bland), surface via config.
6. **Explicit-filename input mode.** v1 reads latest `assumptions-*.json` by date. If a trio wants to re-categorize an older version, add an optional filename parameter.
7. **Schema evolution beyond v0.1.** Procedure same as `solution-brainstorm` and `assumption-generation`: add an Evolution entry to `assumption-categorization.md` and bump `schema_version` in the skill prompt.
8. **Category-grouped rendering option.** The rejected "categories-as-containers" shape (per-category headers within each solution) could be surfaced as a flavor flag if trios prefer that layout for discovery boards.
9. **Effort-vocabulary blocklist post-pass.** Carried from upstream skills' open follow-ups. Eyeball-only at smoke test.
10. **Risk-vocabulary blocklist post-pass.** If sub-agents start writing "this is a high-risk assumption" or "this is the riskiest one" in the input text and that creeps in through the carry-forward (it shouldn't, the text field is byte-identical), surface as a v0.2 check.

## What this skill establishes for the discovery series

- **Identity-mapping precedent.** First skill in the series that strictly preserves every upstream field byte-identical and adds exactly one new field per item. Pattern transfers to any future skill that enriches an existing artifact without restructuring it.
- **Single-pass classification against a locked taxonomy.** First post-brainstorm skill that uses a single LLM pass with no sub-agents and no dedup. Pattern transfers to any future "apply a taxonomy" skill where diversification doesn't help.
- **Latest-by-date input pattern between intermediate phase assists.** First skill that consumes upstream without a ratification gate, because the phase gate is downstream. Establishes the consumer-side pattern for any future intermediate-phase skill (e.g., assist 11 will use the same pattern to consume this skill's output).
- **Carry-forward as a structural contract.** First skill where the JSON schema explicitly distinguishes "carried byte-identical" fields from "new" fields. Pattern transfers to any future skill that enriches rather than transforms.
