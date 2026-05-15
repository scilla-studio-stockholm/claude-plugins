---
title: "OST-select-top-three-solutions: design spec (v2)"
date: 2026-05-11
purpose: Locked v2 design for assist 8 in opportunity-solution-tree-agents.md - takes the v0.1 solution-candidates JSON from OST-brainstorm-solutions (assist 6) plus the trio's chosen-opportunity and product-outcome context, runs a single-pass LLM call to pick 3 specific member solutions ranked by outcome-impact probability, each with a 2-3 sentence outcome-mapping rationale. Schema v0.2 in knowledge/discovery/top-three-selection.md replaces v0.1 (cluster-input + discriminator picks). OST-cluster-solutions stays built but is removed from the required pipeline. Input to the implementation plan.
tags: [skill-design, workshop-3, ost, top-three-selection, schema-v0.2]

---

# OST-select-top-three-solutions: design spec (v2)

This is the locked v2 design for **assist 8** in `opportunity-solution-tree-agents.md`. It supersedes the v0.1 design (committed at `36a2826`, implemented in commits `9693096..2553a1e` on 2026-05-11). Smoke-test of v0.1 surfaced an architectural mismatch with the workshop process — the picker output clusters rather than specific solutions, conflated "explore in parallel" with mechanism diversification, and pre-empted assist 9's assumption-reasoning. The v2 redesign drops the clusterer from the required pipeline and simplifies the picker to "top 3 by outcome-impact probability, each a specific solution".

## What the skill does (v2)

For product trios and researchers, when picking the top 3 solutions to carry into assumption testing from a divergent brainstorm output, output a paired JSON + markdown proposal with 3 specific solutions ranked by outcome-impact probability, each with a 2-3 sentence outcome-mapping rationale. Input to assist 9 (assumption generator) after trio ratification.

Input is the v0.1 solution-candidates JSON from `OST-brainstorm-solutions` (the 18 specific solutions) and the trio's chosen-opportunity + product-outcome context. Output is two files in `workspace/6-top-three/` with the same root name: a top-three-solutions JSON conforming to schema v0.2 in `knowledge/discovery/top-three-selection.md`, and a markdown rendering generated deterministically from the JSON.

The skill produces a **proposal**, not a decision-of-record. The trio reviews the proposal, edits if needed, and writes a one-line entry into `workspace/context/ratifications.md` (the ratification-flag pattern). Assist 9 reads `ratifications.md` to find the approved version. The selector itself does not write to `workspace/context/`.

## What changed from v0.1 (rationale for the redesign)

The v0.1 implementation was built and smoke-tested. The smoke-test output revealed three architectural problems:

1. **Cluster-bias in picker behavior.** The v0.1 discriminator-variant schema let the picker choose cluster-picks or member-picks per pick. In practice the picker chose 3-of-3 cluster-picks because cluster-level rationale is easier to argue than per-member differentiation. The "flexibility" of the discriminator hid a strong default that didn't match the trio's mental model. Specific solutions are what the trio expects to carry forward; clusters are workshop-scaffolding for human cognition.
2. **"Explore in parallel" ≠ mechanism diversification.** v0.1 imported a soft diversification heuristic (via the cluster-context rationale ingredient) on the theory that Torres' "choose three to explore in parallel" implied mechanism diversity. Torres' principle is actually about comparative-learning speed (running 3 simultaneously beats running 1 → evaluate → run next), not about hedging across mechanisms. Three picks that all bet on flavors of one mechanism is a legitimate trio choice. The picker shouldn't enforce diversification.
3. **Premature assumption-reasoning.** v0.1's rationale-ingredient "customer-evidence anchor" plus the diversification heuristic together pushed the picker into reasoning about which assumptions the picks share. That's assist 9's job. The picker's job is "if this works, would it move the outcome?" — not "what makes this risky?".

The v2 redesign collapses the architecture: directly read the brainstormer's 18 specific solutions, rank by outcome-impact probability, return the top 3 with outcome-mapping rationale. No clusters, no diversification, no assumption-reasoning. Simpler at every layer.

## Scope decisions (locked 2026-05-11 v2)

The v2 brainstorm resolved four open questions on top of the v0.1 corrections.

| Question | v0.1 decision | v2 decision |
|---|---|---|
| Pick unit | Either cluster or member, AI chooses per pick (discriminator-variant) | **Always specific member solution.** No discriminator. Each pick is one of the 18 specific solutions from the brainstormer. |
| Pick count | Flexible 2-4, material-driven | **Strict 3** (Torres canon). The material-driven argument was about clusters collapsing; with 18 specific solutions the top 3 by probability always exists. |
| Rationale prose ingredients | outcome-mapping + cluster-context + customer-evidence anchor | **Outcome-mapping only.** 2-3 sentences. Cluster-context dropped (no clusters). Customer-evidence anchor dropped (chosen-opp quote is in the file header; rationale doesn't need to repeat it). |
| Alternatives considered | Every cluster not represented | **None.** Section omitted entirely. Trio reads the brainstormer markdown directly to see the other 15 specific solutions if they want to override. Cleanest output. |
| Diversification | No structural constraint | **No constraint** (unchanged), but the soft diversification heuristic in the v0.1 prompt is removed. The picker ranks by outcome-impact probability; if the top 3 happen to share a mechanism, that's a coherent comparative bet. |
| Assumptions | No `key_assumptions[]` field, assist 9 owns | **No `key_assumptions[]` field** (unchanged). v2 reinforces: rationale prose does NOT mention assumptions or risks. Assist 9 owns that domain. |
| Hedging tone | Confident on clean wins, transparent on close calls | **Same** (unchanged). Rationale prose may name a near-miss inline if the #3 vs #4 distinction is genuinely close; otherwise stays confident. |
| Input source | Cluster-map from OST-cluster-solutions | **Direct from OST-brainstorm-solutions output.** The 18 specific solutions, no intermediate clustering. |
| OST-cluster-solutions in pipeline | Required upstream (assist 7) | **Off-pipeline.** Skill stays built and available; trios may invoke it for their own clustered review of the brainstorm. Not a required input to assist 8. Bygg-status pipeline shrinks from 13 to 12 required assists for the workshop-3 critical path. |
| Schema version | v0.1 in `top-three-selection.md` | **v0.2** in `top-three-selection.md`. v0.1 stays as Evolution entry. |
| Trio ratification | Ratification-flag pattern via `workspace/context/ratifications.md` | **Same** (unchanged). v0.1 introduced this pattern; v2 keeps it. |
| Cross-check chosen-opp id | Source-JSON vs context-md bold-id | **Same** (unchanged). Brainstormer output carries `chosen_opportunity.id`; cross-check against context bold-id row, hard-exit on mismatch. |
| Skill vs agent | Plain skill, single-pass | **Same** (unchanged). One LLM call, deterministic post-processing. |
| Body language | English | **English** (unchanged). |
| Output location | `workspace/6-top-three/` | **Same** (unchanged). |
| Output filename | `top-three-solutions-<YYYY-MM-DD>.{json,md}` | **Same** (unchanged). |
| Output format | Paired JSON + markdown | **Same** (unchanged). |

## Skill identity

| Field | Value |
|---|---|
| File path | `.claude/skills/OST-select-top-three-solutions/SKILL.md` (same path, body rewritten for v2) |
| Skill name | `OST-select-top-three-solutions` (unchanged) |
| Slash-command (optional) | `/OST-select-top-three-solutions` if frequency justifies |
| Body language | English |
| Tools | `Read` |

**Description field** (load-bearing for natural-language trigger):

> For product trios and researchers, when picking the top 3 solutions to carry into assumption testing from a divergent brainstorm output, output a paired JSON + markdown proposal with 3 specific solutions ranked by outcome-impact probability, each with an outcome-mapping rationale. Input to assist 9 (assumption generator).

Distinct from `OST-brainstorm-solutions` (generates the 18; doesn't pick), `OST-cluster-solutions` (optional clustered review; not in the pipeline), `OST-select-opportunity` (picks one opportunity from a comparison matrix; different layer).

## Inputs and prerequisites

**Input files:**

| File pattern | Source | Used for |
|---|---|---|
| `workspace/4-solution-brainstorm/solution-candidates-<date>.json` | `OST-brainstorm-solutions` (assist 6) | The 18 specific solutions to rank and pick from. v0.1 schema (per `knowledge/discovery/solution-brainstorm.md`). |
| `workspace/context/chosen-opportunity.md` | Trio-ratified | Cross-check against source JSON's `chosen_opportunity.id`. Quote and source available as grounding context in the LLM prompt; not required in rationale prose (rationale is outcome-mapping only). |
| `workspace/context/product-outcome.md` | Trio-authored, fixed path | Outcome formulation that grounds the outcome-mapping in the rationale. |

**File-resolution rules:** Latest `solution-candidates-*.json` in `workspace/4-solution-brainstorm/` by date in filename, descending. Context files at fixed paths.

**Knowledge anchors read at runtime:**

- **`knowledge/discovery/top-three-selection.md`** (UPDATED, bumped to v0.2) — schema v0.2, the v2 locked decisions, the ratification-flag pattern (unchanged from v0.1), the no-effort rule.
- `knowledge/discovery/solution-brainstorm.md` — source schema (v0.1) so the picker can parse the brainstormer's output.
- `knowledge/discovery/opportunity-solution-tree-teresa-torres.md` — Torres principles. The canonical anchor is "Choose three solutions to explore in parallel" (CDH ch 7 step 6). The "Don't assess effort during opportunity selection" rule is carried to solution selection prose per convention.

**What the skill does NOT consume:**

- The cluster-map from `OST-cluster-solutions` (off-pipeline; not required).
- The paired markdown brainstormer file (`solution-candidates-<date>.md`). JSON is the contract.
- The experience map, comparison matrix, validated opportunities, interview transcripts.

## The knowledge anchor: `knowledge/discovery/top-three-selection.md` (v0.2)

The existing anchor (created at commit `9693096` for v0.1) is updated in place to v0.2. v0.1's schema and decisions move to the Evolution section as historical record; v0.2 sections describe the current state.

**Sections in the v0.2 anchor:**

1. **What the selector does** — short framework prose tying it to Torres CDH ch 7 step 6 ("Choose three solutions to explore in parallel"). Notes that the picker reads brainstormer output directly (clustering off-pipeline) and produces a proposal that the trio ratifies via `ratifications.md`.
2. **The four v2 locked decisions** — strict 3 picks, always member-pick (no discriminator), outcome-mapping-only rationale, no alternatives section.
3. **The no-effort rule** — carried from the OST anchor. Rationale prose must not introduce effort vocabulary. Eyeballed at smoke test.
4. **The ratification-flag pattern** — unchanged from v0.1. Definition of `workspace/context/ratifications.md` line format and reading rule.
5. **JSON schema (v0.2)** — the contract (below).
6. **Field notes** — per-field commentary, missing-optional convention.
7. **Open questions** — v0.3 candidates (configurable pick count, near-miss surfacing if trios report needing it, etc.).
8. **Evolution** — version history. v0.1 entry kept; v0.2 entry added with rationale for the change.

**Schema v0.2:**

```json
{
  "schema_version": "0.2",
  "team": "string (carried from source brainstorm JSON)",
  "title": "string (e.g., 'Top solutions: <first clause of chosen opportunity quote>')",
  "product_outcome": "string (carried)",
  "chosen_opportunity": {
    "id": "string (carried; e.g., 'opp-5-1'; matches the bold-id row in workspace/context/chosen-opportunity.md)",
    "phase_id": "string (carried)",
    "quote": "string (carried verbatim)",
    "source": "string (carried verbatim)"
  },
  "source_solution_candidates": "string (filename of source solution-candidates-*.json)",
  "picks": [
    {
      "id": "string (verbatim member id from source, e.g., 'sol-r1-pm-1')",
      "title": "string (verbatim from source)",
      "generating_role": "product-manager | ux-designer | tech-lead (verbatim)",
      "round_number": "integer (verbatim)",
      "description": "string (verbatim from source)",
      "rationale": "string (2-3 sentences; outcome-mapping only — names the causal path from this specific solution to moving the product outcome)"
    }
  ],
  "extensions": {}
}
```

**Removed from v0.1:** `pick_count` (always 3, redundant), `pick_type` discriminator and `cluster` / `member` sub-objects (always specific-member, no discriminator), `alternatives_considered[]` (omitted entirely), `notes` (no pick-count deviation possible).

**Invariants** (skill enforces; hard-exit on violation, no partial writes):

- `picks.length == 3`. Exactly 3.
- Each `pick.id` ∈ source `solutions[].id`. No inventions.
- No duplicate pick ids across `picks[]`.
- All carried fields (`title`, `generating_role`, `round_number`, `description`) byte-identical to source for each picked member.
- `chosen_opportunity.{id, phase_id, quote, source}` byte-identical to source brainstormer JSON.
- `chosen_opportunity.id` matches source JSON's `chosen_opportunity.id` AND the bold-id row in `workspace/context/chosen-opportunity.md`.

**Soft conventions** (in prompt, not invariants):

- Picks ordered by descending outcome-impact probability (strongest first).
- Rationale 2-3 sentences. Names a causal path from the pick's mechanism to the product outcome's metrics ("manuella steg" / "antalet aktörer" / etc., depending on the trio's outcome formulation). Eyeballed at smoke test.
- No effort vocabulary in rationale (Torres principle, eyeballed).
- Hedging only when warranted: if #3 vs #4 was genuinely close, the #3 rationale may name the near-miss inline. No always-on hedging.

## Skill execution flow

One LLM call, deterministic post-processing.

1. **Read knowledge anchors:** `top-three-selection.md`, `solution-brainstorm.md`, `opportunity-solution-tree-teresa-torres.md`.
2. **Locate inputs:** latest `solution-candidates-*.json` in `workspace/4-solution-brainstorm/`; `workspace/context/chosen-opportunity.md`; `workspace/context/product-outcome.md`.
3. **Hard-exit checks** (Section "Hard-exit triggers" below).
4. **Parse inputs.** Index source `solutions[]` by `id`. Extract bold-id row from `chosen-opportunity.md`. Extract outcome formulation from `product-outcome.md`'s `## Outcome` section.
5. **Cross-check chosen-opp id.** Source JSON vs context.md. Mismatch → hard-exit.
6. **Compose LLM prompt** in this order:
   - Role frame: "You are picking the 3 specific solutions with the strongest probability of moving the product outcome within the chosen opportunity."
   - Grounding: chosen opportunity (full record with quote+source), product outcome (verbatim).
   - The 18 candidates rendered as a flat list with full records (id, title, generating_role, round_number, description). Raw JSON acceptable; flat-list rendering also acceptable.
   - Schema reference: point to `knowledge/discovery/top-three-selection.md` by path; include v0.2 JSON skeleton inline.
   - The four v2 locked decisions verbatim as rules (strict 3, always specific member, outcome-mapping-only rationale, no alternatives).
   - The no-effort rule.
   - Output instruction: "Return only a single JSON object matching the schema. No prose preamble."
7. **Receive and parse JSON.** Malformed → hard-exit.
8. **Validate invariants** (Section above). Violation → hard-exit naming the specific invariant.
9. **Set top-level `title`** to `"Top solutions: <first 5-10 words of chosen_opportunity.quote, trailing punctuation stripped>"`. Set `source_solution_candidates` to the basename of the source brainstormer JSON.
10. **Write JSON** to `workspace/6-top-three/top-three-solutions-<today>.json`. Create directory lazily.
11. **Render markdown** deterministically from JSON (template below) and write to `workspace/6-top-three/top-three-solutions-<today>.md`.

No retries, no iteration, no JSON self-validation pass. Upstream files immutable.

## Output composition

Two files with the same root name:

```text
workspace/6-top-three/top-three-solutions-<YYYY-MM-DD>.json
workspace/6-top-three/top-three-solutions-<YYYY-MM-DD>.md
```

The JSON is strict schema v0.2.

**Markdown template** (deterministic from JSON):

```markdown
---
title: "Top solutions: <chosen_opportunity.id> - <first 5-10 words of chosen_opportunity.quote>"
date: <YYYY-MM-DD>
purpose: Selector proposal for OST step 6 (top solutions to explore in parallel). Paired with top-three-solutions-<date>.json. Trio reviews and ratifies via workspace/context/ratifications.md. Input to assist 9 (assumption generator).
tags: [top-three-selection, ost, schema-v0.2]

---

# Top solutions: <chosen_opportunity.id>

Source solution candidates: `<source_solution_candidates>`
Source chosen opportunity: `workspace/context/chosen-opportunity.md`
Source product outcome: `workspace/context/product-outcome.md`
Schema version: 0.2
Paired JSON: `top-three-solutions-<YYYY-MM-DD>.json`

> **Trio HITL:** This is the AI's proposal. Review the rationales, override if you disagree, then write a one-line ratification entry into `workspace/context/ratifications.md` so assist 9 reads the approved version.

## Chosen opportunity

**<chosen_opportunity.id>** (Phase: <phase_id>) - "<chosen_opportunity.quote>" - *<chosen_opportunity.source>*

## Product outcome

> <product_outcome>

## Picks (3)

### Pick 1: <title>

**<id>** [<role-abbrev>, R<round_number>]

<description>

*Rationale:* <rationale prose>

### Pick 2: <title>

(same shape)

### Pick 3: <title>

(same shape)
```

**Rendering rules:**

- **Role abbreviation mapping**: `product-manager` → `PM`, `ux-designer` → `UX`, `tech-lead` → `TL`.
- **Source attribution** carried verbatim. Separated from the quote by ` - ` (regular dash).
- **No em-dash** anywhere; uniform across Swedish and English prose.
- **Frontmatter** complies with the project rule (blank line before closing `---`).
- **HITL banner** rendered verbatim every run.
- **Pick numbering** is sequential by `picks[]` array order (which mirrors the AI's confidence ordering).
- **No alternatives section.** Trio reads the brainstormer markdown (`workspace/4-solution-brainstorm/solution-candidates-<date>.md`) to see the other 15 specific solutions.
- **No notes section.** v0.2 schema removes the `notes` field since pick_count is always 3.
- **Output language for prose** (`rationale`) matches the source language detected in the chosen-opportunity quote and brainstormer descriptions.

## Hard-exit triggers

Skill aborts with a clear three-line error naming the violation. No partial writes.

**Error message format:**

```text
ERROR: <one-line failure>
- Looked for: <pattern or field name and where>
- Found: <what was actually present>
- Remedy: <concrete next step the operator should take>
```

| Trigger | Remedy hint |
|---|---|
| Zero `solution-candidates-*.json` in `workspace/4-solution-brainstorm/` | Run `OST-brainstorm-solutions` |
| `workspace/context/chosen-opportunity.md` missing | Restore from git or re-ratify from OST-select-opportunity proposal |
| `workspace/context/product-outcome.md` missing or no `## Outcome` section | Re-author per template |
| Source JSON does not parse | Re-run `OST-brainstorm-solutions` |
| Source JSON `schema_version` is not `"0.1"` | Re-run `OST-brainstorm-solutions` |
| Source `solutions[]` count != 18 | Re-run `OST-brainstorm-solutions` (3 sub-agents × 3 rounds × 2 ideas = 18) |
| `chosen_opportunity.id` mismatch (source JSON vs `chosen-opportunity.md` bold-id row) | Decide which version is authoritative; reconcile manually |
| Missing knowledge anchor (`top-three-selection.md`, `solution-brainstorm.md`, or `opportunity-solution-tree-teresa-torres.md`) | Restore from git |
| LLM output not valid JSON | Re-run; if persistent, prompt issue |
| Invariant: `picks.length != 3` | Re-run; prompt-enforcement issue |
| Invariant: pick id not in source `solutions[]` | Re-run |
| Invariant: duplicate pick ids | Re-run |
| Invariant: carried fields not verbatim from source | Re-run |
| Invariant: `chosen_opportunity.id` in output != source brainstormer JSON | Re-run |

**No JSON self-validation pass.** Trust the invariant check. No effort-vocabulary post-pass — eyeball at smoke test. **Missing-optional convention:** omit optional keys; never write `null`.

## Smoke-test plan (v2)

Use the existing Norrsken brainstormer fixture.

| Component | Path |
|---|---|
| Source solution candidates | `workspace/4-solution-brainstorm/solution-candidates-2026-05-10.json` (18 solutions, chosen-opp `opp-5-1`) |
| Chosen opportunity | `workspace/context/chosen-opportunity.md` (`opp-5-1`, licenstilldelning) |
| Product outcome | `workspace/context/product-outcome.md` (Norrsken: "Minska antalet manuella steg och aktörer ...") |
| Expected output dir | `workspace/6-top-three/` (already exists from v0.1 smoke test) |

**Hard pass criteria** (structural; if any fail, prompt or skill is broken):

- `schema_version` is `"0.2"`
- `picks.length == 3` exactly
- Every `pick.id` is in the source `solutions[]` (no inventions)
- No duplicate pick ids
- All carried fields (`title`, `generating_role`, `round_number`, `description`) byte-identical to source
- `chosen_opportunity.id == "opp-5-1"`, `phase_id == "fas-5"`, quote and source verbatim
- Markdown frontmatter present with blank line before closing `---`
- Markdown HITL banner verbatim
- No em-dash anywhere

**Soft expectations** (eyeball; if missed, surface for design review):

- Each rationale traces a mechanism back to "manuella steg" reduction or "antalet aktörer" reduction (the outcome's metrics)
- Each rationale is 2-3 sentences
- No effort vocabulary (`complex`, `easy`, `simple`, `expensive`, `cheap`, `feasible`, `infeasible`, `scalable`, `quick win`, `low-hanging fruit`, `ambitious`, `risky-to-build`, `effort`, `implementation cost`, `build time`)
- No assumption-reasoning vocabulary (`risky`, `assumption`, `bet`, `if this works` — the rationale should be assertive: "this moves the outcome by X" not "this would move the outcome IF X").
- Picks ordered with the strongest probability first

**What the smoke test does NOT exercise** (parked as v0.3 follow-ups):

- A genuine close-call requiring inline near-miss callout
- Pick-from-same-mechanism scenario (all 3 picks share a primary mechanism family)
- Source with fewer than 18 candidates (off-spec; brainstormer should produce exactly 18)
- Trio override of the AI's picks (out-of-band ratification scenario)

## Scope-out (v2)

The skill explicitly does NOT:

- Read `OST-cluster-solutions` output, `OST-compare-opportunities` matrix, validated opportunities, experience map, or interview transcripts. Everything needed is in the brainstormer JSON + the two context files.
- Cluster, group, or categorize the 18 source solutions. `OST-cluster-solutions` is a separate optional skill the trio may invoke for their own review; not consumed here.
- Generate assumptions per pick. That is assist 9's job (storymap, pre-mortem, outcome-impact methods).
- Surface alternatives, near-misses, runners-up as a structured field. The trio reads brainstormer markdown directly.
- Pick more than 3 or fewer than 3. Hard invariant.
- Pick the same identity twice.
- Write to `workspace/context/`. Ratification is the trio's manual step.
- Score, matrix, or rank numerically. Single-pass qualitative judgement; the ranking is internal to the LLM call and surfaces only as picks[] order.
- Assess effort, feasibility, or implementation cost. Torres principle, carried.
- Apply mechanism diversification as a soft or hard rule. The picker ranks by outcome-impact probability; if the top 3 share a mechanism family, that's a coherent comparative bet (a trio choice to override or accept).
- Iterate, retry, or run multiple passes.
- Run a JSON self-validation pass.
- Ask the trio interactively. Force a pick.
- Write to Miro or external surfaces.

## Knowledge-doc updates required before ship

As part of building v2:

1. **Update `knowledge/discovery/top-three-selection.md`** — bump schema to v0.2. Sections: "The four v2 locked decisions" replaces "The eight locked decisions" (the eight collapse to four after dropping discriminator, alternatives, three-ingredient rationale). Customer-evidence anchor convention section removed (no longer required). v0.1 decisions move to Evolution as historical entry. Schema in the body replaced with v0.2.
2. **Update `skills-design/skill-template.md` Bygg-status** — change the assist-7 (OST-cluster-solutions) entry to note "off-pipeline; available but not required for assist 8". Keep the assist-8 entry as built; update body to describe v2.
3. **Update `skills-design/opportunity-solution-tree-agents.md`** — update assist 8 entry (lines 530-559) to reflect v2: input is OST-brainstorm-solutions output (not OST-cluster-solutions); 3 specific picks; outcome-mapping-only rationale. Update assist 7 entry to note "off-pipeline".

What is NOT updated:

- `knowledge/discovery/solution-cluster.md` — still describes OST-cluster-solutions schema. The skill still works; users can still invoke it. Unchanged.
- `knowledge/discovery/solution-brainstorm.md` — picker reads schema v0.1 unchanged.
- `knowledge/discovery/opportunity-solution-tree-teresa-torres.md` — picker references it but doesn't extend it.

## Open follow-ups (v0.3 candidates)

These go to `TODO.md` rather than blocking v2.

1. **Near-miss inline callout convention.** v0.2 says hedging is "only when warranted" but doesn't enforce a structural convention. If trios report wanting clearer signals about close calls (e.g., "Pick 3 was a hair above Pick 4"), add either an optional `near_miss_inline` field or a prompt convention for surfacing closeness.
2. **Configurable pick count.** v0.2 locks 3. If trios consistently want 2 (assumption-budget concerns) or 4 (extra exploration), surface as configurable in the anchor.
3. **Optional cluster-context provenance.** v2 drops cluster-context entirely. If trios who run `OST-cluster-solutions` separately want the picker to label each pick with its cluster origin (for the trio's reference, not as a constraint), add an optional `cluster_id_if_clustered` field. Only relevant if the trio invokes OST-cluster-solutions out-of-band.
4. **Negative-test fixtures.** Trackad in shared backlog. Cases: missing source, schema mismatch, missing context file, chosen-opp id mismatch, malformed LLM output, source `solutions[]` != 18.
5. **Effort-vocabulary blocklist post-pass.** Eyeball-only at smoke test. If trios catch effort thinking creeping into rationale, add forbidden-vocabulary blocklist or post-pass.
6. **Assumption-vocabulary blocklist post-pass.** Same shape. If rationale prose starts naming assumptions ("this works IF Delfi API permits writes"), that's assist 9's territory. Eyeball-only at smoke test; promote to enforced if observed.
7. **`OST-cluster-solutions` retirement decision.** v2 leaves OST-cluster-solutions built but off-pipeline. Decide later whether to deprecate fully (delete the skill, document as obsolete) or keep as supported standalone tool. Pending evidence of trio usage.
8. **Ratification-pattern consolidation.** Inherited from v0.1 open follow-up. Three patterns coexist; pick one and converge.
9. **`workspace/context/ratifications.md` documentation.** Inherited from v0.1. Document the file convention and one-line format in the workspace README.
10. **Assist 9 reads from `ratifications.md` contract.** Inherited from v0.1. Assist 9's design will specify the line format it parses and behavior on multiple ratification entries.

## What this skill establishes for the workshop-3 series (v2)

- **Direct-input precedent.** v0.2 is the first picker-style skill in the series that reads brainstormer output directly without an intermediate clustering pass. The pattern transfers to any future skill that ranks a flat set of candidates.
- **Schema-version evolution within an anchor.** First instance of an anchor (top-three-selection.md) bumping from v0.1 to v0.2 with the Evolution section carrying the change rationale. Establishes the precedent for in-place schema bumps when the design shifts.
- **Off-pipeline skill convention.** First skill (OST-cluster-solutions) explicitly marked as off-pipeline in Bygg-status. Establishes that "built" doesn't mean "required" — skills can be available as standalone tooling without being in the critical path. Future skills that turn out to be optional can use the same convention.
- **Architectural-mistake recovery pattern.** v0.1 was shipped and smoke-tested before the architectural mistake surfaced. v0.2 rewrites in place rather than reverting. Git history preserves the v0.1 design and implementation as learning artifact. Future skills that get redesigned mid-build can follow the same pattern.
