---
title: "OST-compare-opportunities: design spec"
date: 2026-05-09
purpose: Locked design for assist 4 in opportunity-solution-tree-agents.md - takes the clustered v0.2 experience-map JSON from OST-cluster-opportunities (assist 3b) and the trio's product outcome, filters to approved opportunities, and produces a paired JSON + markdown comparison matrix (5 Torres criteria × N approved opportunities) plus an evidence-gap list. Input to the implementation plan.
tags: [skill-design, ost, opportunity-comparison, schema-v0.1]

---

# OST-compare-opportunities: design spec

This is the locked design for **assist 4** in `opportunity-solution-tree-agents.md`. It is the fifth skill built, after `OST-opportunity-extractor`, `OST-validate-opportunities`, `OST-extract-experience-map`, and `OST-cluster-opportunities`. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when comparing approved opportunities against a product outcome and Torres criteria, output a paired JSON + markdown rendering with a qualitative comparison matrix (5 criteria × N approved opportunities) plus an evidence-gap list of `unknown` cells.

Input is the clustered experience-map JSON (v0.2 from `OST-cluster-opportunities`) and the trio's product outcome at `workspace/context/product-outcome.md`. Output is two files in `workspace/2-opportunity-compare/` with the same root name: a comparison-matrix JSON conforming to schema v0.1 in a new knowledge anchor `../knowledge/discovery/opportunity-comparison.md`, and a markdown rendering generated deterministically from the JSON.

The skill enriches the trio's discovery artifacts with a comparison view; it does not replace any upstream file. Upstream files stay immutable. The matrix and gap list live alongside them at a stage-numbered subdirectory.

## Scope decisions (locked 2026-05-09)

The brainstorm narrowed scope from the open questions in `opportunity-solution-tree-agents.md` (lines 410-414) and added several mechanical decisions. Each decision below resolves an open question.

| Question | Decision |
|---|---|
| Verdict filter | Approved-only. `needs_tweak` and `solution_in_disguise` are excluded with a short visible note in the output ("Excluded from comparison: opp-X-Y (verdict: needs_tweak), ..."). Comparing a solution-in-disguise to a product outcome is incoherent; comparing a needs_tweak risks scoring weakly-worded shape. |
| Cell shape | Qualitative score + 1-2 sentence rationale. No numeric scores. |
| Score vocabulary | Five values: `strong` / `medium` / `weak` / `unknown` / `n/a`. Non-numeric; can't be summed. `unknown` means evidence is thin (goes on gap list); `n/a` means the criterion structurally doesn't apply (does NOT go on gap list). |
| Criteria (matrix rows) | Five hardcoded: outcome alignment, customer importance, market size / frequency, strategic fit (alignment with vision), competitive landscape. Configurable criteria parked for v0.2. |
| Trace-back rule | For scores `strong` / `medium` / `weak`, the rationale must reference at least one `opp-id` from `opportunities_compared[]`. The rationale's structure conveys the "grounded vs reasoned" signal: a `strong`/`medium`/`weak` rationale without an `opp-id` reference is structurally invalid. If the AI cannot honestly cite, score `unknown` and the cell goes on the gap list. `unknown` and `n/a` cells skip the trace-back rule. |
| No-effort rule | First-class output principle with the if-then reasoning-cleanup instruction ("if your reasoning chain ever reaches 'but it would be hard/easy to build', remove that step and re-score on the criterion's dimension only"). No validation pass. Trust the prompt. |
| Skill vs agent | Plain skill. Single-pass composition over a regular matrix structure (5 criteria × N opportunities); each cell is computed independently with no agent-style state or pairwise N×N loops. The "pairwise" framing in the brainstorm-input was misleading: the brainstorm-input's own output spec is criterion × opportunity, not opportunity × opportunity. |
| Output directory | `workspace/2-opportunity-compare/`. Stage-numbered convention continuing `1-opportunity-val/`. The flat workspace-root convention in the workspace README has drifted; updating the README is a follow-up TODO. |
| Output filename | `comparison-matrix-<YYYY-MM-DD>.{json,md}` per cross-cutting datakontrakt. |
| Schema location | New knowledge anchor `../knowledge/discovery/opportunity-comparison.md` (mirrors the experience-mapping precedent). Schema is v0.1. |
| Evidence-gap list | Rendered as a section in the same markdown file as the matrix, derived from `unknown` cells. Not a separate file. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-compare-opportunities/SKILL.md` |
| Skill name | `OST-compare-opportunities` |
| Slash-command (optional) | `/OST-compare-opportunities` if frequency justifies it |
| Body language | English, matching the precedent set by `OST-validate-opportunities`, `OST-extract-experience-map`, and `OST-cluster-opportunities` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when comparing approved opportunities against a product outcome and Torres criteria, output a paired JSON + markdown rendering with a qualitative comparison matrix (criteria × opportunities) plus an evidence-gap list of unknown cells.

This follows the "for X, when Y, output Z" pattern. It is generic, not Metria-specific. It is distinct from `OST-cluster-opportunities` (clusters against an experience map; doesn't compare against the outcome), `OST-validate-opportunities` (per-opportunity verdict; no matrix), and `OST-extract-experience-map` (reads a screenshot; doesn't touch opportunities).

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/1-opportunity-val/experience-map-clustered-<date>.json` | `OST-cluster-opportunities` (assist 3b) | Source of clustered approved opportunities, their quotes, sources, verdicts, and phase placement |
| `workspace/context/product-outcome.md` | Trio-authored, fixed path | Outcome formulation that grounds the "outcome alignment" criterion |

**File-resolution rules:** Latest file matching `experience-map-clustered-*.json` by `<date>` in filename, descending. The product outcome is at a fixed path with no date suffix.

**Knowledge anchors read at runtime:**

- `../knowledge/discovery/opportunity-comparison.md` (NEW, created as part of this build) - the matrix schema, the criteria definitions, the score vocabulary, the trace-back rule, the no-effort rule.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - Torres principles, with the explicit "Don't assess effort during opportunity selection" line as the comparator's lens.
- `../knowledge/discovery/experience-mapping.md` - schema v0.2 of the input JSON, so the skill can read clustered files.

Per the cross-cutting datakontrakt decision, anchors are read at runtime rather than hard-coded into the prompt.

**What the skill does NOT consume:**

- The original `opportunities-extracted-*.md` or `opportunities-validated-*.md` files. Every quote, source, and verdict the comparator needs is already in the clustered JSON.
- Interview transcripts.
- A separate markdown file alongside the clustered JSON. JSON-only on the cluster side.
- A schema file. The schema lives in the new knowledge anchor.

## The new knowledge anchor: `../knowledge/discovery/opportunity-comparison.md`

This anchor carries the same role for the comparator that `experience-mapping.md` carries for the clusterer: it owns the schema, the field semantics, and the framework prose. Created as a one-time write during this skill's build; not modified at runtime.

Sections in the anchor:

1. **What the comparator does** - short framework prose tying it to Torres CDH ch 7.
2. **The five criteria** - outcome alignment, customer importance, market size / frequency, strategic fit, competitive landscape. Each with stable kebab-case ID, display name, and 1-2 sentence description of what the criterion asks.
3. **The score vocabulary** - `strong` / `medium` / `weak` / `unknown` / `n/a`. Each with semantics, including the explicit distinction between `unknown` (evidence thin → gap list) and `n/a` (criterion structurally doesn't apply → not on gap list).
4. **The trace-back rule** - every non-`unknown` rationale must cite at least one `opp-id` from the cluster.
5. **The no-effort rule** - citing the OST anchor's principle.
6. **JSON schema (v0.1)** - the contract.
7. **Field notes** - per-field commentary including the missing-optional convention.
8. **Open questions** - what's punted to v0.2.
9. **Evolution** - version history.

**Schema v0.1:**

```json
{
  "schema_version": "0.1",
  "team": "string (carried from clustered map)",
  "title": "string (carried from clustered map)",
  "product_outcome": "string (full outcome from workspace/context/product-outcome.md)",
  "source_clustered_map": "string (filename of source experience-map-clustered-*.json)",
  "criteria": [
    {
      "id": "string (e.g., 'outcome-alignment')",
      "name": "string (display name, e.g., 'Outcome alignment')",
      "description": "string (what the criterion asks)"
    }
  ],
  "opportunities_compared": [
    {
      "id": "string (carried verbatim from cluster JSON, e.g., 'opp-4-1')",
      "phase_id": "string (carried)",
      "quote": "string (carried)",
      "source": "string (carried)"
    }
  ],
  "opportunities_excluded": [
    {
      "id": "string",
      "phase_id": "string",
      "verdict": "needs_tweak | solution_in_disguise",
      "reason": "string (one-line note, e.g., 'verdict needs_tweak: vag deskriptor')"
    }
  ],
  "cells": [
    {
      "criterion_id": "string",
      "opportunity_id": "string",
      "score": "strong | medium | weak | unknown | n/a",
      "rationale": "string (1-2 sentences)",
      "opp_refs": ["string (opportunity IDs cited in the rationale; non-empty for strong/medium/weak; empty for unknown and n/a)"]
    }
  ],
  "evidence_gaps": [
    {
      "criterion_id": "string",
      "opportunity_id": "string",
      "what_is_missing": "string (one sentence describing what evidence would unlock a score)"
    }
  ]
}
```

**Schema design notes:**

- `cells[]` is flat (one entry per criterion × opportunity), not 2D-nested. Easier to validate and write; renderer groups by `criterion_id` on output.
- `opp_refs[]` is the structural enforcement of the trace-back rule. Schema invariant: if `score ∈ {strong, medium, weak}` then `opp_refs[]` is non-empty; if `score ∈ {unknown, n/a}` then `opp_refs[]` is empty.
- `evidence_gaps[]` is technically derivable from `cells[]` (any cell with `score: "unknown"`), but writing it explicitly lets the AI add a `what_is_missing` sentence per gap. `n/a` cells do not appear here.
- `criteria[]` is denormalized into the JSON output (full definitions, not just IDs). Same precedent as OST-cluster-opportunities carrying the full journey into v0.2 output. Self-documenting; the selector (assist 5) doesn't need to load the anchor to interpret the matrix.
- No effort/feasibility field anywhere in the schema. Structural enforcement of the no-effort rule.

## Steps

The skill follows the same numbered-step pattern as OST-cluster-opportunities. Single pass, no iteration, no retries.

1. **Read knowledge anchors:** the three files listed above.
2. **Locate inputs:**
   - Latest `experience-map-clustered-*.json` in `workspace/1-opportunity-val/` (sorted by `<date>` descending).
   - `workspace/context/product-outcome.md` (fixed path).
3. **Hard-exit checks** (see Error handling). Do not write any output files when these fire.
4. **Parse, filter, and partition.**
   - Parse the clustered JSON. Index `phases[]` by `id`. Walk `phases[].opportunities[]`.
   - Parse the product outcome from `workspace/context/product-outcome.md` - extract the outcome formulation under the `## Outcome` heading. Carry the team name from `## Team`.
   - Partition opportunities by verdict:
     - `verdict == "approved"` → `opportunities_compared[]`. Carry verbatim: `id`, `phase_id`, `quote`, `source`.
     - `verdict ∈ {"needs_tweak", "solution_in_disguise"}` → `opportunities_excluded[]`. Carry `id`, `phase_id`, `verdict`, plus a one-line `reason`.
   - If `opportunities_compared[]` is empty, hard exit.
5. **Compose `criteria[]`** - the five hardcoded criteria, denormalized from the knowledge anchor: outcome-alignment, customer-importance, market-size, strategic-fit, competitive-landscape. Each with `id`, `name`, `description`.
6. **Score each cell** (criterion × approved opportunity):
   - Use the criterion's lens against the opportunity's quote, source, phase placement, and cross-opportunity context within the same cluster.
   - Pick a score from the 5-value vocabulary.
   - Write a 1-2 sentence rationale.
   - Apply the trace-back rule: if `score ∈ {strong, medium, weak}`, the rationale must reference at least one `opp-id` from `opportunities_compared[]`. List every opp-id mentioned in the rationale text in `opp_refs[]`. Typically the cell's own opportunity is cited; cross-references to other opportunities in the cluster are valid when they reinforce the score (e.g., three opportunities referencing the same pain → boosts customer-importance for each).
   - Apply the no-effort rule: if the reasoning chain ever reaches "but it would be hard/easy to build / requires X integration / would scale poorly", remove that step and re-score on the criterion's dimension only.
   - Use `n/a` if the criterion structurally doesn't apply to the trio's context (e.g., "market size" for an internal tool with a fixed user base, "competitive landscape" for an internal tool with no external competitors). `n/a` cells skip the trace-back rule.
   - Use `unknown` if evidence is genuinely thin and an honest non-`unknown` score is not defensible.
   - `opp_refs[]` only references IDs in `opportunities_compared[]`. Do not cite excluded opportunities.
7. **Compose `evidence_gaps[]`** - for each cell where `score == "unknown"`, add one entry with `criterion_id`, `opportunity_id`, and a one-sentence `what_is_missing` describing what evidence would unlock a score. `n/a` cells do not appear here.
8. **Compose the v0.1 JSON.** All fields per the schema. Per the missing-optional convention, omit any optional key whose value isn't set; never write `null`. (For v0.1 the only optional fields are at the document level: `opportunities_excluded[]` and `evidence_gaps[]` may be empty arrays, but never `null`.)
9. **Render the markdown deterministically from the JSON** via the embedded template (Output composition).
10. **Write paired output** to `workspace/2-opportunity-compare/comparison-matrix-<YYYY-MM-DD>.json` and the matching `.md`. Today's date in `YYYY-MM-DD`. Same root name on both files.

The composition is a single pass. No retries, no iteration, no self-validation pass against the schema after composition. Upstream files are never modified.

## Output composition

Two files with the same root name:

```text
workspace/2-opportunity-compare/comparison-matrix-<YYYY-MM-DD>.json
workspace/2-opportunity-compare/comparison-matrix-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.1 from `../knowledge/discovery/opportunity-comparison.md`. No extra fields beyond the schema.

**The markdown** is generated deterministically from the JSON via an embedded template in the prompt:

````markdown
---
title: Comparison matrix - <title> (<team>)
date: <YYYY-MM-DD>
purpose: Opportunity comparison matrix for OST opportunity selection, paired with comparison-matrix-<date>.json
tags: [opportunity-comparison, ost, schema-v0.1]

---

# Comparison matrix: <title> (<team>)

Source clustered map: `experience-map-clustered-<date>.json`
Source product outcome: `workspace/context/product-outcome.md`
Schema version: 0.1
Paired JSON: `comparison-matrix-<YYYY-MM-DD>.json`

## Product outcome

> <full outcome formulation>

## Opportunities compared (<N>)

- **opp-4-1** (Phase: <phase name>) - "<full quote>" - *<source>*
- **opp-4-2** (Phase: <phase name>) - "<full quote>" - *<source>*
- ...

## Excluded from comparison (<N>)

[only if non-empty; otherwise omit this whole section]

- **opp-X-Y** (Phase: <phase name>; verdict: needs_tweak) - <reason>
- **opp-A-B** (Phase: <phase name>; verdict: solution_in_disguise) - <reason>

## Matrix

| Criterion              | opp-4-1 | opp-4-2 | opp-5-1 | ... |
|------------------------|---------|---------|---------|-----|
| Outcome alignment      | strong  | strong  | medium  | ... |
| Customer importance    | strong  | medium  | medium  | ... |
| Market size / frequency| medium  | strong  | strong  | ... |
| Strategic fit          | medium  | strong  | weak    | ... |
| Competitive landscape  | n/a     | n/a     | n/a     | ... |

## Cell rationales

### Outcome alignment

- **opp-4-1** - strong. <rationale prose>. Cites: opp-4-1.
- **opp-4-2** - strong. <rationale prose>. Cites: opp-4-2, opp-4-1.
- **opp-5-1** - medium. <rationale prose>. Cites: opp-5-1.

### Customer importance

- **opp-4-1** - strong. <rationale prose>. Cites: opp-4-1, opp-4-2.
- ...

[repeat one section per criterion, in the order declared in `criteria[]`:
outcome-alignment, customer-importance, market-size, strategic-fit,
competitive-landscape]

## Evidence gaps (<N>)

[only if non-empty; otherwise omit this whole section]

Cells where evidence was thin and an honest score wasn't defensible. Each gap names what evidence would unlock a score.

- **Customer importance × opp-4-3**: <what_is_missing>
- **Market size / frequency × opp-4-3**: <what_is_missing>

## Notes

[only if any criterion scored `n/a` for ALL approved opportunities; otherwise omit this whole section]

- **Competitive landscape** scored `n/a` for all opportunities, suggesting it isn't load-bearing for this trio's context. The trio may consider dropping this criterion in HITL.
````

**Rendering rules:**

- **Score values use full words** in both the matrix table and the rationales: `strong` / `medium` / `weak` / `unknown` / `n/a`. No emoji. (Verdict emoji on OST-cluster-opportunities was a shorthand for a 3-value vocabulary; here we have 5 values, words are clearer and the matrix isn't that wide.)
- **Cites: line.** Every `strong`, `medium`, or `weak` rationale ends with `Cites: opp-X-Y[, opp-A-B...].` listing every opp-id from that cell's `opp_refs[]`. `unknown` and `n/a` cells omit the Cites line entirely.
- **Source attribution** carried verbatim from the clustered JSON. Separated from the quote by ` - ` (regular dash, not em-dash, per the no-em-dash-in-Swedish rule applied uniformly).
- **No em-dash** anywhere, applied uniformly to Swedish and English prose.
- **Criterion display names stay in English** even when quotes and rationales are Swedish. The criteria are Torres-canonical and the kebab-case IDs are English; mixing canonical-English criteria with Swedish rationale prose is normal in product orgs and avoids a translation surface.
- **Output language for prose** (rationales, `what_is_missing`, reasons) matches the source language detected in the clustered JSON's `quote` text and `phases[].name`. Schema field names, JSON key strings, criterion IDs, criterion display names, and score vocabulary stay as defined.
- **Frontmatter on the markdown output** complies with the Metria global rule that every `.md` file has YAML frontmatter, with a blank line before the closing `---`.
- **Empty sections are omitted entirely.** "Excluded from comparison", "Evidence gaps", and "Notes" each omit when their underlying list is empty. Section headings are not rendered for empty lists (no "Evidence gaps (0)").
- **Matrix column order** matches `opportunities_compared[]` order in the JSON, which itself preserves the cluster JSON's traversal order (phases by `order`, then opportunities by their cluster IDs).
- **Matrix row order** matches `criteria[]` order in the JSON: outcome-alignment, customer-importance, market-size, strategic-fit, competitive-landscape.

## Knowledge-doc updates required before ship

As part of building this skill:

- **Create `../knowledge/discovery/opportunity-comparison.md`** (the new anchor). Sections per Inputs and prerequisites above. This is the canonical source for the schema, criteria, score vocabulary, trace-back rule, and no-effort rule.

What is NOT updated:

- `workspace/README.md` - the staged-subdirectory documentation update is a follow-up TODO, not part of this build.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - the comparator references it but doesn't extend it. Torres's content is canonical and the comparator just leans on it.
- `../knowledge/discovery/experience-mapping.md` - the comparator reads schema v0.2 unchanged. No bump.
- `skills-design/skill-template.md` Bygg-status - that gets updated in the implementation plan as a final task (mark `OST-compare-opportunities` built, "5 of 13"), not in this design.

## Error handling

**Hard-exit triggers** (no output files written when these fire):

| Trigger | Looked for | Remedy |
|---|---|---|
| Zero `experience-map-clustered-*.json` in `workspace/1-opportunity-val/` | A clustered experience map | Run `OST-cluster-opportunities` |
| `workspace/context/product-outcome.md` missing | Trio's product outcome file | Restore from git or re-author using the template structure |
| Clustered JSON does not parse | Schema-conformant v0.2 JSON | Re-run `OST-cluster-opportunities` |
| Clustered JSON `schema_version` is not `"0.2"` | `"schema_version": "0.2"` | Re-run `OST-cluster-opportunities` against the latest extracted file |
| Zero approved opportunities after verdict filtering | At least one opportunity with `verdict == "approved"` | Re-run `OST-validate-opportunities` and review verdicts; the comparator cannot compare an empty set |
| Product outcome file has no extractable `## Outcome` section | A heading `## Outcome` followed by the outcome formulation | Re-author `workspace/context/product-outcome.md` using the template structure |
| One or more clustered opportunities missing the `verdict` field | `verdict` set on every opportunity in the clustered JSON | Re-run `OST-cluster-opportunities`; do not hand-edit the clustered JSON |

**Hard-exit message format** (same shape as OST-cluster-opportunities):

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

Three pieces in order: what failed, what the skill saw, what to do about it. No silent degradation. No retries.

**Soft warnings:** None for v1. The comparator's failure modes are tight enough that they're either hard exits or self-policing (the trio catches scoring drift at HITL). The "Known limitations" block in the product outcome file is explicitly NOT flagged - those gaps are accepted by the trio per project memory and the skill scores against the outcome as written.

**Convention for missing optional fields in JSON:** the skill omits the key entirely rather than writing `null`. For v0.1, all cell-level fields are required; the only optional document-level fields are `opportunities_excluded[]` and `evidence_gaps[]` (both written as empty arrays when applicable, never `null`).

**No JSON self-validation pass.** Trust the prompt; downstream skills surface any malformed JSON. Mirrors the precedent set by `OST-extract-experience-map` and `OST-cluster-opportunities`.

## What this skill does NOT do

- **Read interview transcripts.** Quotes come from the clustered JSON.
- **Read the original `opportunities-extracted-*` or `opportunities-validated-*` files.** All quotes, sources, and verdicts the comparator needs are already in the clustered JSON.
- **Validate citation format.** That is `OST-validate-opportunities` upstream.
- **Re-cluster opportunities or change phase placement.** That is `OST-cluster-opportunities`.
- **Modify upstream files.** `experience-map-clustered-*.json` and `product-outcome.md` stay immutable.
- **Compare opportunities against criteria other than the five hardcoded ones.** The criteria list is fixed in v0.1. Configurability is parked for v0.2.
- **Sum, average, or otherwise aggregate scores across criteria.** The matrix is for comparison, not ranking. The selector decides.
- **Pick a winning opportunity.** That is the selector (assist 5).
- **Generate solutions for any opportunity.** That is downstream of the selector.
- **Weigh effort, feasibility, integration cost, or implementation complexity.** Per Torres. Enforced as a first-class output principle, not a validation pass.
- **Compare `needs_tweak` or `solution_in_disguise` opportunities.** They're filtered out at step 4 with a visible note.
- **Score cells with confidence values outside the 5-value vocabulary.** No "high-medium" or numeric scores.
- **Use emoji or numeric encoding for scores.** Words only.
- **Iterate, retry, or run multiple passes.** One pass over the inputs, one pair of output files.
- **Run a JSON self-validation pass after composition.**
- **Write to Miro or any external surface.** JSON + markdown only.
- **Audit the cluster JSON for invariant violations** (e.g., parent-child consistency, step_id references). The comparator only filters by verdict and reads quote/source/phase fields.
- **Ask the trio for clustering choices interactively.** If a cell is genuinely uncertain, score `unknown` and add a gap entry; don't ask.
- **Mark accepted gaps in the product outcome's "Known limitations" section as problems.** Those gaps are trio-accepted per project memory. The comparator scores against the outcome as written.

## Testing

Smoke test only for v1, no formal regression harness. Reuses the Norrsken cluster output from OST-cluster-opportunities's smoke test as the integration fixture. The clustered file has 6 approved + 1 needs_tweak + 1 solution_in_disguise opportunities, and the product outcome at `workspace/context/product-outcome.md` is the Norrsken licens-tilldelning outcome.

```text
Inputs:
  workspace/1-opportunity-val/experience-map-clustered-2026-05-09.json
    (6 approved + 2 excluded opportunities)
  workspace/context/product-outcome.md
    (Norrsken licens-tilldelning outcome with declared accepted limitations)

Expect:
  - schema_version "0.1" in the output JSON
  - opportunities_compared has 6 items (the approved ones)
  - opportunities_excluded has 2 items (verdict needs_tweak + solution_in_disguise),
    each with a one-line reason
  - criteria has 5 items in the canonical order
  - cells has 5 * 6 == 30 items
  - For every cell with score in {strong, medium, weak}, opp_refs is non-empty
  - For every cell with score in {unknown, n/a}, opp_refs is empty
  - Every opp_ref points to an ID in opportunities_compared
  - evidence_gaps entries map 1:1 to cells with score == "unknown"
  - n/a cells do not appear in evidence_gaps
  - No rationale text contains effort-thinking words ("complex", "easy",
    "expensive", "feasible", "scalable", "low-hanging fruit", etc.) - eyeball
  - Markdown matrix table renders 5 rows × 6 opportunity columns
  - Per-criterion rationale sections render in the criteria[] order, with
    one bullet per (criterion, opportunity), each ending with
    "Cites: opp-X-Y[, opp-A-B...]." for non-unknown cells
  - "Excluded from comparison" section renders both verdicts with reasons
  - "Evidence gaps" section renders if any unknown cells exist
  - "Notes" section renders an all-n/a observation if competitive landscape
    (or any other criterion) scored n/a for all 6 opportunities
  - Frontmatter present, blank line before closing ---
  - No em-dash anywhere in markdown body
```

Plausible expected behaviors against the Norrsken fixture:

- **Outcome alignment** likely scores strong-medium for most opportunities (they're all in the licens-tilldelning territory, which is exactly the outcome's domain).
- **Customer importance** likely varies. The säljare-channel opportunity (opp-1-1 in the cluster) and the Pernilla "kreditkontrollen" opportunity are widely felt; the rapportering one in `fas-0-unphased` was already excluded by phase, so it shouldn't even appear here unless approved.
- **Market size / frequency** likely scores `n/a` or `unknown` across the board for an internal Metria tool. The fixture exercises this case.
- **Strategic fit** likely scores strong-medium (Norrsken is the strategic platform).
- **Competitive landscape** likely scores `n/a` for all opportunities (internal tool with no external competitors). This triggers the "Notes" section render in the markdown. The fixture exercises that path.

Eyeball the JSON output and the rendered markdown. If the matrix is empty, verdicts didn't filter, scores are numeric, rationales lack `Cites:`, or effort-thinking shows up in any rationale, the prompt is wrong. A formal regression harness is overkill for v1.

## Open follow-ups

These are added to `TODO.md` rather than blocking v1.

1. **Workspace README staging-convention update.** Document the `1-opportunity-val/`, `2-opportunity-compare/`, and onward staging convention so trios reading the README first don't see a stale flat-root description.
2. **Schema evolution beyond v0.1.** Bumps when (a) downstream skills request new fields or (b) trios produce structures v0.1 cannot represent. Procedure same as experience-mapping: add an "Evolution" entry to `opportunity-comparison.md` and bump `schema_version` in the skill prompt.
3. **Configurable criteria per trio.** Currently the five Torres-derived criteria are hardcoded. If trios want to swap, drop, or extend criteria for their context, surface this as a configurable list in the knowledge anchor (consumed by the prompt) rather than wiring it through every skill run. Revisit only after 2-3 trios have run the comparator.
4. **Effort-creep self-policing.** If trios catch the comparator weighing effort despite the no-effort rule, add either a forbidden-vocabulary blocklist or a post-composition validation pass. Currently parked.
5. **Confidence/guessing visibility beyond trace-back.** If trace-back via `opp_refs[]` turns out to under-signal "this score is reasoned, not grounded", add an explicit per-cell flag or split the rationale into Evidence/Reasoning blocks.
6. **Pairwise comparison output for the selector.** The selector (assist 5) reads this matrix and picks. If it needs explicit pairwise rankings (opp-A vs opp-B on each criterion) rather than per-cell scores, that's a comparator-output extension or a selector-internal computation. Decide during selector design.
7. **Skill-template body-language line.** Already carried from OST-cluster-opportunities's open follow-ups; on the cleanup list.
8. **Evidence-source scope.** The SKILL.md prompt does not explicitly enumerate which fields in the clustered JSON count as legitimate evidence for a cell rationale. The first-run smoke-test (commit `9fa8663`, opp-4-2 outcome-alignment) cited the experience map's `narrativ` field (an extension surface) as evidence. The score is defensible, but a future SKILL.md version should explicitly license or restrict the evidence surface (e.g., `quote`, `source`, phase name, step description, `narrativ` — or restrict to `quote` and `source` only).
9. **"Independence" semantic in cross-opportunity citations.** The first-run smoke-test (commit `9fa8663`, opp-4-1 customer-importance) framed two quotes from the same interviewee as "två oberoende citat", overstating cross-customer independence. The trace-back rule does not currently constrain what "independent" means when an `opp_refs[]` list contains multiple IDs. A future SKILL.md prompt could clarify that "independent" means cross-customer (different sources), not cross-quote within the same interview.
