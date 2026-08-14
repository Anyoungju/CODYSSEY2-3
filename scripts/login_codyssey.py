"""Log in to Codyssey through a verified local Chrome CDP session."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import socket
import struct
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGIN_URL = "https://codyssey.kr/loginForm"
EXPECTED_HOST = "codyssey.kr"
AUTHENTICATED_HOST = "usr.codyssey.kr"


def load_dotenv(path: Path) -> dict[str, str]:
    """Load simple KEY=VALUE entries from a local dotenv file."""
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def read_json(url: str) -> Any:
    """Read JSON from a loopback CDP endpoint."""
    with urlopen(url, timeout=3) as response:
        return json.load(response)


class CDPClient:
    """Minimal loopback WebSocket client for Chrome DevTools Protocol."""

    def __init__(self, websocket_url: str) -> None:
        parsed = urlsplit(websocket_url)
        if parsed.scheme != "ws" or parsed.hostname not in {"127.0.0.1", "localhost"}:
            raise ValueError("CDP WebSocket must be an unencrypted loopback URL.")
        self._host = parsed.hostname
        self._port = parsed.port or 80
        self._path = parsed.path
        self._socket = socket.create_connection((self._host, self._port), timeout=5)
        self._next_id = 0
        self._handshake()

    def _handshake(self) -> None:
        key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
        request = (
            f"GET {self._path} HTTP/1.1\r\n"
            f"Host: {self._host}:{self._port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self._socket.sendall(request.encode("ascii"))
        response = bytearray()
        while b"\r\n\r\n" not in response:
            response.extend(self._socket.recv(4096))
        header_text = response.decode("latin-1")
        if not header_text.startswith("HTTP/1.1 101"):
            raise ConnectionError("Chrome rejected the CDP WebSocket handshake.")

        expected = base64.b64encode(
            hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
            ).digest()
        ).decode("ascii")
        if f"Sec-WebSocket-Accept: {expected}".lower() not in header_text.lower():
            raise ConnectionError("Chrome returned an invalid WebSocket handshake.")

    def _read_exact(self, size: int) -> bytes:
        data = bytearray()
        while len(data) < size:
            chunk = self._socket.recv(size - len(data))
            if not chunk:
                raise ConnectionError("CDP WebSocket closed unexpectedly.")
            data.extend(chunk)
        return bytes(data)

    def _send_frame(self, payload: bytes, opcode: int = 1) -> None:
        mask = secrets.token_bytes(4)
        length = len(payload)
        header = bytearray([0x80 | opcode])
        if length < 126:
            header.append(0x80 | length)
        elif length <= 0xFFFF:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        header.extend(mask)
        masked_payload = bytes(
            value ^ mask[index % 4] for index, value in enumerate(payload)
        )
        self._socket.sendall(header + masked_payload)

    def _receive_message(self) -> str:
        fragments = bytearray()
        message_opcode: int | None = None
        while True:
            first, second = self._read_exact(2)
            final = bool(first & 0x80)
            opcode = first & 0x0F
            masked = bool(second & 0x80)
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._read_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._read_exact(8))[0]
            mask = self._read_exact(4) if masked else b""
            payload = self._read_exact(length)
            if masked:
                payload = bytes(
                    value ^ mask[index % 4] for index, value in enumerate(payload)
                )

            if opcode == 0x8:
                raise ConnectionError("Chrome closed the CDP WebSocket.")
            if opcode == 0x9:
                self._send_frame(payload, opcode=0xA)
                continue
            if opcode == 0xA:
                continue
            if opcode in {0x1, 0x2}:
                message_opcode = opcode
                fragments = bytearray(payload)
            elif opcode == 0x0:
                fragments.extend(payload)
            else:
                continue

            if final and message_opcode is not None:
                if message_opcode != 0x1:
                    raise ValueError("Unexpected binary CDP message.")
                return fragments.decode("utf-8")

    def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send one CDP command and wait for its matching response."""
        self._next_id += 1
        command_id = self._next_id
        self._send_frame(
            json.dumps(
                {"id": command_id, "method": method, "params": params or {}},
                separators=(",", ":"),
            ).encode("utf-8")
        )
        while True:
            message = json.loads(self._receive_message())
            if message.get("id") != command_id:
                continue
            if "error" in message:
                raise RuntimeError(message["error"].get("message", "CDP command failed"))
            return message.get("result")

    def evaluate(self, expression: str) -> Any:
        """Evaluate JavaScript and return a JSON-serializable value."""
        response = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
        )
        if response.get("exceptionDetails"):
            raise RuntimeError("JavaScript evaluation failed in the login page.")
        return response["result"].get("value")

    def close(self) -> None:
        """Close the WebSocket cleanly."""
        try:
            self._send_frame(b"", opcode=0x8)
        finally:
            self._socket.close()


def is_authenticated_tab(tab: dict[str, Any]) -> bool:
    """Return whether a CDP target is a verified authenticated Codyssey page."""
    parsed = urlsplit(tab.get("url", ""))
    return (
        tab.get("type") == "page"
        and parsed.scheme == "https"
        and parsed.hostname == AUTHENTICATED_HOST
    )


def is_login_tab(tab: dict[str, Any]) -> bool:
    """Return whether a CDP target is the verified Codyssey login form."""
    parsed = urlsplit(tab.get("url", ""))
    return (
        tab.get("type") == "page"
        and parsed.scheme == "https"
        and parsed.hostname == EXPECTED_HOST
        and parsed.path == "/loginForm"
    )


def find_session_target(port: int) -> tuple[str, dict[str, Any]]:
    """Wait for either an authenticated page or a verified login form."""
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        tabs = read_json(f"http://127.0.0.1:{port}/json/list")
        login = next((tab for tab in tabs if is_login_tab(tab)), None)
        if login:
            return "login", login
        authenticated = next((tab for tab in tabs if is_authenticated_tab(tab)), None)
        if authenticated:
            return "authenticated", authenticated
        time.sleep(0.25)
    raise RuntimeError("A verified Codyssey browser target was not found.")


def main() -> int:
    """Fill the verified login form and report whether navigation succeeded."""
    config = load_dotenv(PROJECT_ROOT / ".env")
    email = config.get("CODYSSEY_EMAIL", "")
    password = config.get("CODYSSEY_PASSWORD", "")
    if not email or not password:
        raise RuntimeError("CODYSSEY_EMAIL and CODYSSEY_PASSWORD must be set.")

    port = int(config.get("CHROME_CDP_PORT", "9222"))
    session_state, tab = find_session_target(port)
    if session_state == "authenticated":
        print(
            json.dumps(
                {
                    "success": True,
                    "already_authenticated": True,
                    "title": tab.get("title"),
                    "url": tab.get("url"),
                },
                ensure_ascii=False,
            )
        )
        return 0

    client = CDPClient(tab["webSocketDebuggerUrl"])
    try:
        client.call("Runtime.enable")
        verified_url = client.evaluate("location.href")
        if verified_url != LOGIN_URL:
            raise RuntimeError("The active CDP target is not the expected login URL.")

        expression = f"""
        (() => {{
          const emailInput = document.querySelector('#userId');
          const passwordInput = document.querySelector('#password');
          const submit = document.querySelector('button[type="submit"]');
          if (!emailInput || !passwordInput || !submit) {{
            return {{ ready: false }};
          }}
          const setValue = Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype, 'value'
          ).set;
          setValue.call(emailInput, {json.dumps(email)});
          emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
          emailInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
          setValue.call(passwordInput, {json.dumps(password)});
          passwordInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
          passwordInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
          submit.click();
          return {{ ready: true }};
        }})()
        """
        result = client.evaluate(expression)
        if not result or not result.get("ready"):
            raise RuntimeError("The Codyssey login form fields were not found.")

        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            time.sleep(0.5)
            tabs = read_json(f"http://127.0.0.1:{port}/json/list")
            current = next((item for item in tabs if item.get("id") == tab["id"]), None)
            if current and is_authenticated_tab(current):
                print(
                    json.dumps(
                        {
                            "success": True,
                            "already_authenticated": False,
                            "title": current.get("title"),
                            "url": current.get("url"),
                        },
                        ensure_ascii=False,
                    )
                )
                return 0

        print(
            json.dumps(
                {
                    "success": False,
                    "reason": "The page remained on the login form.",
                }
            )
        )
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
