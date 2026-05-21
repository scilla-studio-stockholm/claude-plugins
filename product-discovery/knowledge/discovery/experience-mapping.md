---
title: Experience mapping for OST opportunity work
date: 2026-05-09
purpose: Reference for how product trios map a user experience as input to opportunity-selection. Documents the structural pattern observed in trio practice and specifies the JSON schema that AI assists consume.
tags: [experience-mapping, ost, opportunity-space, customer-journey, schema]

---

# Experience mapping for OST opportunity work

## What this document is

This is a first version (v0.1) reference for experience mapping as it is practiced by Metria product trios in the OST opportunity space. It is grounded in observed trio artifacts, not a fully-developed methodology. It will evolve as more trios complete maps.

It serves two readers:

- **Trios** who need to understand what an experience map should contain and why
- **AI assists** that consume the map as JSON

## Where it sits in the OST flow

In Teresa Torres' Opportunity Solution Tree, the opportunity space layer sits between the desired outcome and the solution space. Before a trio can compare opportunities meaningfully, the opportunities need to be placed in the context of the user experience they belong to.

The experience map is what gives that context. It captures **how a user moves through the experience where the desired behavior change should happen**, and lets the trio cluster opportunities against the phases of that journey.

The map is a prerequisite for the opportunity-selection process. It is created by the trio before AI assists are invoked. AI does not design the phases. It reads what the trio has drawn and produces a structured representation downstream skills can consume.

## Structural pattern

The pattern below is distilled from current trio practice. The reference example is Team Norrsken's "Licenstilldelning" map (`knowledge/discovery/Trion - Team Norrsken - Opportunity Solution Tree - Licenstilldelning.jpg`).

A complete map contains:

### Header

- **Product outcome.** The full outcome formulation the trio works against. Anchored in `knowledge/discovery/product-outcomes-i-olika-skeden.md`.
- **Narrativ (optional).** A short text explaining the intent behind the outcome. Useful when the outcome alone does not communicate the why.

### Användarresa (user journey)

A horizontal sequence of **phases**. The number of phases is variable. The trio decides how to slice the journey, what to call the phases, and where the boundaries sit. Phases are not formulaic.

Within each phase, the trio places **steps**. A step is a concrete action or event in the journey. Steps can branch: a single phase may contain decision points that route the user through different paths (Ny vs Befintlig kund, Ja vs Nej, API vs SSO vs Webb).

Each phase carries a **friction level** indicating how much pain or complexity the trio observes there. Friction is encoded as one of three levels:

- `low` — runs smoothly today, low pain
- `medium` — friction exists but is not blocking
- `high` — significant pain, friction, or complexity

In the Norrsken example, friction level is shown as color (green, yellow, orange, red gradient). The schema collapses this to three named levels.

### Opportunities

Citat-stickies placed under the phase they belong to. Each opportunity follows the citat-stickie format from `knowledge/discovery/opportunity-citation-format.md`: a quote, source, and any tweaks marked with brackets.

Opportunities live inside their phase, not as a separate root list. This means a downstream clusterer skill gets phase membership for free.

### Extensions (team-specific)

Some trios add team-specific context that is useful for them but not part of the canonical pattern. Norrsken added a `systems_in_use` list. The schema accommodates this in an open `extensions` container. Other trios can add their own without bloating the core.

## How a trio creates a map

This part is intentionally light. Trio practice is still evolving and over-specifying it would be premature. What is consistent across observations:

1. Start from the product outcome. The map should cover the part of the user experience where the outcome's behavior change applies.
2. Sketch phases first. Slice the journey into phases that feel right to the trio. Three to seven phases is typical based on current examples.
3. Fill steps inside each phase. Use what you have learned from interviews. Mark decision points where the path branches.
4. Mark friction levels per phase. Use the green-yellow-orange-red gradient or write the level directly.
5. Cluster opportunities. Place each citat-sticky under the phase it belongs to.

The map is a working artifact, not a polished deliverable. "Crummy first draft" applies here as it does to OST in general.

## JSON schema (v0.2)

This is the contract that AI assists 2 (OST-extract-experience-map) and 3b (OST-cluster-opportunities) produce. Downstream skills (steg 4, 5) consume it. v0.2 is backward-compatible with v0.1: any well-formed v0.1 file with non-empty `steps[]` is also valid v0.2.

```json
{
  "schema_version": "0.2",
  "team": "string (e.g., 'Norrsken')",
  "title": "string (e.g., 'Licenstilldelning')",
  "product_outcome": "string (full outcome formulation)",
  "narrativ": "string (optional motivating text)",
  "phases": [
    {
      "id": "string (e.g., 'fas-1', or 'fas-0-unphased' for the synthetic out-of-phase bucket)",
      "order": 1,
      "name": "string (trio-designed phase name)",
      "friction_level": "low | medium | high (optional; omit key if not observed)",
      "steps": [
        {
          "id": "string (e.g., 'step-1-1')",
          "description": "string (optional; omit key if not observed)",
          "decision_branches": [
            {
              "label": "string (e.g., 'Ny', 'Befintlig', 'Ja', 'Nej')",
              "leads_to": "string (step id or short description)"
            }
          ]
        }
      ],
      "opportunities": [
        {
          "id": "string (e.g., 'opp-1-1', or 'opp-0-1' for unphased)",
          "quote": "string (verbatim with bracketed tweaks)",
          "source": "string (interview ref + approximate time)",
          "tweaks": ["string (optional list of tweak notes)"],
          "verdict": "approved | needs_tweak | solution_in_disguise (optional; carried from OST-validate-opportunities)",
          "step_id": "string (optional; a step.id within the same phase, set when the citation makes the step explicit)",
          "parent_id": "string (optional; an opportunity.id within the same phase that is the broader parent; depth at most 2)",
          "out_of_phase_reason": "string (optional; required by skill body whenever phase.id is 'fas-0-unphased')"
        }
      ]
    }
  ],
  "extensions": {}
}
```

### Field notes

- **`friction_level`** is an enum, not a numeric scale. Three levels avoids false precision.
- **`decision_branches`** sit on step level. Sufficient for the patterns observed so far. Extend if a trio needs deeper trees.
- **`opportunities`** are nested inside `phases`. This is intentional. It enforces phase membership and matches the visual layout. The `opportunities[]` array is populated by a downstream workflow (`OST-cluster-opportunities`), not by `OST-extract-experience-map`. The map-extraction skill always omits the key, leaving the slot for the clusterer to fill later.
- **`extensions`** is an open container for team-specific data. Norrsken's `systems_in_use` lives here. Anything trio-unique goes here, not in the core.
- **`step_id`** (v0.2, on opportunity items) points at a `step.id` within the same phase. Set only when the citation makes the step explicit (a quote naming a system or event that maps 1:1 to a step). Otherwise omit per the missing-optional convention. Not used for `fas-0-unphased`.
- **`parent_id`** (v0.2, on opportunity items) points at an `opportunity.id` within the same phase that is the broader parent. Top-level (parent) opportunities omit the key; children carry it. Depth is capped at 2 — a child cannot itself be a parent. Enforced by the `OST-cluster-opportunities` skill, not by the schema.
- **`verdict`** (v0.2, on opportunity items) carries the per-opportunity verdict from `OST-validate-opportunities`. Always written by `OST-cluster-opportunities`. Stays optional in the schema for forward compatibility (e.g., a trio that bypasses 3a). Downstream comparator filters on this.
- **`out_of_phase_reason`** (v0.2, on opportunity items) is a short AI-written explanation of why an opportunity didn't fit any journey phase. Schema-optional, but `OST-cluster-opportunities` requires it whenever `phase.id == "fas-0-unphased"`. Omitted for any opportunity in a real phase.
- **Empty `steps[]`** (v0.2 widening) is allowed, but only meaningful for the synthetic `fas-0-unphased` phase. A real phase with empty `steps[]` is still a hard-exit signal for `OST-extract-experience-map`. The relaxation only matters for the unphased bucket the clusterer creates.
- **Missing optional fields.** When a skill cannot observe an optional field on the source map, it omits the key from the JSON entirely rather than writing `null`. Downstream skills must treat key absence as the missing-value signal. Optional fields: `narrativ`, `phases[].friction_level`, `phases[].steps[].description`, `phases[].steps[].decision_branches`, `phases[].opportunities`, `phases[].opportunities[].tweaks`, `phases[].opportunities[].step_id`, `phases[].opportunities[].parent_id`, `phases[].opportunities[].verdict`, `phases[].opportunities[].out_of_phase_reason`, `extensions`.

## Reference example: Team Norrsken, Licenstilldelning

Source artifact: `knowledge/discovery/Trion - Team Norrsken - Opportunity Solution Tree - Licenstilldelning.jpg`

Observed structure:

- **Product outcome:** Reduce manual steps and actors needed to assign a license for an IPM customer
- **Phases (7):** Förfrågan inkommer, Behovsanalys & avtal, Avtalsskrivning, Kreditkontroll & ekonomi, Licens-upplägg, Rabatter, Aktivering & leverans
- **Friction gradient:** Phase 1 low, phases 2-3 low/medium, phase 4 medium, phases 5-6 high, phase 7 low
- **Decision branches observed:** Ny vs Befintlig kund (phase 2), Rating under vs över 40 (phase 4), API vs SSO vs Webb (phase 5), Rabatt avtalad? Ja/Nej (phase 6), Finns licenspaket i Delfi? Ja/Nej (phase 5)
- **Extension data:** `systems_in_use` list including Outlook, Freshdesk, Credit Safe, SalesForce, Admin V2, Debiteringssystemet, KeyCloak, Delfi, Vendure, Jira, Xledger, Excel, Teams, Confluence

## Open questions

- Is friction-level set per phase or per step? Currently per phase, matching the Norrsken example. If finer granularity is needed, friction can move to step level later.
- Should the schema represent the journey's overall starting and ending state? Not in v0.1. Add if trios show a need.
- ~~Should opportunities carry a `journey_step_id` for finer placement than phase?~~ Answered in v0.2: added as `step_id`, scoped within phase, set only when the citation makes the step explicit.

## Evolution

This document evolves as more trios complete maps. When a new pattern emerges that does not fit the current version, the schema bumps with a note in this section. Trio-specific patterns stay in `extensions`.

**v0.2 (2026-05-09):** Added four optional fields on `phases[].opportunities[]` items (`step_id`, `parent_id`, `verdict`, `out_of_phase_reason`) and widened `phases[].steps[]` to allow empty arrays. The new fields exist to support `OST-cluster-opportunities` (assist 3b): step-level granularity, within-phase hierarchy, verdict carry-through, and a synthetic `fas-0-unphased` bucket for opportunities that don't fit any real phase. Backward-compatible with v0.1.
