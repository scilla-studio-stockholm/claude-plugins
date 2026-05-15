---
title: "OST-cluster-solutions: design spec"
date: 2026-05-11
purpose: Locked design for assist 7 in opportunity-solution-tree-agents.md - takes the 18 paired JSON+markdown solution candidates from OST-brainstorm-solutions (assist 6) plus chosen-opportunity and product-outcome context, runs a single-pass LLM clustering call to group candidates into 3-5 thematic clusters with full member embed and LLM-generated title + summary per cluster, and produces a paired JSON + markdown clustered solution map conforming to a new schema v0.1 in ../knowledge/discovery/solution-cluster.md. Input to the implementation plan.
tags: [skill-design, workshop-3, ost, solution-clustering, schema-v0.1]

---

# OST-cluster-solutions: design spec

This is the locked design for **assist 7** in `opportunity-solution-tree-agents.md`. It is the seventh skill built in the workshop 3 series, after `OST-opportunity-extractor`, `OST-validate-opportunities`, `OST-extract-experience-map`, `OST-cluster-opportunities`, `OST-compare-opportunities`, `OST-select-opportunity`, and `OST-brainstorm-solutions`. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when grouping 18 divergent solution candidates from a brainstorm pass into 3-5 thematic clusters so duplicates collapse and unique ideas surface, output a paired JSON + markdown clustered solution map. Each cluster has a title, a 2-4 sentence summary, and a full embed of its member solutions (id, title, generating role, round, description). Input to assist 8 (top-3 selector).

Input is the v0.1 solution-candidates JSON from `OST-brainstorm-solutions` and the trio's chosen-opportunity + product-outcome context. Output is two files in `workspace/5-solution-cluster/` with the same root name: a clustered-solutions JSON conforming to schema v0.1 in a new knowledge anchor `../knowledge/discovery/solution-cluster.md`, and a markdown rendering generated deterministically from the JSON.

The skill produces a **proposal**, not a decision-of-record. Assist 8 (top-3 selector) consumes the cluster map; the trio reviews assist 8's top-3 proposal, not this intermediate cluster map. The clusterer itself does not write to `workspace/context/`.

## Scope decisions (locked 2026-05-11)

The brainstorm resolved four open questions from `opportunity-solution-tree-agents.md` (lines 519-524) and added several mechanical decisions.

| Question | Decision |
|---|---|
| Cluster count | **Target range 3-5, material-driven.** Soft target. If the 18 candidates genuinely split into 2 or 6-7 themes, the skill allows it and emits a `notes` field naming the reason. The target bounds output for assist 8 (top-3 selector) while letting real structure drive shape. |
| Member representation | **Full embed.** Each cluster's `members[]` carries the full source record per member: id, title, generating_role, round_number, description. Cluster file is self-contained; assist 8 needs no join against the source candidates file. |
| Build-on relationships | **Ignore in v1.** Sol-r2-pm-2's "Bygger på sol-r1-pm-5" prose stays in the description verbatim. No structural `build_on` field on member objects. Reverses to a v0.2 candidate if assist 8 reports needing structured chains. Preserves the brainstormer's prompt-only anti-dup decision. |
| Outliers | **Single-member cluster allowed.** A genuinely unique solution gets its own cluster of one member. No separate `cluster-0-outliers` bucket. The asymmetry of the brainstormer's `fas-0-unphased` (where phases are pre-given) does not apply here: clusters are discovered from data, not measured against a fixed taxonomy. |
| Skill vs Agent | **Plain skill, single-pass.** One LLM call over all 18 candidates. No sub-agents, no retry loop, no tool-use beyond Read. Same shape as `OST-select-opportunity` and `OST-compare-opportunities`. |
| Clustering axis | **Free-form by theme.** Prompt says "group by theme/similarity"; LLM picks dimensions that the material carries (mechanism, target user, system surface, intervention type, etc.). No fixed primary axis. |
| Cluster ordering | **By member count descending; tiebreak first-appearing member id.** Signals which themes dominated the brainstorm. Cluster ids `c1, c2, ...` assigned post-sort. |
| Member ordering within cluster | **Lead-idea first, then round ascending, then role (PM, UX, TL).** Soft convention in the prompt; not a hard invariant. |
| HITL flow | **AI-driven HITL** per the steg 6-8 pattern in the workshop-3 cross-cutting decisions. Trio reviews at the top-3 stage (assist 8), not at this intermediate clusterer stage. |
| Schema location | **New knowledge anchor `../knowledge/discovery/solution-cluster.md` v0.1.** Per the cross-cutting datakontrakt; mirrors `opportunity-comparison.md`, `opportunity-selection.md`, `solution-brainstorm.md`. |
| Body language | **English.** Matches `OST-validate-opportunities`, `OST-extract-experience-map`, `OST-cluster-opportunities`, `OST-compare-opportunities`, `OST-select-opportunity`, `OST-brainstorm-solutions`. |
| Output location | `workspace/5-solution-cluster/` (created lazily if absent). Stage-numbered convention continuing `1-opportunity-val/`, `2-opportunity-compare/`, `3-opportunity-select/`, `4-solution-brainstorm/`. The workspace-folder-convention follow-up TODO opened by `OST-compare-opportunities` / `OST-select-opportunity` / `OST-brainstorm-solutions` was closed 2026-05-11. |
| Output filename | `clustered-solutions-<YYYY-MM-DD>.{json,md}` per cross-cutting datakontrakt. |
| Output format | Paired JSON + markdown. JSON gives assist 8 a parseable contract; markdown is the human review surface for sanity-check before assist 8. |
| Cross-check chosen-opp id | **Skill enforces at this layer.** Source candidates JSON carries a `chosen_opportunity.id`. `workspace/context/chosen-opportunity.md` carries the trio-ratified id in its bold-id row. The clusterer compares both and hard-exits on mismatch. This catches a mismatch downstream of `OST-brainstorm-solutions`; the same check should also be added to the brainstormer to fail earlier (the original TODO item remains open for that). |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-cluster-solutions/SKILL.md` |
| Skill name | `OST-cluster-solutions` |
| Slash-command (optional) | `/OST-cluster-solutions` if frequency justifies it |
| Body language | English |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when grouping 18 divergent solution candidates from a brainstorm pass into 3-5 thematic clusters so duplicates collapse and unique ideas surface, output a paired JSON + markdown clustered solution map. Each cluster has a title, summary, and full embed of its member solutions. Input to assist 8 (top-3 selector).

This follows the "for X, when Y, output Z" pattern. Distinct from `OST-cluster-opportunities` (which groups opportunities against a fixed phase set from the experience map; the clusters there are pre-given). Distinct from `OST-brainstorm-solutions` (which generates candidates; doesn't structure them). Distinct from `OST-select-opportunity` (which picks one; doesn't group).

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/4-solution-brainstorm/solution-candidates-<date>.json` | `OST-brainstorm-solutions` (assist 6) | The 18 candidates to cluster (record per candidate: id, title, generating_role, round_number, description) |
| `workspace/context/chosen-opportunity.md` | Trio-ratified | Grounding context for cluster labeling; cross-check against source-JSON's chosen-opp id |
| `workspace/context/product-outcome.md` | Trio-authored, fixed path | Grounding context for cluster labeling |

**File-resolution rules:** Latest file matching `solution-candidates-*.json` in `workspace/4-solution-brainstorm/` by `<date>` in filename, descending. The context files are at fixed paths with no date suffix.

**Knowledge anchors read at runtime:**

- `../knowledge/discovery/solution-cluster.md` (NEW, created as part of this build) - the JSON schema v0.1, the four locked decisions, the clustering-axis convention, the field-notes section.
- `../knowledge/discovery/solution-brainstorm.md` - source schema (v0.1) so the clusterer can parse what `OST-brainstorm-solutions` produced.

Per the cross-cutting datakontrakt, anchors are read at runtime rather than hard-coded into the prompt.

**What the skill does NOT consume:**

- The paired markdown candidate file (`solution-candidates-<date>.md`). The JSON is the contract.
- The experience map.
- The `opportunities-extracted` or `opportunities-validated` files.
- Interview transcripts.
- The comparison matrix.
- A separate schema file. The schema lives in the new knowledge anchor.

## The new knowledge anchor: `../knowledge/discovery/solution-cluster.md`

This anchor carries the same role for the clusterer that `opportunity-selection.md` carries for the selector: it owns the schema, the four locked decisions, the clustering-axis convention, and the framework prose. Created as a one-time write during this skill's build; not modified at runtime.

**Sections in the anchor:**

1. **What the clusterer does** - short framework prose tying it to Torres CDH ch 9 "Identify hidden assumptions" preparatory step (you group candidate solutions before identifying assumptions per representative idea). Notes that the clusterer consumes the brainstormer's output and produces a proposal that assist 8 consumes.
2. **The four locked decisions** - cluster count target 3-5, full member embed, no `build_on` field in v0.1, single-member clusters allowed.
3. **The clustering-axis convention** - free-form by theme. LLM picks dimensions that the material carries. Examples of dimensions that recur (mechanism, target user, system surface, intervention type) are listed as informational, not prescriptive.
4. **The chosen-opportunity cross-check rule** - source-JSON `chosen_opportunity.id` must match the bold-id row in `workspace/context/chosen-opportunity.md`. Skill hard-exits on mismatch.
5. **JSON schema (v0.1)** - the contract (below).
6. **Field notes** - per-field commentary, including the missing-optional convention (e.g., `notes` is omitted from JSON when nothing non-standard happened, not written as `null`).
7. **Open questions** - what's punted to v0.2 (build-on parsing, cluster-axis disclosure field, weak-fit flag on members, configurable cluster-count target).
8. **Evolution** - version history.

**Schema v0.1:**

```json
{
  "schema_version": "0.1",
  "team": "string (carried from source candidates JSON)",
  "title": "string (e.g., 'Clustered solutions: <first clause of chosen opportunity quote>')",
  "product_outcome": "string (carried from source)",
  "chosen_opportunity": {
    "id": "string (carried; e.g., 'opp-5-1'; matches the bold-id row in workspace/context/chosen-opportunity.md)",
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

**Invariants** (skill enforces; hard-exit on violation, no partial writes):

- Sum of `members[]` across all clusters = exactly 18 (every source candidate appears in exactly one cluster).
- Every member `id` matches a source candidate id verbatim; no duplicates across clusters, no inventions.
- `cluster_count` equals `clusters.length`.
- Cluster ordering: by member count descending; ties broken by first-appearing member id.

**Soft conventions** (in prompt, not invariants):

- Target 3-5 clusters; if material genuinely splits outside this range, allow but populate `notes` explaining why.
- Member ordering within a cluster: lead-idea first (the member whose description most centrally expresses the cluster theme), then by round ascending, then by role (PM, UX, TL).

## Skill execution flow

One LLM call, deterministic post-processing.

1. **Resolve inputs.** Find latest `workspace/4-solution-brainstorm/solution-candidates-*.json` by date in filename, descending. Hard-exit if none found. Read `workspace/context/chosen-opportunity.md` and `workspace/context/product-outcome.md`. Read knowledge anchors `solution-cluster.md` and `solution-brainstorm.md` at runtime.
2. **Cross-check chosen-opportunity id.** Parse the bold-id row from `chosen-opportunity.md`. Compare to source-JSON's `chosen_opportunity.id`. Mismatch → hard-exit.
3. **Compose LLM prompt** with these blocks, in order:
   - Role frame: "You are clustering 18 solution candidates by theme."
   - Grounding: chosen opportunity (full record), product outcome (verbatim).
   - The 18 candidates rendered as a flat list with full records (id, title, role, round, description).
   - Schema reference: point to the knowledge anchor by path, include the v0.1 JSON skeleton inline.
   - The four locked decisions verbatim as rules (target 3-5, full embed, no build-on, single-member clusters allowed).
   - Output instruction: "Return only a single JSON object matching the schema. No prose preamble."
4. **Receive and parse JSON.** Malformed JSON → hard-exit.
5. **Validate invariants.** Member sum, unique ids, count match, ordering. Specific violation → hard-exit with the violation named.
6. **Post-sort clusters.** Reorder clusters by member-count descending (the hard invariant); ties broken by first-appearing member id. Assign `cluster_id` values `c1, c2, ...` post-sort. Member ordering within a cluster is the LLM's choice and is preserved verbatim - "lead-idea first, then round, then role" is a soft prompt convention, not a post-sort step (semantic judgement can't be reproduced structurally).
7. **Write JSON** to `workspace/5-solution-cluster/clustered-solutions-<today>.json`.
8. **Render markdown** deterministically from the JSON (template below) and write to `workspace/5-solution-cluster/clustered-solutions-<today>.md`.

## Hard-exit triggers

Skill aborts with a clear three-line error naming the violation. No partial writes.

**Error message format:**

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

| Trigger | Looked for | Remedy |
|---|---|---|
| Missing knowledge anchor `solution-cluster.md` or `solution-brainstorm.md` | The anchor file present at the expected path under `knowledge/discovery/` | Restore the anchor from git, or re-run Task 1 of the OST-cluster-solutions build (skills-design/OST-cluster-solutions-plan.md) |
| Zero `solution-candidates-*.json` in `workspace/4-solution-brainstorm/` | A source candidates file | Run `OST-brainstorm-solutions` |
| `workspace/context/chosen-opportunity.md` missing | Trio-ratified chosen-opportunity file | Trio ratifies after assist 5 (`OST-select-opportunity`) |
| `workspace/context/product-outcome.md` missing | Trio's product outcome file | Restore from git or re-author using the template structure |
| Source JSON does not parse | Schema-conformant v0.1 JSON | Re-run `OST-brainstorm-solutions` |
| Source JSON `schema_version` is not `"0.1"` | `"schema_version": "0.1"` | Re-run `OST-brainstorm-solutions` against the latest chosen-opportunity |
| Source `solutions[]` count != 18 | Exactly 18 source candidates | Re-run `OST-brainstorm-solutions` (3 sub-agents × 3 rounds × 2 ideas = 18) |
| Chosen-opp id mismatch (source-JSON vs. context-md bold-id) | Same opp-id in both files | Inspect `workspace/context/chosen-opportunity.md` and source candidates JSON; re-ratify or re-run the upstream brainstorm |
| LLM output not valid JSON | A single JSON object | Re-run the skill; if persistent, inspect the prompt for ambiguity |
| Member sum != 18, unknown member id, or duplicate id across clusters | All 18 source ids present exactly once across `clusters[].members[]` | Re-run the skill; if persistent, tighten the prompt's invariant rules |
| `cluster_count` != `clusters.length` | Top-level count matches array length | Re-run the skill |

## Markdown rendering template

Deterministic from JSON; no separate LLM call for rendering.

```markdown
---
title: "Clustered solutions: <chosen_opportunity.id> - <derived from chosen_opportunity.quote first clause>"
date: <YYYY-MM-DD>
purpose: Paired with clustered-solutions-<date>.json. Consumed by assist 8 (top-3 selector). 18 candidates grouped into <cluster_count> thematic clusters.
tags: [solution-cluster, ost, schema-v0.1]

---

# Clustered solutions: <chosen_opportunity.id>

Source candidates: `<source_solution_candidates>`
Source chosen opportunity: `workspace/context/chosen-opportunity.md`
Source product outcome: `workspace/context/product-outcome.md`
Schema version: 0.1
Paired JSON: `clustered-solutions-<date>.json`

## Chosen opportunity

**<chosen_opportunity.id>** (Phase: <phase_id>) - "<quote>" - *<source>*

## Product outcome

> <product_outcome>

## Clusters (<cluster_count>)

### <cluster_id>: <title>

<summary>

Members (<n>):

- **<member.id>** [<role-abbrev>, R<round>] *<member.title>* - <member.description>
- ...

(role-abbrev is derived from generating_role: product-manager → PM, ux-designer → UX, tech-lead → TL)

### <next cluster_id>: <next title>

...

(if notes present:)
## Notes

<notes>
```

## Smoke-test plan

Use the existing Norrsken fixture.

| Component | Path |
|---|---|
| Input candidates (18) | `workspace/4-solution-brainstorm/solution-candidates-2026-05-10.json` |
| Chosen opportunity | `workspace/context/chosen-opportunity.md` (`opp-5-1`, licenstilldelning) |
| Product outcome | `workspace/context/product-outcome.md` |
| Expected output dir | `workspace/5-solution-cluster/` (skill creates lazily) |

**Pass criteria:**

- Invariants hold: member sum = 18, every id present exactly once, `cluster_count` in 3-5 (or `notes` explains why outside).
- JSON parses and conforms to schema v0.1.
- Markdown renders deterministically from JSON.
- Known-tough case: `sol-r1-pm-1` ("Automatisera licens-upplägg via direktintegration mot Delfi API") and `sol-r1-tl-1` ("Automatiserad licens-provisionering via Delfi API") land in the same cluster. This is the within-round near-duplicate that the brainstormer accepted as a designed property (see `OST-brainstorm-solutions-design.md` Future considerations #11). If they don't co-cluster, the cluster prompt is too narrow - surface for design review, not a hard failure.

Negative-test fixtures are deferred to the same backlog item that OST-brainstorm-solutions opened (`smoke-test-failure-cases.md`, currently tracked in `TODO.md`).

## Scope-out

The skill explicitly does NOT:

- Pick winners or rank clusters by quality - that's assist 8 (top-3 selector).
- Filter, dedupe, or modify source candidates - the clusterer is read-only against its input.
- Generate cluster-level rationale tied to the product outcome - also assist 8's territory.
- Write to `workspace/context/` - the cluster map is a proposal, not a ratified artifact.
- Add assumptions, risks, or test cards per cluster - that's assist 9+.
- Re-run the brainstormer or request additional candidates - it consumes what it gets.

## Future considerations (v0.2 candidates)

1. **Parse `build_on` from description prose.** Deferred from Q3 of the brainstorm. If assist 8 reports needing structured chain data, add a member-level `build_on: ["sol-r1-pm-5"]` field populated by regex + cross-check against member ids. Captures the brainstormer's prose anti-dup signal as structural data without changing the brainstormer.
2. **Cluster-axis disclosure.** Optional `cluster_axis_summary` field that names what dimensions the LLM used (e.g., "mechanism (API vs. UI vs. process) + intervention type (add vs. remove)"). Helps trio sanity-check the clustering logic.
3. **Weak-fit flag on members.** Optional `fit_confidence: strong | weak` on member objects, for solutions the LLM placed but with low confidence. Surfaces ambiguity for trio review without forcing single-member clusters.
4. **Configurable target range.** v1 locks 3-5. If trios find 4-6 or 2-4 fits better for specific material profiles, expose as config in the anchor.
5. **Re-cluster on disagreement.** If trio review surfaces "this cluster should split", let the skill take a subset of members + a split instruction and produce a re-clustered output. Avoids full re-runs.
6. **Cluster ordering by outcome-relevance.** v1 orders by member count. Could order by LLM-judged outcome-impact if assist 8 finds that more useful (but likely assist 8's job).
7. **Cluster rationale field.** A short *why* per cluster (why these members go together, beyond the `summary`). Likely subsumed by assist 8's downstream rationale.
8. **Negative-test fixtures.** Tracked in `TODO.md` (shared with OST-brainstorm-solutions). Construct fixtures for: missing source file, schema mismatch, ≠ 18 candidates, missing context file, chosen-opp id mismatch, malformed LLM output, invariant violation.

## What this skill establishes for the workshop-3 series

- **Discovered-cluster precedent.** Where `OST-cluster-opportunities` clusters against a known taxonomy (experience-map phases), `OST-cluster-solutions` discovers clusters from data. The single-member-cluster rule and the cluster-ordering-by-member-count rule are the first locked conventions for the discovered-cluster pattern. If future assists need similar pattern (e.g., clustering assumptions across solutions), this design is the reference.
- **Chosen-opp cross-check.** First skill to enforce a hard-exit cross-check between a JSON id and a markdown bold-id row. Pattern transfers to any skill that consumes a context file alongside a downstream-derived JSON.
- **Single-pass clustering with embedded examples.** Reinforces the same shape used by `OST-select-opportunity` and `OST-compare-opportunities`. Three skills now share the pattern; it's the default for single-pass structured-output skills in the series.
