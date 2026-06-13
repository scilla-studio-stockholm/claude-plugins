# The living tree (`tree.json`)

The third layer of the OST artifact model: the **cross-round memory** of a product's discovery work. Layer 1 is the disposable working material in `_working/`; layer 2 is `decisions.json`, the ratified record of *one* round. `tree.json` is what survives across rounds — the accumulated Opportunity Solution Tree with the fate of everything the trio has considered, tested, validated, or killed.

Location: `<scope>/tree.json` (scope root, next to `decisions.json`). It is append-mostly: each round adds one entry to `rounds[]`; experiment results update entries in place. Nothing is ever deleted — superseded knowledge gets a `status`, not removal.

## Why it exists

- **The next round starts smarter.** Skills and workflows that read the tree know which opportunities were already invalidated, which solutions were killed and why, which assumptions already have evidence. The brainstorm doesn't retread dead solutions; the validator can flag "this opportunity lost in round 2 on weak customer-importance".
- **Any agent can orient from one file.** A facilitator, `/pickup`, or a future agent reads `tree.json` instead of re-reading a round's worth of `_working/`.
- **Experiment results have a home.** Assist 13 ends with a run-list; without the tree, what the trio *learned* from running the experiments never makes it back into the corpus.

## Schema v0.1

```json
{
  "schema_version": "0.1",
  "product": "string (slug, carried from decisions.json)",
  "team": "string",
  "product_outcome": "string (current formulation; superseded ones move to outcome_history)",
  "outcome_history": [ { "formulation": "string", "superseded": "YYYY-MM-DD" } ],
  "rounds": [
    {
      "round_id": "string (the round's ratification date, YYYY-MM-DD; suffix -2 etc. on collision)",
      "recorded": "YYYY-MM-DD",
      "chosen_opportunity": { "id": "...", "phase_id": "...", "quote": "...", "source": "..." },
      "opportunities": [
        { "id": "...", "quote": "...", "phase_id": "...",
          "fate": "chosen | alternative | excluded_needs_tweak | excluded_solution_in_disguise",
          "reason": "string (reason_not_picked or exclusion reason; omit for chosen)" }
      ],
      "solutions": [
        { "id": "...", "title": "...", "generating_role": "...",
          "fate": "picked | not_picked",
          "reason": "string (rationale for picked; omit otherwise)" }
      ],
      "assumptions": [
        { "id": "...", "text": "...", "category": "desirability | usability | feasibility | viability | ethical_other",
          "riskiest": true,
          "validation": {
            "experiment": "string (the test run, from the Test Card)",
            "result": "validated | invalidated | inconclusive",
            "evidence": "string (what was observed, with the numeric anchor where available)",
            "date": "YYYY-MM-DD"
          } }
      ],
      "notes": "string (optional trio free-text: what this round taught us)"
    }
  ]
}
```

Conventions:
- **Missing-optional convention** as everywhere in the workspace: omit unset optional keys, never `null`.
- **`validation` is absent until results are recorded.** A riskiest assumption without `validation` is an open question — that absence is signal.
- **Only riskiest assumptions are carried** into `rounds[].assumptions[]` (`riskiest: true` always; non-riskiest assumptions stay in the round's `_working/` and are not tree memory). Rationale: the tree records what the trio acted on.
- **Quotes, ids, titles are byte-identical** to their `decisions.json` / `_working/` sources. The tree is a ledger, not a paraphrase.
- **Fates are terminal per round.** A previously `excluded` opportunity may be chosen in a later round — that's a new entry in the new round, not an edit of the old one.

## Read-side contract

Skills/workflows that consume the tree (when `<scope>/tree.json` exists):
- **Facilitator orientation:** summarize prior rounds (chosen opportunity + validated/invalidated assumptions) in one breath before proposing the next move.
- **Opportunity validation/selection (assists 03, 05, 06):** may flag, never auto-exclude — "opp similar to round-N's chosen/killed opportunity X" is advisory context for the trio.
- **Solution brainstorm (assist 07):** prior `not_picked` solutions and `invalidated` assumptions are anti-context — new ideas must not retread them unless the idea explicitly addresses why the prior one failed.
- **Assumption generation (assist 10):** assumptions already `validated` count as evidence (cite the round); already `invalidated` ones must not silently reappear.

Absence of `tree.json` is never an error — every consumer treats it as optional context.
