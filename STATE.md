# State

**Last session:** 2026-05-29
**Branch:** `master` (clean; SCI-53 merged + published)

## Shipped this session — SCI-53 (PR #37, merged)
OST `product-discovery` redesign, Track A (artifact model + folder structure). Bumped to **2.0.0** (breaking) and published to the marketplace via the master merge.
- Flat `OST-discovery/` workspace: all phase JSON + plumbing markdown in `_working/`; only 4 self-contained milestone docs (`1-opportunity.md`…`4-experiments.md`) + `decisions.json` + `product-context/` at the scope root. A full run went from ~27 files to 5 at root.
- Renamed `discovery/` → `OST-discovery/`; dropped two-mode/dated-round/`_product-context/` structure (multi-product + multi-round are now opt-in, documented in `knowledge/discovery/workspace-scope.md`).
- `init_workspace.sh` simplified to flat (`--product`/`--date` only); 00b setup reconciled to it.
- Viewer (`templates/viewer/index.html`) reads view JSON from `_working/`, `decisions.json` from the scope root.
- `MIGRATION.md` added for converting existing `discovery/` workspaces.
- Spec: `docs/superpowers/specs/2026-05-29-ost-artifact-model-and-speed-redesign-design.md`. Plan: `docs/superpowers/plans/2026-05-29-ost-track-a-artifact-folder-redesign.md`.

## Next steps
1. **Golden-run validation (deferred, Joni testing live).** Full pipeline 00b→13 on a real input; check the rubric: 5 files at `OST-discovery/` root, phase 07 still yields 18 candidates, phase 10 still runs multi-method passes, milestone docs self-contained, viewer tabs all render. If a regression surfaces → fast 2.0.1.
2. **Track B (speed)** — own spec, quality-neutral levers only: measure first; compress (not remove) grounding; stop re-reading the knowledge base every skill; kill redundant JSON re-parsing. Gate on a golden baseline existing. Not yet a Linear ticket.

## Open Linear tickets
- [SCI-31](https://linear.app/scilla/issue/SCI-31) — Replace hardcoded viewer score colors with `--sc-*` tokens. Backlog/Low. Still valid.
- [SCI-27](https://linear.app/scilla/issue/SCI-27) — Rename `ratifications.md` → `trio-decisions.md`. **Likely superseded by SCI-53**: `ratifications.md` is now deprecated (not written or read in the flat model). Candidate to close as won't-fix.

## Recent decisions
- Artifact model = milestone/plumbing split. Milestones are self-contained — they embed the decision-relevant upstream reasoning (alternatives + comparison) so a reader never opens `_working/`.
- Flat single-product is the default; multi-product/multi-round nesting is opt-in (see `workspace-scope.md`).
- 2.0.0 is a breaking major — existing workspaces need `MIGRATION.md`.
- Speed work (Track B) may NOT cut role-diversified divergence or thin grounding depth — those ARE the quality. Levers must be quality-neutral.
- Three-layer artifact model still holds: (1) brainstorming slop (disposable, now in `_working/`), (2) Opportunity Solution Tree (living cross-round, still not built), (3) `decisions.json` (per-round ratified record).

## Gotchas
- **This repo IS the marketplace source** (`autoUpdate: true`). Merging to `master` publishes. Teammates get 2.0.0 via `/plugin update product-discovery@scilla-studio` + restart; the cache path moves `…/product-discovery/1.0.0/` → `…/2.0.0/`.
- Plugin cache won't auto-refresh mid-session — copy `<plugin>/skills/<skill>/` into the cache to test changes immediately.
- `knowledge/discovery/*.md` anchors are **symlinked** into each skill's `references/` and read verbatim at runtime — keep them consistent with the SKILL.md bodies when editing (they were a missed surface in this redesign until the final integration review caught them).
- Skill folder numeric prefixes (e.g. `06-OST-select-opportunity`) are for human navigation; the `name:` field in SKILL.md is the canonical identifier.
