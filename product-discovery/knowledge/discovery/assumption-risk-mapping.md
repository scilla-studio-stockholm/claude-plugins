---
title: Assumption risk mapping
date: 2026-05-12
purpose: Reference for the 2x2 method that identifies the riskiest assumptions per solution, based on David Bland's Assumptions Mapping. Used by the OST-riskiest-assumptions agent in phase 4. Specifies the two scoring questions, the quadrant interpretation and the JSON output schema downstream consumers expect.
tags: [assumptions, risk, validation, bland, leap-of-faith]

---

# Assumption risk mapping

## What this document is

A reference for identifying the riskiest assumptions among those generated and categorized in fas 3. Riskiness is determined by a 2x2 mapping based on two binary scoring questions per assumption.

The taxonomy is used in two places:

- **By the AI OST-riskiest-assumptions agent** (`claude-plugins/product-discovery/skills-design/opportunity-solution-tree-agents.md`, fas 4) when scoring and outputting assumptions to JSON for downstream consumers.
- **By trios** as a learning aid when practicing risk-mapping themselves.

## Where this sits in the OST flow

After all assumptions for a solution have been generated and categorized (fas 3), the trio cannot meaningfully test all of them. The next step in OST is to identify the **riskiest** assumptions and test those first. Torres calls this "test the riskiest assumptions". David Bland operationalizes the prioritization through a 2x2 mapping.

The output of this step feeds into assumption testing (designing experiments to validate the riskiest assumptions), which sits outside the current scope.

## Source

David J. Bland and Alexander Osterwalder, *Testing Business Ideas* (Wiley, 2019). The Assumptions Mapping technique sits in chapter 1 ("Design") of the book and builds on Eric Ries' *The Lean Startup* concept of "leap of faith assumptions".

The version below is a simplified variant. Bland's original uses slightly different axis labels but the core 2x2 logic is identical.

## The 2x2 framework

Two binary axes per assumption:

| Axis | Low end | High end |
|------|---------|----------|
| **Importance** (vertical) | Less decisive | More decisive |
| **Evidence** (horizontal) | Weak evidence | Strong evidence |

The quadrants:

```text
                      More decisive
                            │
                            │
   Strong evidence ─────────┼───────── Weak evidence
                            │
                            │
                      Less decisive
```

- **Top-right (High importance + Weak evidence):** **Riskiest assumptions.** These are leap-of-faith assumptions. If they turn out to be false, the solution fails. Test these first with cheap, fast experiments.
- **Top-left (High importance + Strong evidence):** Important but already evidenced. Keep an eye on them but they are not the priority.
- **Bottom-right (Less decisive + Weak evidence):** Defer. Worth knowing about but not blocking.
- **Bottom-left (Less decisive + Strong evidence):** Settled. Move on.

## The two scoring questions

For each assumption, ask both:

### Question 1: Evidence

> **Har vi redan bevis för att det här antagandet är sant?**

If yes → **strong evidence** (left side).
If no → **weak evidence** (right side).

What counts as evidence: customer interview data, prior product validation, market research, internal usage data, or other empirical observation. Internal opinion or "we think so" does not count as evidence.

### Question 2: Importance

> **Om vi har fel i det här antagandet, skiter det sig då?**

If yes → **more decisive** (top).
If no → **less decisive** (bottom).

What "skiter det sig" means: the solution materially fails to deliver its impact on the product outcome. Edge-case wobbles do not qualify. The bar is whether the solution as a whole stops working.

## JSON output schema (v0.1)

The OST-riskiest-assumptions agent outputs JSON in this structure. Downstream consumers (assumption testing, trion review, future risk dashboards) read it.

```json
{
  "schema_version": "0.1",
  "method": "assumption-risk-mapping",
  "method_source": "David Bland, Testing Business Ideas (2019)",
  "solutions": [
    {
      "solution_id": "string",
      "title": "string",
      "assumptions": [
        {
          "assumption_id": "string",
          "text": "string (the assumption verbatim)",
          "category": "desirability | usability | feasibility | viability | other",
          "importance": "high | low",
          "evidence": "strong | weak",
          "is_riskiest": "boolean (true when importance=high AND evidence=weak)",
          "rationale": "string (one-line explanation of the scoring)"
        }
      ]
    }
  ]
}
```

### Field notes

- **`importance`** and **`evidence`** are binary, mirroring the two yes/no scoring questions. No graded scale. The simplification is deliberate: graded scoring invites false precision and rabbit holes.
- **`is_riskiest`** is computed from importance and evidence. Including it as an explicit field makes downstream consumption simpler than re-deriving it.
- **`rationale`** is a required one-line string. It exists so the trion can validate AI:s scoring at a glance and so future audits can see the reasoning. Brief, not a paragraph.
- **`category`** is preserved from fas 3 categorization. It travels with the assumption through fas 4 because some downstream uses (e.g., risk dashboards split by category) need it.

## Application notes

- **Riskiness is per solution, not global.** An assumption that is risky for solution A may not exist for solution B. The JSON groups assumptions under their solution.
- **Not every solution will have the same number of riskiest assumptions.** Some may have several, others zero. Both are legitimate outputs.
- **The agent does not propose tests.** That is the next step (assumption testing), out of scope here. Output stops at "this is risky and here is why".
- **Practice note:** As trios train their ability to see assumptions and assess risk, the matrix becomes scaffolding rather than the goal. AI is a training aid, not a permanent crutch.

## Open evolutions

- Add an explicit "uncertain" option to either axis if trios report that binary scoring forces premature commitment? Bland's original is binary; we follow him for now.
- Track scoring history when the same assumption is re-mapped (evidence changes over time as testing happens). Out of scope for v0.1.

## v0.2 extensions (2026-05-12)

The sections below extend v0.1 for the `OST-riskiest-assumptions` skill (assist 11). The v0.1 framework, scoring questions, and application notes above are unchanged. v0.2 adds the runtime contract the skill reads at execution: a soft-evidence rule (replacing the strict empirical-only standard for the AI scoring pass; trios still override at HITL), a structured rationale format (regex-checked), full identity-mapping over the upstream assist-10 output (every upstream field byte-identical; 4 new per-assumption fields), the v0.2 JSON schema, and the renderer template with Trio HITL gate banner.

### Soft-evidence rule (v0.2)

Evidence includes empirical observation from the inputs AND domain norms, industry conventions, and general engineering practice. Mark `strong` if the assumption seems well-grounded; mark `weak` if genuinely speculative.

The v0.1 anchor said "internal opinion does not count as evidence". v0.2 softens that for the AI scoring pass: the LLM may reason about plausibility using its general knowledge. Trion override at HITL by editing the paired JSON. The v0.1 strict standard remains the right standard when trions do the scoring themselves manually; v0.2 is the rule the AI applies when it scores.

### Rationale format rule (v0.2)

Write rationale as one sentence in the form:

```text
Importance=<level> (<reason>); evidence=<level> (<reason>).
```

Each parenthetical reason is one short clause. The format is regex-checked at validation:

```text
^Importance=(high|low) \(.+\); evidence=(strong|weak) \(.+\)\.$
```

Each rationale covers both axes in one sentence; the structure makes downstream parsing trivial and gives the trion a fixed scan pattern at review.

### Carry-forward rules and identity-mapping invariants (v0.2)

Every upstream field from the assist-10 v0.1 output carries through byte-identical. The skill adds exactly four per-assumption fields: `importance`, `evidence`, `is_riskiest`, `rationale`. Specifically:

- Top-level: `team`, `title`, `product_outcome`, `chosen_opportunity.*`, `source_assumptions`, `source_top_three_solutions`, `source_experience_map`, `categorization_summary` carried verbatim.
- Per-solution: `pick_position`, `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number` carried byte-identical.
- Per-assumption: `id`, `text`, `source_methods`, `category` carried byte-identical; `importance`, `evidence`, `is_riskiest`, `rationale` are added.

No re-ordering, no re-wording, no merging, no dropping, no enrichment beyond the four new fields.

**`is_riskiest`** is computed by the skill from importance and evidence: `is_riskiest = (importance == "high" AND evidence == "weak")`. The LLM returns importance + evidence + rationale only; the skill derives `is_riskiest` itself. This prevents LLM drift on the riskiest definition and guarantees the schema invariant holds.

**Identity-mapping invariants** (hard-exit on violation, no partial writes):

- `assumptions_per_solution.length == 3`.
- For each per-solution entry, `assumptions.length` equals the corresponding upstream per-solution entry's `assumptions.length`.
- For each per-solution entry, the upstream `assumptions[]` ids appear in the output in the same order at each index.
- Every `importance` in `{high, low}`; every `evidence` in `{strong, weak}`; exactly one value each; never null; never an array.
- Every `rationale` matches the regex above.
- `is_riskiest == true` iff `importance == "high" AND evidence == "weak"` (computed, not LLM-decided).
- Every upstream field is byte-identical to the source JSON (top-level, per-solution, per-assumption).
- `risk_summary.total_assumptions` equals the sum of `assumptions[].length` across the three solutions.
- `risk_summary.total_riskiest` equals the count of assumptions where `is_riskiest=true`.
- `risk_summary` matches the fixed v0.2 block (other than the two integer fields).

### JSON schema (v0.2)

```json
{
  "schema_version": "0.2",
  "method": "assumption-risk-mapping",
  "method_source": "David Bland, Testing Business Ideas (2019)",
  "team": "string (carried byte-identical from upstream assumptions-categorized-*.json)",
  "title": "string (carried byte-identical)",
  "product_outcome": "string (carried byte-identical)",
  "chosen_opportunity": {
    "id": "string (carried byte-identical)",
    "phase_id": "string (carried byte-identical)",
    "quote": "string (carried byte-identical)",
    "source": "string (carried byte-identical)"
  },
  "source_assumptions_categorized": "string (filename of source assumptions-categorized-*.json)",
  "source_assumptions": "string (carried byte-identical)",
  "source_top_three_solutions": "string (carried byte-identical)",
  "source_experience_map": "string (carried byte-identical)",
  "categorization_summary": "object (carried byte-identical from upstream)",
  "risk_summary": {
    "framework": "2x2 importance x evidence (David Bland)",
    "evidence_rule": "soft: domain norms and industry conventions count",
    "rationale_format": "single sentence; importance-then-evidence",
    "total_assumptions": "integer (sum across all 3 solutions)",
    "total_riskiest": "integer (count where is_riskiest=true)"
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
          "category": "string (carried byte-identical; one of desirability | usability | feasibility | viability | other)",
          "importance": "high | low",
          "evidence": "strong | weak",
          "is_riskiest": "boolean (computed: importance=high AND evidence=weak)",
          "rationale": "string (format: 'Importance=<level> (<reason>); evidence=<level> (<reason>).')"
        }
      ]
    }
  ]
}
```

### Renderer template (v0.2)

````markdown
---
title: "Riskiest assumptions: <chosen_opportunity.id> - <first 5-10 words of quote>"
date: <YYYY-MM-DD>
purpose: Per-solution assumptions scored on importance x evidence (Bland 2x2), with the riskiest flagged. Phase-3 trio review-and-approve gate. Paired with OST-riskiest-assumptions-<date>.json. Input to assist 12 (OST-validation-experiment-designer).
tags: [assumption-risk-mapping, ost, bland, schema-v0.2]

---

# Riskiest assumptions: <chosen_opportunity.id>

> **Trio HITL gate.** Review the importance/evidence calls per assumption. If you disagree, edit the paired JSON directly. Riskiest rows are flagged `[RISKIEST]` inline; each solution opens with a `Riskiest:` summary line of the flagged ids. Assist 12 will read the latest `riskiest-assumptions-*.json` by date in filename.

Source assumptions-categorized: `<source_assumptions_categorized>`
Source assumptions: `<source_assumptions>`
Source top 3 solutions: `<source_top_three_solutions>`
Source chosen opportunity: `<scope>/../chosen-opportunity.md`
Source product outcome: `<scope>/../../../_product-context/product-outcome.md`
Schema version: 0.2
Paired JSON: `OST-riskiest-assumptions-<YYYY-MM-DD>.json`

Framework: 2x2 importance x evidence (David Bland, *Testing Business Ideas* 2019). Riskiest = high importance + weak evidence. Evidence rule: soft (domain norms and industry conventions count). Rationale format: single sentence, importance-then-evidence.

Total assumptions: <N>. Total riskiest: <M>.

## Chosen opportunity

**<chosen.id>** (Phase: <phase_id>) - "<quote>" - *<source>*

## Product outcome

> <outcome formulation>

## Solution 1: <solution_title>

**<solution_id>** [<role-abbrev>, R<round_number>]

<solution_description>

**Riskiest:** <comma-separated ids of riskiest in this solution, or "(none)">

### Assumptions (<count>)

- **<asm-id>** [<methods-tag>] [<category>] [<importance>/<evidence>] [optional **[RISKIEST]**] <text>
  - <rationale>
- **<asm-id>** [<methods-tag>] [<category>] [<importance>/<evidence>] <text>
  - <rationale>
- ...

## Solution 2: <solution_title>

(same shape)

## Solution 3: <solution_title>

(same shape)
````

Rendering rules:

- Role abbreviation, method-tag, category-tag mappings carried unchanged from assist 10 (`product-manager` -> `PM`, `ux-designer` -> `UX`, `tech-lead` -> `TL`; `storymap` -> `SM`, `pre-mortem` -> `PrM`, `outcome-impact` -> `OI`; categories lowercase verbatim).
- Score tag: `[<importance>/<evidence>]` with values lowercase verbatim. Four possible values: `[high/strong]`, `[high/weak]`, `[low/strong]`, `[low/weak]`.
- `[RISKIEST]` marker: appears only when `is_riskiest=true`. Bold all-caps in brackets, placed AFTER the score tag and BEFORE the text. Format: `**[RISKIEST]**`.
- Tag order per row is fixed: `[<methods>] [<category>] [<importance>/<evidence>] [optional RISKIEST]`. Methods -> category -> score -> optional riskiest marker -> text.
- Rationale rendered as a nested sub-bullet under each assumption row, indented 2 spaces, single line, verbatim from JSON. Never edited at render.
- Per-solution `Riskiest:` summary line. Placed between the solution-description paragraph and the `### Assumptions (<count>)` heading. Format: `**Riskiest:** <comma-separated ids>` or `**Riskiest:** (none)` if zero riskiest in that solution.
- Trio HITL banner: top-of-body blockquote (`>` prefix), placed after the H1 and before the source-metadata lines. Verbatim text from the template above.
- Total summary line: `Total assumptions: <N>. Total riskiest: <M>.` placed after the framework-summary paragraph.
- Chosen-opportunity source attribution carried verbatim. Separated from the quote with ` - ` (regular dash).
- No em-dash anywhere. Frontmatter has blank line before closing `---`.
- No `Cites:` line.
- Pick ordering in the markdown mirrors the upstream `picks[]` array order.
- Row ordering within each solution preserves the upstream `assumptions[]` order. No re-sort by score or risk.
- Output language for assumption text and rationale follows the language of the upstream (typically Swedish for this trio). Schema field names, JSON keys, importance/evidence enum values, role enums, and id strings stay English.

## Evolution

| Version | Date | Change |
|---|---|---|
| v0.1 | 2026-05-06 | Initial 2x2 framework with binary axes (importance high/low, evidence strong/weak), two Swedish scoring questions, JSON schema v0.1 (`solutions[]` shape), application notes. |
| v0.2 | 2026-05-12 | Extended for the OST-riskiest-assumptions skill (assist 11): identity-mapping over upstream assist-10 output (every upstream field byte-identical + 4 new per-assumption fields), soft-evidence rule, structured rationale format (regex-checked), schema v0.2 (full carry-forward shape using `assumptions_per_solution[]` and `id` field names), renderer template with Trio HITL gate banner. |
