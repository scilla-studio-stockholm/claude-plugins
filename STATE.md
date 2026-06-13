# State

**Last session:** 2026-06-13
**Branch:** `master` (clean; all session PRs merged + published)

## Shipped this session — OST agent/workflow redesign (product-discovery 2.1.0 → 2.2.0)
Turned the slow, manually-chained OST skill pipeline into orchestrated phase workflows + a conversational facilitator, and added cross-round memory. Five PRs (#82–#86), all merged to master (= published to the marketplace).

- **SCI-195 (#82)** — `workflows/ost-opportunity-phase.js`: assists 02→06 as one pipeline (parallel per-transcript extraction → merge → validate → cluster → compare → select), stops at the trio HITL gate. Thin runner skill `00c-OST-run-opportunity-phase`.
- **SCI-196 (#83)** — `workflows/ost-solution-phase.js` (07→09; 3-round × 3-role blind brainstorm at script level) and `ost-assumption-phase.js` (10→12; preflight once, 9 method-pass agents + 3 dedup passes). Plus **`00-OST-facilitator`** skill: conversational discovery partner — orients from `decisions.json` via a state table, proposes the next move, launches workflows, walks HITL gates. (Shipped as a *skill*, not an `agents/` subagent — subagents are one-shot, can't hold the dialogue.)
- **SCI-197 (#84)** — living tree memory: `knowledge/discovery/living-tree.md` (schema for `tree.json`, the cross-round ledger) + `14-OST-record-round` skill (terminal write-back: appends round lineage + records experiment results). Read-side hooks in the facilitator and both phase workflows (prior killed solutions / invalidated assumptions = anti-context).
- **SCI-206 (#85)** — OST Viewer fixes + guidance: fixed journey-map clipping + dangling decision-branch arrows (cross-phase → first step; prose → exit chip), experience-map blank step labels (`step.description`) and duplicated opportunities. Added an **Overview** landing tab (OST explainer + phase tracker from `decisions.json`), per-view "how to read this" banners, and plain-language legends.
- **#86** — version bump to 2.2.0.

## Validation
Full 02→12 pipeline ran end-to-end on the golden fixture, chained on one scope at `/tmp/ost-pilot/OST-discovery/` (opportunity → solutions → assumptions, then `OST-record-round`). Each phase ~9–22 min unattended; converged with the frozen reference run (same chosen opportunity). Each PR passed the pr-merge-gatekeeper; two minor findings (skill-14 `recorded` field, viewer listener leak) were fixed before merge, not deferred.

## Next steps
1. **Real-round trial.** Have a trio run a live round through the facilitator before optimizing — see actual quality headroom first.
2. **Token-cost optimization (unticketed).** Each phase run is ~450–650k subagent tokens because stage agents execute the full SKILL.md verbatim. Trim per-stage grounding once the pattern is trusted. Quality-neutral levers only (per SCI-53). File a ticket when ready.
3. **Viewer full IA redesign (deferred from SCI-206).** SCI-206 patched within the current tab structure; an overview-first, phase-sequenced redesign was the deferred "Full redesign" option.

## Open Linear tickets (background, not touched this session)
- [SCI-31](https://linear.app/scilla/issue/SCI-31) — Replace hardcoded viewer score colors with `--sc-*` tokens. Backlog/Low. (Viewer changed in SCI-206 but this specific token cleanup remains.)
- [SCI-27](https://linear.app/scilla/issue/SCI-27) — Rename `ratifications.md` → `trio-decisions.md`. Likely superseded by SCI-53; candidate to close as won't-fix.

## Recent decisions
- Facilitator = skill, not subagent (needs to hold a conversation).
- Phase workflows execute the existing SKILL.md files verbatim → artifact/schema parity with the skill-by-skill path; skills 02–14 remain the fallback and source of truth. Orchestration overhead removed, reasoning untouched.
- Living tree carries **riskiest assumptions only**; absence of `tree.json` is never an error; append-mostly, byte-identical carry-through.
- Stacked PRs merged with **merge commits** (not squash) to keep shared ancestors so retargets stay conflict-free.

## Gotchas
- **This repo IS the marketplace** (`autoUpdate: true`). Merging to `master` publishes. Teammates get 2.2.0 via `/plugin update product-discovery@scilla-studio` + restart.
- **Real client data lives at `../ost-skill-testbed/`** (sibling repo, NOT version-controlled here) — Team Norrsken / Licenstilldelning. Never copy its content or identifying names into this repo; use the synthetic `fixtures/golden/` for anything committed. See CLAUDE.md "Test data".
- **Pre-existing client-name exposure in git** (not fixed — user said "it's fine"): "Norrsken"/"Licenstilldelning" appear in `knowledge/discovery/experience-mapping.md`, `fixtures/golden/RUBRIC.md` (the safety-gate blocklist itself), and a 2026-05-25 spec. Private repo, team-only. Content scrub or `git filter-repo` history rewrite available if priorities change.
- Knowledge anchors in `knowledge/discovery/*.md` are symlinked into each skill's `references/` and read verbatim at runtime — keep consistent with SKILL.md bodies when editing.
- Workflow contract: stage agents signal hard-exit by returning text starting `ERROR`; failures filtered with `filter(Boolean)`. Converged cleanly every run, but if a real run behaves oddly (silent transcript drop, non-string return) that's the first place to look.
