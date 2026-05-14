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


if __name__ == "__main__":
    unittest.main()
