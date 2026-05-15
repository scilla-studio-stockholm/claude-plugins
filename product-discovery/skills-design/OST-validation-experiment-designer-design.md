---
title: "OST-validation-experiment-designer: design spec"
date: 2026-05-12
purpose: Locked design for assist 12 in opportunity-solution-tree-agents.md - takes the scored per-solution assumption list from OST-riskiest-assumptions (assist 11), filters to is_riskiest=true, runs a single cross-solution LLM pass that designs a Bland Test Card per riskiest assumption using a hybrid category-default + named-override selection rule, and writes paired JSON + markdown with one Test Card per riskiest assumption plus 2 alternative tests. success_criteria regex-anchored to require numeric thresholds; identity-mapping over surviving (riskiest) upstream assumptions. Terminal assist in the workshop-3 critical path; markdown carries a run-list handoff banner. Input to the implementation plan.
tags: [skill-design, workshop-3, ost, OST-validation-experiment-designer, bland, test-card, schema-v0.2]

---

# OST-validation-experiment-designer: design spec

This is the locked design for **assist 12** in `opportunity-solution-tree-agents.md`. It is the twelfth and final skill in the workshop 3 critical path, and the only assist in **phase 5 (assumption validation experiments)**. Upstream is assist 11 (`OST-riskiest-assumptions`), which produces the scored per-solution assumption lists with the `is_riskiest` flag plus the full carry-forward chain. Downstream is the trio (and a hypothetical future Learning-Card capture skill, out of scope). This skill is terminal: it produces a run-list of Bland Test Cards that the trio reads, picks execution order, and runs. The markdown HITL banner is framed as a run-list handoff, not a review-and-approve gate. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when designing validation experiments for the riskiest assumptions surfaced in phase 4, output a paired JSON + markdown rendering with one Bland Test Card per riskiest assumption (hypothesis, test, metric, success criteria with required numeric anchor) plus 2 alternative tests. Terminal assist; trio reads, picks execution order, and runs.

Input is the latest `riskiest-assumptions-*.json` in `workspace/9-riskiest-assumptions/` by date in filename (assist 11's output). Output is two files in `workspace/10-validation-experiments/` with the same root name: a validation-experiments JSON conforming to schema v0.2 in the extended knowledge anchor `../knowledge/discovery/assumption-validation.md` (existing v0.1 bumped to v0.2), and a markdown rendering generated deterministically from the JSON.

The orchestration is a **single cross-solution LLM Test Card design pass**. One LLM call sees the filtered set of riskiest assumptions (typically 15-25 across the three solutions) plus the solution context, chosen opportunity, product outcome, the v0.1 anchor's test-type catalog and selection principles, and the v0.2 anchor's category-default mapping + success_criteria regex rule. The LLM returns one `{id, recommended_test, alternative_tests}` object per assumption. The skill then merges these 2 new fields into the filtered upstream structure.

The skill enforces strict **filtered identity-mapping**: every upstream field byte-identical for surviving (`is_riskiest=true`) assumptions; non-riskiest assumptions dropped; exactly 2 new per-assumption fields added; no other field touched.

## Scope decisions (locked 2026-05-12)

The six open questions in `opportunity-solution-tree-agents.md` section 12 are narrowed below, plus several mechanical decisions. Each decision resolves an open question.

| Question | Decision |
|---|---|
| Skill vs agent | **Single-pass skill, no sub-agents.** Mirrors assists 10 + 11 precedent. Per-card complexity is higher than scoring (4 Test Card fields + 2 alternatives + 4 meta-fields), but single-pass keeps "cheapest viable" calibration consistent across solutions. |
| Schema relationship to existing anchor | **Bump existing `assumption-validation.md` to v0.2.** The v0.1 schema (written 2026-05-06) uses `solutions[]` → `validations[]` shape with `assumption_id`/`assumption_text` field names. v0.2 extends it: full carry-forward of every upstream field byte-identical PLUS 2 new per-assumption fields (`recommended_test`, `alternative_tests`). Uses assist-11 field names (`assumptions_per_solution`, `id`, `text`) for chain consistency. Existing v0.1 content stays as reference; new sections appended; Evolution row added. Mirrors the v0.1→v0.2 pattern from assist 11. |
| Filtering | **Filter input to `is_riskiest=true` only.** Per Bland's "test the riskiest first" principle and the v0.1 anchor's application note ("One Test Card per riskiest assumption"). Non-riskiest assumptions are dropped from the output. The trio can run validation only on what's riskiest by design. Filter is applied at parse-time; the LLM never sees non-riskiest assumptions. |
| Cheapest-viable selection | **Hybrid: category-default + named override.** Start from a fixed default per category (`desirability → Customer interview`, `usability → Paper or click-through prototype`, `feasibility → Technical spike or proof-of-concept`, `viability → Landing page with sign-up`, `other → Customer interview` fallback). LLM overrides if the specific assumption text suggests a better cheapest-viable. Override must be named in `recommended_test.rationale` using the verbatim format `Default for <category> is <X>, but <Y> fits because <reason>.` (or `Default for <category> is <X> (used as-is).` when no override). Regex-checked. |
| `alternative_tests` count | **Fixed 2.** Predictable shape for downstream consumers; trio sees a consistent number of swap candidates per Test Card. Schema invariant `alternative_tests.length == 2`. Forces LLM to think about alternatives even when default is clearly right. |
| `success_criteria` precision | **Regex-checked numeric anchor.** Every `success_criteria` must include either a number (`\b\d+\b`), a percent (`\b\d+%\b`), a time-frame (`(within\|under\|over)\s+\d+\s+(seconds\|minutes\|hours\|days\|weeks)`), or a count expression (`\d+\s+(of\|out of)\s+\d+`). Case-insensitive. Hard-fail on regex miss. Verbatim acceptable/rejected examples in v0.2 anchor. Prevents the "many customers like it" failure mode. |
| Test sequencing | **Trio picks; skill silent.** Per anchor v0.1 application note: "The agent does not pick which assumption to test first." No `priority` or `sequence` field. Test Cards rendered in upstream order (preserved via identity-mapping). Trio orders by resource availability, dependencies, team capacity. Markdown HITL banner explicitly says this. |
| Customer-access flagging | **Trio catches at HITL.** No `requires_customer_access` field. Trio reads the test type and infers access needs themselves. Aligned with v0.1 anchor which doesn't flag this. Keeps schema lean. |
| Learning Card scaffold | **Defer to v0.3 (or future skill).** Learning Cards capture post-test insights; this skill stops at "designed the test". Execution + result capture is the trio's job, possibly with a future capture skill. v1 schema stays focused on test design. |
| HITL framing | **Run-list handoff (not review-and-approve gate).** This skill is terminal; no downstream skill consumes the output. Markdown banner says "Trio run-list handoff. Read the Test Cards; pick execution order; run cheapest viable first; capture results separately." No `ratifications.md` entry. No re-rendering on trio edits. |
| Input source pattern | **Latest-by-date.** Read latest `riskiest-assumptions-*.json` from `workspace/9-riskiest-assumptions/` by date in filename. No ratification gate (assist 11 uses markdown-banner-only HITL). |
| Output location | `workspace/10-validation-experiments/`. Final stage-numbered subdir, continuing `1-` through `9-`. |
| Output filename | `validation-experiments-<YYYY-MM-DD>.{json,md}` per cross-cutting datakontrakt. |
| Output format | Paired JSON + markdown. JSON is the structured contract (future tooling); markdown is the trio's run-list. |
| Slug name | `OST-validation-experiment-designer`. Verb-less compound noun; matches the spec section title ("Validation-experiment-designer agent"); consistent with `OST-riskiest-assumptions` and `OST-assumption-categorizer` precedent (also verb-less). |
| Body language | English, matching all skill-body precedent. Test Card prose (hypothesis, test, metric, success_criteria, rationales) inherits language from upstream assumption text (typically Swedish for this trio). |
| Tools | `Read`. No sub-agents, no Write tool beyond orchestrator output. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-validation-experiment-designer/SKILL.md` |
| Skill name | `OST-validation-experiment-designer` |
| Slash-command (optional) | `/OST-validation-experiment-designer` if frequency justifies |
| Body language | English |
| Tools | `Read` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when designing validation experiments for the riskiest assumptions surfaced in phase 4, output a paired JSON + markdown rendering with one Bland Test Card per riskiest assumption (hypothesis, test, metric, success criteria with required numeric anchor) plus 2 alternative tests. Terminal assist; trio reads, picks execution order, and runs.

Follows the "for X, when Y, output Z" pattern. Distinct from `OST-riskiest-assumptions` (scores; doesn't design tests) and from future Learning-Card-capture work (captures post-test results; out of scope).

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/9-riskiest-assumptions/OST-riskiest-assumptions-<latest-date>.json` | `OST-riskiest-assumptions` (assist 11) v0.2 | Per-solution scored assumptions with full carry-forward chain. Filtered to `is_riskiest=true` at parse-time. |

**File-resolution rule:** latest `riskiest-assumptions-*.json` in `workspace/9-riskiest-assumptions/` by date in filename, descending. Trio re-runs assist 12 against an edited JSON by re-saving the upstream JSON (the trio's HITL edits) and invoking; latest-by-date picks it up.

That is the only input. The skill does NOT read:

- `workspace/context/ratifications.md` — no ratification gate.
- `workspace/context/chosen-opportunity.md`, `product-outcome.md`, experience map — context flows through the identity-mapping chain.
- Interview transcripts, brainstorm outputs, comparison matrix, etc.
- Role anchors.

**Knowledge anchors read at runtime:**

- **`../knowledge/discovery/assumption-validation.md`** (EXISTING v0.1, bumped to v0.2 as part of this build) — owns the Test Card structure (v0.1), 12-test-type catalog (v0.1), 5 selection principles (v0.1), category-default mapping (NEW in v0.2), success_criteria regex rule (NEW in v0.2), carry-forward + filtered-identity-mapping invariants (NEW in v0.2), schema v0.2 (NEW), renderer template with run-list HITL banner (NEW in v0.2).
- **`../knowledge/discovery/assumption-risk-mapping.md`** (v0.2) — for input semantics (importance/evidence/is_riskiest definitions; schema v0.2 carry-forward shape).
- **`../knowledge/discovery/assumption-types.md`** — the 5-category taxonomy. Read for the category→default-test mapping in the new v0.2 anchor section.
- **`../knowledge/discovery/opportunity-solution-tree-teresa-torres.md`** — Torres "test the riskiest assumptions" framing (CDH ch 9).

## The knowledge anchor extension: `../knowledge/discovery/assumption-validation.md` → v0.2

The existing v0.1 anchor (committed 2026-05-06) stays intact. Five new sections appended; Evolution table updated.

**New sections to append (in order):**

1. **Category-default test mapping (v0.2)** — explicit defaults plus override rule + rationale convention.
2. **Success_criteria regex rule (v0.2)** — required numeric anchor; verbatim regex; acceptable/rejected examples.
3. **Carry-forward, filter, and identity-mapping invariants (v0.2)** — every upstream field byte-identical for surviving (riskiest) assumptions; non-riskiest dropped; 2 Test Card fields added per retained assumption.
4. **JSON schema (v0.2)** — below.
5. **Renderer template (v0.2)** — run-list HITL banner + per-Test-Card block format combining assist-10/11 per-solution shape with v0.1 Bland Test Card prose block.

Plus an Evolution row dated 2026-05-12.

**Category-default mapping (v0.2):**

| Category | Default cheapest-viable test |
|---|---|
| `desirability` | Customer interview |
| `usability` | Paper or click-through prototype |
| `feasibility` | Technical spike or proof-of-concept |
| `viability` | Landing page with sign-up |
| `other` | Customer interview (fallback) |

**Override rule:** LLM may pick a different test if the specific assumption text suggests it better fits the cheapest-viable principle. Override must be named in `recommended_test.rationale` using one of these two formats:

- `Default for <category> is <default-test> (used as-is).` — when no override.
- `Default for <category> is <default-test>, but <chosen-test> fits because <reason>.` — when overriding.

Regex-checked at validation: `^Default for (desirability|usability|feasibility|viability|other) is .+ \(used as-is\.\)$|^Default for (desirability|usability|feasibility|viability|other) is .+, but .+ fits because .+\.$`.

**success_criteria regex rule (v0.2):**

Every `success_criteria` must include at least one of:

- A bare number: `\b\d+\b` (e.g., "7 interviewees")
- A percent: `\b\d+%\b` (e.g., "30%")
- A bounded time-frame: `(within|under|over)\s+\d+\s+(seconds|minutes|hours|days|weeks)` (e.g., "within 200ms" — note that bare ms is not in the time-frame regex; use `under 1 second` or `\d+\s*ms` — for cross-language robustness, the regex accepts the longer forms only; "200ms" still passes via the bare-number check)
- A count expression: `\d+\s+(of|out of)\s+\d+` (e.g., "7 out of 10")

Composite regex (case-insensitive): `\b\d+\b|\b\d+%\b|(within|under|over)\s+\d+\s+(seconds|minutes|hours|days|weeks)|\d+\s+(of|out of)\s+\d+`. Because all but the third alternative reduce to "contains a digit", the effective rule is: success_criteria MUST contain at least one digit. The longer alternatives are documented for prompt-side guidance; the regex check is a single-digit floor.

**Acceptable examples:**

- "We are right if 7 out of 10 interviewees describe the manual step as their biggest friction."
- "We are right if 30% of sign-ups complete the licens-tilldelning flow without help."
- "We are right if the spike returns valid JSON within 200ms."

**Rejected examples** (no digit):

- "We are right if many customers like it."
- "We are right if it's broadly useful."
- "We are right if the team is happy."

**Filtered identity-mapping invariants (v0.2):**

- `assumptions_per_solution.length == 3`.
- For each per-solution entry, output `assumptions.length` equals the count of `is_riskiest=true` entries in the upstream per-solution `assumptions[]`.
- Every output assumption has `is_riskiest == true` (filter invariant).
- For each retained assumption, every upstream field (`id`, `text`, `source_methods`, `category`, `importance`, `evidence`, `is_riskiest`, `rationale`) is byte-identical to the upstream.
- Order of retained assumptions within each per-solution entry mirrors upstream order (no re-sort).
- Each retained assumption has exactly 2 new top-level fields: `recommended_test` and `alternative_tests`. No other field is added or modified.
- `alternative_tests.length == 2` for every retained assumption.
- `validation_summary.total_test_cards == validation_summary.total_riskiest` (one Test Card per retained assumption).

**JSON schema v0.2:**

```json
{
  "schema_version": "0.2",
  "method": "assumption-validation-bland",
  "method_source": "David Bland, Testing Business Ideas (2019)",
  "team": "string (carried byte-identical from upstream)",
  "title": "string (carried byte-identical)",
  "product_outcome": "string (carried byte-identical)",
  "chosen_opportunity": {
    "id": "string (carried)",
    "phase_id": "string (carried)",
    "quote": "string (carried)",
    "source": "string (carried)"
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

**Schema design notes:**

- `assumptions_per_solution[]` is fixed-length-3.
- Within each per-solution entry, `assumptions[]` is the filtered set (riskiest only). Length varies per solution: typically 0 to upstream-count.
- A solution with zero riskiest assumptions has `assumptions: []` (empty array, not missing). The renderer surfaces this as "Test Cards in this solution (0): _none — no riskiest assumptions to validate._"
- `recommended_test.test_type` SHOULD be from the v0.1 anchor's 12-test catalog. v1 permits free-form strings (per anchor's "consult Bland for additional types" clause) but surfaces a soft warning. Hard-exit is not triggered for outside-catalog test_type strings.
- `recommended_test.hypothesis`, `test_description`, `metric`, `success_criteria` together form the Bland Test Card. All four are required strings; `success_criteria` is regex-checked.
- `estimated_cost`, `estimated_time`, `evidence_strength` are coarse-grained (3 buckets each, per v0.1 anchor); finer scales invite false precision.
- `alternative_tests[]` is fixed-length-2; each entry has `test_type` and `rationale` strings only (no full Test Card body — alternatives are pointers, not full designs).

## Steps

The skill follows the same numbered-step pattern as `OST-riskiest-assumptions`. Single orchestrator pass; one LLM design call nested inside step 6.

1. **Read knowledge anchors:** `assumption-validation.md` (v0.2), `assumption-risk-mapping.md` (v0.2), `assumption-types.md`, `opportunity-solution-tree-teresa-torres.md`.

2. **Locate input:** latest `workspace/9-riskiest-assumptions/riskiest-assumptions-*.json` by date in filename, descending.

3. **Hard-exit checks** (see Error handling).

4. **Parse and filter.** Extract all top-level carried fields. Filter `assumptions_per_solution[].assumptions[]` to entries where `is_riskiest == true`. Build an index of retained assumptions keyed by `assumption.id`. Compute `total_riskiest` from the filter (sum across solutions). If `total_riskiest == 0`, hard-exit (see Error handling).

5. **Build the Test Card design input.** Flatten retained assumptions across the 3 solutions into a single ordered list. For each retained assumption, format one line as:

   ```text
   <solution_id> :: <id> :: [<category>] :: [<importance>/<evidence>] :: <text> :: <upstream-rationale>
   ```

   Including importance/evidence/upstream-rationale gives the LLM grounding for the Test Card framing (e.g., a weak-evidence usability assumption suggests a usability-default test).

6. **Run one LLM Test Card design pass.** Issue a single LLM call. The prompt contains, in order:

   - **Role frame:** "You design Bland Test Cards for product-discovery assumptions that the trio has flagged as riskiest. Apply the cheapest-viable principle. Each Test Card has 4 fields (hypothesis, test, metric, success_criteria) plus 2 alternative tests."

   - **Test Card structure** verbatim from anchor v0.1 (4-field table with Hypothesis / Test / Metric / Success criteria patterns).

   - **Selection principles** verbatim from anchor v0.1 (5 numbered: cheapest viable first; match test to assumption type; revealed preferences over stated; time-box the test; plan for both outcomes).

   - **Test type catalog** verbatim from anchor v0.1 (12-row table with `Best for / Cost / Time / Evidence` ratings).

   - **Category-default mapping** verbatim from anchor v0.2 (the 5-row table with defaults).

   - **Override rule + rationale format** verbatim from anchor v0.2:

     > For each assumption, start from the category default. If the specific assumption text suggests a better cheapest-viable, override and name the override in `recommended_test.rationale` using one of these verbatim formats: `Default for <category> is <default-test> (used as-is).` or `Default for <category> is <default-test>, but <chosen-test> fits because <reason>.`

   - **success_criteria regex rule** verbatim from anchor v0.2 with acceptable and rejected examples.

   - **Solution context block:** for each of the 3 solutions, `solution_id`, `title`, `description`, `generating_role`, `round_number`. Used to ground Test Card framing.

   - **Carried context:** chosen opportunity (id, phase, quote, source) and product outcome (verbatim). Used to ground Test Card outcomes.

   - **The full flat list of retained assumptions** (one per line, in the format from step 5).

   - **Task:** "For each assumption in the list, return a JSON object `{id, recommended_test, alternative_tests}`. `recommended_test` includes all 9 sub-fields (test_type, hypothesis, test_description, metric, success_criteria, estimated_cost, estimated_time, evidence_strength, rationale). `alternative_tests` is exactly 2 objects, each with `test_type` and `rationale`. Apply category-default + named override in `recommended_test.rationale` using the verbatim format. `success_criteria` MUST include a digit (numeric anchor). Test Card prose (hypothesis, test_description, metric, success_criteria) in the language of the assumption text (typically Swedish). Return only a JSON array, one per retained assumption, in the same order as the input. No other fields, no prose preamble."

   Collect the response. Parse as a JSON array. If parsing fails, hard-exit.

7. **Validate the design response.** Verify:

   - Length equals retained count.
   - Every entry has `id` (string), `recommended_test` (object), `alternative_tests` (array of length 2).
   - Every `recommended_test` has all 9 sub-fields with correct types.
   - Every `recommended_test.success_criteria` matches the success_criteria regex (case-insensitive).
   - Every `recommended_test.rationale` matches the Default-or-override regex.
   - Every `recommended_test.estimated_cost` in `{low, medium, high}`; `estimated_time` in `{hours, days, weeks}`; `evidence_strength` in `{weak, moderate, strong}`.
   - Every `recommended_test.test_type` is a non-empty string. Soft warning (not hard-exit) if outside the 12-test catalog from v0.1 anchor; the catalog is non-exhaustive.
   - Every `alternative_tests` entry has non-empty `test_type` and `rationale` strings.
   - The set of ids in the response equals the retained set (no missing, no unknown, no duplicates).

8. **Merge designs back into the filtered upstream structure.** Build a lookup map: `designs_by_id[id] = {recommended_test, alternative_tests}`. For each retained upstream assumption, build the output assumption object as a copy of the upstream object plus the two new fields. Every other field is carried byte-identical. Preserve upstream `assumptions[]` order within each per-solution entry.

9. **Compose the v0.2 JSON.** Top-level fields per schema. Carry every upstream top-level field byte-identical (including `categorization_summary` and `risk_summary` blocks). Add `source_riskiest_assumptions` (basename of source file). Add `validation_summary` (fixed v0.2 block + 2 integer counts). `assumptions_per_solution[]` ordered by upstream `pick_position` (1, 2, 3). Within each per-solution entry, `assumptions[]` contains only retained (riskiest) entries in upstream order.

10. **Validate invariants** per the full list above.

11. **Render the markdown deterministically** from the JSON via the embedded template.

12. **Write paired output** to:
    - `workspace/10-validation-experiments/validation-experiments-<YYYY-MM-DD>.json`
    - `workspace/10-validation-experiments/validation-experiments-<YYYY-MM-DD>.md`

    Create `workspace/10-validation-experiments/` if absent. Same root name on both files. The skill does NOT modify any input files.

One pass through one LLM design call plus deterministic filter + merge. No retries beyond what a single Agent call inherently does; any invariant violation hard-exits.

## Output composition

Two files with the same root name:

```text
workspace/10-validation-experiments/validation-experiments-<YYYY-MM-DD>.json
workspace/10-validation-experiments/validation-experiments-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.2.

**The markdown** combines the assist-10/11 per-solution shape with the elaborate Bland Test Card block (from v0.1 anchor) per assumption:

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

**Upstream rationale:** <importance/evidence rationale carried verbatim from assist 11>

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

**Rendering rules:**

- **Carried tags from upstream:** method-tag (`SM`/`PrM`/`OI`), category (`[desirability]` etc.), score (`[high/weak]` etc., always `[high/weak]` for retained set since filter requires `is_riskiest=true`), role-abbrev (`PM`/`UX`/`TL`).
- **Per-Test-Card heading:** `### <asm-id> [<methods>] [<category>] [<imp>/<ev>]`. Tag order fixed: methods → category → score. No separate `[RISKIEST]` marker — every Test Card IS for a riskiest assumption.
- **Test Card prose:** the Bland 4-field block rendered as a `>` blockquote (Hypothesis / Test / Metric / Success criteria each on its own line, bold-prefixed). Cost/time/evidence triple rendered on one line for compact scanning, separated by ` | `. "Why this test" line carries `recommended_test.rationale` verbatim. "Upstream rationale" line carries `assumption.rationale` (from assist 11) verbatim.
- **Alternatives:** 2 bullets, bold test_type + rationale.
- **Horizontal rule (`---`)** between Test Cards within a solution for visual separation. No trailing `---` after the last Test Card in a solution before the next `##`.
- **"Test Cards in this solution (count)" line** between solution-description and the first Test Card. If count is 0, render `**Test Cards in this solution (0):** _none — no riskiest assumptions to validate._` and skip the Test Card section for that solution.
- **Run-list HITL banner** at top of body (blockquote with `>` prefix). Verbatim text from the template.
- **Total summary line** under framework paragraph.
- **No em-dash anywhere.** Frontmatter blank line before closing `---`. No `Cites:` line.
- **Pick ordering** in the markdown mirrors upstream `picks[]` order.
- **Row ordering within each solution** preserves upstream `assumptions[]` order (among retained).
- **Output language for Test Card prose:** assumption text and Test Card fields (hypothesis, test, metric, success_criteria, rationales) follow upstream language (typically Swedish). Schema field names, test_type names, cost/time/evidence enums, category enum, role/method abbrev, JSON keys stay English.

## Knowledge-doc updates required before ship

As part of building this skill:

- **Bump `../knowledge/discovery/assumption-validation.md` to v0.2.** Append 5 new sections (category-default mapping, success_criteria regex rule, carry-forward + filter + identity-mapping invariants, schema v0.2, renderer template). Append Evolution row dated 2026-05-12 ("Extended for OST-validation-experiment-designer skill: filtered identity-mapping over upstream assist-11 output, category-default + named-override selection rule, regex-anchored success_criteria, schema v0.2 with full carry-forward + 2 new per-assumption fields, renderer template with run-list HITL banner."). Update frontmatter date to 2026-05-12. v0.1 content stays intact.
- **Update `skills-design/skill-template.md` Bygg-status** — mark `OST-validation-experiment-designer` as built. Update the tail count from `en` to `0` or remove the "Övriga … återstår" line entirely (workshop-3 critical path complete). Final task in the implementation plan.
- **Update `skills-design/opportunity-solution-tree-agents.md`** — replace section 12's six open design questions with a reference to the locked design at `skills-design/OST-validation-experiment-designer-design.md`. Update "Föreslagen typ" from "Agent" to "Skill (single-pass Test Card design against locked category-default mapping)" to match the actual decision.

What is NOT updated:

- `../knowledge/discovery/assumption-types.md` — read for category mapping; no changes.
- `../knowledge/discovery/assumption-risk-mapping.md` — read for upstream schema; no changes.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` — referenced but not extended.
- `workspace/context/ratifications.md` — intentionally NOT appended. Terminal assist; no ratification mechanism.

## Error handling

**Hard-exit triggers** (no output files written when these fire):

| Trigger | Looked for | Remedy |
|---|---|---|
| No `riskiest-assumptions-*.json` in `workspace/9-riskiest-assumptions/` | At least one file | Run `OST-riskiest-assumptions` (assist 11) first |
| Source JSON does not parse | Valid JSON conforming to v0.2 | Re-run assist 11 |
| Source JSON `schema_version` is not `"0.2"` | The exact string `"0.2"` | Re-run assist 11 against v0.2 |
| Source `assumptions_per_solution.length != 3` | 3 entries | Re-run assist 11 |
| **Zero `is_riskiest=true` assumptions across all solutions** | `total_riskiest > 0` | Surface message: "No riskiest assumptions to validate. Either re-run assist 11 with stricter scoring, or accept that this opportunity has no leap-of-faith assumptions to test." Hard-exit (no Test Cards to design). |
| Any knowledge anchor missing | All four files at fixed paths | Restore from git |
| Design LLM pass returned malformed JSON | A JSON array of `{id, recommended_test, alternative_tests}` objects | Re-run; if persistent, tighten prompt |
| Design omits a retained `assumption.id` | Every retained id in the response | Re-run |
| Design contains an `id` not in the retained set | Every response id is in the retained set | Re-run |
| Design contains a duplicate `id` | No duplicates | Re-run |
| Any `recommended_test` missing a sub-field | All 9 sub-fields present per Test Card | Re-run |
| Any `alternative_tests.length != 2` | Exactly 2 alternatives | Re-run |
| `success_criteria` fails regex | Numeric anchor present | Re-run; if persistent, tighten the success_criteria-rule instruction in prompt |
| `recommended_test.rationale` fails format regex | Default-or-override format | Re-run; if persistent, tighten the rationale-format instruction |
| Any enum violation (cost/time/evidence_strength) | Enum membership | Re-run |
| Identity-mapping violation (any upstream field changed for retained assumption) | All upstream fields byte-identical | Re-run; merge logic has drifted |
| Non-riskiest assumption appears in output | Filter applied correctly | Re-run; filter logic has drifted |
| `validation_summary.total_test_cards != total_riskiest` | Counts match | Re-run |
| Final-JSON invariant violation | Schema invariants | Re-run |

**Hard-exit message format** (same shape as upstream skills):

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

No silent degradation. No retries beyond the implicit retry inside any single Agent tool call.

**Soft warnings (not hard-exit):** `test_type` outside the v0.1 12-test catalog. The catalog is explicitly non-exhaustive ("consult Bland for additional types"); the skill accepts free-form test_type strings but logs a one-line note in the output (rendered as a brief callout in markdown, or in console output). v1 soft-warns; v0.3 could promote to enforced if trios report drift.

**Convention for missing optional fields:** v0.2 has no optional fields. `null` is never written.

**No JSON self-validation pass.** Trust the prompt and the invariant check; trio is the consumer of any malformed output.

## What this skill does NOT do

- **Read interview transcripts, brainstorm outputs, comparison matrix, validated opportunities, OST-cluster-solutions, top-three-solutions, the assumptions JSON, the categorized JSON, or the experience map directly.** Only the upstream `riskiest-assumptions-*.json` contract.
- **Read `chosen-opportunity.md`, `product-outcome.md`, or `ratifications.md`.** Context flows through the upstream JSON.
- **Append to `ratifications.md`.** Terminal assist; no ratification mechanism.
- **Read role anchors.** Role info is data only.
- **Include non-riskiest assumptions in output.** Filter is mandatory (per Bland's "test the riskiest first" principle).
- **Re-order assumptions.** Order preserved from upstream within the retained set.
- **Score or re-flag riskiness.** `is_riskiest` is carried byte-identical; the skill does not re-derive.
- **Modify upstream files.** `riskiest-assumptions-*.json` and all context files stay immutable.
- **Write to `workspace/context/`.** Output lives in `workspace/10-validation-experiments/`.
- **Add an in-skill ratification mechanism.** Terminal assist; no downstream consumer.
- **Pick execution sequence.** Trio picks based on resource availability and dependencies.
- **Flag customer-access requirements as a structured field.** Trio infers from test_type at HITL.
- **Include a Learning Card scaffold.** Deferred to v0.3 / future skill.
- **Run experiments.** Designs only; execution is the trio's job.
- **Provide more than 2 alternative tests.** Fixed at 2.
- **Provide finer-grained cost/time/evidence ratings than 3 buckets each.** False-precision avoidance.
- **Run a JSON self-validation pass beyond invariant checks.**
- **Retry the design pass on partial failures.** Hard-exit; operator re-runs.
- **Use a `priority`, `sequence`, `requires_customer_access`, `learning_card`, or `confidence` schema field.** All deferred to v0.3.
- **Spawn sub-agents.** Single-pass design is the architecture.
- **Default to vague success_criteria.** Regex requires numeric anchor; hard-exit on miss.
- **Default to a non-catalog test_type.** Catalog is preferred (soft warning if outside).
- **Re-render markdown when trio edits JSON.** v1 generates markdown once at skill run; trio edits are not reflected.
- **Write to Miro or any external surface.** JSON + markdown only.

## Testing

Smoke test only for v1. Reuses the Norrsken assist-11 output (23 riskiest of 31 assumptions across 3 solutions).

```text
Input:
  workspace/9-riskiest-assumptions/riskiest-assumptions-2026-05-12.json
    (23 riskiest assumptions: 9 / 7 / 7 per solution)

Expect:
  - schema_version "0.2", method, method_source exact
  - assumptions_per_solution.length == 3
  - Per-solution assumptions[] filtered to riskiest-only: 9 / 7 / 7 retained
  - Every retained assumption has is_riskiest=true, byte-identical upstream fields
    (id, text, source_methods, category, importance=high, evidence=weak,
     is_riskiest=true, rationale)
  - Every retained assumption has recommended_test (9 sub-fields) +
    alternative_tests (length=2)
  - Every success_criteria contains at least one digit (numeric anchor regex)
  - Every recommended_test.rationale matches the Default-or-override format
  - Every estimated_cost in {low, medium, high}; estimated_time in {hours, days,
    weeks}; evidence_strength in {weak, moderate, strong}
  - validation_summary.total_test_cards == validation_summary.total_riskiest == 23
  - chosen_opportunity, all source_* fields, categorization_summary, risk_summary
    carried byte-identical from upstream
  - source_riskiest_assumptions == "riskiest-assumptions-2026-05-12.json"
  - Markdown frontmatter with date 2026-05-12, blank line before closing ---
  - Trio run-list handoff banner present at top of body
  - "Total Test Cards: 23" line present
  - Three "## Solution N: <title>" sections
  - Each solution has "**Test Cards in this solution (<count>):**" line
  - 23 Test Card blocks (### headings with [methods] [category] [imp/ev] tags)
  - Each Test Card has Bland 4-field blockquote (Hypothesis / Test / Metric /
    Success criteria)
  - Each Test Card has Cost / Time / Evidence triple line
  - Each Test Card has "Why this test" + "Upstream rationale" lines
  - Each Test Card has 2 alternative bullets
  - --- horizontal rule between Test Cards within each solution
  - No em-dash, no Cites: line

Eyeball checks:
  - Category-default consistently applied: feasibility assumptions default to
    Technical spike, desirability to Customer interview, etc. Overrides have a
    clear "because" naming the assumption-specific reason
  - success_criteria all have a concrete number, percent, time-frame, or count
  - Cost ratings lean low (cheapest-viable principle): majority should be "low";
    "high" should be rare and justified in rationale
  - Alternative tests are genuinely different from the recommended (not just
    cosmetic variants)
  - Test prose grounded in the specific assumption text and solution context,
    not generic boilerplate
  - hypothesis prefixed with "We believe that"; test with "To verify that,
    we will"; metric with "And measure"; success_criteria with "We are right if"
  - Output language matches upstream (Swedish assumption text → Swedish
    hypothesis/test/metric/success_criteria/rationales)
```

What the smoke test does NOT exercise (parked as open follow-ups):

- Edge case: zero riskiest in some solutions (one solution with `assumptions: []`)
- Edge case: zero riskiest across all solutions (hard-exit fires)
- Configurable category-default mapping (per-team overrides)
- Test-type outside the 12-catalog (soft warning surfaces)
- Trio re-runs after editing the upstream JSON
- Learning Card integration

These gaps are accepted for v1.

## Open follow-ups

These are added to `TODO.md` rather than blocking v1.

1. **Learning Card scaffold.** Add `learning_card` object per Test Card (status, result, learning, action) for post-execution capture. Deferred from v1.
2. **Customer-access flagging.** Add `requires_customer_access` boolean per test object. Trio currently catches at HITL.
3. **Test sequencing.** Add `recommended_sequence` integer per Test Card. v1 keeps trio in charge of order.
4. **Configurable category-default mapping.** Per-team overrides of the desirability → Customer interview etc. defaults. Re-open if a trio's domain consistently warrants different defaults.
5. **Configurable `alternative_tests` count.** v1 locks 2. Surface 1-3 range if trios report needs.
6. **Sharper cost estimates.** Cost-in-currency or time-in-hours fields. Anchor's existing open evolution. v1 keeps three-bucket categories.
7. **Test-type catalog expansion.** v0.1 12-row list is a subset of Bland's 44. Re-open if trios consistently fall back to free-form test_types.
8. **Outcome-tracking integration.** Anchor's existing open evolution. Track results when experiments run.
9. **Cheapest-viable distribution sanity check.** Soft-warn if all retained Test Cards default to the same test type (signals miscalibration or unusual domain). v1 is eyeball-only.
10. **Schema evolution beyond v0.2.** Procedure same as upstream skills: add Evolution entry and bump `schema_version`.

## What this skill establishes for the workshop-3 series

- **Filtered identity-mapping precedent.** First skill that filters upstream input (`is_riskiest=true` only) while preserving byte-identical carry-forward for the surviving subset. Pattern transfers to any future skill that consumes a flagged subset (e.g., "design tests only for the top-priority opportunities").
- **Terminal-assist HITL framing.** First skill with a run-list handoff banner instead of a review-and-approve gate. Pattern transfers to any future skill that produces a final deliverable for the trio rather than feeding a downstream skill.
- **Regex-anchored content rule.** First skill that enforces a content-level regex (numeric anchor in `success_criteria`) beyond simple format checks. Pattern transfers to any future skill where a free-form field has substantive correctness constraints.
- **Category-default with named-override rule.** First skill that uses a mechanical default + LLM-override pattern with a regex-checked rationale format documenting the override. Pattern transfers to any future skill that picks from a catalog with a category-grounded baseline.
- **Multi-anchor v0.1 → v0.2 extension.** Second skill (after assist 11) to bump an existing v0.1 anchor to v0.2 rather than create a new anchor. Pattern is now established as the default for re-using existing schema artifacts.
- **Workshop-3 critical path completion.** Twelfth and final assist. After this build, the workshop-3 series shrinks to 0 remaining critical-path assists; future work moves to scilla-broader productization, per-team smoke tests against live trios, and post-test capture (Learning Card etc.).
