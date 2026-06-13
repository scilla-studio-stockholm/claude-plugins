---
name: OST-record-round
description: Close the loop on a discovery round by writing it into the living tree (tree.json). Use when a trio has run (some of) their validation experiments and wants to record results ("experimentet visade...", "record experiment results", "log what we learned"), or when a finished round should be archived into cross-round memory before starting the next one. Appends the round's lineage (opportunities, solutions, riskiest assumptions) and records per-assumption validation outcomes.
---

# Record round (living tree write-back)

You close the loop on a discovery round: you append the round's decision lineage to `<scope>/tree.json` (the cross-round living tree) and record experiment results against the riskiest assumptions. This is assist 14, the terminal write-back after assist 13's run-list — it turns a finished round into memory the next round reads.

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`.

2. **Read the schema anchor:** `references/living-tree.md` — schema v0.1, conventions (append-mostly, missing-optional, byte-identical carry-through, riskiest-only), and the read-side contract.

3. **Load the round's sources:**
   - `<scope>/decisions.json` (required) — `product_outcome`, `team`, `product`, `decided.opportunity`, `decided.solutions`, `decided.assumptions`, `decided.experiments`.
   - `<scope>/_working/chosen-opportunity-proposal.json` — `alternatives_considered[]` with `reason_not_picked`, plus excluded opportunities if carried.
   - `<scope>/_working/comparison-matrix.json` — `opportunities_excluded[]` (verdict + reason).
   - `<scope>/_working/top-three-solutions.json` and `<scope>/_working/solution-candidates.json` — picked vs not-picked solutions with roles.
   - `<scope>/_working/riskiest-assumptions.json` — riskiest assumptions with categories.
   - `<scope>/_working/validation-experiments.json` — the Test Cards (for the `experiment` text per assumption).

   Hard-exit (skill-standard ERROR block: one-line failure / Looked for / Found / Remedy) if `decisions.json` is missing or has no `decided.opportunity`. Every `_working/` source is optional — record what exists, list what was skipped in the completion summary.

4. **Build (or extend) `tree.json`.**
   - If `<scope>/tree.json` doesn't exist, initialize it per the schema anchor: `schema_version "0.1"`, `product`, `team`, `product_outcome` from `decisions.json`, empty `outcome_history`, empty `rounds[]`.
   - If it exists and its `product_outcome` differs from the current `decisions.json` value, move the old formulation to `outcome_history[]` with today's date and set the new one.
   - Determine `round_id` from `decided.opportunity.ratified`. If a round with that id already exists in `rounds[]`, you are **updating** that round (typical for recording experiment results later); otherwise append a new round entry. Set `recorded` to today's date (the date this skill runs, distinct from the ratification-derived `round_id`); on an update, leave the existing `recorded` unchanged.
   - Populate the round per the schema anchor: chosen opportunity (byte-identical), all opportunities with fates (`chosen` / `alternative` + reason_not_picked / `excluded_*` + reason), all 18 solutions with fates (`picked` + rationale / `not_picked`), and the riskiest assumptions with categories (`riskiest: true`, no `validation` yet).

5. **Record experiment results (interactive).** For each riskiest assumption without a `validation` entry, ask the trio — one assumption at a time, showing its text and its Test Card's test/metric/success criteria:
   - Was the experiment run? (skip if not — absence stays signal)
   - Result: `validated` / `invalidated` / `inconclusive`
   - Evidence: what was observed, with the numeric anchor where available
   The trio may answer for only some assumptions; record what they give, leave the rest open. If the user invoked this skill with results already stated in their message, use those directly and only ask about what's ambiguous.

6. **Write `<scope>/tree.json`.** Pretty-printed, missing-optional convention, nothing deleted. Upstream files are immutable.

7. **Summarize:** rounds in the tree, this round's counts (opportunities by fate, solutions picked, assumptions open/validated/invalidated), what was skipped for missing sources, and — if any assumption was `invalidated` — note explicitly that this is tree memory now: the next brainstorm/assumption pass must not retread it.

## Output principles

- **Ledger, not narrative.** Quotes, ids, titles, texts byte-identical from sources. Free-text only in `notes` (offer the trio one optional line) and `evidence`.
- **Append-mostly.** Never remove or rewrite prior rounds; updates only fill `validation` or extend the current round.
- **Riskiest-only assumptions** per the schema anchor.
- **Absence is signal.** Don't invent `inconclusive` for experiments that weren't run.
- **Output language:** prose matches the round's source language; schema fields and enums stay English.

## What this skill does NOT do

- Design experiments (assist 13) or judge results — the trio's read of the evidence is recorded, not second-guessed.
- Feed the tree into other skills — consumers read `tree.json` themselves per the anchor's read-side contract.
- Modify `decisions.json` or anything in `_working/`.
