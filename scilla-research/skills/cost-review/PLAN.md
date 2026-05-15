# cost-review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `cost-review` skill — a repo-agnostic Claude Code cost analyzer + cost-reduction coach — per spec at `scilla-research/skills/cost-review/DESIGN.md`.

**Architecture:** Single Python 3.8+ script (`scripts/analyze_costs.py`) with no third-party dependencies (stdlib only). Walks JSONL transcripts under `~/.claude/projects/<encoded-cwd>/`, aggregates token usage, applies hardcoded API list pricing, runs 6 signal detectors, prints a human report or emits JSON. SKILL.md frames invocation and follow-up. Reference doc explains each signal in depth.

**Tech Stack:** Python 3.8+ stdlib (`argparse`, `json`, `pathlib`, `re`, `collections`, `unittest` for tests). Bash via SKILL.md only for invocation. Markdown for SKILL.md and references.

---

## File Structure

```
scilla-research/skills/cost-review/
├── SKILL.md                                # Task 13
├── DESIGN.md                               # already done
├── PLAN.md                                 # this file
├── scripts/
│   └── analyze_costs.py                    # Tasks 1-11
├── references/
│   └── cost-reduction-patterns.md          # Task 12
└── tests/
    ├── __init__.py                         # Task 1
    ├── test_analyze_costs.py               # Tasks 1-10
    └── fixtures/
        └── sample_session.jsonl            # Task 3
```

All Python lives in `analyze_costs.py` as module-level functions (no classes; YAGNI). Public API consumed by tests:

| Function | Purpose |
|---|---|
| `encode_cwd_to_transcript_dir(cwd: Path) -> Path` | Path encoding rule |
| `parse_message(line: str) -> dict | None` | Extract `{sid, model, usage_dict, ts}` from a JSONL line |
| `walk_transcripts(transcript_dir: Path) -> dict[str, list[dict]]` | sessionId → list of message dicts |
| `family_for_model(model: str) -> tuple[str, bool]` | `(family, estimated)` |
| `compute_cost(usage: dict, family: str) -> float` | Dollar cost from usage dict |
| `aggregate(sessions: dict) -> dict` | Top-level summary structure |
| `filter_by_topic(sessions, transcript_dir, topic) -> dict` | Drop sessions with <3 hits (case-insensitive) |
| `detect_signals(aggregate) -> list[dict]` | Run all 6 detectors |
| `format_human_report(aggregate, signals) -> str` | Pretty stdout report |
| `format_json_report(aggregate, signals) -> str` | JSON dump |
| `main(argv) -> int` | argparse wiring |

**Working directory for all commands below:** `/Users/jonilindgren/claude-projects/claude-plugins`

**Branch:** `feat/cost-review-skill` (already created and checked out; spec already committed there).

---

### Task 1: Project skeleton + path encoder

**Files:**
- Create: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Create: `scilla-research/skills/cost-review/tests/__init__.py`
- Create: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Create empty package init for tests**

```bash
mkdir -p scilla-research/skills/cost-review/tests/fixtures
touch scilla-research/skills/cost-review/tests/__init__.py
```

- [ ] **Step 2: Write the failing test for path encoding**

Create `scilla-research/skills/cost-review/tests/test_analyze_costs.py`:

```python
"""Tests for cost-review analyze_costs.py. Stdlib unittest only."""
import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import analyze_costs as ac  # noqa: E402


class TestPathEncoding(unittest.TestCase):
    def test_encodes_absolute_path_with_leading_dash(self):
        cwd = Path("/Users/jonilindgren/claude-projects/Metria")
        expected = Path.home() / ".claude/projects/-Users-jonilindgren-claude-projects-Metria"
        self.assertEqual(ac.encode_cwd_to_transcript_dir(cwd), expected)

    def test_encodes_root(self):
        self.assertEqual(
            ac.encode_cwd_to_transcript_dir(Path("/")),
            Path.home() / ".claude/projects/-",
        )

    def test_encodes_path_with_dots(self):
        # Claude Code preserves dots in folder names
        self.assertEqual(
            ac.encode_cwd_to_transcript_dir(Path("/tmp/foo.bar")),
            Path.home() / ".claude/projects/-tmp-foo.bar",
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestPathEncoding -v
```

Expected: ImportError (no `analyze_costs.py`) or AttributeError (`encode_cwd_to_transcript_dir` not defined).

- [ ] **Step 4: Implement path encoder (minimal)**

Create `scilla-research/skills/cost-review/scripts/analyze_costs.py`:

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestPathEncoding -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/__init__.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: scaffold + path encoder

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: JSONL message parser

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
class TestParseMessage(unittest.TestCase):
    def test_parses_assistant_message_with_usage(self):
        line = (
            '{"type":"assistant","sessionId":"abc-123","timestamp":"2026-05-13T16:32:45Z",'
            '"message":{"model":"claude-opus-4-7","usage":{'
            '"input_tokens":6,"cache_creation_input_tokens":18195,'
            '"cache_read_input_tokens":8851,"output_tokens":394}}}'
        )
        result = ac.parse_message(line)
        self.assertEqual(result["sid"], "abc-123")
        self.assertEqual(result["model"], "claude-opus-4-7")
        self.assertEqual(result["ts"], "2026-05-13T16:32:45Z")
        self.assertEqual(result["usage"]["input_tokens"], 6)
        self.assertEqual(result["usage"]["output_tokens"], 394)
        self.assertEqual(result["usage"]["cache_read_input_tokens"], 8851)
        self.assertEqual(result["usage"]["cache_creation_input_tokens"], 18195)

    def test_returns_none_for_user_message_without_usage(self):
        line = '{"type":"user","sessionId":"abc","message":{"role":"user","content":"hi"}}'
        self.assertIsNone(ac.parse_message(line))

    def test_returns_none_for_metadata_line(self):
        line = '{"type":"permission-mode","sessionId":"abc","permissionMode":"default"}'
        self.assertIsNone(ac.parse_message(line))

    def test_returns_none_for_malformed_json(self):
        self.assertIsNone(ac.parse_message("{not json"))

    def test_handles_missing_optional_fields(self):
        # Session-summary records may have usage but no top-level timestamp
        line = (
            '{"type":"assistant","sessionId":"x",'
            '"message":{"model":"claude-haiku-4-5","usage":{'
            '"input_tokens":10,"output_tokens":20}}}'
        )
        result = ac.parse_message(line)
        self.assertEqual(result["sid"], "x")
        self.assertEqual(result["ts"], "")
        self.assertEqual(result["usage"]["cache_read_input_tokens"], 0)
        self.assertEqual(result["usage"]["cache_creation_input_tokens"], 0)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestParseMessage -v
```

Expected: AttributeError (`parse_message` not defined).

- [ ] **Step 3: Implement parse_message**

Append to `scripts/analyze_costs.py`:

```python
import json
from typing import Optional


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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestParseMessage -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: parse_message — extract sid/model/usage/ts from JSONL line

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Transcript folder walker

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`
- Create: `scilla-research/skills/cost-review/tests/fixtures/sample_session.jsonl`

- [ ] **Step 1: Create fixture**

Create `scilla-research/skills/cost-review/tests/fixtures/sample_session.jsonl`:

```
{"type":"permission-mode","sessionId":"abc-123","permissionMode":"default"}
{"type":"user","sessionId":"abc-123","message":{"role":"user","content":"hi"}}
{"type":"assistant","sessionId":"abc-123","timestamp":"2026-05-13T16:32:45Z","message":{"model":"claude-opus-4-7","usage":{"input_tokens":6,"cache_creation_input_tokens":18195,"cache_read_input_tokens":8851,"output_tokens":394}}}
{"type":"assistant","sessionId":"abc-123","timestamp":"2026-05-13T16:33:10Z","message":{"model":"claude-opus-4-7","usage":{"input_tokens":2,"cache_creation_input_tokens":0,"cache_read_input_tokens":27052,"output_tokens":188}}}
{"type":"assistant","sessionId":"sub-456","timestamp":"2026-05-13T16:33:30Z","message":{"model":"claude-haiku-4-5-20251001","usage":{"input_tokens":4,"cache_creation_input_tokens":3000,"cache_read_input_tokens":1000,"output_tokens":50}}}
{not valid json
```

- [ ] **Step 2: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
import tempfile
import shutil


class TestWalkTranscripts(unittest.TestCase):
    def setUp(self):
        self.fixture_dir = SKILL_DIR / "tests/fixtures"

    def test_walks_single_jsonl_and_groups_by_session(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            shutil.copy(self.fixture_dir / "sample_session.jsonl", td_path / "session.jsonl")
            sessions = ac.walk_transcripts(td_path)
            # Two distinct sessionIds in the fixture
            self.assertEqual(set(sessions.keys()), {"abc-123", "sub-456"})
            self.assertEqual(len(sessions["abc-123"]), 2)
            self.assertEqual(len(sessions["sub-456"]), 1)

    def test_walks_subagent_subdir(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            (td_path / "abc/subagents").mkdir(parents=True)
            shutil.copy(self.fixture_dir / "sample_session.jsonl",
                        td_path / "abc/subagents/agent-x.jsonl")
            sessions = ac.walk_transcripts(td_path)
            self.assertIn("abc-123", sessions)

    def test_returns_empty_for_missing_dir(self):
        sessions = ac.walk_transcripts(Path("/does/not/exist/anywhere"))
        self.assertEqual(sessions, {})
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestWalkTranscripts -v
```

Expected: AttributeError (`walk_transcripts` not defined).

- [ ] **Step 4: Implement walk_transcripts**

Append to `scripts/analyze_costs.py`:

```python
from collections import defaultdict


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
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestWalkTranscripts -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py \
        scilla-research/skills/cost-review/tests/fixtures/sample_session.jsonl
git commit -m "cost-review: walk_transcripts — top-level + subagent JSONL aggregation by sessionId

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Pricing table + cost computation

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
class TestPricing(unittest.TestCase):
    def test_family_for_opus(self):
        self.assertEqual(ac.family_for_model("claude-opus-4-7"), ("opus", False))

    def test_family_for_sonnet(self):
        self.assertEqual(ac.family_for_model("claude-sonnet-4-6"), ("sonnet", False))

    def test_family_for_haiku(self):
        self.assertEqual(ac.family_for_model("claude-haiku-4-5-20251001"), ("haiku", False))

    def test_family_for_unknown_falls_back_to_sonnet_estimated(self):
        self.assertEqual(ac.family_for_model("claude-3-opus-20240229"),
                         ("opus", False))  # still contains 'opus'
        self.assertEqual(ac.family_for_model("some-future-model"),
                         ("sonnet", True))

    def test_family_for_empty(self):
        self.assertEqual(ac.family_for_model(""), ("sonnet", True))

    def test_compute_cost_opus(self):
        # 1M input, 1M output, 1M cache_write, 1M cache_read on opus
        usage = {
            "input_tokens": 1_000_000, "output_tokens": 1_000_000,
            "cache_creation_input_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000,
        }
        cost = ac.compute_cost(usage, "opus")
        # 15 + 75 + 18.75 + 1.50 = 110.25
        self.assertAlmostEqual(cost, 110.25, places=2)

    def test_compute_cost_haiku(self):
        usage = {
            "input_tokens": 1_000_000, "output_tokens": 1_000_000,
            "cache_creation_input_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000,
        }
        cost = ac.compute_cost(usage, "haiku")
        # 1 + 5 + 1.25 + 0.10 = 7.35
        self.assertAlmostEqual(cost, 7.35, places=2)

    def test_compute_cost_zero(self):
        usage = {"input_tokens": 0, "output_tokens": 0,
                 "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
        self.assertEqual(ac.compute_cost(usage, "opus"), 0.0)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestPricing -v
```

Expected: AttributeError (`family_for_model`, `compute_cost` not defined).

- [ ] **Step 3: Implement pricing**

Append to `scripts/analyze_costs.py`:

```python
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
        usage.get("input_tokens", 0)              * p["input"]
        + usage.get("output_tokens", 0)             * p["output"]
        + usage.get("cache_creation_input_tokens", 0) * p["cache_write"]
        + usage.get("cache_read_input_tokens", 0)   * p["cache_read"]
    ) / 1_000_000
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestPricing -v
```

Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: pricing table + family detection + cost computation

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Aggregate (per-session and per-model totals)

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
class TestAggregate(unittest.TestCase):
    def _msg(self, sid, model, ts, **usage):
        defaults = dict(input_tokens=0, output_tokens=0,
                        cache_creation_input_tokens=0, cache_read_input_tokens=0)
        defaults.update(usage)
        return {"sid": sid, "model": model, "ts": ts, "usage": defaults}

    def test_aggregates_two_sessions_one_model(self):
        sessions = {
            "s1": [
                self._msg("s1", "claude-opus-4-7", "2026-05-10T10:00:00Z",
                          input_tokens=10, output_tokens=100, cache_read_input_tokens=1000),
                self._msg("s1", "claude-opus-4-7", "2026-05-10T10:05:00Z",
                          input_tokens=5, output_tokens=50, cache_read_input_tokens=500),
            ],
            "s2": [
                self._msg("s2", "claude-opus-4-7", "2026-05-11T08:00:00Z",
                          input_tokens=20, output_tokens=200, cache_read_input_tokens=2000),
            ],
        }
        agg = ac.aggregate(sessions)
        self.assertEqual(agg["window"]["sessions"], 2)
        self.assertEqual(agg["window"]["turns"], 3)
        self.assertEqual(agg["window"]["first"], "2026-05-10T10:00:00Z")
        self.assertEqual(agg["window"]["last"], "2026-05-11T08:00:00Z")

        # one model entry, opus
        self.assertEqual(len(agg["per_model"]), 1)
        opus = agg["per_model"][0]
        self.assertEqual(opus["family"], "opus")
        self.assertEqual(opus["turns"], 3)
        self.assertEqual(opus["input_tokens"], 35)
        self.assertEqual(opus["output_tokens"], 350)
        self.assertEqual(opus["cache_read"], 3500)

        # per-session
        self.assertEqual(len(agg["per_session"]), 2)
        s1 = next(s for s in agg["per_session"] if s["sid"] == "s1")
        self.assertEqual(s1["turns"], 2)

    def test_aggregates_mixed_models(self):
        sessions = {
            "s1": [
                self._msg("s1", "claude-opus-4-7", "2026-05-10T10:00:00Z", output_tokens=100),
                self._msg("s1", "claude-haiku-4-5", "2026-05-10T10:01:00Z", output_tokens=50),
            ],
        }
        agg = ac.aggregate(sessions)
        self.assertEqual(len(agg["per_model"]), 2)
        families = {m["family"] for m in agg["per_model"]}
        self.assertEqual(families, {"opus", "haiku"})

    def test_empty_input(self):
        agg = ac.aggregate({})
        self.assertEqual(agg["window"]["sessions"], 0)
        self.assertEqual(agg["window"]["turns"], 0)
        self.assertEqual(agg["per_model"], [])
        self.assertEqual(agg["per_session"], [])
        self.assertEqual(agg["total"]["cost"], 0.0)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestAggregate -v
```

Expected: AttributeError (`aggregate` not defined).

- [ ] **Step 3: Implement aggregate**

Append to `scripts/analyze_costs.py`:

```python
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
    # Per-session accumulator
    per_session: list = []
    # Per-day accumulator
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
        s_models: dict = defaultdict(int)  # model -> turn count

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

        # Pick the model with the most turns as the session's primary
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

    # Compute per-model cost
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestAggregate -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: aggregate — totals, per-model, per-session, daily

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Topic filter

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
class TestFilterByTopic(unittest.TestCase):
    def _write_session(self, dir_path: Path, sid: str, content_lines: list[str]):
        """Write a JSONL file with one assistant turn carrying given text."""
        path = dir_path / f"{sid}.jsonl"
        with open(path, "w") as f:
            for content in content_lines:
                f.write(
                    '{"type":"assistant","sessionId":"' + sid + '",'
                    '"timestamp":"2026-05-10T10:00:00Z",'
                    '"message":{"model":"claude-opus-4-7","usage":{"input_tokens":1,"output_tokens":1,'
                    '"cache_creation_input_tokens":0,"cache_read_input_tokens":0},'
                    '"content":[{"type":"text","text":' + json.dumps(content) + '}]}}\n'
                )

    def test_drops_sessions_below_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            self._write_session(td_path, "match", [
                "this is about OST", "more OST work", "OST again"  # 3 hits
            ])
            self._write_session(td_path, "nomatch", ["unrelated work"])  # 0 hits
            self._write_session(td_path, "weak", ["one OST mention"])  # 1 hit

            sessions = ac.walk_transcripts(td_path)
            kept = ac.filter_by_topic(sessions, td_path, "OST")
            self.assertIn("match", kept)
            self.assertNotIn("nomatch", kept)
            self.assertNotIn("weak", kept)

    def test_case_insensitive(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            self._write_session(td_path, "s1", ["ost", "Ost", "OST"])  # 3 hits if ci
            sessions = ac.walk_transcripts(td_path)
            kept = ac.filter_by_topic(sessions, td_path, "OST")
            self.assertIn("s1", kept)

    def test_empty_topic_returns_all(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            self._write_session(td_path, "s1", ["anything"])
            sessions = ac.walk_transcripts(td_path)
            kept = ac.filter_by_topic(sessions, td_path, "")
            self.assertEqual(kept, sessions)
```

Add `import json` to the test file imports if not already there:

```python
import json
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestFilterByTopic -v
```

Expected: AttributeError (`filter_by_topic` not defined).

- [ ] **Step 3: Implement filter_by_topic**

Append to `scripts/analyze_costs.py`:

```python
def filter_by_topic(sessions: dict, transcript_dir: Path, topic: str) -> dict:
    """Return subset of sessions whose JSONL content has >=3 hits of `topic`.

    Case-insensitive substring match across all lines of all files. If a session
    has hits in any of its files (parent + subagents), they sum.
    """
    if not topic:
        return sessions
    needle = topic.lower()
    hits_by_sid: dict = defaultdict(int)

    if not transcript_dir.exists():
        return {}
    paths = list(transcript_dir.glob("*.jsonl")) + list(transcript_dir.glob("*/subagents/*.jsonl"))
    for p in paths:
        # Cheap pass: count needle, then attribute to whichever sessionIds appear in the file.
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        n = text.lower().count(needle)
        if n == 0:
            continue
        # Find sessionIds in this file
        sids_in_file = set()
        for line in text.splitlines():
            if '"sessionId"' not in line:
                continue
            try:
                obj = json.loads(line)
                sid = obj.get("sessionId")
                if sid:
                    sids_in_file.add(sid)
            except (json.JSONDecodeError, ValueError):
                continue
        # Attribute hits to each session in the file (a session may span multiple files)
        for sid in sids_in_file:
            hits_by_sid[sid] += n

    return {sid: msgs for sid, msgs in sessions.items() if hits_by_sid.get(sid, 0) >= 3}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestFilterByTopic -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: filter_by_topic — case-insensitive, >=3 hits across files

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Signal detectors

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
class TestDetectSignals(unittest.TestCase):
    def _build_agg(self, **overrides):
        """Minimal aggregate skeleton; tests override fields they care about."""
        agg = {
            "window": {"first": "2026-05-10T10:00:00Z", "last": "2026-05-10T10:00:00Z",
                       "days": 1, "sessions": 1, "turns": 1},
            "total": {"cost": 100.0, "tokens": 1_000_000},
            "per_model": [],
            "per_session": [],
            "daily": [],
        }
        agg.update(overrides)
        return agg

    def test_opus_on_lightweight_work(self):
        # 3 opus sessions, each with avg output <2K per turn
        per_session = [
            {"sid": f"s{i}", "first_ts": "2026-05-10T10:00:00Z",
             "last_ts": "2026-05-10T10:00:00Z", "turns": 5, "tokens": 50_000,
             "cost": 10.0, "model": "claude-opus-4-7",
             "input_tokens": 0, "output_tokens": 5_000,  # avg 1K per turn
             "cache_read": 50_000, "cache_write": 0}
            for i in range(3)
        ]
        agg = self._build_agg(per_session=per_session)
        signals = ac.detect_signals(agg)
        ids = {s["id"] for s in signals}
        self.assertIn("opus-on-lightweight", ids)

    def test_high_cache_write_ratio(self):
        per_model = [{"model": "claude-opus-4-7", "family": "opus", "estimated": False,
                      "turns": 100, "input_tokens": 1000, "output_tokens": 0,
                      "cache_read": 0, "cache_write": 1_000_000, "cost": 18.78}]
        agg = self._build_agg(per_model=per_model)
        signals = ac.detect_signals(agg)
        ids = {s["id"] for s in signals}
        self.assertIn("high-cache-write", ids)

    def test_low_cache_read_ratio(self):
        per_model = [{"model": "claude-opus-4-7", "family": "opus", "estimated": False,
                      "turns": 10, "input_tokens": 1_000_000, "output_tokens": 0,
                      "cache_read": 100_000, "cache_write": 0, "cost": 15.15}]
        agg = self._build_agg(per_model=per_model)
        signals = ac.detect_signals(agg)
        ids = {s["id"] for s in signals}
        self.assertIn("low-cache-read", ids)

    def test_output_heavy_session(self):
        per_session = [{"sid": "big", "first_ts": "2026-05-10T10:00:00Z",
                        "last_ts": "2026-05-10T10:00:00Z", "turns": 50, "tokens": 100_000,
                        "cost": 50.0, "model": "claude-opus-4-7",
                        "input_tokens": 0, "output_tokens": 60_000,
                        "cache_read": 40_000, "cache_write": 0}]
        agg = self._build_agg(per_session=per_session)
        signals = ac.detect_signals(agg)
        ids = {s["id"] for s in signals}
        self.assertIn("output-heavy", ids)

    def test_session_fragmentation(self):
        per_session = [
            {"sid": f"s{i}", "first_ts": "2026-05-10T08:00:00Z",
             "last_ts": "2026-05-10T08:30:00Z", "turns": 10, "tokens": 5000,
             "cost": 1.0, "model": "claude-opus-4-7",
             "input_tokens": 0, "output_tokens": 100,
             "cache_read": 5000, "cache_write": 0}
            for i in range(5)
        ]
        agg = self._build_agg(per_session=per_session)
        signals = ac.detect_signals(agg)
        ids = {s["id"] for s in signals}
        self.assertIn("session-fragmentation", ids)

    def test_direct_input_cost(self):
        # Need direct input >5% of total cost. Direct input tokens at $15/M.
        per_model = [{"model": "claude-opus-4-7", "family": "opus", "estimated": False,
                      "turns": 1, "input_tokens": 1_000_000, "output_tokens": 0,
                      "cache_read": 0, "cache_write": 0, "cost": 15.0}]
        # Total cost = 15, all from direct input -> 100% > 5%
        agg = self._build_agg(per_model=per_model, total={"cost": 15.0, "tokens": 1_000_000})
        signals = ac.detect_signals(agg)
        ids = {s["id"] for s in signals}
        self.assertIn("direct-input-cost", ids)

    def test_no_signals_on_clean_data(self):
        # One sonnet session, healthy cache, normal output volume
        per_session = [{"sid": "ok", "first_ts": "2026-05-10T08:00:00Z",
                        "last_ts": "2026-05-10T12:00:00Z", "turns": 100, "tokens": 1_000_000,
                        "cost": 30.0, "model": "claude-sonnet-4-6",
                        "input_tokens": 100, "output_tokens": 10_000,
                        "cache_read": 800_000, "cache_write": 100_000}]
        per_model = [{"model": "claude-sonnet-4-6", "family": "sonnet", "estimated": False,
                      "turns": 100, "input_tokens": 100, "output_tokens": 10_000,
                      "cache_read": 800_000, "cache_write": 100_000, "cost": 0.79}]
        agg = self._build_agg(per_session=per_session, per_model=per_model,
                              total={"cost": 0.79, "tokens": 910_100})
        signals = ac.detect_signals(agg)
        warn_ids = {s["id"] for s in signals if s["severity"] == "warn"}
        self.assertEqual(warn_ids, set())
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestDetectSignals -v
```

Expected: AttributeError (`detect_signals` not defined).

- [ ] **Step 3: Implement detect_signals**

Append to `scripts/analyze_costs.py`:

```python
def _signal(sid: str, severity: str, anchor: str, cost_share: float, tip: str) -> dict:
    return {"id": sid, "severity": severity, "anchor": anchor,
            "cost_share": round(cost_share, 2), "tip": tip}


def detect_signals(agg: dict) -> list:
    """Run all 6 signal detectors. Return list of triggered signals (warn/ok)."""
    out: list = []
    total_cost = agg["total"]["cost"]

    # 1. Opus on lightweight work (>=3 sessions where opus and avg output < 2K)
    light_opus = [
        s for s in agg["per_session"]
        if "opus" in (s["model"] or "").lower()
        and s["turns"] > 0
        and (s["output_tokens"] / s["turns"]) < 2000
    ]
    if len(light_opus) >= 3:
        avg_out = sum(s["output_tokens"] for s in light_opus) / sum(s["turns"] for s in light_opus)
        cost = sum(s["cost"] for s in light_opus)
        out.append(_signal(
            "opus-on-lightweight", "warn",
            f"{len(light_opus)} sessions: avg {avg_out/1000:.1f}K output tokens per turn",
            cost,
            "Use /model haiku for routine edits and lookups",
        ))

    # 2/3. Cache-write and cache-read ratios — computed across all models
    total_cw = sum(m["cache_write"] for m in agg["per_model"])
    total_cr = sum(m["cache_read"] for m in agg["per_model"])
    total_di = sum(m["input_tokens"] for m in agg["per_model"])
    cw_cost = sum(compute_cost({"cache_creation_input_tokens": m["cache_write"],
                                "input_tokens": 0, "output_tokens": 0,
                                "cache_read_input_tokens": 0}, m["family"])
                  for m in agg["per_model"])
    di_cost = sum(compute_cost({"input_tokens": m["input_tokens"], "output_tokens": 0,
                                "cache_creation_input_tokens": 0,
                                "cache_read_input_tokens": 0}, m["family"])
                  for m in agg["per_model"])
    input_cost = cw_cost + di_cost  # excludes cache_read which is much cheaper
    if input_cost > 0:
        cw_ratio = cw_cost / input_cost
        if cw_ratio > 0.30:
            out.append(_signal(
                "high-cache-write", "warn",
                f"{cw_ratio*100:.0f}% of input cost spent re-creating cache",
                cw_cost,
                "Long sessions are cheaper than many short ones — reuse rather than restart",
            ))
    cr_basis = total_cr + total_di
    if cr_basis > 0:
        cr_ratio = total_cr / cr_basis
        if cr_ratio < 0.50:
            out.append(_signal(
                "low-cache-read", "warn",
                f"only {cr_ratio*100:.0f}% of input came from warm cache",
                0.0,
                "Avoid /clear early in a session; it discards your warm cache",
            ))
        else:
            out.append(_signal(
                "low-cache-read", "ok",
                f"cache-read ratio healthy ({cr_ratio*100:.0f}%) — caching is working",
                0.0, "",
            ))

    # 4. Output-heavy sessions (>50K output tokens in one session)
    heavy = [s for s in agg["per_session"] if s["output_tokens"] > 50_000]
    if heavy:
        for s in heavy:
            out.append(_signal(
                "output-heavy", "warn",
                f"session {s['sid'][:8]} had {s['output_tokens']/1000:.0f}K output tokens",
                s["cost"],
                "Use Edit instead of Write for partial changes; reference files instead of re-outputting them",
            ))

    # 5. Session fragmentation (>=5 sessions started in one calendar day, >=4 of them <30 turns)
    by_day_sessions: dict = defaultdict(list)
    for s in agg["per_session"]:
        if s["first_ts"]:
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
    if total_cost > 0 and (di_cost / total_cost) > 0.05:
        out.append(_signal(
            "direct-input-cost", "warn",
            f"direct (uncached) input is {di_cost/total_cost*100:.1f}% of total cost",
            di_cost,
            "First user message sets the cache breakpoint — keep system prompt + initial context stable",
        ))

    return out
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestDetectSignals -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: 6 signal detectors (opus-light, cache ratios, output-heavy, fragmentation, direct-input)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: Human report formatter

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
class TestFormatHumanReport(unittest.TestCase):
    def _agg(self):
        return {
            "window": {"first": "2026-05-10T08:00:00Z", "last": "2026-05-13T16:00:00Z",
                       "days": 4, "sessions": 2, "turns": 250},
            "total": {"cost": 1273.77, "tokens": 547_800_000},
            "per_model": [
                {"model": "claude-opus-4-7", "family": "opus", "estimated": False,
                 "turns": 200, "input_tokens": 30_000, "output_tokens": 4_000_000,
                 "cache_read": 416_000_000, "cache_write": 16_000_000, "cost": 1235.33},
            ],
            "per_session": [
                {"sid": "5626067c-aaaa-bbbb-cccc-dddddddddddd",
                 "first_ts": "2026-05-07T10:18:00Z", "last_ts": "2026-05-07T12:00:00Z",
                 "turns": 224, "tokens": 12_300_000, "cost": 161.46,
                 "model": "claude-opus-4-7", "input_tokens": 0, "output_tokens": 0,
                 "cache_read": 12_000_000, "cache_write": 300_000},
            ],
            "daily": [
                {"date": "2026-05-10", "cost": 100.0, "tokens": 5_000_000},
                {"date": "2026-05-11", "cost": 213.56, "tokens": 18_200_000},
            ],
        }

    def test_includes_repo_scope_window(self):
        out = ac.format_human_report(self._agg(), [], repo="/Users/x/y", scope_label="all-time")
        self.assertIn("Repo:", out)
        self.assertIn("/Users/x/y", out)
        self.assertIn("Scope:   all-time", out)
        self.assertIn("Window:", out)

    def test_includes_total_with_dollar_and_tokens(self):
        out = ac.format_human_report(self._agg(), [], repo="x", scope_label="all-time")
        self.assertIn("$1,273.77", out)
        self.assertIn("547.8M tokens", out)

    def test_includes_per_model_line(self):
        out = ac.format_human_report(self._agg(), [], repo="x", scope_label="all-time")
        self.assertIn("claude-opus-4-7", out)
        self.assertIn("$1,235.33", out)

    def test_includes_top_session_with_short_sid(self):
        out = ac.format_human_report(self._agg(), [], repo="x", scope_label="all-time")
        self.assertIn("$161.46", out)
        self.assertIn("224 turns", out)
        self.assertIn("5626067c", out)

    def test_includes_daily_timeline(self):
        out = ac.format_human_report(self._agg(), [], repo="x", scope_label="all-time")
        self.assertIn("2026-05-11", out)
        self.assertIn("$213.56", out)

    def test_includes_signal_lines(self):
        signals = [
            {"id": "opus-on-lightweight", "severity": "warn",
             "anchor": "3 sessions: avg 1.4K output tokens per turn",
             "cost_share": 45.0, "tip": "Use /model haiku for routine edits and lookups"},
            {"id": "low-cache-read", "severity": "ok",
             "anchor": "cache-read ratio healthy (62%) — caching is working",
             "cost_share": 0.0, "tip": ""},
        ]
        out = ac.format_human_report(self._agg(), signals, repo="x", scope_label="all-time")
        self.assertIn("⚠ Opus", out)  # warn marker for lightweight
        self.assertIn("Use /model haiku", out)
        self.assertIn("✓", out)  # ok marker

    def test_empty_aggregate_still_renders_a_message(self):
        empty = {
            "window": {"first": "", "last": "", "days": 0, "sessions": 0, "turns": 0},
            "total": {"cost": 0.0, "tokens": 0},
            "per_model": [], "per_session": [], "daily": [],
        }
        out = ac.format_human_report(empty, [], repo="x", scope_label="all-time")
        self.assertIn("0 sessions", out)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestFormatHumanReport -v
```

Expected: AttributeError (`format_human_report` not defined).

- [ ] **Step 3: Implement format_human_report**

Append to `scripts/analyze_costs.py`:

```python
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
        push(f"  {m['model']:<28s}{est}  {_fmt_dollars(m['cost']):>12s}  "
             f"{_fmt_tokens(m['input_tokens']+m['output_tokens']+m['cache_read']+m['cache_write']):>8s} tokens   "
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestFormatHumanReport -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: format_human_report — totals, per-model, top sessions, daily, signals

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 9: JSON report formatter

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
class TestFormatJsonReport(unittest.TestCase):
    def test_emits_valid_json_with_expected_top_keys(self):
        agg = {
            "window": {"first": "", "last": "", "days": 0, "sessions": 0, "turns": 0},
            "total": {"cost": 0.0, "tokens": 0},
            "per_model": [], "per_session": [], "daily": [],
        }
        out = ac.format_json_report(agg, [], repo="/x", scope_label="all-time", topic=None)
        parsed = json.loads(out)
        self.assertEqual(parsed["repo"], "/x")
        self.assertEqual(parsed["scope"]["mode"], "all-time")
        self.assertIsNone(parsed["scope"]["topic"])
        self.assertIn("window", parsed)
        self.assertIn("total", parsed)
        self.assertIn("per_model", parsed)
        self.assertIn("per_session", parsed)
        self.assertIn("daily", parsed)
        self.assertEqual(parsed["signals"], [])

    def test_topic_mode_in_json(self):
        agg = {"window": {"first":"","last":"","days":0,"sessions":0,"turns":0},
               "total": {"cost":0.0, "tokens":0},
               "per_model":[],"per_session":[],"daily":[]}
        out = ac.format_json_report(agg, [], repo="/x", scope_label="topic=OST",
                                    topic="OST")
        parsed = json.loads(out)
        self.assertEqual(parsed["scope"]["mode"], "topic")
        self.assertEqual(parsed["scope"]["topic"], "OST")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestFormatJsonReport -v
```

Expected: AttributeError (`format_json_report` not defined).

- [ ] **Step 3: Implement format_json_report**

Append to `scripts/analyze_costs.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestFormatJsonReport -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: format_json_report — structured output for follow-up reshaping

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 10: CLI wiring (argparse + main)

**Files:**
- Modify: `scilla-research/skills/cost-review/scripts/analyze_costs.py`
- Modify: `scilla-research/skills/cost-review/tests/test_analyze_costs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_analyze_costs.py`:

```python
import io
from unittest.mock import patch


class TestMain(unittest.TestCase):
    def test_missing_transcript_dir_prints_message_exits_zero(self):
        # Use a path whose encoded transcript dir won't exist
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with patch("sys.stdout", buf):
                rc = ac.main(["--cwd", td])
            self.assertEqual(rc, 0)
            self.assertIn("No Claude Code transcripts", buf.getvalue())

    def test_nonexistent_cwd_exits_one(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            rc = ac.main(["--cwd", "/nonexistent/path/xyz123"])
        self.assertEqual(rc, 1)

    def test_json_flag_emits_json(self):
        with tempfile.TemporaryDirectory() as td:
            # Set up a real transcript dir under a fake home
            with patch.dict("os.environ", {"HOME": td}):
                # Reload so Path.home() picks up the patched HOME — actually Path.home()
                # uses pwd, not HOME. So instead, we test via --cwd that resolves to a
                # tmp transcript dir we create directly.
                home = Path(td)
                td_cwd = home / "myrepo"
                td_cwd.mkdir()
                # Encoded transcript dir for td_cwd
                encoded = str(td_cwd.resolve()).replace("/", "-")
                tdir = home / ".claude/projects" / encoded
                tdir.mkdir(parents=True)
                # Drop a one-turn JSONL
                (tdir / "s.jsonl").write_text(
                    '{"type":"assistant","sessionId":"s",'
                    '"timestamp":"2026-05-10T10:00:00Z",'
                    '"message":{"model":"claude-haiku-4-5","usage":{'
                    '"input_tokens":1,"output_tokens":1,'
                    '"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}}\n'
                )
                # Patch Path.home to return our temp home
                with patch.object(Path, "home", classmethod(lambda cls: home)):
                    buf = io.StringIO()
                    with patch("sys.stdout", buf):
                        rc = ac.main(["--cwd", str(td_cwd), "--json"])
                    self.assertEqual(rc, 0)
                    parsed = json.loads(buf.getvalue())
                    self.assertEqual(parsed["scope"]["mode"], "all-time")
                    self.assertEqual(parsed["window"]["sessions"], 1)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestMain -v
```

Expected: AttributeError (`main` not defined).

- [ ] **Step 3: Implement main**

Append to `scripts/analyze_costs.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest tests.test_analyze_costs.TestMain -v
```

Expected: 3 passed.

- [ ] **Step 5: Run full test suite**

```bash
cd scilla-research/skills/cost-review && python3 -m unittest discover tests -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/scripts/analyze_costs.py \
        scilla-research/skills/cost-review/tests/test_analyze_costs.py
git commit -m "cost-review: CLI wiring (argparse) + main entry point

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 11: Sanity check against Metria/OST data

**Files:** none (verification step)

- [ ] **Step 1: Run the script against Metria with --topic OST**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins/scilla-research/skills/cost-review
python3 scripts/analyze_costs.py --cwd /Users/jonilindgren/claude-projects/Metria --topic OST
```

Expected: report ends with a total cost between **$1,272 and $1,275** (yesterday's manual analysis came to $1,273.77; allow ±$1 for rounding/edge cases). Per-model split should show Opus dominating (~97%).

- [ ] **Step 2: If figure is outside that band, debug**

If total > $1,275: filter is too permissive — sessions are leaking in that shouldn't be. Spot-check the top 5 sessions reported and verify they look OST-related.
If total < $1,272: filter is too strict — sessions are being dropped. Check the "N of M sessions matched" line.
If total is close (e.g. $1,200–$1,272): could be threshold differences (we used a different marker list yesterday). Document the delta in the commit message rather than block.

- [ ] **Step 3: Capture the run output to a one-off log file (NOT committed)**

```bash
python3 scripts/analyze_costs.py --cwd /Users/jonilindgren/claude-projects/Metria --topic OST > /tmp/cost-review-sanity.log
echo "Total line: $(grep -E '^\\$' /tmp/cost-review-sanity.log | head -1)"
```

- [ ] **Step 4: No commit needed (verification only)**

If the figure is in band, proceed. If not, return to Task 6 (filter) or Task 5 (aggregate) before continuing.

---

### Task 12: Reference doc — cost-reduction-patterns.md

**Files:**
- Create: `scilla-research/skills/cost-review/references/cost-reduction-patterns.md`

- [ ] **Step 1: Write the reference doc**

Create the file with one section per signal id. Each section: mechanism, how to spot in your workflow, concrete remediation.

```markdown
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

**What it means:** More than 30% of your input cost went to writing cache (re-creating the prompt prefix), not reading from it. Indicates context churn or session fragmentation.

**Why it costs more:** Cache write is $18.75/M (Opus) — 12.5× the cache read rate of $1.50/M. You pay the write cost once per cache breakpoint; if you're hitting many breakpoints, that adds up.

**How to spot it:** Lots of short sessions (`/clear` or new windows), long context that keeps growing past the 5-min cache window, or system-prompt-level churn from frequent settings tweaks.

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
1. The model regenerated a long file via Write instead of using Edit
2. Long markdown reports / specs / plans being authored
3. Verbose narration during refactoring

**Why it costs more:** Output is the most expensive token type — $75/M on Opus.

**How to spot it:** Watch for the model rewriting whole files when only a section changed. Or for explanations that re-print code blocks instead of referencing them.

**Remediation:**
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
```

- [ ] **Step 2: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/references/cost-reduction-patterns.md
git commit -m "cost-review: reference doc — long-form coaching per signal id

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 13: SKILL.md

**Files:**
- Create: `scilla-research/skills/cost-review/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

Create `scilla-research/skills/cost-review/SKILL.md`:

```markdown
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
- `--topic <text>` — narrow to sessions with ≥3 case-insensitive hits of TEXT (use for feature-specific cost like `--topic OST` or `--topic auth-refactor`)
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
- Topic filter uses ≥3 case-insensitive substring hits — conservative by design.
- Pricing table is hardcoded (April 2026). If the table looks stale, update `PRICING` in `scripts/analyze_costs.py`.
- Doesn't cover Cowork sessions (server-side, not in local JSONL).
```

- [ ] **Step 2: Verify frontmatter parses**

```bash
python3 -c "
import yaml
with open('scilla-research/skills/cost-review/SKILL.md') as f:
    text = f.read()
parts = text.split('---', 2)
fm = yaml.safe_load(parts[1])
assert fm['name'] == 'cost-review'
assert fm['user_invocable'] is True
assert 'description' in fm and len(fm['description']) > 50
print('SKILL.md frontmatter OK')
" 2>&1 || python3 -c "
# Fallback if PyYAML isn't installed
import re
with open('scilla-research/skills/cost-review/SKILL.md') as f:
    text = f.read()
parts = text.split('---', 2)
fm = parts[1]
assert 'name: cost-review' in fm
assert 'user_invocable: true' in fm
assert re.search(r'description:\\s*\\S', fm)
print('SKILL.md frontmatter OK (regex check)')
"
```

Expected: "SKILL.md frontmatter OK".

- [ ] **Step 3: Commit**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git add scilla-research/skills/cost-review/SKILL.md
git commit -m "cost-review: SKILL.md — invocation, presentation, follow-up handling

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 14: End-to-end install + invocation check

**Files:** none (verification step)

- [ ] **Step 1: Refresh the plugin cache**

The plugin source is at `/Users/jonilindgren/claude-projects/claude-plugins/scilla-research/`. The installed cache is at `~/.claude/plugins/cache/scilla-studio/scilla-research/1.0.0/`. The marketplace is registered with `autoUpdate: true` so changes should propagate, but we'll force a sync.

```bash
# Inspect current cache state
ls ~/.claude/plugins/cache/scilla-studio/scilla-research/1.0.0/skills/ | grep cost-review || echo "(not yet present)"
# If not present: copy manually for now
cp -R /Users/jonilindgren/claude-projects/claude-plugins/scilla-research/skills/cost-review \
      ~/.claude/plugins/cache/scilla-studio/scilla-research/1.0.0/skills/
ls ~/.claude/plugins/cache/scilla-studio/scilla-research/1.0.0/skills/cost-review/
```

Expected: `SKILL.md`, `scripts/`, `references/`.

- [ ] **Step 2: Run a sanity invocation against Metria**

```bash
python3 ~/.claude/plugins/cache/scilla-studio/scilla-research/1.0.0/skills/cost-review/scripts/analyze_costs.py \
  --cwd /Users/jonilindgren/claude-projects/Metria --topic OST | head -30
```

Expected: human-readable report with `Repo:`, `Scope:`, `Total:` sections and a `$1,2XX.XX` figure.

- [ ] **Step 3: Run JSON mode and validate it parses**

```bash
python3 ~/.claude/plugins/cache/scilla-studio/scilla-research/1.0.0/skills/cost-review/scripts/analyze_costs.py \
  --cwd /Users/jonilindgren/claude-projects/Metria --json | python3 -m json.tool > /dev/null && echo "JSON OK"
```

Expected: `JSON OK`.

- [ ] **Step 4: Run with default scope (no topic) on a smaller repo**

Pick a repo with less Claude usage to confirm the no-topic path:

```bash
python3 ~/.claude/plugins/cache/scilla-studio/scilla-research/1.0.0/skills/cost-review/scripts/analyze_costs.py \
  --cwd /Users/jonilindgren/claude-projects/claude-plugins
```

Expected: report renders without errors. May say "no transcripts" if Claude Code hasn't been used in that repo — that's also a valid outcome to verify.

- [ ] **Step 5: Push branch (if Joni asks)**

```bash
cd /Users/jonilindgren/claude-projects/claude-plugins
git push -u origin feat/cost-review-skill
```

Only push when Joni explicitly says to; per his global preference, commits are local until he asks.

- [ ] **Step 6: Final commit (none needed — verification only)**

If everything passed, the skill is shippable. If something failed in steps 2–4, return to the relevant task to fix.

---

## Self-Review Notes

**Spec coverage check:** Every section of DESIGN.md maps to a task:

| Spec section | Tasks |
|---|---|
| Path encoding | 1 |
| Walk transcripts (top-level + subagents) | 3 |
| Pricing table + family detection | 4 |
| Aggregate (per-session, per-model, daily) | 5 |
| Topic filter (≥3 hits, case-insensitive) | 6 |
| 6 signal detectors | 7 |
| Human report format | 8 |
| JSON mode | 9 |
| Error handling (missing dir, no transcripts, no topic match, unknown model, malformed JSONL) | 2, 3, 4, 10 |
| SKILL.md contract | 13 |
| Reference doc | 12 |
| Sanity test ($1,273.77 ±$1) | 11 |

**Type/name consistency:** All function signatures used in tests match the implementation tasks. `encode_cwd_to_transcript_dir`, `parse_message`, `walk_transcripts`, `family_for_model`, `compute_cost`, `aggregate`, `filter_by_topic`, `detect_signals`, `format_human_report`, `format_json_report`, `main` — all defined once, called consistently.

**No placeholders:** Every code step shows complete code. Every command shows expected output. Every commit message is concrete.
