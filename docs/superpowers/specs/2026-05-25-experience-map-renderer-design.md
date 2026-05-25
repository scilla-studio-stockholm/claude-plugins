# Experience Map Renderer — Design Spec

**Date:** 2026-05-25
**Status:** Draft
**Scope:** New "Experience Map (Extracted)" tab in the OST Viewer

## Problem

The OST Viewer has no visualization for the extracted experience map (skill 01 output). The trio goes from a screenshot input to raw JSON/markdown, then sees nothing visual until the clustered experience map appears after skill 04. This gap means three skills run (extract, extract opportunities, validate) with no rendered view of the journey structure.

## Solution

Add a new tab to the existing OST Viewer (`templates/viewer/index.html`) that renders `experience-map-extracted.json` as a flowchart-style journey map. The design is based on a Claude Design prototype that visualizes Team Norrsken's Licenstilldelning journey.

## Audiences

- **Trio during workshop:** See their journey rendered live as they work through the OST process.
- **Trio between sessions:** Review the extracted journey map async.
- **Stakeholders:** Understand the shape of the journey at a glance without reading JSON.

## Design Principles

1. **Scannable at a glance.** Someone should see the shape of the journey in 5 seconds: how many phases, where complexity lives (many steps, branching), where it's simple (few steps, linear).
2. **Fit on screen.** The entire journey fits in one viewport — no scrolling. Phase columns adapt to the number of phases present.
3. **Every step connected.** Arrows show the complete flow — every step connects to the next. Decision branches show as labeled forks. No implied connections.
4. **Structural, not analytical.** This view shows phases, steps, and flow. No friction levels, no opportunities, no scores. Those come later in the OST process.

## Data Source

- **File:** `experience-map-extracted.json` (schema v0.1, output of skill 01 `OST-extract-experience-map`)
- **Tab appears only when** this file exists in the round directory's file listing.
- **Distinct from** the existing "Experience Map" tab which renders `experience-map-clustered.json` (schema v0.2, output of skill 04).

### Schema v0.1 → Renderer Format Transform

The renderer uses an internal format optimized for arrow routing (rows with explicit `next[]` edge pointers). A JS transform function converts v0.1 at load time:

**v0.1 input (from skill 01):**
```json
{
  "schema_version": "0.1",
  "team": "Norrsken",
  "title": "Licenstilldelning",
  "product_outcome": "Reduce manual steps...",
  "phases": [
    {
      "id": "fas-1",
      "order": 1,
      "name": "Förfrågan inkommer",
      "steps": [
        {
          "id": "step-1-1",
          "description": "Förfrågan mottagen"
        },
        {
          "id": "step-1-2",
          "description": "Tilldela säljare"
        }
      ]
    },
    {
      "id": "fas-3",
      "order": 3,
      "name": "Avtalsskrivning",
      "steps": [
        {
          "id": "step-3-1",
          "description": "Avtal upprättas",
          "decision_branches": [
            { "label": "Ny kund", "leads_to": "step-4-1" },
            { "label": "Befintlig kund", "leads_to": "step-5-1" }
          ]
        }
      ]
    }
  ]
}
```

**Renderer internal format (after transform):**
```json
{
  "title": "Licenstilldelning",
  "subtitle": "Reduce manual steps...",
  "meta": [
    { "label": "Faser", "value": "7" },
    { "label": "Steg", "value": "18" },
    { "label": "Beslutspunkter", "value": "4" }
  ],
  "phases": [
    {
      "num": 1,
      "title": "Förfrågan inkommer",
      "rows": [
        [{ "id": "step-1-1", "label": "Förfrågan mottagen", "next": [{ "to": "step-1-2" }] }],
        [{ "id": "step-1-2", "label": "Tilldela säljare", "next": [{ "to": "step-2-1" }] }]
      ]
    },
    {
      "num": 3,
      "title": "Avtalsskrivning",
      "rows": [
        [{ "id": "step-3-1", "label": "Avtal upprättas", "decision": true, "next": [
          { "to": "step-4-1", "label": "Ny kund" },
          { "to": "step-5-1", "label": "Befintlig kund" }
        ]}]
      ]
    }
  ]
}
```

**Transform logic (high-level; implementation details in the plan):**

1. Sort phases by `order`.
2. For each phase, create one row per step. When a decision step's branches both lead to steps within the same phase (parallel paths, e.g. SSO vs API), group those target steps into a single fork row.
3. Build `next` edges: steps with `decision_branches` become `decision: true` with one `next` entry per branch. Steps without branches get an implicit edge to the next step in sequence (same phase by array order, or first step of the next phase for the last step in a phase). Avoid duplicate edges when a decision branch already provides the cross-phase link.
4. Detect terminal/rejection steps: steps that have no outgoing edges and are the target of a decision branch (not the main flow) are marked `terminal: "reject"`.
5. Compute `meta` summary: count phases, total steps, steps with `decision_branches`.

## Layout

### Phase Columns

- CSS Grid: `grid-template-columns: repeat(N, 1fr)` where N = number of phases.
- Each phase column has a header (phase number + name) and a steps area below.
- Phase columns have subtly distinct background tints (desaturated, low-opacity) — not functional, just visual separation. Cycle through a small palette.
- Dashed border between columns.
- The grid fills the available viewport height (below the header/legend bars).

### Step Cards

- White background, subtle border, small border-radius.
- Content: step ID (monospace, faint) + step label (medium weight).
- Decision steps: blue left-border accent + "Beslut" flag badge.
- Hover: border-color shifts to accent, brutalist shadow offset, non-connected steps dim to 35% opacity.

### Fork Rows

When a decision creates parallel paths that both continue in the same phase (e.g. SSO and API in Fas 5), both step cards render side-by-side in a 2-column sub-grid within their row.

### Rejection/Terminal Paths

Steps that represent dead ends (e.g. credit check rejection) render:
- At the bottom of their phase column, visually separated.
- Dashed red/coral border, soft red background.
- Connected by a dashed red arrow routed through the column's right gutter.

## Arrow System

SVG overlay positioned absolutely over the map grid. Arrows are computed from DOM element positions after layout, recomputed on resize (ResizeObserver).

### Arrow routing rules

| Case | Route |
|---|---|
| Same column, sequential | Vertical line from bottom of source to top of target |
| Same column, reject path | Right-exit from source → column right gutter → down → left-enter to terminal node |
| Adjacent phase | Horizontal exit right → S-curve if vertical offset → enter left of target |
| Long cross-phase jump (>1 phase gap) | Right-exit → up to top channel → horizontal across phases → down → left-enter target |
| Same column, same row (fork merge) | Short horizontal connector |

### Arrow styling

- **Normal flow:** Solid line, accent color (blue-monday), arrowhead marker.
- **Rejection path:** Dashed line, reject color (red), arrowhead marker.
- **Branch labels:** Pill-shaped labels positioned on the arrow, accent-colored border.

### Legend Bar

A horizontal bar below the header showing the visual vocabulary:
- Flow arrow example + "Steg-flöde"
- Decision pill example + "Beslutsgren"
- Rejection arrow example + "Avslagsväg"

## Header

Metadata bar above the map:
- **Title:** `title` from JSON (split on em-dash for visual hierarchy if present).
- **Subtitle:** `product_outcome` from JSON.
- **Meta stats:** Phase count, step count, decision point count.

## Interaction

- **Hover highlighting:** Hovering a step dims all non-connected steps to 35% opacity. Connected = direct predecessors and successors via `next` edges.
- **No click actions** in v1. The map is read-only.

## Integration with Existing Viewer

### View Registry

Add a new entry to the `views` object in `index.html`:

```js
'experience-map-extracted.json': {
  label: 'Journey Map',
  render: renderJourneyMap
}
```

The label is "Journey Map" (not "Experience Map") to distinguish from the existing "Experience Map" tab that shows the clustered version.

### Rendering Approach

The journey map renderer needs fundamentally different layout from the other tabs:
- Other tabs use the viewer's scrollable body with card-based layouts.
- The journey map needs a full-viewport fixed-height grid with an SVG overlay.

When this tab is active, the renderer takes over the `#view-container` element and applies its own layout (flexbox column filling remaining viewport height). When switching away, the container returns to normal flow.

### CSS

All journey map styles are scoped under a `.journey-map` parent class to avoid conflicts with existing viewer styles. The renderer uses `--sc-*` tokens from `tokens.css` where suitable (font family, spacing, radii, shadows, blue-monday, grey scale) and defines a small set of view-specific variables for phase tints and arrow colors.

### Fixture Data

Add `experience-map-extracted.json` to the fixture directory (`fixtures/discovery/metria/opp-1/2026-05-25/`) for development and testing. Content: the Norrsken Licenstilldelning journey in v0.1 format.

## What This Spec Does NOT Cover

- Friction level visualization (not relevant at the extraction stage).
- Opportunity display (comes later, handled by the existing clustered view).
- The full Opportunity Solution Tree visualization (separate future work).
- Mobile/responsive layout (the viewer is a desktop workshop tool).
- Print styling for the journey map.

## Open Questions

None — all design questions resolved during brainstorming.
