---
name: OST-init-workspace
description: Low-level scaffolding for the OST OST-discovery/ tree. Use when an existing workspace needs a new product, opportunity, or opportunity-selection round folder added without running the full guided setup, or when invoked as a building block by OST-setup-product. For first-time setup of a new product, prefer OST-setup-product, which wraps this skill and also walks the trio through filling in product-outcome.md, experience-map.md, and chosen-opportunity.md.
user_invocable: true
---

# OST-init-workspace

Scaffolds the `OST-discovery/` directory tree, context templates, round-folder READMEs, and `.current-scope` pointer that every other OST-* skill depends on. Without this scaffold, downstream skills hard-exit on missing files.

Two layout modes are supported:
- **Multi-product** (default): `OST-discovery/<team>/<product>/...` — for repos that hold work for multiple teams or products.
- **Single-product** (`--single-product`): `OST-discovery/...` directly — for repos that hold work for one product only.

Both modes use the same relative-path math, so all 13 phase OST-* skills work identically regardless of mode.

## Prerequisites

- Run from the repo root where the `OST-discovery/` directory should live.
- No other skills required.

## Steps

1. **Read the knowledge anchor** at `references/workspace-scope.md`. It defines the directory hierarchy (both modes), the scope-resolution protocol, canonical filenames, and slug rules. Apply these — do not invent.

2. **Get input from the user.** Required:
   - `product` slug (short, lowercase, ASCII; transliterate Swedish chars: `å→a, ä→a, ö→o`)
   - Layout mode: ask "Will this repo hold work for one product only, or multiple products/teams?"
     - One product → use `--single-product` (no team slug needed)
     - Multiple → use multi-product mode (also ask for `team` slug)

   Optional:
   - `opportunity` slug — if given, also scaffolds `opportunities/<opp>/chosen-opportunity.md` plus an empty discovery round folder dated today, and points `.current-scope` at that round.
   - `selection` flag — if set, scaffolds `opportunity-selection/<today>/` and points `.current-scope` there. Mutually exclusive with `opportunity`.
   - `date` (YYYY-MM-DD) — overrides today for the round folder name. Useful for back-dating.

   If the user passes a Swedish name (e.g. "Sök på karta"), transliterate it to a slug (`sok-pa-karta`) and confirm with the user before scaffolding. The full Swedish title belongs in the file frontmatter, not the path.

3. **Run the scaffold script:**

   Multi-product:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/00a-OST-init-workspace/scripts/init_workspace.sh" \
     --team <team> --product <product> \
     [--opportunity <opp>] [--selection] [--date YYYY-MM-DD]
   ```

   Single-product:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/00a-OST-init-workspace/scripts/init_workspace.sh" \
     --single-product --product <product> \
     [--opportunity <opp>] [--selection] [--date YYYY-MM-DD]
   ```

   The script is idempotent: existing files are never overwritten, only created if missing. Each action prints `CREATED`, `SKIPPED (exists)`, or `ERROR`. The summary at the end lists every path touched.

4. **Print the script's stdout verbatim.** Do not paraphrase paths or rename files. The script is the source of truth for what was scaffolded.

5. **Tell the user what to do next.** Pick the relevant pointer:
   - If `_product-context/product-outcome.md` was newly created: "Open `OST-discovery/.../_product-context/product-outcome.md` and write the product outcome before running any other OST skill. Skills hard-exit when this file is empty or contains the TBD placeholder."
   - If `_product-context/experience-map.md` was newly created and no `.png/.jpg` is present: "Either save an experience-map screenshot at `_product-context/experience-map.png` and run `OST-extract-experience-map`, or run `OST-setup-product` to walk through the experience map interview (it writes `experience-map-extracted.{md,json}` into the active round folder, which is what downstream skills need)."
   - If `.current-scope` was set: "Scope is set to `<path>`. Open the round folder's `README.md` to see what files will land there. Subsequent OST-* skills will read/write inside that folder unless you pass `scope=` explicitly."

## Output principles

- **Idempotent always.** Re-running the skill on an existing discovery workspace must be safe. Never overwrite files. Print `SKIPPED (exists)` for anything already present.
- **No silent decisions.** If the user gives a non-slug input (uppercase, spaces, non-ASCII), transliterate to a slug and confirm before scaffolding. Do not scaffold under a wrong path and let the user discover it later.
- **Templates prompt for action.** Every template file written contains a `TBD` marker and a one-line instruction for what the human needs to fill in and why. Downstream OST skills already hard-exit on missing content; the TBD marker signals "this file exists but is not ready yet."
- **Round folders document themselves.** Each round folder (under `opportunity-selection/` or under `opportunities/<opp>/`) gets a `README.md` listing the canonical files that will land there and which OST-* skill produces each. The user can open the folder and see what's coming without consulting the spec.
- **One scaffold per invocation.** If the user wants to add a second opportunity later, they re-invoke with the new `opportunity=` value. Do not try to scaffold multiple opportunities in one call.

## What this skill does NOT do

- Write the product outcome, experience map, or opportunity citation. Those are the human's job; templates only prompt for them. `OST-setup-product` is the orchestrator that walks the trio through filling them in.
- Run downstream OST-* skills. After scaffolding, the user picks the next skill themselves.
- Migrate existing non-conforming directories into the convention. Out of scope; if the user has prior artifacts in a different layout, they move them manually.
- Set up the `product-discovery` plugin itself. That happens via `/plugin install product-discovery@scilla-studio` and is a prerequisite for this skill being available at all.
- Initialize git, create README.md at repo root, or touch anything outside `OST-discovery/`. The skill scopes its writes to `OST-discovery/` only.
