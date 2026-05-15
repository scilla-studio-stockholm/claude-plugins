---
name: OST-compare-opportunities
description: For product trios and researchers, when comparing approved opportunities against a product outcome and Torres criteria, output a paired JSON + markdown rendering with a qualitative comparison matrix (criteria × opportunities) plus an evidence-gap list of unknown cells.
---

# Compare opportunities

You help a product trio compare approved opportunities against their product outcome and Torres prioritization criteria, producing paired JSON (per the opportunity-comparison schema v0.1) plus a markdown rendering. The output is a 5×N matrix (5 Torres-derived criteria × N approved opportunities) with qualitative scores and grounded rationales, plus an evidence-gap list derived from cells that scored `unknown`.

This skill is assist 4 in `skills-design/opportunity-solution-tree-agents.md`. The full design lives in `skills-design/OST-compare-opportunities-design.md`.

**Out of scope:** transcript reading, citation validation (`OST-validate-opportunities` upstream), re-clustering (`OST-cluster-opportunities` upstream), summing or ranking scores (the selector decides), picking a winning opportunity (`OST-select-opportunity`, assist 5), generating solutions (downstream of selector), and weighing effort or feasibility (Torres principle).

The comparator filters by verdict before scoring: only `verdict == "approved"` opportunities enter the matrix. `needs_tweak` and `solution_in_disguise` opportunities are listed in an "Excluded from comparison" note.

## Steps

1. **Resolve scope.** Follow `knowledge/discovery/workspace-scope.md`. Portfolio scope only.

2. **Load context via parent walk-up:**
   - `<scope>/../../_product-context/product-outcome.md`
   - Same-round predecessor: `<scope>/experience-map-clustered.json` and `<scope>/opportunities-validated.md`

3. **Read the knowledge anchors:**
   - `knowledge/discovery/opportunity-comparison.md` - the matrix schema (v0.1), the five criteria, the score vocabulary, the trace-back rule, the no-effort rule.
   - `knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - Torres principles, especially "Don't assess effort during opportunity selection".
   - `knowledge/discovery/experience-mapping.md` - schema v0.2 of the input clustered JSON.

4. **Locate inputs:**
   - `<scope>/experience-map-clustered.json` (same-round predecessor).
   - `<scope>/../../_product-context/product-outcome.md` (parent walk-up).

5. **Hard-exit checks** (see Hard-exit format below). Do not write any output files when these fire:
   - `<scope>/experience-map-clustered.json` missing.
   - `<scope>/../../_product-context/product-outcome.md` missing.
   - Clustered JSON does not parse.
   - Clustered JSON `schema_version` is not `"0.2"`.
   - Zero approved opportunities after verdict filtering.
   - Product outcome file has no extractable `## Outcome` section.
   - One or more clustered opportunities missing the `verdict` field.

6. **Parse, filter, and partition.**
   - Parse the clustered JSON. Index `phases[]` by `id`. Walk `phases[].opportunities[]`.
   - Parse the product outcome from `<scope>/../../_product-context/product-outcome.md`. Extract the outcome formulation under the `## Outcome` heading. Carry the team name from `## Team`.
   - Partition opportunities by verdict:
     - `verdict == "approved"` → `opportunities_compared[]`. Carry verbatim: `id`, `phase_id`, `quote`, `source`.
     - `verdict ∈ {"needs_tweak", "solution_in_disguise"}` → `opportunities_excluded[]`. Carry `id`, `phase_id`, `verdict`, plus a one-line `reason`.
   - If `opportunities_compared[]` is empty, hard exit.

7. **Compose `criteria[]`.** Five hardcoded entries, denormalized from the knowledge anchor:

   | id | name | description |
   |---|---|---|
   | `outcome-alignment` | Outcome alignment | Does solving this opportunity move the trio's product outcome? How directly would the opportunity's pain, when relieved, shift the outcome's metric or behavior? |
   | `customer-importance` | Customer importance | How strongly do the customers in the cluster feel this pain? Intensity, recurrence, and cross-customer signal in the source quotes. |
   | `market-size` | Market size / frequency | How many customers experience this pain, and how often? Frequency multiplies importance: a moderately painful experience that happens daily can outweigh a sharp pain that happens once a year. |
   | `strategic-fit` | Strategic fit | Does solving this opportunity align with the team's vision and the product's positioning? Fit with the team's domain, the product's core promise, and the trio's stated direction. |
   | `competitive-landscape` | Competitive landscape | Does solving this opportunity differentiate against alternatives the customer could choose? For internal products with no external competition this often scores `n/a`. |

8. **Score each cell** (criterion × approved opportunity). For every (criterion, opportunity) pair:
   - Use the criterion's lens against the opportunity's quote, source, phase placement, and cross-opportunity context within the same cluster.
   - Pick a score from the 5-value vocabulary: `strong` / `medium` / `weak` / `unknown` / `n/a`.
   - Write a 1-2 sentence rationale.
   - **Trace-back rule.** If `score ∈ {strong, medium, weak}`, the rationale must reference at least one `opp-id` from `opportunities_compared[]`. List every opp-id mentioned in the rationale text in `opp_refs[]`. The cell's own opportunity is the typical citation; cross-references to other opportunities in the cluster are valid when they reinforce the score (e.g., three opportunities referencing the same pain → boosts customer-importance for each). `unknown` and `n/a` cells skip this rule (`opp_refs` is empty).
   - **No-effort rule.** If your reasoning chain ever reaches "but it would be hard/easy to build / requires X integration / would scale poorly", remove that step and re-score on the criterion's dimension only. Effort is decided downstream in assumption testing (step 4 of the OST process).
   - Use `n/a` if the criterion structurally doesn't apply to the trio's context (e.g., "market size" for an internal tool with a fixed user base, "competitive landscape" for an internal tool with no external competitors). `n/a` is different from `unknown`: it's a structural decision, not an evidence gap.
   - Use `unknown` if evidence is genuinely thin and an honest non-`unknown` score is not defensible.
   - `opp_refs[]` only references IDs in `opportunities_compared[]`. Do not cite excluded opportunities.

9. **Compose `evidence_gaps[]`.** For each cell where `score == "unknown"`, add one entry:
   - `criterion_id` (matches the cell)
   - `opportunity_id` (matches the cell)
   - `what_is_missing` (one sentence describing what evidence would unlock a score)

   `n/a` cells do not appear here. Empty array if no `unknown` cells.

10. **Compose the v0.1 JSON.** All fields per the schema in `knowledge/discovery/opportunity-comparison.md`. Per the missing-optional convention, omit any optional key whose value isn't set; never write `null`. `opportunities_excluded[]` and `evidence_gaps[]` are written as empty arrays when applicable, never as `null` and never omitted.

11. **Render the markdown deterministically from the JSON** using the template in the "Markdown template" section below.

12. **Write paired output** to:
    - `<scope>/comparison-matrix.json`
    - `<scope>/comparison-matrix.md`

    Upstream `experience-map-clustered.json` and `product-outcome.md` are not modified. Create `<scope>/` if it doesn't exist.

## Hard-exit format

When a hard-exit condition fires, respond with this exact pattern (substitute actual values) and stop. Do not write any output files.

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

The seven hard-exit triggers:

| Trigger | Looked for | Remedy |
|---|---|---|
| `<scope>/experience-map-clustered.json` missing | A clustered experience map at the resolved scope path | Run `OST-cluster-opportunities` for this round |
| `<scope>/../../_product-context/product-outcome.md` missing | Trio's product outcome file via parent walk-up | Restore from git or re-author using the template structure |
| Clustered JSON does not parse | Schema-conformant v0.2 JSON | Re-run `OST-cluster-opportunities` |
| Clustered JSON `schema_version` is not `"0.2"` | `"schema_version": "0.2"` | Re-run `OST-cluster-opportunities` against the latest extracted file |
| Zero approved opportunities after verdict filtering | At least one opportunity with `verdict == "approved"` | Re-run `OST-validate-opportunities` and review verdicts; the comparator cannot compare an empty set |
| Product outcome file has no extractable `## Outcome` section | A heading `## Outcome` followed by the outcome formulation | Re-author `<scope>/../../_product-context/product-outcome.md` using the template structure |
| One or more clustered opportunities missing the `verdict` field | `verdict` set on every opportunity in the clustered JSON | Re-run `OST-cluster-opportunities`; do not hand-edit the clustered JSON |

## Markdown template

The markdown output is rendered deterministically from the composed JSON using this template:

```markdown
---
title: Comparison matrix - <title> (<team>)
date: <YYYY-MM-DD>
purpose: Opportunity comparison matrix for OST opportunity selection, paired with comparison-matrix-<date>.json
tags: [opportunity-comparison, ost, schema-v0.1]

---

# Comparison matrix: <title> (<team>)

Source clustered map: `<scope>/experience-map-clustered.json`
Source product outcome: `<scope>/../../_product-context/product-outcome.md`
Schema version: 0.1
Paired JSON: `<scope>/comparison-matrix.json`

## Product outcome

> <full outcome formulation>

## Opportunities compared (<N>)

- **opp-4-1** (Phase: <phase name>) - "<full quote>" - *<source>*
- **opp-4-2** (Phase: <phase name>) - "<full quote>" - *<source>*
- ...

## Excluded from comparison (<N>)

(only if non-empty; otherwise omit this whole section)

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

(repeat one section per criterion, in the order declared in `criteria[]`:
outcome-alignment, customer-importance, market-size, strategic-fit,
competitive-landscape)

## Evidence gaps (<N>)

(only if non-empty; otherwise omit this whole section)

Cells where evidence was thin and an honest score wasn't defensible. Each gap names what evidence would unlock a score.

- **Customer importance × opp-4-3**: <what_is_missing>
- **Market size / frequency × opp-4-3**: <what_is_missing>

## Notes

(only if any criterion scored `n/a` for ALL approved opportunities; otherwise omit this whole section)

- **Competitive landscape** scored `n/a` for all opportunities, suggesting it isn't load-bearing for this trio's context. The trio may consider dropping this criterion in HITL.
```

## Output principles

- **Score values use full words** in both the matrix table and the rationales: `strong` / `medium` / `weak` / `unknown` / `n/a`. No emoji.
- **Cites: line.** Every `strong`, `medium`, or `weak` rationale ends with `Cites: opp-X-Y[, opp-A-B...].` listing every opp-id from that cell's `opp_refs[]`. `unknown` and `n/a` cells omit the Cites line entirely.
- **Source attribution** carried verbatim from the clustered JSON. Separated from the quote by ` - ` (regular dash, not em-dash).
- **No em-dash** anywhere, applied uniformly to Swedish and English prose.
- **Criterion display names stay in English** even when quotes and rationales are Swedish. The criteria are Torres-canonical; mixing canonical-English criteria with Swedish rationale prose is normal in product orgs and avoids a translation surface.
- **Output language for prose** (rationales, `what_is_missing`, reasons) matches the source language detected in the clustered JSON's `quote` text and `phases[].name`. Schema field names, JSON key strings, criterion IDs, criterion display names, and score vocabulary stay as defined.
- **Frontmatter on the markdown output** complies with the project convention that every `.md` file has YAML frontmatter, with a blank line before the closing `---`.
- **Empty sections are omitted entirely.** "Excluded from comparison", "Evidence gaps", and "Notes" each omit when their underlying list is empty.
- **Matrix column order** matches `opportunities_compared[]` order in the JSON.
- **Matrix row order** matches `criteria[]` order in the JSON: outcome-alignment, customer-importance, market-size, strategic-fit, competitive-landscape.
- **No silent degradation.** Hard exit on the conditions in the Hard-exit format table; never write partial output.
- **No JSON self-validation pass.** Trust the prompt; downstream skills surface any malformed JSON.
- **Upstream files are immutable.** Never modify `<scope>/experience-map-clustered.json` or `<scope>/../../_product-context/product-outcome.md`. The skill only writes `<scope>/comparison-matrix.json` and `<scope>/comparison-matrix.md`.
- **Single pass.** No retries, no iteration over the inputs.

## What this skill does NOT do

- **Read interview transcripts.** Quotes come from the clustered JSON.
- **Read the original `opportunities-extracted-*` or `opportunities-validated-*` files.** All quotes, sources, and verdicts the comparator needs are already in the clustered JSON.
- **Validate citation format.** That is `OST-validate-opportunities` upstream.
- **Re-cluster opportunities or change phase placement.** That is `OST-cluster-opportunities`.
- **Modify upstream files.** `<scope>/experience-map-clustered.json` and `<scope>/../../_product-context/product-outcome.md` stay immutable.
- **Compare opportunities against criteria other than the five hardcoded ones.** The criteria list is fixed in v0.1.
- **Sum, average, or otherwise aggregate scores across criteria.** The matrix is for comparison, not ranking. The selector decides.
- **Pick a winning opportunity.** That is the selector (assist 5).
- **Generate solutions for any opportunity.** Downstream of the selector.
- **Weigh effort, feasibility, integration cost, or implementation complexity.** Per Torres.
- **Compare `needs_tweak` or `solution_in_disguise` opportunities.** Filtered out at step 4 with a visible note.
- **Score cells with confidence values outside the 5-value vocabulary.** No "high-medium" or numeric scores.
- **Use emoji or numeric encoding for scores.** Words only.
- **Iterate, retry, or run multiple passes.** One pass over the inputs, one pair of output files.
- **Run a JSON self-validation pass after composition.**
- **Write to Miro or any external surface.** JSON + markdown only.
- **Audit the cluster JSON for invariant violations** beyond what's needed to filter. The comparator only filters by verdict and reads quote/source/phase fields.
- **Ask the trio for clustering choices interactively.** If a cell is genuinely uncertain, score `unknown` and add a gap entry; don't ask.
- **Mark accepted gaps in the product outcome's "Known limitations" section as problems.** Those gaps are trio-accepted.
