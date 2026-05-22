# OST-compare-opportunities HTML Rendering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a swim-lane HTML rendering to `OST-compare-opportunities/SKILL.md` so the trio can scan 96 opportunities at a glance. The skill currently produces JSON + markdown; this plan adds a third paired output (HTML) without changing the schema version or the markdown template.

**Architecture:** All edits land in a single prompt file (`SKILL.md`). The skill is prompt-driven — no test runner, no compilation step. Verification is structural (grep checks and numbering checks) per commit, then a final end-to-end render against the Metria fixture. Three additive JSON fields (`summary_title`, `score_counts`, `journey_phases`) make HTML re-renders cheap and deterministic.

**Tech Stack:** Markdown (SKILL.md is a prompt), HTML + CSS + vanilla inline JavaScript (~50 LOC, no framework, no external deps). No build step.

**Spec:** `docs/superpowers/specs/2026-05-22-ost-compare-opportunities-html-redesign-design.md`.

**Working directory:** `/Users/jonilindgren/claude-projects/claude-plugins` (the canonical workspace per the project's CLAUDE.md). All git commands and file paths in this plan are relative to that directory.

---

## File Structure

Two files are modified.

- **Modify:** `product-discovery/skills/OST-compare-opportunities/SKILL.md` — the bulk of the change lands here. Procedure steps gain three additive JSON fields, an AI title pass step, and an HTML render step. The Hard-exit table gains one row. The HTML template and HTML rendering rules sections are added. Output principles and "What this skill does NOT do" are updated. Front matter description and opening paragraph mention HTML.
- **Modify:** `CLAUDE.md` — append a status entry to the **Current State** section.

There is no separate template file. The HTML template lives inline inside SKILL.md (matching the existing convention for OST skills). Splitting it out would diverge from the OST plugin's per-skill pattern and create a coupling problem (the SKILL.md prompt and template have to stay in lockstep).

---

## Task 1: Update procedure steps and hard-exit table

**Why this task is first:** The procedure steps drive what ends up in the composed JSON. They must add the three new fields (and the AI title pass) before the template can render them.

**Files:**
- Modify: `product-discovery/skills/OST-compare-opportunities/SKILL.md` — edits to the `## Steps` section (currently steps 1-12) and the `## Hard-exit format` section.

- [ ] **Step 1: Read the current Steps section so you know exact anchor text.**

Run: `sed -n '16,85p' product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected: see steps 1 ("Resolve scope") through 12 ("Write paired output"). The file currently has no HTML render step.

- [ ] **Step 2: Edit step 6 (Parse, filter, and partition) to add a journey_phases snapshot.**

Find this exact block:

```markdown
6. **Parse, filter, and partition.**
   - Parse the clustered JSON. Index `phases[]` by `id`. Walk `phases[].opportunities[]`.
   - Parse the product outcome from `<scope>/../../_product-context/product-outcome.md`. Extract the outcome formulation under the `## Outcome` heading. Carry the team name from `## Team`.
   - Partition opportunities by verdict:
     - `verdict == "approved"` → `opportunities_compared[]`. Carry verbatim: `id`, `phase_id`, `quote`, `source`.
     - `verdict ∈ {"needs_tweak", "solution_in_disguise"}` → `opportunities_excluded[]`. Carry `id`, `phase_id`, `verdict`, plus a one-line `reason`.
   - If `opportunities_compared[]` is empty, hard exit.
```

Replace with:

```markdown
6. **Parse, filter, and partition.**
   - Parse the clustered JSON. Index `phases[]` by `id`. Walk `phases[].opportunities[]`.
   - Parse the product outcome from `<scope>/../../_product-context/product-outcome.md`. Extract the outcome formulation under the `## Outcome` heading. Carry the team name from `## Team`.
   - **Snapshot `journey_phases[]`** from the clustered JSON: one entry per `phases[]` element in upstream array order, carrying `{ id, name }` verbatim. Include every phase, even those with zero approved opportunities (zero-opp phases still render as empty swim-lane columns in the HTML).
   - Partition opportunities by verdict:
     - `verdict == "approved"` → `opportunities_compared[]`. Carry verbatim: `id`, `phase_id`, `quote`, `source`.
     - `verdict ∈ {"needs_tweak", "solution_in_disguise"}` → `opportunities_excluded[]`. Carry `id`, `phase_id`, `verdict`, plus a one-line `reason`.
   - If `opportunities_compared[]` is empty, hard exit.
```

- [ ] **Step 3: Insert a new step 10 for AI title generation, before the existing step 10 (Compose v0.1 JSON).**

Find this exact block (current step 10):

```markdown
10. **Compose the v0.1 JSON.** All fields per the schema in `references/opportunity-comparison.md`. Per the missing-optional convention, omit any optional key whose value isn't set; never write `null`. `opportunities_excluded[]` and `evidence_gaps[]` are written as empty arrays when applicable, never as `null` and never omitted.
```

Replace with (inserting a new step 10 before it, and renumbering the compose step to 11 with three additive fields called out):

```markdown
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
```

- [ ] **Step 4: Renumber the markdown render step (was 11, now 12).**

Find:

```markdown
11. **Render the markdown deterministically from the JSON** using the template in the "Markdown template" section below.
```

Change leading number only:

```markdown
12. **Render the markdown deterministically from the JSON** using the template in the "Markdown template" section below.
```

- [ ] **Step 5: Insert a new step 13 for HTML rendering.**

Insert this new step directly after the markdown render step (between current step 11/new step 12 and the existing write step):

```markdown
13. **Render the HTML deterministically from the same JSON** using the template in the "HTML template" section below. The HTML carries the same data as the markdown (same outcome, same opportunities, same scores, same rationales, same gaps, same notes, same excluded list) but presents them as a journey-grouped, scannable view: phases as horizontal swim-lane columns, opportunities as cards within each column (sorted by `score_counts.strong` desc then `score_counts.weak` asc), with rationales collocated inside expandable `<details>`. The HTML carries the matrix's data, not the matrix's tabular form. Single self-contained file with inline `<style>` and inline `<script>`; no external CSS, no remote dependencies. Filter chips above the swim-lanes toggle visibility of cards based on score-count thresholds.
```

- [ ] **Step 6: Update the write step (was 12, now 14) to include the HTML output.**

Find:

```markdown
12. **Write paired output** to:
    - `<scope>/comparison-matrix.json`
    - `<scope>/comparison-matrix.md`

    Upstream `experience-map-clustered.json` and `product-outcome.md` are not modified. Create `<scope>/` if it doesn't exist.
```

Replace with:

```markdown
14. **Write paired output** to:
    - `<scope>/comparison-matrix.json`
    - `<scope>/comparison-matrix.md`
    - `<scope>/comparison-matrix.html`

    All three artifacts are written from the same composed JSON in a single pass. Upstream `experience-map-clustered.json` and `product-outcome.md` are not modified. Create `<scope>/` if it doesn't exist.
```

- [ ] **Step 7: Verify the Steps section structurally.**

Run: `grep -n "^[0-9]\{1,2\}\. \*\*" product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected: 14 lines, one per step, in order 1 through 14 with no gaps and no duplicates.

Run: `sed -n '16,110p' product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected visually:
- Step 6 has the new "Snapshot `journey_phases[]`" bullet.
- Step 10 is "Generate AI summary titles".
- Step 11 mentions the three additive fields (`journey_phases`, `summary_title`, `score_counts`).
- Step 12 is the markdown render.
- Step 13 is the HTML render and mentions swim-lanes and filter chips.
- Step 14 is the write step listing all three files.

- [ ] **Step 8: Add a hard-exit row for AI title generation failure.**

Find the hard-exit preamble:

```markdown
The seven hard-exit triggers:
```

Replace with:

```markdown
The eight hard-exit triggers:
```

Then append a new row to the hard-exit table immediately before the next `##` heading. The current last row of the table is:

```markdown
| One or more clustered opportunities missing the `verdict` field | `verdict` set on every opportunity in the clustered JSON | Re-run `OST-cluster-opportunities`; do not hand-edit the clustered JSON |
```

Add this row directly below it (same table, new row):

```markdown
| AI title generation failed for one or more opportunities | A 3-6 word noun-phrase `summary_title` for every approved opportunity | Re-run the skill; if it recurs, hand-edit the missing `summary_title` values into `<scope>/comparison-matrix.json` and re-run (cached titles are reused) |
```

After editing, the hard-exit table has 8 rows.

- [ ] **Step 9: Verify the hard-exit edits.**

Run: `grep -c "^| " product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected: at least 14 (8 hard-exit rows + 1 separator + 1 header = 10 in the hard-exit table; 5 criteria rows + 1 separator + 1 header = 7 in the criteria table; total ≥ 17). The exact count depends on other tables, but the count must be ≥ the count before this task plus 1 (since you added one row).

Run: `grep -n "The eight hard-exit triggers" product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected: exactly one match.

- [ ] **Step 10: Commit Task 1.**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add product-discovery/skills/OST-compare-opportunities/SKILL.md
git commit -m "$(cat <<'EOF'
OST-compare-opportunities: add HTML render step and three additive JSON fields

Procedure now snapshots phases (including zero-opp ones), generates
AI summary titles for opportunities (with re-render cache), computes
per-opp score counts, and renders an HTML output. Three additive
fields under schema v0.1. New hard-exit row for title-generation
failure. Markdown render unchanged. HTML template and rendering rules
land in the next commit.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Add HTML template section

**Why this task is second:** The procedure now expects an HTML template to exist (step 13 references "the HTML template section below"), but the section doesn't exist yet. This task adds the entire HTML template inline.

**Files:**
- Modify: `product-discovery/skills/OST-compare-opportunities/SKILL.md` — insert a new `## HTML template` section between the existing `## Markdown template` section and the `## Output principles` section.

- [ ] **Step 1: Locate the insertion point.**

Run: `grep -n "^## Markdown template\|^## Output principles" product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected:
```
<L1>:## Markdown template
<L2>:## Output principles
```
You will insert the new section between L1's section (which ends just before L2) and L2. Specifically, find the closing ` ``` ` of the markdown template's code block. The new section goes immediately after that closing fence, separated by a blank line.

- [ ] **Step 2: Insert the entire `## HTML template` section.**

The new section is below. Insert it verbatim. It is one heading, one descriptive paragraph, then a triple-backtick `html` code block containing the template.

````markdown
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
      with data-phase-index="<0-based index mod 5>" (the tint cycles past 5 phases).
      Then, if at least one opportunity has
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
````

- [ ] **Step 3: Verify the template was inserted correctly.**

Run: `grep -nE "^## HTML template|^## Output principles|^## HTML rendering rules" product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected: `## HTML template` appears once, then `## Output principles` appears once after it. `## HTML rendering rules` should NOT appear yet (that's Task 3).

Run: `grep -n "data-strong-count\|data-weak-count\|data-unknown-count\|swim-col\|opp-card\|nav class=\"filters\"\|<details id=\"steps\">" product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected: each token appears at least once.

- [ ] **Step 4: Commit Task 2.**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add product-discovery/skills/OST-compare-opportunities/SKILL.md
git commit -m "$(cat <<'EOF'
OST-compare-opportunities: add HTML template (swim-lane journey layout)

Adds the HTML template section between the existing Markdown template
and Output principles. Cards live in phase-column swim-lanes
(#journey), sorted by strong-count desc then weak-count asc. Each
card is a <details> with the AI title + step label + standout-score
chips when collapsed, and full quote + per-criterion rationales when
expanded. Includes a sticky filter bar (#filters), inline ~50 LOC
vanilla JS, and a collapsed step index (#steps). Rendering rules
documented in the next commit.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Add HTML rendering rules section

**Why this task is third:** The template now exists but lacks the structured rules that constrain how the LLM renders it (anchor ID scheme, sort order, column behavior, filter semantics). This task adds a `### HTML rendering rules` subsection under the `## HTML template` heading, matching the convention from the markdown template's rendering principles.

**Files:**
- Modify: `product-discovery/skills/OST-compare-opportunities/SKILL.md` — insert a new `### HTML rendering rules` heading directly after the closing ` ``` ` of the HTML template's code block (and before the `## Output principles` heading).

- [ ] **Step 1: Locate the insertion point.**

Run: `grep -n "^## HTML template\|^## Output principles" product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected:
```
<L1>:## HTML template
<L2>:## Output principles
```
The new `### HTML rendering rules` subsection goes between L1's section (after the closing ` ``` ` of its code block) and L2.

- [ ] **Step 2: Insert the rendering rules subsection.**

Insert this exact content:

```markdown
### HTML rendering rules

- **Single self-contained file.** Inline `<style>` and inline `<script>` only. No external CSS, no remote fonts, no external scripts. The trio can open the file from any path, email it, or open it offline.
- **JavaScript scope.** ~50 LOC of vanilla JS in one inline `<script>` at the end of `<body>`. Drives only filter-chip toggling and (optionally) opening a `<details>` if the URL fragment is `#opp-X-Y`. No event handlers on cards; native `<details>` toggle is used for expand/collapse. No framework, no fetch, no async, no global state beyond the IIFE.
- **No emoji.** Score values are conveyed by background color, text color, and (for `n/a`) a dashed border. Matches the markdown's "words only" rule.
- **Anchor IDs are deterministic.**
  - Opportunity cards: `id="opp-X-Y"` on the `<details>` element (matches the `opp-id`). URL fragments like `#opp-4-1` open the card expanded.
  - Phase columns: `id="phase-<phase_id>"` (matches the upstream phase id). Unphased column: `id="phase-unphased"`.
  - Step index entries: `id="step-<step_id>"` (matches the upstream step id). Card step labels link via `<a href="#step-X-Y">`.
- **Color classes match the score vocabulary exactly.** `strong` / `medium` / `weak` / `unknown` / `na`. `n/a` uses class `na` (dot is invalid in a class name).
- **Phase color accents.** Each swim-lane column gets a subtle left-border tint, rotated through five warm-neutral CSS variables (`--phase-tint-1` through `--phase-tint-5`) keyed off the phase's 0-based index. The unphased column uses `--ink-soft` with a dashed left border to distinguish it from regular phases. Phase tints are deliberately distinct from score colors to avoid semantic confusion.
- **Swim-lane column rendering rules.**
  - One column per entry in `journey_phases[]`, in array order, including zero-opp phases. Set `data-phase-index="<0-based index mod 5>"` so the tint cycles correctly past five phases.
  - One trailing column with `data-phase-index="unphased"` renders only when ≥1 opportunity has no `phase` set.
  - Each column header carries the phase name and opportunity count. Headers are `position: sticky; top: <filter-bar-height>` so they stay visible during vertical scroll.
  - Columns with zero opportunities render `<div class="swim-col-empty">No opportunities in this phase.</div>` in place of any cards (and never render the `<div class="swim-col-nomatch">` placeholder).
  - Columns with opportunities always render the `<div class="swim-col-nomatch">` placeholder at the bottom (hidden via CSS unless all cards in the column are filtered out).
  - Column width: `minmax(220px, 1fr)`. The swim-grid uses `min-width: max-content` so on narrow viewports the grid overflows horizontally with scroll instead of collapsing columns.
- **Card rendering rules.**
  - Cards within a column are sorted by `score_counts.strong` descending, then `score_counts.weak` ascending, then upstream `opportunities_compared[]` array index. Deterministic and stable.
  - The card title (`<p class="card-title">`) renders the AI-generated `summary_title` from the JSON.
  - The collapsed card shows standout chips only: a `card-standouts strong` row listing the criterion display names of cells scoring `strong` (only if at least one such cell exists), and a `card-standouts weak` row listing the criterion display names of cells scoring `weak` (only if at least one such cell exists). Criterion names appear in their full English display form (e.g., "outcome alignment", "customer importance"), comma-joined in `criteria[]` order.
  - If neither bucket has entries, the card shows `<p class="card-no-standouts">No standout scores.</p>` in their place.
  - The expanded card (`.card-detail` block, revealed when the `<details>` is opened) renders the full quote, source citation, and one `.rationale-row` per criterion in `criteria[]` order. Unknown and n/a rows omit the `.cites` paragraph entirely, matching the markdown rule.
  - The step label (`<a class="card-step" href="#step-X-Y">`) appears floated to the right of the title and links into the `<details id="steps">` index at the bottom of the page.
  - `data-strong-count`, `data-weak-count`, and `data-unknown-count` attributes on each `<details class="opp-card">` mirror the JSON's `score_counts` and drive the filter logic.
- **Filter chip semantics.**
  - `strong-heavy`: hides cards where `score_counts.strong < 3`.
  - `has-weak`: hides cards where `score_counts.weak < 1`.
  - `has-unknown`: hides cards where `score_counts.unknown < 1`.
  - Active chips AND-combine. The Reset button clears all active chips.
  - The counter (`<span class="counter">`) updates to `N of M shown` based on visible cards.
  - When a column has cards but the active filter hides them all, the column shows `No matching opportunities.` in place of the cards (via the `.is-empty-filter` class toggled by the script).
- **Section omission matches the markdown.** `#excluded`, `#gaps`, `#notes` are omitted entirely (the whole `<section>` element) when their underlying list is empty.
- **Print stylesheet** hides the filter bar, forces all `<details>` content to be visible (`details:not([open]) > *:not(summary) { display: revert; }`), drops sticky positioning, and removes the chevron marker. The trio gets a complete printable record showing every card fully expanded.
- **Language attribute.** Set `<html lang>` to match the source language detected in the clustered JSON's `quote` text and `phases[].name` (`sv` for Swedish, `en` for English, etc.). Criterion display names stay in English regardless, matching the markdown's rule.
- **Step index (`#steps`).** Renders one `<li id="step-<step_id>">` per distinct `(phase_id, step_id, step_name)` tuple referenced by at least one card. Order: upstream phases[].steps[] traversal order. Wrapped in a `<details>` collapsed by default so it doesn't push the journey content down on first view.
```

- [ ] **Step 3: Verify.**

Run: `grep -nE "^## HTML template|^### HTML rendering rules|^## Output principles" product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected, in this order:
```
<a>:## HTML template
<b>:### HTML rendering rules
<c>:## Output principles
```
with `a < b < c`.

- [ ] **Step 4: Commit Task 3.**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add product-discovery/skills/OST-compare-opportunities/SKILL.md
git commit -m "$(cat <<'EOF'
OST-compare-opportunities: add HTML rendering rules

Documents the per-column rendering rules (empty/filtered states), the
card sort order, the filter chip semantics, the phase tint convention,
the JS scope (~50 LOC inline only, no external deps), and the
step-index anchor scheme. Anchor IDs use opp-X-Y, phase-<phase_id>,
and step-<step_id>.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Update front matter, intro, output principles, and "does NOT do"

**Why this task is fourth:** Now that the HTML render path exists end-to-end, small touch-ups across the file bring prose in sync. The description and opening paragraph still say "JSON + markdown" (no HTML). The output principles don't mention the third artifact or the JS rule. The "does NOT do" list says "JSON + markdown only" which is no longer accurate.

**Files:**
- Modify: `product-discovery/skills/OST-compare-opportunities/SKILL.md` — four small edits.

- [ ] **Step 1: Update the description front-matter line.**

Find this exact line:

```markdown
description: For product trios and researchers, when comparing approved opportunities against a product outcome and Torres criteria, output a paired JSON + markdown rendering with a qualitative comparison matrix (criteria × opportunities) plus an evidence-gap list of unknown cells.
```

Replace with:

```markdown
description: For product trios and researchers, when comparing approved opportunities against a product outcome and Torres criteria, output paired JSON + markdown + HTML. JSON and markdown carry the full 5×N matrix; HTML renders the same data as journey-grouped opportunity cards with expandable rationales and filter chips, scannable at 96 opportunities.
```

- [ ] **Step 2: Update the opening paragraph (line 8 in canonical).**

Find this exact line:

```markdown
You help a product trio compare approved opportunities against their product outcome and Torres prioritization criteria, producing paired JSON (per the opportunity-comparison schema v0.1) plus a markdown rendering. The output is a 5×N matrix (5 Torres-derived criteria × N approved opportunities) with qualitative scores and grounded rationales, plus an evidence-gap list derived from cells that scored `unknown`.
```

Replace with:

```markdown
You help a product trio compare approved opportunities against their product outcome and Torres prioritization criteria, producing paired JSON (per the opportunity-comparison schema v0.1) plus a markdown rendering and a self-contained HTML rendering. The data shape is a 5×N matrix (5 Torres-derived criteria × N approved opportunities) with qualitative scores and grounded rationales, plus an evidence-gap list derived from cells that scored `unknown`. The JSON and markdown render this as a literal matrix table; the HTML renders the same data as a journey-grouped card view (phases as swim-lane columns) optimized for skimming at 96+ opportunities.
```

- [ ] **Step 3: Add three new bullets to the Output principles section.**

Find this exact line under `## Output principles`:

```markdown
- **Upstream files are immutable.** Never modify `<scope>/experience-map-clustered.json` or `<scope>/../../_product-context/product-outcome.md`. The skill only writes `<scope>/comparison-matrix.json` and `<scope>/comparison-matrix.md`.
```

Replace with three bullets (one modified + two new):

```markdown
- **Upstream files are immutable.** Never modify `<scope>/experience-map-clustered.json` or `<scope>/../../_product-context/product-outcome.md`. The skill only writes `<scope>/comparison-matrix.json`, `<scope>/comparison-matrix.md`, and `<scope>/comparison-matrix.html`.
- **Three artifacts, one render.** `.json`, `.md`, and `.html` are written from the same composed JSON in a single pass. They carry identical data; the markdown and HTML are different views of the JSON. Never write one without the other two, and never re-render one in isolation.
- **HTML is self-contained.** Inline `<style>` and inline `<script>` only. No external CSS, no remote fonts, no external scripts. JS is limited to ~50 LOC of filter logic. See HTML rendering rules in the "HTML template" section above.
```

- [ ] **Step 4: Update the "one pair of output files" line in the `## What this skill does NOT do` section.**

Find this exact line:

```markdown
- **Iterate, retry, or run multiple passes.** One pass over the inputs, one pair of output files.
```

Replace with:

```markdown
- **Iterate, retry, or run multiple passes.** One pass over the inputs, one set of three output files.
```

- [ ] **Step 5: Update the "Write to Miro" line in the `## What this skill does NOT do` section.**

Find this exact line:

```markdown
- **Write to Miro or any external surface.** JSON + markdown only.
```

Replace with:

```markdown
- **Write to Miro or any external surface.** JSON + markdown + HTML only, all local files under `<scope>/`.
```

- [ ] **Step 6: Verify all five edits.**

Run: `grep -n "scannable at 96 opportunities\|swim-lane columns\|Three artifacts, one render\|one set of three output files\|JSON + markdown + HTML only" product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected: five hits, one per edit.

Run: `head -10 product-discovery/skills/OST-compare-opportunities/SKILL.md`
Expected: YAML front matter still valid (`---` delimiters intact, single `description:` line, no stray whitespace).

- [ ] **Step 7: Commit Task 4.**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add product-discovery/skills/OST-compare-opportunities/SKILL.md
git commit -m "$(cat <<'EOF'
OST-compare-opportunities: sync front matter and output principles with HTML output

Description and opening paragraph now distinguish the JSON/markdown
matrix view from the HTML journey-card view. Output principles gain
'Three artifacts, one render' and 'HTML is self-contained' rules.
'Does NOT do' list updates 'Write to Miro' to include HTML.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Verify against the Metria fixture (manual, HITL)

**Why this task is last among the edits:** The skill is prompt-driven; the only meaningful "test" is rendering it against a real dataset. The Metria fixture (96 opps, 5 phases, 0-opp Fulfillment, 40 unphased) is the worst case the redesign targets — if it scans cleanly there, smaller datasets follow trivially.

**Files:**
- No code edits in this task. Verification only.

- [ ] **Step 1: Ask the user where the Metria discovery scope lives.**

The Metria fixture lives outside this plugin repo. Ask the user (or check `~/claude-projects/`) for the absolute path to the Metria discovery scope folder — the one that contains `experience-map-clustered.json`. Example shape:

```
/Users/jonilindgren/<projects-root>/metria/discovery/<team>/<product>/opportunity-selection/<YYYY-MM-DD>/
```

You need this path for the next steps. If the user can't immediately produce it, ask them to set `.current-scope` on the Metria workspace and run from there.

- [ ] **Step 2: If a previous render exists, snapshot the current JSON and markdown for diff.**

Run (substitute `<scope>` with the path from Step 1):

```bash
cp <scope>/comparison-matrix.json /tmp/comparison-matrix.before.json 2>/dev/null || echo "no prior JSON"
cp <scope>/comparison-matrix.md   /tmp/comparison-matrix.before.md   2>/dev/null || echo "no prior MD"
```

There is no prior `.html` to snapshot — this skill produces HTML for the first time.

- [ ] **Step 3: Force-sync the marketplace cache so a fresh session picks up the edits.**

Per CLAUDE.md, the marketplace cache mirrors at `~/.claude/plugins/cache/scilla-studio/product-discovery/1.0.0/skills/`. Until the next session start (when autoUpdate refreshes from GitHub), the cache won't have your edits. Either:

- Copy directly: `cp -R product-discovery/skills/OST-compare-opportunities/ ~/.claude/plugins/cache/scilla-studio/product-discovery/1.0.0/skills/` then restart Claude Code, OR
- Push and restart: `git push origin master` and restart Claude Code (autoUpdate pulls from GitHub).

- [ ] **Step 4: Run the skill end-to-end.**

In a fresh Claude Code session inside the Metria project directory, invoke `OST-compare-opportunities`. It will read upstream files, score cells, generate AI titles, and produce three artifacts. Wait for completion.

Expected outcome: three files written under `<scope>/`:
- `comparison-matrix.json` (with new fields)
- `comparison-matrix.md` (byte-identical to prior render, if any)
- `comparison-matrix.html` (new file, swim-lane layout)

- [ ] **Step 5: Diff the JSON against the prior render.**

```bash
diff /tmp/comparison-matrix.before.json <scope>/comparison-matrix.json | head -100
```

Expected diff content (if a prior JSON existed):
- New `journey_phases` array at top level.
- New `summary_title` per opportunity.
- New `score_counts` per opportunity.
- `schema_version` still `"0.1"`.

No structural diffs in `opportunities_compared[]`, `criteria[]`, `evidence_gaps[]`, or `opportunities_excluded[]` (modulo the additive fields above).

If no prior JSON existed, this step is N/A; verify the new JSON has the three additive fields:

```bash
jq '.schema_version, (.journey_phases | length), (.opportunities_compared[0] | keys)' <scope>/comparison-matrix.json
```

Expected: `"0.1"`, a positive integer, and an array of keys that includes `summary_title` and `score_counts`.

- [ ] **Step 6: Byte-diff the markdown against the prior render.**

```bash
diff /tmp/comparison-matrix.before.md <scope>/comparison-matrix.md
```

Expected: no output (byte-identical). Title generation must not leak into the markdown.

If the markdown diffs, that's a bug in step 12 (markdown render) — likely an accidental reference to a new field. Open SKILL.md and check the markdown template region for any inserted `<summary_title>` or `<score_counts>` placeholders. Fix and re-render.

- [ ] **Step 7: Open the HTML in Chrome and walk the verification checklist.**

```bash
open -a "Google Chrome" <scope>/comparison-matrix.html
```

Manually verify each item:

1. The filter bar is visible at the top of the viewport and stays visible when you scroll vertically.
2. Each phase column header sticks under the filter bar when you scroll.
3. Clicking `strong-heavy (≥3 strongs)` filters cards live; counter updates to "N of 96 shown".
4. Clicking `has weak` while `strong-heavy` is still active AND-combines; counter drops further.
5. Clicking `has unknown` adds another AND filter; counter drops further.
6. Clicking Reset clears all chips and counter returns to "96 of 96 shown".
7. The Fulfillment column (the zero-opp phase) shows the "No opportunities in this phase." placeholder.
8. The Unphased column appears as the rightmost column with the dashed left border, listing all 40 unphased opportunities.
9. Click any card in the Efterarbete column — it expands inline via the native `<details>` toggle. Open a second card without closing the first; both stay open.
10. The expanded card shows the full quote, source citation, and 5 rationale rows (one per criterion), with unknown and n/a rows missing their Cites line.
11. The step label in the card's top-right is a link; clicking it scrolls to the Step index at the bottom of the page.
12. Cmd-P (print preview) shows every card fully expanded, the filter bar gone, and no chevron markers on `<details>`.

Then verify in Safari:

```bash
open -a Safari <scope>/comparison-matrix.html
```

Verify items 1-12 again. Safari's `<details>` styling and `:has()` selector support are the most common sources of regression.

- [ ] **Step 8: Verify the file is fully self-contained.**

```bash
grep -nE "https?://|src=|href=\"//\|@import" <scope>/comparison-matrix.html | grep -v "href=\"#"
```

Expected: no output. The only `href` references should be in-page fragments (`#opp-X-Y`, `#phase-...`, `#step-...`).

- [ ] **Step 9: Verify offline rendering.**

Disable wifi (or use a `file://` URL while disconnected). Reload `<scope>/comparison-matrix.html` and re-run steps 7.1–7.12.

Expected: identical behavior. No network errors in the browser console.

- [ ] **Step 10: Verify sorting within a column.**

Pick the Beställning column (24 opps). Compare card order on screen against the JSON:

```bash
jq '.opportunities_compared[] | select(.phase_id == "beställning") | {id, strong: .score_counts.strong, weak: .score_counts.weak}' <scope>/comparison-matrix.json
```

Sort the output by `strong DESC, weak ASC, id (upstream order tiebreaker)`. The rendered card order must match.

- [ ] **Step 11: Re-render and verify the title cache.**

Re-run the skill. Watch for:
- The render completes faster (no LLM titles regenerated).
- Diff the JSON before/after: `summary_title` values are byte-identical for every opportunity.

If titles re-generated despite being present, the cache rule in step 10 of the procedure isn't being honored — re-open SKILL.md and verify the cache rule wording is clear.

- [ ] **Step 12: If any verification step failed, file the failure as a fix task and re-run from Step 4.**

Do not declare verification passed if any of the steps above failed. List the failures and stop; the user will direct the fix.

- [ ] **Step 13: No commit in this task.** Verification only.

---

## Task 6: Update CLAUDE.md current state

**Why this task is last:** Capture what shipped and what's still loose so the next session has accurate context.

**Files:**
- Modify: `/Users/jonilindgren/claude-projects/claude-plugins/CLAUDE.md` — replace the **In progress:** line and add a "Recent decisions" block.

- [ ] **Step 1: Read the current state section.**

Run: `grep -n "^## Current State\|^\*\*In progress\|^\*\*Recent decisions" CLAUDE.md`
Expected: see where the **Current State** section starts and what's there.

- [ ] **Step 2: Update the `In progress` line and add a new Recent decisions block at the top of the section.**

Find this line:

```markdown
**In progress:** Nothing active. Last shipped: discovery-workspace rename + single-product mode + opportunity-selection rename (2026-05-15). Same day: `OST-setup-product` and `OST-init-workspace`.
```

Replace with:

```markdown
**In progress:** OST-compare-opportunities HTML rendering shipped to `master`; needs first live use on the Metria 96-opp fixture (Task 5 of the plan was run as part of execution, but the trio hasn't actually used the new layout in a real workshop yet — first real-trio session is the real test). Last shipped: HTML swim-lane rendering for `OST-compare-opportunities` (2026-05-22). Earlier: discovery-workspace rename + single-product mode + opportunity-selection rename (2026-05-15). Same day: `OST-setup-product` and `OST-init-workspace`.

**Recent decisions (OST-compare-opportunities HTML rendering, 2026-05-22):**
- Added HTML as a third paired output alongside JSON + markdown. Reason: the markdown matrix is unscannable at workshop scale (Metria has 96 opps × 5 criteria = 480 cells). HTML uses a swim-lane card layout (phases as columns) sorted by strong-count then weak-count, expandable via native `<details>` for per-criterion rationales.
- A previous session experimented with a literal matrix HTML table in the marketplace clone. That work was never pushed to GitHub and is abandoned. We went straight to the swim-lane redesign on a clean canonical base.
- AI-generated `summary_title` per opportunity, cached in the persisted JSON so re-renders are stable and cheap. Trio can override by hand-editing the JSON. Hard exit on title-generation failure with the opp-id named.
- Added two additive fields per opportunity (`summary_title`, `score_counts`) and one top-level field (`journey_phases`) under schema version 0.1 — backward-compatible additions, no schema version bump. `journey_phases` carries zero-opp phases through so empty columns still render (Metria's Fulfillment is zero-opp).
- ~50 LOC of inline vanilla JS is now allowed in the HTML output for filter chip toggling. External dependencies still forbidden. The file remains self-contained and openable offline. This is the first OST skill that ships runtime JS.
- Filter chips: `strong-heavy (≥3 strongs)`, `has weak`, `has unknown`. AND-combined when multiple active. Per-criterion filtering intentionally absent — the markdown view + Cmd-F is the deep-inspection escape hatch.
- Card sort within column: strong-count DESC, weak-count ASC, then upstream `opportunities_compared[]` order. Deterministic, no randomness.
- Markdown template untouched — it stays the "complete tabular view" while the HTML is the "skim view." JSON+MD+HTML still ship as a paired triple from a single render pass.
- Spec: `docs/superpowers/specs/2026-05-22-ost-compare-opportunities-html-redesign-design.md`. Plan: `docs/superpowers/plans/2026-05-22-ost-compare-opportunities-html-redesign.md`.
```

- [ ] **Step 3: Add a follow-up bullet to the Next steps section.**

Find the existing `**Next steps (when picked up):**` block. Add this bullet at the top of the list:

```markdown
- `OST-compare-opportunities`: needs first live workshop with a real trio on the Metria 96-opp fixture. Watch for: does the trio find the strong-heavy filter useful? Does the AI title style feel natural in Swedish, or do trios reach for the JSON to override? Does the empty `Fulfillment` column communicate "no opps here" clearly enough?
```

- [ ] **Step 4: Verify CLAUDE.md still scans cleanly.**

Run: `head -100 CLAUDE.md`
Expected: no malformed markdown, section headings in order, no doubled headings.

- [ ] **Step 5: Commit Task 6.**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
CLAUDE.md: capture OST-compare-opportunities HTML rendering decisions

Records what shipped (swim-lane layout, AI titles, three additive
JSON fields, light JS for filter chips), why (96-opp scannability),
the abandoned matrix-HTML experiment, and what still needs validation
(first real-trio workshop on the Metria fixture).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Plan Self-Review

**Spec coverage check.** Walking each section of the spec:

- *Motivation* — context only, no implementation needed.
- *What changes / does NOT change* — covered by Task 1 (procedure), Task 2 (template), Task 3 (rules), Task 4 (front matter + principles).
- *Composed JSON additions* (`summary_title`, `score_counts`, `journey_phases`) — covered by Task 1 (steps 2, 3, 4).
- *HTML structure* — covered by Task 2 (template body).
- *Layout: swim-lanes* — covered by Task 2 (CSS + grid markup) and Task 3 (rendering rules per-column).
- *Card design (collapsed + expanded)* — covered by Task 2 (template) and Task 3 (rules).
- *Filter bar and JS* — covered by Task 2 (inline `<script>`) and Task 3 (filter chip semantics).
- *AI title pass* — covered by Task 1 (new step 10).
- *Print and share* — covered by Task 2 (`@media print` block in inline `<style>`).
- *Verification checklist* — covered by Task 5 (11 sub-steps mirror the spec's checklist).
- *Risks and mitigations* — addressed in spec; the cache rule is Task 1 step 3, the JS-rule documented in Task 3 step 2 / Task 4 step 3.
- *Out of scope* — no plan tasks; nothing to do.

No spec gaps detected.

**Placeholder scan.** Searched the plan for the "No placeholders" red flags:
- "TBD" / "TODO" / "implement later" — none.
- "appropriate error handling" / "add validation" / "handle edge cases" — none.
- "Write tests for the above" — N/A; this skill has no test runner.
- "Similar to Task N" — none; each task is self-contained.
- Steps without code — every code-bearing step shows the full text to insert or replace.

**Type consistency check.**
- `summary_title` (lowercase snake_case) — consistent across Task 1 step 3, Task 1 step 3 (compose step), Task 2 template (`<summary_title>` placeholder), Task 3 step 2 ("renders the AI-generated `summary_title` from the JSON"), Task 5 step 5.
- `score_counts` — consistent across Task 1 step 3, Task 1 step 3 (compose step), Task 2 template (`data-strong-count="<n>"` derived from `score_counts.strong`), Task 3 step 2 (filter chip semantics reference `score_counts.strong/weak/unknown`).
- `journey_phases` — consistent across Task 1 step 2, Task 1 step 3 (compose step), Task 2 template comment ("one `<div class="swim-col">` per entry in `journey_phases[]`"), Task 3 step 2 ("one column per entry in `journey_phases[]`").
- CSS class names (`swim-col`, `opp-card`, `card-standouts`, `card-step`, `card-title`, `card-no-standouts`, `card-detail`, `rationale-row`, `swim-col-head`, `swim-col-empty`, `swim-col-nomatch`, `is-empty-filter`, `score-pill`, `crit-name`, `cites`, `phase-name`, `phase-count`, `filters`, `chip`, `reset`, `counter`) — all defined in Task 2's `<style>` and referenced verbatim in Task 2's markup, Task 3's rules, and Task 5's verification commands.
- Anchor ID conventions (`opp-X-Y`, `phase-<phase_id>`, `phase-unphased`, `step-<step_id>`) — defined in Task 3 and used in Task 2 template and Task 5 verification.

No drift detected.
