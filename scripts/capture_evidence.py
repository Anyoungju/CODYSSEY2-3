"""Capture responsive Codyssey Compass evidence through local Chrome CDP."""

from __future__ import annotations

import base64
import json
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from login_codyssey import CDPClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = PROJECT_ROOT / "docs" / "screenshots"
CDP_PORT = 9222
WEB_PORT = 8765


class QuietHandler(SimpleHTTPRequestHandler):
    """Serve project files without request logs."""

    def log_message(self, _format: str, *args: object) -> None:
        return


def create_target(url: str) -> dict[str, object]:
    """Create a new Chrome target via the loopback CDP endpoint."""
    request = Request(
        f"http://127.0.0.1:{CDP_PORT}/json/new?{quote(url, safe=':/?=&')}",
        method="PUT",
    )
    with urlopen(request, timeout=5) as response:
        return json.load(response)


def wait_until(client: CDPClient, expression: str, timeout: float = 8) -> None:
    """Wait until a browser expression evaluates to true."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if client.evaluate(expression):
            return
        time.sleep(0.15)
    raise TimeoutError(f"Browser condition was not met: {expression}")


def save_screenshot(client: CDPClient, name: str) -> None:
    """Save a PNG viewport screenshot."""
    result = client.call(
        "Page.captureScreenshot",
        {"format": "png", "fromSurface": True, "captureBeyondViewport": False},
    )
    (SCREENSHOT_DIR / name).write_bytes(base64.b64decode(result["data"]))


def set_viewport(client: CDPClient, width: int, height: int, *, mobile: bool) -> None:
    """Apply a reproducible browser viewport for visual evidence."""
    client.call(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile,
        },
    )
    client.evaluate("scrollTo(0, 0); true")
    time.sleep(0.3)


def main() -> None:
    """Serve the app, capture desktop/mobile/result views, and clean up."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    handler = partial(QuietHandler, directory=str(PROJECT_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", WEB_PORT), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = create_target(f"http://127.0.0.1:{WEB_PORT}/?demo=1")
    client = CDPClient(str(target["webSocketDebuggerUrl"]))
    try:
        client.call("Page.enable")
        client.call("Runtime.enable")
        wait_until(client, "document.readyState === 'complete'")
        time.sleep(1)

        set_viewport(client, 1440, 1000, mobile=False)
        save_screenshot(client, "desktop.png")

        set_viewport(client, 390, 844, mobile=True)
        save_screenshot(client, "mobile.png")

        set_viewport(client, 844, 390, mobile=True)
        save_screenshot(client, "tablet-landscape.png")

        set_viewport(client, 390, 844, mobile=True)
        client.evaluate(
            """(() => {
              const form = document.querySelector('#blueprint-form');
              const idea = document.querySelector('#idea');
              idea.value = '';
              idea.dispatchEvent(new Event('input', {bubbles: true}));
              form.requestSubmit();
              form.classList.add('visible');
              const top = form.getBoundingClientRect().top + scrollY - 76;
              scrollTo({top, behavior: 'instant'});
              return true;
            })()"""
        )
        wait_until(client, "document.querySelector('#idea-error').textContent.length > 0")
        time.sleep(0.8)
        save_screenshot(client, "validation-error.png")

        set_viewport(client, 1440, 1000, mobile=False)
        client.evaluate(
            """(() => {
              document.querySelector('#idea').value = '감정을 기록하면 회고 질문을 제안하는 서비스';
              document.querySelector('#blueprint-form').requestSubmit();
              return true;
            })()"""
        )
        wait_until(client, "!document.querySelector('#result').hidden")
        time.sleep(1)
        client.evaluate(
            "document.querySelector('#result').scrollIntoView({block:'start'}); true"
        )
        time.sleep(0.4)
        save_screenshot(client, "ai-result.png")
    finally:
        client.close()
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
