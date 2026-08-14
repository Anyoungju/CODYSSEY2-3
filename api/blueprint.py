"""Vercel Python function that generates a project blueprint with OpenAI."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler
from typing import Any

MAX_BODY_BYTES = 8_192
MAX_IDEA_LENGTH = 600
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

SYSTEM_PROMPT = """당신은 초보 개발자의 아이디어를 작고 검증 가능한 웹 서비스로 바꾸는 제품 코치입니다.
한국어로 답하고, 과장 없이 Vanilla HTML/CSS/JavaScript 프론트엔드와 Python API로 40시간 안에 만들 수 있는 범위를 제안하세요.
반드시 유효한 JSON 객체만 출력하세요. 스키마:
{"service_name":"짧은 이름","one_liner":"한 문장 설명","pages":["화면 1 설명","화면 2 설명","화면 3 설명"],"ai_feature":{"title":"기능명","input":"입력","output":"출력","user_value":"가치","failure_handling":"빈 입력/API 실패/시간 초과 중 하나 이상의 UX"},"milestones":["1단계","2단계","3단계","4단계"],"risks":["위험 1","위험 2","위험 3"]}
pages는 정확히 3개 이상, milestones는 정확히 4개, risks는 2~3개로 작성하세요."""


def validate_payload(payload: Any) -> dict[str, str]:
    """Validate and normalize a client request."""
    if not isinstance(payload, dict):
        raise ValueError("요청 형식이 올바르지 않습니다.")
    idea = str(payload.get("idea", "")).strip()
    if not idea:
        raise ValueError("아이디어를 입력해 주세요.")
    if len(idea) > MAX_IDEA_LENGTH:
        raise ValueError(f"아이디어는 {MAX_IDEA_LENGTH}자 이내로 입력해 주세요.")
    return {
        "idea": idea,
        "audience": str(payload.get("audience", "")).strip()[:120] or "아직 정하지 않음",
        "constraint": str(payload.get("constraint", "")).strip()[:80] or "빠르게 MVP 완성",
    }


def parse_blueprint(raw_text: str) -> dict[str, Any]:
    """Parse and minimally validate the model's JSON response."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("AI 응답에서 JSON을 찾지 못했습니다.")
    data = json.loads(text[start : end + 1])
    required = {"service_name", "one_liner", "pages", "ai_feature", "milestones", "risks"}
    if not isinstance(data, dict) or not required.issubset(data):
        raise ValueError("AI 응답에 필요한 항목이 없습니다.")
    if not isinstance(data["pages"], list) or len(data["pages"]) < 3:
        raise ValueError("AI 응답의 화면 구성이 부족합니다.")
    return data


def generate_blueprint(payload: dict[str, str]) -> dict[str, Any]:
    """Call OpenAI Responses API and return a validated blueprint."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=18.0, max_retries=1)
    user_input = json.dumps(payload, ensure_ascii=False)
    response = client.responses.create(model=MODEL, instructions=SYSTEM_PROMPT, input=user_input)
    return parse_blueprint(response.output_text)


class handler(BaseHTTPRequestHandler):
    """HTTP handler discovered by the Vercel Python runtime."""

    def _json(self, status: int, body: dict[str, Any]) -> None:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > MAX_BODY_BYTES:
                self._json(413, {"error": "요청 크기가 허용 범위를 벗어났습니다."})
                return
            payload = validate_payload(json.loads(self.rfile.read(size)))
            if not os.getenv("OPENAI_API_KEY"):
                self._json(503, {"error": "AI 서비스 설정이 아직 완료되지 않았습니다."})
                return
            self._json(200, {"blueprint": generate_blueprint(payload), "model": MODEL})
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "JSON 요청을 읽을 수 없습니다."})
        except ValueError as error:
            self._json(400, {"error": str(error)})
        except TimeoutError:
            self._json(504, {"error": "AI 응답 시간이 초과되었습니다. 다시 시도해 주세요."})
        except Exception:
            self._json(502, {"error": "AI 응답을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."})

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        self._json(405, {"error": "POST 요청만 지원합니다."})
