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
