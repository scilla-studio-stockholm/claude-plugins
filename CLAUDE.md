# claude-plugins

Scilla Studio Claude Code skills/plugins library. Five collections:
- `scilla-research/` — 9 PM/research skills (competitive teardown, CSV summarizer, feedback triage, JTBD interview planner, knowledge capture/finder, research docs, transcript cleaner, **cost-review**)
- `scilla-writing/` — 2 writing skills (case study, LinkedIn post)
- `prototype-kit/` — 4 prototype skills (add-component, add-prototype, design-system, setup-kit)
- `product-discovery/` — 16 OST (Opportunity Solution Tree) skills for workshop-driven discovery (13 phase assists + `OST-init-workspace` for scaffolding + `OST-setup-product` as the guided entrypoint + `OST-run-opportunity-phase` to run assists 02→06 as one workflow; the workflow script lives in `product-discovery/workflows/`)
- `scilla-claude-toolkit/` — 3 meta-skills for managing the way of working with Claude (`wrapup`, `whats-new`, `pickup`)

Marketplace: `scilla-studio` (GitHub source: `scilla-studio-stockholm/claude-plugins`, `autoUpdate: true`). Plugin cache mirrors at `~/.claude/plugins/cache/scilla-studio/<plugin-name>/1.0.0/`. With autoUpdate on, the marketplace clone (`~/.claude/plugins/marketplaces/scilla-studio/`) pulls from GitHub on session start; force-sync within a session by copying `<plugin>/skills/<skill>/` into the cache path.

## Test data

Two tiers for validating the OST pipeline:
- **Synthetic (in-repo, distributable):** `product-discovery/fixtures/golden/` — fictional Flowbase/Aurora case with 4 transcripts, frozen reference run, and `RUBRIC.md` checks.
- **Real (local only, NEVER in git):** `../ost-skill-testbed/` (sibling repo, not version-controlled here) — real client discovery data the golden fixture was derived from: `transcripts/` (4 cleaned interviews), `OST-discovery/` (full flat-2.0.0 reference run incl. `product-context/`), and the legacy pre-2.0 `discovery/` layout. Use it for realistic end-to-end testing. **Never copy its content, client/team/product names, or any identifying terms into this repo** — the synthetic golden fixture exists precisely so that data stays private. The fixture's `RUBRIC.md` safety gate must pass before committing fixture changes.

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

## Session state

Session state lives in `STATE.md` at the repo root — what shipped last session, open PRs/tickets, next steps, and gotchas. Keep it current via the `wrapup` skill; keep this file to orientation only.

## Session Startup
- Run `git status` to understand current repo state
- Read `STATE.md`
- Ask if we should pick up where we left off or start something new
