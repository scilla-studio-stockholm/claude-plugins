---
title: "OST-cluster-opportunities: design spec"
date: 2026-05-09
purpose: Locked design for assist 3b in opportunity-solution-tree-agents.md - takes validated opportunities and an experience-map JSON and produces an enriched experience-map JSON (schema v0.2) where each opportunity is tagged with phase_id (and optionally step_id), parent-child grouped within phase, with a separate fas-0-unphased bucket. Input to the implementation plan.
tags: [skill-design, ost, opportunity-clustering, schema-v0.2]

---

# OST-cluster-opportunities: design spec

This is the locked design for **assist 3b** in `opportunity-solution-tree-agents.md`. It is the fourth skill built, after `OST-opportunity-extractor`, `OST-validate-opportunities`, and `OST-extract-experience-map`. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when clustering validated opportunities against an experience map, output a paired JSON + markdown rendering where each opportunity is tagged with `phase_id` (and optionally `step_id`), parent-child grouped within phase (max 2 levels), with a separate `fas-0-unphased` bucket for opportunities that don't fit any journey phase.

Input is the extracted experience map (v0.1 JSON), the validated-opportunities table from assist 3a, and the extracted-opportunities markdown (full quotes). Output is two files in `workspace/1-opportunity-val/` with the same root name: an enriched experience-map JSON conforming to schema v0.2 in `../knowledge/discovery/experience-mapping.md`, and a markdown rendering generated deterministically from the JSON.

The skill enriches the experience map; it does not replace the upstream extracted file. The upstream file stays immutable. The clustered file lives alongside it, with a different root name.

## Scope decisions (locked 2026-05-09)

The brainstorm narrowed scope from the open questions in `opportunity-solution-tree-agents.md` (lines 360-386) and added several mechanical decisions. Each decision below resolves an open question.

| Question | Decision |
|---|---|
| Parent-child depth | Max 2 levels (parent + child). A child cannot itself be a parent. |
| Out-of-phase representation | Synthetic phase `fas-0-unphased` with `order: 0`, empty `steps[]`. Lives in `phases[]` like any other phase. Each opportunity placed there carries an `out_of_phase_reason`. |
| Output form | Enrich the experience-map JSON in place (same schema family, bumped to v0.2). Different filename keeps the upstream extracted file immutable. |
| Input filter | Cluster ALL validated opportunities regardless of verdict. Each carries its `verdict` field. Comparator downstream filters as needed. |
| Multi-phase ambiguity | AI silently picks highest-confidence phase. No warning. The trio's parallel manual clustering catches misclassifications at the HITL checkpoint. |
| Parent-child mechanics | AI actively proposes a hierarchy: identifies a broader parent + more specific children within each phase. Gives the trio something concrete to compare against. Skipped when fewer than 3 opportunities exist in a phase. |
| `step_id` granularity | Set only when the citation makes the step explicit (e.g., a quote names "Credit Safe" → `step-4-4`). Otherwise the key is omitted per the missing-optional convention. Not used for `fas-0-unphased`. |
| Skill vs agent | Plain skill. Single-pass composition over three text inputs; no iteration, no vision. |
| Output-file convention | Paired output at `workspace/1-opportunity-val/experience-map-clustered-<YYYY-MM-DD>.{json,md}`, per cross-cutting datakontrakt. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-cluster-opportunities/SKILL.md` |
| Skill name | `OST-cluster-opportunities` |
| Slash-command (optional) | `/OST-cluster-opportunities` if frequency justifies it |
| Body language | English, matching the precedent set by `OST-validate-opportunities` and `OST-extract-experience-map` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when clustering validated opportunities against an experience map, output a paired JSON + markdown rendering where each opportunity is tagged with phase_id (and optionally step_id), parent-child grouped within phase (max 2 levels), with a separate fas-0-unphased bucket for opportunities that don't fit any journey phase.

This follows the "for X, when Y, output Z" pattern. It is generic, not Metria-specific. It is distinct from `OST-validate-opportunities` (per-opportunity verdict, no journey context), `OST-extract-experience-map` (reads a screenshot, doesn't touch opportunities), and `OST-opportunity-extractor` (reads transcripts, doesn't cluster).

## Inputs and prerequisites

**Input files** (all in `workspace/1-opportunity-val/`):

| File pattern | Source | Used for |
|---|---|---|
| `experience-map-extracted-<date>.json` | `OST-extract-experience-map` (assist 2) | The journey structure to cluster against |
| `opportunities-validated-<date>.md` | `OST-validate-opportunities` (assist 3a) | Per-opportunity verdict |
| `opportunities-extracted-<date>.md` | `OST-opportunity-extractor` (assist 3a-pre) or manual capture | Full quotes (validation table truncates excerpts to ~50 chars) |

**File-resolution rule:** Default to the latest file matching each pattern (sort by `<date>` in filename, descending). If the dates of the three latest don't align, emit a warning to the markdown output but proceed with the latest of each.

**Knowledge anchors read at runtime:**

- `../knowledge/discovery/experience-mapping.md` — schema v0.2 and the structural pattern.
- `../knowledge/discovery/opportunity-citation-format.md` — citation conventions, used to read the source/quote structure.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` — opportunity-space principles, used as the lens for parent-child grouping.

Per the cross-cutting datakontrakt decision, anchors are read at runtime rather than hard-coded into the prompt.

**What the skill does NOT consume:**

- Interview transcripts. Quotes are pre-extracted upstream.
- Miro or any external surface. JSON + markdown only.
- A schema file. The schema lives in the experience-mapping knowledge anchor.

## Schema bump v0.1 → v0.2

The skill writes JSON conforming to v0.2 of the schema in `../knowledge/discovery/experience-mapping.md`. v0.2 adds four optional fields and widens one constraint. It is backward-compatible: any well-formed v0.1 file with non-empty `steps[]` is also valid v0.2.

**New optional fields on `phases[].opportunities[]` items:**

| Field | Type | Semantics |
|---|---|---|
| `step_id` | string | A `step.id` within the same phase. Set only when the citation makes the step explicit. The skill validates that the referenced step exists in the assigned phase. Not used for `fas-0-unphased`. Otherwise omitted. |
| `parent_id` | string | An `opportunity.id` within the same phase that is the broader parent. Top-level (parent) opportunities omit the key; children carry it. Depth ≤ 2 — a child cannot itself be a parent. The skill enforces this; the schema does not. |
| `verdict` | string enum: `approved` \| `needs_tweak` \| `solution_in_disguise` | Carried forward from `OST-validate-opportunities`. Always written by this skill. Stays optional in the schema for forward compatibility (e.g., a trio that bypasses 3a). |
| `out_of_phase_reason` | string | Short AI-written explanation of why an opportunity didn't fit any journey phase. Schema-optional, but required by the skill body whenever `phase_id == "fas-0-unphased"`. Omitted for any opportunity in a real phase. |

**Relaxation of `phases[].steps[]`:** v0.1 wording is "`steps[]` not empty"; v0.2 allows zero-length arrays. The key is always present. This is the minimum change needed so `fas-0-unphased` can carry `steps: []`. A real phase with empty `steps[]` is still a hard-exit signal in `OST-extract-experience-map`; the relaxation only matters for the synthetic unphased bucket.

**ID conventions (clarification, not a change):**

- Opportunity IDs are flat sequential per phase: `opp-<phaseN>-<seq>`. Hierarchy lives in `parent_id`, not in the ID string.
- Unphased opportunities: `opp-0-<seq>`.
- IDs are globally unique within the file so `parent_id` resolves unambiguously. Within-phase parenthood is a skill-level invariant, not a schema-level constraint.

**`schema_version` bump:** The skill writes `"0.2"`.

## Steps

The skill follows the same numbered-step pattern as `OST-validate-opportunities` and `OST-extract-experience-map`:

1. **Read knowledge anchors:** the three files listed above.
2. **Locate the three input files** in `workspace/1-opportunity-val/`. Default to the latest match for each pattern.
3. **Hard-exit checks** (see Error handling): zero-file matches and malformed experience-map JSON.
4. **Parse and join.** Index phases by `id`. Parse the validated table (one row per opportunity, with verdict). Parse the extracted markdown (full quotes). Join validated rows to extracted opportunities **by row order**, with a prefix verification: the validated excerpt must be a prefix of the corresponding extracted full quote. Mismatch on any row triggers a hard exit naming the row.
5. **Cluster each opportunity against a phase.** Decide phase membership using quote semantics, source context, and phase names/steps. Silently pick the highest-confidence phase. If no phase fits with reasonable confidence, place the opportunity in `fas-0-unphased` and write an `out_of_phase_reason`. If the citation explicitly names something that maps 1:1 to a step (a system in `systems_in_use`, an event in a step description), set `step_id`; verify the referenced step exists in the assigned phase.
6. **Within each phase, propose parent-child grouping.** For phases with 3+ opportunities, identify a broader/narrower relationship: one opportunity that names a category-level pain plus one or more that name specific instances. Promote the broader one to parent (omit `parent_id`); set `parent_id` on each child. Cap depth at 2; flatten any deeper chain. Skip parent-child grouping inside `fas-0-unphased`.
7. **Compose the v0.2 JSON.** Start from the experience-map JSON. Bump `schema_version` to `"0.2"`. Populate `phases[].opportunities[]` with clustered items. Append the synthetic `fas-0-unphased` phase only if at least one opportunity was placed there. Per the missing-optional convention, omit any optional key whose value isn't set; never write `null`.
8. **Render markdown deterministically from the JSON** via the embedded template (see Output composition).
9. **Write paired output** to `workspace/1-opportunity-val/experience-map-clustered-<YYYY-MM-DD>.json` and the matching `.md`. Today's date in `YYYY-MM-DD`. Same root name on both files.

The composition is a single pass. No retries, no iteration, no self-validation pass against the schema after composition. Upstream files are never modified.

## Output composition

Two files with the same root name:

```text
workspace/1-opportunity-val/experience-map-clustered-<YYYY-MM-DD>.json
workspace/1-opportunity-val/experience-map-clustered-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.2 from `../knowledge/discovery/experience-mapping.md`. No extra fields beyond the v0.2 additions. `phases[].opportunities[]` is populated for every real phase that received any opportunity (and for `fas-0-unphased` if it exists); per the missing-optional-fields convention, the key is omitted from any phase that received zero opportunities.

**The markdown** is generated deterministically from the JSON via an embedded template in the prompt:

```markdown
---
title: Experience map (clustered) - <title> (<team>)
date: <YYYY-MM-DD>
purpose: Clustered experience map for OST opportunity work, paired with experience-map-clustered-<date>.json
tags: [experience-mapping, ost, opportunity-clustering, schema-v0.2]

---

# Experience map (clustered): <title> (<team>)

Source experience map: `experience-map-extracted-<date>.json`
Source validated opportunities: `opportunities-validated-<date>.md`
Source extracted opportunities: `opportunities-extracted-<date>.md`
Schema version: 0.2
Paired JSON: `experience-map-clustered-<YYYY-MM-DD>.json`

## Product outcome

<full outcome formulation>

## Narrativ
[only if present]

<narrativ>

## Clustering summary

- Phases with opportunities: <N> of <total>
- Opportunities per phase: <name 1>: <N>, <name 2>: <N>, ...
- Unphased: <N>
- Verdicts: ✅ Approved <N>, 🔧 Needs tweak <N>, ⚠️ Solution in disguise <N>

## Journey

### Phase 1: <name> (friction: <low|medium|high>)

**Steps:**

- <step description>
- [step description not legible]
  - Branch: <label> -> <leads_to>

**Opportunities (<N>):**

- ✅ **opp-1-1** "<full quote>" - *<source>* [steg: <step_id> if present]
  - 🔧 **opp-1-2** "<full quote>" - *<source>*
  - ✅ **opp-1-3** "<full quote>" - *<source>* [steg: <step_id>]
- ⚠️ **opp-1-4** "<full quote>" - *<source>*

[Children indented one level under their parent. Top-level bullets are
parents or stand-alones. If a phase has no opportunities, render
"_Inga opportunities klustrade till denna fas._" instead of the Opportunities
block.]

[repeat for each real phase in `order` order]

## fas-0-unphased
[only if at least one opportunity was placed here; otherwise omit this whole
section. No steps, no friction, flat list - no parent-child.]

- ⚠️ **opp-0-1** "<full quote>" - *<source>*
  Reason: <out_of_phase_reason>
- ✅ **opp-0-2** "<full quote>" - *<source>*
  Reason: <out_of_phase_reason>

## Extensions
[only if extensions is non-empty on the source map; carried through unchanged
from the extracted JSON]

**Systems in use:** Outlook, Freshdesk, ...

## Warnings
[only if any]

- Input file dates do not align: experience-map=2026-05-08, validated=2026-05-09, extracted=2026-05-09. Used latest of each.
- Phase 5 step reference 'Credit Safe' resolved to step-5-2 (only step in phase that mentions Credit Safe).
```

**Rendering rules:**

- **Verdict prefix.** Each opportunity bullet starts with the emoji per `OST-validate-opportunities` (✅ / 🔧 / ⚠️). Verdict label text is omitted from the bullet — the emoji carries the signal.
- **Quote vs excerpt.** Always render the full quote, never the truncated excerpt from the validation table.
- **Source attribution.** Carried verbatim from the extracted file. Separated from the quote by ` - ` (regular dash, not em-dash, per the no-em-dash-in-Swedish rule applied uniformly).
- **Step reference.** `[steg: <step_id>]` (or `[step: <step_id>]` if the experience map is in English) appended at end of the bullet, only when `step_id` is present.
- **Parent-child nesting.** One level of indentation under the parent. Never deeper. The `parent_id` field is the source of truth; the indentation is the rendering of it.
- **Unphased section heading uses the technical key `fas-0-unphased`** so the JSON↔markdown correspondence is visible.
- **Output language matches the experience map's body language.** Schema field names, JSON key strings, and verdict emojis stay as defined; everything else (phase headings, opportunity quotes, source lines, `out_of_phase_reason`) follows the source language.

The frontmatter on the markdown output complies with the Metria global rule that every `.md` file has YAML frontmatter, with a blank line before the closing `---`.

## Knowledge-doc updates required before ship

As part of building this skill, `../knowledge/discovery/experience-mapping.md` is updated to:

- Replace the "JSON schema (v0.1)" code block with v0.2 (adds the four optional fields, widens the `steps[]` rule).
- Extend the "Field notes" list to cover the four new fields and the new `steps[]` rule.
- Update the "Open questions" section: the v0.1 question "Should opportunities carry a `journey_step_id` for finer placement than phase?" is now answered — added in v0.2 as `step_id`, scoped within phase.
- Add a v0.2 entry to the "Evolution" section noting the new fields exist to support the OST-cluster-opportunities skill.

Backward compatibility: any well-formed v0.1 file with non-empty `steps[]` arrays is also a valid v0.2 file. v0.2 adds optional fields and widens one constraint; nothing is removed or tightened.

## Error handling

**Hard-exit triggers** (no output files written when these fire):

| Trigger | Looked for | Remedy |
|---|---|---|
| Zero files match `experience-map-extracted-*.json` | The extracted experience map | Run `OST-extract-experience-map` |
| Zero files match `opportunities-validated-*.md` | The validated opportunity table | Run `OST-validate-opportunities` |
| Zero files match `opportunities-extracted-*.md` | The extracted opportunities (full quotes) | Run `OST-opportunity-extractor` or capture opportunities manually in citat-stickie format |
| Experience-map JSON does not parse, or required v0.1 fields missing/empty | Schema-conformant `product_outcome`, `title`, `team`, non-empty `phases[]` with `name`/`order`/non-empty `steps[]` per phase | Re-run `OST-extract-experience-map` against the source screenshot |
| Row-order join prefix mismatch between validated table and extracted markdown | Validated row N's excerpt is a prefix of extracted opportunity N's full quote | Re-run `OST-validate-opportunities` against the current `opportunities-extracted-*.md`; do not hand-edit either file out of sync |

**Hard-exit message format** (same as `OST-extract-experience-map`):

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

Three pieces in order: what failed, what the skill saw, what to do about it. No silent degradation. No retries.

**Soft warnings** (written to the Warnings section in the markdown output, do not block):

- Input file dates do not align across the three patterns. Skill proceeds with the latest of each.
- A `step_id` was inferred from a citation reference and resolved to a single matching step. (Logged for trio review.)

**Convention for missing optional fields in JSON:** the skill omits the key entirely rather than writing `null`. Applies to all v0.1 optional fields and all four new v0.2 fields. Downstream skills must handle key absence as the missing-value signal.

**No JSON self-validation pass.** Trust the prompt; downstream skills surface any malformed JSON. Mirrors `OST-extract-experience-map`.

## What this skill does NOT do

- **Read interview transcripts.** Quotes come pre-extracted from `opportunities-extracted-*.md`. That extraction is `OST-opportunity-extractor` upstream, or manual capture by the trio.
- **Validate citation format.** Bad citations get clustered anyway and carried through with whatever verdict 3a assigned. Format quality is `OST-validate-opportunities`'s job.
- **Filter by verdict.** All validated opportunities are clustered regardless of verdict. Each carries its `verdict` field; the downstream comparator (step 4) decides what to filter.
- **Fix or rewrite opportunities flagged `needs_tweak` or `solution_in_disguise`.** The trio's wording is canonical; the skill clusters as-is.
- **Compare opportunities against the product outcome.** That is `OST-compare-opportunities` (step 4).
- **Decide which opportunity to pick.** That is the selector (step 5).
- **Modify the upstream extracted experience map.** `experience-map-extracted-*.json` stays immutable.
- **Propose new phases or change existing phase boundaries.** Phase structure is the trio's job inside `OST-extract-experience-map`. The clusterer accepts the journey as given. The single exception is appending `fas-0-unphased` for the unphased bucket — that's a fixed convention, not a designed phase.
- **Ask the trio for clustering choices interactively.** Multi-phase ambiguity is resolved silently by highest confidence. The trio's parallel manual clustering catches misclassifications at the HITL checkpoint.
- **Iterate, retry, or run multiple passes.** One pass over the inputs, one pair of output files. No incremental state across runs.
- **Write to Miro or any external surface.** JSON + markdown in `workspace/1-opportunity-val/` only.
- **Update `../knowledge/discovery/experience-mapping.md` at runtime.** The doc bump to v0.2 is a one-time edit done as part of building this skill, not something the skill performs.
- **Audit global parent-child consistency.** Within-phase parent-child is enforced inline during composition (depth ≤ 2, parent in same phase). The skill does not run a second sweep over the finished JSON to re-check invariants.

## Testing

Smoke test only for v1, no formal regression harness. Reuses the Norrsken Licenstilldelning example as the integration fixture:

```text
Inputs:
  workspace/1-opportunity-val/experience-map-extracted-2026-05-09.json
    (from OST-extract-experience-map smoke test)
  workspace/1-opportunity-val/opportunities-validated-2026-05-09.md
    (from OST-validate-opportunities smoke test)
  workspace/1-opportunity-val/opportunities-extracted-2026-05-09.md
    (the source the validated table was built from)

Expect:
  - schema_version "0.2" in the output JSON
  - Each validated opportunity is present in the output JSON
  - Each opportunity has a verdict matching the validation table
  - Each opportunity has a phase_id pointing at a real phase or fas-0-unphased
  - At least one phase shows a parent-child pair (with parent omitting parent_id
    and child carrying it)
  - opp-* IDs are unique across the file
  - parent_id always references an id in the same phase
  - step_id (when present) always references a step in the assigned phase
  - fas-0-unphased opportunities all carry out_of_phase_reason
  - The markdown renders the same set of opportunities, with emoji prefixes
    matching the verdicts and indentation matching parent_id
```

Eyeball the JSON output. If clustering is wrong, parent-child structure is missing, or step_id references the wrong phase, the prompt is wrong. A formal regression harness is overkill for v1.

## Open follow-ups

These are added to the existing cleanup TODO list rather than blocking v1.

1. **Schema evolution beyond v0.2.** Bumps when (a) downstream skills request new fields or (b) trios produce structures v0.2 cannot represent. Procedure: add an "Evolution" entry to `experience-mapping.md` and bump `schema_version` in skill prompts.
2. **Confidence visibility.** Multi-phase ambiguity is currently resolved silently. If trios consistently catch the same kinds of misclassifications at HITL, consider exposing a per-opportunity confidence signal (or an alternative-phase suggestion) to make the trio's review faster.
3. **Re-run on edited inputs.** The skill is one-shot per run. If trios edit a clustered file by hand and want to re-cluster from a tweaked validation table, they currently re-run from scratch. Revisit only if this becomes painful.
4. **Step-level clustering as default.** Currently `step_id` is set only when explicit. If trio practice converges on step-level granularity as the working unit (rather than phase-level), promote step-level clustering from opportunistic to default.
5. **Auto-warn on cross-phase parent-child attempts.** The skill flattens deep chains silently. If trios ever want to see what was flattened, surface it in the Warnings section.
6. **Skill-template body-language line.** `skills-design/skill-template.md` still says "Svenska i body och output". Update the template to reflect the English convention now confirmed across `OST-validate-opportunities`, `OST-extract-experience-map`, and this skill. Already on the cleanup list.
