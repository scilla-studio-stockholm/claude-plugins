# claude-plugins

Personal Claude Code skills/plugins library. Three collections:
- `joni-skills/` — 9 PM/research skills (competitive teardown, CSV summarizer, feedback triage, JTBD interview planner, knowledge capture/finder, research docs, transcript cleaner, **cost-review**)
- `joni-writing/` — 2 writing skills (case study, LinkedIn post)
- `prototype-kit/` — 4 prototype skills (add-component, add-prototype, design-system, setup-kit)

Marketplace: `joni-local` (registered as `directory` source, `autoUpdate: true`). Plugin cache mirrors at `~/.claude/plugins/cache/joni-local/joniskills/1.0.0/`. After changes, the cache auto-updates between sessions; force-sync within a session by copying `joni-skills/skills/<skill>/` into the cache path.

## Current State

**In progress:** Nothing active. Last shipped: `cost-review` skill (2026-05-14), merged to `master`.

**Recent decisions (cost-review build, 2026-05-14):**
- Stdlib-only Python (no pip), single `scripts/analyze_costs.py` + thin SKILL.md + reference doc. Matches `transcript-cleaner` shape.
- Topic filter is generic case-insensitive substring (≥3 hits); cannot replicate domain-curated marker lists. Pick distinctive substrings (`skills-design/`, `OST-`) — bare common tokens (e.g. "OST") match metadata in every session.
- High-cache-write detector uses **token-ratio** (`cw / (cw + cr) > 50%`), not the spec's original cost-ratio — corrected mid-build because cost-ratio false-fired on healthy usage.
- Output-heavy detector caps at top-5 sessions + tail line ("…and N more").
- API list pricing (April 2026), not actual Pro/Max bill. Stated as caveat everywhere.

**Next steps (when picked up):**
- Output-heavy detector tip "use Edit instead of Write" overfit in observed sessions — actual driver was subagent dispatches and Edit volume, not Write. Consider adding a sub-detector or rephrasing the tip to point at where the output actually came from.
- Daily timeline bar scale uses all-time max, not 30-day max — recent bars get compressed when older days dominated. Minor cosmetic.
- `(estimated)` suffix breaks per-model column alignment. Cosmetic.
- DESIGN.md `Open questions` is empty; can stay.

**Gotchas:**
- `joniskills` (plugin name in `plugin.json`) vs `joni-skills` (folder name). Both correct.
- Plugin cache won't auto-refresh mid-session — copy `joni-skills/skills/<skill>/` into the cache manually if you want to test immediately after changes.
- `cost-review --topic OST` on a large project reports ~$4.7K, not yesterday's $1.27K manual figure. Not a bug: substring filter is broader than a curated marker list. Document, don't fix.

## Session Startup
- Run `git status` to understand current repo state
- Read the **Current State** section above
- Ask if we should pick up where we left off or start something new
