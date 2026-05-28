# pickup skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `pickup` as a third skill in the `scilla-claude-toolkit` plugin, mirroring the existing `wrapup` skill.

**Architecture:** Three-file change in the `claude-plugins` repo. A new SKILL.md with the skill body (prose for an LLM), plus a README block and a count update — all on branch `joni/sci-48-add-pickup-skill`, shipped via PR to master.

**Tech Stack:** Markdown SKILL.md format (frontmatter + body), JSON marketplace config (no change needed — plugin already registered).

**Spec reference:** `docs/superpowers/specs/2026-05-28-pickup-skill-design.md`

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `scilla-claude-toolkit/skills/pickup/SKILL.md` | Create | The skill body — triggers, process, output template, edge cases |
| `scilla-claude-toolkit/README.md` | Modify | Add a third skill block under "Skills Included", matching the existing format |
| `CLAUDE.md` (root) | Modify | Bump "2 meta-skills" → "3 meta-skills" in the scilla-claude-toolkit bullet, add the skill name |

No marketplace.json change — the plugin is already registered.
No test files — SKILL.md is prose for an LLM, not code. Verification is manual reading + a fresh-session smoke test after merge.

---

### Task 1: Create the pickup SKILL.md

**Files:**
- Create: `scilla-claude-toolkit/skills/pickup/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p scilla-claude-toolkit/skills/pickup
```

- [ ] **Step 2: Write the SKILL.md with the full body**

Write to `scilla-claude-toolkit/skills/pickup/SKILL.md`:

```markdown
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
```

- [ ] **Step 3: Verify the file by reading it back**

Run: `wc -l scilla-claude-toolkit/skills/pickup/SKILL.md`
Expected: ~95-110 lines.

Manually read through and confirm:
- Frontmatter has `name: pickup` and a `description` that includes both English and Swedish trigger phrases.
- All 6 process steps from the spec are present.
- The output template is included.
- The edge-cases table has 7 rows matching the spec.

- [ ] **Step 4: Commit**

```bash
git add scilla-claude-toolkit/skills/pickup/SKILL.md
git commit -m "$(cat <<'EOF'
feat: add pickup skill to scilla-claude-toolkit (SCI-48)

Mirror image of the wrapup skill. Reads STATE.md (or project-specific
source-of-truth files), runs git fetch + gh pr list + Linear MCP to
detect what changed since last session, presents a digest plus ranked
next steps, and asks for confirmation before acting.

Spec: docs/superpowers/specs/2026-05-28-pickup-skill-design.md
EOF
)"
```

---

### Task 2: Update plugin README and root CLAUDE.md

**Files:**
- Modify: `scilla-claude-toolkit/README.md` (add third block)
- Modify: `CLAUDE.md` (bump count + skill list)

- [ ] **Step 1: Add the third skill block to the plugin README**

Find the end of the "Skills Included" section (after the "What's New (`whats-new`)" block) and append:

```markdown
### 3. Pickup (`pickup`)
Reads the state file written by `wrapup` and orients you to where you left off in this repo.

**Triggers:**
- `/pickup`
- "where was I", "pick up", "what was I working on", "what are we doing today", "what was the last thing I worked on"
- Swedish: "vad ska vi börja med i den här sessionen", "vad jobbade vi på senast", "vad är nästa steg"

**What it does:** Detects where state lives (`STATE.md` or project-specific source-of-truth files), runs `git fetch` + `gh pr list` + Linear MCP (if installed) to detect what changed since last session, and presents a digest with ranked next steps. Read-only — asks for confirmation before acting.
```

- [ ] **Step 2: Update the plugin description blurb at the top of the README**

Replace this line at the top of `scilla-claude-toolkit/README.md`:

```
Scilla team's curated meta-skills for managing the way of working with Claude — not domain skills, but workflow helpers that keep sessions tidy and projects pickup-friendly.
```

No change needed — the "pickup-friendly" phrasing already covers the new skill.

- [ ] **Step 3: Update root CLAUDE.md skill count**

In `/Users/jonilindgren/claude-projects/claude-plugins/CLAUDE.md`, find:

```
- `scilla-claude-toolkit/` — 2 meta-skills for managing the way of working with Claude (`wrapup`, `whats-new`)
```

Replace with:

```
- `scilla-claude-toolkit/` — 3 meta-skills for managing the way of working with Claude (`wrapup`, `whats-new`, `pickup`)
```

- [ ] **Step 4: Verify the diff**

Run: `git diff --stat`
Expected: 2 files changed (README + CLAUDE.md), small line counts.

Run: `git diff scilla-claude-toolkit/README.md`
Expected: only an addition of the new skill block at the bottom of the "Skills Included" section.

Run: `git diff CLAUDE.md`
Expected: single-line replacement on the scilla-claude-toolkit bullet.

- [ ] **Step 5: Commit**

```bash
git add scilla-claude-toolkit/README.md CLAUDE.md
git commit -m "$(cat <<'EOF'
docs: register pickup skill in README and root CLAUDE.md (SCI-48)

Adds the third skill block to the plugin README and bumps the
scilla-claude-toolkit bullet in root CLAUDE.md from "2 meta-skills" to
"3 meta-skills" with the new skill name.
EOF
)"
```

---

### Task 3: Push branch and open PR

**Files:** None — git/gh operations only.

- [ ] **Step 1: Verify branch and confirm both commits land**

Run: `git log --oneline master..HEAD`
Expected: 3 commits in this order (oldest first):
1. `spec: pickup skill design`
2. `feat: add pickup skill to scilla-claude-toolkit (SCI-48)`
3. `docs: register pickup skill in README and root CLAUDE.md (SCI-48)`

Run: `git branch --show-current`
Expected: `joni/sci-48-add-pickup-skill`

- [ ] **Step 2: Push branch with upstream tracking**

```bash
git push -u origin joni/sci-48-add-pickup-skill
```

Expected: new branch created on origin, tracking set up.

- [ ] **Step 3: Open PR**

```bash
gh pr create --title "feat: add pickup skill to scilla-claude-toolkit (SCI-48)" --body "$(cat <<'EOF'
## Summary
- Adds **pickup** as the third skill in `scilla-claude-toolkit`
- Mirror image of `wrapup`: reads STATE.md / project-specific source-of-truth files, runs `git fetch` + `gh pr list` + Linear MCP (if installed) to detect what changed since last session, presents a digest with ranked next steps, asks for confirmation before acting
- Triggers in both English and Swedish

## Linear
SCI-48

## Spec
`docs/superpowers/specs/2026-05-28-pickup-skill-design.md`

## Test plan
- [ ] After merge: `/plugin update scilla-claude-toolkit@scilla-studio` in a fresh session, confirm `scilla-claude-toolkit:pickup` shows up in the available-skills list
- [ ] Run `/pickup` in a repo with a recent `STATE.md` — confirm digest format, "since then" detection, ranked next steps, and confirmation prompt
- [ ] Run `/pickup` in a repo with **no** state file — confirm graceful fallback message
- [ ] Try a Swedish trigger ("vad jobbade vi på senast") — confirm the skill activates

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Expected: PR URL printed.

- [ ] **Step 4: Record PR number**

Capture the PR number from the output of Step 3 (e.g., `#30`). Will be needed for the review step.

---

### Task 4: Review and merge

**Files:** None — review only.

- [ ] **Step 1: Review the PR**

Invoke the `/review` skill with the PR number from Task 3 Step 4. Confirm:
- Diff matches the spec.
- No accidental Joni-specific hardcoding (mirror of the SCI-47 lesson).
- README block is consistent with the other two.
- Commit messages all reference SCI-48.

- [ ] **Step 2: Address review findings**

If review finds issues, fix them on the same branch with a follow-up commit (also referencing SCI-48). Push.

- [ ] **Step 3: Merge**

```bash
gh pr merge <PR-number> --merge --delete-branch
```

Expected: merge commit on master, branch deleted locally and on origin.

- [ ] **Step 4: Verify SCI-48 closes**

Linear's GitHub integration should auto-transition SCI-48 to Done after merge. Verify by checking Linear (or by Linear MCP if the user wants).

---

## Self-Review

**Spec coverage:**
- Trigger phrases (Eng + Swe) → Task 1, frontmatter description ✓
- Process steps 1-6 → Task 1, body ✓
- Output template → Task 1, body ✓
- Edge cases table → Task 1, body ✓
- README block → Task 2 ✓
- Root CLAUDE.md count bump → Task 2 ✓
- "Where it lives" (skill path + plugin registration) → Task 1 + Task 2 ✓

**Placeholder scan:** None.

**Type consistency:** N/A (no code types). Skill name `pickup` used consistently throughout. Trigger phrases listed identically in both the SKILL.md frontmatter and the README block.

---

## Execution notes for the runner

- All commits must include `(SCI-48)` in the message subject so Linear's GitHub integration links them.
- The branch `joni/sci-48-add-pickup-skill` already exists locally with the spec commit. Don't recreate it.
- Don't push until Task 3 — wait for both Task 1 and Task 2 commits to land locally first.
- The skill body is intentionally a near-mirror of `wrapup`. Don't over-engineer differences — symmetry is the point.
