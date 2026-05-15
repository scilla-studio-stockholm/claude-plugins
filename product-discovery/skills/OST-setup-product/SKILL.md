---
name: OST-setup-product
description: For product trios starting OST discovery for a new product, when the workspace needs both scaffolding and the product-context files filled in (product outcome, experience map, optional opportunity citation), output a fully ready workspace via a guided interview. Use when teammates say "set up OST for product X," "kick off OST discovery," or "start a new product in the discovery workspace." This is the high-level entrypoint that wraps OST-init-workspace plus the context-filling interview.
user_invocable: true
---

# OST-setup-product

The high-level entrypoint to the OST collection. Wraps `OST-init-workspace` (scaffold) plus a guided interview that fills the three context files downstream skills depend on: `product-outcome.md`, `experience-map.md`, and (optional) `chosen-opportunity.md`.

After this skill completes, the workspace is **ready to run**: every downstream OST-* skill will find the context it needs and stop hard-exiting on TBD content.

## Prerequisites

- Run from the repo root where `workspace/` should live.
- `OST-init-workspace` skill present in the same plugin (this skill calls its script).
- The trio has at least the rough material for a product outcome (the measurable customer-behavior change to move). The interview shapes it; it does not invent it.

## Steps

1. **Read the knowledge anchors:**
   - `references/workspace-scope.md` — directory hierarchy, scope resolution, slug rules
   - `references/product-outcomes-i-olika-skeden.md` — what a good product outcome looks like at different product stages
   - `references/product-outcomes-vs-business-outcomes.md` — distinguish customer-behavior outcomes from business outcomes
   - `references/experience-mapping.md` — schema v0.1 for the journey structure
   - `references/opportunity-citation-format.md` — citation format for chosen opportunities

   Apply these — do not invent.

2. **Gather scaffold inputs.** Ask one question at a time, wait for answer before the next:
   - `team` slug (apply slug rules; transliterate Swedish chars `å→a, ä→a, ö→o`; confirm with the user if you transliterate)
   - `product` slug (same rules)
   - Round type — ask: "Is this the start of a portfolio round (validating/comparing opportunities) or a discovery round (a specific opportunity has already been ratified)?" Map to `--portfolio` or `--opportunity <slug>`. If discovery, ask for the opportunity slug.
   - `date` — default to today; ask only if the user volunteers a back-date.

3. **Run the scaffold script:**

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/OST-init-workspace/scripts/init_workspace.sh" \
     --team <team> --product <product> \
     [--opportunity <opp>] [--portfolio] [--date YYYY-MM-DD]
   ```

   Print the script's stdout verbatim so the user sees what was created vs. skipped.

4. **Inspect the context files.** For each of the following, decide whether it needs the interview:
   - `workspace/<team>/<product>/_product-context/product-outcome.md` — read it; if the body still contains "TBD" or is empty after the frontmatter, mark as **needs interview**. Same for `experience-map.md`.
   - If `--opportunity` was given: `workspace/<team>/<product>/opportunities/<opp>/chosen-opportunity.md` — read it; mark as **needs interview** if the opportunity body is still TBD.

   If everything is already filled, tell the user: "Workspace is already set up and all context files have content. Nothing to interview. Active scope: `<path>` (from `workspace/.current-scope`)." Stop.

5. **Interview: product outcome** (if needed). One question at a time:
   - "What customer behavior do you want to change? (the thing your users *do*, not what the business gets)"
   - "How do you measure that today? What's the current value or rough baseline?"
   - "What's the target value, and by when?"
   - If the answer drifts into business outcomes (revenue, retention as a number, conversion rate of a paid action), gently challenge using the distinction from `product-outcomes-vs-business-outcomes.md` and re-ask. Do not silently rewrite.
   - Compose a draft in the format: "Increase/Reduce [behavior] from [current] to [target] by [date]." Show the draft. Ask: "Does this capture the outcome correctly, or should I adjust?"
   - When confirmed, **write the full file** (replace the TBD body, preserve the frontmatter, set `date:` to today). Confirm the path written.

6. **Interview: experience map** (if needed). First fork on input mode:
   - Ask: "Do you have a screenshot of your experience map?"
   - **If yes:** "Save it at `workspace/<team>/<product>/_product-context/experience-map.png` (or .jpg). Tell me when it's saved." Once confirmed, tell the user: "Run `OST-extract-experience-map` to convert it into the structured schema. I'll leave `experience-map.md` as TBD — the extraction skill writes its output into the active round folder, not the context folder." Skip writing this file.
   - **If no, and the user wants to write it directly:** Walk through the schema from `experience-mapping.md` — phases (name + friction level), steps within each phase, decision branches if any. One phase at a time. Compose the markdown rendering, show, confirm, write.
   - **If no, and the user wants to defer:** Tell them: "Leaving `experience-map.md` as TBD. Downstream skills that need the journey (`OST-cluster-opportunities`) will hard-exit until you either save a screenshot and run `OST-extract-experience-map`, or re-invoke `OST-setup-product` to fill it in." Skip.

7. **Interview: chosen opportunity** (if needed). One question at a time:
   - "Who said this? (role + interview reference if you have one)"
   - "What did they say? Paste the verbatim quote if you have it; otherwise the closest paraphrase you remember."
   - "What's the underlying job-to-be-done? What were they trying to accomplish when they said that?"
   - "Why did the trio pick this opportunity over the alternatives compared in the portfolio round?"
   - Compose the citation per `opportunity-citation-format.md` (quote + source + tweaks marked with `[square brackets]`). Show the draft. Confirm. Write.

8. **Final summary.** After all interviews, print:
   - Files written (full paths)
   - Files still TBD with the remedy for each (e.g., "experience-map.md deferred — run `OST-extract-experience-map` after saving a screenshot")
   - Active scope from `workspace/.current-scope`
   - "Next OST-* skill to run" — pick the right one based on round type: portfolio → `OST-opportunity-extractor`, discovery → `OST-brainstorm-solutions`.

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
