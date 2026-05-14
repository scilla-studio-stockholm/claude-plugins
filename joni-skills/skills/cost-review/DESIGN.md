# cost-review — design spec

**Date:** 2026-05-14
**Plugin:** joniskills
**Status:** approved for implementation

## Purpose

Repo-agnostic Claude Code skill that surfaces what a user has spent (in tokens and at API list prices) and teaches them how to spend less. Reads local JSONL transcripts that Claude Code writes for every session, regardless of subscription plan. Works on API, Pro, and Max.

## User goals

1. **Visibility:** "What did I spend in this repo? On this feature? In the last week?"
2. **Learning:** "Which sessions were expensive and why? What patterns drive my cost up?"
3. **Reduction:** Concrete, actionable tips tied to detected patterns ("use Haiku for this kind of work", "stop fragmenting sessions").

## Non-goals (v1)

- Cross-repo or global cost dashboards (single repo only).
- Date-range or path-glob narrowing (topic filter covers the main case; YAGNI on the rest).
- Live pricing fetch (hardcoded table, easy to update).
- Writing reports to disk (inline only; user can ask to save individual runs).
- Tracking actual Max/Pro billing — this is API-equivalent cost, period.
- Real-time / streaming (one-shot report per invocation).

## Scope and naming

- **Skill name:** `cost-review`
- **Invocation:** auto-trigger phrases include "what did this cost", "how much have I spent", "analyze my Claude costs", or explicit `/cost-review`. Frontmatter `user_invocable: true`.
- **Default scope:** current working directory → corresponding `~/.claude/projects/<encoded>/` folder, all-time.
- **Optional narrowing:** topic filter only (`--topic <text>`), greps transcripts for the term, includes sessions with ≥3 hits.

## Architecture

```
joni-skills/skills/cost-review/
├── SKILL.md
├── DESIGN.md                          # this file
├── scripts/
│   └── analyze_costs.py
└── references/
    └── cost-reduction-patterns.md
```

**SKILL.md** — instructs Claude when to invoke the script, what args to pass, how to present the output verbatim, and how to handle follow-up questions ("explain signal X" → read `references/cost-reduction-patterns.md`).

**scripts/analyze_costs.py** — self-contained Python 3.8+ script. No third-party dependencies. Reads JSONLs directly, computes totals and signals, prints report or emits JSON. Re-runnable any time.

**references/cost-reduction-patterns.md** — long-form coaching content for each signal, loaded by Claude on demand. Not printed by the script.

## Script contract

### Inputs

```
python3 analyze_costs.py [--cwd PATH] [--topic TEXT] [--json]
```

- `--cwd PATH` — directory to analyze. Default: `$PWD`. Resolved to transcript folder via the encoding `~/.claude/projects/-<path-with-slashes-replaced-by-hyphens>/`.
- `--topic TEXT` — only include sessions whose transcripts contain ≥3 hits of `TEXT` (case-insensitive substring match across all message records). Optional.
- `--json` — emit structured JSON instead of human report. Default: human report.

### Behavior

1. Resolve `--cwd` to transcript folder. If it doesn't exist, print "No Claude Code transcripts for this repo" and exit 0.
2. Walk `*.jsonl` (top-level sessions) + `*/subagents/*.jsonl` (subagent transcripts). Subagent files share their parent's `sessionId` — token usage rolls up correctly.
3. For each session: parse JSONL line-by-line, collect every `message` record that has `usage`, sum `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, by `model`.
4. If `--topic` set: count substring hits across all lines of all files for each session; drop sessions with <3 hits. Report what fraction of sessions matched.
5. Compute cost using hardcoded pricing table (see below).
6. Run signal detectors (see below).
7. Format report (human or JSON).

### Pricing table (USD per million tokens)

| Family | Input | Output | Cache write | Cache read |
|---|---:|---:|---:|---:|
| Opus 4.x | 15.00 | 75.00 | 18.75 | 1.50 |
| Sonnet 4.x | 3.00 | 15.00 | 3.75 | 0.30 |
| Haiku 4.x | 1.00 | 5.00 | 1.25 | 0.10 |

Family detection: lowercase `model` field, substring match on `opus`/`sonnet`/`haiku`. Older `claude-3-*` or unrecognized: fall back to Sonnet pricing, mark "(estimated)" in the per-model line.

### Cost-reduction signals

All thresholds are first-pass; tunable in code. Signals that don't trigger are omitted from output.

| Signal | Threshold | Tip |
|---|---|---|
| Opus on lightweight work | ≥3 sessions where model contains `opus` AND avg output per turn <2K tokens | Use `/model haiku` for routine edits and lookups |
| High cache-write ratio | `cache_write_tokens / (cache_write_tokens + cache_read_tokens) > 50%` — writes exceed reads, cache isn't paying back | Long sessions are cheaper than many short ones — reuse rather than restart |
| Low cache-read ratio | overall `cache_read / (cache_read + direct_input) < 50%` | Avoid `/clear` early in a session; it discards your warm cache |
| Output-heavy session | individual session with output >50K tokens | Use Edit instead of Write for partial changes; reference files instead of re-outputting them |
| Session fragmentation | ≥5 sessions started in one calendar day, ≥4 of them under 30 turns | Consolidate into fewer longer sessions to retain warm cache |
| Direct-input cost | direct input (uncached) > 5% of total cost | First user message sets the cache breakpoint — keep system prompt + initial context stable |

Each signal's report line includes the relevant numeric anchor (count, percentage, token volume, dollar share).

### Output — human report

```
=== Claude Code cost report ===
Repo:    <cwd>
Scope:   all-time            [or: topic="<text>" (N of M sessions)]
Window:  <first> → <last>  (<days> days, <sessions>, <turns> turns)

=== Total ===
$X,XXX.XX   X.XM tokens
  Opus 4.7    $X,XXX.XX  X.XM tokens   (cache_read XM, output XM, cache_write XM, input XK)
  Sonnet 4.6  $XX.XX   XM tokens
  Haiku 4.5   $XX.XX   XM tokens

=== Top 5 sessions by cost ===
$XXX.XX  <ts>  <turns> turns  <tokens> tokens  <model>  <sid-short>
...

=== Daily timeline (last 30 days) ===
<date>  $XXX.XX  <tokens>   <bar>
...

=== Cost-reduction signals ===
⚠ <signal>: <anchor>  (~$XX of bill)
   → Tip: <one-line remediation>
✓ <green signal, when applicable>
...

To dig deeper: ask "explain signal X", "show sessions matching <topic>", or rerun with --topic <text>.
```

### Output — JSON mode

Top-level object:

```json
{
  "repo": "...",
  "scope": {"mode": "all-time" | "topic", "topic": "..." | null},
  "window": {"first": "...", "last": "...", "days": N, "sessions": N, "turns": N},
  "total": {"cost": 0.0, "tokens": 0},
  "per_model": [
    {"model": "...", "family": "opus"|"sonnet"|"haiku", "turns": N,
     "input_tokens": N, "output_tokens": N, "cache_read": N, "cache_write": N,
     "cost": 0.0, "estimated": false}
  ],
  "top_sessions": [
    {"sid": "...", "timestamp": "...", "turns": N, "tokens": N, "model": "...", "cost": 0.0}
  ],
  "daily": [{"date": "YYYY-MM-DD", "cost": 0.0, "tokens": N}],
  "signals": [
    {"id": "opus-on-lightweight", "severity": "warn"|"ok",
     "anchor": "3 sessions with avg 1.4K output tokens",
     "cost_share": 45.00, "tip": "..."}
  ]
}
```

### Error handling

| Condition | Behavior |
|---|---|
| `~/.claude/projects/<encoded-cwd>/` doesn't exist | Print "No Claude Code transcripts for this repo (looked under <path>). Have you used Claude Code in this directory?" Exit 0. |
| Folder exists but 0 `.jsonl` files | Print "Found the project folder but no `.jsonl` transcripts." Exit 0. |
| Topic filter matches 0 sessions | Print "No sessions matched topic '<text>' (≥3 hits required). <N> total sessions in this repo." Exit 0. |
| Unknown model name in a record | Use Sonnet pricing, mark "(estimated)" on its per-model line and in JSON. |
| Malformed JSONL line | Skip silently. |
| Record with no `usage` field | Skip silently (not all messages have usage — only assistant messages do). |
| `--cwd` was passed and the path doesn't exist on disk | Print "Path <path> does not exist." Exit 1. (No-arg default is `$PWD`, which always exists.) |

### Path encoding

Claude Code stores transcripts at `~/.claude/projects/<encoded>/` where `<encoded>` is the absolute path with every `/` replaced by `-`, and a leading `-`. Example:
- `/Users/jonilindgren/claude-projects/Metria` → `-Users-jonilindgren-claude-projects-Metria`

The script implements this encoding deterministically and tests it against a known fixture.

## SKILL.md contract

The SKILL.md frontmatter:

```yaml
---
name: cost-review
description: Analyze Claude Code token cost for the current repo. Surfaces total spend (API list prices) by model, top expensive sessions, daily timeline, and auto-detected cost-reduction signals with one-line remediations. Use when the user asks "what did this cost", "how much have I spent on X", "analyze my Claude costs", or invokes /cost-review. Supports --topic <text> to narrow to a feature.
user_invocable: true
---
```

Body sections:

1. **When to run** — trigger phrases and examples
2. **How to invoke** — `python3 scripts/analyze_costs.py` with optional flags; resolve via `${CLAUDE_PLUGIN_ROOT}` or relative `scripts/` path
3. **How to present output** — print the script's stdout verbatim; do not paraphrase numbers
4. **Follow-up handling** — if user asks "explain signal X", read `references/cost-reduction-patterns.md` and explain that signal in depth. If user asks for a different cut, re-run with different `--topic` or re-shape from `--json` output
5. **Caveats line** — always remind: API list prices, not Max/Pro actual outlay

## Reference doc contract

`references/cost-reduction-patterns.md`: one section per signal ID, each with:

- The signal's mechanism (why it costs more)
- How to spot it in your workflow before the bill confirms it
- Concrete remediation steps (commands, settings, workflow changes)
- Links to relevant Claude Code docs/skills (e.g., `/model` command, caching docs, `superpowers:executing-plans` for long sessions)

## Sanity test

Running against a real repo with a known topic must produce a plausible cost (positive, dominated by the model the user actually used, with a window matching when work happened). The original target was reproducing the manual OST analysis of $1,273.77 (2026-05-13), but that figure used a domain-curated marker list (specific paths + 13 skill names) that a generic substring filter cannot replicate. With `--topic OST` against Metria, the skill reports ≈$4,000–4,700 because the bare token "OST" appears in every session (skill listing, system reminders), not because the filter is broken. For tight Metria-OST scoping use a more specific term like `--topic skills-design` or `--topic "OST-"`; for arbitrary repos, pick a substring distinctive to the work being measured.

## Caveats and known limits

- **API list prices, not actual bill.** A Max user pays subscription; this is what the same usage would have cost via the API.
- **Topic filter is a substring match, not domain curation.** ≥3 case-insensitive hits keeps the signal-to-noise tight, but a short token (e.g. "OST") can appear in metadata (installed skill names in system reminders) across sessions that didn't actually do that work. Pick distinctive substrings, or use a path fragment like `skills-design/` or a hyphenated prefix like `OST-`. For domain-precise filtering, a curated marker list outside the skill is still the right tool.
- **Subagent attribution.** Subagent JSONLs carry the parent's `sessionId`, so their costs roll up into the parent — verified manually against Metria data. If a future Claude Code version changes this, the script needs a re-verification.
- **Pricing table goes stale.** Hardcoded April 2026 list prices. Bump when Anthropic ships new pricing.
- **Older model families (claude-3-\*)** estimated at Sonnet rates. Fine for the recent past; if you analyze old transcripts, the figure is approximate.

## Open questions

None at design time. All scope decisions captured above.
