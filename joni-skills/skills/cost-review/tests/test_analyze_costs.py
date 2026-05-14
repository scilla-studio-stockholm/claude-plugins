"""Tests for cost-review analyze_costs.py. Stdlib unittest only."""
import json
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


class TestFilterByTopic(unittest.TestCase):
    def _write_session(self, dir_path: Path, sid: str, content_lines: list):
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

    def test_per_line_attribution_when_file_has_multiple_sids(self):
        """When a JSONL file mixes two sessionIds, each session should only get
        credited for hits on lines mentioning its own sessionId."""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            # One file with both sessions; only s1's lines mention the topic
            path = td_path / "mixed.jsonl"
            with open(path, "w") as f:
                # 3 lines for s1, each with "OST"
                for _ in range(3):
                    f.write(
                        '{"type":"assistant","sessionId":"s1",'
                        '"timestamp":"2026-05-10T10:00:00Z",'
                        '"message":{"model":"claude-opus-4-7","usage":{"input_tokens":1,"output_tokens":1,'
                        '"cache_creation_input_tokens":0,"cache_read_input_tokens":0},'
                        '"content":[{"type":"text","text":"talking about OST"}]}}\n'
                    )
                # 1 line for s2 with no topic hit
                f.write(
                    '{"type":"assistant","sessionId":"s2",'
                    '"timestamp":"2026-05-10T10:00:00Z",'
                    '"message":{"model":"claude-opus-4-7","usage":{"input_tokens":1,"output_tokens":1,'
                    '"cache_creation_input_tokens":0,"cache_read_input_tokens":0},'
                    '"content":[{"type":"text","text":"unrelated"}]}}\n'
                )
            sessions = ac.walk_transcripts(td_path)
            kept = ac.filter_by_topic(sessions, td_path, "OST")
            # s1 has 3 hits on its own lines — should be kept
            self.assertIn("s1", kept)
            # s2 has 0 hits on its own lines — must NOT be kept even though the file has 3 OST mentions
            self.assertNotIn("s2", kept)


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
             "input_tokens": 0, "output_tokens": 5_000,
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
        per_session = [{"sid": "big", "first_ts": "2026-05-10T08:00:00Z",
                        "last_ts": "2026-05-10T12:00:00Z", "turns": 50, "tokens": 100_000,
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
        per_model = [{"model": "claude-opus-4-7", "family": "opus", "estimated": False,
                      "turns": 1, "input_tokens": 1_000_000, "output_tokens": 0,
                      "cache_read": 0, "cache_write": 0, "cost": 15.0}]
        # Total cost = 15, all from direct input -> 100% > 5%
        agg = self._build_agg(per_model=per_model, total={"cost": 15.0, "tokens": 1_000_000})
        signals = ac.detect_signals(agg)
        ids = {s["id"] for s in signals}
        self.assertIn("direct-input-cost", ids)

    def test_no_signals_on_clean_data(self):
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


if __name__ == "__main__":
    unittest.main()
