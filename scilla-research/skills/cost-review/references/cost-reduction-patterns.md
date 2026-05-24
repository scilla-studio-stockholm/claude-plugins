---
title: Cost-reduction patterns
purpose: Long-form coaching for each signal surfaced by cost-review. Loaded by the SKILL.md when the user asks "explain signal X" or "tell me more about <signal>".
---

# Cost-reduction patterns

Six signal detectors run on every cost-review invocation. Each gets a one-line tip in the report; this doc holds the deeper explanation.

## opus-on-lightweight

**What it means:** You ran Claude Opus on sessions where the average output per turn was under 2K tokens. That's typical of routine edits, lookups, file renames, small refactors — work where the model size doesn't change the answer quality but does change the bill.

**Why it costs more:** Opus output is $75/M tokens vs Haiku at $5/M — 15× the rate. A 200-turn lightweight session at 1K avg output costs ~$15 on Opus and ~$1 on Haiku.

**How to spot it before the report:** During a session, if you're mostly doing tool calls and short confirmations rather than reasoning, you're paying Opus rates for routine work.

**Remediation:**
- Use `/model haiku` at the start of routine sessions (file cleanup, doc edits, small refactors).
- Use `/model opus` for design work, debugging, multi-file reasoning.
- Switching mid-session is fine — only future turns use the new model.

## high-cache-write

**What it means:** More than 50% of your cached tokens are being written rather than read. Indicates that the cache isn't paying back — context is being primed but not reused.

**Why it costs more:** Cache write is $18.75/M (Opus) — 12.5× the cache read rate of $1.50/M. You pay the write cost once per cache breakpoint; if you're hitting many breakpoints without subsequent reads, the writes never amortize.

**How to spot it:** Lots of short sessions (`/clear` or new windows) where work ends before the cache gets reused, system-prompt-level churn from frequent settings tweaks, or large context that keeps changing between turns.

**Remediation:**
- Keep one Claude Code session open longer rather than starting fresh ones.
- For repeated tasks across the day, append work to one session rather than splitting.
- Avoid `/clear` unless you really want a clean slate — it discards your warm cache.

## low-cache-read

**What it means:** Less than 50% of your input came from warm cache. The other 50%+ is direct input that gets billed at the higher rate.

**Why it costs more:** Direct input is $15/M (Opus) — 10× the cache read rate.

**How to spot it:** Many short sessions, frequent `/clear`, or starting Claude Code repeatedly throughout the day for small tasks.

**Remediation:** Same as high-cache-write — consolidate sessions. The first ~10 turns of any session can't fully benefit from caching; longer sessions amortize that.

## output-heavy

**What it means:** A single session produced more than 50K output tokens (~25K words). Often a sign of one of:
1. Subagent dispatches — each subagent generates its own output tokens, which accumulate in the parent session
2. The model regenerated a long file via Write instead of using Edit
3. Long markdown reports / specs / plans being authored
4. Verbose narration during refactoring

**Why it costs more:** Output is the most expensive token type — $75/M on Opus.

**How to spot it:** Watch for the model rewriting whole files when only a section changed. Or for explanations that re-print code blocks instead of referencing them.

**Remediation:**
- Check whether subagent dispatches drove the output. Each Agent call generates its own output tokens — consider whether the same work could be done inline or with fewer agents.
- Prefer Edit over Write for partial changes.
- For long reports, ask the model to write to a file rather than print to chat.
- If you're getting long narrations, ask: "show me only the diff" or "skip the explanation."

## session-fragmentation

**What it means:** Five or more sessions started in one calendar day, with at least four under 30 turns. Each new session pays cache-write cost for its initial context.

**Why it costs more:** Cache reuse is per-session. Five 20-turn sessions cost more than one 100-turn session — same number of turns, but 5× the cache writes.

**How to spot it:** Looking at your session list and seeing many small entries from the same day.

**Remediation:**
- When stopping for lunch / a meeting, leave Claude Code running and resume the same session.
- Use `/resume` (if installed) or open the same project session ID rather than starting a new one.
- If you genuinely need a new context, fine — but don't fragment by accident.

## direct-input-cost

**What it means:** Direct (uncached) input is more than 5% of your total cost. Usually means the cache breakpoint is being missed — maybe because the system prompt or initial context keeps changing.

**Why it costs more:** Direct input at $15/M (Opus) is 10× cache read.

**How to spot it:** If you change CLAUDE.md, settings, or initial context often, every change invalidates the cache prefix.

**Remediation:**
- Stabilize CLAUDE.md and settings during a work session — make changes between sessions, not within them.
- The first user message of a session sets the cache breakpoint. Keep it consistent across similar sessions.
- If you're doing many small one-shot prompts, consider batching them into one longer session.
