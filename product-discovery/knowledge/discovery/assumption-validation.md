---
title: Assumption validation experiments
date: 2026-05-12
purpose: Reference for designing the cheapest viable validation experiment per riskiest assumption, based on David Bland's Test Card method and experiment catalog. Used by the OST-validation-experiment-designer assist in workshop 3 fas 5. Specifies the Test Card structure, common test types with effort/time/evidence ratings and the JSON output schema downstream consumers expect.
tags: [assumptions, validation, testing, experiments, bland, test-card]

---

# Assumption validation experiments

## What this document is

A reference for designing validation experiments for the riskiest assumptions surfaced in fas 4. The goal is the cheapest, fastest test that produces enough evidence to know whether the assumption holds.

The document is used in two places:

- **By the AI OST-validation-experiment-designer agent** (`claude-plugins/product-discovery/skills-design/opportunity-solution-tree-agents.md`, fas 5) when proposing per-assumption Test Cards to JSON and markdown for trion review.
- **By trios** as a learning aid when designing experiments themselves and as a reference catalog of test types.

## Where this sits in the OST flow

After the riskiest assumptions per solution are flagged in fas 4, the next step in OST and Bland's process is to design experiments that validate or invalidate them. Torres calls this "test the riskiest assumptions". Bland operationalizes it through the Test Card template applied to a catalog of experiment types.

The output of this step feeds into experiment execution and result interpretation, which sits outside the current scope.

## Source

David J. Bland and Alexander Osterwalder, *Testing Business Ideas* (Wiley, 2019). The Test Card structure and experiment catalog are central to the book. The catalog contains 44 experiment types organized along several dimensions; this document distills a representative subset that covers most assumption categories at low effort.

## The Test Card structure

A Test Card is a one-page artifact that captures everything a trio needs to run an experiment. It has four mandatory parts:

| Field | Pattern |
|-------|---------|
| **Hypothesis** | "We believe that [the assumption]" |
| **Test** | "To verify that, we will [concrete test method and steps]" |
| **Metric** | "And measure [the data point we collect]" |
| **Success criteria** | "We are right if [threshold the metric must hit]" |

The Test Card forces the trio to commit to a falsifiable threshold before running the test. Without that, the result is interpretable in any direction and the test is useless.

## Selection principles

Per Bland and per Joni's brief ("med minst effort"):

1. **Cheapest viable test first.** Pick the experiment that produces enough evidence at the lowest cost. "Enough evidence" depends on the decision the trio will make from the result.
2. **Match the test to the assumption type.** Desirability assumptions need real customer behavior, not opinions. Feasibility assumptions need technical proof, not user voting. Viability needs revealed preferences, not surveys.
3. **Prefer revealed preferences over stated ones.** People say one thing and do another. A landing page with a sign-up beats a survey asking "would you sign up".
4. **Time-box the test.** Without a deadline the experiment becomes a project.
5. **Plan for both outcomes.** What does the trio do if the assumption holds, and what if it does not? If the answer is "nothing changes either way", the test is not worth running.

## Common test types

A representative subset of Bland's catalog. For each test, the table lists which assumption category it most often suits, plus rough cost, time and evidence-strength ratings.

| Test type | Best for | Cost | Time | Evidence |
|-----------|----------|------|------|----------|
| Customer interview | Desirability, usability | Low | Hours-days | Moderate (qualitative) |
| Survey | Desirability (broad) | Low | Days | Weak (stated preference) |
| Landing page with sign-up | Desirability, viability | Medium | Days | Moderate (revealed interest) |
| Smoke test (fake door, 404 ad) | Desirability | Low | Days | Weak-moderate |
| Wizard of Oz | Usability, desirability | Medium | Days-weeks | Strong |
| Concierge | Usability, desirability | Medium | Days-weeks | Strong |
| Paper or click-through prototype | Usability | Low | Hours-days | Moderate |
| Pre-order or pre-sale | Desirability, viability | Medium | Days-weeks | Strong (revealed preference plus money) |
| Technical spike or proof-of-concept | Feasibility | Low-medium | Days-weeks | Strong |
| A/B test (with existing traffic) | Usability, desirability | Low-medium | Days-weeks | Strong (with sufficient n) |
| Card sort or 5-second test | Usability | Low | Hours-days | Moderate |
| Search trend analysis | Desirability (latent demand) | Low | Hours | Weak-moderate |

The catalog is not exhaustive. When the riskiest assumption is unusual, the trio or the agent should consult Bland directly for additional test types.

## JSON output schema (v0.1)

The OST-validation-experiment-designer agent produces JSON in this structure. Downstream consumers (assumption testing execution, future experiment-tracking dashboards, trion review) read it.

```json
{
  "schema_version": "0.1",
  "method": "assumption-validation-bland",
  "method_source": "David Bland, Testing Business Ideas (2019)",
  "solutions": [
    {
      "solution_id": "string",
      "title": "string",
      "validations": [
        {
          "assumption_id": "string",
          "assumption_text": "string (verbatim)",
          "category": "desirability | usability | feasibility | viability | other",
          "recommended_test": {
            "test_type": "string (e.g., 'Customer interview', 'Landing page with sign-up')",
            "hypothesis": "We believe that [assumption phrased as belief].",
            "test_description": "Concrete description of what to do, in 2-3 sentences.",
            "metric": "Specific data point to measure.",
            "success_criteria": "We are right if [threshold the metric must hit].",
            "estimated_cost": "low | medium | high",
            "estimated_time": "hours | days | weeks",
            "evidence_strength": "weak | moderate | strong",
            "rationale": "One-line explanation of why this test was chosen as the cheapest viable."
          },
          "alternative_tests": [
            {
              "test_type": "string",
              "rationale": "One-line explanation of when the trio might choose this instead."
            }
          ]
        }
      ]
    }
  ]
}
```

### Field notes

- **`recommended_test`** is the default action the trio can run with. It is the cheapest test the agent considers viable for the assumption.
- **`alternative_tests`** lists 1-2 alternatives with situational rationale (e.g., "if the trio has access to high-traffic existing surfaces, an A/B test gives stronger evidence at similar cost"). Not exhaustive. Helps the trio swap when context warrants.
- **`hypothesis`, `test_description`, `metric`, `success_criteria`** together form the Test Card. All four are required; without success_criteria the test is not falsifiable.
- **`estimated_cost`, `estimated_time`, `evidence_strength`** are coarse-grained on purpose. Three buckets each. Finer scales invite false precision.
- **`rationale`** in the recommended test exists so the trion can quickly see why this particular test was picked over alternatives, and audit the agent's reasoning.

## Markdown rendering format

For trion-facing display, the agent also produces markdown Test Cards, one per assumption. Format:

```markdown
### Assumption: <assumption text verbatim>

**Category:** <category>

**Recommended test: <test type>**

> **Hypothesis:** We believe that ...
> **Test:** To verify that, we will ...
> **Metric:** And measure ...
> **Success criteria:** We are right if ...

**Cost:** low / medium / high
**Time:** hours / days / weeks
**Evidence:** weak / moderate / strong

**Why this test:** <rationale>

**Alternatives:**

- <test type>: <rationale>
- <test type>: <rationale>
```

The markdown is what the trion reads. The JSON is what downstream tooling consumes. Both are produced from the same underlying extraction.

## Application notes

- **One Test Card per riskiest assumption.** Not per solution. A solution can have multiple riskiest assumptions, each gets its own card.
- **The agent does not run the test.** It designs it. Execution, result collection and interpretation are out of scope here.
- **The agent does not pick which assumption to test first.** All riskiest get cards. The trio picks execution order based on resources and dependencies.
- **Lean toward "ship the test today" cost levels.** If the recommended test is "run a landing page for two weeks", consider whether a five-customer interview round produces enough evidence in three days instead. Bland: "Run experiments at the speed and scale that match the risk you are addressing."

## Open evolutions

- Track test outcomes when experiments are run, so future iterations can learn what evidence held and what surprised. Out of scope for v0.1.
- Add cost-in-currency or time-in-hours estimates if trios consistently want sharper budget signals than three-bucket categories.
- Connect Test Cards to Bland's "Learning Card" template for capturing post-test insights.

## v0.2 extensions (2026-05-12)

The sections below extend v0.1 for the `OST-validation-experiment-designer` skill (workshop 3 assist 12, terminal assist in the critical path). The v0.1 Test Card structure, 12-test-type catalog, 5 selection principles, JSON schema v0.1, markdown rendering format, and application notes above are unchanged. v0.2 adds the runtime contract the skill reads at execution: a category-default test mapping, a success_criteria regex rule (numeric anchor required), full filtered identity-mapping over the upstream assist-11 output, the v0.2 JSON schema, and the renderer template with run-list HITL gate banner.

### Category-default test mapping (v0.2)

Explicit defaults per category. The skill applies these as the cheapest-viable test for each assumption, then permits LLM-driven override when the specific assumption text suggests a better fit.

| Category | Default cheapest-viable test |
|---|---|
| `desirability` | Customer interview |
| `usability` | Paper or click-through prototype |
| `feasibility` | Technical spike or proof-of-concept |
| `viability` | Landing page with sign-up |
| `other` | Customer interview (fallback) |

**Override rule:** the LLM may pick a different test if the specific assumption text suggests it better fits the cheapest-viable principle. The override must be named in `recommended_test.rationale` using one of these two verbatim formats:

- `Default for <category> is <default-test> (used as-is).` when no override.
- `Default for <category> is <default-test>, but <chosen-test> fits because <reason>.` when overriding.

Regex-checked at validation:

```text
^Default for (desirability|usability|feasibility|viability|other) is .+ \(used as-is\.\)$|^Default for (desirability|usability|feasibility|viability|other) is .+, but .+ fits because .+\.$
```

The rationale-format constraint makes the LLM commit to either accepting the default or naming a reason for departing. Vague "I picked this test" rationales are rejected.

### Success_criteria regex rule (v0.2)

Every `success_criteria` in a Test Card MUST include a numeric anchor. The composite regex (case-insensitive):

```text
\b\d+\b|\b\d+%\b|(within|under|over)\s+\d+\s+(seconds|minutes|hours|days|weeks)|\d+\s+(of|out of)\s+\d+
```

Four alternatives:

1. A bare number: `\b\d+\b` (e.g., "7 interviewees")
2. A percent: `\b\d+%\b` (e.g., "30%")
3. A bounded time-frame: `(within|under|over)\s+\d+\s+(seconds|minutes|hours|days|weeks)` (e.g., "within 5 days")
4. A count expression: `\d+\s+(of|out of)\s+\d+` (e.g., "7 out of 10")

Because alternative 1 (bare number) matches any digit, the effective rule reduces to: **success_criteria MUST contain at least one digit.** The longer alternatives are documented for prompt-side guidance.

**Acceptable examples:**

- "We are right if 7 out of 10 interviewees describe the manual step as their biggest friction."
- "We are right if 30% of sign-ups complete the licens-tilldelning flow without help."
- "We are right if the spike returns valid JSON within 200ms."

**Rejected examples** (no digit):

- "We are right if many customers like it."
- "We are right if it is broadly useful."
- "We are right if the team is happy."

### Carry-forward, filter, and identity-mapping invariants (v0.2)

The skill consumes assist-11 v0.2 output and filters it to `is_riskiest=true` only. For surviving (retained) assumptions, every upstream field carries through byte-identical; the skill adds exactly 2 new per-assumption fields (`recommended_test`, `alternative_tests`). Specifically:

- Top-level: `team`, `title`, `product_outcome`, `chosen_opportunity.*`, `source_assumptions_categorized`, `source_assumptions`, `source_top_three_solutions`, `source_experience_map`, `categorization_summary`, `risk_summary` carried verbatim. The skill adds `source_riskiest_assumptions` (basename of source file) and `validation_summary`.
- Per-solution: `pick_position`, `solution_id`, `solution_title`, `solution_description`, `generating_role`, `round_number` carried byte-identical.
- Per-assumption: `id`, `text`, `source_methods`, `category`, `importance`, `evidence`, `is_riskiest`, `rationale` carried byte-identical; `recommended_test` and `alternative_tests` added. Non-riskiest assumptions are dropped from the output.

**Identity-mapping invariants (hard-exit on violation):**

- `assumptions_per_solution.length == 3`.
- For each per-solution entry, output `assumptions.length` equals the count of `is_riskiest=true` entries in the upstream per-solution `assumptions[]`.
- Every retained output assumption has `is_riskiest == true` (filter invariant).
- For each retained assumption, every upstream field is byte-identical to the upstream.
- Order of retained assumptions within each per-solution entry mirrors upstream order (no re-sort).
- Every retained assumption has exactly 2 new top-level fields (`recommended_test`, `alternative_tests`).
- `alternative_tests.length == 2` for every retained assumption.
- `recommended_test` has all 9 sub-fields: `test_type`, `hypothesis`, `test_description`, `metric`, `success_criteria`, `estimated_cost`, `estimated_time`, `evidence_strength`, `rationale`.
- Every `success_criteria` matches the regex above.
- Every `recommended_test.rationale` matches the Default-or-override format regex.
- Every `estimated_cost` in `{low, medium, high}`; `estimated_time` in `{hours, days, weeks}`; `evidence_strength` in `{weak, moderate, strong}`.
- `validation_summary.total_test_cards == validation_summary.total_riskiest` and matches actual count of retained assumptions.

### JSON schema (v0.2)

```json
{
  "schema_version": "0.2",
  "method": "assumption-validation-bland",
  "method_source": "David Bland, Testing Business Ideas (2019)",
  "team": "string (carried byte-identical from upstream)",
  "title": "string (carried byte-identical)",
  "product_outcome": "string (carried byte-identical)",
  "chosen_opportunity": {
    "id": "string (carried byte-identical)",
    "phase_id": "string (carried byte-identical)",
    "quote": "string (carried byte-identical)",
    "source": "string (carried byte-identical)"
  },
  "source_riskiest_assumptions": "string (filename of source riskiest-assumptions-*.json)",
  "source_assumptions_categorized": "string (carried byte-identical)",
  "source_assumptions": "string (carried byte-identical)",
  "source_top_three_solutions": "string (carried byte-identical)",
  "source_experience_map": "string (carried byte-identical)",
  "categorization_summary": "object (carried byte-identical from upstream)",
  "risk_summary": "object (carried byte-identical from upstream)",
  "validation_summary": {
    "framework": "Bland Test Card with cheapest-viable selection (David Bland)",
    "selection_rule": "category-default with named override; alternative_tests fixed at 2",
    "success_criteria_rule": "regex-anchored numeric threshold required",
    "total_riskiest": "integer (from upstream risk_summary.total_riskiest)",
    "total_test_cards": "integer (count of Test Cards produced; equals total_riskiest)"
  },
  "assumptions_per_solution": [
    {
      "pick_position": 1,
      "solution_id": "string (carried byte-identical)",
      "solution_title": "string (carried byte-identical)",
      "solution_description": "string (carried byte-identical)",
      "generating_role": "product-manager | ux-designer | tech-lead (carried)",
      "round_number": "integer (carried byte-identical)",
      "assumptions": [
        {
          "id": "string (carried byte-identical)",
          "text": "string (carried byte-identical)",
          "source_methods": ["array carried byte-identical"],
          "category": "string (carried byte-identical)",
          "importance": "string (carried byte-identical; always 'high' for retained set)",
          "evidence": "string (carried byte-identical; always 'weak' for retained set)",
          "is_riskiest": "boolean (carried byte-identical; always true for retained set)",
          "rationale": "string (carried byte-identical)",
          "recommended_test": {
            "test_type": "string (from catalog, e.g., 'Customer interview', 'Technical spike or proof-of-concept', 'Landing page with sign-up')",
            "hypothesis": "string (We believe that <assumption phrased as belief>.)",
            "test_description": "string (To verify that, we will <2-3 sentence concrete description>.)",
            "metric": "string (And measure <specific data point>.)",
            "success_criteria": "string (We are right if <... numeric anchor>.)",
            "estimated_cost": "low | medium | high",
            "estimated_time": "hours | days | weeks",
            "evidence_strength": "weak | moderate | strong",
            "rationale": "string (Default-or-override format)"
          },
          "alternative_tests": [
            {
              "test_type": "string",
              "rationale": "string (when the trio might choose this instead, one short clause)"
            },
            {
              "test_type": "string",
              "rationale": "string"
            }
          ]
        }
      ]
    }
  ]
}
```

### Renderer template (v0.2)

The markdown is generated deterministically from the JSON via this template:

````markdown
---
title: "Validation experiments: <chosen_opportunity.id> - <first 5-10 words of quote>"
date: <YYYY-MM-DD>
purpose: Bland Test Cards for the riskiest assumptions surfaced in phase 4. Terminal run-list for the trio. Paired with validation-experiments-<date>.json.
tags: [assumption-validation, ost, bland, test-card, schema-v0.2]

---

# Validation experiments: <chosen_opportunity.id>

> **Trio run-list handoff.** This is the terminal artifact for the workshop-3 critical path. Read the Test Cards; pick execution order based on resource availability, dependencies, and team capacity; run the cheapest viable test first per Bland's principle. The skill does NOT pick sequence. Capture results separately (a future Learning-Card skill is parked). If a recommended test does not fit your context, swap to one of the 2 alternatives.

Source OST-riskiest-assumptions: `<source_riskiest_assumptions>`
Source assumptions-categorized: `<source_assumptions_categorized>`
Source top 3 solutions: `<source_top_three_solutions>`
Schema version: 0.2
Paired JSON: `validation-experiments-<YYYY-MM-DD>.json`

Framework: Bland Test Card with cheapest-viable selection. Category-default + named override. alternative_tests fixed at 2. success_criteria regex-anchored.

Total riskiest: <N>. Total Test Cards: <N>.

## Chosen opportunity

**<chosen.id>** (Phase: <phase_id>) - "<quote>" - *<source>*

## Product outcome

> <outcome formulation>

## Solution 1: <solution_title>

**<solution_id>** [<role-abbrev>, R<round_number>]

<solution_description>

**Test Cards in this solution (<count>):**

### <asm-id> [<methods-tag>] [<category>] [<importance>/<evidence>]

**Assumption:** <text>

**Upstream rationale:** <assumption.rationale carried verbatim from assist 11>

**Recommended test: <test_type>**

> **Hypothesis:** We believe that <...>.
> **Test:** To verify that, we will <...>.
> **Metric:** And measure <...>.
> **Success criteria:** We are right if <... numeric anchor>.

**Cost:** <low|medium|high> | **Time:** <hours|days|weeks> | **Evidence:** <weak|moderate|strong>

**Why this test:** <recommended_test.rationale>

**Alternatives:**

- **<alt1.test_type>:** <alt1.rationale>
- **<alt2.test_type>:** <alt2.rationale>

---

### <asm-id> [<methods-tag>] [<category>] [<importance>/<evidence>]

(same Test Card shape)

---

## Solution 2: <solution_title>

(same shape)

## Solution 3: <solution_title>

(same shape)
````

Rendering rules:

- Carried tags from upstream: method-tag (`SM`/`PrM`/`OI`), category (`[desirability]` etc.), score (`[high/weak]` etc.; always `[high/weak]` for retained set per filter), role-abbrev (`PM`/`UX`/`TL`).
- Per-Test-Card heading: `### <asm-id> [<methods>] [<category>] [<imp>/<ev>]`. Tag order fixed: methods -> category -> score. No separate `[RISKIEST]` marker (every Test Card IS for a riskiest assumption).
- Test Card prose: Bland 4-field block as `>` blockquote (Hypothesis / Test / Metric / Success criteria each on its own line, bold-prefixed).
- Cost/time/evidence triple on one line, separated by ` | `.
- "Why this test" line carries `recommended_test.rationale` verbatim.
- "Upstream rationale" line carries `assumption.rationale` (from assist 11) verbatim.
- Alternatives: 2 bullets, bold test_type + rationale.
- Horizontal rule `---` between Test Cards within a solution. No trailing `---` after the last Test Card before the next `##`.
- "Test Cards in this solution (count)" line between solution-description and first Test Card. If count is 0, render `**Test Cards in this solution (0):** _none - no riskiest assumptions to validate._` and skip the Test Card section.
- Run-list HITL banner at top of body (blockquote with `>` prefix). Verbatim text from template.
- Total summary line under framework paragraph.
- No em-dash anywhere. Frontmatter blank line before closing `---`. No `Cites:` line.
- Pick ordering in markdown mirrors upstream `picks[]` order.
- Row ordering within each solution preserves upstream order (among retained).
- Output language: Test Card prose follows upstream language (typically Swedish). Schema field names, test_type names, cost/time/evidence enums, category enum, role/method abbrev, JSON keys stay English.

## Evolution

| Version | Date | Change |
|---|---|---|
| v0.1 | 2026-05-06 | Initial Bland Test Card structure (4 fields), 12-test-type catalog with cost/time/evidence ratings, 5 selection principles, JSON schema v0.1 (`solutions[]` shape), markdown rendering format, application notes. |
| v0.2 | 2026-05-12 | Extended for the OST-validation-experiment-designer skill (assist 12, terminal in workshop-3 critical path): filtered identity-mapping over upstream assist-11 output (every retained upstream field byte-identical + 2 new per-assumption fields), category-default test mapping with named-override rule (regex-checked rationale format), success_criteria regex rule (numeric anchor required), schema v0.2 (full carry-forward shape using `assumptions_per_solution[]` and `id` field names), renderer template with run-list HITL gate banner. |
