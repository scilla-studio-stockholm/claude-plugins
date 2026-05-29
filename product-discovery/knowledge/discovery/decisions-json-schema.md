# decisions.json schema

Single file per discovery round. Accumulates only what the trio ratified at each HITL gate. Written incrementally — each section added when the trio signs off.

## Location

`OST-discovery/<round-folder>/decisions.json`

## Schema (v1.0)

```json
{
  "schema_version": "1.0",
  "product": "<product-slug>",
  "team": "<team-slug or null>",
  "round": "<round-folder-path>",
  "product_outcome": "<full outcome formulation>",
  "decided": {
    "opportunity": {
      "ratified": "<YYYY-MM-DD>",
      "id": "<opp-id>",
      "phase_id": "<experience-map phase>",
      "quote": "<verbatim customer quote>",
      "source": "<interviewee + reference>",
      "scores": {
        "outcome_alignment": "<strong|medium|weak|unknown|n/a>",
        "customer_importance": "<strong|medium|weak|unknown|n/a>",
        "market_size_frequency": "<strong|medium|weak|unknown|n/a>",
        "strategic_fit": "<strong|medium|weak|unknown|n/a>",
        "competitive_landscape": "<strong|medium|weak|unknown|n/a>"
      },
      "rationale": "<prose explaining the pick>",
      "evidence_gaps": [
        {
          "criterion": "<criterion key>",
          "gap": "<what is missing>",
          "why_relevant": "<why it matters for phase 2>"
        }
      ]
    },
    "solutions": {
      "ratified": "<YYYY-MM-DD>",
      "picks": [
        {
          "id": "<sol-id>",
          "title": "<solution title>",
          "description": "<solution description>",
          "rationale": "<2-3 sentences, outcome-mapping only>"
        }
      ]
    },
    "assumptions": {
      "ratified": "<YYYY-MM-DD>",
      "riskiest": [
        {
          "id": "<asm-id>",
          "solution_id": "<sol-id>",
          "text": "<what must be true>",
          "category": "<desirability|usability|feasibility|viability|other>",
          "importance": "high",
          "evidence": "weak",
          "rationale": "Importance=high (<reason>); evidence=weak (<reason>)."
        }
      ]
    },
    "experiments": {
      "ratified": "<YYYY-MM-DD>",
      "test_cards": [
        {
          "assumption_id": "<asm-id>",
          "solution_id": "<sol-id>",
          "test_type": "<e.g. Customer interview>",
          "hypothesis": "We believe that ...",
          "metric": "And measure ...",
          "success_criteria": "We are right if ... (<numeric anchor>)",
          "estimated_cost": "<low|medium|high>",
          "estimated_time": "<hours|days|weeks>"
        }
      ]
    }
  }
}
```

## Rules

- **`decided` starts empty.** Skills check for key presence to know if upstream is ready.
- **`solutions.picks` is always exactly 3.**
- **`assumptions.riskiest` contains only assumptions where importance=high AND evidence=weak.**
- **`experiments.test_cards` has one entry per riskiest assumption.**
- **`ratified` is the date the trio signed off, not the date the skill ran.**
- **No alternatives, no process metadata, no source filenames.** The file is self-contained. Working artifacts (comparison matrices, brainstorm lists, clustering) stay as markdown in `_working/`.
- **`success_criteria` must contain at least one numeric anchor** (regex-enforced).

## What this replaces

Previously each skill wrote its own JSON file. Those intermediate files move to `_working/` and are treated as disposable process artifacts. `decisions.json` is the only structured file that persists as the round's decision record.

## What this does NOT replace

- **The Opportunity Solution Tree** (future artifact) — a living, cross-round accumulation of all validated opportunities under a product outcome. `decisions.json` records one path through the tree per round.
- **Working markdown** — comparison matrices, brainstorm outputs, assumption inventories. These remain as human-readable working documents during each phase.
