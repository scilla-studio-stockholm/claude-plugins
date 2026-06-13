# State

**Last session:** 2026-06-13
**Branch:** `master` (clean; SCI-207 merged + published)

## Shipped this session — OST Tree view (product-discovery 2.2.0 → 2.3.0)
**SCI-207** — the viewer now renders the actual Opportunity Solution Tree. New default **Tree** tab, merged to master (`aa46750`, = published to the marketplace). Built brainstorm → spec → plan → subagent-driven execution (7 tasks), verified with headless-browser screenshots against the golden fixture.

- **One tree, two cuts** in a new default Tree tab (Overview moved to 2nd):
  - *Opportunity space* (horizontal/breadth): outcome → full opportunity space via `parent_id`, chosen opp marked (`Vald`), others muted, stops at opp layer.
  - *Chosen branch* (vertical/depth): outcome → chosen opp → top-3 solutions → **Antaganden** table.
- **Antaganden table:** all assumptions grouped by solution; risk as the **2×2** (Betydelse=importance, Bevis=evidence) + `is_riskiest` flag; Testmetod/Framgångskriterier **sparse** (riskiest rows only, `—` otherwise); Status/Issue ID/Insikter greyed "(coming soon)".
- **Build:** vanilla `renderTree()` in `templates/viewer/index.html`, pure-CSS orthogonal tree (no libraries), DOM-measured swimlane bands, `--ost-*` tokens over `--sc-*`, phase auto-default from `decisions.json` + manual toggle.
- **Data layer:** `loadTreeData` sources the full assumption set from `riskiest-assumptions.json` (33 rows w/ axes) and merges test cards from `validation-experiments.json` by assumption id. `buildOpportunityTree` flattens `phases[].opportunities[]` and rebuilds hierarchy by `parent_id` (ignores journey phases), filters to `verdict==approved` + chosen.
- **Bonus fixes (same file):** Riskiest Assumptions grid + Experiments tab were reading an obsolete flat schema and rendering empty — now read v0.2 `assumptions_per_solution[]` nesting (21 riskiest in red quadrant, 21 test cards).

Design artifacts: `docs/superpowers/specs/2026-06-13-ost-tree-view-design.md` (spec), `…-design-brief.md` (design-Claude brief), `ost-tree-view-mockup/` (vendored mockup + rationale), `docs/superpowers/plans/2026-06-13-ost-tree-view.md` (plan).

## Recent decisions
- **Tree is the default landing tab** (Overview → 2nd), per the ticket. One-line revert (`switchView('tree')` → `'overview'`) if reconsidered.
- **Two cuts, not one giant tree** — breadth view for choosing an opportunity, depth view for working the chosen branch (assumptions as a table). Matches how coached teams actually use it.
- **Merged direct to master, no PR review** — user's call ("small project"). Published to team without a review pass.
- Minor version bump (new feature). Risk rendered as the 2×2, not a single level (the riskiest method's whole point).

## Open Linear tickets (background, not touched this session)
- [SCI-31](https://linear.app/scilla/issue/SCI-31) — Replace hardcoded viewer score colors with `--sc-*` tokens. Backlog/Low. (Tree view added a clean `--ost-*`-over-`--sc-*` layer — a good pattern to extend to the older renderers.)
- [SCI-27](https://linear.app/scilla/issue/SCI-27) — Rename `ratifications.md` → `trio-decisions.md`. Likely superseded by SCI-53; candidate to close.

## Next steps
1. **Click through the shipped viewer** once (it published without review) — Tree both cuts, Riskiest/Experiments tabs. Quick follow-up if anything's off.
2. **Real-round trial** of the facilitator + viewer with a live trio (carried from last session — see actual quality headroom before optimizing).
3. **Token-cost optimization** (unticketed) — phase runs ~450–650k subagent tokens; trim per-stage grounding once trusted. Quality-neutral only (SCI-53).
4. **Viewer IA redesign** (deferred from SCI-206) — overview-first, phase-sequenced. Tree tab is now the centerpiece it can build around.

## Gotchas
- **This repo IS the marketplace** (`autoUpdate: true`). Merging to `master` publishes. Teammates get 2.3.0 via `/plugin update product-discovery@scilla-studio` + restart.
- **Viewer launch:** `serve.py` lives at `templates/serve.py` (NOT `templates/viewer/`) and needs `--templates templates/viewer --data <OST-discovery dir> --port 3000`; browse `/_viewer/?round=<rel-path>`. (An earlier plan draft had the wrong command.) Golden fixture round path is `.`.
- **Tree feature relies on real data shapes:** opp text = `quote`; chosen opp from `decisions.json.decided.opportunity.id`; solutions from `top-three-solutions.json.picks` (fallback `decisions…picks`); assumptions from riskiest (all 33 + axes) merged with validation (test cards, riskiest only). The three assumption JSONs differ: categorized=33 no axes, riskiest=33 w/axes, validation=21 riskiest-only w/tests.
- Real client data still lives at `../ost-skill-testbed/` (sibling, not in git). Never copy its content/names here; use `fixtures/golden/`. Pre-existing client-name exposure in a few committed files unchanged (user: "it's fine").
- Headless screenshots used for verification: `Google Chrome --headless --screenshot=… <url>` works; `--dump-dom` greps are inflated by the inlined `<style>` block (count rendered rows via in-table markers like `grp-count`, not CSS-selector substrings).