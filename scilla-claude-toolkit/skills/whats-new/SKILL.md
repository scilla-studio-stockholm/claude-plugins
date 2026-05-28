---
name: whats-new
description: Pull recent Claude/Anthropic updates and explain what they mean for your specific project
---

# What's New — Personalized Claude Update Brief

You are generating a personalized update brief. Your job is to fetch recent Claude/Anthropic updates, compare them against the user's project context, and explain what matters — and what doesn't — for their specific workflow.

## Phase 1: Setup

1. Run `date +%Y-%m-%dT%H:%M:%S%z` to anchor current time.
2. Check if `~/.claude-whats-new/last-seen.json` exists.
   - If it exists, read it. It contains: `{ "blog": "<date>", "claude_code": "<version>", "sdk_python": "<version>" }`
   - If it does NOT exist, create the directory `~/.claude-whats-new/` and set the default lookback to 14 days ago from today. In the brief header, note "(first run — showing last 14 days)" so the user understands why the window is wide.

## Phase 2: Fetch Sources

Fetch ALL three sources in parallel:

### Source 1: Claude Blog
Use `WebFetch` to fetch `https://claude.com/blog` with the prompt:
> "List every blog post on this page. For each post, return the exact title and publication date in YYYY-MM-DD format. Return as a JSON array: [{\"title\": \"...\", \"date\": \"...\", \"url_slug\": \"...\"}]. Only include posts, not navigation or footer content."

### Source 2: Claude Code GitHub Releases
Run via Bash. IMPORTANT: Only fetch the first line of each release body to keep token usage low.
```bash
gh api repos/anthropics/claude-code/releases --jq '[.[0:15] | .[] | {tag: .tag_name, date: (.published_at | split("T")[0]), title: .name, summary: (.body | split("\n")[0:3] | join(" ") | .[:300])}]'
```

### Source 3: Anthropic Python SDK Releases
Run via Bash. Same truncation rule — first line of body only.
```bash
gh api repos/anthropics/anthropic-sdk-python/releases --jq '[.[0:10] | .[] | {tag: .tag_name, date: (.published_at | split("T")[0]), title: .name, summary: (.body | split("\n")[0:3] | join(" ") | .[:300])}]'
```

## Phase 3: Filter to New Items

Compare fetched results against last-seen state:
- **Blog:** include posts with date > last-seen blog date
- **Claude Code:** include releases with tag > last-seen claude_code version (use semantic version comparison)
- **SDK Python:** include releases with tag > last-seen sdk_python version

If there are NO new items across all sources:
- Output: "You're up to date. No new Claude updates since your last check."
- Stop here.

## Phase 4: Read Project Context

Read the user's project context to personalize the analysis. Do this in parallel:

1. **CLAUDE.md** — Read `CLAUDE.md` in the current working directory (if it exists). This is the primary context for personalization. If it doesn't exist, note that personalization will be generic.
2. **Skills** — Run `ls .claude/skills/ 2>/dev/null` to list installed skills.
3. **MCP Servers** — Read `.claude/settings.local.json` or `.claude/settings.json` (whichever exists) to identify configured MCP servers.
4. **Plugin list** — Run `ls .claude-plugin/ 2>/dev/null` or check for plugin configuration.

Synthesize this into a mental model of what the user's project does and what tools/integrations they rely on.

## Phase 5: Generate Brief

Output a markdown brief with this structure:

```
## Claude Update Brief — {today's date}

{1-2 sentence summary: X new updates since last check, Y relevant to this project}

### Highlights

For each new item that IS relevant to this project:

**{Item title}** ({source} — {date})
{One-line summary of the update}
> **Why this matters for you:** {Specific explanation referencing the user's CLAUDE.md, skills, or MCP servers. Be concrete — name the skill, the workflow, the tool that's affected.}
> **Action:** {What the user should do, if anything. "No action needed" is valid.}

### Also New

For items that are NOT directly relevant to this project, list them briefly:

- **{Title}** ({date}) — {One-line summary}. *Not directly relevant: {brief reason}*

### Sources
- Claude Blog: https://claude.com/blog
- Claude Code Releases: https://github.com/anthropics/claude-code/releases
- Anthropic Python SDK: https://github.com/anthropics/anthropic-sdk-python/releases
```

## Phase 6: Update State

After outputting the brief, update the last-seen state:

Write to `~/.claude-whats-new/last-seen.json`:
```json
{
  "blog": "{date of newest blog post seen}",
  "claude_code": "{tag of newest claude-code release seen}",
  "sdk_python": "{tag of newest sdk-python release seen}",
  "last_checked": "{current ISO timestamp}"
}
```

## Rules

- **Be specific in relevance analysis.** "This might be useful" is not helpful. Either name the specific skill/workflow/tool it affects, or mark it as not relevant.
- **Don't oversell.** If an update is minor (bug fix, niche feature), say so. The user trusts this brief because it's honest about what doesn't matter.
- **Group Claude Code releases.** If there are 5+ releases since last check, group them by theme (e.g., "MCP improvements", "Bedrock support", "UX polish") rather than listing each individually.
- **Keep it scannable.** The user should be able to read this in 2 minutes. Lead with what matters.
- **If no CLAUDE.md exists**, still provide useful analysis but note that the brief would be more targeted with a CLAUDE.md in the project.
- **Best practices and prompting posts are relevant to everyone.** Blog posts about how to use Claude better (prompting guides, workflow tips, skill-writing advice) should be treated as relevant to any project that has a CLAUDE.md or skills — they directly inform how the user writes their agent configuration. Don't dismiss these as "not project-specific."
