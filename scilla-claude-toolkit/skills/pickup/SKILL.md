---
name: pickup
description: Use when starting a work session and need to orient to where you left off. Use when the user says /pickup or asks "where was I", "what was I working on", "what are we doing today", "vad jobbade vi på senast", "vad är nästa steg", or similar pickup phrasings in English or Swedish.
---

# Session Pickup

Orient the user to where they left off in this repo and propose a ranked next step. Mirror image of the `wrapup` skill — `wrapup` writes state, `pickup` reads it and acts on what changed since.

**Core principle:** Don't act autonomously. Read state, detect what changed, propose, then wait for confirmation.

## Process

### 1. Detect where state lives

Mirror `wrapup`'s detection logic:

1. Read the project's `CLAUDE.md`. If it points to specific source-of-truth files (e.g. "Wave 1 scope is in `transformationsteamet/vag-1-idoarrt.md`", or "State lives in `STATE.md`"), read those.
2. Else, if `STATE.md` exists at the repo root, read it.
3. Else, if CLAUDE.md contains a legacy embedded `## Current State` section, read that and note it in the digest header — offer to migrate to `STATE.md` (don't auto-migrate).
4. Else (no state captured), tell the user explicitly: "No prior state captured in this repo. Want me to look at git log + open PRs as a fallback?" Don't fabricate.

### 2. Auto-orient

Run in parallel (skip git/gh steps if not in a git repo):

```
git fetch
git status
git worktree list
git log --oneline @{u}..HEAD
git log --oneline HEAD..@{u}
gh pr list --author @me --state all --json number,title,state,reviewDecision,mergedAt,updatedAt --limit 10
```

**Enrich with Linear MCP if available.** If a Linear MCP server is configured (any tool matching `mcp__linear*` or `mcp__claude_ai_Linear*` — the official remote server registers as `mcp__linear-server__*`), fetch current title + status for each `SCI-\d+` mentioned in the state files. This lets the digest reflect what's *now* true in Linear, not just what was true at last wrapup.

If `gh` isn't installed or authenticated, skip PR detection and note "(gh not available)" in the digest.

### 3. Diff vs last session

Compare auto-orient results against state-file contents. Explicitly call out:

- PRs that were open in state but are now merged or closed.
- Linear tickets whose status has changed (e.g., In Progress → Done).
- Upstream commits the local branch is now behind.
- Worktrees that have been removed since last session.

This "since then" line is the single most useful piece of the digest. Lead with it.

### 4. Rank next steps

Start from the state file's `Next steps` list, then adjust based on what auto-orient found:

- **Drop** items whose corresponding ticket/PR is now closed/merged.
- **Promote** items that became unblocked (e.g., a PR that's now approved is ready to merge).
- **Demote** items whose dependency hasn't moved (e.g., still waiting on someone else's review).

Re-rank by what is *now* actionable, not what was actionable at last wrapup. If you change the order, add a one-line "why this first" note next to the top item.

### 5. Present digest

Output format — drop empty sections:

```
## Pickup — <repo name>

**Last session:** YYYY-MM-DD · branch <name>
**Since then:** <one-line summary of what changed>

## Where you were
- <one-line summary from state's "In progress" section>

## Open work
- PRs: <list with current review state>
- Linear: <list with current status if MCP available>
- Worktrees: <list if more than one>

## Suggested next steps
1. <ranked, with one-line "why this first" if non-obvious>
2. ...

Want me to start with #1?
```

If the state file is more than 14 days old, prepend a "(state is N days old — picture may have drifted)" note to the header.

### 6. Wait for confirmation

Do not act on the suggested next step without explicit user confirmation. If the user says "yes" / "start with 1" / a Swedish equivalent, proceed. If the user names a different step, do that instead. If the user wants to do something not on the list, follow their direction.

## Edge cases

| Case | Behavior |
|---|---|
| No `STATE.md` and no embedded state | Tell user explicitly; offer git-log + open-PR fallback. Don't fabricate. |
| State file older than 14 days | Flag in digest header. |
| Not in a git repo | Skip all git/gh steps; just read state file. |
| `gh` not installed or not authenticated | Skip PR detection; note in digest. |
| Linear MCP not configured | Skip status enrichment; use IDs as-is from state file. |
| Multiple worktrees, ambiguous which to pick up | List them and ask which one. |
| Stale STATE.md mentions a deleted branch | Note "(branch deleted)" next to the entry; don't crash. |

## Rules

- Don't act without confirmation. Propose, then ask.
- Lead with what changed since last session. That's the most useful piece.
- If state is missing, say so plainly. Don't invent a "where you were" from git log alone — that's a fallback, not a substitute.
- Keep the digest scannable. The user should know in 30 seconds what's open and what to do next.
- The skill is read-only by default. It can run `git fetch` and `gh pr list` (both safe reads) but does not pull, push, checkout, or modify state.
