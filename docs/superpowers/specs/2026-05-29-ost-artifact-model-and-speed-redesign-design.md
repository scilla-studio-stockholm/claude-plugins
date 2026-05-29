# OST Redesign: Artifact Model, Folder Structure & Speed

**Date:** 2026-05-29
**Status:** Design approved, pending spec review
**Scope:** Track A (artifact + folder redesign) in full detail; Track B (speed) as defined levers + measure-first rule, to be planned in its own spec.

## Background

A usability test of the full `product-discovery/` OST (Opportunity Solution Tree) skill set (15 skills, phases 00→13) surfaced four findings:

1. **Unintuitive folder structure** — users landing in another person's repo don't understand why `discovery/` is named/organized as it is or what it contains.
2. **Too many files** — a full run produces ~27 files (nearly every phase writes a paired JSON + markdown, plus a shared `decisions.json`). The output model needs rethinking, not just tidying.
3. **Output quality is excellent and must be preserved** — output exceeded participant expectations; this is a constraint on every change, not a task.
4. **Skills are slow** — suspected cause is context volume.

### Diagnosis (from code exploration)

- **Files:** ~27 per full run, dominated by the JSON+markdown pairing on all 13 content phases.
- **Folders:** two modes (single- vs multi-product), deep `<team>/<product>/…` nesting, `<YYYY-MM-DD>` round folders, `_underscore` context folders, slug naming.
- **Slowness sources:** phases **07 and 10 each spawn 9 sub-agents**; full **role-anchor files (~300+ lines) are injected into every sub-agent prompt**; the **~3,623-line knowledge base is re-read by every skill**; large upstream JSONs (e.g. 54 raw assumptions) are **re-parsed by each downstream skill**.

### Central tension

The two mechanisms responsible for the surprising quality — **role-diversified divergence** (07's 3 roles × 3 rounds = 18 candidates; the multi-method assumption passes) and **rich grounding context** (Torres principles, role anchors, product outcome, experience map fed deeply into each step) — are the *same* mechanisms that make it slow. Therefore **speed work may not cut divergence or thin grounding depth.** Speed comes only from quality-neutral levers.

## Decisions

- **Framing:** two tracks — (A) redesign the artifact/workspace model (fixes findings #1 and #2 together), then (B) a dedicated speed pass (#4). Quality (#3) is a guardrail throughout.
- **Consumption surfaces to preserve:** both the **OST Viewer (HTML, rendered from JSON)** and **direct markdown reading** are in real use. Neither may be broken.
- **Artifact approach:** Approach 1 — milestone / plumbing split (chosen over a single living document and over JSON-only).
- **Folder approach:** simplify the structure itself (chosen over README-only or rename-only).
- **Quality drivers to treat as untouchable:** role-diversified divergence and rich grounding context.

## Track A — Artifact Model

### Two layers

- **Machine layer.** Every skill writes its JSON exactly as today (the viewer needs it; downstream skills read it). All JSON lives in a hidden **`_working/`** folder.
- **Human layer.** Only *milestone* phases write a markdown document a person opens. These sit at the round root.

### Classifying principle

> A phase persists a visible, human-readable artifact **if and only if** it is a HITL ratification gate or foundational context. Everything between gates is plumbing.

This maps exactly onto the four existing trio decision points (phases 06, 09, 12, 13) plus the foundational context (setup + experience map).

### Per-phase classification

| Phase | Output today | New role | Visible location |
|-------|-------------|----------|------------------|
| 00b setup / 01 experience-map | context + `experience-map.{md,json}` | Foundation | ✅ `product-context/` |
| 02 extract opportunities | `opportunities-extracted.md` | Plumbing | `_working/` |
| 03 validate opportunities | `opportunities-validated.md` | Plumbing | `_working/` |
| 04 cluster opportunities | `experience-map-clustered.{md,json}` | Plumbing (viewer reads JSON) | `_working/` |
| 05 compare opportunities | `comparison-matrix.{md,json}` | Plumbing (viewer reads JSON) | `_working/` |
| **06 select opportunity** | proposal + `decisions.json` | **Milestone (gate)** | ✅ `1-opportunity.md` |
| 07 brainstorm solutions (18) | `solution-candidates.{md,json}` | Plumbing (the slop) | `_working/` |
| 08 cluster solutions | `clustered-solutions.{md,json}` | Plumbing (viewer reads JSON) | `_working/` |
| **09 top-3 solutions** | proposal + `decisions.json` | **Milestone (gate)** | ✅ `2-solutions.md` |
| 10 generate assumptions | `assumptions.{md,json}` | Plumbing | `_working/` |
| 11 categorize assumptions | `assumptions-categorized.{md,json}` | Plumbing | `_working/` |
| **12 riskiest assumptions** | proposal + `decisions.json` | **Milestone (gate)** | ✅ `3-riskiest-assumptions.md` |
| **13 validation experiments** | `validation-experiments.{md,json}` | **Milestone (terminal)** | ✅ `4-experiments.md` |

**Result:** the round root goes from ~27 scattered files to **4 milestone docs + `decisions.json` + `product-context/`**, with all JSON and intermediates in `_working/`. Divergence and grounding are untouched — they simply stop cluttering the visible tree. The viewer renders everything because it reads JSON from `_working/`.

### Self-contained milestone principle

Hiding plumbing is safe **only if** nothing a human needs for a decision is buried. Therefore each milestone doc embeds enough of its upstream plumbing's reasoning to stand alone — a reader never opens `_working/` to understand or challenge a decision.

- **`1-opportunity.md`** (phase 06): proposed opportunity + rationale; **every other approved opportunity as an "alternative considered" with its why-not**; the decision-relevant slice of the comparison matrix (what lost, on which criteria); carried-forward evidence gaps. The matrix JSON stays plumbing; its decision content is promoted into the proposal.
- **`2-solutions.md`** (phase 09): the top-3 *and* the clusters/candidates that didn't make it, with why-not.
- **`3-riskiest-assumptions.md`** (phase 12): the riskiest assumptions *against* the full categorized set.
- **`4-experiments.md`** (phase 13): the chosen tests *and* the alternatives.

## Track A — Folder Structure

### Before

```
discovery/
├── .current-scope
└── <team>/<product>/
    ├── _product-context/
    ├── opportunity-selection/<YYYY-MM-DD>/   ← ~12 files
    └── opportunities/<slug>/<YYYY-MM-DD>/     ← ~15 files
```

### After

```
discovery/
├── product-context/              ← inputs (outcome + experience map)
│   ├── product-outcome.md
│   └── experience-map.md (+ .json)
├── decisions.json                ← the spine: ratified decisions
├── 1-opportunity.md              ← gate 06
├── 2-solutions.md                ← gate 09
├── 3-riskiest-assumptions.md     ← gate 12
├── 4-experiments.md              ← gate 13 (terminal)
└── _working/                     ← all JSON + intermediates (viewer reads here)
```

### Changes

- **Drop the two-mode branching.** Single-product is the default. Multi-product becomes an explicit opt-in nested folder *only when actually needed* (YAGNI for most users).
- **Drop date-stamped round folders** for the first/only round. A dated subfolder appears only when a *second* round starts.
- **Drop the `_underscore` context convention** in favor of a plain `product-context/` name.
- **Numbered `1-`…`4-` milestone docs** make the journey order self-evident.
- **Optional, low-cost orientation aid:** a one-paragraph header (in `decisions.json` or a tiny `discovery/README.md`). Marked optional; structural simplification leads.

## Track B — Speed (quality-neutral levers only)

Hard rule: **no cutting divergence (07's 18 candidates, the method passes) and no thinning grounding depth.** Levers:

1. **Measure first.** Instrument one full run to locate time: sub-agent generation vs. context loading vs. file I/O. Don't optimize blind. Some slowness is inherent to generating 18 grounded candidates — that is not fought; the expectation is set honestly.
2. **Compress grounding, don't remove it.** Rewrite role-anchor and knowledge files to be dense — same framework and substance, fewer tokens of prose. Quality-neutral, verified by the golden-run check.
3. **Stop re-reading the knowledge base every skill.** Pass needed context forward through `decisions.json` structured fields instead of re-loading ~3,623 lines per phase.
4. **Kill redundant JSON re-parsing.** Downstream skills (11, 12) read structured `decisions.json` fields instead of the full upstream item-level JSON.
5. **Track A dividend.** Moving intermediates to `_working/` and surfacing only milestones already shrinks per-phase context — a speed win before Track B starts.

## Sequencing & Quality Guardrail

1. **Track A first** — biggest user-visible win; partially relieves speed.
2. **Golden-run regression check** — run the **same real input** through old vs. new and compare output quality, before *and* after each track. This *proves* divergence + grounding survived rather than assuming it. It is the gate between tracks.
3. **Track B second** — measure, apply quality-neutral levers, re-run the golden check.
4. **Ship ticket-first** — Linear → branch → PR → review per the standard workflow (this repo has a GitHub remote).

## Out of Scope

- Track B detailed implementation plan (own spec, after a golden-run baseline exists).
- Building the cross-round "living OST" artifact (separate design).
- Viewer redesign beyond pointing it at `_working/` for JSON.
- Any change that reduces sub-agent count, brainstorm rounds, or grounding depth.

## Risks

- **Migration of existing workspaces** to the new folder layout — needs a migration note or a one-time mover; existing in-flight rounds must not break.
- **Viewer data-path change** — the viewer's `serve.py` / fetch paths must be updated to read JSON from `_working/`; this is a required, tracked part of Track A, not optional.
- **Golden-run subjectivity** — "quality preserved" needs a concrete comparison rubric (divergence breadth, grounding fidelity, gate-doc completeness) defined before the baseline run.
