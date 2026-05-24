# claude-plugins

Scilla Studio Claude Code skills/plugins library. Four collections:
- `scilla-research/` — 9 PM/research skills (competitive teardown, CSV summarizer, feedback triage, JTBD interview planner, knowledge capture/finder, research docs, transcript cleaner, **cost-review**)
- `scilla-writing/` — 2 writing skills (case study, LinkedIn post)
- `prototype-kit/` — 4 prototype skills (add-component, add-prototype, design-system, setup-kit)
- `product-discovery/` — 15 OST (Opportunity Solution Tree) skills for workshop-driven discovery (13 phase assists + `OST-init-workspace` for scaffolding + `OST-setup-product` as the guided entrypoint)

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
```
Teammates need GitHub auth (`gh auth login`) since the repo is private.

**Update propagation:** Each plugin install pins a `gitCommitSha`. With `autoUpdate: true` on the marketplace, the marketplace clone refreshes on session start. To pull a newer pinned commit into a plugin cache, teammates run `/plugin update <plugin>@scilla-studio` or `/plugin marketplace update scilla-studio`. Skills reload on session start, so an in-progress session won't see updates until restart.

## Current State

**Last session (2026-05-24):** HITL verification of OST-compare-opportunities swim-lane HTML against Metria 96-opp fixture. Repo cleanup: numbered skill folders, deleted `skills-design/`, cleaned dangling references.

**Changes shipped this session:**
- CSS fix: added `overflow-wrap: anywhere` on `.swim-col` and `.card-detail` to prevent long quotes and rationales from overflowing card width. Also `min-width: 0` on `.swim-col` to let grid columns shrink below content width.
- Step index in HTML now grouped by phase with sequential numbering across all phases for at-a-glance ordering.
- Skill folders renamed with numeric prefixes (`00a-OST-init-workspace` through `13-OST-validation-experiment-designer`). `name:` field in SKILL.md frontmatter unchanged — skill invocation unaffected.
- Deleted `product-discovery/skills-design/` (build-time design docs, all decisions captured in CLAUDE.md and SKILL.md files). Cleaned all 14 dangling `skills-design/` references across 13 SKILL.md files.

**HITL verification status (Metria fixture):**
- Steps 5, 6, 8, 10 pass (JSON augmentation, markdown unchanged, self-contained HTML, sort order correct).
- Step 7 (visual check in browser): text wrapping fixed, remaining items need manual confirmation (filter chips, print preview, Safari).
- Steps 9, 11 not yet run (offline test, title cache re-render).
- A one-off Python render script (`render_swimlane.py`) was used to augment the JSON and render the HTML without re-running the full 480-cell analysis. Located in the Metria fixture folder — not part of the plugin.

**OST-compare-opportunities HTML design (2026-05-22, still current):**
- Swim-lane card layout (phases as columns), sorted by strong-count DESC then weak-count ASC, expandable `<details>` for rationales. Self-contained file, ~50 LOC inline JS for filter chips.
- Three additive JSON fields: `summary_title`, `score_counts`, `journey_phases`. Schema stays v0.1.
- Filter chips: `strong-heavy (≥3 strongs)`, `has weak`, `has unknown`. AND-combined.
- JSON+MD+HTML ship as a paired triple from a single render pass. Markdown is the tabular view, HTML is the skim view.

**Cost-review decisions (still relevant):**
- Stdlib-only Python, single `scripts/analyze_costs.py`. Topic filter is generic substring (≥3 hits). API list pricing, not actual bill.
- All three cosmetic issues fixed (2026-05-24).

**Next steps (when picked up):**
- `OST-compare-opportunities`: finish remaining HITL verification steps (filter chips, print preview, Safari, offline, title cache). Then first live workshop with a real trio.
- `OST-setup-product`: not yet tested with a real trio.
- `OST-init-workspace`: watch for teammate feedback on `--opportunity`/`--selection` split.

**Gotchas:**
- Plugin name in `plugin.json` matches folder name (e.g. `scilla-research` for both).
- Plugin cache won't auto-refresh mid-session — copy `<plugin>/skills/<skill>/` into the cache manually if you want to test immediately after changes.
- Skill folders now have numeric prefixes (e.g. `05-OST-compare-opportunities`) but the `name:` field in SKILL.md is the canonical identifier — folder name is for human navigation only.

## Session Startup
- Run `git status` to understand current repo state
- Read the **Current State** section above
- Ask if we should pick up where we left off or start something new
