---
title: "Discovery scope and path conventions for OST skills"
date: 2026-05-29
purpose: Defines the OST-discovery workspace hierarchy and the scope-resolution protocol that every OST skill follows. Referenced by all OST-* skills in their input/output sections so the protocol is documented once and reused.
tags: [discovery, workspace, ost, knowledge-anchor]

---

# Discovery scope and path conventions

OST skills read and write inside the `OST-discovery/` folder. The default layout is **flat, single-product, single-round**. Product and round nesting are opt-in and appear only when actually needed.

## Default layout

```text
OST-discovery/
├── product-context/              # product-outcome.md, experience-map.md (human-readable inputs)
├── decisions.json                # ratified decisions — the spine
├── 1-opportunity.md              # milestone: opportunity selected (gate 06)
├── 2-solutions.md                # milestone: top-3 solutions (gate 09)
├── 3-riskiest-assumptions.md     # milestone: riskiest assumptions (gate 12)
├── 4-experiments.md              # milestone: validation experiments (gate 13, terminal)
└── _working/                     # ALL phase JSON + ALL intermediate markdown (viewer data source)
```

The scope is `OST-discovery/` itself.

## Multi-product (opt-in)

When one repo holds more than one product, each product gets its own subfolder and the scope is the product folder. The internal layout is identical to the default:

```text
OST-discovery/
├── <product-a>/   # product-context/, decisions.json, 1..4-*.md, _working/
└── <product-b>/
```

## Multiple rounds (opt-in)

The first discovery round lives flat (no date folder). A dated round folder appears **only when a second round starts** for the same product: move the first round's milestones + `decisions.json` + `_working/` into `rounds/<first-date>/`, keep `product-context/` at the product level, and create the new round beside it.

```text
OST-discovery/[<product>/]
├── product-context/
└── rounds/
    ├── <first-round-date>/   # 1..4-*.md + decisions.json + _working/
    └── <second-round-date>/
```

## Scope resolution

A skill resolves its scope (the folder it reads/writes inside), first that exists:

1. Explicit `scope=` argument.
2. `OST-discovery/.current-scope` — one-line relative path to the active scope folder. Written only when product/round nesting exists.
3. Default: `OST-discovery/` when flat. If nesting exists, prompt, defaulting to the only product / latest round.

## Path conventions within a scope

- `product-outcome.md`, `experience-map.md` → `<scope>/product-context/`. When the scope is a `rounds/<date>/` folder, walk up to the product-level context: `<scope>/../../product-context/`.
- `decisions.json` → `<scope>/decisions.json`.
- Milestone docs → `<scope>/<n>-<name>.md` (see table).
- **Everything else — all JSON for every phase, all intermediate markdown — → `<scope>/_working/<artifact>.{md,json}`.**

## Canonical files

**Visible at scope root (milestones + spine):**

| Gate | File |
|------|------|
| Decision record (all gates write here) | `decisions.json` |
| Opportunity selected (06) | `1-opportunity.md` |
| Top-3 solutions (09) | `2-solutions.md` |
| Riskiest assumptions (12) | `3-riskiest-assumptions.md` |
| Validation experiments (13) | `4-experiments.md` |

**Plumbing — written to `<scope>/_working/`:**

| Step | File |
|------|------|
| Opportunity extraction | `opportunities-extracted.{md,json}` |
| Experience map import | `experience-map-extracted.{md,json}` |
| Experience map clustering | `experience-map-clustered.{md,json}` |
| Opportunity validation | `opportunities-validated.md` |
| Comparison matrix | `comparison-matrix.{md,json}` |
| Opportunity selection (machine JSON) | `chosen-opportunity-proposal.json` |
| Solution brainstorm | `solution-candidates.{md,json}` |
| Solution cluster | `clustered-solutions.{md,json}` |
| Top-3 selection (machine JSON) | `top-three-solutions.json` |
| Assumption generation | `assumptions.{md,json}` |
| Assumption categorization | `assumptions-categorized.{md,json}` |
| Riskiest assumptions (machine JSON) | `riskiest-assumptions.json` |
| Validation experiments (machine JSON) | `validation-experiments.json` |

The four gate phases write their machine JSON to `_working/` and their **self-contained** human-readable markdown to the scope root as `<n>-<name>.md`.

## Slug convention

Product and (when nested) round folder names are short, lowercase, ASCII-only slugs. For Swedish names, transliterate `å→a, ä→a, ö→o`. The full title lives in frontmatter inside the folder; the slug is for the path only.
