# OST Viewer Template — Design Spec

**Linear ticket:** [SCI-21](https://linear.app/scilla/issue/SCI-21/design-discovery-for-html-output-generation-in-ost-skills-round)

**Goal:** Replace per-skill inline HTML generation with a standalone viewer app that renders skill JSON output using the scilla.studio brand design system. Skills write JSON only; the viewer handles all presentation.

**Architecture:** Client-server split. A lightweight Python server (stdlib only) serves the viewer from the plugin directory and data from the workspace. The trio sees a URL; the designer edits HTML/CSS and refreshes.

## Core principles

- **Skills write JSON, never HTML.** The viewer is the only thing that renders presentation.
- **Design iteration without running skills.** Open the viewer, point it at any round folder with JSON, edit CSS, refresh.
- **Self-updating.** The viewer lives in the plugin repo. Plugin autoUpdate delivers design changes to all trios on session start. No copying into workspaces.
- **Scilla brand.** All styling uses `--sc-*` CSS custom properties from `tokens.css` (vendored from `scilla-design-system`). Inter font family, scilla color palette, spacing scale, shadow system.
- **Offline-capable after first load.** Once the server is running, no external network requests. Google Fonts loaded once; viewer works without them (Inter falls back to system sans-serif).

## File structure

```
product-discovery/
  templates/
    serve.py                  # dual-mount Python server (~40 LOC)
    viewer/
      index.html              # the viewer app (all views, CSS, JS in one file)
      tokens.css              # vendored from scilla-design-system/tokens.css
```

## Server (`serve.py`)

Stdlib-only Python script. Two mount points:

| URL path | Serves from |
|---|---|
| `/_viewer/*` | `<plugin>/templates/viewer/` |
| `/*` | `<workspace>/discovery/` |

**CLI:**
```
python3 serve.py --templates /path/to/plugin/templates/viewer --data /path/to/workspace/discovery [--port 3000]
```

Default port: 3000. Prints `Serving at http://localhost:3000` on startup.

**Routing rules:**
- `GET /_viewer/` → `index.html`
- `GET /_viewer/tokens.css` → `tokens.css`
- `GET /opportunities/opp-1/2026-05-25/comparison-matrix.json` → workspace file
- `GET /<round-path>/` → directory listing as JSON (array of `*.json` filenames only) for round scanning

The directory-listing endpoint lets the viewer discover which JSON files exist in a round without hardcoding filenames. Non-JSON files are excluded from the listing.

## Viewer (`index.html`)

Single HTML file containing all CSS and JS inline (alongside the external `tokens.css` link).

### URL interface

```
http://localhost:3000/_viewer/?round=opportunities/opp-1/2026-05-25
```

The `round` query parameter is the path relative to `discovery/`.

### Startup sequence

1. Parse `round` from query string
2. Fetch `/<round>/decisions.json` — the spine. Show error state if missing.
3. Fetch directory listing `/<round>/` to discover available JSON files
4. Build navigation tabs from discovered files (one tab per recognized JSON type)
5. Render the default view (decisions summary, or first available view)

### Recognized JSON types → views

| JSON file | View name | Renderer |
|---|---|---|
| `decisions.json` | Decisions | Summary of ratified picks at each gate |
| `comparison-matrix.json` | Comparison Matrix | Swim-lane card layout (current design, ported) |
| `riskiest-assumptions.json` | Riskiest Assumptions | Grouped by solution, 2x2 importance/evidence |
| `validation-experiments.json` | Experiments | Test cards with hypothesis/metric/criteria |
| `solution-candidates.json` | Solutions | 18 candidates grouped by round |
| `experience-map-clustered.json` | Experience Map | Phase/step/opportunity hierarchy |

Unrecognized JSON files are ignored (not shown as tabs). New view types are added by adding a renderer function and registering the filename.

### CSS architecture

```html
<link rel="stylesheet" href="tokens.css">
<style>
  /* Layout, components, and view-specific styles */
  /* All colors, fonts, spacing reference --sc-* tokens */
  /* No hardcoded colors — everything goes through tokens */
</style>
```

**Design token usage:**
- Colors: `--sc-blue-monday`, `--sc-pink-moon`, `--sc-grey-*` etc. for surfaces, borders, status indicators
- Typography: `--sc-font-family`, `--sc-font-size-*`, `--sc-font-weight-*`
- Spacing: `--sc-space-xs` through `--sc-space-2xl`
- Shadows: `--sc-shadow-soft-*` for card elevation
- Radius: `--sc-radius-*` for card corners
- Transitions: `--sc-transition-*` for interactive states

**Components reused from design system:**
- `SelectorChips` pattern for filter chips (ported to inline, same visual language)
- `Accordion` pattern for expandable card details
- `Tabs` pattern for view navigation

These are ported as inline CSS/JS in the viewer, not imported as ES modules (keeps it self-contained per file beyond the tokens.css link).

### JS architecture

Single `<script>` block. Structure:

```
// Data layer
async function loadRound(roundPath) → { decisions, files[] }
async function loadJSON(path) → parsed JSON

// View registry
const views = {
  'comparison-matrix.json': { label: 'Comparison Matrix', render: renderComparisonMatrix },
  'riskiest-assumptions.json': { label: 'Riskiest Assumptions', render: renderRiskiest },
  ...
}

// Renderers (one function per view)
function renderComparisonMatrix(json, container) → void
function renderRiskiest(json, container) → void
function renderExperiments(json, container) → void
function renderDecisions(json, container) → void
function renderSolutions(json, container) → void
function renderExperienceMap(json, container) → void

// Navigation
function buildTabs(availableFiles) → tab bar DOM
function switchView(filename) → load + render

// Init
main()
```

No framework. Vanilla JS. DOM creation via `document.createElement` or template literals with `innerHTML`. Each renderer is independent — it receives JSON and a container element, and fills it.

### Print support

`@media print` stylesheet:
- Hides tab navigation
- Shows current view only
- Forces all collapsible sections open
- Removes interactive elements (filter chips)
- Fits A4/Letter width

## Skill integration

### What changes in SKILL.md files

Skills that currently produce HTML (only skill 05 today) drop their HTML template section entirely. They write JSON only.

Skills that could benefit from a viewer (06, 09, 12, 13) already write JSON — no SKILL.md changes needed. The viewer picks up their files automatically.

### Server lifecycle

When a skill writes JSON output that has a registered viewer:

1. Check if `localhost:3000` responds (quick `curl` or Python socket check)
2. If not running, resolve paths:
   - `--templates`: the plugin's `templates/viewer/` directory (skill knows its own install path)
   - `--data`: the workspace's `discovery/` directory (from scope resolution)
3. Start `serve.py` in the background
4. Print to trio: `View at: http://localhost:3000/_viewer/?round=<round-path>`

If the server is already running, just print the URL.

## Design iteration workflow

**Designer (Joni):**
1. `cd ~/claude-projects/claude-plugins`
2. `python3 product-discovery/templates/serve.py --templates product-discovery/templates/viewer --data /path/to/fixture/discovery`
3. Open `localhost:3000/_viewer/?round=<fixture-round>`
4. Edit `product-discovery/templates/viewer/index.html`
5. Refresh browser → see changes
6. `git commit && git push` → all trios get the update on next session start

**Trio:**
1. Run an OST skill in Claude Code
2. Skill prints a URL
3. Click URL → browser opens the viewer with their data
4. Review, make HITL decisions, continue in Claude Code

## Porting the existing comparison-matrix.html

The current swim-lane card design in skill 05 (lines 214-540 of SKILL.md) is ported into `renderComparisonMatrix()` in the viewer. The design is preserved but restyled with `--sc-*` tokens:

- Card backgrounds: `--sc-grey-50` (surface), `--sc-blue-monday` accents for strong scores
- Text: `--sc-grey-900` (primary), `--sc-grey-500` (secondary)
- Shadows: `--sc-shadow-soft-sm` for cards
- Filter chips: `SelectorChips` visual pattern from design system
- Expandable details: `Accordion` visual pattern

The swim-lane layout (CSS grid, one column per journey phase) and filter chip logic (AND-combined toggles) carry over unchanged.

## What this does NOT cover

- **Hosted/SaaS version.** This is local-only. A future hosted version would replace `serve.py` with a proper backend and the viewer with a framework-based frontend. The JSON data model carries over.
- **Real-time updates.** The viewer loads data on page load. No WebSocket or polling. Refresh to see new data.
- **Editing decisions.json from the viewer.** The viewer is read-only. HITL decisions are made in Claude Code or by editing JSON directly.
- **Views for skills 02/03 (markdown-only output).** These don't produce JSON; the viewer can't render them.
