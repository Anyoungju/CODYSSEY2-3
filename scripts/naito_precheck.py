"""Run and export Codyssey Naito pre-evaluations through authenticated Chrome CDP."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

try:
    from scripts.login_codyssey import CDPClient, is_authenticated_tab, read_json
except ModuleNotFoundError:  # Support direct execution: python scripts/naito_precheck.py
    from login_codyssey import CDPClient, is_authenticated_tab, read_json

EVALUATION_URL = "https://usr.codyssey.kr/daejeon/ev/request/evalutionRequestWrite"
DEFAULT_PORT = 9222


def find_target(port: int) -> dict[str, Any]:
    """Find an authenticated Codyssey page, preferring the evaluation page."""
    tabs = read_json(f"http://127.0.0.1:{port}/json/list")
    authenticated = [tab for tab in tabs if is_authenticated_tab(tab)]
    if not authenticated:
        raise RuntimeError("인증된 Codyssey CDP 탭이 없습니다. open_chrome_cdp.py를 먼저 실행하세요.")
    return next(
        (tab for tab in authenticated if "evalutionRequestWrite" in tab.get("url", "")),
        authenticated[0],
    )


def wait_ready(client: CDPClient, timeout: float = 15) -> None:
    """Wait for the current document to finish loading."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if client.evaluate("document.readyState === 'complete'"):
            return
        time.sleep(0.25)
    raise TimeoutError("Codyssey 평가 페이지 로딩 시간이 초과됐습니다.")


def open_evaluation_page(client: CDPClient) -> None:
    """Navigate the authenticated tab to the evaluation request page."""
    current = client.evaluate("location.href")
    if current != EVALUATION_URL:
        client.call("Page.enable")
        client.call("Page.navigate", {"url": EVALUATION_URL})
        wait_ready(client)
        time.sleep(1)


def open_dialog(client: CDPClient) -> None:
    """Open the Naito dialog without starting a new attempt."""
    if client.evaluate("!!document.querySelector('[role=dialog]')"):
        return
    clicked = client.evaluate(
        """(() => {
          const button = [...document.querySelectorAll('button')]
            .find((item) => (item.textContent || '').includes('네이토 사전평가'));
          if (!button) return false;
          button.click();
          return true;
        })()"""
    )
    if not clicked:
        raise RuntimeError("네이토 사전평가 버튼을 찾지 못했습니다.")
    time.sleep(1)


def refresh_dialog(client: CDPClient) -> None:
    """Close and reopen the dialog so server-side results are fetched again."""
    client.evaluate(
        "document.querySelector('.ai-preeval-btn-close, .modal-close-btn')?.click(); true"
    )
    time.sleep(0.5)
    open_dialog(client)


def snapshot(client: CDPClient) -> dict[str, Any]:
    """Extract the active result and repository metadata from the dialog."""
    return client.evaluate(
        """(() => {
          const dialog = document.querySelector('[role=dialog]');
          const panel = dialog?.querySelector('.ai-pre-eval-result-panel');
          const tabs = dialog ? [...dialog.querySelectorAll('.ai-pre-evaluation-tab-header button')]
            .map((item) => (item.textContent || '').trim()) : [];
          const items = panel ? [...panel.querySelectorAll('li')].map((item) =>
            (item.innerText || '').trim()) : [];
          return {
            repository_url: document.querySelector('#srccdUrlAddr')?.value || '',
            branch: document.querySelector('#brnchNm')?.value || '',
            dialog_text: dialog?.innerText || '',
            tabs,
            summary: panel ? (panel.innerText || '').split('항목별 평가')[0].trim() : '',
            items
          };
        })()"""
    )


def parse_item_text(text: str) -> dict[str, Any]:
    """Convert one Korean result card into structured fields."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    status = lines[0] if lines and lines[0] in {"PASS", "FAIL"} else "UNKNOWN"
    match = re.search(r"#(\d+)", text)
    labels = {"근거": "evidence", "잘한 점": "strength", "부족한 점": "gap", "보완": "action"}
    fields: dict[str, str] = {}
    current: str | None = None
    values: list[str] = []
    for line in lines[2:]:
        if line in labels:
            if current:
                fields[current] = "\n".join(values)
            current, values = labels[line], []
        elif current:
            values.append(line)
    if current:
        fields[current] = "\n".join(values)
    return {"number": int(match.group(1)) if match else None, "status": status, **fields}


def structured_result(raw: dict[str, Any]) -> dict[str, Any]:
    """Build a stable JSON result from a browser snapshot."""
    score = re.search(r"(\d+)%", raw.get("summary", ""))
    passed = re.search(r"\((\d+)\s*/\s*(\d+)", raw.get("summary", ""))
    items = []
    for position, item_text in enumerate(raw.get("items", []), start=1):
        item = parse_item_text(item_text)
        if item["number"] is None:
            item["number"] = position
        items.append(item)
    return {
        "repository_url": raw.get("repository_url"),
        "branch": raw.get("branch"),
        "score_percent": int(score.group(1)) if score else None,
        "passed": int(passed.group(1)) if passed else None,
        "total": int(passed.group(2)) if passed else None,
        "summary": raw.get("summary", ""),
        "items": items,
        "tabs": raw.get("tabs", []),
    }


def start_attempt(client: CDPClient) -> int:
    """Start a new attempt and return the previous result-tab count."""
    before = len(snapshot(client).get("tabs", []))
    clicked = client.evaluate(
        """(() => {
          const button = document.querySelector(
            '.ai-preeval-empty__start-btn, .ai-preeval-btn-primary'
          );
          if (!button || button.disabled) return false;
          button.click();
          return true;
        })()"""
    )
    if not clicked:
        raise RuntimeError("평가 시작 버튼이 없거나 남은 시도가 없습니다.")
    return before


def wait_for_attempt(
    client: CDPClient, previous_tabs: int, timeout: float, poll_interval: float
) -> dict[str, Any]:
    """Wait for a new completed result, refreshing the dialog periodically."""
    deadline = time.monotonic() + timeout
    next_refresh = time.monotonic() + 30
    while time.monotonic() < deadline:
        raw = snapshot(client)
        tabs = raw.get("tabs", [])
        running = "진행 중" in raw.get("dialog_text", "") or "평가 중" in raw.get("dialog_text", "")
        if len(tabs) > previous_tabs and raw.get("items") and not running:
            return raw
        if time.monotonic() >= next_refresh:
            refresh_dialog(client)
            next_refresh = time.monotonic() + 30
        time.sleep(poll_interval)
    raise TimeoutError("네이토 평가 결과 대기 시간이 초과됐습니다. 나중에 조회 모드로 확인하세요.")


def to_markdown(result: dict[str, Any]) -> str:
    """Render a compact Markdown report."""
    lines = [
        "# 네이토 사전평가 결과",
        "",
        f"- 저장소: {result.get('repository_url') or '-'}",
        f"- 브랜치: `{result.get('branch') or '-'}`",
        f"- 점수: **{result.get('score_percent')}% ({result.get('passed')}/{result.get('total')})**",
        "",
        "## 항목별 결과",
        "",
    ]
    for item in result.get("items", []):
        lines.extend(
            [
                f"### #{item.get('number')} — {item.get('status')}",
                "",
                f"- 근거: {item.get('evidence', '-')}",
                f"- 잘한 점: {item.get('strength', '-')}",
                f"- 부족한 점: {item.get('gap', '-')}",
                f"- 보완: {item.get('action', '-')}",
                "",
            ]
        )
    return "\n".join(lines)


def save_result(result: dict[str, Any], output: Path) -> None:
    """Save JSON and a sibling Markdown report."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    output.with_suffix(".md").write_text(to_markdown(result), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--start", action="store_true", help="새 평가 시도를 시작합니다.")
    mode.add_argument(
        "--wait",
        action="store_true",
        help="이미 진행 중인 평가에 다시 연결해 완료까지 기다립니다.",
    )
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--poll", type=float, default=5)
    parser.add_argument("--output", type=Path, help="JSON 저장 경로(.md도 함께 생성)")
    return parser.parse_args()


def main() -> int:
    """Inspect the latest result or explicitly start and wait for a new one."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    target = find_target(args.port)
    client = CDPClient(target["webSocketDebuggerUrl"])
    try:
        open_evaluation_page(client)
        open_dialog(client)
        if args.start:
            previous_tabs = start_attempt(client)
            raw = wait_for_attempt(client, previous_tabs, args.timeout, args.poll)
        elif args.wait:
            current = snapshot(client)
            if not any("⏳" in tab for tab in current.get("tabs", [])):
                raise RuntimeError("진행 중인 네이토 평가를 찾지 못했습니다.")
            previous_tabs = max(0, len(current.get("tabs", [])) - 1)
            raw = wait_for_attempt(client, previous_tabs, args.timeout, args.poll)
        else:
            raw = snapshot(client)
        result = structured_result(raw)
    finally:
        client.close()
    if args.output:
        save_result(result, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("score_percent") is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
