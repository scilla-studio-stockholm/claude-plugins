---
title: "OST-riskiest-assumptions: design spec"
date: 2026-05-12
purpose: Locked design for assist 11 in opportunity-solution-tree-agents.md - takes the categorized per-solution assumption list from OST-assumption-categorizer (assist 10), runs a single cross-solution LLM pass that scores each assumption on Bland's 2x2 (importance: high/low; evidence: strong/weak), computes is_riskiest deterministically as (importance=high AND evidence=weak), and writes paired JSON + markdown with the riskiest flagged inline and per-solution. Identity-mapping over upstream assist-10 output (no reorder, no add, no drop, no re-wording). This skill is the phase-3 trio HITL gate; markdown carries a review-and-approve banner. Input to assist 12 (OST-validation-experiment-designer) via latest-by-date. Input to the implementation plan.
tags: [skill-design, workshop-3, ost, OST-riskiest-assumptions, bland, schema-v0.2]

---

# OST-riskiest-assumptions: design spec

This is the locked design for **assist 11** in `opportunity-solution-tree-agents.md`. It is the eleventh skill built in the workshop 3 series and the only assist in **phase 4 (assumption risk mapping)**. Upstream is assist 10 (`OST-assumption-categorizer`), which produces the categorized per-solution assumption lists with full carry-forward chain. Downstream is assist 12 (`OST-validation-experiment-designer`), which reads the riskiest-flagged assumptions and designs Test Cards. This skill is the phase-3 trio HITL gate: the trio reads and approves (or edits the JSON before approving) the importance/evidence scoring here, then assist 12 picks the latest version by date. The implementation plan derives from this document.

## What the skill does

For product trios and researchers, when identifying the riskiest assumptions among the categorized assumptions for the top 3 solutions, output a paired JSON + markdown rendering with each assumption scored on importance (high/low) and evidence (strong/weak), and flagged as riskiest when importance=high AND evidence=weak. Phase-3 trio review gate; input to assist 12 (OST-validation-experiment-designer).

Input is the latest `assumptions-categorized-*.json` in `workspace/8-assumptions-categorized/` by date in filename (assist 10's output). Output is two files in `workspace/9-riskiest-assumptions/` with the same root name: a OST-riskiest-assumptions JSON conforming to schema v0.2 in the **extended** knowledge anchor `../knowledge/discovery/assumption-risk-mapping.md` (existing v0.1 bumped to v0.2), and a markdown rendering generated deterministically from the JSON.

The orchestration is a **single cross-solution LLM scoring pass**. One LLM call sees all ~30-42 assumptions across the three solutions (each tagged with its solution_id, id, category, and text) plus the solution context, the chosen opportunity, and the product outcome. The LLM returns one `{id, importance, evidence, rationale}` object per assumption. The skill then computes `is_riskiest` deterministically and merges the four new fields into the upstream structure. The skill enforces strict **identity-mapping** over the upstream assumptions: every upstream field carries through byte-identical; the skill adds exactly four new per-assumption fields and nothing else.

This skill IS the phase-3 trio HITL gate. The markdown output opens with a `Trio HITL gate.` banner directing the trio to review the importance/evidence calls and edit the paired JSON if they disagree. Assist 12 picks up the latest version by date. There is no `ratifications.md` mechanism for this gate (locked decision; lighter operational overhead than the OST-select-top-three-solutions v2 precedent).

## Scope decisions (locked 2026-05-12)

The four open questions in `opportunity-solution-tree-agents.md` section 11 are narrowed below, plus several mechanical decisions. Each decision below resolves an open question.

| Question | Decision |
|---|---|
| Skill vs agent | **Single-pass skill, no sub-agents.** Single SKILL.md prompt at `.claude/skills/OST-riskiest-assumptions/SKILL.md`. Body instructs Claude to run one LLM scoring pass over the full flat list. Mirrors the precedent set by `OST-assumption-categorizer` (v1). The brainstorm-input doc listed "agent" as the suggested type for cleaner packaging; in practice the workshop-3 series has converged on skills, and a 2x2 scoring against a locked framework is a bounded transformation. |
| Schema relationship to existing anchor | **Bump existing `assumption-risk-mapping.md` to v0.2.** The v0.1 schema in the anchor (written 2026-05-06) predates the identity-mapping pattern established by assist 10. v0.2 extends it: full carry-forward of every upstream field byte-identical PLUS four new per-assumption fields. Uses assist-10's field names (`assumptions_per_solution`, `id`) rather than v0.1's (`solutions`, `assumption_id`) for consistency through the chain. The existing v0.1 content stays in the anchor as historical reference; new sections are appended; Evolution entry added. |
| Evidence rule (strict vs soft) | **Soft.** LLM may reason about plausibility, including domain norms, industry conventions, and general engineering practice. Mark `strong` if the assumption seems well-grounded; `weak` if genuinely speculative. Wider net of `strong` calls than strict; trio overrides at review by editing the JSON. Trade-off: lower auditability than strict, but more useful default for trios who do not want to research every assumption to mark it `strong`. |
| Rationale format | **Single sentence, importance-then-evidence, structurally parseable.** Format: `Importance=<level> (<reason>); evidence=<level> (<reason>).` Regex-checked at validation. Each rationale covers both axes in one sentence; the structure makes downstream parsing trivial and gives trio a fixed scan pattern at review. |
| Per-solution vs single cross-solution pass | **Single cross-solution pass.** One LLM call sees all assumptions and scores them in one context. Best calibration of `strong`/`weak` across solutions; lowest latency and cost. Matches the assist-10 precedent (same orchestration pattern for the categorizer). |
| Rationale-rendering in markdown | **Nested sub-bullet under each assumption row.** Verbatim from JSON; never edited at render. Gives the trio a one-glance "here's why I scored this way" without bloating the row itself. |
| `is_riskiest` derivation | **Computed deterministically by the skill.** The LLM returns importance + evidence + rationale; the skill computes `is_riskiest = (importance == "high" AND evidence == "weak")`. Prevents LLM drift on the riskiest definition; guarantees the schema-invariant holds. |
| HITL gate mechanism | **Markdown banner only; latest-by-date for assist 12.** Markdown opens with a `Trio HITL gate.` banner stating that the trio should review the importance/evidence calls and edit the paired JSON if they disagree. No `ratifications.md` log entry required. Lighter than the OST-select-top-three-solutions v2 ratification pattern; relies on the trio not running the skill again without first reviewing the latest. Assist 12 picks up the latest `riskiest-assumptions-*.json` by date. |
| Riskiest visual marker in markdown | **Inline `[RISKIEST]` tag + per-solution `Riskiest:` summary line.** Each assumption row carries `[<importance>/<evidence>]`; when `is_riskiest=true`, an additional `**[RISKIEST]**` (bold, all-caps) tag follows the score tag. Each solution section opens with a `**Riskiest:**` line listing flagged ids (or `(none)`). Trio sees riskiest twice for redundancy. |
| Row ordering | **Preserve upstream order.** Identity-mapping continues from assist 10. No re-sort by importance, evidence, or risk. Riskiest are surfaced via marker + summary line, not via re-ordering. |
| Input source pattern | **Latest-by-date.** Read latest `assumptions-categorized-*.json` from `workspace/8-assumptions-categorized/` by date in filename. No ratification gate between assists 10 and 11 (assist 10 has no in-skill HITL). |
| Output location | `workspace/9-riskiest-assumptions/`. Stage-numbered convention continuing the `1-` through `8-` subdirs. |
| Output filename | `OST-riskiest-assumptions-<YYYY-MM-DD>.{json,md}` per cross-cutting datakontrakt. |
| Output format | Paired JSON + markdown (cross-cutting decision applies; the v0.1 anchor only specified JSON, but the brainstorm-input cross-cutting locked-decision now adds markdown for trio readability). |
| Slug name | `OST-riskiest-assumptions`. Verb-less noun; matches the existing `assumption-risk-mapping.md` anchor's framing; consistent with the `OST-assumption-categorizer` precedent (also verb-less). |
| Body language | English, matching all skill-body precedent. Inputs (the Swedish scoring questions from the anchor) and output prose (Swedish assumption text and rationale) may be Swedish; the skill body and the new anchor sections are English. The two scoring questions are quoted verbatim in Swedish in the prompt to preserve the workshop wall's exact wording. |
| Tools | `Read`. No sub-agents, no Write tool needed beyond the orchestrator's normal output-file writes. |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-riskiest-assumptions/SKILL.md` |
| Skill name | `OST-riskiest-assumptions` |
| Slash-command (optional) | `/OST-riskiest-assumptions` if frequency justifies it |
| Body language | English |
| Tools | `Read` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when identifying the riskiest assumptions among the categorized assumptions for the top 3 solutions, output a paired JSON + markdown rendering with each assumption scored on importance (high/low) and evidence (strong/weak), and flagged as riskiest when importance=high AND evidence=weak. Phase-3 trio review gate; input to assist 12 (OST-validation-experiment-designer).

This follows the "for X, when Y, output Z" pattern. Generic and company-agnostic. Distinct from `OST-assumption-categorizer` (which categorizes into Cagan-five but does not score) and from `OST-validation-experiment-designer` (which designs Test Cards for already-flagged riskiest).

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/8-assumptions-categorized/assumptions-categorized-<latest-date>.json` | `OST-assumption-categorizer` (assist 10) v0.1 | Per-solution categorized assumptions with full carry-forward chain back to source_methods, source_assumptions, chosen_opportunity, product_outcome, etc. |

**File-resolution rule:** latest `assumptions-categorized-*.json` in `workspace/8-assumptions-categorized/` by date in filename, descending. If a trio wants to score an older version, they pass the filename explicitly at invocation time (v0.3 follow-up; v1 reads latest only).

That is the only input. The skill does NOT read:

- `workspace/context/ratifications.md` - no upstream ratification gate for phase 3.
- `workspace/context/chosen-opportunity.md`, `product-outcome.md`, or the experience map - all identifying context flows through the upstream JSON via the identity-mapping chain assist 10 preserved.
- Interview transcripts, OST-brainstorm-solutions output, top-three-solutions JSON, comparison matrix, or any OST-cluster-solutions output.
- Role anchors. Role information carries as the role abbreviation only.

**Knowledge anchors read at runtime:**

- **`../knowledge/discovery/assumption-risk-mapping.md`** (EXISTING, bumped to v0.2 as part of this build) - owns the 2x2 framework, the two scoring questions, the binary axes semantics, the soft-evidence rule (NEW in v0.2), the rationale format rule (NEW in v0.2), the identity-mapping + 4-new-fields contract (NEW in v0.2), the carry-forward rules (NEW in v0.2), the schema v0.2 (NEW), and the renderer template with HITL banner (NEW in v0.2).
- **`../knowledge/discovery/assumption-types.md`** - the 5-category taxonomy. Read for reference only; categorization is upstream from assist 10 and carries through unchanged.
- **`../knowledge/discovery/opportunity-solution-tree-teresa-torres.md`** - the "test the riskiest assumptions" framing (Torres CDH ch 9).
- **`../knowledge/discovery/assumption-categorization.md`** - the upstream schema v0.1 so the skill can parse the input cleanly.

Per the cross-cutting datakontrakt, anchors are read at runtime rather than hard-coded into the prompt.

## The knowledge anchor extension: `../knowledge/discovery/assumption-risk-mapping.md` → v0.2

The existing v0.1 anchor (committed 2026-05-06) stays intact as historical reference. Five new sections are appended; an Evolution entry is added. No v0.1 content is rewritten.

**New sections to append (in order):**

1. **Soft-evidence rule (v0.2).** Verbatim prompt-instruction text the LLM uses: evidence includes empirical observation from inputs AND domain norms, industry conventions, and general engineering practice. Mark `strong` if the assumption seems well-grounded; `weak` if genuinely speculative. Replaces the v0.1 "internal opinion does not count as evidence" guidance with a softer standard for the AI scoring; trio still overrides at HITL.
2. **Rationale format rule (v0.2).** Single sentence, importance-then-evidence, format: `Importance=<level> (<reason>); evidence=<level> (<reason>).` Regex-checked.
3. **Carry-forward rules and identity-mapping invariants (v0.2).** Every upstream field from assist 10's v0.1 output carries through byte-identical. The skill adds exactly four per-assumption fields: `importance`, `evidence`, `is_riskiest`, `rationale`. Length-equality per solution; id-order at each index; byte-identical text/source_methods/category/all carried fields. Hard-exit on violation, no partial writes.
4. **JSON schema (v0.2).** Below.
5. **Renderer template (v0.2).** The deterministic markdown template with HITL banner.

**Schema v0.2:**

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

**Schema design notes:**

- `assumptions_per_solution[]` is fixed-length-3, in the same order as upstream `pick_position` (1, 2, 3).
- Every upstream field carries through byte-identical. The skill adds exactly 4 fields per assumption.
- `importance` and `evidence` are binary, each one value from the fixed enum. Never null. Never an array.
- `is_riskiest` is **computed by the skill**, not returned by the LLM. The LLM returns importance + evidence + rationale; the skill computes `is_riskiest` from importance + evidence. Prevents LLM drift on the definition.
- `rationale` is one sentence in the structured format. The format is regex-checked at validation.
- `risk_summary` is a fixed-shape sanity block with two integer counts; v0.2 string fields are locked.
- `categorization_summary` is carried byte-identical from upstream; it stays untouched.

**Schema invariants** (skill enforces; hard-exit on violation, no partial writes):

- `schema_version == "0.2"`.
- `method == "assumption-risk-mapping"` (locked).
- `method_source` matches the v0.1 string verbatim.
- `assumptions_per_solution.length == 3`.
- For each per-solution entry, `assumptions.length` equals the corresponding upstream per-solution entry's `assumptions.length`.
- For each per-solution entry, the upstream `assumptions[]` ids appear in the output in the same order at each index.
- Every `importance` in `{high, low}`; every `evidence` in `{strong, weak}`.
- `is_riskiest == true` iff `importance == "high" AND evidence == "weak"` (computed, not LLM-decided).
- Every `rationale` matches the regex `^Importance=(high|low) \(.+\); evidence=(strong|weak) \(.+\)\.$`.
- Every upstream field is byte-identical to the source JSON (top-level, per-solution, per-assumption).
- `risk_summary.total_assumptions` equals the sum of `assumptions[].length` across the three solutions.
- `risk_summary.total_riskiest` equals the count of assumptions where `is_riskiest=true`.
- `risk_summary.framework`, `evidence_rule`, `rationale_format` match the fixed v0.2 strings.

## Steps

The skill follows the same numbered-step pattern as `OST-assumption-categorizer`. Single orchestrator pass; one LLM scoring call nested inside step 6.

1. **Read knowledge anchors:** `assumption-risk-mapping.md` (v0.2), `assumption-types.md` (reference only), `opportunity-solution-tree-teresa-torres.md`, `assumption-categorization.md`.

2. **Locate input:** latest `workspace/8-assumptions-categorized/assumptions-categorized-*.json` by date in filename, descending.

3. **Hard-exit checks** (see Error handling). Do not write any output files when these fire.

4. **Parse input.** Extract all top-level carried fields. Extract `assumptions_per_solution[]`. Build an index of all upstream `assumption` objects keyed by `assumption.id` for the later merge.

5. **Build the scoring input.** Flatten all assumptions across the 3 solutions into a single ordered list. For each assumption, format one line as:

   ```text
   <solution_id> :: <assumption.id> :: [<category>] :: <assumption.text>
   ```

   The `<category>` (from upstream) is included so the LLM can ground importance calls against the type of risk an assumption carries. Order: solution 1's assumptions in upstream order, then solution 2's, then solution 3's.

6. **Run one LLM scoring pass.** Issue a single LLM call. The prompt contains, in order:

   - **Role frame:** "You are scoring product-discovery assumptions on Bland's 2x2: importance (high/low) and evidence (strong/weak). Riskiest = high importance + weak evidence."
   - **The two scoring questions** verbatim from `assumption-risk-mapping.md` v0.1 (Swedish-language original preserved for workshop fidelity):
     - Q1 (evidence): *Har vi redan bevis för att det här antagandet är sant?* Yes → `strong`. No → `weak`.
     - Q2 (importance): *Om vi har fel i det här antagandet, skiter det sig då?* Yes → `high`. No → `low`.
   - **The soft-evidence rule** verbatim from v0.2 (NEW):

     > Evidence includes empirical observation from the inputs AND domain norms, industry conventions, and general engineering practice. Mark `strong` if the assumption seems well-grounded; mark `weak` if genuinely speculative.

   - **The "skiter det sig" semantics** verbatim from v0.1:

     > The solution materially fails to deliver its impact on the product outcome. Edge-case wobbles do not qualify. The bar is whether the solution as a whole stops working.

   - **The rationale format rule** verbatim from v0.2 (NEW):

     > Write rationale as one sentence in the form `Importance=<level> (<reason>); evidence=<level> (<reason>).` Each parenthetical reason is one short clause.

   - **Solution context block:** for each of the 3 solutions, list `solution_id`, `title`, `description`, `generating_role`, `round_number`. Used to ground importance calls against the actual solution.
   - **Carried context:** chosen opportunity (id, phase, quote, source) and product outcome (verbatim). Used to ground importance calls against the outcome metric.
   - **The full flattened list of assumptions** (one per line, in the format from step 5).
   - **Task:** "For each assumption, return a JSON object `{id, importance, evidence, rationale}`. Use exactly one value from `{high, low}` for importance and `{strong, weak}` for evidence. Write rationale in the structured format. Return only a JSON array, one per assumption, in the same order as the input. No other fields, no prose preamble. Do NOT return `is_riskiest`; the skill computes that."

   Collect the response. Parse as a JSON array. If parsing fails, hard-exit.

7. **Validate the scoring response.** Verify:
   - Length equals the total upstream assumption count.
   - Every entry has `id` (string), `importance` (string), `evidence` (string), `rationale` (string).
   - Every `importance` in `{high, low}`; every `evidence` in `{strong, weak}`.
   - Every `rationale` matches the regex `^Importance=(high|low) \(.+\); evidence=(strong|weak) \(.+\)\.$`.
   - The set of ids in the response equals the set of upstream `assumption.id` values (no missing ids, no unknown ids).
   - No duplicate ids in the response.

   Any failure → hard-exit.

8. **Compute `is_riskiest` deterministically.** For each scored entry: `is_riskiest = (importance == "high" AND evidence == "weak")`. The skill computes this; the LLM is forbidden from returning it.

9. **Merge scores back into the upstream structure.** Build a lookup map: `scores_by_id[id] = {importance, evidence, is_riskiest, rationale}`. For each upstream assumption, build the output assumption object as a copy of the upstream object plus the four new fields. Every other field is carried byte-identical. Preserve upstream `assumptions[]` order within each per-solution entry (identity-mapping).

10. **Compose the v0.2 JSON.** Top-level fields per the schema. Carry every upstream top-level field byte-identical (`team`, `title`, `product_outcome`, `chosen_opportunity`, `source_assumptions`, `source_top_three_solutions`, `source_experience_map`, `categorization_summary`). Add `source_assumptions_categorized` (basename of the source `assumptions-categorized-*.json` file). Add `risk_summary` (fixed v0.2 block plus the two computed integer counts). Add `method` and `method_source` (carried from v0.1 anchor). `assumptions_per_solution[]` ordered by upstream `pick_position` (1, 2, 3). Within each per-solution entry, `assumptions[]` in upstream order.

11. **Validate invariants.** Hard-exit on any violation per the invariants list above.

12. **Render the markdown deterministically** from the JSON via the embedded template (Output composition).

13. **Write paired output** to:
    - `workspace/9-riskiest-assumptions/OST-riskiest-assumptions-<YYYY-MM-DD>.json`
    - `workspace/9-riskiest-assumptions/OST-riskiest-assumptions-<YYYY-MM-DD>.md`

    Use today's date in `YYYY-MM-DD`. Same root name on both files. Create `workspace/9-riskiest-assumptions/` if it does not exist. The skill does NOT modify any input files; the upstream `assumptions-categorized-*.json` stays immutable.

One pass through one LLM scoring call plus deterministic merge and `is_riskiest` computation. No retries beyond what the single Agent call inherently does; if scoring output is malformed or violates an invariant, the skill hard-exits.

## Output composition

Two files with the same root name:

```text
workspace/9-riskiest-assumptions/OST-riskiest-assumptions-<YYYY-MM-DD>.json
workspace/9-riskiest-assumptions/OST-riskiest-assumptions-<YYYY-MM-DD>.md
```

**The JSON** is strict schema v0.2.

**The markdown** is generated deterministically from the JSON via an embedded template in the prompt:

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
Source chosen opportunity: `workspace/context/chosen-opportunity.md`
Source product outcome: `workspace/context/product-outcome.md`
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

**Rendering rules:**

- **Role abbreviation, method-tag, category-tag mappings:** carried unchanged from assist 10 (`product-manager` → `PM`, `ux-designer` → `UX`, `tech-lead` → `TL`; `storymap` → `SM`, `pre-mortem` → `PrM`, `outcome-impact` → `OI`; categories lowercase verbatim).
- **Score tag:** `[<importance>/<evidence>]` with values lowercase verbatim. Four possible values: `[high/strong]`, `[high/weak]`, `[low/strong]`, `[low/weak]`.
- **`[RISKIEST]` marker:** appears only when `is_riskiest=true`. Bold all-caps in brackets, placed AFTER the score tag and BEFORE the text. Format: `**[RISKIEST]**`.
- **Tag order per row** is fixed: `[<methods>] [<category>] [<importance>/<evidence>] [optional RISKIEST]`. Methods → category → score → optional riskiest marker → text.
- **Rationale** rendered as a nested sub-bullet under each assumption row, indented 2 spaces, single line, verbatim from JSON. Never edited at render.
- **Per-solution `Riskiest:` summary line.** Placed between the solution-description paragraph and the `### Assumptions (<count>)` heading. Format: `**Riskiest:** <comma-separated ids>` or `**Riskiest:** (none)` if zero riskiest in that solution.
- **Trio HITL banner.** Top-of-file blockquote (`>` prefix), placed after the H1 and before the source-metadata lines. Verbatim text from the template above.
- **Total summary line.** `Total assumptions: <N>. Total riskiest: <M>.` placed after the framework-summary paragraph.
- **Chosen-opportunity source attribution** carried verbatim. Separated from the quote with ` - ` (regular dash).
- **No em-dash anywhere.** Frontmatter has blank line before closing `---`.
- **No `Cites:` line.**
- **Pick ordering** in the markdown mirrors the upstream `picks[]` array order.
- **Row ordering within each solution** preserves the upstream `assumptions[]` order. No re-sort by score or risk.
- **Output language** for assumption text and rationale follows the language of the upstream (typically Swedish for this trio). Schema field names, JSON keys, importance/evidence enum values, role enums, and id strings stay English.

## Knowledge-doc updates required before ship

As part of building this skill:

- **Bump `../knowledge/discovery/assumption-risk-mapping.md` to v0.2.** Append five new sections per "The knowledge anchor extension" above; existing v0.1 content stays intact. Add an Evolution entry at the bottom: `v0.2 / 2026-05-12 / "Extended for the OST-riskiest-assumptions skill: identity-mapping over upstream assist-10 output, soft-evidence rule, structured rationale format, schema v0.2 with full carry-forward + 4 new per-assumption fields, renderer template with Trio HITL banner."` and update the front-matter date to 2026-05-12.
- **Update `skills-design/skill-template.md` Bygg-status** - mark `OST-riskiest-assumptions` as built. Final task in the implementation plan, not in this design.
- **Update `skills-design/opportunity-solution-tree-agents.md`** - replace section 11's four open design questions with a reference to the locked decisions in `skills-design/OST-riskiest-assumptions-design.md`. Update the "Föreslagen typ" line from "Agent" to "Skill (single-pass classification against locked 2x2)" to match the actual decision.

What is NOT updated:

- `../knowledge/discovery/assumption-types.md` - read as reference; categorization is upstream and untouched.
- `../knowledge/discovery/opportunity-solution-tree-teresa-torres.md` - referenced but not extended.
- `../knowledge/discovery/assumption-categorization.md` - read for upstream schema; no changes.
- `workspace/context/ratifications.md` - intentionally NOT appended. The HITL gate is markdown-banner-only.

## Error handling

**Hard-exit triggers** (no output files written when these fire):

| Trigger | Looked for | Remedy |
|---|---|---|
| No `assumptions-categorized-*.json` in `workspace/8-assumptions-categorized/` | At least one `assumptions-categorized-<YYYY-MM-DD>.json` file | Run `OST-assumption-categorizer` (assist 10) first |
| Source JSON does not parse | Valid JSON conforming to `assumption-categorization.md` v0.1 | Re-run assist 10 |
| Source JSON `schema_version` is not `"0.1"` | The exact string `"0.1"` | Re-run assist 10 against v0.1 |
| Source `assumptions_per_solution.length != 3` | 3 entries (one per pick) | Re-run assist 10 |
| Any per-solution `assumptions.length` outside `6..18` | Per-solution count within the v0.1 invariant range | Re-run upstream `OST-generate-assumptions` |
| Any knowledge anchor missing | All four files at fixed paths | Restore from git |
| Scoring LLM pass returned malformed JSON | A JSON array of `{id, importance, evidence, rationale}` objects | Re-run; if persistent, the prompt's JSON instruction needs tightening |
| Scoring omits an upstream `assumption.id` | Every upstream id in the response | Re-run; if persistent, emphasize exhaustive coverage |
| Scoring contains an `id` not in the upstream input | Every response id is in the upstream input | Re-run |
| Scoring contains a duplicate `id` | No duplicate ids | Re-run |
| `importance` outside `{high, low}` or `evidence` outside `{strong, weak}` | Enum membership | Re-run; tighten enum instruction |
| `rationale` does not match format regex | `^Importance=(high\|low) \(.+\); evidence=(strong\|weak) \(.+\)\.$` | Re-run; if persistent, the rationale-format instruction needs tightening |
| LLM returned `is_riskiest` in any entry | Field absent (skill computes it) | Re-run; tighten the "do not return is_riskiest" instruction |
| Identity-mapping violation | All upstream fields byte-identical | Re-run; merge logic has drifted |
| `risk_summary.total_assumptions` does not match summed assumption count | Sum equals total | Re-run |
| `risk_summary.total_riskiest` does not match computed count of `is_riskiest=true` | Counts match | Re-run |
| Final-JSON invariant violation | Schema invariants | Re-run |

**Hard-exit message format** (same shape as upstream skills):

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

No silent degradation. No retries beyond the implicit retry inside any single Agent tool call.

**Soft warnings:** None for v1. Distribution sanity (e.g., 0 riskiest or 100% riskiest) is eyeball-only at v1 smoke test and parked as a v0.3 follow-up.

**Convention for missing optional fields in JSON:** v0.2 has no optional fields. `null` is never written.

**No JSON self-validation pass.** Trust the prompt and the invariant check; downstream consumers surface any malformed JSON. Mirrors all upstream skills.

## What this skill does NOT do

- **Read interview transcripts.** Scoring is judgmental on the assumption text + carried context, not evidence-traced.
- **Read the OST-brainstorm-solutions output, comparison matrix, validated opportunities, OST-cluster-solutions output, top-three-solutions JSON, the assumptions JSON, or the experience map directly.** Only the upstream `assumptions-categorized-*.json` contract listed in Inputs.
- **Read `chosen-opportunity.md`, `product-outcome.md`, or `ratifications.md`.** Identifying context flows through the upstream JSON; no ratification gate consumed at input.
- **Append to `ratifications.md`.** The phase-3 HITL gate is markdown-banner-only by locked decision; assist 12 reads latest-by-date.
- **Generate, modify, merge, or drop assumptions.** Identity-mapping over upstream `assumptions[]` is the core invariant; every upstream assumption appears exactly once in the output with four new fields added.
- **Re-order assumptions.** Row order preserves upstream. Riskiest are surfaced via marker and summary line, not re-ordering.
- **Return `is_riskiest` from the LLM.** The skill computes it from importance + evidence.
- **Use graded scoring on importance or evidence.** Binary axes; "binary, no graded scale" carried from v0.1 anchor. The brainstorm-input's open question on `not_sure` fallback is resolved by the anchor: no fallback, force binary.
- **Design test cards or validation experiments.** That is assist 12.
- **Score riskiness across solutions (cross-solution comparison).** Each solution scored independently in the same prompt; no global riskiest ranking. Per-solution `Riskiest:` summary and inline marker only.
- **Modify upstream files.** The `assumptions-categorized-*.json` and all context files stay immutable.
- **Write to `workspace/context/`.** Output lives in `workspace/9-riskiest-assumptions/`.
- **Add an in-skill ratification mechanism.** Trio gate is markdown-banner-only.
- **Run a JSON self-validation pass beyond the invariant check.**
- **Retry the scoring pass on partial failures.** Hard-exit; operator re-runs end-to-end.
- **Use a `confidence`, `alt_importance`, `alt_evidence`, `risk_level`, or `shared_with` schema field.** All either downstream territory or v0.3 follow-ups.
- **Spawn sub-agents.** Single-pass scoring is the architecture.
- **Default to a single axis value when uncertain.** Force one binary value on each axis (no `null`, no `unknown`).
- **Group assumptions by risk in markdown.** Flat row order preserves upstream; risk surfaces as a per-row marker and a per-solution summary line.
- **Write to Miro or any external surface.** JSON + markdown only.

## Testing

Smoke test only for v1, no formal regression harness. Reuses the Norrsken assist-10 output from this build.

```text
Inputs:
  workspace/8-assumptions-categorized/assumptions-categorized-2026-05-12.json
    (Norrsken; 31 assumptions across 3 solutions, categorized)

Expect:
  - schema_version "0.2" in the output JSON
  - method "assumption-risk-mapping", method_source verbatim
  - assumptions_per_solution.length == 3
  - Identity-mapping: every assumption.id, text, source_methods, category byte-identical
    to upstream at each index in the same order
  - For each per-solution entry, assumptions[].length equals upstream length
  - Every importance in {high, low}; every evidence in {strong, weak}
  - Every rationale matches the regex
    ^Importance=(high|low) \(.+\); evidence=(strong|weak) \(.+\)\.$
  - is_riskiest correctly computed from importance + evidence in every assumption
  - chosen_opportunity, all source_* fields, categorization_summary carried byte-identical
  - source_assumptions_categorized correctly references the source filename
  - risk_summary is the fixed v0.2 block with total_assumptions=31 and total_riskiest
    matching actual count
  - Markdown frontmatter present with blank line before closing ---
  - Trio HITL banner present at top of body (>-prefixed blockquote)
  - "Total assumptions: 31. Total riskiest: <M>." line present
  - Three "## Solution N: <title>" sections
  - Each solution opens with a "**Riskiest:**" line (ids comma-separated or "(none)")
  - Every assumption row matches the strict regex with the score tag and optional [RISKIEST] marker
  - Rationale rendered as nested sub-bullet under each assumption row
  - No em-dash anywhere
  - No "Cites:" line
  - No changes to workspace/context/ratifications.md

Eyeball checks:
  - Total riskiest count is plausible (typically 30-50% of assumptions in early discovery;
    not 0%, not 100%)
  - Per-solution riskiest counts are not all zero and not all max
  - Spot-check 5 riskiest: do they read as "high + weak" calls a human would also make?
  - Spot-check 5 non-riskiest: do they read as either established knowledge or non-critical-path?
  - Score tags consistent with rationale: importance=high in rationale matches [high/...] tag, etc.
  - Soft-evidence rule visibly applied: a few assumptions about widely-known domain norms
    score evidence=strong even without input data backing them
  - is_riskiest visible inline matches the JSON for 5 spot-check ids
```

What the smoke test does NOT exercise (parked as open follow-ups):

- Edge case: all assumptions scored riskiest (signals scoring miscalibration or trivial input).
- Edge case: zero assumptions scored riskiest (signals over-strict scoring or genuinely de-risked solution set).
- Edge case: scoring response missing or duplicating ids (hard-exit fires, but the operator experience hasn't been smoke-tested).
- Multi-pass scoring for consistency (single pass is v1).
- Configurable evidence rule (soft locked at v1).
- Per-team scoring overrides.
- Explicit-filename input mode (v1 reads latest by date).
- Trio edits to JSON then re-renders the markdown (markdown is generated by the skill; trio edits to JSON without re-rendering would create JSON↔markdown drift, which is acceptable at v1 since assist 12 reads JSON).

These gaps are accepted for v1.

## Open follow-ups

These are added to `TODO.md` rather than blocking v1.

1. **Per-solution riskiness floor/ceiling sanity check.** Soft-warn if 0 or all assumptions in a solution are flagged riskiest. v1 is eyeball-only.
2. **Configurable evidence rule (strict vs soft).** v1 locks soft. Surface as a config flag if a trio wants strict-only scoring for audit purposes.
3. **Scoring history tracking.** Anchor's existing open evolution from v0.1 ("Track scoring history when the same assumption is re-mapped"). Parked.
4. **Categories breakdown in `risk_summary`.** Add `riskiest_by_category` map to surface whether the trio is testing only feasibility, etc. Parked.
5. **Optional `confidence` field on importance/evidence.** Anchor's existing open evolution from v0.1 ("Add an explicit 'uncertain' option"). Parked.
6. **Effort-vocabulary blocklist post-pass.** Carried from upstream skills' open follow-ups. Eyeball-only at smoke test.
7. **Schema evolution beyond v0.2.** Procedure same as upstream skills: add an Evolution entry and bump `schema_version`.
8. **Re-score-only mode.** Preserve upstream identity-mapping, re-run scoring against changed inputs. Useful if the trio want to redo importance/evidence calls without re-running upstream. Parked.
9. **Explicit-filename input mode.** v1 reads latest `assumptions-categorized-*.json` by date. Add an optional filename parameter for re-scoring older versions.
10. **Trio-edit re-render mode.** v1 generates markdown once at skill run; trio edits to JSON are not reflected in markdown. Parked feature: a separate "re-render markdown from current JSON" mode.

## What this skill establishes for the workshop-3 series

- **Schema-extension precedent.** First skill that BUMPS an existing knowledge anchor (v0.1 → v0.2) rather than creating a new one. Pattern transfers to any future skill that extends an existing structured artifact rather than introducing a new artifact type.
- **Identity-mapping with multi-field add.** Builds on assist 10's precedent (identity-map + 1 new field) by demonstrating that the pattern scales to 4 new fields cleanly. Future skills can add larger field sets without breaking the carry-forward chain.
- **Deterministic-derivation field.** First skill where one field (`is_riskiest`) is computed by the skill from LLM-returned fields rather than returned by the LLM directly. Pattern transfers to any field whose definition must remain stable across LLM drift.
- **Structured rationale format.** First skill that constrains rationale to a regex-checked structural template. Pattern transfers to any future field where downstream parseability matters.
- **Markdown HITL banner without ratifications.md.** First skill that uses a markdown banner as the trio gate without writing to the ratifications log. Lighter alternative to the OST-select-top-three-solutions v2 pattern; appropriate when downstream is also a skill consuming latest-by-date (not a long-tail consumer needing audit trail).
- **Knowledge anchor as both reference (for human readers) and runtime input (for LLM).** v0.2 of `assumption-risk-mapping.md` serves dual roles: original v0.1 framing for trios learning the method, plus new v0.2 sections that the skill loads at runtime. Pattern formalizes the dual-purpose anchor convention.
