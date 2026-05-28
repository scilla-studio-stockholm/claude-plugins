# pickup skill — design

**Date:** 2026-05-28
**Plugin:** `scilla-claude-toolkit`
**Status:** Approved by Joni, ready for implementation plan
**Related:** mirror image of the `wrapup` skill in the same plugin.

## Problem

Jumping between many projects and cloud repos, Joni forgets where he left off in each one. The existing `wrapup` skill captures session-end state into `STATE.md` (or project-specific source-of-truth files), but there is no symmetric session-start skill that reads that state, orients to what has changed since, and proposes a concrete next step.

## Goal

A `/pickup` slash command that, on entering a project, produces a short orientation digest and a ranked list of suggested next steps — ending with a single confirmation prompt before acting.

## Trigger

- Slash command: `/pickup`
- Natural-language triggers (English):
  - "where was I"
  - "pick up"
  - "what was I working on"
  - "what are we doing today"
  - "what was the last thing I worked on"
- Natural-language triggers (Swedish):
  - "vad ska vi börja med i den här sessionen"
  - "vad jobbade vi på senast"
  - "vad är nästa steg"

## Activeness

**Read + auto-orient, then propose.** The skill reads state, runs external checks to detect what changed since the last session, presents a digest plus ranked next steps, and asks for confirmation before acting. It does not act autonomously.

Rejected alternatives:
- *Read-only digest* — too passive; user has to drive every follow-up.
- *Digest + propose + start* — too pushy; removes the confirmation gate.

## Process

### 1. Detect where state lives

Mirror `wrapup`'s detection logic:

1. Read the project's `CLAUDE.md`. If it points to specific source-of-truth files (e.g. "Wave 1 scope is in `transformationsteamet/vag-1-idoarrt.md`", or "State lives in `STATE.md`"), read those.
2. Else, if `STATE.md` exists at the repo root, read it.
3. Else, if CLAUDE.md contains a legacy embedded `## Current State` section, read that and note it in the digest header — offer to migrate to `STATE.md` (no auto-migration).
4. Else (no state captured), tell the user explicitly: "No prior state captured in this repo. Want me to look at git log + open PRs as a fallback?"

### 2. Auto-orient

Run in parallel (only if relevant — skip git/gh steps if not in a git repo):

- `git fetch` (silent)
- `git status`
- `git worktree list`
- `git log --oneline @{u}..HEAD` and `git log --oneline HEAD..@{u}` to detect commits ahead/behind upstream
- `gh pr list --author @me --state all --json number,title,state,reviewDecision,mergedAt,updatedAt --limit 10`
- If a Linear MCP server is configured (any tool matching `mcp__linear*` or `mcp__claude_ai_Linear*` — the official remote server registers as `mcp__linear-server__*`), fetch current title + status for each `SCI-\d+` mentioned in the state files.

### 3. Diff vs last session

Compare auto-orient results against state-file contents. Explicitly call out:

- PRs that were open in state but are now merged or closed.
- Linear tickets that have changed status (e.g., in progress → done).
- Upstream commits the local branch is now behind.
- Worktrees that have been removed.

This "since then" line is the single most useful piece of the digest — it tells Joni what changed while he was away.

### 4. Rank next steps

Start from the state file's `Next steps` list, then adjust:

- Drop items whose corresponding ticket/PR is now closed.
- Promote items that became unblocked (e.g., a PR that's now approved).
- Demote items whose dependency hasn't moved (e.g., waiting on someone else's review).

Re-rank by what is *now* actionable, not what was actionable at last wrapup.

### 5. Present digest

Output format:

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

Empty sections are dropped. If a state file is more than 14 days old, prepend a "(state is N days old — picture may have drifted)" note to the header.

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

## Where it lives

- Source path: `claude-plugins/scilla-claude-toolkit/skills/pickup/SKILL.md`
- Plugin already registered in `marketplace.json`; no marketplace change needed.
- Will be a third skill alongside `wrapup` and `whats-new`.
- README update needed: add a third block under "Skills Included" matching the existing style.
- Root `CLAUDE.md` update needed: bump skill count from 2 to 3 in the `scilla-claude-toolkit/` bullet.

## Out of scope

- Auto-pulling upstream commits. The skill reports what's behind; the user decides whether to `git pull`.
- Auto-checking out a different branch or worktree. Only reports.
- Generating a `STATE.md` if none exists. That's `wrapup`'s job.
- Cross-project digests ("what's open across all my repos"). One repo at a time.
