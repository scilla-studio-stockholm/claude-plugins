---
title: "OST-select-opportunity: design spec"
date: 2026-05-10
purpose: Locked design for assist 5 in opportunity-solution-tree-agents.md - takes the v0.1 comparison-matrix JSON from OST-compare-opportunities (assist 4) and the trio's product outcome, applies a locked three-step decision rule (outcome-alignment filter, strongest-aggregate-profile rank, fewer-evidence-gaps tiebreak), and produces a paired JSON + markdown chosen-opportunity proposal with rationale, every other approved opportunity as an alternative-considered, and an AI-judged subset of evidence gaps to carry into phase 2. Input to the implementation plan.
tags: [skill-design, ost, opportunity-selection, schema-v0.1]

---

# OST-select-opportunity: design spec

This is the locked design for **assist 5** in `opportunity-solution-tree-agents.md`. It is the sixth skill built, after `OST-opportunity-extractor`, `OST-validate-opportunities`, `OST-extract-experience-map`, `OST-cluster-opportunities`, and `OST-compare-opportunities`. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when selecting one opportunity from an approved set already compared against a product outcome and Torres criteria, output a paired JSON + markdown proposal with the chosen opportunity, its rationale, every other approved opportunity as an alternative-considered (with reason not picked), and an AI-judged subset of the chosen opportunity's evidence gaps to carry into phase 2.

Input is the comparison-matrix JSON (v0.1 from `OST-compare-opportunities`) and the trio's product outcome at `workspace/context/product-outcome.md`. Output is two files in `workspace/3-opportunity-select/` with the same root name: a chosen-opportunity JSON conforming to schema v0.1 in a new knowledge anchor `../knowledge/discovery/opportunity-selection.md`, and a markdown rendering generated deterministically from the JSON.

The skill produces a **proposal**, not a decision-of-record. The trio reviews the proposal, overrides if it disagrees, and ratifies the final pick into `workspace/context/chosen-opportunity.md` (which assist 6 reads). The selector itself does not write to `workspace/context/`.

## Scope decisions (locked 2026-05-10)

The brainstorm narrowed scope from the open questions in `opportunity-solution-tree-agents.md` (lines 438-442) and added several mechanical decisions. Each decision below resolves an open question.

| Question | Decision |
|---|---|
| HITL flavor | Picks one + alternatives. The AI commits to a single chosen opportunity with rationale; lists every other approved opportunity as an alternative-considered with a 1-2 sentence reason not picked. Trio reviews and ratifies separately. |
| Decision rule | Three-step rule: **(1) Filter** opportunities scoring `weak` or `unknown` on `outcome-alignment` (deprioritize). **(2) Rank** the remaining by strongest aggregate profile (most `strong` scores, fewest `weak` and `unknown` scores; `n/a` is neutral). **(3) Tiebreak** on fewer evidence gaps (fewer `unknown` cells in the chosen opp's column). Edge case: if step 1 empties the candidate set, fall back to "best of the rest" using the highest outcome-alignment score available, and the rationale names this fallback explicitly. |
| Tie handling | Force a pick; name the tied opp(s) explicitly in the rationale prose; populate `decision_signals.tie_with[]` with the tied opp-ids. No separate "coin-flip" header or warning chrome. |
| Calibration tone | Confident rationale on clean wins, transparent rationale on close calls (implied by tie handling). |
| Output location | `workspace/3-opportunity-select/`. Stage-numbered convention continuing `1-opportunity-val/` and `2-opportunity-compare/`. The workspace README's `workspace/context/chosen-opportunity.md` is the trio's ratification target, not the skill's write target. The staging-convention README update is the same follow-up TODO already opened by OST-compare-opportunities. |
| Output format | Paired JSON + markdown. JSON gives assist 6 a parseable contract; markdown is the trio's review surface. |
| Schema location | New knowledge anchor `../knowledge/discovery/opportunity-selection.md` (mirrors the comparator and experience-mapping precedents). Schema is v0.1. |
| Evidence-gap carry-forward | AI-judged subset of the chosen opportunity's `unknown` cells from the matrix. Symmetric `evidence_gaps_carried[]` / `evidence_gaps_excluded[]` lists, both with reason fields, so the AI's filter judgement is auditable rather than a black box. `n/a` cells are structural, not gaps; they appear in neither list. |
| Skill vs agent | Plain skill. Single-pass over a small structured input. No agent-style state, no retries, no tool-use beyond Read. The decision rule is deterministic enough that a single composition pass suffices. |
| Slug name | `OST-select-opportunity`. Verb-first matches `OST-validate-opportunities`, `OST-cluster-opportunities`, `OST-compare-opportunities`, `OST-extract-experience-map`. Singular noun reflects that the output is one chosen opportunity (mirrors `OST-extract-experience-map`'s singular-noun pattern). |
| Cites convention | No structural `Cites:` line. The comparator had per-cell `opp_refs[]` that needed structural enforcement; the selector's rationale references opp-ids inline naturally and there is no per-cell trace-back invariant to audit. |
| Output directory creation | Skill creates `workspace/3-opportunity-select/` lazily if it does not exist. |
| Output filename | `chosen-opportunity-<YYYY-MM-DD>.{json,md}` per cross-cutting datakontrakt. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-select-opportunity/SKILL.md` |
| Skill name | `OST-select-opportunity` |
| Slash-command (optional) | `/OST-select-opportunity` if frequency justifies it |
| Body language | English, matching the precedent set by `OST-validate-opportunities`, `OST-extract-experience-map`, `OST-cluster-opportunities`, and `OST-compare-opportunities` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when selecting one opportunity from an approved set already compared against a product outcome and Torres criteria, output a paired JSON + markdown proposal with the chosen opportunity, rationale, every other approved opportunity as an alternative considered, and an AI-judged subset of evidence gaps to carry into phase 2.

This follows the "for X, when Y, output Z" pattern. It is generic, not Metria-specific. It is distinct from `OST-compare-opportunities` (produces the matrix; doesn't pick), `OST-cluster-opportunities` (clusters against an experience map; doesn't compare), and `OST-validate-opportunities` (per-opportunity verdict; no comparison).

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/2-opportunity-compare/comparison-matrix-<date>.json` | `OST-compare-opportunities` (assist 4) | Source of approved opportunities, their quotes, sources, phase placement, comparison cells, and evidence gaps |
| `workspace/context/product-outcome.md` | Trio-authored, fixed path | Outcome formulation that grounds the rationale's outcome-alignment narrative |

**File-resolution rules:** Latest file matching `comparison-matrix-*.json` by `<date>` in filename, descending. The product outcome is at a fixed path with no date suffix.

**Knowledge anchors read at runtime:**

- `../knowledge/discovery/opportunity-selection.md` (NEW, created as part of this build) - the JSON schema, the decision rule, the tie-handling convention, the evidence-gap-filter convention, the no-effort reminder.
- `../knowledge/discovery/opportunity-comparison.md` - the matrix schema (v0.1) so the selector can read the comparator's output, and the criteria/score-vocabulary definitions used in the rationale prose.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - Torres principles, especially "Don't assess effort during opportunity selection" (carried from the comparator and reinforced for selector rationale prose).

Per the cross-cutting datakontrakt decision, anchors are read at runtime rather than hard-coded into the prompt.

**What the skill does NOT consume:**

- The clustered experience-map JSON (`experience-map-clustered-*.json`). Every quote, source, phase, score, and rationale the selector needs is already in the comparison matrix.
- The original `opportunities-extracted-*` or `opportunities-validated-*` files.
- Interview transcripts.
- A schema file. The schema lives in the new knowledge anchor.

## The new knowledge anchor: `../knowledge/discovery/opportunity-selection.md`

This anchor carries the same role for the selector that `opportunity-comparison.md` carries for the comparator: it owns the schema, the decision rule, the tie-handling convention, the gap-filter convention, and the framework prose. Created as a one-time write during this skill's build; not modified at runtime.

Sections in the anchor:

1. **What the selector does** - short framework prose tying it to Torres CDH ch 7 step 4 of the OST process ("Select one target opportunity"). Notes that the selector consumes the comparator's output and produces a proposal that the trio ratifies.
2. **The decision rule** - the locked three-step rule (filter, rank, tiebreak) with the empty-candidate-set fallback.
3. **Tie handling** - force pick, name tied opp(s) inline in the rationale, populate `decision_signals.tie_with[]`. No separate header.
4. **The evidence-gap filter** - AI-judged carried/excluded with reason fields. `n/a` cells are not gaps.
5. **The no-effort rule** - carried from the OST anchor and the comparator. The rationale and reason-not-picked prose must not introduce effort thinking.
6. **JSON schema (v0.1)** - the contract.
7. **Field notes** - per-field commentary including the missing-optional convention.
8. **Open questions** - what's punted to v0.2.
9. **Evolution** - version history.

**Schema v0.1:**

```json
{
  "schema_version": "0.1",
  "team": "string (carried from comparison matrix)",
  "title": "string (carried from comparison matrix)",
  "product_outcome": "string (carried from comparison matrix)",
  "source_comparison_matrix": "string (filename of source comparison-matrix-*.json)",
  "chosen_opportunity": {
    "id": "string (e.g., 'opp-5-1'; matches an id in the matrix's opportunities_compared[])",
    "phase_id": "string (carried from comparison matrix)",
    "quote": "string (carried verbatim)",
    "source": "string (carried verbatim)"
  },
  "chosen_opportunity_scores": [
    {
      "criterion_id": "string (e.g., 'outcome-alignment')",
      "score": "strong | medium | weak | unknown | n/a"
    }
  ],
  "rationale": "string (2-4 sentences using the locked decision rule: outcome-alignment first, strongest-aggregate-profile rank, evidence-gap tiebreak; mentions opp-ids and criterion names; on tied picks, names the tied opp(s) explicitly)",
  "decision_signals": {
    "outcome_alignment_score_for_chosen": "strong | medium | weak | unknown | n/a",
    "profile_summary": "string (one-line tally, e.g., '4 strong, 0 medium, 0 weak, 0 unknown, 1 n/a')",
    "tie_with": ["string (opp-ids the chosen was tied with at any decision step; empty array if unambiguous)"]
  },
  "alternatives_considered": [
    {
      "id": "string (carried verbatim from matrix opportunities_compared[])",
      "phase_id": "string",
      "quote": "string (carried verbatim)",
      "source": "string (carried verbatim)",
      "reason_not_picked": "string (1-2 sentences anchored in matrix scores)"
    }
  ],
  "evidence_gaps_carried": [
    {
      "criterion_id": "string (carried from matrix evidence_gaps[])",
      "what_is_missing": "string (carried verbatim from matrix evidence_gaps[], or lightly rephrased)",
      "why_relevant_to_phase_2": "string (1 sentence on why this gap affects solution evaluation)"
    }
  ],
  "evidence_gaps_excluded": [
    {
      "criterion_id": "string",
      "what_is_missing": "string",
      "why_excluded": "string (1 sentence on why this gap doesn't affect solution work)"
    }
  ]
}
```

**Schema design notes:**

- `chosen_opportunity` is a singular object. We picked one; not forward-designing for multi-pick which we explicitly rejected (HITL flavor: picks one + alternatives).
- `chosen_opportunity_scores[]` is denormalized at the top level so assist 6 can read the chosen opp's score profile without reloading the matrix. Five entries (one per criterion) for v0.1.
- `decision_signals.tie_with[]` is the structured signal for tied picks. Empty when the pick is unambiguous. The rationale prose still names the tie inline; this field is the parseable counterpart.
- `alternatives_considered[]` contains every other approved opportunity from the matrix (count = `|opportunities_compared| - 1`). Carries the same `id`, `phase_id`, `quote`, `source` fields as the chosen, plus a `reason_not_picked`. Self-contained; trio reads alternatives without reloading the matrix.
- `evidence_gaps_carried[]` and `evidence_gaps_excluded[]` are a symmetric pair so the AI's filter judgement is auditable. Their union (by `criterion_id`) equals the chosen opportunity's `unknown`-cell set in the matrix; their intersection is empty. `n/a` cells appear in neither.
- No effort/feasibility field anywhere. Structural enforcement of the no-effort rule.

**Schema invariants:**

- `chosen_opportunity.id` ∈ matrix `opportunities_compared[].id`.
- `chosen_opportunity_scores[].criterion_id` covers all 5 criteria from the matrix's `criteria[]`.
- `alternatives_considered[].id` set equals matrix `opportunities_compared[].id` minus `chosen_opportunity.id`.
- `evidence_gaps_carried[]` and `evidence_gaps_excluded[]` together cover every matrix cell where `score == "unknown"` AND `opportunity_id == chosen_opportunity.id`. Intersection is empty.
- `decision_signals.tie_with[]` references only opp-ids in `opportunities_compared[]` (excluding `chosen_opportunity.id`).
- No effort vocabulary in `rationale`, `reason_not_picked`, `why_relevant_to_phase_2`, or `why_excluded` (eyeballed at smoke test, not validated by post-pass).

## Steps

The skill follows the same numbered-step pattern as OST-compare-opportunities. Single pass, no iteration, no retries.

1. **Read knowledge anchors:** the three files listed above.
2. **Locate inputs:**
   - Latest `comparison-matrix-*.json` in `workspace/2-opportunity-compare/` (sorted by `<date>` descending).
   - `workspace/context/product-outcome.md` (fixed path).
3. **Hard-exit checks** (see Error handling). Do not write any output files when these fire.
4. **Parse inputs.**
   - Parse the matrix JSON. Index `opportunities_compared[]` by `id`. Build a per-opportunity score map from `cells[]` (key: `(criterion_id, opportunity_id)`, value: `score`).
   - Parse the product outcome from `workspace/context/product-outcome.md` - extract the outcome formulation under the `## Outcome` heading. Carry the team name from `## Team`.
5. **Apply step 1 of the decision rule (filter).** Identify opportunities where `outcome-alignment` score is `weak` or `unknown`. These are deprioritized. The remaining set is the candidate pool.
   - **Edge case:** if the candidate pool is empty (every approved opp scored `weak` or `unknown` on outcome-alignment), fall back to "best of the rest": include opportunities with the highest available outcome-alignment score (e.g., if no `strong`/`medium` exists, include all `weak`s; if no `weak`s, include `unknown`s). The `rationale` must explicitly name the fallback ("No opportunity scored strong/medium on outcome-alignment; falling back to ...").
6. **Apply step 2 of the decision rule (rank).** Among the candidate pool, score each opportunity's profile across the other 4 criteria: count `strong`, `medium`, `weak`, `unknown`. `n/a` is neutral (does not count as positive or negative). Pick the opportunity with the strongest profile by this ordering: more `strong` is better; among equal `strong` counts, fewer `weak` is better; among equal `weak` counts, fewer `unknown` is better.
7. **Apply step 3 of the decision rule (tiebreak).** If two or more opportunities tie under step 2, prefer the one with fewer `unknown` cells across all 5 criteria (including outcome-alignment). If still tied, prefer the one with the better outcome-alignment score (`strong` > `medium` > `weak` > `unknown`). If still tied, force a pick (any of the tied opps, AI's choice) and populate `decision_signals.tie_with[]` with the tied opp-ids. The rationale must name the tie inline.
8. **Compose `chosen_opportunity`, `chosen_opportunity_scores`, `decision_signals`.**
   - `chosen_opportunity`: carry `id`, `phase_id`, `quote`, `source` verbatim from the matrix.
   - `chosen_opportunity_scores`: one entry per criterion, with the score from the matrix's cells.
   - `decision_signals.outcome_alignment_score_for_chosen`: pulled from the matrix.
   - `decision_signals.profile_summary`: one-line tally (e.g., `"4 strong, 0 medium, 0 weak, 0 unknown, 1 n/a"`).
   - `decision_signals.tie_with`: opp-ids tied with the chosen at any decision step (empty if unambiguous).
9. **Compose `rationale`.** 2-4 sentences explaining the pick using the locked decision rule. Mentions opp-ids and criterion names by their canonical English form. On tied picks, names the tied opp(s) explicitly. On the empty-candidate-set fallback, names the fallback explicitly. No effort vocabulary.
10. **Compose `alternatives_considered`.** One entry for every other opp in `opportunities_compared[]` (matrix - chosen). For each: carry `id`, `phase_id`, `quote`, `source`. Write a 1-2 sentence `reason_not_picked` anchored in matrix scores (e.g., "Profile is weaker than chosen on customer-importance and market-size") or in the decision-rule step that filtered it (e.g., "Deprioritized at step 1: scored weak on outcome-alignment"). No effort vocabulary.
11. **Compose `evidence_gaps_carried` and `evidence_gaps_excluded`.**
   - Walk matrix `evidence_gaps[]` for entries where `opportunity_id == chosen_opportunity.id`. (Do NOT pull gaps from other opportunities; the carry-forward is chosen-only.)
   - For each gap, judge whether it would affect phase-2 solution evaluation:
     - **Carried:** the gap describes evidence that would change which solutions are reasonable, how to prioritize them, or how to test them. Add to `evidence_gaps_carried[]` with a 1-sentence `why_relevant_to_phase_2`.
     - **Excluded:** the gap is real but doesn't affect solution work (e.g., political/governance unknowns, market-size unknowns when the chosen opp is internal-only). Add to `evidence_gaps_excluded[]` with a 1-sentence `why_excluded`.
   - The two lists together cover every chosen-opp `unknown` cell. `n/a` cells are not gaps and appear in neither list.
12. **Compose the v0.1 JSON.** All fields per the schema. Per the missing-optional convention, omit any optional key whose value isn't set; never write `null`. (For v0.1 the only optional fields are `decision_signals.tie_with[]`, `evidence_gaps_carried[]`, and `evidence_gaps_excluded[]`, all written as empty arrays when applicable, never `null`.)
13. **Render the markdown deterministically from the JSON** via the embedded template (Output composition).
14. **Write paired output** to `workspace/3-opportunity-select/chosen-opportunity-<YYYY-MM-DD>.json` and the matching `.md`. Today's date in `YYYY-MM-DD`. Same root name on both files. Create `workspace/3-opportunity-select/` if it doesn't exist.

The composition is a single pass. No retries, no iteration, no self-validation pass against the schema after composition. Upstream files (matrix JSON, product outcome) are never modified. The skill does NOT write to `workspace/context/chosen-opportunity.md` - that is the trio's ratification step.

## Output composition

Two files with the same root name:

```text
workspace/3-opportunity-select/chosen-opportunity-<YYYY-MM-DD>.json
workspace/3-opportunity-select/chosen-opportunity-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.1 from `../knowledge/discovery/opportunity-selection.md`. No extra fields beyond the schema.

**The markdown** is generated deterministically from the JSON via an embedded template in the prompt:

````markdown
---
title: Chosen opportunity - <title> (<team>)
date: <YYYY-MM-DD>
purpose: Selector proposal for OST opportunity selection, paired with chosen-opportunity-<date>.json. Trio reviews and ratifies into workspace/context/chosen-opportunity.md.
tags: [opportunity-selection, ost, schema-v0.1]

---

# Chosen opportunity: <title> (<team>)

Source comparison matrix: `comparison-matrix-<date>.json`
Source product outcome: `workspace/context/product-outcome.md`
Schema version: 0.1
Paired JSON: `chosen-opportunity-<YYYY-MM-DD>.json`

> **Trio HITL:** This is the AI's proposal. Review the rationale, override if you disagree, then ratify into `workspace/context/chosen-opportunity.md` (which assist 6 reads).

## Product outcome

> <full outcome formulation>

## Chosen opportunity

**<chosen.id>** (Phase: <phase name>) - "<chosen.quote>" - *<chosen.source>*

### Score profile

| Criterion               | Score   |
|-------------------------|---------|
| Outcome alignment       | <score> |
| Customer importance     | <score> |
| Market size / frequency | <score> |
| Strategic fit           | <score> |
| Competitive landscape   | <score> |

Profile summary: <decision_signals.profile_summary>.

### Rationale

<rationale prose, 2-4 sentences. Mentions opp-ids and criterion names; on tied picks, names the tied opp(s) explicitly so the trio sees the closeness.>

## Alternatives considered (<N>)

- **opp-X-Y** (Phase: <phase>) - "<quote>" - *<source>*
  Reason not picked: <1-2 sentences anchored in matrix scores>
- **opp-A-B** (Phase: <phase>) - "<quote>" - *<source>*
  Reason not picked: <...>
- ...

## Evidence gaps carried into phase 2 (<N>)

[only if non-empty; otherwise omit this whole section]

These gaps from the chosen opportunity affect how phase-2 solutions are evaluated.

- **<criterion display name>**: <what_is_missing>
  *Why relevant: <why_relevant_to_phase_2>*
- ...

## Evidence gaps not carried (<N>)

[only if non-empty; otherwise omit this whole section]

These gaps from the chosen opportunity were judged not to affect phase-2 solution work. Listed for transparency; trio may decide to investigate them anyway.

- **<criterion display name>**: <what_is_missing>
  *Why excluded: <why_excluded>*
- ...
````

**Rendering rules:**

- **Score values use full words** in the score-profile table and in any inline reference: `strong` / `medium` / `weak` / `unknown` / `n/a`. No emoji, no numeric encoding.
- **Source attribution** carried verbatim from the matrix JSON (which carried it verbatim from the cluster). Separated from the quote by ` - ` (regular dash, not em-dash).
- **No em-dash** anywhere, applied uniformly to Swedish and English prose.
- **Criterion display names stay in English** even when quotes and rationales are Swedish. The criteria are Torres-canonical and the kebab-case IDs are English; mixing canonical-English criteria with Swedish rationale prose is normal in product orgs and avoids a translation surface.
- **Output language for prose** (`rationale`, `reason_not_picked`, `why_relevant_to_phase_2`, `why_excluded`) matches the source language detected in the matrix's `quote` text and `phase` placement. Schema field names, JSON key strings, criterion IDs, criterion display names, and score vocabulary stay as defined.
- **Frontmatter on the markdown output** complies with the Metria global rule that every `.md` file has YAML frontmatter, with a blank line before the closing `---`.
- **Empty optional sections are omitted entirely.** "Evidence gaps carried into phase 2" and "Evidence gaps not carried" each omit when their underlying list is empty. Section headings are not rendered for empty lists.
- **Tie callouts live inline in the rationale prose.** No separate "tie note" or "coin-flip" section.
- **No `Cites:` line** anywhere. The selector's rationale references opp-ids inline; there is no per-cell trace-back invariant to enforce.
- **Section order is fixed** and the AI does not insert ad-hoc sections.
- **The HITL banner** (`> **Trio HITL:** ...`) is a fixed string in the template, rendered verbatim every run. It is the trio's reminder that the file is a proposal, not a decision.

## Knowledge-doc updates required before ship

As part of building this skill:

- **Create `../knowledge/discovery/opportunity-selection.md`** (the new anchor). Sections per The new knowledge anchor above. This is the canonical source for the schema, decision rule, tie-handling convention, gap-filter convention, and no-effort reminder.
- **Fix the typo on `skills-design/opportunity-solution-tree-agents.md` line 464.** Currently reads `"Vald opportunity plus rationale (från assist 7)"`. Should read `"Vald opportunity plus rationale (från assist 5)"` (assist 6 reads from the selector, which is assist 5; assist 7 is the downstream solution clusterer). Trivial Edit, included in this build.

What is NOT updated:

- `workspace/README.md` - the staging-subdirectory documentation update is the same follow-up TODO already opened by OST-compare-opportunities. The README's `workspace/context/chosen-opportunity.md` line is correct as the trio's ratification target; only the staging-dir convention needs catch-up.
- `../knowledge/discovery/opportunity-comparison.md` - the selector reads schema v0.1 unchanged. No bump.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - the selector references it but doesn't extend it.
- `skills-design/skill-template.md` Bygg-status - that gets updated in the implementation plan as a final task (mark `OST-select-opportunity` built, "6 of 13"), not in this design.

## Error handling

**Hard-exit triggers** (no output files written when these fire):

| Trigger | Looked for | Remedy |
|---|---|---|
| Zero `comparison-matrix-*.json` in `workspace/2-opportunity-compare/` | A comparison matrix | Run `OST-compare-opportunities` |
| `workspace/context/product-outcome.md` missing | Trio's product outcome file | Restore from git or re-author using the template structure |
| Matrix JSON does not parse | Schema-conformant v0.1 JSON | Re-run `OST-compare-opportunities` |
| Matrix JSON `schema_version` is not `"0.1"` | `"schema_version": "0.1"` | Re-run `OST-compare-opportunities` against the latest clustered map |
| Zero items in matrix `opportunities_compared[]` | At least one approved opportunity in the matrix | Re-run `OST-validate-opportunities` and review verdicts; the selector cannot select from an empty set |
| Product outcome file has no extractable `## Outcome` section | A heading `## Outcome` followed by the outcome formulation | Re-author `workspace/context/product-outcome.md` using the template structure |

**Hard-exit message format** (same shape as OST-compare-opportunities):

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

Three pieces in order: what failed, what the skill saw, what to do about it. No silent degradation. No retries.

**Soft warnings:** None for v1. Notable degenerate-but-valid case: a matrix with only 1 approved opportunity. The selector trivially picks it; `alternatives_considered[]` renders as empty. Not flagged, not blocked. The trio sees the empty section and infers. (Open follow-up if this lands wrong in practice.)

**Convention for missing optional fields in JSON:** the skill omits the key entirely rather than writing `null`. For v0.1, the only optional fields are `decision_signals.tie_with[]`, `evidence_gaps_carried[]`, and `evidence_gaps_excluded[]`, all written as empty arrays when applicable, never `null`.

**No JSON self-validation pass.** Trust the prompt; downstream skills surface any malformed JSON. Mirrors the precedent set by `OST-extract-experience-map`, `OST-cluster-opportunities`, and `OST-compare-opportunities`.

## What this skill does NOT do

- **Read interview transcripts.** Quotes come from the comparison matrix.
- **Read the clustered experience-map JSON, validated table, or extracted opportunities.** All quotes, sources, scores, and rationales the selector needs are already in the comparison matrix.
- **Re-validate, re-cluster, or re-compare.** Those are upstream skills.
- **Modify upstream files.** `comparison-matrix-*.json` and `product-outcome.md` stay immutable.
- **Write to `workspace/context/chosen-opportunity.md`.** The skill writes only to `workspace/3-opportunity-select/`. Ratification into `context/` is the trio's step, manual and deliberate.
- **Pick more than one opportunity.** HITL flavor is locked as picks-one + alternatives.
- **Produce a shortlist.** Even on tied picks, the AI commits to one and names the tie in the rationale.
- **Produce a free-form recommendation without alternatives.** Every other approved opportunity from the matrix appears in `alternatives_considered[]` with a `reason_not_picked`.
- **Sum, average, or otherwise aggregate matrix scores into a numeric ranking.** The decision rule operates on score profiles qualitatively. Pattern-matching, not arithmetic.
- **Weigh effort, feasibility, integration cost, or implementation complexity.** Per Torres. The matrix already enforced no-effort scoring; the rationale and reason-not-picked prose must not introduce effort thinking either.
- **Generate solutions for the chosen opportunity.** That is downstream (assist 6).
- **Re-introduce excluded opportunities** (verdict `needs_tweak` or `solution_in_disguise`) into the candidate set. The matrix already filtered them.
- **Iterate, retry, or run multiple passes.** One pass over the inputs, one pair of output files.
- **Run a JSON self-validation pass after composition.**
- **Write to Miro or any external surface.** JSON + markdown only.
- **Audit the matrix JSON for invariant violations** beyond what's needed to apply the decision rule. The selector trusts the comparator's output.
- **Ask the trio for a pick interactively.** If the matrix is genuinely ambiguous, force a pick and populate `decision_signals.tie_with[]`; don't ask.
- **Carry evidence gaps from non-chosen opportunities.** The carry-forward is chosen-only, by design (the trio's phase-2 work is on the chosen opp; other opps' gaps are in the matrix if needed).
- **Use a `Cites:` line in the markdown.** No per-cell trace-back invariant; opp-ids referenced inline.
- **Use emoji or numeric encoding for scores or in tie callouts.** Words only, prose only.

## Testing

Smoke test only for v1, no formal regression harness. Reuses the Norrsken comparison-matrix from OST-compare-opportunities's smoke test as the integration fixture: `workspace/2-opportunity-compare/comparison-matrix-2026-05-10.json` (6 approved opportunities × 5 criteria = 30 cells, 1 evidence gap on opp-0-1 × market-size, all competitive-landscape cells `n/a`). Product outcome at `workspace/context/product-outcome.md` (Norrsken licens-tilldelning).

```text
Inputs:
  workspace/2-opportunity-compare/comparison-matrix-2026-05-10.json
    (6 approved opportunities, 30 cells, 1 evidence gap)
  workspace/context/product-outcome.md
    (Norrsken licens-tilldelning outcome with declared accepted limitations)

Expect:
  - schema_version "0.1" in the output JSON
  - chosen_opportunity.id is "opp-5-1" (Delfi licens-upplägg)
    [Reasoning: opp-0-1 deprioritized at step 1 (weak on outcome-alignment).
     Among remaining 5, opp-5-1 has the cleanest profile: 4 strong, 0 medium,
     0 weak, 0 unknown, 1 n/a. No tie at step 2; no tiebreak needed.]
  - chosen_opportunity_scores has 5 items, one per criterion
  - decision_signals.outcome_alignment_score_for_chosen == "strong"
  - decision_signals.profile_summary names "4 strong" and "1 n/a"
  - decision_signals.tie_with is empty (no tie at step 2 or 3)
  - alternatives_considered has 5 items (opp-1-1, opp-4-1, opp-4-2, opp-6-1,
    opp-0-1) - exactly |opportunities_compared| - 1
  - alternatives_considered[opp-0-1].reason_not_picked names the step-1
    outcome-alignment filter explicitly
  - evidence_gaps_carried is empty (opp-5-1 has zero unknown cells)
  - evidence_gaps_excluded is empty (opp-5-1 has zero unknown cells)
  - rationale mentions "opp-5-1" and at least "outcome-alignment" by name
  - rationale does NOT mention effort vocabulary (complex, easy, expensive,
    feasible, scalable, low-hanging fruit, quick win, ambitious, etc.) - eyeball
  - Markdown frontmatter present with blank line before closing ---
  - Markdown HITL banner renders verbatim
  - Markdown score-profile table renders 5 rows
  - Markdown alternatives section has 5 entries with "Reason not picked:" lines
  - Markdown "Evidence gaps carried into phase 2" section omitted (empty)
  - Markdown "Evidence gaps not carried" section omitted (empty)
  - No em-dash anywhere in markdown body
```

Eyeball the JSON output and the rendered markdown. If the pick isn't `opp-5-1`, alternatives count isn't 5, the rationale doesn't trace the decision rule, or effort thinking shows up anywhere, the prompt is wrong. A formal regression harness is overkill for v1.

What the smoke test does NOT exercise (parked as open follow-ups):

- Tie handling at step 2 or step 3.
- Empty-candidate-set fallback (when all opps are weak/unknown on outcome-alignment).
- Non-empty `evidence_gaps_carried[]` and `evidence_gaps_excluded[]` rendering (the Norrsken fixture's chosen opp has zero unknowns).
- Multi-pick / shortlist (locked out of v1).

These gaps in test coverage are accepted for v1; they go on the open-follow-ups list.

## Open follow-ups

These are added to `TODO.md` rather than blocking v1.

1. **Workspace README staging-convention update.** Already on the follow-up list from OST-compare-opportunities. The selector's `workspace/3-opportunity-select/` is another data point that the README's staging-dir documentation needs to catch up.
2. **Schema evolution beyond v0.1.** Bumps when downstream skills request new fields or trios produce structures v0.1 cannot represent. Procedure same as opportunity-comparison: add an "Evolution" entry to `opportunity-selection.md` and bump `schema_version` in the skill prompt.
3. **Tie-handling smoke-test fixture.** Construct a matrix where step 2 and step 3 both tie, to exercise `decision_signals.tie_with[]` rendering and the "force a pick + name tie" rationale pattern.
4. **Empty-candidate-set fixture.** Construct a matrix where every opp scores `weak` or `unknown` on outcome-alignment, to exercise the fallback and verify the rationale names the fallback explicitly.
5. **Non-empty gap-filter fixture.** Construct a matrix where the chosen opp has 2-3 `unknown` cells, to exercise the AI's `carried` vs `excluded` judgement and verify both sections render with `Why relevant:` and `Why excluded:` lines.
6. **Configurable decision rule per trio.** Currently the three-step rule is hardcoded. If trios want different weighting (e.g., privilege strategic-fit over outcome-alignment for a vision-driven team), surface this as configurable in the knowledge anchor. Revisit only after 2-3 trios have run the selector.
7. **Multi-pick / shortlist mode.** If trios consistently want a 2-3 opp shortlist instead of a single pick + alternatives, add a configurable HITL flavor. Revisit if requested.
8. **Selector self-doubt signaling beyond the tie note.** If trios report that low-confidence non-tied picks land as too confident, add an explicit per-pick confidence signal (e.g., `decision_signals.confidence: "high" | "medium" | "low"`).
9. **Effort-creep self-policing in selector prose.** If trios catch the rationale or reason-not-picked weighing effort despite the no-effort rule, add either a forbidden-vocabulary blocklist or a post-composition validation pass. Currently parked.
10. **Inherited evidence-overstatement from matrix rationales.** The comparator's v2 follow-ups (commit `018e176`) flagged that matrix rationales can over-state cross-customer "independence" or pull from the cluster's `narrativ` extension surface as evidence. The selector inherits these rationales by reference. If selector outputs over-state evidence as a result, surface this as a v2 follow-up to either constrain selector rationale prose or add a sanity-check pass.
11. **Step-2 profile-count precision in `reason_not_picked` prose.** The Task 3 smoke-test (commit `e8cd551`) showed the selector's `reason_not_picked` for opp-1-1 referenced "4 strong" for opp-5-1, conflating the full 5-criterion profile with the 4-criterion rank profile (step 2 explicitly excludes outcome-alignment from the rank count). A future SKILL.md could add a note to Step 10 clarifying that alternatives' `reason_not_picked` anchors in the 4-criterion rank profile, not the full 5-criterion profile, when invoking step-2 comparisons.
12. **Confidence-calibration length heuristic.** The design spec says "confident rationale on clean wins, transparent rationale on close calls". The Task 3 smoke-test produced a 4-sentence rationale on a clean win, which is at the upper end of the locked 2-4 range. A future SKILL.md could give a length heuristic by case (clean win: 2 sentences; close call: 3-4 sentences with tie context) rather than a flat 2-4 range.
