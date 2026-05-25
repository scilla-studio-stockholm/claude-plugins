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

**Last session (2026-05-25):** decisions.json refactor + prerequisites README + PR workflow test.

**Changes shipped (2026-05-25):**
- **decisions.json refactor (PR #3, merged)** — Single `decisions.json` per discovery round replaces per-skill JSON files as the durable record. Schema at `knowledge/discovery/decisions-json-schema.md`. HITL gate skills (06, 09, 12, 13) write their section; downstream skills (07, 08, 10) read from it. `chosen-opportunity.md` and `ratifications.md` deprecated as skill inputs.
- **Prerequisites section in README** — Documents what trios need before starting (product outcome, experience map, cleaned transcripts).
- **Review fix** — Skill 09 step contradiction resolved; skill 10 pick-swap remedy note added.

**OST-compare-opportunities HTML design (2026-05-22, still current):**
- Swim-lane card layout (phases as columns), sorted by strong-count DESC then weak-count ASC, expandable `<details>` for rationales. Self-contained file, ~50 LOC inline JS for filter chips.
- Three additive JSON fields: `summary_title`, `score_counts`, `journey_phases`. Schema stays v0.1.
- Filter chips: `strong-heavy (≥3 strongs)`, `has weak`, `has unknown`. AND-combined.
- JSON+MD+HTML ship as a paired triple from a single render pass. Markdown is the tabular view, HTML is the skim view.

**Known issue: `summary_title` quality in Metria fixture.** The 96 titles in `comparison-matrix.json` are quote fragments, not the 3-6 word noun phrases the spec requires. This is from the original render before the title generation instructions were finalized. A fresh render will regenerate them correctly. Low priority — cosmetic only.

**Cost-review decisions (still relevant):**
- Stdlib-only Python, single `scripts/analyze_costs.py`. Topic filter is generic substring (≥3 hits). API list pricing, not actual bill.

**Open ticket:**
- [SCI-27](https://linear.app/scilla/issue/SCI-27) — Rename `ratifications.md` to `trio-decisions.md` across OST plugin. Lower priority now that `ratifications.md` is deprecated as a skill input; consider closing as won't-fix.

**Design decisions made this session:**
- **Three-layer artifact model:** (1) brainstorming slop (intermediate outputs, markdown-only, disposable), (2) the Opportunity Solution Tree (living cross-round artifact, not yet built), (3) `decisions.json` (per-round ratified decisions). The OST is the library; each round is one checkout from it.
- **`extract-experience-map` belongs in Phase 0** — it's a one-time setup step, not recurring. Renumbering to `00c` is a future task.
- **Implicit ratification** — skills write `decided.*` at run time; trio approves or edits. Shift from explicit creation of `chosen-opportunity.md`/`ratifications.md`.

**Next steps (when picked up):**
- First live workshop with a real trio (OST-compare-opportunities + OST-setup-product).
- Build the Opportunity Solution Tree as a living artifact (separate design needed — accumulates validated opportunities across rounds under a product outcome).
- Move intermediate files to `_working/` subfolder (follow-up to decisions.json refactor).
- Move `extract-experience-map` to Phase 0 (`00c`).
- SCI-27: consider closing as won't-fix given `ratifications.md` deprecation.

**Gotchas:**
- Plugin name in `plugin.json` matches folder name (e.g. `scilla-research` for both).
- Plugin cache won't auto-refresh mid-session — copy `<plugin>/skills/<skill>/` into the cache manually if you want to test immediately after changes.
- Skill folders now have numeric prefixes (e.g. `05-OST-compare-opportunities`) but the `name:` field in SKILL.md is the canonical identifier — folder name is for human navigation only.

## Session Startup
- Run `git status` to understand current repo state
- Read the **Current State** section above
- Ask if we should pick up where we left off or start something new
