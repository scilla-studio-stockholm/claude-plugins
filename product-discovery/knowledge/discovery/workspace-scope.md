---
title: "Discovery scope and path conventions for OST skills"
date: 2026-05-15
purpose: Defines the discovery-workspace hierarchy and the scope-resolution protocol that every OST skill follows. Referenced by all OST-* skills in their input/output sections so the protocol is documented once and reused.
tags: [discovery, workspace, ost, knowledge-anchor]

---

# Discovery scope and path conventions

OST skills read and write inside the `discovery/` hierarchy. Two layout modes are supported:

## Multi-product mode (default)

For organisations with multiple teams and/or products in one repo:

```text
discovery/
├── .current-scope                            # one-line file; relative path to the active round folder
├── <team>/                                   # e.g., fast, norrsken
│   ├── _team-context/                        # team-level docs (optional)
│   └── <product>/                            # e.g., fsok
│       ├── _product-context/                 # product-outcome.md, experience-map.{md,json}
│       ├── opportunity-selection/<YYYY-MM-DD>/   # phase A round: validate / compare / select
│       └── opportunities/<opp-slug>/         # ratified opportunity
│           ├── chosen-opportunity.md         # persistent context
│           ├── ratifications.md              # optional trio log
│           └── <YYYY-MM-DD>/                 # phase B round: brainstorm → experiments
```

## Single-product mode

For small repos with exactly one product. The `<team>/<product>/` nesting is dropped:

```text
discovery/
├── .current-scope
├── _product-context/                         # product-outcome.md, experience-map.{md,json}
├── opportunity-selection/<YYYY-MM-DD>/       # phase A round
└── opportunities/<opp-slug>/                 # ratified opportunity
    ├── chosen-opportunity.md
    ├── ratifications.md                      # optional
    └── <YYYY-MM-DD>/                         # phase B round
```

Both modes use the same relative-path math for scope resolution (see below), so phase skills work identically regardless of which mode the repo uses. Only the absolute path differs.

Filenames inside a round folder drop the date suffix (date lives on the round folder). Underscore-prefixed folders (`_team-context/`, `_product-context/`) are read-only context for skills.

## Scope resolution

A skill resolves its scope (the round folder it reads and writes inside) in this order, taking the first that exists:

1. Explicit `scope=` argument passed by the user when invoking the skill.
2. `discovery/.current-scope` — a one-line file containing a relative path from the repo root to the active round folder.
3. Prompt the user, defaulting to the latest dated round under the most recently touched opportunity, or a new round dated today if no scope exists yet for the target opportunity.

A scope is an **opportunity-selection round** if its path contains `/opportunity-selection/`, otherwise a **discovery round** if it contains `/opportunities/`.

## Context walk-up

From a discovery scope ending in `opportunities/<opp>/<YYYY-MM-DD>/`:

- `chosen-opportunity.md` → `<scope>/..`
- `ratifications.md` → `<scope>/..` (optional)
- `decisions.json` → `<scope>/decisions.json` (same round folder; no walk-up needed)
- `product-outcome.md`, `experience-map.{md,json}` → `<scope>/../../../_product-context/`
- Previous-step artifacts in the same round → `<scope>/<artifact>.{md,json}`; if missing, walk siblings (other dated rounds under the same opportunity) in date-descending order to find the most recent preceding run.

From an opportunity-selection scope ending in `opportunity-selection/<YYYY-MM-DD>/`:

- `product-outcome.md`, `experience-map.{md,json}` → `<scope>/../../_product-context/`
- No `chosen-opportunity.md` lookup — opportunity-selection rounds produce the proposal `chosen-opportunity-proposal.{md,json}` inside their own round folder.

The walk-up depths (three levels for discovery, two for opportunity-selection) are identical in both layout modes because the `<team>/<product>/` nesting (when present) sits above both `_product-context/` and the round folder. Skills do not need to know which mode the repo uses.

## Canonical filenames inside a round

| Step | Filename |
|------|------|
| Decision record | `decisions.json` |
| Opportunity extraction | `opportunities-extracted.{md,json}` |
| Experience map import | `experience-map-extracted.{md,json}` |
| Experience map clustering | `experience-map-clustered.{md,json}` |
| Opportunity validation | `opportunities-validated.md` |
| Comparison matrix | `comparison-matrix.{md,json}` |
| Opportunity selection (proposal) | `chosen-opportunity-proposal.{md,json}` |
| Solution brainstorm | `solution-candidates.{md,json}` |
| Solution cluster | `clustered-solutions.{md,json}` |
| Top-3 selection | `top-three-solutions.{md,json}` |
| Assumption generation | `assumptions.{md,json}` |
| Assumption categorization | `assumptions-categorized.{md,json}` |
| Riskiest assumptions | `riskiest-assumptions.{md,json}` |
| Validation experiments | `validation-experiments.{md,json}` |

The ratified chosen-opportunity is `chosen-opportunity.md` at the opportunity-folder root. The proposal produced by the selector inside an opportunity-selection round is `chosen-opportunity-proposal.md`. The two file names differ deliberately so a ratified record cannot be silently overwritten.

**Deprecated as skill inputs (read from `decisions.json` instead):**
- `chosen-opportunity.md` — skills 07, 08, 09 previously read this; now read `decided.opportunity` from `decisions.json`. The file may still exist as a human-readable reference.
- `ratifications.md` — skill 10 previously checked this for top-3 ratification; now checks `decided.solutions` in `decisions.json`. The file is no longer maintained.

## Slug convention

Product and opportunity folder names are short, lowercase, ASCII-only slugs. For Swedish-named opportunities, transliterate `å→a, ä→a, ö→o`. The full Swedish title lives in frontmatter inside the folder; the slug is for the path only.

## Round-folder date convention

A round folder is named after the date its **first step** was run. Opportunity-selection: opportunity-extraction date. Discovery: solution-brainstorm date.
