---
name: wrapup
description: Use when ending a work session and need to capture context for future sessions. Use when the user says /wrapup or mentions wrapping up, ending session, or saving progress.
---

# Session Wrapup

Capture session context into project files so the next session can pick up seamlessly.

**Core principle:** CLAUDE.md is orientation (what the project is, conventions, pointers). State lives in a dedicated state file or project-specific source-of-truth files — never embedded in CLAUDE.md.

## Process

### 1. Commit work in progress (if any)

Run `git status` and, if relevant, `git worktree list` to confirm which branch/worktree you're in. If there are unversioned changes from the work itself (separate from the wrapup updates you're about to write), ask if the user wants to commit and push first.

Joni follows a Linear → GitHub PR workflow (see global CLAUDE.md). If the branch is `joni/sci-XX-…`, commits and PRs should include the ticket ID.

### 2. Review what happened

Scan the current conversation and identify:
- What was worked on (features, bugs, refactors) and which Linear tickets it relates to
- PRs opened, merged, or still awaiting review/merge
- Active worktrees and what each is for
- Key decisions made and why
- What's done vs still in progress
- Blockers or open questions
- Any architectural changes

**Extract ticket IDs the conversation may not have named.** Don't rely on the conversation alone — the session may have worked on a ticket without ever saying the ID aloud. Run these and collect every `SCI-\d+` match:

```
git branch --show-current
git worktree list
git log --since='2 days ago' --format='%s%n%b'
gh pr list --author @me --state all --json number,title,headRefName,state,updatedAt --limit 20
```

Dedupe the IDs. For each, decide whether it's *touched this session* (commit/PR/branch matches the work you did) or *just open in the background* (carry forward from previous state).

**Enrich with Linear MCP if available.** If a Linear MCP server is configured (any tool matching `mcp__linear*` or `mcp__claude_ai_Linear*` — the official remote server registers as `mcp__linear-server__*`), fetch title + status + assignee for each extracted ID so the *Open Linear tickets* section of `STATE.md` has real state, not just IDs. If no Linear MCP is configured, write the IDs with whatever context you have from PR titles and commit messages.

### 3. Update the project's state file

**Find where state lives in this project:**

1. Read the project's `CLAUDE.md`. If it points to specific source-of-truth files for state (e.g. *"Wave 1 scope is in `transformationsteamet/vag-1-idoarrt.md`"*, or *"State lives in `STATE.md`"*), update those files.
2. Otherwise default to `STATE.md` at the repo root. Create it if it doesn't exist, and add a one-line pointer to it from CLAUDE.md (e.g. *"Session state lives in `STATE.md`."*).

**`STATE.md` template** — adjust headings to match what's actually useful for the project. Drop empty sections.

```
# State

**Last session:** YYYY-MM-DD
**Branch / worktree:** <branch name or worktree path>
**Active worktrees:** (only if more than one — path + purpose)

## In progress
- <what's being worked on, with ticket ID>

## Open PRs
- #N — <title> (SCI-XX) — awaiting review / changes requested / ready to merge

## Open Linear tickets
- [SCI-XX](https://linear.app/scilla/issue/SCI-XX) — one-line summary + state

## Recent decisions
- <decision + brief why>

## Next steps
1. <priority-ordered list>

## Gotchas
- <anything the next session needs to watch out for>
```

Keep this a living snapshot, not a changelog. Strip stale entries. Information already in git log or PR descriptions doesn't belong here — only intent and context that commits don't capture.

### 4. Update CLAUDE.md (only if conventions changed)

CLAUDE.md is orientation. Only touch it if the session revealed:
- New project conventions worth preserving
- Changes to folder structure or where things live
- Changes to how state is tracked (e.g. a new source-of-truth file added)

If the project has no session-startup section yet, add one:

```
## Session Startup
- Run `git status` (and `git worktree list` if worktrees are in use)
- Read `STATE.md` (or the project's source-of-truth state files)
- Ask if we should pick up where we left off or start something new
```

If CLAUDE.md still contains an embedded `## Current State` section from an older convention, flag it to the user and offer to migrate the content out to `STATE.md`. Don't auto-migrate without confirmation.

### 5. Update README.md (only if user-facing changes)

Only touch README if the session changed something user-facing:
- Setup instructions changed
- New dependencies added
- Architecture shifted
- New features that affect usage

Don't touch README for internal refactors or work-in-progress.

### 6. Update project-conventional living docs

If the project maintains specific living artifacts, update them when the session changed what they describe. Common ones:
- `CHANGELOG.md` — dated entry per session for project-level events
- `TODO.md` — cross-cutting TODO list
- Mermaid journey/flow diagram — if the user flow actually shifted
- `.env.example` — if new env vars were introduced
- Migration files or setup scripts

Don't create these files speculatively. Only update what already exists.

### 7. Offer to commit the wrapup

After all updates, propose a commit. Two observed styles:
- `docs: session wrapup — <one-line topic>`
- `CLAUDE.md: wrapup session YYYY-MM-DD` (when only CLAUDE.md changed)

Ask before committing. Don't push automatically.

### 8. Summarize to user

- Which files were updated and what changed
- What the next session should start with

## Rules

- Be concise. Future Claude has limited context — every word should earn its place.
- Don't duplicate info that's already in git history or PR descriptions. Focus on intent and context that commits don't capture.
- Don't create files that don't exist unless there's clear value. Updating existing files is preferred.
- Strip stale information. If something from a previous wrapup is done or no longer relevant, remove it.
- Use bullet points, not prose. Scannable > readable for pickup context.
- CLAUDE.md is orientation. State lives in `STATE.md` or project-specific source-of-truth files — never embedded in CLAUDE.md.
