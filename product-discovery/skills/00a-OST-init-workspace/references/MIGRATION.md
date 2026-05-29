# Migrating an existing discovery/ workspace to OST-discovery/

The OST workspace layout was simplified. Follow these steps to convert an
existing `discovery/` tree to the new flat `OST-discovery/` layout.

1. Rename the top folder: `discovery/` -> `OST-discovery/`.
2. Rename `_product-context/` -> `product-context/`.
3. For each round folder, create a `_working/` subfolder and MOVE into it
   every file EXCEPT `decisions.json` and any `1-`..`4-*.md` milestone docs.
   (All the paired `*.{md,json}` phase artifacts are now plumbing and live in
   `_working/`.)
4. Rename the gate proposal files to their milestone names if present:
   - `chosen-opportunity-proposal.md` -> `1-opportunity.md`
   - `top-three-solutions.md`         -> `2-solutions.md`
   - `riskiest-assumptions.md`        -> `3-riskiest-assumptions.md`
   - `validation-experiments.md`      -> `4-experiments.md`
   If a run predates the self-contained milestone docs, re-run the
   corresponding gate skill (06 / 09 / 12 / 13) to regenerate them so they
   stand alone.
5. If the repo has only one product and one round, flatten it: the round
   folder's contents become the `OST-discovery/` root, and `product-context/`
   moves to `OST-discovery/product-context/`. Keep multi-product or
   multi-round nesting only if you actually have more than one (see
   workspace-scope.md for the opt-in nested layouts).
6. Update `OST-discovery/.current-scope` if it exists, or delete it for the
   flat default (the flat layout needs no scope pointer).

After migrating, launch the viewer with `--data OST-discovery/` (or the active
scope folder). The viewer reads `decisions.json` from the scope root and all
other views from `_working/`.
