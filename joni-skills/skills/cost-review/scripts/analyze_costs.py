#!/usr/bin/env python3
"""cost-review: Claude Code cost analyzer + cost-reduction coach.

Reads local JSONL transcripts under ~/.claude/projects/<encoded-cwd>/ and
prints a token+dollar usage report with auto-detected cost-reduction signals.

Self-contained: stdlib only, Python 3.8+.
"""
from __future__ import annotations

from pathlib import Path


def encode_cwd_to_transcript_dir(cwd: Path) -> Path:
    """Return ~/.claude/projects/<encoded>/ for the given cwd.

    Encoding: replace every '/' in the absolute path with '-'.
    Example: /Users/x/y -> -Users-x-y
    """
    abs_path = str(cwd.resolve()) if cwd.exists() else str(cwd)
    encoded = abs_path.replace("/", "-")
    return Path.home() / ".claude/projects" / encoded
