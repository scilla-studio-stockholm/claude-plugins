---
name: OST-run-opportunity-phase
description: Run the full OST opportunity phase (assists 02→06) as one workflow command. Use when a discovery trio has cleaned transcripts and an extracted experience map and wants extraction, validation, clustering, comparison, and the selection proposal in one run instead of invoking five skills sequentially. Stops at the trio HITL gate (1-opportunity.md + decisions.json).
---

# Run opportunity phase (workflow)

You launch the `ost-opportunity-phase` workflow, which executes assists 02→06 as one deterministic pipeline: per-transcript parallel extraction, merge, validation, clustering, Torres comparison, and the selection proposal. It stops at the existing trio HITL gate. The individual skills (02–06) remain the fallback path and the source of truth for each stage's behavior — the workflow's agents execute those SKILL.md files verbatim.

## Steps

1. **Resolve scope.** Follow `references/workspace-scope.md`. The scope is `OST-discovery/` itself in the default flat layout.

2. **Check prerequisites.** Hard-exit (tell the user what is missing and which skill produces it; launch nothing) unless all of these exist:
   - `<scope>/_working/experience-map-extracted.json` (from `OST-extract-experience-map`)
   - `<scope>/product-context/product-outcome.md` with a `## Outcome` section
   - `<scope>/decisions.json`

3. **Confirm transcript inputs.** If the user gave file paths, use them. If they gave a folder, list the transcript files, skip non-transcript siblings (synthesis docs, coaching notes), and confirm the list with the user before launching. Transcripts must be cleaned with speaker labels; if not, recommend `scilla-research:transcript-cleaner` first and exit.

4. **Resolve the plugin root** — the directory containing this plugin's `skills/` folder (this skill lives at `<pluginRoot>/skills/00c-OST-run-opportunity-phase/`).

5. **Launch the workflow** with the Workflow tool:
   - `scriptPath`: `<pluginRoot>/workflows/ost-opportunity-phase.js`
   - `args`: `{ "pluginRoot": "<pluginRoot>", "scope": "<absolute scope path>", "transcripts": [<absolute transcript paths>], "date": "<today YYYY-MM-DD>" }`

   Pass `transcripts` as an actual JSON array, not a string.

6. **When the workflow completes**, relay the result to the trio:
   - On `status: awaiting_trio_hitl`: point them at `<scope>/1-opportunity.md` and explain the HITL step — review the proposal, override by editing `decided.opportunity` in `decisions.json` if they disagree. Next phase after ratification: `OST-brainstorm-solutions`.
   - On `stopped_at: <stage>`: relay the stage's ERROR block verbatim, including its Remedy line. The pipeline wrote nothing downstream of the failed stage; after the remedy, the run can be repeated (or the remaining stages run via the individual skills 03–06).

## What this skill does NOT do

- Re-implement any stage logic. Stage behavior lives in the SKILL.md files of assists 02–06; this skill only orchestrates.
- Run phase 01 (experience-map extraction) or 00b (product setup) — those are prerequisites.
- Ratify the opportunity. The trio's HITL edit of `decisions.json` stays manual.
- Launch the viewer mid-run. Offer `knowledge/discovery/viewer-launch.md` after completion if the trio wants the visual view.
