# product-discovery

Claude Code plugin for **Opportunity Solution Tree (OST)** discovery, based on Teresa Torres' Continuous Discovery Habits framework. Guides a product trio (PM, UX designer, tech lead) from experience mapping through opportunity selection, solution brainstorming, assumption testing, and validation experiment design.

## Install

Requires the `scilla-studio` marketplace (private repo — needs `gh auth login`):

```
/plugin marketplace add scilla-studio-stockholm/claude-plugins
/plugin install product-discovery@scilla-studio
```

Updates pull automatically on session start (`autoUpdate: true`). Force-update mid-session:

```
/plugin update product-discovery@scilla-studio
```

## Prerequisites

Before starting, the product trio (PM, UX designer, tech lead) needs to have the following ready:

### Required

| What | Why | Format |
|---|---|---|
| **Product outcome** | Every downstream skill filters and scores against this. Without it, opportunities can't be evaluated. | A rough draft is fine — `OST-setup-product` will shape it into "Increase/Reduce [behavior] from [current] to [target] by [date]." |
| **Experience map** | Provides the journey structure for clustering opportunities into phases and steps. | Either a **screenshot** (PNG/JPG — `OST-extract-experience-map` converts it to structured data) or a **mental model** the trio can walk through in the setup interview. |
| **Cleaned interview transcripts** | Source material for extracting customer-voice opportunities. `OST-opportunity-extractor` reads these to find pain, friction, unmet needs, and workarounds. | Text files with speaker labels (e.g. `P01:` or `Interviewee:`). Raw transcripts from Otter/Zoom/etc. should be cleaned first — use `scilla-research:transcript-cleaner` if needed. |

### Optional (depends on starting point)

| What | When needed | Format |
|---|---|---|
| **Chosen opportunity ID & citation** | Only if the trio has *already decided* which opportunity to pursue and wants to skip the selection phase. | Opportunity ID (e.g. `opp-3-2`), journey phase, verbatim quote, source (interviewee + reference), and why it was chosen. |

### What you do NOT need upfront

The plugin generates everything else — validated opportunity lists, clustered maps, comparison matrices, solution candidates, assumption inventories, and experiment designs. The trio reviews and ratifies at HITL gates along the way.

## Skill flow

Each round produces a single `decisions.json` that accumulates the trio's ratified decisions at each gate. Intermediate artifacts (comparison matrices, brainstorm outputs, assumption inventories) are working documents consumed within their phase. See `knowledge/discovery/decisions-json-schema.md` for the schema.

Red diamonds = **required HITL** (workflow blocks until the trio acts). Yellow diamonds = **optional HITL** (trio can review/override but the workflow doesn't block).

```mermaid
flowchart TD
    subgraph phase0 ["Phase 0 — Setup"]
        setup["setup-product"]
        init["init-workspace"]
        setup -.->|"calls"| init
    end

    h_setup{{"HITL: trio confirms\noutcome, map, citation"}}:::required

    subgraph phase1 ["Phase 1 — Opportunities"]
        xmap["extract-experience-map"]
        extract["opportunity-extractor"]
        validate["validate-opportunities"]
        h_validate{{"HITL: trio reviews\nverdicts"}}:::optional
        cluster_o["cluster-opportunities"]
        h_cluster{{"HITL: trio parallel-\nclusters"}}:::optional
        compare["compare-opportunities"]
        select_o["select-opportunity"]
    end

    h_ratify{{"HITL: trio ratifies\ninto decisions.json"}}:::required

    subgraph phase2 ["Phase 2 — Solutions"]
        brainstorm["brainstorm-solutions"]
        cluster_s["cluster-solutions"]
        top3["select-top-three"]
    end

    h_top3{{"HITL: trio ratifies\ntop 3 into decisions.json"}}:::required

    subgraph phase3 ["Phase 3 — Assumptions"]
        gen["generate-assumptions"]
        categorize["assumption-categorizer"]
    end

    subgraph phase4 ["Phase 4 — Risk mapping"]
        riskiest["riskiest-assumptions"]
    end

    h_riskiest{{"HITL: trio reviews\nrisk calls, edits JSON"}}:::required

    subgraph phase5 ["Phase 5 — Validation"]
        experiment["validation-experiment-designer"]
    end

    h_run{{"HITL: trio picks order,\nruns experiments"}}:::required

    setup --> h_setup
    h_setup --> xmap
    h_setup --> extract
    extract --> validate --> h_validate --> cluster_o --> h_cluster --> compare --> select_o
    xmap --> cluster_o
    select_o --> h_ratify --> brainstorm
    brainstorm --> cluster_s --> top3
    top3 --> h_top3 --> gen
    gen --> categorize
    categorize --> riskiest
    riskiest --> h_riskiest --> experiment
    experiment --> h_run

    classDef required fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#991b1b
    classDef optional fill:#fef9c3,stroke:#ca8a04,stroke-width:1px,color:#854d0e
```

## Skills

The plugin ships 15 skills organized into five phases. Each skill outputs paired JSON + markdown (and sometimes HTML) that feeds into the next.

### Phase 0 — Setup

| Skill | What it does |
|---|---|
| `OST-setup-product` | Guided entrypoint. Walks the trio through product outcome, experience map, and opportunity citation to scaffold a ready-to-use `discovery/` workspace. Start here. |
| `OST-init-workspace` | Low-level scaffolding. Adds product, opportunity, or selection-round folders to an existing workspace. Called by `OST-setup-product` under the hood. |

### Phase 1 — Opportunities

| Skill | What it does |
|---|---|
| `OST-extract-experience-map` | Extracts a screenshot of an experience map into structured JSON + markdown (phases, steps, friction, decision branches). |
| `OST-opportunity-extractor` | Reads cleaned interview transcripts and pulls out verbatim customer-voice citat-stickies (pain, friction, unmet need, workaround). |
| `OST-validate-opportunities` | Quality-checks opportunities: approved, needs tweak, or solution in disguise. |
| `OST-cluster-opportunities` | Tags each opportunity to an experience-map phase/step and groups them into parent-child clusters. |
| `OST-compare-opportunities` | Scores all opportunities on 5 Torres criteria against the product outcome. Outputs a full matrix (JSON + markdown) and a swim-lane HTML card view for skimming at scale. |
| `OST-select-opportunity` | Proposes one opportunity to carry forward with rationale, alternatives considered, and evidence gaps. |

### Phase 2 — Solutions

| Skill | What it does |
|---|---|
| `OST-brainstorm-solutions` | Generates 18 divergent solution candidates via three role-diversified sub-agents (PM, UX, Tech Lead) over three rounds. |
| `OST-cluster-solutions` | Groups the 18 candidates into 3-5 thematic clusters. |
| `OST-select-top-three-solutions` | Picks the top 3 solutions ranked by outcome-impact probability. |

### Phase 3 — Assumptions

| Skill | What it does |
|---|---|
| `OST-generate-assumptions` | Decomposes top 3 solutions into assumptions via storymap, pre-mortem, and outcome-impact passes. |
| `OST-assumption-categorizer` | Tags each assumption into one of Cagan's five product-risk categories. |

### Phase 4 — Risk mapping

| Skill | What it does |
|---|---|
| `OST-riskiest-assumptions` | Scores assumptions on Bland's importance x evidence 2x2 and flags the riskiest (high importance, weak evidence). |

### Phase 5 — Validation

| Skill | What it does |
|---|---|
| `OST-validation-experiment-designer` | Designs a Bland Test Card per riskiest assumption (hypothesis, test, metric, success criteria) plus 2 alternative tests. Terminal skill — the trio picks execution order and runs. |

## Knowledge base

The `knowledge/` folder provides grounding material the skills reference at runtime:

- **`discovery/`** — Schemas and methodology for each OST phase (experience mapping, opportunity comparison, solution brainstorm, assumption generation, etc.)
- **`foundations/`** — Product operating model (Cagan), trio roles and responsibilities, operational practices

## Methodology sources

- Teresa Torres — *Continuous Discovery Habits* (OST framework, opportunity selection criteria)
- Marty Cagan — *Inspired* / *Empowered* (product operating model, five risk categories)
- David Bland — *Testing Business Ideas* (assumption risk mapping, Test Cards)

## Structure

```
product-discovery/
  .claude-plugin/plugin.json
  knowledge/
    discovery/          # phase-specific schemas and methodology
    foundations/        # product model and trio role definitions
  skills/
    00a-OST-init-workspace/
    00b-OST-setup-product/
    01-OST-extract-experience-map/
    ...
    13-OST-validation-experiment-designer/
```

Folder numeric prefixes are for human navigation. The `name:` field in each skill's `SKILL.md` is the canonical identifier used for invocation.
