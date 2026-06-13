# OST Tree View Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a default "Tree" tab to the OST viewer that renders the Opportunity Solution Tree two ways — a horizontal opportunity-space cut and a vertical chosen-branch cut with an assumption table — from the existing round JSON.

**Architecture:** One new synthetic view (`renderTree`) inside the existing single-file tabbed viewer (`product-discovery/templates/viewer/index.html`). Pure-CSS orthogonal tree (no libraries), DOM-measured swimlane bands, `--ost-*` tokens layered over the viewer's `--sc-*` tokens. A segmented toggle flips cuts; the default cut is chosen from `decisions.json`. Data-shaping logic (tree build, assumption-row merge) is written as pure functions so it can be smoke-tested in node against the golden fixture.

**Tech Stack:** Vanilla ES5-ish JS (match the file's existing style — `var`, function declarations, string-building renderers), CSS, the bundled `serve.py` static server, the golden fixture at `product-discovery/fixtures/golden/expected-output/OST-discovery/`.

---

## Reference material (all in-repo)

- **Spec:** `docs/superpowers/specs/2026-06-13-ost-tree-view-design.md` — the authoritative decisions.
- **Visual mockup (vendored):** `docs/superpowers/specs/ost-tree-view-mockup/mockup.html` — the canonical CSS + markup to port. Line ranges are cited below. **Note the two corrections the spec makes to it:** risk is a 2×2 (not a single `Risknivå`), and `Testmetod`/`Framgångskriterier` are sparse (riskiest rows only).
- **Mockup rationale:** `docs/superpowers/specs/ost-tree-view-mockup/rationale.html`.

## File structure

- **Modify only:** `product-discovery/templates/viewer/index.html` — add CSS into the existing `<style>`, add `renderTree` + helpers into the existing `<script>`, register the view, change the default tab. One file, matching the established single-file pattern.
- **Temporary, NOT committed:** `/tmp/ost-tree-smoke.mjs` — node smoke test for the pure data functions (Tasks 2 & 6). Deleted before final commit.

## Data sources (confirmed against the golden fixture)

All under `<round>/_working/` except `decisions.json` (round root):

- **`decisions.json`** → `decided.opportunity.id` (chosen opp, e.g. `"opp-7-1"`), `decided.solutions.picks[]` (`{id,title,description}`), `product_outcome`. Presence of `decided.opportunity` ⇒ default to vertical cut; absence ⇒ horizontal.
- **`experience-map-clustered.json`** → `phases[].opportunities[]`, each `{id, quote, source, verdict, step_id, parent_id}`. **Opportunities live nested under journey phases — flatten all `phases[].opportunities[]` into one list, then rebuild hierarchy from `parent_id`** (ignore phases entirely). Display text = `quote`. `parent_id` is `null` for roots or an opp `id` for children. Filter to `verdict === "approved"`, but always keep the chosen opp even if its verdict differs.
- **`top-three-solutions.json`** → `picks[]` (`{id, title, description, ...}`) — the 3 solutions for the vertical cut. Fall back to `decisions.json` `decided.solutions.picks` if this file is absent.
- **Assumptions — load the richest file present, in this precedence:**
  1. `validation-experiments.json` (best — has everything),
  2. else `riskiest-assumptions.json` (no test cards),
  3. else `assumptions-categorized.json` (no risk axes, no tests).
  All three share the shape `assumptions_per_solution[]` = `{pick_position, solution_id, solution_title, assumptions[]}`. Each assumption: `{id, text, category}` always; `+{importance, evidence, is_riskiest, rationale}` from riskiest onward; `+{recommended_test:{test_type, success_criteria, ...}}` on **riskiest only** from validation onward.

---

## Task 1: Register the Tree tab, route it, make it default

**Files:**
- Modify: `product-discovery/templates/viewer/index.html` — `views` registry (~1167), `switchView` (~1206), init `switchView('overview')` (~2306).

- [ ] **Step 1: Add the synthetic `tree` view as the FIRST registry entry**

In the `var views = { ... }` object, insert as the first key so it becomes the first (default) tab:

```js
  var views = {
    'tree':                        { label: 'Tree', render: renderTree, synthetic: true },
    'overview':                    { label: 'Overview',           render: renderOverview, synthetic: true },
    // ...existing entries unchanged...
```

- [ ] **Step 2: Route the synthetic `tree` view in `switchView` (async — it loads several files)**

`renderTree` is async (loads multiple `_working` files). Add this branch right after the existing `if (filename === 'overview')` block:

```js
    if (filename === 'tree') {
      await entry.render(roundData, container);
      return;
    }
```

(The `overview` branch stays as-is; `tree` gets its own because it awaits.)

- [ ] **Step 3: Make Tree the default landing tab**

Change the final init line from `switchView('overview');` to:

```js
    switchView('tree');
```

> **DECISION FLAG (surface to Joni before merge):** this makes Tree the landing tab, displacing the Overview explainer added in SCI-206. The spec calls for Tree as default; Overview remains one click away as the second tab. If Joni prefers Overview to stay the landing, revert this one line and Tree is simply the second tab.

- [ ] **Step 4: Add a temporary stub `renderTree` so the app loads**

Add near the other renderers (above `renderOverview`):

```js
  async function renderTree(roundData, container) {
    container.innerHTML = '<div class="ost-tree-tab"><p style="padding:2rem;color:var(--sc-grey-600);">Tree view — coming in this branch.</p></div>';
  }
```

- [ ] **Step 5: Verify in the browser against the golden fixture**

Start the server (kill any stale one on 3000 first):

```bash
lsof -ti:3000 | xargs -r kill
python3 product-discovery/templates/viewer/serve.py \
  --data product-discovery/fixtures/golden/expected-output/OST-discovery \
  --port 3000 &
sleep 1
open "http://localhost:3000/_viewer/?round=."
```

Expected: the tab bar shows **Tree** first and it is active on load; the stub text renders; other tabs still work.

- [ ] **Step 6: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-207): register default Tree tab with stub renderer"
```

---

## Task 2: Data layer — load + pure tree builder

**Files:**
- Modify: `product-discovery/templates/viewer/index.html` — add helpers near `renderTree`.
- Test: `/tmp/ost-tree-smoke.mjs` (temporary).

- [ ] **Step 1: Write the failing smoke test for `buildOpportunityTree`**

Create `/tmp/ost-tree-smoke.mjs`. It inlines the pure function (copy-kept in sync with the HTML) and asserts against the fixture:

```js
import fs from 'node:fs';
const F = 'product-discovery/fixtures/golden/expected-output/OST-discovery';
const clustered = JSON.parse(fs.readFileSync(`${F}/_working/experience-map-clustered.json`));
const decisions = JSON.parse(fs.readFileSync(`${F}/decisions.json`));

// --- paste of the pure function under test ---
function buildOpportunityTree(clustered, chosenId) {
  var flat = [];
  (clustered.phases || []).forEach(function (ph) {
    (ph.opportunities || []).forEach(function (o) { flat.push(o); });
  });
  var keep = flat.filter(function (o) { return o.verdict === 'approved' || o.id === chosenId; });
  var byId = {};
  keep.forEach(function (o) {
    byId[o.id] = { id: o.id, text: o.quote, chosen: o.id === chosenId, children: [] };
  });
  var roots = [];
  keep.forEach(function (o) {
    var node = byId[o.id];
    if (o.parent_id && byId[o.parent_id]) byId[o.parent_id].children.push(node);
    else roots.push(node);
  });
  return roots;
}
// --- end paste ---

const chosenId = decisions.decided.opportunity.id;
const roots = buildOpportunityTree(clustered, chosenId);
const count = (ns) => ns.reduce((n, x) => n + 1 + count(x.children), 0);
console.assert(roots.length > 0, 'expected root opportunities');
console.assert(count(roots) >= roots.length, 'children counted');
const chosen = JSON.stringify(roots).includes('"chosen":true');
console.assert(chosen, 'chosen opportunity flagged');
const nested = roots.some(r => r.children.length > 0);
console.assert(nested, 'expected at least one parent_id nesting (fixture has 10)');
console.log(`OK — ${roots.length} roots, ${count(roots)} nodes total, nested=${nested}, chosen=${chosen}`);
```

- [ ] **Step 2: Run it to verify it fails (function not yet in HTML, but test is self-contained — confirm assertions pass against fixture)**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins && node /tmp/ost-tree-smoke.mjs
```

Expected: prints `OK — N roots, M nodes total, nested=true, chosen=true`. (This validates the algorithm against real data before it goes in the file.)

- [ ] **Step 3: Add `buildOpportunityTree` + `loadTreeData` to index.html**

Place above the stub `renderTree`. `buildOpportunityTree` is the exact function from the test. Add the loader:

```js
  function buildOpportunityTree(clustered, chosenId) { /* exact copy from the smoke test */ }

  async function loadTreeData(roundData) {
    var base = roundData.basePath + '/_working/';
    var clustered = await loadJSON(base + 'experience-map-clustered.json');
    var top3 = await loadJSON(base + 'top-three-solutions.json');
    var assum = await loadJSON(base + 'validation-experiments.json')
             || await loadJSON(base + 'riskiest-assumptions.json')
             || await loadJSON(base + 'assumptions-categorized.json');
    var d = roundData.decisions || {};
    var chosenId = d.decided && d.decided.opportunity ? d.decided.opportunity.id : null;
    var picks = (top3 && top3.picks) || (d.decided && d.decided.solutions && d.decided.solutions.picks) || [];
    return {
      outcome: d.product_outcome || (clustered && clustered.product_outcome) || '',
      oppRoots: clustered ? buildOpportunityTree(clustered, chosenId) : [],
      chosenId: chosenId,
      solutions: picks,
      assumBlocks: assum ? assum.assumptions_per_solution || [] : [],
      hasOpp: !!chosenId
    };
  }
```

- [ ] **Step 4: Re-run the smoke test (still green, function now canonical)**

```bash
node /tmp/ost-tree-smoke.mjs
```
Expected: same `OK` line.

- [ ] **Step 5: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-207): tree data layer — loadTreeData + buildOpportunityTree"
```

---

## Task 3: CSS — port the tree/board/bands/table styles

**Files:**
- Modify: `product-discovery/templates/viewer/index.html` — append to the existing `<style>`.

- [ ] **Step 1: Copy the `--ost-*` token block**

From `docs/superpowers/specs/ost-tree-view-mockup/mockup.html` lines **52–76** (the `/* ---- OST-specific, remappable color tokens ---- */` group), paste into the viewer's `:root`. **Do NOT copy lines 14–51** (the `--sc-*` / font / radius tokens) — the viewer already defines those; reuse them. If any referenced `--sc-*` token is missing in the viewer, add only the missing ones.

- [ ] **Step 2: Copy the structural CSS blocks**

From the same mockup file, port these rule groups verbatim into the viewer `<style>` (they're already namespaced and won't collide):
- Board + bands: lines **166–196** (`.board`, `.bandbg`, `.gutter`, `.bandlabel`, `.canvas`, `.tree-wrap`).
- Pure-CSS tree: lines **201–227** (`.tree`, `.tree ul`, `.tree li`, `::before/::after` connectors).
- Nodes: lines **232–282** (`.node`, `.n-outcome`, `.n-opp`, `.n-sol`, `.node-tag`, `.badge`, `.n-empty`, `.empty-stub`).
- Table: lines **287–357** (`.antaganden`, `.tbl-card`, `table.assum`, chips, `.soon`, `.risky`, `.tbl-empty`).
- The segmented toggle: lines **116–134** (`.seg`, `.seg button`), but rename selectors to `.ost-seg` to avoid clashing with viewer chrome.

- [ ] **Step 3: Add the two-axis risk chip styles (NEW — not in the mockup)**

The mockup only had `.chip-risk.high/.low`. The spec needs two axis chips + a riskiest flag. Add:

```css
  .chip-axis{font-weight:600;font-size:.72rem;}
  .chip-axis.hi{background:var(--ost-typ-ons);color:#6b5800;}   /* importance/evidence "strong/high" */
  .chip-axis.lo{background:var(--sc-grey-100);color:var(--sc-grey-600);}
  .flag-riskiest{display:inline-flex;align-items:center;gap:.3rem;font-size:.66rem;font-weight:700;
    text-transform:uppercase;letter-spacing:.04em;color:#B3261E;}
  .flag-riskiest::before{content:"⚑";}
```

- [ ] **Step 4: Verify CSS loads without breaking existing tabs**

Refresh `http://localhost:3000/_viewer/?round=.` and click through every existing tab. Expected: no visual regressions (the new rules are unused until Task 4).

- [ ] **Step 5: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-207): port tree/board/band/table CSS + two-axis risk chips"
```

---

## Task 4: Horizontal cut + vertical cut node rendering

**Files:**
- Modify: `product-discovery/templates/viewer/index.html` — flesh out `renderTree`, add node builders + cut renderers.

- [ ] **Step 1: Add node builders**

Adapt mockup lines 498–511 to real fields (outcome text from data; opp text is `quote`; solutions get display index `S1/S2/S3` but keep real id):

```js
  function ostOutcomeNode(text){ return '<div class="node n-outcome">' + esc(text) + '</div>'; }
  function ostOppNode(o, variant){
    var cls = ['node','n-opp','arr'];
    if (variant === 'sub') cls.push('sub');
    if (o.chosen) cls.push('chosen'); else if (variant !== 'solo') cls.push('muted');
    var badge = o.chosen ? '<span class="badge">Vald</span>' : '';
    return '<div class="' + cls.join(' ') + '">' + badge + esc(o.text) + '</div>';
  }
  function ostSolNode(s, i){
    return '<div class="node n-sol arr"><span class="node-tag">S' + (i+1) + '</span>' + esc(s.title) + '</div>';
  }
```

- [ ] **Step 2: Add the recursive opportunity `<li>` builder + horizontal cut**

```js
  function ostOppLi(node){
    var subs = (node.children || []).map(function (c){
      return '<li data-band="opp">' + ostOppNode(c, 'sub') + '</li>';
    }).join('');
    var subUl = subs ? '<ul>' + subs + '</ul>' : '';
    return '<li data-band="opp">' + ostOppNode(node) + subUl + '</li>';
  }

  function ostRenderHorizontal(data, mount){
    var childLis = data.oppRoots.map(ostOppLi).join('');
    mount.innerHTML =
      '<ul class="tree"><li data-band="outcome">' + ostOutcomeNode(data.outcome) +
      '<ul>' + childLis + '</ul></li></ul>';
  }
```

- [ ] **Step 3: Add the vertical cut (outcome → chosen opp → top-3 solutions)**

```js
  function ostRenderVertical(data, mount){
    var chosen = null;
    (function find(ns){ (ns||[]).forEach(function(n){ if(n.chosen) chosen = n; find(n.children); }); })(data.oppRoots);
    var chosenNode = chosen
      ? ostOppNode(chosen, 'solo')
      : '<div class="node n-empty arr">Ingen opportunity vald ännu</div>';

    var leaves;
    if (data.solutions.length){
      leaves = '<ul>' + data.solutions.map(function(s,i){
        return '<li data-band="sol">' + ostSolNode(s, i) + '</li>';
      }).join('') + '</ul>';
    } else {
      leaves = '<ul><li class="empty-stub" data-band="sol">' +
        '<div class="node n-empty arr">Inga lösningar ännu — välj top-3 för att gå vidare</div></li></ul>';
    }

    mount.innerHTML =
      '<ul class="tree"><li data-band="outcome">' + ostOutcomeNode(data.outcome) +
      '<ul><li data-band="opp">' + chosenNode + leaves + '</li></ul></li></ul>';
  }
```

- [ ] **Step 4: Replace the stub `renderTree` body with the shell that mounts a cut**

For now hard-render the horizontal cut; the toggle comes in Task 5. Build the DOM shell (board + gutter + canvas) once:

```js
  async function renderTree(roundData, container){
    var data = await loadTreeData(roundData);
    container.innerHTML =
      '<div class="ost-tree-tab">' +
        '<div class="ost-seg" id="ost-seg"></div>' +
        '<div class="board" id="ost-board">' +
          '<div class="bandbg"></div><div class="gutter"></div>' +
          '<div class="canvas"><div class="tree-wrap" id="ost-treewrap"></div></div>' +
        '</div>' +
        '<div class="antaganden" id="ost-antaganden"></div>' +
      '</div>';
    ostRenderHorizontal(data, document.getElementById('ost-treewrap'));
    container.__ostData = data; // stash for the toggle/resize handlers (Task 5)
  }
```

- [ ] **Step 5: Verify both cuts render (temporarily call vertical to eyeball it)**

Refresh the viewer. Expected (horizontal): outcome lozenge at top, approved opportunities branching below, the chosen one (`opp-7-1`) blue-ringed with a `Vald` badge, others muted. Temporarily swap `ostRenderHorizontal` → `ostRenderVertical` in Step 4, refresh, confirm outcome → chosen opp → 3 solution pills, then swap back.

- [ ] **Step 6: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-207): render horizontal + vertical tree cuts"
```

---

## Task 5: Toggle, auto-default, DOM-measured bands, center + resize

**Files:**
- Modify: `product-discovery/templates/viewer/index.html`.

- [ ] **Step 1: Add `ostLayoutBands` (DOM measurement) and `ostCenterRoot`**

Port mockup `layoutBands` (lines 589–625) and `centerOnRoot` (577–584), renamed, with the band color map keyed `outcome/opp/sol`. Bands present depend on which `data-band` nodes exist, so partial data self-adjusts.

```js
  function ostCenterRoot(canvas){
    if(!canvas) return;
    var node = canvas.querySelector('.n-outcome');
    if(!node || canvas.scrollWidth <= canvas.clientWidth) return;
    var cr = canvas.getBoundingClientRect(), nr = node.getBoundingClientRect();
    canvas.scrollLeft = (nr.left - cr.left) + canvas.scrollLeft + nr.width/2 - canvas.clientWidth/2;
  }
  function ostLayoutBands(board, bands){ /* exact port of mockup layoutBands, minus the `cut` arg */ }
```

(`bands` for horizontal = `[{key:'outcome',label:'Product outcome'},{key:'opp',label:'Möjligheter',sub:'opportunities'}]`; vertical adds `{key:'sol',label:'Lösningar',sub:'solutions'}`.)

- [ ] **Step 2: Add the toggle UI + `ostSetCut`**

```js
  function ostRenderSeg(cut){
    document.getElementById('ost-seg').innerHTML =
      '<button data-cut="h" class="' + (cut==='h'?'active':'') + '">Opportunity space</button>' +
      '<button data-cut="v" class="' + (cut==='v'?'active':'') + '"><span class="dir">↧</span> Chosen branch</button>';
  }
  function ostSetCut(container, cut){
    var data = container.__ostData;
    ostRenderSeg(cut);
    var wrap = document.getElementById('ost-treewrap');
    var board = document.getElementById('ost-board');
    var bands;
    if(cut==='h'){
      ostRenderHorizontal(data, wrap);
      bands = [{key:'outcome',label:'Product outcome'},{key:'opp',label:'Möjligheter',sub:'opportunities'}];
      document.getElementById('ost-antaganden').classList.add('hidden');
    } else {
      ostRenderVertical(data, wrap);
      bands = [{key:'outcome',label:'Product outcome'},{key:'opp',label:'Möjligheter',sub:'opportunity'},{key:'sol',label:'Lösningar',sub:'solutions'}];
      ostRenderTable(data, document.getElementById('ost-antaganden')); // Task 6
      document.getElementById('ost-antaganden').classList.remove('hidden');
    }
    ostLayoutBands(board, bands);
    ostCenterRoot(board.querySelector('.canvas'));
    container.__ostCut = cut;
  }
```

- [ ] **Step 2b: Stub `ostRenderTable` so Task 5 runs standalone**

```js
  function ostRenderTable(data, mount){ mount.innerHTML = ''; } // replaced in Task 6
```

- [ ] **Step 3: Wire auto-default + delegated toggle click + resize into `renderTree`**

Replace the tail of `renderTree` (after building the shell + stashing data) with:

```js
    container.__ostData = data;
    var defaultCut = data.hasOpp ? 'v' : 'h';
    document.getElementById('ost-seg').addEventListener('click', function(e){
      var b = e.target.closest('[data-cut]');
      if(b) ostSetCut(container, b.dataset.cut);
    });
    if(!window.__ostResizeBound){
      window.__ostResizeBound = true;
      window.addEventListener('resize', function(){
        clearTimeout(window.__ostT);
        window.__ostT = setTimeout(function(){
          var c = document.querySelector('.ost-tree-tab');
          if(c && c.parentElement && c.parentElement.__ostData) ostSetCut(c.parentElement, c.parentElement.__ostCut || 'h');
        }, 120);
      });
    }
    ostSetCut(container, defaultCut);
```

(Remove the direct `ostRenderHorizontal(...)` call from Task 4 Step 4 — `ostSetCut` now owns first render.)

- [ ] **Step 4: Verify toggle + auto-default + bands**

Refresh `?round=.`. Expected: opens on the **vertical** cut (fixture has a chosen opp). Swimlane bands tint behind the tree with sticky left labels. Toggle to "Opportunity space" → horizontal cut, two bands, no table. Toggle back → vertical, three bands + (empty) table area. Resize the window → bands re-measure and stay aligned.

- [ ] **Step 5: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-207): cut toggle, phase auto-default, DOM-measured bands, center+resize"
```

---

## Task 6: Assumption table (2-axis risk, sparse tests, coming-soon cols, empty states)

**Files:**
- Modify: `product-discovery/templates/viewer/index.html` — replace the `ostRenderTable` stub.
- Test: `/tmp/ost-tree-smoke.mjs` (extend).

- [ ] **Step 1: Extend the smoke test with `buildAssumptionRows`**

Append to `/tmp/ost-tree-smoke.mjs`:

```js
const valExp = JSON.parse(fs.readFileSync(`${F}/_working/validation-experiments.json`));
function buildAssumptionRows(blocks){
  return blocks.map(b => ({
    solId: b.solution_id, solTitle: b.solution_title,
    rows: (b.assumptions||[]).map(a => ({
      text: a.text, category: a.category,
      importance: a.importance || null, evidence: a.evidence || null,
      riskiest: !!a.is_riskiest,
      test: a.recommended_test ? a.recommended_test.test_type : null,
      success: a.recommended_test ? a.recommended_test.success_criteria : null
    }))
  }));
}
const groups = buildAssumptionRows(valExp.assumptions_per_solution);
const allRows = groups.flatMap(g => g.rows);
console.assert(groups.length === 3, 'three solution groups');
console.assert(allRows.some(r => r.riskiest && r.test), 'riskiest rows carry a test');
console.assert(allRows.some(r => !r.riskiest && !r.test), 'non-riskiest rows have no test (sparse)');
console.assert(allRows.every(r => ['desirability','usability','feasibility','viability','other'].includes(r.category)), 'valid categories');
console.log(`OK table — ${groups.length} groups, ${allRows.length} rows, ${allRows.filter(r=>r.riskiest).length} riskiest`);
```

- [ ] **Step 2: Run it — expect green**

```bash
node /tmp/ost-tree-smoke.mjs
```
Expected: both `OK` lines print; table assertions pass.

- [ ] **Step 3: Add the Swedish label maps + chip helpers**

```js
  var OST_CAT = { desirability:['Önskvärdhet','ons'], usability:['Användbarhet','anv'],
    feasibility:['Genomförbarhet','gen'], viability:['Lönsamhet','lon'], other:['Övrigt','ovr'] };
  function ostCatChip(c){ var m = OST_CAT[c] || ['—','ovr'];
    return '<span class="chip chip-typ ' + m[1] + '">' + esc(m[0]) + '</span>'; }
  function ostAxisChip(val, hiWord){ // importance: high/low ; evidence: strong/weak
    if(!val) return '<span class="chip chip-axis lo">—</span>';
    var hi = (val === hiWord);
    var sv = ({high:'Hög',low:'Låg',strong:'Starkt',weak:'Svagt'})[val] || val;
    return '<span class="chip chip-axis ' + (hi?'hi':'lo') + '">' + sv + '</span>';
  }
```

- [ ] **Step 4: Implement `ostRenderTable` (replaces the stub)**

`buildAssumptionRows` goes in the HTML too (copy from the smoke test). Columns: `#`, Antagande, Lösning, **Betydelse**, **Bevis**, Riskigast, Typ av antagande, Testmetod, Framgångskriterier, then greyed Status / Issue ID / Insikter.

```js
  function buildAssumptionRows(blocks){ /* exact copy from the smoke test */ }

  function ostRenderTable(data, mount){
    var groups = buildAssumptionRows(data.assumBlocks);
    var SOON = ['Status','Issue ID','Insikter'];
    var COLS = ['Antagande','Lösning','Betydelse','Bevis','Riskigast','Typ av antagande','Testmetod','Framgångskriterier'];
    if(!groups.length){
      mount.innerHTML = '<div class="tbl-head"><span class="title">Antaganden</span></div>' +
        '<div class="tbl-card"><div class="tbl-empty">Inga antaganden ännu — kör fas 3.</div></div>';
      return;
    }
    var solIndex = {};
    data.solutions.forEach(function(s,i){ solIndex[s.id] = 'S' + (i+1); });
    var head = '<thead><tr><th class="idx"></th>' +
      COLS.map(function(h){ return '<th>' + esc(h) + '</th>'; }).join('') +
      SOON.map(function(h){ return '<th class="soon">' + esc(h) + '<span class="tag">(coming soon)</span></th>'; }).join('') +
      '</tr></thead>';
    var n = 0, body = '';
    groups.forEach(function(g){
      body += '<tr class="grp"><td colspan="' + (1+COLS.length+SOON.length) + '">' +
        '<div class="grp-label"><span class="node-tag">' + esc(solIndex[g.solId]||'') + '</span>' + esc(g.solTitle) +
        '<span class="grp-count">' + g.rows.length + ' antaganden</span></div></td></tr>';
      if(!g.rows.length){
        body += '<tr><td class="idx"></td><td colspan="' + (COLS.length+SOON.length) + '" style="color:var(--sc-grey-400);font-style:italic;">Inga antaganden ännu för den här lösningen.</td></tr>';
        return;
      }
      g.rows.forEach(function(r){
        n++;
        body += '<tr class="' + (r.riskiest?'risky':'') + '">' +
          '<td class="idx">' + n + '</td>' +
          '<td class="assum-txt">' + esc(r.text) + '</td>' +
          '<td><span class="chip chip-sol">' + esc(solIndex[g.solId]||'') + '</span></td>' +
          '<td>' + ostAxisChip(r.importance,'high') + '</td>' +
          '<td>' + ostAxisChip(r.evidence,'strong') + '</td>' +
          '<td>' + (r.riskiest ? '<span class="flag-riskiest">Riskigast</span>' : '') + '</td>' +
          '<td>' + ostCatChip(r.category) + '</td>' +
          '<td class="test">' + (r.test ? esc(r.test) : '—') + '</td>' +
          '<td class="succ">' + (r.success ? esc(r.success) : '—') + '</td>' +
          '<td class="soon">—</td><td class="soon">—</td><td class="soon">—</td>' +
        '</tr>';
      });
    });
    mount.innerHTML = '<div class="tbl-head"><span class="title">Antaganden</span></div>' +
      '<div class="tbl-card"><div class="tbl-scroll"><table class="assum">' + head + '<tbody>' + body + '</tbody></table></div></div>';
  }
```

- [ ] **Step 5: Verify the table against the fixture**

Refresh `?round=.` (vertical cut). Expected: three solution groups (S1/S2/S3) with headers + counts; each assumption row shows Betydelse (Hög/Låg) and Bevis (Starkt/Svagt) chips; `is_riskiest` rows have the red left rule + a "Riskigast" flag and carry Testmetod + Framgångskriterier; non-riskiest rows show `—` in those two columns; Status/Issue ID/Insikter columns are hatched "(coming soon)"; category chips are color-coded with correct Swedish labels.

- [ ] **Step 6: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-207): assumption table — 2-axis risk, sparse tests, coming-soon cols"
```

---

## Task 7: Reading-guide banner, empty-state pass, cleanup, fixture safety

**Files:**
- Modify: `product-discovery/templates/viewer/index.html` — `VIEW_GUIDE` map; verify empty paths.

- [ ] **Step 1: Add a "how to read this" guide entry for the tree**

The synthetic `tree` view doesn't go through `injectGuide` (that runs for file-backed views). Render the banner inside `renderTree` instead, reusing the existing guide markup classes. Add at the top of the `.ost-tree-tab` innerHTML:

```js
        '<div class="tab-guide-banner"><b>How to read this</b> — the Opportunity Solution Tree. ' +
        '<b>Opportunity space</b> shows every opportunity branching off the outcome (the chosen one is marked “Vald”). ' +
        '<b>Chosen branch</b> drills the chosen opportunity down through the top-3 solutions to the assumptions that must hold. ' +
        'Switch with the toggle.</div>' +
```

(Match the class the other banners use — check `injectGuide` for the exact wrapper class and reuse it for visual consistency.)

- [ ] **Step 2: Manually verify empty/partial states**

Use a scratch round with thinner data:

```bash
mkdir -p /tmp/ost-empty/_working
printf '{"schema_version":"1.0","product_outcome":"Test outcome","decided":{}}' > /tmp/ost-empty/decisions.json
cp product-discovery/fixtures/golden/expected-output/OST-discovery/_working/experience-map-clustered.json /tmp/ost-empty/_working/
lsof -ti:3000 | xargs -r kill
python3 product-discovery/templates/viewer/serve.py --data /tmp/ost-empty --port 3000 &
sleep 1; open "http://localhost:3000/_viewer/?round=."
```

Expected: no chosen opp ⇒ defaults to **horizontal** cut; opportunities still branch (none marked Vald); toggle to vertical shows "Ingen opportunity vald ännu" + "Inga lösningar ännu" placeholder + "Inga antaganden ännu" table empty state. No console errors.

- [ ] **Step 3: Remove the temporary smoke test**

```bash
rm -f /tmp/ost-tree-smoke.mjs
```

- [ ] **Step 4: Run the fixture safety gate (RUBRIC) before any fixture-adjacent commit**

We did not modify fixtures, but confirm no client identifiers leaked into the viewer template:

```bash
grep -niE "norrsken|licenstilldelning|delfi|vendure|xledger" product-discovery/templates/viewer/index.html || echo "clean"
```

Expected: `clean`.

- [ ] **Step 5: Final regression pass across all tabs on the golden fixture**

Restart the server pointed at the golden fixture (`?round=.`), click every tab (Tree, Overview, Comparison, Solutions, Riskiest, Experiments, Journey, Experience Map, Decisions). Expected: all render, Tree is default, no console errors.

- [ ] **Step 6: Commit**

```bash
git add product-discovery/templates/viewer/index.html
git commit -m "feat(SCI-207): tree reading-guide banner + empty-state polish"
```

---

## Self-review against the spec

- **One tree, two cuts, new default Tree tab** → Tasks 1, 4, 5. ✔
- **Horizontal: outcome → opportunity space via `parent_id`, chosen marked, others muted, stops at opp layer** → Task 2 (`buildOpportunityTree`), Task 4 (`ostRenderHorizontal`). ✔
- **Vertical: outcome → chosen opp → top-3 solutions → assumption table** → Task 4 (`ostRenderVertical`), Task 6. ✔
- **Auto-default by `decisions.json`, manual toggle override** → Task 5 Step 3. ✔
- **Pure-CSS tree, no libraries; DOM-measured bands; `--ost-*` over `--sc-*`** → Task 3, Task 5. ✔
- **Ignore journey phases; flatten then rebuild by parent_id** → Task 2 Step 1. ✔
- **Carry real solution IDs; assumptions grouped by solution** → Task 6 (`solIndex` maps real `solution_id`→display Sn; grouping by `solution_id`). ✔
- **Risk = 2×2 (Betydelse/Bevis) + riskiest flag** → Task 3 Step 3, Task 6 Steps 3–4. ✔
- **Testmetod/Framgångskriterier sparse (riskiest only)** → Task 6 Step 4 (`r.test ? … : '—'`), asserted in Step 1. ✔
- **Status/Issue ID/Insikter greyed "(coming soon)"** → Task 6 Step 4 (`.soon` columns). ✔
- **Category enum → Swedish chips** → Task 6 Step 3 (`OST_CAT`). ✔
- **Partial/empty states degrade, don't error** → Task 4 (empty leaves), Task 6 (empty table), Task 7 Step 2. ✔
- **Data source precedence (validation→riskiest→categorized)** → Task 2 Step 3 (`loadTreeData`). ✔
- **Out of scope honored** (no editing, no living tree, scoring stays in Comparison, nesting ≤2 levels — the fixture's `parent_id` is single-level so the recursive builder handles ≤2 naturally) → no tasks add these. ✔

**Open decision flagged for Joni:** Task 1 Step 3 makes Tree displace Overview as the landing tab — confirm or revert that one line.
