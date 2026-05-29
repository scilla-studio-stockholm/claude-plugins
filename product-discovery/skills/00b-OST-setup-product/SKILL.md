---
name: OST-setup-product
description: For product trios starting OST discovery for a new product, when the discovery workspace needs both scaffolding and the product-context files filled in (product outcome and experience map), output a fully ready OST-discovery/ tree via a guided interview. Use when teammates say "set up OST for product X," "kick off OST discovery," or "start a new product in the discovery workspace." This is the high-level entrypoint that wraps OST-init-workspace plus the context-filling interview.
user_invocable: true
---

# OST-setup-product

The high-level entrypoint to the OST collection. Wraps `OST-init-workspace` (scaffold) plus a guided interview that fills the two product-context files downstream skills depend on: `product-outcome.md` and `experience-map.md`.

The workspace is **flat, single-product, single-round**: one `OST-discovery/` folder with `product-context/`, `_working/`, and `decisions.json`. Multi-product and multi-round nesting are opt-in and created manually only when needed — this skill never asks about or scaffolds them. See `references/workspace-scope.md`.

After this skill completes, the discovery workspace is **ready to run**: every downstream OST-* skill will find the context it needs and stop hard-exiting on TBD content.

## Prerequisites

- Run from the repo root where `OST-discovery/` should live.
- `OST-init-workspace` skill present in the same plugin (this skill calls its script).
- The trio has at least the rough material for a product outcome (the measurable customer-behavior change to move). The interview shapes it; it does not invent it.

## Steps

1. **Read the knowledge anchors:**
   - `references/workspace-scope.md` — the flat directory layout, scope resolution, slug rules, and the opt-in multi-product/multi-round conventions
   - `references/product-outcomes-i-olika-skeden.md` — what a good product outcome looks like at different product stages
   - `references/product-outcomes-vs-business-outcomes.md` — distinguish customer-behavior outcomes from business outcomes
   - `references/experience-mapping.md` — schema for the journey structure

   Apply these — do not invent.

2. **Gather scaffold inputs.** Ask one question at a time, wait for answer before the next:
   - `product` slug (apply slug rules; transliterate Swedish chars `å→a, ä→a, ö→o`; confirm with the user if you transliterate)
   - `date` — default to today; ask only if the user volunteers a back-date.

   Do NOT ask "one product or multiple?" or "have you decided which opportunity?" — the workspace is always flat single-product, single-round. Multi-product/multi-round nesting is opt-in and created manually later per `references/workspace-scope.md`.

3. **Run the scaffold script:**

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/00a-OST-init-workspace/scripts/init_workspace.sh" \
     --product <product> [--date YYYY-MM-DD]
   ```

   `--product` is the only required flag. Pass `--date` only if the user volunteered a back-date. The script accepts no other flags.

   Print the script's stdout verbatim so the user sees what was created vs. skipped.

4. **Inspect the context files.** The scope is `OST-discovery/` (flat). For each of the following, decide whether it needs the interview:
   - `OST-discovery/product-context/product-outcome.md` — read it; if the body still contains "TBD" or is empty after the frontmatter, mark as **needs interview**. Same for `OST-discovery/product-context/experience-map.md`.

   If everything is already filled, tell the user: "Workspace is already set up and all context files have content. Nothing to interview. Active scope: `OST-discovery/`." Stop.

5. **Interview: product outcome** (if needed). One question at a time:
   - "What customer behavior do you want to change? (the thing your users *do*, not what the business gets)"
   - "How do you measure that today? What's the current value or rough baseline?"
   - "What's the target value, and by when?"
   - If the answer drifts into business outcomes (revenue, retention as a number, conversion rate of a paid action), gently challenge using the distinction from `product-outcomes-vs-business-outcomes.md` and re-ask. Do not silently rewrite.
   - Compose a draft in the format: "Increase/Reduce [behavior] from [current] to [target] by [date]." Show the draft. Ask: "Does this capture the outcome correctly, or should I adjust?"
   - When confirmed, **write the full file** (replace the TBD body, preserve the frontmatter, set `date:` to today). Confirm the path written: `OST-discovery/product-context/product-outcome.md`.
   - After writing `product-outcome.md`, also update `OST-discovery/decisions.json`: set `product_outcome` to the full outcome formulation string. Read the existing `decisions.json`, update the field, write it back. The init script already created `decisions.json` at the scope root; never write to `_working/decisions.json`.

6. **Interview: experience map** (if needed). First fork on input mode:
   - Ask: "Do you have a screenshot of your experience map?"
   - **If yes:** "Save it at `OST-discovery/product-context/experience-map.png` (or .jpg). Tell me when it's saved." Once confirmed, tell the user: "Run `OST-extract-experience-map` to convert it into the structured schema. I'll leave `experience-map.md` as TBD — the extraction skill writes its output into `OST-discovery/_working/`, not the context folder." Skip writing this file.
   - **If no, and the user wants to write it directly:** Walk through the schema from `experience-mapping.md` — phases (name + friction level), steps within each phase, decision branches if any. One phase at a time. Compose the markdown rendering AND the matching JSON (per experience-mapping schema), show both, confirm, then write **to `_working/`** as `OST-discovery/_working/experience-map-extracted.md` and `OST-discovery/_working/experience-map-extracted.json`. Do NOT write to `product-context/experience-map.md` — downstream skills (`OST-cluster-opportunities`) require `experience-map-extracted.json` in `_working/`.
   - **If no, and the user wants to defer:** Tell them: "Leaving `experience-map.md` as TBD. Downstream skills that need the journey (`OST-cluster-opportunities`) will hard-exit until you either save a screenshot and run `OST-extract-experience-map`, or fill in the map by re-invoking `OST-setup-product`." Skip.

7. **Launch the viewer** (if any JSON was written). If `experience-map-extracted.json` was written in step 6, follow `knowledge/discovery/viewer-launch.md` to resolve the viewer path, start the server, and open the browser. If step 6 was deferred or delegated to `OST-extract-experience-map`, skip this step.

8. **Final summary.** After all interviews, print:
   - Files written (full paths)
   - Files still TBD with the remedy for each (e.g., "experience-map.md deferred — run `OST-extract-experience-map` after saving a screenshot")
   - Active scope: `OST-discovery/` (flat).
   - "Next OST-* skill to run" — `OST-opportunity-extractor` (the first phase-1 step: surface opportunities from interview transcripts).

## Output principles

- **One question at a time.** Wait for the answer before asking the next. This is a guided interview, not a form.
- **Knowledge-anchor before drafting.** Read the relevant reference file before composing a draft. Apply the framework; do not invent your own version.
- **Show, confirm, write.** Never write a context file without showing the draft and getting explicit confirmation. The user is the source of truth for their product outcome.
- **Challenge drift.** If the user's product outcome reads like a business outcome, push back with the reasoning from `product-outcomes-vs-business-outcomes.md`. Do not silently rewrite the user's outcome.
- **Defer gracefully.** Users can skip the experience map and come back later via `OST-extract-experience-map` or by re-invoking this skill. Print the deferred-file remedy in the final summary so the user does not need to remember.
- **Re-runnable.** Re-invoking on an already-filled workspace must short-circuit without re-interviewing. The init script is already idempotent; this skill's content-detection step in step 4 handles the rest.

## What this skill does NOT do

- Re-implement scaffolding. It calls `OST-init-workspace`'s script; it does not duplicate the directory creation logic.
- Run downstream OST-* skills (`OST-extract-experience-map`, `OST-brainstorm-solutions`, etc.). It points at the right next skill in the final summary; the user invokes it.
- Overwrite existing context content. Once a file is filled, this skill leaves it alone on re-runs. To edit, the user edits the file directly.
- Invent a product outcome the user didn't provide. The interview shapes their material into the right format; it does not generate outcomes from thin air. If the user does not have a rough outcome in mind, the skill tells them to come back when they do.
- Select or cite an opportunity. The flat workspace has no chosen-opportunity file at setup — opportunity selection happens downstream in the pipeline (`OST-opportunity-extractor` → ... → `OST-select-opportunity`, which writes `1-opportunity.md`).
- Scaffold multi-product or multi-round nesting. The default is flat single-product, single-round; nesting is opt-in and created manually per `references/workspace-scope.md`.
