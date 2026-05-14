#!/usr/bin/env python3
"""cost-review: Claude Code cost analyzer + cost-reduction coach.

Reads local JSONL transcripts under ~/.claude/projects/<encoded-cwd>/ and
prints a token+dollar usage report with auto-detected cost-reduction signals.

Self-contained: stdlib only, Python 3.8+.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Optional


def encode_cwd_to_transcript_dir(cwd: Path) -> Path:
    """Return ~/.claude/projects/<encoded>/ for the given cwd.

    Encoding: replace every '/' in the absolute path with '-'.
    Example: /Users/x/y -> -Users-x-y
    """
    abs_path = str(cwd.resolve()) if cwd.exists() else str(cwd)
    encoded = abs_path.replace("/", "-")
    return Path.home() / ".claude/projects" / encoded


def parse_message(line: str) -> Optional[dict]:
    """Parse one JSONL line. Return {sid, model, usage, ts} or None.

    Returns None for: malformed JSON, non-assistant types, messages without usage.
    """
    try:
        obj = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    if obj.get("type") != "assistant":
        return None
    msg = obj.get("message") or {}
    usage = msg.get("usage")
    if not usage:
        return None
    sid = obj.get("sessionId")
    if not sid:
        return None
    return {
        "sid": sid,
        "model": msg.get("model") or "",
        "ts": obj.get("timestamp") or "",
        "usage": {
            "input_tokens": usage.get("input_tokens", 0) or 0,
            "output_tokens": usage.get("output_tokens", 0) or 0,
            "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0) or 0,
        },
    }


def walk_transcripts(transcript_dir: Path) -> dict:
    """Walk *.jsonl + */subagents/*.jsonl under transcript_dir.

    Returns: dict mapping sessionId -> list of parsed message dicts.
    """
    sessions: dict = defaultdict(list)
    if not transcript_dir.exists() or not transcript_dir.is_dir():
        return {}
    paths = list(transcript_dir.glob("*.jsonl")) + list(transcript_dir.glob("*/subagents/*.jsonl"))
    for p in paths:
        try:
            with open(p, "r", errors="ignore") as f:
                for line in f:
                    msg = parse_message(line)
                    if msg is not None:
                        sessions[msg["sid"]].append(msg)
        except OSError:
            continue
    return dict(sessions)


# USD per million tokens. Anthropic public list prices, April 2026.
PRICING = {
    "opus":   {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "sonnet": {"input":  3.00, "output": 15.00, "cache_write":  3.75, "cache_read": 0.30},
    "haiku":  {"input":  1.00, "output":  5.00, "cache_write":  1.25, "cache_read": 0.10},
}


def family_for_model(model: str) -> tuple:
    """Return (family, estimated). family is 'opus'|'sonnet'|'haiku'.

    estimated=True when model name didn't match any known family and we fell back.
    """
    m = (model or "").lower()
    for family in ("opus", "sonnet", "haiku"):
        if family in m:
            return (family, False)
    return ("sonnet", True)  # conservative fallback for unknown


def compute_cost(usage: dict, family: str) -> float:
    """Dollar cost for one usage dict at the family's rates."""
    p = PRICING[family]
    return (
        usage.get("input_tokens", 0)                 * p["input"]
        + usage.get("output_tokens", 0)              * p["output"]
        + usage.get("cache_creation_input_tokens", 0) * p["cache_write"]
        + usage.get("cache_read_input_tokens", 0)    * p["cache_read"]
    ) / 1_000_000


from datetime import datetime


def aggregate(sessions: dict) -> dict:
    """Build summary structure from sessionId -> [messages]."""
    if not sessions:
        return {
            "window": {"first": "", "last": "", "days": 0, "sessions": 0, "turns": 0},
            "total": {"cost": 0.0, "tokens": 0},
            "per_model": [],
            "per_session": [],
            "daily": [],
        }

    # Per-model accumulator
    by_model: dict = defaultdict(lambda: {
        "model": "", "family": "", "estimated": False, "turns": 0,
        "input_tokens": 0, "output_tokens": 0, "cache_read": 0, "cache_write": 0,
    })
    per_session: list = []
    by_day: dict = defaultdict(lambda: {"cost": 0.0, "tokens": 0})

    all_ts = []
    total_turns = 0
    total_cost = 0.0
    total_tokens = 0

    for sid, msgs in sessions.items():
        s_cost = 0.0
        s_tokens = 0
        s_input = 0; s_output = 0; s_cw = 0; s_cr = 0
        s_first_ts = ""
        s_last_ts = ""
        s_models: dict = defaultdict(int)

        for m in msgs:
            family, estimated = family_for_model(m["model"])
            cost = compute_cost(m["usage"], family)
            tokens = (m["usage"]["input_tokens"] + m["usage"]["output_tokens"]
                      + m["usage"]["cache_creation_input_tokens"]
                      + m["usage"]["cache_read_input_tokens"])

            bm = by_model[m["model"] or "(unknown)"]
            bm["model"] = m["model"] or "(unknown)"
            bm["family"] = family
            bm["estimated"] = bm["estimated"] or estimated
            bm["turns"] += 1
            bm["input_tokens"] += m["usage"]["input_tokens"]
            bm["output_tokens"] += m["usage"]["output_tokens"]
            bm["cache_read"] += m["usage"]["cache_read_input_tokens"]
            bm["cache_write"] += m["usage"]["cache_creation_input_tokens"]

            s_cost += cost
            s_tokens += tokens
            s_input += m["usage"]["input_tokens"]
            s_output += m["usage"]["output_tokens"]
            s_cw += m["usage"]["cache_creation_input_tokens"]
            s_cr += m["usage"]["cache_read_input_tokens"]
            s_models[m["model"]] += 1

            ts = m["ts"]
            if ts:
                all_ts.append(ts)
                if not s_first_ts or ts < s_first_ts:
                    s_first_ts = ts
                if not s_last_ts or ts > s_last_ts:
                    s_last_ts = ts
                day = ts[:10]
                by_day[day]["cost"] += cost
                by_day[day]["tokens"] += tokens

            total_turns += 1
            total_cost += cost
            total_tokens += tokens

        primary_model = max(s_models.items(), key=lambda kv: kv[1])[0] if s_models else ""
        per_session.append({
            "sid": sid,
            "first_ts": s_first_ts,
            "last_ts": s_last_ts,
            "turns": len(msgs),
            "tokens": s_tokens,
            "cost": s_cost,
            "model": primary_model,
            "input_tokens": s_input, "output_tokens": s_output,
            "cache_read": s_cr, "cache_write": s_cw,
        })

    per_model = []
    for bm in by_model.values():
        usage = {"input_tokens": bm["input_tokens"], "output_tokens": bm["output_tokens"],
                 "cache_creation_input_tokens": bm["cache_write"],
                 "cache_read_input_tokens": bm["cache_read"]}
        bm["cost"] = compute_cost(usage, bm["family"])
        per_model.append(bm)
    per_model.sort(key=lambda x: -x["cost"])

    daily = [{"date": d, "cost": v["cost"], "tokens": v["tokens"]} for d, v in sorted(by_day.items())]

    first = min(all_ts) if all_ts else ""
    last = max(all_ts) if all_ts else ""
    days = 0
    if first and last:
        try:
            d1 = datetime.fromisoformat(first.rstrip("Z"))
            d2 = datetime.fromisoformat(last.rstrip("Z"))
            days = (d2.date() - d1.date()).days + 1
        except ValueError:
            days = 0

    return {
        "window": {"first": first, "last": last, "days": days,
                   "sessions": len(sessions), "turns": total_turns},
        "total": {"cost": total_cost, "tokens": total_tokens},
        "per_model": per_model,
        "per_session": per_session,
        "daily": daily,
    }


def filter_by_topic(sessions: dict, transcript_dir: Path, topic: str) -> dict:
    """Return subset of sessions whose JSONL content has >=3 hits of `topic`.

    Case-insensitive substring match, attributed per line: each line's hits are
    credited only to the sessionId on that line. A session that spans multiple
    files (parent + subagents) sums its hits across them.
    """
    if not topic:
        return sessions
    if not transcript_dir.exists() or not transcript_dir.is_dir():
        return {}
    needle = topic.lower()
    hits_by_sid: dict = defaultdict(int)

    paths = list(transcript_dir.glob("*.jsonl")) + list(transcript_dir.glob("*/subagents/*.jsonl"))
    for p in paths:
        try:
            with open(p, "r", errors="ignore") as f:
                for line in f:
                    if '"sessionId"' not in line:
                        continue
                    hits = line.lower().count(needle)
                    if hits == 0:
                        continue
                    try:
                        obj = json.loads(line)
                    except (json.JSONDecodeError, ValueError):
                        continue
                    sid = obj.get("sessionId")
                    if sid:
                        hits_by_sid[sid] += hits
        except OSError:
            continue

    return {sid: msgs for sid, msgs in sessions.items() if hits_by_sid.get(sid, 0) >= 3}


def _signal(sid: str, severity: str, anchor: str, cost_share: float, tip: str) -> dict:
    return {"id": sid, "severity": severity, "anchor": anchor,
            "cost_share": round(cost_share, 2), "tip": tip}


def detect_signals(agg: dict) -> list:
    """Run all 6 signal detectors. Return list of triggered signals (warn/ok)."""
    out: list = []
    total_cost = agg["total"]["cost"]

    # 1. Opus on lightweight work (>=3 sessions where model is opus and avg output <2K per turn)
    light_opus = [
        s for s in agg["per_session"]
        if "opus" in (s.get("model") or "").lower()
        and s["turns"] > 0
        and (s["output_tokens"] / s["turns"]) < 2000
    ]
    if len(light_opus) >= 3:
        total_turns = sum(s["turns"] for s in light_opus)
        avg_out = sum(s["output_tokens"] for s in light_opus) / total_turns
        cost = sum(s["cost"] for s in light_opus)
        out.append(_signal(
            "opus-on-lightweight", "warn",
            f"{len(light_opus)} sessions: avg {avg_out / 1000:.1f}K output tokens per turn",
            cost,
            "Use /model haiku for routine edits and lookups",
        ))

    # 2/3. Cache-write and cache-read ratios
    total_cr = sum(m["cache_read"] for m in agg["per_model"])
    total_di = sum(m["input_tokens"] for m in agg["per_model"])

    cw_cost = sum(
        compute_cost({"cache_creation_input_tokens": m["cache_write"],
                      "input_tokens": 0, "output_tokens": 0,
                      "cache_read_input_tokens": 0}, m["family"])
        for m in agg["per_model"]
    )
    cr_cost = sum(
        compute_cost({"cache_read_input_tokens": m["cache_read"],
                      "input_tokens": 0, "output_tokens": 0,
                      "cache_creation_input_tokens": 0}, m["family"])
        for m in agg["per_model"]
    )

    # Detector 2: high-cache-write — writing more cache than you read back (cache not reused)
    # Compare token counts: if writes > reads, cache is being thrown away between sessions.
    total_cw = sum(m["cache_write"] for m in agg["per_model"])
    cache_token_basis = total_cw + total_cr
    if cache_token_basis > 0:
        cw_token_ratio = total_cw / cache_token_basis
        if cw_token_ratio > 0.50:
            out.append(_signal(
                "high-cache-write", "warn",
                f"{cw_token_ratio * 100:.0f}% of cached tokens were writes (not reads)",
                cw_cost,
                "Long sessions are cheaper than many short ones — reuse rather than restart",
            ))

    # Detector 3: low-cache-read — warm cache underused relative to direct input
    cr_basis = total_cr + total_di
    if cr_basis > 0:
        cr_ratio = total_cr / cr_basis
        if cr_ratio < 0.50:
            out.append(_signal(
                "low-cache-read", "warn",
                f"only {cr_ratio * 100:.0f}% of input came from warm cache",
                0.0,
                "Avoid /clear early in a session; it discards your warm cache",
            ))
        else:
            out.append(_signal(
                "low-cache-read", "ok",
                f"cache-read ratio healthy ({cr_ratio * 100:.0f}%) — caching is working",
                0.0, "",
            ))

    # 4. Output-heavy sessions (>50K output tokens in one session)
    for s in agg["per_session"]:
        if s["output_tokens"] > 50_000:
            out.append(_signal(
                "output-heavy", "warn",
                f"session {s['sid'][:8]} had {s['output_tokens'] / 1000:.0f}K output tokens",
                s["cost"],
                "Use Edit instead of Write for partial changes; reference files instead of re-outputting them",
            ))

    # 5. Session fragmentation: >=5 sessions on one calendar day, >=4 with <30 turns
    by_day_sessions: dict = defaultdict(list)
    for s in agg["per_session"]:
        if s.get("first_ts"):
            by_day_sessions[s["first_ts"][:10]].append(s)
    for day, sess in by_day_sessions.items():
        if len(sess) >= 5:
            short = [s for s in sess if s["turns"] < 30]
            if len(short) >= 4:
                out.append(_signal(
                    "session-fragmentation", "warn",
                    f"{day}: {len(sess)} sessions started, {len(short)} under 30 turns",
                    sum(s["cost"] for s in short),
                    "Consolidate into fewer longer sessions to retain warm cache",
                ))

    # 6. Direct-input cost > 5% of total cost
    di_cost = sum(
        compute_cost({"input_tokens": m["input_tokens"],
                      "output_tokens": 0, "cache_creation_input_tokens": 0,
                      "cache_read_input_tokens": 0}, m["family"])
        for m in agg["per_model"]
    )
    if total_cost > 0 and (di_cost / total_cost) > 0.05:
        out.append(_signal(
            "direct-input-cost", "warn",
            f"direct (uncached) input is {di_cost / total_cost * 100:.1f}% of total cost",
            di_cost,
            "First user message sets the cache breakpoint — keep system prompt + initial context stable",
        ))

    return out


SIGNAL_TITLES = {
    "opus-on-lightweight": "Opus on lightweight work",
    "high-cache-write": "High cache-write ratio",
    "low-cache-read": "Cache-read ratio",
    "output-heavy": "Output-heavy session",
    "session-fragmentation": "Session fragmentation",
    "direct-input-cost": "Direct (uncached) input",
}


def _fmt_tokens(n: int) -> str:
    """Compact token formatter: 1.2M, 3.4K, 567."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def _fmt_dollars(n: float) -> str:
    return f"${n:,.2f}"


def format_human_report(agg: dict, signals: list, repo: str, scope_label: str) -> str:
    lines = []
    push = lines.append

    push("=== Claude Code cost report ===")
    push(f"Repo:    {repo}")
    push(f"Scope:   {scope_label}")
    w = agg["window"]
    if w["sessions"] == 0:
        push(f"Window:  (no transcripts) — 0 sessions")
    else:
        push(f"Window:  {w['first'][:10]} → {w['last'][:10]}  "
             f"({w['days']} days, {w['sessions']} sessions, {w['turns']:,} turns)")
    push("")

    push("=== Total ===")
    push(f"{_fmt_dollars(agg['total']['cost'])}   {_fmt_tokens(agg['total']['tokens'])} tokens")
    for m in agg["per_model"]:
        est = " (estimated)" if m["estimated"] else ""
        total_tokens = m['input_tokens'] + m['output_tokens'] + m['cache_read'] + m['cache_write']
        push(f"  {m['model']:<28s}{est}  {_fmt_dollars(m['cost']):>12s}  "
             f"{_fmt_tokens(total_tokens):>8s} tokens   "
             f"(cache_read {_fmt_tokens(m['cache_read'])}, output {_fmt_tokens(m['output_tokens'])}, "
             f"cache_write {_fmt_tokens(m['cache_write'])}, input {_fmt_tokens(m['input_tokens'])})")
    push("")

    if agg["per_session"]:
        push("=== Top 5 sessions by cost ===")
        for s in sorted(agg["per_session"], key=lambda x: -x["cost"])[:5]:
            push(f"  {_fmt_dollars(s['cost']):>10s}  {s['first_ts'][:16]}  "
                 f"{s['turns']:>4} turns  {_fmt_tokens(s['tokens']):>8s} tokens  "
                 f"{s['model']:<25s}  {s['sid'][:8]}")
        push("")

    if agg["daily"]:
        push("=== Daily timeline (last 30 days) ===")
        max_cost = max(d["cost"] for d in agg["daily"])
        for d in agg["daily"][-30:]:
            bar_len = int((d["cost"] / max_cost) * 40) if max_cost > 0 else 0
            push(f"  {d['date']}  {_fmt_dollars(d['cost']):>10s}  "
                 f"{_fmt_tokens(d['tokens']):>8s} tokens   {'█' * bar_len}")
        push("")

    if signals:
        push("=== Cost-reduction signals ===")
        for s in signals:
            mark = "⚠" if s["severity"] == "warn" else "✓"
            title = SIGNAL_TITLES.get(s["id"], s["id"])
            extra = f"  (~{_fmt_dollars(s['cost_share'])} of bill)" if s["cost_share"] > 0 else ""
            push(f"  {mark} {title}: {s['anchor']}{extra}")
            if s["tip"]:
                push(f"     → Tip: {s['tip']}")
        push("")

    push("To dig deeper: ask \"explain signal X\", \"show sessions matching <topic>\", "
         "or rerun with --topic <text>.")
    return "\n".join(lines)


def format_json_report(agg: dict, signals: list, repo: str,
                       scope_label: str, topic) -> str:
    payload = {
        "repo": repo,
        "scope": {"mode": "topic" if topic else "all-time", "topic": topic},
        "window": agg["window"],
        "total": agg["total"],
        "per_model": agg["per_model"],
        "per_session": sorted(agg["per_session"], key=lambda x: -x["cost"]),
        "daily": agg["daily"],
        "signals": signals,
    }
    return json.dumps(payload, indent=2, default=str)


import argparse
import os
import sys


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(
        description="Claude Code cost analyzer + cost-reduction coach."
    )
    parser.add_argument("--cwd", default=os.getcwd(),
                        help="Repo to analyze (default: $PWD)")
    parser.add_argument("--topic", default=None,
                        help="Narrow to sessions with >=3 case-insensitive hits of TEXT")
    parser.add_argument("--json", action="store_true",
                        help="Emit structured JSON instead of human report")
    args = parser.parse_args(argv)

    cwd = Path(args.cwd)
    if not cwd.exists():
        print(f"Path {cwd} does not exist.")
        return 1

    transcript_dir = encode_cwd_to_transcript_dir(cwd)
    if not transcript_dir.exists():
        print(f"No Claude Code transcripts for this repo (looked under {transcript_dir}). "
              "Have you used Claude Code in this directory?")
        return 0

    sessions = walk_transcripts(transcript_dir)
    if not sessions:
        print(f"Found the project folder but no .jsonl transcripts.")
        return 0

    total_sessions_before = len(sessions)
    if args.topic:
        sessions = filter_by_topic(sessions, transcript_dir, args.topic)
        if not sessions:
            print(f"No sessions matched topic '{args.topic}' (>=3 hits required). "
                  f"{total_sessions_before} total sessions in this repo.")
            return 0
        scope_label = f"topic=\"{args.topic}\" ({len(sessions)} of {total_sessions_before} sessions)"
    else:
        scope_label = "all-time"

    agg = aggregate(sessions)
    signals = detect_signals(agg)

    if args.json:
        print(format_json_report(agg, signals, repo=str(cwd.resolve()),
                                  scope_label=scope_label, topic=args.topic))
    else:
        print(format_human_report(agg, signals, repo=str(cwd.resolve()),
                                   scope_label=scope_label))
    return 0


if __name__ == "__main__":
    sys.exit(main())
