# claude-plugins

Scilla Studio Claude Code skills/plugins library. Five collections:
- `scilla-research/` — 9 PM/research skills (competitive teardown, CSV summarizer, feedback triage, JTBD interview planner, knowledge capture/finder, research docs, transcript cleaner, **cost-review**)
- `scilla-writing/` — 2 writing skills (case study, LinkedIn post)
- `prototype-kit/` — 4 prototype skills (add-component, add-prototype, design-system, setup-kit)
- `product-discovery/` — 15 OST (Opportunity Solution Tree) skills for workshop-driven discovery (13 phase assists + `OST-init-workspace` for scaffolding + `OST-setup-product` as the guided entrypoint)
- `scilla-claude-toolkit/` — 2 meta-skills for managing the way of working with Claude (`wrapup`, `whats-new`)

Marketplace: `scilla-studio` (GitHub source: `scilla-studio-stockholm/claude-plugins`, `autoUpdate: true`). Plugin cache mirrors at `~/.claude/plugins/cache/scilla-studio/<plugin-name>/1.0.0/`. With autoUpdate on, the marketplace clone (`~/.claude/plugins/marketplaces/scilla-studio/`) pulls from GitHub on session start; force-sync within a session by copying `<plugin>/skills/<skill>/` into the cache path.

## Iteration workflow

**Editing a skill locally:**
1. Edit files in `/Users/jonilindgren/claude-projects/claude-plugins/<plugin>/skills/<skill>/`
2. `git commit && git push origin master`
3. To test in the current session: `cp -R <plugin>/skills/<skill>/ ~/.claude/plugins/cache/scilla-studio/<plugin>/1.0.0/skills/` — then restart Claude Code so skill metadata reloads
4. To test from a fresh session: just restart — autoUpdate will pull from GitHub automatically

**Team install (one-time):**
```
/plugin marketplace add scilla-studio-stockholm/claude-plugins
/plugin install scilla-research@scilla-studio
/plugin install scilla-writing@scilla-studio
/plugin install product-discovery@scilla-studio
/plugin install prototype-kit@scilla-studio
/plugin install scilla-claude-toolkit@scilla-studio
```
Teammates need GitHub auth (`gh auth login`) since the repo is private.

**Update propagation:** Each plugin install pins a `gitCommitSha`. With `autoUpdate: true` on the marketplace, the marketplace clone refreshes on session start. To pull a newer pinned commit into a plugin cache, teammates run `/plugin update <plugin>@scilla-studio` or `/plugin marketplace update scilla-studio`. Skills reload on session start, so an in-progress session won't see updates until restart.

## Current State

**Last session (2026-05-25):** decisions.json refactor, OST viewer template, Journey Map renderer, Linear→GitHub pipeline setup.

**Changes shipped (2026-05-25):**
- **decisions.json refactor (PR #3)** — Single `decisions.json` per round replaces per-skill JSON files. Schema at `knowledge/discovery/decisions-json-schema.md`. HITL gate skills write; downstream skills read. `chosen-opportunity.md` and `ratifications.md` deprecated as skill inputs.
- **OST viewer template (PR #5, SCI-30)** — Standalone viewer app at `templates/viewer/index.html` renders skill JSON output using scilla brand tokens. Dual-mount `serve.py` serves viewer from plugin + data from workspace. 7 view renderers. Spec at `docs/superpowers/specs/2026-05-25-ost-viewer-template-design.md`.
- **Journey Map renderer (PR #9, SCI-33)** — New "Journey Map" tab renders `experience-map-extracted.json` (skill 01 output) as a flowchart-style journey visualization with phase columns, step cards, SVG arrow overlay, decision branches, rejection paths, and hover highlighting. Design based on Claude Design prototype. Spec at `docs/superpowers/specs/2026-05-25-experience-map-renderer-design.md`.
- **Prerequisites section in README** — Documents what trios need before starting.

**Design decisions (still current):**
- **Three-layer artifact model:** (1) brainstorming slop (disposable), (2) Opportunity Solution Tree (living cross-round, not yet built), (3) `decisions.json` (per-round ratified decisions).
- **Viewer architecture:** Skills write JSON only, never HTML. Viewer fetches JSON via local server, renders client-side. Template lives in plugin repo, auto-updates via `autoUpdate: true`. Designer iterates on HTML/CSS without running skills.
- **`extract-experience-map` belongs in Phase 0** — one-time setup, not recurring.
- **Implicit ratification** — skills write `decided.*` at run time; trio approves or edits.

**Cost-review decisions (still relevant):**
- Stdlib-only Python, single `scripts/analyze_costs.py`. Topic filter is generic substring (≥3 hits). API list pricing, not actual bill.

**Open tickets:**
- [SCI-27](https://linear.app/scilla/issue/SCI-27) — Rename `ratifications.md` → `trio-decisions.md`. Consider closing as won't-fix.
- [SCI-31](https://linear.app/scilla/issue/SCI-31) — Replace hardcoded score colors in viewer with `--sc-*` tokens. Low priority.
- [SCI-32](https://linear.app/scilla/issue/SCI-32) — Remove inline HTML generation from skill 05. After viewer is validated with a real trio.
- [SCI-33](https://linear.app/scilla/issue/SCI-33) — Add Journey Map renderer to OST Viewer. PR #9 open.

**Next steps (when picked up):**
- Review and merge PR #9 (Journey Map renderer, SCI-33).
- Iterate on viewer design using scilla brand tokens (open `serve.py`, edit `index.html`, refresh).
- First live workshop with a real trio (OST-setup-product + viewer).
- Build the Opportunity Solution Tree as a living artifact (separate design needed).
- Move intermediate files to `_working/` subfolder.
- Move `extract-experience-map` to Phase 0 (`00c`).

**Gotchas:**
- Plugin name in `plugin.json` matches folder name (e.g. `scilla-research` for both).
- Plugin cache won't auto-refresh mid-session — copy `<plugin>/skills/<skill>/` into the cache manually if you want to test immediately after changes.
- Skill folders now have numeric prefixes (e.g. `05-OST-compare-opportunities`) but the `name:` field in SKILL.md is the canonical identifier — folder name is for human navigation only.

## Session Startup
- Run `git status` to understand current repo state
- Read the **Current State** section above
- Ask if we should pick up where we left off or start something new
