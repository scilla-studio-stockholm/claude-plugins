---
name: OST-cluster-solutions
description: For product trios and researchers, when grouping 18 divergent solution candidates from a brainstorm pass into 3-5 thematic clusters so duplicates collapse and unique ideas surface, output a paired JSON + markdown clustered solution map. Each cluster has a title, summary, and full embed of its member solutions. Input to assist 8 (top-3 selector).
---

# Cluster solutions

You help a product trio cluster 18 divergent solution candidates from a brainstorm pass into 3-5 thematic clusters. Each cluster gets a 3-7 word title, a 2-4 sentence summary, and a full embed of its member solutions. Output is paired JSON (per the solution-cluster schema v0.1) plus a markdown rendering generated deterministically from the JSON.

This skill is assist 7 in the OST discovery workflow.

The output is a **proposal** that assist 8 (top-3 selector) consumes. The trio reviews assist 8's top-3 proposal, not this intermediate cluster map. This skill does not modify the opportunity folder root (`<scope>/..`) or `product-context/`.

**Out of scope:** picking winners, ranking clusters by quality (assist 8's job), filtering or modifying source candidates, generating cluster-level outcome rationale, adding assumptions or risks per cluster (assist 9+), re-running the brainstormer.

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`. Discovery scope only; hard-exit if the resolved scope contains `/opportunity-selection/`.

2. **Load context via parent walk-up:**
   - `<scope>/decisions.json`
   - Same-round predecessor: `<scope>/_working/solution-candidates.json`. If missing in `<scope>/_working/`, walk siblings (other dated rounds under the same opportunity) in date-descending order.

3. **Read the knowledge anchors:**
   - `references/solution-cluster.md` - the clustered-solutions schema (v0.1), the four locked decisions, the clustering-axis convention, the chosen-opp cross-check rule, the field-notes section.
   - `references/solution-brainstorm.md` - the source schema (v0.1) so you can parse what `OST-brainstorm-solutions` produced.

4. **Locate inputs:**
   - `<scope>/_working/solution-candidates.json` (same-round predecessor; walk siblings in date-descending order if missing in `<scope>/_working/`).
   - `<scope>/decisions.json`

5. **Hard-exit checks** (see Hard-exit format below). Do not write any output files when these fire:
   - Missing knowledge anchor `solution-cluster.md` or `solution-brainstorm.md` (expected under `knowledge/discovery/`).
   - `<scope>/_working/solution-candidates.json` missing (no same-round or sibling predecessor found).
   - `<scope>/decisions.json` missing.
   - `decided.opportunity` key absent from `decisions.json`.
   - Source JSON does not parse.
   - Source JSON `schema_version` is not `"0.1"`.
   - Source `solutions[]` does not contain exactly 18 entries.
   - Chosen-opp id in source JSON does not match `decided.opportunity.id` in `decisions.json`.

6. **Parse inputs.**
   - Parse the source candidates JSON. Carry `team`, `product_outcome`, `chosen_opportunity` (full sub-object) verbatim. Index `solutions[]` by `id`. Confirm count == 18.
   - Read `<scope>/decisions.json`. Extract `decided.opportunity` (fields: `id`, `phase_id`, `quote`, `source`) and `product_outcome`.
   - Cross-check: source-JSON `chosen_opportunity.id` must equal `decided.opportunity.id` from `decisions.json`. Mismatch → hard-exit (see triggers). This ensures the chosen opportunity hasn't changed between brainstorm and clustering.
   - Use `product_outcome` from `decisions.json` for grounding in the LLM prompt (the `product_outcome` field in output is carried from source-JSON, which is the authoritative copy at brainstorm-time).

7. **Compose the clustering prompt.** Build a single LLM prompt with these sections, in this order:

   **a. Role frame:**
   > You are clustering 18 solution candidates by theme. Group them into 3-5 thematic clusters so duplicates collapse and unique ideas surface. Each cluster gets a 3-7 word title and a 2-4 sentence summary.

   **b. Grounding context:**
   > Chosen opportunity: `<chosen_opportunity.id>` (Phase: `<phase_id>`) - "`<quote>`" - *`<source>`*
   >
   > Product outcome: `<product_outcome verbatim>`

   **c. The 18 candidates** rendered as a flat list, one per line:
   ```
   - sol-r1-pm-1 [product-manager, R1] "Title here" - Description here.
   - sol-r1-pm-2 [product-manager, R1] "Title here" - Description here.
   ...
   ```

   **d. The four locked decisions** (verbatim from `solution-cluster.md` section "The four locked decisions"):
   - Cluster count target 3-5, material-driven. If the 18 candidates genuinely split into 2 or 6-7 themes, allow it and populate the top-level `notes` field naming the reason.
   - Full member embed. Each cluster's `members[]` carries `id`, `title`, `generating_role`, `round_number`, `description` verbatim from source.
   - No `build_on` field in v0.1. "Bygger på sol-..." prose stays inside `description`, not surfaced as structural data.
   - Single-member clusters allowed. A genuinely unique solution gets its own cluster of one. No separate outlier bucket.

   **e. The clustering-axis convention:**
   > Group by theme/similarity. Pick dimensions that the material actually carries (mechanism, target user, system surface, intervention type, or others). No fixed primary axis. Aim for thematic distinctness across clusters.

   **f. Soft member-ordering convention:**
   > Within each cluster, order members lead-idea first (the member whose description most centrally expresses the cluster theme), then by round ascending, then by role (product-manager, ux-designer, tech-lead).

   **g. Schema skeleton** (the v0.1 JSON shape from `solution-cluster.md`):
   ```json
   {
     "schema_version": "0.1",
     "team": "...",
     "title": "Clustered solutions: <derived from chosen opportunity quote>",
     "product_outcome": "...",
     "chosen_opportunity": { "id": "...", "phase_id": "...", "quote": "...", "source": "..." },
     "source_solution_candidates": "<source filename>",
     "cluster_count": <integer>,
     "clusters": [
       {
         "cluster_id": "<placeholder; assigned post-sort in Step 8>",
         "title": "3-7 words",
         "summary": "2-4 sentences",
         "members": [
           { "id": "sol-...", "title": "...", "generating_role": "...", "round_number": <int>, "description": "..." }
         ]
       }
     ],
     "notes": "<optional, omit key if not needed>",
     "extensions": {}
   }
   ```

   Leave the `cluster_id` values as placeholders in the LLM response; cluster_id values are assigned post-sort in Step 10 sequentially (c1, c2, ...).

   **h. Output instruction:**
   > Return only a single JSON object matching the schema. No prose preamble. No markdown code fences in the output.

8. **Make the LLM call.** Pass the composed prompt to the model. Receive the JSON response.

9. **Parse and validate the response.**
   - Parse JSON. Malformed JSON → hard-exit (see triggers).
   - Validate invariants:
     - Sum of `members[]` across all clusters = exactly 18.
     - Every `member.id` exists in source `solutions[]` (no inventions).
     - No `member.id` appears in two clusters (no duplicates).
     - `cluster_count` equals `clusters.length`.
   - Invariant violation → hard-exit (see triggers) with the specific violation named.

10. **Post-sort clusters.** Reorder `clusters[]` by member count descending; ties broken by first-appearing member id. Assign `cluster_id` values `c1, c2, ...` post-sort. Member ordering within a cluster is the LLM's choice and is preserved verbatim.

11. **Set top-level `title`** to `"Clustered solutions: <first 5-10 words of chosen_opportunity.quote, trailing punctuation stripped>"`. Set `source_solution_candidates` to the basename of the source JSON file (no directory prefix).

12. **Write JSON output** to `<scope>/_working/clustered-solutions.json` using today's date. Create the `<scope>/_working/` directory if it doesn't exist.

13. **Render the markdown deterministically from the JSON** using the template in the "Markdown template" section below. Write to `<scope>/_working/clustered-solutions.md`.

    Use today's date in `YYYY-MM-DD` format. The two files share the same root name. Upstream files (`solution-candidates.json`, `decisions.json`) are not modified. This skill does not modify the opportunity folder root (`<scope>/..`) or `product-context/`.

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
| Missing knowledge anchor `solution-cluster.md` or `solution-brainstorm.md` | The anchor file present at the expected path under `knowledge/discovery/` | Restore the anchor from git. |
| `<scope>/_working/solution-candidates.json` missing (no same-round or sibling predecessor found) | `solution-candidates.json` in `<scope>/_working/` or sibling dated rounds under the same opportunity | Run `OST-brainstorm-solutions` |
| `<scope>/decisions.json` missing | `decisions.json` in `<scope>` | Run `OST-select-opportunity` to produce `decisions.json` |
| `decided.opportunity` key absent from `decisions.json` | `decided.opportunity` object with `id`, `phase_id`, `quote`, `source` | Run `OST-select-opportunity` to ratify an opportunity into `decisions.json` |
| Source JSON does not parse | Schema-conformant v0.1 JSON | Re-run `OST-brainstorm-solutions` |
| Source JSON `schema_version` is not `"0.1"` | `"schema_version": "0.1"` | Re-run `OST-brainstorm-solutions` against the latest decided opportunity |
| Source `solutions[]` count != 18 | Exactly 18 source candidates | Re-run `OST-brainstorm-solutions` (3 sub-agents × 3 rounds × 2 ideas = 18) |
| Chosen-opp id mismatch (source-JSON vs. decisions.json) | Same opp-id in source candidates JSON `chosen_opportunity.id` and `decisions.json` `decided.opportunity.id` | Inspect `decisions.json` and source candidates JSON; re-ratify or re-run the upstream brainstorm |
| LLM output not valid JSON | A single JSON object | Re-run the skill; if persistent, inspect the prompt for ambiguity |
| Member sum != 18, unknown member id, or duplicate id across clusters | All 18 source ids present exactly once across `clusters[].members[]` | Re-run the skill; if persistent, tighten the prompt's invariant rules |
| `cluster_count` != `clusters.length` | Top-level count matches array length | Re-run the skill |

## Markdown template

The markdown output is rendered deterministically from the composed JSON using this template:

```markdown
---
title: "Clustered solutions: <chosen_opportunity.id> - <first 5-10 words of chosen_opportunity.quote>"
date: <YYYY-MM-DD>
purpose: Paired with clustered-solutions.json. Consumed by assist 8 (top-3 selector). 18 candidates grouped into <cluster_count> thematic clusters.
tags: [solution-cluster, ost, schema-v0.1]

---

# Clustered solutions: <chosen_opportunity.id>

Source candidates: `<source_solution_candidates>`
Source chosen opportunity: `<scope>/decisions.json` → `decided.opportunity`
Source product outcome: `<scope>/decisions.json` → `product_outcome`
Schema version: 0.1
Paired JSON: `_working/clustered-solutions.json`

> **Assist 8 consumes this map.** Trio reviews the top-3 proposal that assist 8 produces, not this intermediate map.

## Chosen opportunity

**<chosen_opportunity.id>** (Phase: <chosen_opportunity.phase_id>) - "<chosen_opportunity.quote>" - *<chosen_opportunity.source>*

## Product outcome

> <product_outcome>

## Clusters (<cluster_count>)

### <cluster_id>: <title>

<summary>

Members (<N>):

- **<member.id>** [<role-abbrev>, R<member.round_number>] *<member.title>* - <member.description>

(repeat one bullet per member; preserve LLM's member ordering verbatim)

### <next cluster_id>: <next title>

...

(only if notes is present:)

## Notes

<notes>
```

**Role abbreviation mapping** (used in the markdown bullet, not in JSON):

- `product-manager` → `PM`
- `ux-designer` → `UX`
- `tech-lead` → `TL`

## Output principles

- **Cluster IDs are post-sort.** `cluster_id` values `c1, c2, ...` are assigned after sorting clusters by member-count descending. Do not assign cluster ids during composition.
- **Member ordering is preserved verbatim from the LLM response.** The soft convention (lead-idea first, then round, then role) lives in the prompt only; no post-sort on members.
- **Source attribution** carried verbatim from the source JSON. The `chosen_opportunity` sub-object is copied as-is.
- **No em-dash** anywhere, applied uniformly to Swedish and English prose.
- **Role abbreviations in markdown** map `product-manager` → `PM`, `ux-designer` → `UX`, `tech-lead` → `TL`. The JSON field `generating_role` keeps the full slug.
- **Output language for prose** (`title`, `summary`, `notes`, top-level `title`) matches the source language detected in the source candidates' `description` text. Schema field names, JSON keys, cluster ids, and the role-slug vocabulary stay as defined.
- **Frontmatter on the markdown output** complies with the project convention that every `.md` file has YAML frontmatter, with a blank line before the closing `---`.
- **Notes section in markdown** is omitted entirely when `notes` is absent from JSON.
- **The assist-8-consumer banner** (`> **Assist 8 consumes this map.** ...`) is rendered verbatim every run.
- **No silent degradation.** Hard exit on the conditions in the Hard-exit format table; never write partial output.
- **No JSON self-validation pass after composition.** Trust the invariant check; downstream skills surface any malformed JSON.
- **Upstream files are immutable.** Never modify `solution-candidates.json` or `decisions.json`. The skill writes only the two `clustered-solutions.*` files inside `<scope>/_working/`.
- **This skill does not modify the opportunity folder root (`<scope>/..`) or `product-context/`.** The cluster map is a proposal, not a ratified artifact.
- **Single pass.** No retries, no iteration over the inputs.

## What this skill does NOT do

- **Pick winners or rank clusters by quality.** That's assist 8 (top-3 selector).
- **Filter, dedupe, or modify source candidates.** The clusterer is read-only against its input.
- **Re-cluster on disagreement.** If the trio disagrees with the cluster map, that's a re-run scenario, not a feature of this skill.
- **Generate cluster-level rationale tied to product outcome.** Also assist 8's territory.
- **Modify the opportunity folder root (`<scope>/..`) or `product-context/`.** The cluster map is a proposal, not ratified.
- **Add assumptions, risks, or test cards per cluster.** That's assist 9+.
- **Re-run the brainstormer or request additional candidates.** It consumes what it gets.
- **Read interview transcripts.** Candidates come from the brainstormer.
- **Read the experience map, validated opportunities table, opportunity-comparison matrix, or chosen-opportunity selector output.** Everything the clusterer needs is in `<scope>/_working/solution-candidates.json` and `<scope>/decisions.json`.
- **Use a `Cites:` line or per-member trace-back invariant.** Members are carried verbatim; no trace-back needed beyond `id` matching.
- **Apply effort or feasibility weighing.** Torres principle is in effect through the whole discovery pipeline; no exceptions here.
- **Parse `build_on` references from description prose.** Deferred to v0.2 if assist 8 reports needing it.
- **Generate a `cluster_axis_summary` field.** Deferred to v0.2.
- **Flag low-fit members.** Deferred to v0.2.
- **Sub-agent orchestration.** Single LLM call, no Agent-tool dispatch.
- **Iterate, retry, or run multiple passes.** One pass over the inputs, one pair of output files.
- **Run a JSON self-validation pass after composition.** Trust the invariant check.
- **Write to Miro or any external surface.** JSON + markdown only.
- **Audit the source candidates JSON for invariant violations beyond what's needed to apply the cluster prompt.** The clusterer trusts the brainstormer's output beyond schema-version and 18-count checks.
