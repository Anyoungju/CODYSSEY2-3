"""Inspect the current authenticated Codyssey page through local CDP."""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

from login_codyssey import CDPClient, is_authenticated_tab, read_json


def find_page(port: int) -> dict[str, Any]:
    """Return the first authenticated Codyssey page target."""
    tabs = read_json(f"http://127.0.0.1:{port}/json/list")
    page = next((tab for tab in tabs if is_authenticated_tab(tab)), None)
    if page is None:
        raise RuntimeError("An authenticated Codyssey page was not found.")
    return page


def inspect_page(port: int) -> dict[str, Any]:
    """Return visible text and navigation elements from the current page."""
    page = find_page(port)
    client = CDPClient(page["webSocketDebuggerUrl"])
    try:
        client.call("Runtime.enable")
        expression = """
        (() => ({
          title: document.title,
          url: location.href,
          text: document.body.innerText,
          links: [...document.querySelectorAll('a')].map((element, index) => ({
            index,
            text: (element.innerText || '').trim(),
            href: element.href
          })).filter((item) => item.text || item.href),
          buttons: [...document.querySelectorAll('button')].map((element, index) => ({
            index,
            text: (element.innerText || '').trim(),
            ariaLabel: element.getAttribute('aria-label') || '',
            title: element.getAttribute('title') || ''
          })).filter((item) => item.text || item.ariaLabel || item.title),
          missionNodes: (() => {
            const matches = [];
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let node;
            while ((node = walker.nextNode())) {
              const text = (node.nodeValue || '').trim();
              if (!/^A[0-9]+-[0-9]+$/.test(text)) continue;
              const element = node.parentElement;
              matches.push({
                text,
                tag: element.tagName,
                className: element.className || '',
                role: element.getAttribute('role') || '',
                tabIndex: element.getAttribute('tabindex') || '',
                outerHTML: element.outerHTML.slice(0, 1000),
                parentHTML: element.parentElement?.outerHTML.slice(0, 3000) || ''
              });
            }
            return matches;
          })()
        }))()
        """
        return client.evaluate(expression)
    finally:
        client.close()


def open_mission(port: int, mission: str) -> dict[str, Any]:
    """Open a mission node by its visible roadmap label."""
    page = find_page(port)
    client = CDPClient(page["webSocketDebuggerUrl"])
    try:
        client.call("Runtime.enable")
        expression = f"""
        (() => {{
          const label = {json.dumps(mission)};
          const node = [...document.querySelectorAll('text')]
            .find((element) => (element.textContent || '').trim() === label);
          if (!node || !node.parentElement) return false;
          node.parentElement.dispatchEvent(
            new MouseEvent('click', {{ bubbles: true, cancelable: true }})
          );
          return true;
        }})()
        """
        if not client.evaluate(expression):
            raise RuntimeError(f"Mission node {mission!r} was not found.")
        time.sleep(1)
    finally:
        client.close()
    return inspect_page(port)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9222)
    parser.add_argument(
        "--elements-only",
        action="store_true",
        help="omit the full visible page text",
    )
    parser.add_argument("--mission", help="open a roadmap mission before inspection")
    return parser.parse_args()


def main() -> int:
    """Print the current page inspection as UTF-8 JSON."""
    args = parse_args()
    result = (
        open_mission(args.port, args.mission)
        if args.mission
        else inspect_page(args.port)
    )
    if args.elements_only:
        result.pop("text", None)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
