---
name: cost-review
description: Analyze Claude Code token cost for the current repo. Surfaces total spend (API list prices) by model, top expensive sessions, daily timeline, and auto-detected cost-reduction signals with one-line remediations. Use when the user asks "what did this cost", "how much have I spent on X", "analyze my Claude costs", or invokes /cost-review. Supports --topic <text> to narrow to a feature.
user_invocable: true
---

# cost-review

Repo-agnostic Claude Code cost analyzer + cost-reduction coach. Reads local JSONL transcripts that Claude Code writes regardless of subscription plan (works on API, Pro, and Max).

## When to run

Trigger phrases include:
- "What did this cost?"
- "How much have I spent on <X>?"
- "Analyze my Claude costs"
- "Cost report for this repo"
- Explicit `/cost-review`

## How to invoke

The script lives at `${CLAUDE_PLUGIN_ROOT}/skills/cost-review/scripts/analyze_costs.py`. Invoke it via Bash:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/cost-review/scripts/analyze_costs.py"
```

Default scope: current working directory, all-time. Optional flags:
- `--topic <text>` — narrow to sessions with ≥3 case-insensitive hits of TEXT (use for feature-specific cost like `--topic OST` or `--topic auth-refactor`). Pick a distinctive substring — short common tokens may match metadata in unrelated sessions.
- `--json` — emit structured JSON instead of the human report (useful when the user asks follow-up questions you want to reshape data for)

## How to present output

**Print the script's stdout verbatim.** Do not paraphrase the numbers, do not round, do not skip sections. The script is the source of truth.

After printing, add a one-line caveat:
> _Numbers are at API list prices (April 2026), not your actual Pro/Max bill._

## Follow-up handling

When the user asks "explain signal X" or "tell me more about <signal-name>", read `${CLAUDE_PLUGIN_ROOT}/skills/cost-review/references/cost-reduction-patterns.md` and surface the relevant section.

When the user asks for a different cut ("by week", "just May", "without the OST stuff"):
- If date/path narrowing is needed, re-run with `--topic` (only narrowing flag in v1).
- If the user wants reshape (e.g. weekly buckets from daily, or per-skill from per-session), re-run with `--json` and reshape the structured output rather than re-parsing transcripts.

When the user asks "save this report" or similar, write it to a markdown file at a sensible location in the current repo (typically `docs/cost-reports/YYYY-MM-DD-<scope>.md`) — but only when explicitly asked. Default behavior is inline only.

## Limits and caveats

- API list prices, not actual Pro/Max bill.
- Topic filter uses ≥3 case-insensitive substring hits — conservative by design. Bare common tokens (e.g. a skill name that appears in every session's available-skills list) can match unintended sessions; prefer distinctive substrings like `skills-design/` or hyphenated prefixes (`OST-`).
- Pricing table is hardcoded (April 2026). If the table looks stale, update `PRICING` in `scripts/analyze_costs.py`.
- Doesn't cover Cowork sessions (server-side, not in local JSONL).
