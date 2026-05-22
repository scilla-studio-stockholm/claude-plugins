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

1. **Resolve scope.** Follow `references/workspace-scope.md`. Portfolio scope only.

2. **Load context via parent walk-up:**
   - `<scope>/../../_product-context/product-outcome.md`
   - Same-round predecessor: `<scope>/experience-map-clustered.json` and `<scope>/opportunities-validated.md`

3. **Read the knowledge anchors:**
   - `references/opportunity-comparison.md` - the matrix schema (v0.1), the five criteria, the score vocabulary, the trace-back rule, the no-effort rule.
   - `references/opportunity-solution-tree-teresa-torres.md` - Torres principles, especially "Don't assess effort during opportunity selection".
   - `references/experience-mapping.md` - schema v0.2 of the input clustered JSON.

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
   - **Snapshot `journey_phases[]`** from the clustered JSON: one entry per `phases[]` element in upstream array order, carrying `{ id, name }` verbatim. Include every phase, even those with zero approved opportunities (zero-opp phases still render as empty swim-lane columns in the HTML).
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

10. **Generate AI summary titles** for opportunities in `opportunities_compared[]`. For each opportunity without an existing non-empty `summary_title`, generate a short descriptive noun phrase (3-6 words) that names the underlying pain or friction. Style: in the source language of the underlying `quote` (Swedish if the quote is Swedish, English if English, etc.).

    Examples:
    - quote: "Användare förstår inte hur de ska beställa och måste mejla support..." → summary_title: `Otydlig beställningsprocess`
    - quote: "Mejlkonversation om beställningen drar ut på tiden..." → summary_title: `Mejlkonversation drar ut på tiden`
    - quote: "Customers can't tell whether their order shipped..." → summary_title: `Unclear shipping status`

    Cache rule: if the input `<scope>/comparison-matrix.json` already exists and contains `summary_title` values for any opportunities, carry those titles through unchanged. Generate titles only for opportunities missing the field. This makes re-renders cheap and stable.

    Compute `score_counts` per opportunity in `opportunities_compared[]` as `{ strong, medium, weak, unknown, na }` (integer counts of cells with each score across the five criteria, for that opportunity's column).

    If you cannot produce a valid `summary_title` for any opportunity (LLM returns empty, refuses, or produces something outside the 3-6 word noun-phrase style), hard exit with the opp-id named.

11. **Compose the v0.1 JSON.** All fields per the schema in `references/opportunity-comparison.md`, plus three additive fields at v0.1 (schema version stays `"0.1"`):
    - `journey_phases[]` at top level (from step 6).
    - `summary_title` on each `opportunities_compared[]` entry (from step 10).
    - `score_counts` on each `opportunities_compared[]` entry (from step 10).

    Per the missing-optional convention, omit any optional key whose value isn't set; never write `null`. `opportunities_excluded[]` and `evidence_gaps[]` are written as empty arrays when applicable, never as `null` and never omitted. `journey_phases[]` is always non-empty (at least one phase exists in any valid clustered JSON).

12. **Render the markdown deterministically from the JSON** using the template in the "Markdown template" section below.

13. **Render the HTML deterministically from the same JSON** using the template in the "HTML template" section below. The HTML carries the same data as the markdown (same outcome, same opportunities, same scores, same rationales, same gaps, same notes, same excluded list) but presents them as a journey-grouped, scannable view: phases as horizontal swim-lane columns, opportunities as cards within each column (sorted by `score_counts.strong` desc then `score_counts.weak` asc), with rationales collocated inside expandable `<details>`. The HTML carries the matrix's data, not the matrix's tabular form. Single self-contained file with inline `<style>` and inline `<script>`; no external CSS, no remote dependencies. Filter chips above the swim-lanes toggle visibility of cards based on score-count thresholds.

14. **Write paired output** to:
    - `<scope>/comparison-matrix.json`
    - `<scope>/comparison-matrix.md`
    - `<scope>/comparison-matrix.html`

    All three artifacts are written from the same composed JSON in a single pass. Upstream `experience-map-clustered.json` and `product-outcome.md` are not modified. Create `<scope>/` if it doesn't exist.

## Hard-exit format

When a hard-exit condition fires, respond with this exact pattern (substitute actual values) and stop. Do not write any output files.

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

The eight hard-exit triggers:

| Trigger | Looked for | Remedy |
|---|---|---|
| `<scope>/experience-map-clustered.json` missing | A clustered experience map at the resolved scope path | Run `OST-cluster-opportunities` for this round |
| `<scope>/../../_product-context/product-outcome.md` missing | Trio's product outcome file via parent walk-up | Restore from git or re-author using the template structure |
| Clustered JSON does not parse | Schema-conformant v0.2 JSON | Re-run `OST-cluster-opportunities` |
| Clustered JSON `schema_version` is not `"0.2"` | `"schema_version": "0.2"` | Re-run `OST-cluster-opportunities` against the latest extracted file |
| Zero approved opportunities after verdict filtering | At least one opportunity with `verdict == "approved"` | Re-run `OST-validate-opportunities` and review verdicts; the comparator cannot compare an empty set |
| Product outcome file has no extractable `## Outcome` section | A heading `## Outcome` followed by the outcome formulation | Re-author `<scope>/../../_product-context/product-outcome.md` using the template structure |
| One or more clustered opportunities missing the `verdict` field | `verdict` set on every opportunity in the clustered JSON | Re-run `OST-cluster-opportunities`; do not hand-edit the clustered JSON |
| AI title generation failed for one or more opportunities | A 3-6 word noun-phrase `summary_title` for every approved opportunity | Re-run the skill; if it recurs, hand-edit the missing `summary_title` values into `<scope>/comparison-matrix.json` and re-run (cached titles are reused) |

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

## HTML template

The HTML output is rendered deterministically from the same composed JSON as the markdown, using this template. Single self-contained file with inline `<style>` and inline `<script>`; no external CSS, no remote fonts, no external scripts. The HTML carries the matrix data as a journey-grouped scannable view (cards in phase columns), not as a tabular matrix.

```html
<!DOCTYPE html>
<html lang="<lang>">
<head>
<meta charset="utf-8">
<title>Comparison matrix: <title> (<team>)</title>
<style>
  :root {
    --bg: #faf8f5;
    --surface: #ffffff;
    --ink: #1a1815;
    --ink-soft: #5a564f;
    --rule: #e8e4dc;
    --strong-bg: #d4ead5; --strong-ink: #1f5e2a;
    --medium-bg: #fbe7b8; --medium-ink: #6b4a05;
    --weak-bg:   #f4cfc6; --weak-ink:   #7a2418;
    --unknown-bg:#ecebe7; --unknown-ink:#5a564f;
    --na-bg:    transparent; --na-ink:  #98948c;
    --accent: #6b3fa0;
    --phase-tint-1: #f3ede0;
    --phase-tint-2: #ebe5d6;
    --phase-tint-3: #e3ddce;
    --phase-tint-4: #ddd5c5;
    --phase-tint-5: #d5ccbb;
  }
  html { scroll-behavior: smooth; }
  body {
    font: 15px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    color: var(--ink); background: var(--bg);
    max-width: 1600px; margin: 0 auto; padding: 1.5rem 1rem 6rem;
  }
  header { border-bottom: 1px solid var(--rule); padding-bottom: 1.25rem; margin-bottom: 1.25rem; }
  h1 { font-size: 1.75rem; margin: 0 0 .4rem; letter-spacing: -.01em; }
  h2 { font-size: 1.15rem; margin: 2rem 0 .8rem; letter-spacing: -.005em; }
  .meta { color: var(--ink-soft); font-size: .85rem; margin: 0; }
  .meta code { font-size: .8rem; background: var(--surface); padding: 1px 5px; border-radius: 3px; border: 1px solid var(--rule); }
  blockquote { margin: 0; padding: .9rem 1.1rem; border-left: 3px solid var(--accent); background: var(--surface); border-radius: 0 4px 4px 0; }
  section { scroll-margin-top: 1rem; }

  /* Filter bar */
  nav.filters { position: sticky; top: 0; z-index: 3; background: var(--bg); padding: .65rem 0; margin: 0 0 .25rem; display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; border-bottom: 1px solid var(--rule); }
  nav.filters .chip { font-size: .85rem; padding: .3rem .75rem; border-radius: 999px; border: 1px solid var(--rule); background: var(--surface); color: var(--ink); cursor: pointer; user-select: none; }
  nav.filters .chip.active { background: var(--accent); color: white; border-color: var(--accent); }
  nav.filters .reset { font-size: .8rem; padding: .3rem .65rem; border-radius: 4px; border: 1px solid var(--rule); background: transparent; color: var(--ink-soft); cursor: pointer; }
  nav.filters .counter { margin-left: auto; font-size: .85rem; color: var(--ink-soft); font-variant-numeric: tabular-nums; }

  /* Swim-lane grid */
  section.journey { overflow-x: auto; }
  .swim-grid { display: grid; grid-template-columns: repeat(var(--col-count), minmax(220px, 1fr)); gap: .6rem; min-width: max-content; }
  .swim-col { background: var(--surface); border: 1px solid var(--rule); border-radius: 6px; padding: .55rem; border-left: 3px solid var(--phase-tint-1); }
  .swim-col[data-phase-index="0"] { border-left-color: var(--phase-tint-1); }
  .swim-col[data-phase-index="1"] { border-left-color: var(--phase-tint-2); }
  .swim-col[data-phase-index="2"] { border-left-color: var(--phase-tint-3); }
  .swim-col[data-phase-index="3"] { border-left-color: var(--phase-tint-4); }
  .swim-col[data-phase-index="4"] { border-left-color: var(--phase-tint-5); }
  .swim-col[data-phase-index="unphased"] { border-left-color: var(--ink-soft); border-left-style: dashed; }
  .swim-col-head { position: sticky; top: 3rem; background: var(--surface); padding: .35rem .25rem .5rem; margin-bottom: .35rem; z-index: 2; border-bottom: 1px solid var(--rule); }
  .swim-col-head .phase-name { font-weight: 600; font-size: .95rem; }
  .swim-col-head .phase-count { color: var(--ink-soft); font-size: .8rem; margin-left: .3rem; font-variant-numeric: tabular-nums; }
  .swim-col-empty { font-size: .85rem; color: var(--ink-soft); font-style: italic; padding: .5rem .25rem; }
  .swim-col-nomatch { font-size: .85rem; color: var(--ink-soft); font-style: italic; padding: .5rem .25rem; display: none; }
  .swim-col.is-empty-filter .swim-col-nomatch { display: block; }

  /* Opportunity cards */
  details.opp-card { background: #fefdfb; border: 1px solid var(--rule); border-radius: 4px; padding: .55rem .65rem; margin-bottom: .4rem; scroll-margin-top: 4rem; }
  details.opp-card[open] { background: var(--surface); border-color: var(--ink-soft); }
  details.opp-card.filtered-out { display: none; }
  details.opp-card > summary { cursor: pointer; list-style: none; outline: none; }
  details.opp-card > summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 3px; }
  details.opp-card > summary::-webkit-details-marker { display: none; }
  details.opp-card > summary::after { content: "▾"; float: right; color: var(--ink-soft); font-size: .85rem; transition: transform .15s; }
  details.opp-card[open] > summary::after { transform: rotate(180deg); }
  .card-title { display: block; font-weight: 600; font-size: .92rem; margin: 0 1.5rem .15rem 0; line-height: 1.35; }
  .card-step { float: right; font-size: .72rem; color: var(--ink-soft); font-family: ui-monospace, "SF Mono", Menlo, monospace; margin-left: .25rem; text-decoration: none; }
  .card-step:hover { text-decoration: underline; }
  .card-standouts { display: block; font-size: .8rem; margin: .15rem 0 .1rem; line-height: 1.5; }
  .card-standouts .label { color: var(--ink-soft); display: inline-block; min-width: 3.6em; }
  .card-standouts.strong .label { color: var(--strong-ink); font-weight: 600; }
  .card-standouts.weak .label { color: var(--weak-ink); font-weight: 600; }
  .card-no-standouts { display: block; font-size: .8rem; color: var(--ink-soft); font-style: italic; margin: .15rem 0; }

  /* Card expansion content */
  .card-detail { margin-top: .55rem; padding-top: .5rem; border-top: 1px dashed var(--rule); }
  .card-detail blockquote { font-size: .85rem; margin: 0 0 .35rem; padding: .5rem .65rem; border-left: 2px solid var(--accent); }
  .card-detail cite { display: block; font-style: normal; font-size: .75rem; color: var(--ink-soft); margin-bottom: .55rem; }
  .card-detail .rationale-row { font-size: .8rem; margin-bottom: .5rem; padding: .35rem .5rem; background: #faf8f3; border-radius: 3px; border-left: 2px solid var(--rule); }
  .card-detail .rationale-row.strong  { border-left-color: var(--strong-ink); }
  .card-detail .rationale-row.medium  { border-left-color: var(--medium-ink); }
  .card-detail .rationale-row.weak    { border-left-color: var(--weak-ink); }
  .card-detail .rationale-row.unknown { border-left-color: var(--unknown-ink); }
  .card-detail .rationale-row.na      { border-left-color: var(--na-ink); border-left-style: dashed; }
  .card-detail .rationale-head { display: flex; gap: .4rem; align-items: baseline; margin-bottom: .15rem; }
  .card-detail .crit-name { font-weight: 600; }
  .card-detail .score-pill { font-size: .7rem; padding: 1px 6px; border-radius: 999px; font-weight: 600; }
  .card-detail .score-pill.strong  { background: var(--strong-bg);  color: var(--strong-ink); }
  .card-detail .score-pill.medium  { background: var(--medium-bg);  color: var(--medium-ink); }
  .card-detail .score-pill.weak    { background: var(--weak-bg);    color: var(--weak-ink); }
  .card-detail .score-pill.unknown { background: var(--unknown-bg); color: var(--unknown-ink); }
  .card-detail .score-pill.na      { background: var(--na-bg);      color: var(--na-ink); border: 1px dashed var(--rule); }
  .card-detail .cites { font-size: .72rem; color: var(--ink-soft); margin-top: .15rem; }

  /* Gaps / excluded / notes / step index */
  .gap-list, .excluded-list, .notes-list { list-style: none; padding: 0; }
  .gap-list li, .excluded-list li, .notes-list li { background: var(--surface); border: 1px solid var(--rule); border-radius: 4px; padding: .55rem .85rem; margin-bottom: .45rem; }
  .gap-list strong { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-weight: 600; color: var(--accent); }
  details#steps summary { cursor: pointer; padding: .4rem 0; font-weight: 600; color: var(--ink-soft); text-transform: uppercase; font-size: .8rem; letter-spacing: .04em; }
  details#steps ul { list-style: none; padding: 0; columns: 3; column-gap: 1.5rem; }
  details#steps li { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: .8rem; padding: .15rem 0; }
  details#steps li code { color: var(--accent); }

  /* Print */
  @media print {
    body { max-width: none; padding: 1cm; background: white; }
    nav.filters { display: none; }
    section { page-break-inside: avoid; }
    a { color: inherit; text-decoration: none; }
    details.opp-card, details.opp-card[open] { background: white; border-color: var(--rule); }
    details > *:not(summary) { display: block; }
    details > summary::after { display: none; }
    .swim-col-head { position: static; }
    .swim-grid { grid-template-columns: repeat(var(--col-count), minmax(0, 1fr)); }
  }
</style>
</head>
<body>

<header>
  <h1>Comparison matrix: <title> (<team>)</h1>
  <p class="meta">
    <YYYY-MM-DD> · Schema v0.1 · Paired with
    <code><scope>/comparison-matrix.json</code> and
    <code><scope>/comparison-matrix.md</code>
    <br>Source clustered map: <code><scope>/experience-map-clustered.json</code>
    <br>Source product outcome: <code><scope>/../../_product-context/product-outcome.md</code>
  </p>
</header>

<section id="outcome">
  <h2>Product outcome</h2>
  <blockquote><full outcome formulation></blockquote>
</section>

<!-- Omit entirely if opportunities_excluded[] is empty -->
<section id="excluded">
  <h2>Excluded from comparison (<N>)</h2>
  <ul class="excluded-list">
    <li><strong>opp-X-Y</strong> (Phase: <phase name>; verdict: needs_tweak) - <reason></li>
    <li><strong>opp-A-B</strong> (Phase: <phase name>; verdict: solution_in_disguise) - <reason></li>
  </ul>
</section>

<nav class="filters" id="filters">
  <button class="chip" data-filter="strong-heavy" type="button">strong-heavy (≥3 strongs)</button>
  <button class="chip" data-filter="has-weak" type="button">has weak</button>
  <button class="chip" data-filter="has-unknown" type="button">has unknown</button>
  <button class="reset" type="button">Reset</button>
  <span class="counter"><span id="counter-shown"><N></span> of <span id="counter-total"><N></span> shown</span>
</nav>

<section id="journey" class="journey">
  <h2>Opportunities by journey phase (<N>)</h2>
  <div class="swim-grid" style="--col-count: <col-count>;">
    <!--
      Render one <div class="swim-col"> per entry in journey_phases[], in array order,
      with data-phase-index="<0-based index>". Then, if at least one opportunity has
      no phase set (unphased bucket), render a final <div class="swim-col"
      data-phase-index="unphased"> at the end. <col-count> is the total column count
      (length of journey_phases + 1 if unphased column is rendered, else just length).
    -->
    <div class="swim-col" data-phase-index="0" id="phase-<phase_id>">
      <div class="swim-col-head">
        <span class="phase-name"><phase name></span>
        <span class="phase-count">(<N>)</span>
      </div>

      <!-- If this column has zero opportunities, render the empty placeholder instead of any cards: -->
      <!-- <div class="swim-col-empty">No opportunities in this phase.</div> -->

      <!-- Otherwise, render cards sorted by score_counts.strong DESC,
           then score_counts.weak ASC, then upstream opportunities_compared[] order: -->
      <details class="opp-card" id="opp-X-Y"
               data-strong-count="<n>" data-weak-count="<n>" data-unknown-count="<n>">
        <summary>
          <a class="card-step" href="#step-<step_id>">step-X-Y</a>
          <span class="card-title"><summary_title></span>
          <!-- If score_counts.strong >= 1, render the strong row; otherwise omit it: -->
          <span class="card-standouts strong"><span class="label">strong:</span> outcome alignment, customer importance</span>
          <!-- If score_counts.weak >= 1, render the weak row; otherwise omit it: -->
          <span class="card-standouts weak"><span class="label">weak:</span> strategic fit</span>
          <!-- If both score_counts.strong == 0 AND score_counts.weak == 0, render this instead: -->
          <!-- <span class="card-no-standouts">No standout scores.</span> -->
        </summary>
        <div class="card-detail">
          <blockquote>"<full quote>"</blockquote>
          <cite><source></cite>
          <!-- One rationale-row per criterion, in criteria[] order:
               outcome-alignment, customer-importance, market-size, strategic-fit,
               competitive-landscape. unknown and n/a rows omit the .cites line. -->
          <div class="rationale-row strong">
            <div class="rationale-head"><span class="crit-name">Outcome alignment</span><span class="score-pill strong">strong</span></div>
            <p><rationale prose></p>
            <p class="cites">Cites: opp-X-Y.</p>
          </div>
          <div class="rationale-row na">
            <div class="rationale-head"><span class="crit-name">Competitive landscape</span><span class="score-pill na">n/a</span></div>
            <p><rationale prose></p>
            <!-- no .cites for unknown / n/a -->
          </div>
        </div>
      </details>
      <!-- ...more cards in this column... -->

      <div class="swim-col-nomatch">No matching opportunities.</div>
    </div>
    <!-- ...more phase columns... -->

    <!-- Optional final unphased column. Render only if at least one opportunity has no phase set: -->
    <div class="swim-col" data-phase-index="unphased" id="phase-unphased">
      <div class="swim-col-head">
        <span class="phase-name">Unphased</span>
        <span class="phase-count">(<N>)</span>
      </div>
      <!-- ...same card structure as above... -->
      <div class="swim-col-nomatch">No matching opportunities.</div>
    </div>
  </div>
</section>

<!-- Omit entirely if evidence_gaps[] is empty -->
<section id="gaps">
  <h2>Evidence gaps (<N>)</h2>
  <p class="meta">Cells where evidence was thin and an honest score wasn't defensible. Each gap names what evidence would unlock a score.</p>
  <ul class="gap-list">
    <li><strong>Customer importance × opp-4-3</strong>: <what_is_missing></li>
    <li><strong>Market size / frequency × opp-4-3</strong>: <what_is_missing></li>
  </ul>
</section>

<!-- Omit entirely unless a criterion scored n/a for ALL approved opportunities -->
<section id="notes">
  <h2>Notes</h2>
  <ul class="notes-list">
    <li><strong>Competitive landscape</strong> scored <code>n/a</code> for all opportunities, suggesting it isn't load-bearing for this trio's context. The trio may consider dropping this criterion in HITL.</li>
  </ul>
</section>

<details id="steps">
  <summary>Step index</summary>
  <ul>
    <!-- One <li> per (phase_id, step_id, step name) tuple traversed in upstream phases[].steps[] order.
         List every step that appears on at least one card's data-step link. -->
    <li id="step-<step_id>"><code>step-X-Y</code> — <step name></li>
  </ul>
</details>

<script>
(function () {
  var activeFilters = new Set();
  var bar = document.getElementById('filters');
  var shown = document.getElementById('counter-shown');
  var total = document.getElementById('counter-total');
  var cards = Array.prototype.slice.call(document.querySelectorAll('details.opp-card'));
  var cols = Array.prototype.slice.call(document.querySelectorAll('.swim-col'));
  total.textContent = cards.length;

  function passes(card) {
    if (activeFilters.size === 0) return true;
    if (activeFilters.has('strong-heavy') && (+card.dataset.strongCount || 0) < 3) return false;
    if (activeFilters.has('has-weak')     && (+card.dataset.weakCount || 0) < 1) return false;
    if (activeFilters.has('has-unknown')  && (+card.dataset.unknownCount || 0) < 1) return false;
    return true;
  }

  function apply() {
    var count = 0;
    cards.forEach(function (c) {
      var ok = passes(c);
      c.classList.toggle('filtered-out', !ok);
      if (ok) count++;
    });
    shown.textContent = count;
    cols.forEach(function (col) {
      var visible = col.querySelectorAll('details.opp-card:not(.filtered-out)').length;
      var hasAnyCard = col.querySelector('details.opp-card') !== null;
      col.classList.toggle('is-empty-filter', hasAnyCard && visible === 0);
    });
  }

  bar.addEventListener('click', function (e) {
    var t = e.target;
    if (t.classList && t.classList.contains('chip')) {
      var f = t.dataset.filter;
      if (activeFilters.has(f)) { activeFilters.delete(f); t.classList.remove('active'); }
      else { activeFilters.add(f); t.classList.add('active'); }
      apply();
    } else if (t.classList && t.classList.contains('reset')) {
      activeFilters.clear();
      bar.querySelectorAll('.chip.active').forEach(function (c) { c.classList.remove('active'); });
      apply();
    }
  });

  // Open the card if URL fragment points at one
  if (location.hash && location.hash.indexOf('#opp-') === 0) {
    var target = document.querySelector(location.hash);
    if (target && target.tagName === 'DETAILS') target.open = true;
  }
})();
</script>

</body>
</html>
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
