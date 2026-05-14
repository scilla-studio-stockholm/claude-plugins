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
