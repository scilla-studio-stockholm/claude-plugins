---
name: OST-init-workspace
description: Low-level scaffolding for the OST-discovery/ tree. Use when a repo needs the flat single-product discovery workspace created without running the full guided setup, or when invoked as a building block by OST-setup-product. For first-time setup of a new product, prefer OST-setup-product, which wraps this skill and also walks the trio through filling in product-outcome.md and experience-map.md.
user_invocable: true
---

# OST-init-workspace

Scaffolds the flat `OST-discovery/` directory tree, context templates, and an empty `decisions.json` that every other OST-* skill depends on. Without this scaffold, downstream skills hard-exit on missing files.

The default layout is flat, single-product, single-round:

```
OST-discovery/
├── product-context/   product-outcome.md, experience-map.md
├── _working/          all phase JSON + intermediate markdown (viewer data source)
└── decisions.json     ratified decisions (the spine), initialized empty
```

Multi-product and multi-round nesting are opt-in and created manually only when needed — they are documented in `references/workspace-scope.md`, not scaffolded by this script.

## Prerequisites

- Run from the repo root where the `OST-discovery/` directory should live.
- No other skills required.

## Steps

1. **Read the knowledge anchor** at `references/workspace-scope.md`. It defines the flat directory layout, canonical filenames, slug rules, and the opt-in multi-product/multi-round nesting. Apply these — do not invent.

2. **Get input from the user.** Required:
   - `product` slug (short, lowercase, ASCII; transliterate Swedish chars: `å→a, ä→a, ö→o`)

   Optional:
   - `date` (YYYY-MM-DD) — overrides today's date used in the template frontmatter. Useful for back-dating.

   If the user passes a Swedish name (e.g. "Sök på karta"), transliterate it to a slug (`sok-pa-karta`) and confirm with the user before scaffolding. The full Swedish title belongs in the file frontmatter, not the path.

3. **Run the scaffold script:**

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/00a-OST-init-workspace/scripts/init_workspace.sh" \
     --product <slug> [--date YYYY-MM-DD]
   ```

   The script is idempotent: existing files are never overwritten, only created if missing. Each action prints `CREATED`, `SKIPPED (exists)`, or `ERROR`. The summary at the end lists every path touched.

4. **Print the script's stdout verbatim.** Do not paraphrase paths or rename files. The script is the source of truth for what was scaffolded.

5. **Tell the user what to do next.** Pick the relevant pointer:
   - If `product-context/product-outcome.md` was newly created: "Open `OST-discovery/product-context/product-outcome.md` and write the product outcome before running any other OST skill. Skills hard-exit when this file is empty or contains the TBD placeholder."
   - If `product-context/experience-map.md` was newly created and no `.png/.jpg` is present: "Either save an experience-map screenshot at `OST-discovery/product-context/experience-map.png` and run `OST-extract-experience-map`, or run `OST-setup-product` to walk through the experience map interview (it writes `experience-map-extracted.{md,json}` into `_working/`, which is what downstream skills need)."

## Output principles

- **Idempotent always.** Re-running the skill on an existing discovery workspace must be safe. Never overwrite files. Print `SKIPPED (exists)` for anything already present.
- **No silent decisions.** If the user gives a non-slug input (uppercase, spaces, non-ASCII), transliterate to a slug and confirm before scaffolding. Do not scaffold under a wrong path and let the user discover it later.
- **Templates prompt for action.** Every template file written contains a `TBD` marker and a one-line instruction for what the human needs to fill in and why. Downstream OST skills already hard-exit on missing content; the TBD marker signals "this file exists but is not ready yet."
- **Flat by default.** The script scaffolds one flat single-product, single-round workspace. Multi-product and multi-round nesting are opt-in and created manually later (see `references/workspace-scope.md`); this skill does not scaffold them.

## What this skill does NOT do

- Write the product outcome or experience map. Those are the human's job; templates only prompt for them. `OST-setup-product` is the orchestrator that walks the trio through filling them in.
- Run downstream OST-* skills. After scaffolding, the user picks the next skill themselves.
- Migrate existing non-conforming directories into the convention. Out of scope; if the user has prior artifacts in a different layout, they move them manually.
- Set up the `product-discovery` plugin itself. That happens via `/plugin install product-discovery@scilla-studio` and is a prerequisite for this skill being available at all.
- Initialize git, create README.md at repo root, or touch anything outside `OST-discovery/`. The skill scopes its writes to `OST-discovery/` only.
