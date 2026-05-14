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


if __name__ == "__main__":
    unittest.main()
