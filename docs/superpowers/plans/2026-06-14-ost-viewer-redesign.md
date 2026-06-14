# OST Viewer Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collapse the OST viewer from 9 co-equal artifact tabs to 4 purposeful, static surfaces — Tree · Prioritise · Journey · Table (rollup) — so a trio can make sense of one discovery round without reconstructing relationships from IDs.

**Architecture:** Edits to the single dependency-free `product-discovery/templates/viewer/index.html` (vanilla ES5-style JS, string-building renderers, CSS, no libraries). Reuses the SCI-207 Tree renderer + data helpers. Adds one new static rollup renderer. The page stays **read-only**: only view-navigation (tab/lens switching, the Tree cut toggle, collapsible sections). No download/sort/export/action controls — acting on the round is a terminal job (SCI-243).

**Tech Stack:** Vanilla JS (match the file: `var`, function declarations, single quotes, 2-space indent), CSS, the bundled `serve.py` static server, the golden fixture at `product-discovery/fixtures/golden/expected-output/OST-discovery/`.

---

## Reference material (in-repo)

- **Spec (authoritative):** `docs/superpowers/specs/2026-06-14-ost-viewer-redesign-design.md`.
- Builds on the SCI-207 Tree view already in `index.html`.

## How to run / verify (correct command — note serve.py lives in templates/, needs --templates)

```bash
lsof -ti:3000 | xargs -r kill
python3 product-discovery/templates/serve.py \
  --templates product-discovery/templates/viewer \
  --data product-discovery/fixtures/golden/expected-output/OST-discovery \
  --port 3000 >/tmp/serve.log 2>&1 &
for i in $(seq 1 20); do c=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/_viewer/?round=."); [ "$c" = 200 ] && break; sleep 0.4; done
```
The controller does visual verification via headless screenshot (`Google Chrome --headless --screenshot=… "http://localhost:3000/_viewer/?round=."`) and `--dump-dom` greps. Subagents do objective checks (server 200, node smoke tests, grep of served HTML) only.

## Current state (line numbers as of this plan)

- `var views = {…}` registry — `index.html:1420`. 9 entries.
- Default tab: `switchView('tree')` — `index.html:2885`.
- Renderers: `renderTree` (1791), `renderOverview` (1824), `renderHeader` (1895), `renderDecisions` (1909), `renderComparisonMatrix` (1976), `renderRiskiest` (2173), `renderExperiments` (2229), `renderSolutions` (2271), `renderJourneyMap` (2523), `renderExperienceMap` (2800).
- `buildTabs` (1437), `VIEW_GUIDE` (1501), `injectGuide` (1532).
- SCI-207 data helpers available: `loadTreeData(roundData)`, `buildOpportunityTree`, `buildAssumptionRows`, `loadJSON`, `esc`.

## Target IA (4 surfaces)

| Surface | Renderer | Source |
|---|---|---|
| **Tree** (default) | `renderTree` (exists) | unchanged |
| **Prioritise** | `renderComparisonMatrix` (exists) | relabel only |
| **Journey** | `renderJourney` (NEW, merges Experience + Journey map) | `experience-map-clustered.json` (+ extracted beneath) |
| **Table** | `renderRollup` (NEW, synthetic) | rollup of `_working/*.json` |

Removed as tabs: Overview (→ header round-status), Decisions, Riskiest (in Tree table), Experiments, Solutions, the separate Journey Map (→ inside Journey lens).

---

## Task 1: Collapse the view registry to 4 surfaces

**Files:** Modify `product-discovery/templates/viewer/index.html` — `views` registry (~1420).

- [ ] **Step 1: Replace the registry with the 4 surfaces**

```js
  var views = {
    'tree':                          { label: 'Tree',       render: renderTree, synthetic: true },
    'comparison-matrix.json':        { label: 'Prioritise', render: renderComparisonMatrix },
    'experience-map-clustered.json': { label: 'Journey',    render: renderJourney },
    'rollup':                        { label: 'Table',      render: renderRollup, synthetic: true },
  };
```
(`renderJourney` and `renderRollup` are added in later tasks. Add temporary stubs now so the file parses:)
```js
  function renderJourney(json, container){ container.innerHTML = '<div class="view-section"><p>Journey — coming in this branch.</p></div>'; }
  async function renderRollup(roundData, container){ container.innerHTML = '<div class="ost-tree-tab"><p style="padding:2rem;">Table — coming in this branch.</p></div>'; }
```
Place the stubs next to `renderTree`.

- [ ] **Step 2: Route the synthetic `rollup` view in `switchView`**

Find the `if (filename === 'tree') { await entry.render(roundData, container); return; }` block (added in SCI-207) and add an identical branch for rollup right after it:
```js
    if (filename === 'rollup') {
      await entry.render(roundData, container);
      return;
    }
```

- [ ] **Step 3: Verify the tab bar shows exactly 4 tabs**

Start the server (command above). Controller screenshots; objective check:
```bash
curl -s "http://localhost:3000/_viewer/index.html" | grep -cE "renderJourney|renderRollup|'rollup'|'comparison-matrix.json'.*Prioritise"
```
Expected: ≥3. The tab bar should read **Tree · Prioritise · Journey · Table** (Decisions/Overview/Riskiest/Experiments/Solutions/Journey-Map gone).

- [ ] **Step 4: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-242): collapse viewer to 4 surfaces (Tree/Prioritise/Journey/Table)"
```

---

## Task 2: Fold round-status into the header; drop the Overview tab

**Files:** Modify `index.html` — `renderHeader` (~1895), `renderHeader` call site (~2876 area).

The Overview tab is gone from the registry (Task 1). Its useful part — the phase tracker ("where this round is") — moves into the always-visible header. The OST explainer prose is dropped (one short per-lens guide covers orientation; Task 7).

- [ ] **Step 1: Extend `renderHeader` to render the phase tracker**

Replace the body of `renderHeader` with:
```js
  function renderHeader(decisions, roundPath) {
    var header = document.getElementById('viewer-header');
    var product = decisions ? (decisions.product || 'Unknown product') : 'Unknown product';
    var team = decisions && decisions.team ? ' (' + decisions.team + ')' : '';
    var outcome = decisions ? (decisions.product_outcome || '') : '';
    var d = (decisions && decisions.decided) || {};

    document.title = 'OST Viewer — ' + product + team;

    var gates = [
      { label: 'Opportunity', on: !!d.opportunity },
      { label: 'Solutions',   on: !!d.solutions },
      { label: 'Assumptions', on: !!d.assumptions },
      { label: 'Experiments', on: !!d.experiments }
    ];
    var curIdx = gates.findIndex(function (g) { return !g.on; });
    if (curIdx === -1) curIdx = gates.length;
    var track = gates.map(function (g, i) {
      var state = g.on ? 'done' : (i === curIdx ? 'current' : 'pending');
      var mark = state === 'done' ? '✓' : (state === 'current' ? '▶' : '·');
      return '<span class="hdr-gate ' + state + '"><span class="hdr-mark">' + mark + '</span>' + esc(g.label) + '</span>';
    }).join('<span class="hdr-sep">→</span>');

    header.innerHTML = '<h1>' + esc(product) + esc(team) + '</h1>'
      + '<p class="meta">Round: <code>' + esc(roundPath) + '</code></p>'
      + (outcome ? '<blockquote>' + esc(outcome) + '</blockquote>' : '')
      + '<div class="hdr-track">' + track + '</div>';
  }
```

- [ ] **Step 2: Add header-track CSS**

Append to the OST CSS section in `<style>`:
```css
  .hdr-track{display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;margin-top:.6rem;}
  .hdr-gate{display:inline-flex;align-items:center;gap:.35rem;font-size:.78rem;color:var(--sc-grey-500);}
  .hdr-gate.done{color:var(--sc-essex-green);} .hdr-gate.current{color:var(--sc-blue-monday);font-weight:600;}
  .hdr-mark{font-weight:700;} .hdr-sep{color:var(--sc-grey-300);}
```

- [ ] **Step 3: Remove the now-dead `renderOverview` + its link-handler**

Delete the `renderOverview` function (~1824–1893) and the one-time Overview tab-guide click handler near init (the `document.getElementById('view-container').addEventListener('click', … data-goto …)` block added for Overview's link-tabs). Verify nothing else references `renderOverview` or `data-goto`:
```bash
grep -nE "renderOverview|data-goto|link-tab" product-discovery/templates/viewer/index.html || echo "clean"
```
Expected: `clean` (no references remain).

- [ ] **Step 4: Verify**

Server up; controller screenshots the header (should show the outcome + a `Opportunity → Solutions → Assumptions → Experiments` gate track). Objective:
```bash
curl -s "http://localhost:3000/_viewer/index.html" | grep -c "hdr-track"
```
Expected: ≥1 (the CSS + the renderHeader insertion).

- [ ] **Step 5: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-242): fold round-status into header, drop Overview tab"
```

---

## Task 3: Journey lens — merge Experience Map + raw Journey Map

**Files:** Modify `index.html` — replace the `renderJourney` stub; keep `renderExperienceMap` (2800) and `renderJourneyMap` (2523) as the two pieces it composes.

The Journey lens leads with **opportunities clustered by phase** (the density view) and offers the **raw journey** (steps/decision-branches) beneath, collapsed.

- [ ] **Step 1: Implement `renderJourney`**

`renderExperienceMap(json, container)` already renders opps-by-phase from `experience-map-clustered.json`. `renderJourneyMap(json, container)` renders the raw journey from `experience-map-extracted.json`. Compose them:
```js
  async function renderJourney(clusteredJson, container){
    // Primary: opportunities clustered by journey phase (the density lens).
    var primary = document.createElement('div');
    renderExperienceMap(clusteredJson, primary);

    // Secondary (collapsed): the raw journey map, loaded on demand.
    var details = document.createElement('details');
    details.className = 'journey-raw';
    details.innerHTML = '<summary>Show the raw journey (steps &amp; decision branches)</summary>'
      + '<div class="journey-raw-body"></div>';

    container.innerHTML = '';
    container.appendChild(primary);
    container.appendChild(details);

    var extracted = await loadJSON(roundData_basePath() + '/_working/experience-map-extracted.json');
    if (extracted) {
      renderJourneyMap(extracted, details.querySelector('.journey-raw-body'));
    } else {
      details.querySelector('.journey-raw-body').innerHTML = '<p class="tbl-empty">No raw journey map for this round.</p>';
    }
  }
```

- [ ] **Step 2: Add the `roundData_basePath` accessor**

`renderJourney` is called as a file-backed view (`switchView` passes the parsed JSON, not roundData), so it needs the round base path. The module already keeps `roundData` in a closure var. Add a tiny helper near `loadTreeData`:
```js
  function roundData_basePath(){ return (roundData && roundData.basePath) || ''; }
```

- [ ] **Step 3: Style the collapsible**

```css
  .journey-raw{margin-top:1.5rem;border-top:1px solid var(--sc-purple-mountains);padding-top:1rem;}
  .journey-raw summary{cursor:pointer;font-weight:600;color:var(--sc-blue-monday);font-size:.9rem;}
  .journey-raw-body{margin-top:1rem;}
```

- [ ] **Step 4: Verify**

Server up; switch to the Journey tab. Controller screenshots: opps-by-phase on top, a "Show the raw journey" disclosure beneath; expanding it renders the journey map. Objective:
```bash
curl -s "http://localhost:3000/_viewer/index.html" | grep -cE "renderJourney\b|journey-raw"
```
Expected: ≥2.

- [ ] **Step 5: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-242): Journey lens merges opps-by-phase + raw journey"
```

---

## Task 4: Rollup data layer — `buildRollupRows` (pure) + smoke test

**Files:** Modify `index.html` (add `buildRollupRows` near `loadTreeData`). Test: `/tmp/ost-rollup-smoke.mjs` (temporary, not committed).

**Grain:** one row per *deepest leaf on each branch.* Chosen-opportunity assumptions → deep rows (recommended test inline); every other approved opportunity → one shallow row (right-hand cells empty). Sub-opportunities (`parent_id`) → child rows.

Data sources confirmed in the fixture:
- `experience-map-clustered.json` → `phases[]` with `name` + `opportunities[]` (`id, quote, verdict, parent_id, step_id`). Phase name = the stage; resolve each opp's stage via the phase it sits under.
- `comparison-matrix.json` → per-opportunity scores (chosen-set). Use it to mark a `score` summary; absence ⇒ blank.
- `decisions.json` → `decided.opportunity.id` (chosen).
- Assumptions: reuse `loadTreeData`'s merged `assumBlocks` (riskiest rows + tests) and `solutions` (top-3) — already joins riskiest + validation by id.

- [ ] **Step 1: Write the smoke test `/tmp/ost-rollup-smoke.mjs`**

```js
import fs from 'node:fs';
const F = 'product-discovery/fixtures/golden/expected-output/OST-discovery';
const clustered = JSON.parse(fs.readFileSync(`${F}/_working/experience-map-clustered.json`));
const decisions = JSON.parse(fs.readFileSync(`${F}/decisions.json`));
const riskiest  = JSON.parse(fs.readFileSync(`${F}/_working/riskiest-assumptions.json`));
const validation= JSON.parse(fs.readFileSync(`${F}/_working/validation-experiments.json`));

function buildRollupRows(clustered, decisions, assumBlocks, solutions, chosenId){
  // stage per opportunity, flattened across phases
  var rows = [];
  var outcome = decisions.product_outcome || '';
  var solTitleById = {};
  (solutions || []).forEach(function(s){ solTitleById[s.id] = s.title; });
  // index assumptions by solution_id
  var asmBySol = {};
  (assumBlocks || []).forEach(function(b){ asmBySol[b.solution_id] = b.assumptions || []; });

  (clustered.phases || []).forEach(function(ph){
    (ph.opportunities || []).forEach(function(o){
      if (o.verdict !== 'approved' && o.id !== chosenId) return;
      var base = { outcome: outcome, stage: ph.name, opp: o.quote, parent: o.parent_id || '', chosen: o.id === chosenId };
      if (o.id !== chosenId) { rows.push(Object.assign({}, base, { solution:'', assumption:'', importance:'', evidence:'', riskiest:false, typ:'', test:'', success:'' })); return; }
      // chosen opportunity → deep rows across its solutions' assumptions
      (solutions || []).forEach(function(s){
        var asms = asmBySol[s.id] || [];
        if (!asms.length) { rows.push(Object.assign({}, base, { solution:s.title, assumption:'', importance:'', evidence:'', riskiest:false, typ:'', test:'', success:'' })); return; }
        asms.forEach(function(a){
          var rt = a.recommended_test || null;
          rows.push(Object.assign({}, base, {
            solution: s.title, assumption: a.text,
            importance: a.importance||'', evidence: a.evidence||'', riskiest: !!a.is_riskiest, typ: a.category||'',
            test: rt ? rt.test_type : '', success: rt ? rt.success_criteria : ''
          }));
        });
      });
    });
  });
  return rows;
}

// emulate loadTreeData's merge: riskiest rows + validation tests by id
const testById = {};
validation.assumptions_per_solution.forEach(s => s.assumptions.forEach(a => { if (a.recommended_test) testById[a.id] = a.recommended_test; }));
const assumBlocks = riskiest.assumptions_per_solution.map(b => ({ solution_id: b.solution_id, assumptions: b.assumptions.map(a => Object.assign({}, a, { recommended_test: a.recommended_test || testById[a.id] || null })) }));
const solutions = riskiest.assumptions_per_solution.map(b => ({ id: b.solution_id, title: b.solution_title }));
const chosenId = decisions.decided.opportunity.id;

const rows = buildRollupRows(clustered, decisions, assumBlocks, solutions, chosenId);
const deep = rows.filter(r => r.assumption);
const shallow = rows.filter(r => !r.assumption && !r.solution);
console.assert(rows.every(r => r.outcome && r.stage && r.opp), 'every row has outcome+stage+opp');
console.assert(deep.length >= 30, `expected ~33 deep rows, got ${deep.length}`);
console.assert(shallow.length >= 30, `expected ~43 shallow opp rows, got ${shallow.length}`);
console.assert(deep.some(r => r.riskiest && r.test), 'riskiest deep rows carry a test');
console.assert(deep.some(r => !r.riskiest && !r.test), 'non-riskiest deep rows have empty test (sparse)');
console.assert(rows.some(r => r.chosen), 'chosen opportunity present');
console.log(`OK rollup — ${rows.length} rows (${deep.length} deep, ${shallow.length} shallow)`);
```

- [ ] **Step 2: Run it — must pass**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins && node /tmp/ost-rollup-smoke.mjs
```
Expected: `OK rollup — ~76 rows (~33 deep, ~43 shallow)`. If counts are wildly off, STOP and report BLOCKED with output.

- [ ] **Step 3: Add `buildRollupRows` to index.html (exact copy of the tested function), plus a `loadRollupData` loader**

```js
  function buildRollupRows(clustered, decisions, assumBlocks, solutions, chosenId){ /* EXACT copy from the smoke test */ }

  async function loadRollupData(roundData){
    var base = roundData.basePath + '/_working/';
    var clustered = await loadJSON(base + 'experience-map-clustered.json');
    var t = await loadTreeData(roundData); // gives solutions + merged assumBlocks + chosenId + outcome
    var rows = (clustered && roundData.decisions)
      ? buildRollupRows(clustered, roundData.decisions, t.assumBlocks, t.solutions, t.chosenId)
      : [];
    return { rows: rows, outcome: t.outcome };
  }
```

- [ ] **Step 4: Re-run smoke test (still green), then commit (do NOT add /tmp file)**

```bash
node /tmp/ost-rollup-smoke.mjs
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-242): rollup data layer — buildRollupRows + loadRollupData"
```

---

## Task 5: Rollup renderer — the static Table surface

**Files:** Modify `index.html` — replace the `renderRollup` stub; add table CSS.

Static, read-only. One sensible default order: rows already arrive in phase-then-opportunity order from `buildRollupRows` (it walks `phases[]` in order). No sort/filter/download controls.

- [ ] **Step 1: Replace the `renderRollup` stub**

```js
  async function renderRollup(roundData, container){
    var data = await loadRollupData(roundData);
    var COLS = ['Stage','Opportunity','Solution','Assumption','Betydelse','Bevis','Riskigast','Typ','Testmetod','Framgångskriterier'];
    var sv = function(v, map){ return v ? (map[v] || v) : '—'; };
    if (!data.rows.length){
      container.innerHTML = '<div class="view-section"><div class="tbl-empty">No round data to roll up yet.</div></div>';
      return;
    }
    var head = '<tr><th>#</th>' + COLS.map(function(h){ return '<th>' + esc(h) + '</th>'; }).join('') + '</tr>';
    var n = 0;
    var body = data.rows.map(function(r){
      n++;
      return '<tr class="' + (r.riskiest ? 'risky' : '') + (r.chosen ? ' rollup-chosen' : '') + '">' +
        '<td class="idx">' + n + '</td>' +
        '<td>' + esc(r.stage) + '</td>' +
        '<td class="rollup-opp">' + esc(r.opp) + (r.parent ? ' <span class="rollup-sub">↳ sub</span>' : '') + (r.chosen ? ' <span class="badge">Vald</span>' : '') + '</td>' +
        '<td>' + (r.solution ? esc(r.solution) : '—') + '</td>' +
        '<td class="assum-txt">' + (r.assumption ? esc(r.assumption) : '—') + '</td>' +
        '<td>' + sv(r.importance, {high:'Hög',low:'Låg'}) + '</td>' +
        '<td>' + sv(r.evidence, {strong:'Starkt',weak:'Svagt'}) + '</td>' +
        '<td>' + (r.riskiest ? '<span class="flag-riskiest">Riskigast</span>' : '') + '</td>' +
        '<td>' + (r.typ ? esc(({desirability:'Önskvärdhet',usability:'Användbarhet',feasibility:'Genomförbarhet',viability:'Lönsamhet',other:'Övrigt'})[r.typ] || r.typ) : '—') + '</td>' +
        '<td class="test">' + (r.test ? esc(r.test) : '—') + '</td>' +
        '<td class="succ">' + (r.success ? esc(r.success) : '—') + '</td>' +
      '</tr>';
    }).join('');
    container.innerHTML =
      '<div class="ost-tree-tab">' +
        '<div class="view-guide"><h3>Full output — one row per deepest item</h3>' +
        '<p>Every opportunity in the round, laddered out to the chosen branch\'s assumptions and recommended tests. Empty cells on the right mean a branch wasn\'t taken deeper — not missing data. The completeness/guardrail view; to slice or act on it, ask in the terminal.</p></div>' +
        '<blockquote class="rollup-outcome"><b>Outcome:</b> ' + esc(data.outcome) + '</blockquote>' +
        '<div class="tbl-card"><div class="tbl-scroll"><table class="assum rollup">' +
          '<thead>' + head + '</thead><tbody>' + body + '</tbody></table></div></div>' +
      '</div>';
  }
```

- [ ] **Step 2: Add rollup CSS**

```css
  table.rollup th{position:sticky;top:0;}
  .rollup-opp{min-width:240px;}
  .rollup-sub{font-size:.66rem;color:var(--sc-grey-500);}
  tr.rollup-chosen td{background:rgba(0,34,255,.03);}
  .rollup-outcome{margin:.5rem 0 1rem;}
```

- [ ] **Step 3: Verify against the fixture**

Server up; switch to the Table tab. Controller screenshots + dump-dom check:
```bash
"$CHROME" --headless --disable-gpu --virtual-time-budget=5000 --dump-dom "http://localhost:3000/_viewer/?round=." 2>/dev/null > /tmp/dom.html
# (after temporarily defaulting to the rollup tab, or have controller click) confirm row count
grep -oE '<tr class="[^"]*"><td class="idx">[0-9]+' /tmp/dom.html | wc -l   # ~76 data rows
```
Expected: ~76 data rows; riskiest rows flagged; sparse `—` on shallow rows.

- [ ] **Step 4: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-242): static rollup Table surface"
```

---

## Task 6: Solutions-considered drill-down (rehome the 18)

**Files:** Modify `index.html` — `renderTree`'s vertical-cut path.

The Solutions tab is gone; the breadth (18 candidates) returns as a collapsible "considered" list beneath the Tree's chosen branch — static, view-navigation only.

- [ ] **Step 1: Load solution-candidates in `loadTreeData` (additive)**

In `loadTreeData`, after `top3` is loaded, also load the candidates and pass them through:
```js
    var candidates = await loadJSON(base + 'solution-candidates.json');
```
Add to the returned object: `candidates: (candidates && candidates.solutions) || [],` (confirmed key: `solution-candidates.json` has a top-level `solutions[]` array; each item is `{id, title, description, round_number, generating_role}`).

- [ ] **Step 2: Append a collapsible to the vertical cut**

In `renderTree`, after the vertical board renders and only when `data.candidates.length`, append below `#ost-antaganden`:
```js
    if (container.__ostCut === 'v' && data.candidates && data.candidates.length){
      var det = document.createElement('details');
      det.className = 'sol-considered';
      det.innerHTML = '<summary>All ' + data.candidates.length + ' solutions considered</summary>' +
        '<ul class="sol-list">' + data.candidates.map(function(c){
          return '<li><b>' + esc(c.title || c.id) + '</b>' + (c.description ? ' — ' + esc(c.description) : '') + '</li>';
        }).join('') + '</ul>';
      document.querySelector('.ost-tree-tab').appendChild(det);
    }
```
(Wire this into `ostSetCut`'s vertical branch so it re-renders with the cut.)

- [ ] **Step 3: Style**

```css
  .sol-considered{margin-top:1.5rem;} .sol-considered summary{cursor:pointer;font-weight:600;color:var(--sc-blue-monday);}
  .sol-list{margin-top:.75rem;columns:2;gap:1.5rem;font-size:.82rem;line-height:1.5;}
```

- [ ] **Step 4: Verify** — Tree vertical cut shows an "All 18 solutions considered" disclosure; expanding lists them. Commit.

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-242): rehome 18-solution breadth as a Tree collapsible"
```

---

## Task 7: Static-only audit, per-lens guides, cleanup, fixture safety

**Files:** Modify `index.html` — `VIEW_GUIDE`; remove dead renderers.

- [ ] **Step 1: Remove now-dead renderers**

`renderDecisions`, `renderRiskiest`+`renderQuadrant`, `renderExperiments`, `renderSolutions` are no longer registered. Remove them only if nothing references them:
```bash
for fn in renderDecisions renderRiskiest renderQuadrant renderExperiments renderSolutions; do
  echo "$fn: $(grep -c "$fn" product-discovery/templates/viewer/index.html) refs"; done
```
A function with exactly 1 ref (its own definition) is safe to delete. `renderComparisonMatrix`, `renderExperienceMap`, `renderJourneyMap`, `renderOppCard` stay (still used).

- [ ] **Step 2: Per-lens guide text**

Update `VIEW_GUIDE` keys to match the new registry (`comparison-matrix.json` = Prioritise, `experience-map-clustered.json` = Journey). One short sentence each; drop stale keys (decisions/riskiest/experiments/solutions). Tree + rollup render their own inline guide (already added).

- [ ] **Step 3: Static-only audit (the core principle)**

Confirm no action controls leaked in:
```bash
grep -niE "download|export|\.csv|createObjectURL|<button[^>]*sort|onclick=.*(sort|export|download)" product-discovery/templates/viewer/index.html || echo "no action controls — clean"
```
Expected: `clean` (the only buttons are the Tree cut toggle + tab nav, which are view-navigation).

- [ ] **Step 4: Remove temp test + fixture safety**

```bash
rm -f /tmp/ost-rollup-smoke.mjs /tmp/dom.html
grep -niE "norrsken|licenstilldelning|delfi|vendure|xledger" product-discovery/templates/viewer/index.html || echo "clean"
```
Expected: `clean`.

- [ ] **Step 5: Full regression** — server up, screenshot each of the 4 tabs; confirm no console errors, Tree still default, partial-data round (no chosen opp) still renders.

- [ ] **Step 6: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-242): remove dead renderers, per-lens guides, static-only audit"
```

---

## Self-review against the spec

- **4 surfaces (Tree/Prioritise/Journey/Table), 9→4** → Task 1. ✔
- **Overview → header round-status** → Task 2. ✔
- **Journey merges Experience + raw Journey** → Task 3. ✔
- **Rollup grain = deepest leaf; ragged depth; sub-opps; sparse tests** → Task 4 (`buildRollupRows`, asserted in smoke test). ✔
- **Rollup columns + static render, sensible order** → Task 5. ✔
- **Solutions-18 rehomed (drill-down)** → Task 6. ✔
- **Cut Decisions/Riskiest/Experiments/Solutions tabs; risk already in Tree table** → Tasks 1 + 7. ✔
- **Static, read-only — no action controls** → Task 7 Step 3 audit. ✔
- **Data sources all from `_working/`; reuse SCI-207 helpers** → Task 4 (`loadTreeData`, `buildAssumptionRows` reuse). ✔
- **Degrade gracefully on partial rounds** → Task 5 empty-state + Task 7 Step 5. ✔
- **Out of scope: action skill (SCI-243), action model (SCI-244), living tree** → no tasks touch them. ✔

No open items — the `solution-candidates.json` key (`solutions[]`) is confirmed and locked into Task 6.
