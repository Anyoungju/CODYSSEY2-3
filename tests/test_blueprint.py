"""Unit tests for request and model-response validation."""

import json
import unittest

from api.blueprint import parse_blueprint, validate_payload


class ValidatePayloadTests(unittest.TestCase):
    def test_normalizes_optional_fields(self) -> None:
        result = validate_payload({"idea": "  학습 도우미  "})
        self.assertEqual(result["idea"], "학습 도우미")
        self.assertEqual(result["audience"], "아직 정하지 않음")

    def test_rejects_empty_idea(self) -> None:
        with self.assertRaisesRegex(ValueError, "아이디어"):
            validate_payload({"idea": "  "})

    def test_rejects_long_idea(self) -> None:
        with self.assertRaises(ValueError):
            validate_payload({"idea": "가" * 601})


class ParseBlueprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.blueprint = {
            "service_name": "테스트",
            "one_liner": "설명",
            "pages": ["홈", "설계", "결과"],
            "ai_feature": {"title": "기능"},
            "milestones": ["1", "2", "3", "4"],
            "risks": ["위험"],
        }

    def test_parses_fenced_json(self) -> None:
        raw = f"```json\n{json.dumps(self.blueprint, ensure_ascii=False)}\n```"
        self.assertEqual(parse_blueprint(raw)["service_name"], "테스트")

    def test_rejects_missing_pages(self) -> None:
        self.blueprint["pages"] = ["홈"]
        with self.assertRaisesRegex(ValueError, "화면 구성"):
            parse_blueprint(json.dumps(self.blueprint))


if __name__ == "__main__":
    unittest.main()
