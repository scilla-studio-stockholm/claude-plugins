# Scilla Claude Toolkit

Scilla team's curated meta-skills for managing the way of working with Claude — not domain skills, but workflow helpers that keep sessions tidy and projects pickup-friendly.

## Install

Requires the `scilla-studio` marketplace (private repo — needs `gh auth login`):

```
/plugin marketplace add scilla-studio-stockholm/claude-plugins
/plugin install scilla-claude-toolkit@scilla-studio
```

Updates pull automatically on session start (`autoUpdate: true`). Force-update mid-session:

```
/plugin update scilla-claude-toolkit@scilla-studio
```

## Skills Included

### 1. Wrapup (`wrapup`)
Captures session context into project files so the next session can pick up seamlessly.

**Triggers:**
- `/wrapup`
- "wrap up", "end session", "save progress"

**What it does:** Reviews the conversation, extracts touched Linear ticket IDs from git/PRs (with optional Linear MCP enrichment), updates a `STATE.md` (or project-specific source-of-truth files), and offers to commit the wrapup. CLAUDE.md is treated as orientation only — state never gets embedded there.

### 2. What's New (`whats-new`)
Pulls recent Claude/Anthropic updates and explains what they mean for the current project.

**Triggers:**
- `/whats-new`
- "what's new in Claude", "any new Claude features"

**What it does:** Fetches the Claude blog, Claude Code GitHub releases, and SDK changelogs in parallel; compares them against the project's stack and conventions; produces a short brief of what matters and what to ignore. Tracks last-seen versions in `~/.claude-whats-new/` so repeat runs only show what's new.
