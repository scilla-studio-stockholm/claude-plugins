# State

**Last session:** 2026-06-14
**Branch:** `master` (clean; all session work merged + published)

## Shipped this session (product-discovery 2.2.0 → 2.4.0)
- **SCI-207 — OST Tree view (2.3.0).** New default **Tree** tab: horizontal *Opportunity space* cut + vertical *Chosen branch* cut with the assumption table. Pure-CSS orthogonal tree, DOM-measured swimlane bands, `--ost-*` over `--sc-*`. Plus fixed two pre-existing renderers (Riskiest grid, Experiments) that read an obsolete flat schema and rendered empty.
- **SCI-230 — per-stage model tiering (2.3.1).** OST phase workflows pinned cheaper models on the 7 mechanical single-agent stages (haiku: merge/compose×2/categorize; sonnet: cluster×2/dedup); generative/judgment stages left inherited. Quality-neutral; loop opts use conditional spread so no `model:undefined` reaches the harness.
- **SCI-242 — viewer redesign to 4 surfaces (2.4.0).** 9 artifact tabs → **Tree · Prioritise · Journey · Table**. Journey has a Tree-style toggle (**User journey ⇄ Opportunities by phase**, defaults to User journey). **Table** = static denormalized **rollup** (one row per deepest leaf; ragged depth; sparse cells where a branch wasn't taken deeper). Header gained a read-only round gate-track. Overview/Decisions/Riskiest/Experiments/Solutions/Journey-Map tabs removed (folded in); 222 lines of dead code stripped.

Design artifacts in `docs/superpowers/specs/` + `docs/superpowers/plans/` (2026-06-13 tree, 2026-06-14 redesign).

## The architecture decision that frames the open tickets
**HTML renders, the terminal acts.** The viewer is a **static, read-only** per-iteration sense-making helper (NOT Torres' living OST). Only view-navigation in the page (tab/lens switching, toggles, collapsibles) — no download/sort/export/action controls. *Acting* on a round (start an experiment, spec a ticket, design a prototype) is a **terminal/skill** job. The header gate-track is pure status, not an action prompt.

## Open Linear tickets (filed this session, not started)
- [SCI-244](https://linear.app/scilla/issue/SCI-244) — define the OST post-discovery **action model** (knowledge anchor: action catalog · state→enabled-actions preconditions · likely-intent defaults · per-action output templates). **Blocks SCI-243.** Medium.
- [SCI-243](https://linear.app/scilla/issue/SCI-243) — the conversational **"act on this round" skill** (reads round JSON, asks what to act on, writes a Claude Design brief / Linear ticket / Claude Code prompt). A skill, not a one-shot agent. **Blocked by SCI-244.** Low.
- [SCI-247](https://linear.app/scilla/issue/SCI-247) — maybe promote Journey's "Opportunities by phase" to its own tab (vs the current toggle). Decide after real use. Low.

## Background tickets (untouched)
- [SCI-31](https://linear.app/scilla/issue/SCI-31) — hardcoded viewer score colors → `--sc-*` tokens. The viewer now has a clean `--ost-*`-over-`--sc-*` layer to extend. Backlog/Low.
- [SCI-27](https://linear.app/scilla/issue/SCI-27) — rename `ratifications.md` → `trio-decisions.md`. Likely superseded by SCI-53; candidate to close.

## Next steps
1. **Real-round trial** of the facilitator + redesigned viewer with a live trio (carried across two sessions now — it gates token optimization and informs SCI-243/247).
2. **SCI-244 → SCI-243** — the action layer. Build the action model first (it's the definition of "right"), then the skill; a golden/RUBRIC-style validation reference is a sub-task of SCI-243.
3. Token optimization beyond SCI-230: the big fan-outs (07 brainstorm, 10 generate, 9 agents each) need golden-reference validation before downgrading — do after a real run gives per-stage cost attribution.

## Gotchas
- **This repo IS the marketplace** (`autoUpdate: true`). Merging to `master` publishes. Teammates get 2.4.0 via `/plugin update product-discovery@scilla-studio` + restart.
- **Viewer launch:** `serve.py` is at `templates/serve.py` (NOT `templates/viewer/`); needs `--templates templates/viewer --data <OST-discovery dir> --port 3000`; browse `/_viewer/?round=.` (golden round path is `.`).
- **Visual verification is essential for viewer work** — subagent grep/ref checks can't catch runtime breaks. A curly-quote (smart-quote) paste blanked the whole viewer this session and only a headless screenshot caught it. Verify renders with `Google Chrome --headless --screenshot`; to screenshot a non-default tab, temporarily flip `switchView('tree')` then revert.
- **Cost reality (from `/cost-review` this session):** ~$1k of local-CLI spend on THIS repo over 22 days, cache_read-dominated (huge grounding contexts re-read per turn). cost-review scopes to the cwd's `~/.claude/projects/<encoded>` folder only — the heavy `pmf-analys` repo and any cloud/Cowork sessions are NOT included.
- Real client data lives at `../ost-skill-testbed/` (sibling, not in git). Never copy its content/names here; use `fixtures/golden/`.
- Knowledge anchors in `knowledge/discovery/*.md` are symlinked into each skill's `references/` and read verbatim at runtime — keep consistent with SKILL.md bodies.