# claude-plugins

Scilla Studio Claude Code skills/plugins library. Four collections:
- `scilla-research/` — 9 PM/research skills (competitive teardown, CSV summarizer, feedback triage, JTBD interview planner, knowledge capture/finder, research docs, transcript cleaner, **cost-review**)
- `scilla-writing/` — 2 writing skills (case study, LinkedIn post)
- `prototype-kit/` — 4 prototype skills (add-component, add-prototype, design-system, setup-kit)
- `product-discovery/` — 14 OST (Opportunity Solution Tree) skills for workshop-driven discovery (13 phase assists + `OST-init-workspace` for scaffolding)

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

**In progress:** Nothing active. Last shipped: `OST-init-workspace` skill (2026-05-15), merged to `master`.

**Recent decisions (OST-init-workspace build, 2026-05-15):**
- Closes the "OST skills assume Metria layout" gap. The 13 phase-assist skills reference `<scope>/../../_product-context/...` and `workspace/<team>/<product>/...` paths but no skill bundled the scaffold — teammates outside the original repo hit hard-exits on missing files. This skill bootstraps the structure.
- Bash + heredoc templates, no Python. Idempotent (`SKIPPED (exists)` on re-run, never overwrites). Matches the thin-SKILL-plus-script pattern from `cost-review`/`transcript-cleaner`.
- Args: `--team --product` required; `--opportunity` and `--portfolio` are mutually exclusive (a single `.current-scope` can only point at one round). `--date` overrides today for back-dating.
- Slug validation enforces the convention from `knowledge/discovery/workspace-scope.md`: lowercase ASCII, hyphen-separated. Swedish chars must be transliterated by the caller (`å→a, ä→a, ö→o`); script rejects with a clear message rather than guessing.
- Templates ship a `TBD` marker plus an inline comment explaining what to fill in and why. Downstream OST skills already hard-exit on empty content — the marker signals "exists but not ready" rather than masking failure.
- Workspace `README.md` orients teammates with the layout tree, scope-resolution rules, and a pointer to the canonical spec in the plugin source (`product-discovery/knowledge/discovery/workspace-scope.md`). Duplication is intentional — matches the existing per-skill `references/workspace-scope.md` pattern.

**Prior shipped:** `cost-review` skill (2026-05-14).

**Cost-review decisions (still relevant for follow-ups):**
- Stdlib-only Python (no pip), single `scripts/analyze_costs.py` + thin SKILL.md + reference doc.
- Topic filter is generic case-insensitive substring (≥3 hits); cannot replicate domain-curated marker lists. Pick distinctive substrings (`skills-design/`, `OST-`).
- High-cache-write detector uses **token-ratio** (`cw / (cw + cr) > 50%`), not the spec's original cost-ratio.
- Output-heavy detector caps at top-5 sessions + tail line ("…and N more").
- API list pricing (April 2026), not actual Pro/Max bill. Stated as caveat everywhere.

**Next steps (when picked up):**
- `OST-init-workspace`: no known issues from smoke testing. Watch for teammate feedback on whether the `--opportunity`/`--portfolio` split is intuitive or whether a single round-type flag reads better.
- `cost-review`: output-heavy detector tip "use Edit instead of Write" overfit in observed sessions — actual driver was subagent dispatches and Edit volume, not Write. Consider adding a sub-detector or rephrasing the tip.
- `cost-review`: daily timeline bar scale uses all-time max, not 30-day max — recent bars get compressed when older days dominated. Minor cosmetic.
- `cost-review`: `(estimated)` suffix breaks per-model column alignment. Cosmetic.

**Gotchas:**
- Plugin name in `plugin.json` matches folder name (e.g. `scilla-research` for both).
- Plugin cache won't auto-refresh mid-session — copy `<plugin>/skills/<skill>/` into the cache manually if you want to test immediately after changes.
- `cost-review --topic OST` on a large project reports ~$4.7K, not yesterday's $1.27K manual figure. Not a bug: substring filter is broader than a curated marker list. Document, don't fix.

## Session Startup
- Run `git status` to understand current repo state
- Read the **Current State** section above
- Ask if we should pick up where we left off or start something new
