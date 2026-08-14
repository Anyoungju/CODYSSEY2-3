"""Tests for reusable Naito result parsing."""

import unittest

from scripts.naito_precheck import parse_item_text, structured_result, to_markdown


class NaitoParsingTests(unittest.TestCase):
    def test_parses_result_card(self) -> None:
        parsed = parse_item_text(
            "FAIL\n평가 항목 #11\n근거\nREADME.md\n부족한 점\n로그 설명 없음\n보완\n로그 명령 추가"
        )
        self.assertEqual(parsed["number"], 11)
        self.assertEqual(parsed["status"], "FAIL")
        self.assertEqual(parsed["action"], "로그 명령 추가")

    def test_structures_score_and_counts(self) -> None:
        result = structured_result(
            {
                "summary": "74%\n(14 / 19 항목 통과)",
                "items": ["PASS\n제목 없는 평가 항목\n근거\nREADME.md"],
                "tabs": ["시도 1(14/19)"],
            }
        )
        self.assertEqual(result["score_percent"], 74)
        self.assertEqual(result["passed"], 14)
        self.assertEqual(result["total"], 19)
        self.assertEqual(result["items"][0]["number"], 1)

    def test_renders_markdown(self) -> None:
        markdown = to_markdown(
            {"score_percent": 100, "passed": 1, "total": 1, "items": []}
        )
        self.assertIn("100% (1/1)", markdown)


if __name__ == "__main__":
    unittest.main()
