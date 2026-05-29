---
name: OST-setup-product
description: For product trios starting OST discovery for a new product, when the discovery workspace needs both scaffolding and the product-context files filled in (product outcome, experience map, optional opportunity citation), output a fully ready OST-discovery/ tree via a guided interview. Use when teammates say "set up OST for product X," "kick off OST discovery," or "start a new product in the discovery workspace." This is the high-level entrypoint that wraps OST-init-workspace plus the context-filling interview.
user_invocable: true
---

# OST-setup-product

The high-level entrypoint to the OST collection. Wraps `OST-init-workspace` (scaffold) plus a guided interview that fills the three context files downstream skills depend on: `product-outcome.md`, `experience-map.md`, and (optional) `chosen-opportunity.md`.

After this skill completes, the discovery workspace is **ready to run**: every downstream OST-* skill will find the context it needs and stop hard-exiting on TBD content.

## Prerequisites

- Run from the repo root where `OST-discovery/` should live.
- `OST-init-workspace` skill present in the same plugin (this skill calls its script).
- The trio has at least the rough material for a product outcome (the measurable customer-behavior change to move). The interview shapes it; it does not invent it.

## Steps

1. **Read the knowledge anchors:**
   - `references/workspace-scope.md` — directory hierarchy (both modes), scope resolution, slug rules
   - `references/product-outcomes-i-olika-skeden.md` — what a good product outcome looks like at different product stages
   - `references/product-outcomes-vs-business-outcomes.md` — distinguish customer-behavior outcomes from business outcomes
   - `references/experience-mapping.md` — schema v0.1 for the journey structure
   - `references/opportunity-citation-format.md` — citation format for chosen opportunities

   Apply these — do not invent.

2. **Gather scaffold inputs.** Ask one question at a time, wait for answer before the next:
   - **Layout mode** — ask: "Will this repo hold work for one product only, or multiple products/teams?" Map "one product" → `--single-product`; "multiple" → multi-product mode (then ask for `team` slug).
   - `product` slug (apply slug rules; transliterate Swedish chars `å→a, ä→a, ö→o`; confirm with the user if you transliterate)
   - Round type — ask: "Have you already decided which opportunity to pursue, or are you still figuring out which one to pick?" Map "still figuring out" → `--selection` (opportunity-selection round); "already decided" → `--opportunity <slug>` (discovery round, then ask for the opportunity slug).
   - `date` — default to today; ask only if the user volunteers a back-date.

3. **Run the scaffold script:**

   Multi-product mode:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/00a-OST-init-workspace/scripts/init_workspace.sh" \
     --team <team> --product <product> \
     [--opportunity <opp>] [--selection] [--date YYYY-MM-DD]
   ```

   Single-product mode:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/00a-OST-init-workspace/scripts/init_workspace.sh" \
     --single-product --product <product> \
     [--opportunity <opp>] [--selection] [--date YYYY-MM-DD]
   ```

   Print the script's stdout verbatim so the user sees what was created vs. skipped.

4. **Inspect the context files.** For each of the following, decide whether it needs the interview:
   - `<product-root>/_product-context/product-outcome.md` — read it; if the body still contains "TBD" or is empty after the frontmatter, mark as **needs interview**. Same for `experience-map.md`.
   - If `--opportunity` was given: `<product-root>/opportunities/<opp>/chosen-opportunity.md` — read it; mark as **needs interview** if the opportunity body is still TBD.

   `<product-root>` is `OST-discovery/` in single-product mode, or `OST-discovery/<team>/<product>/` in multi-product mode.

   If everything is already filled, tell the user: "Workspace is already set up and all context files have content. Nothing to interview. Active scope: `<path>` (from `OST-discovery/.current-scope`)." Stop.

5. **Interview: product outcome** (if needed). One question at a time:
   - "What customer behavior do you want to change? (the thing your users *do*, not what the business gets)"
   - "How do you measure that today? What's the current value or rough baseline?"
   - "What's the target value, and by when?"
   - If the answer drifts into business outcomes (revenue, retention as a number, conversion rate of a paid action), gently challenge using the distinction from `product-outcomes-vs-business-outcomes.md` and re-ask. Do not silently rewrite.
   - Compose a draft in the format: "Increase/Reduce [behavior] from [current] to [target] by [date]." Show the draft. Ask: "Does this capture the outcome correctly, or should I adjust?"
   - When confirmed, **write the full file** (replace the TBD body, preserve the frontmatter, set `date:` to today). Confirm the path written.
   - After writing `product-outcome.md`, also update `decisions.json` in the active round folder: set `product_outcome` to the full outcome formulation string. Read the existing `decisions.json`, update the field, write it back. If `decisions.json` does not exist yet (round not scaffolded), skip this step.

6. **Interview: experience map** (if needed). First fork on input mode:
   - Ask: "Do you have a screenshot of your experience map?"
   - **If yes:** "Save it at `<product-root>/_product-context/experience-map.png` (or .jpg). Tell me when it's saved." Once confirmed, tell the user: "Run `OST-extract-experience-map` to convert it into the structured schema. I'll leave `experience-map.md` as TBD — the extraction skill writes its output into the active round folder, not the context folder." Skip writing this file.
   - **If no, and the user wants to write it directly:** Walk through the schema from `experience-mapping.md` — phases (name + friction level), steps within each phase, decision branches if any. One phase at a time. Compose the markdown rendering AND the matching JSON (per experience-mapping schema v0.2), show both, confirm, then write **to the active round folder** as `<scope>/experience-map-extracted.md` and `<scope>/experience-map-extracted.json`. Do NOT write to `_product-context/experience-map.md` — downstream skills (`OST-cluster-opportunities`) require `experience-map-extracted.json` in the round folder.
   - **If no, and the user wants to defer:** Tell them: "Leaving `experience-map.md` as TBD. Downstream skills that need the journey (`OST-cluster-opportunities`) will hard-exit until you either save a screenshot and run `OST-extract-experience-map`, or fill in the map by re-invoking `OST-setup-product`." Skip.

7. **Interview: chosen opportunity** (if needed). One question at a time:
   - "What's the opportunity ID? (e.g. opp-3-2 — if this came from OST-select-opportunity, use the ID from the proposal)"
   - "Which journey phase does it belong to? (e.g. onboarding, search, checkout)"
   - "Who said this? (role + interview reference, e.g. P03, licensansvarig)"
   - "What did they say? Paste the verbatim quote if you have it; otherwise the closest paraphrase you remember."
   - "Why did the trio pick this opportunity over the alternatives?"
   - Compose the citation in the format downstream skills expect: `**<opp-id>** (Phase: <phase-id>) - "<quote>" - *<source>*`. Apply tweak rules from `opportunity-citation-format.md` (tweaks in `[square brackets]`). Show the draft. Confirm.
   - Also compose the `## Product outcome` blockquote by copying the confirmed outcome from `product-outcome.md`.
   - Write both sections into `chosen-opportunity.md`, replacing the TBD placeholders. Write the rationale into the `### Rationale` subsection.

8. **Launch the viewer** (if any JSON was written). If `experience-map-extracted.json` was written in step 6, follow `knowledge/discovery/viewer-launch.md` to resolve the viewer path, start the server, and open the browser. If step 6 was deferred or delegated to `OST-extract-experience-map`, skip this step.

9. **Final summary.** After all interviews, print:
   - Files written (full paths)
   - Files still TBD with the remedy for each (e.g., "experience-map.md deferred — run `OST-extract-experience-map` after saving a screenshot")
   - Active scope: read `OST-discovery/.current-scope` and print the path. If `.current-scope` does NOT point at the round folder just created (e.g. because it already existed from a previous product), print a warning: "Note: `.current-scope` still points at `<old path>`, not the round you just set up. To switch, run: `echo '<new round path>' > OST-discovery/.current-scope`"
   - "Next OST-* skill to run" — pick the right one based on round type: opportunity-selection → `OST-opportunity-extractor`, discovery → `OST-brainstorm-solutions`.

## Output principles

- **One question at a time.** Wait for the answer before asking the next. This is a guided interview, not a form.
- **Knowledge-anchor before drafting.** Read the relevant reference file before composing a draft. Apply the framework; do not invent your own version.
- **Show, confirm, write.** Never write a context file without showing the draft and getting explicit confirmation. The user is the source of truth for their product outcome and opportunity citation.
- **Challenge drift.** If the user's product outcome reads like a business outcome, push back with the reasoning from `product-outcomes-vs-business-outcomes.md`. If the opportunity citation is a paraphrase that lost the customer's voice, ask for the verbatim quote.
- **Defer gracefully.** Users can skip the experience map and come back later via `OST-extract-experience-map` or by re-invoking this skill. Print the deferred-file remedy in the final summary so the user does not need to remember.
- **Re-runnable.** Re-invoking on an already-filled workspace must short-circuit without re-interviewing. The init script is already idempotent; this skill's content-detection step in step 4 handles the rest.

## What this skill does NOT do

- Re-implement scaffolding. It calls `OST-init-workspace`'s script; it does not duplicate the directory creation logic.
- Run downstream OST-* skills (`OST-extract-experience-map`, `OST-brainstorm-solutions`, etc.). It points at the right next skill in the final summary; the user invokes it.
- Overwrite existing context content. Once a file is filled, this skill leaves it alone on re-runs. To edit, the user edits the file directly.
- Invent a product outcome the user didn't provide. The interview shapes their material into the right format; it does not generate outcomes from thin air. If the user does not have a rough outcome in mind, the skill tells them to come back when they do.
- Handle ratifications (`ratifications.md`). That's a separate trio log, out of scope for setup.
- Validate the opportunity citation against the format rules. That's `OST-validate-opportunities` downstream.
