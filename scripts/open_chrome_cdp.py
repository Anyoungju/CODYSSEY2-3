"""Open Chrome with a loopback-only Chrome DevTools Protocol endpoint."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CDP_PORT = 9222
DEFAULT_START_URL = "https://codyssey.kr/loginForm"


def load_dotenv(path: Path) -> dict[str, str]:
    """Load simple KEY=VALUE entries without adding a third-party dependency."""
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def find_chrome(config: dict[str, str]) -> Path:
    """Return the configured Chrome executable or a standard Windows install."""
    configured_path = config.get("CHROME_PATH") or os.environ.get("CHROME_PATH")
    candidates = [
        Path(configured_path) if configured_path else None,
        Path(os.environ.get("PROGRAMFILES", ""))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", ""))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Google/Chrome/Application/chrome.exe",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise FileNotFoundError("Google Chrome executable was not found.")


def read_cdp_version(port: int) -> dict[str, object] | None:
    """Return CDP version metadata when the local endpoint is ready."""
    try:
        with urlopen(
            f"http://127.0.0.1:{port}/json/version", timeout=1
        ) as response:
            return json.load(response)
    except (OSError, URLError, json.JSONDecodeError):
        return None


def open_tab(port: int, url: str) -> None:
    """Open a new tab through an existing CDP endpoint."""
    encoded_url = quote(url, safe="")
    request = Request(
        f"http://127.0.0.1:{port}/json/new?{encoded_url}", method="PUT"
    )
    with urlopen(request, timeout=2):
        return


def launch_chrome(chrome: Path, port: int, profile_dir: Path, url: str) -> None:
    """Launch a detached Chrome process configured for local CDP access."""
    profile_dir.mkdir(parents=True, exist_ok=True)
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )

    subprocess.Popen(
        [
            str(chrome),
            f"--remote-debugging-port={port}",
            "--remote-debugging-address=127.0.0.1",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            url,
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
        close_fds=True,
    )


def is_enabled(value: str) -> bool:
    """Return whether a dotenv-style boolean value is enabled."""
    return value.strip().lower() in {"1", "true", "yes", "on"}


def auto_login(config: dict[str, str]) -> int:
    """Run the Codyssey login helper when automatic login is enabled."""
    configured = os.environ.get(
        "CODYSSEY_AUTO_LOGIN",
        config.get("CODYSSEY_AUTO_LOGIN", "true"),
    )
    if not is_enabled(configured):
        return 0

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts/login_codyssey.py")],
        check=False,
        timeout=20,
    )
    return result.returncode


def main() -> int:
    """Open or reuse the project's CDP-enabled Chrome instance."""
    config = load_dotenv(PROJECT_ROOT / ".env")
    port = int(
        os.environ.get(
            "CHROME_CDP_PORT",
            config.get("CHROME_CDP_PORT", str(DEFAULT_CDP_PORT)),
        )
    )
    if not 1 <= port <= 65535:
        raise ValueError("CHROME_CDP_PORT must be between 1 and 65535.")

    start_url = os.environ.get(
        "CHROME_CDP_START_URL",
        config.get("CHROME_CDP_START_URL", DEFAULT_START_URL),
    )
    profile_dir = Path(
        os.environ.get(
            "CHROME_CDP_PROFILE_DIR",
            config.get(
                "CHROME_CDP_PROFILE_DIR",
                str(Path(tempfile.gettempdir()) / "codyssey-chrome-cdp"),
            ),
        )
    ).expanduser()

    version = read_cdp_version(port)
    if version is not None:
        open_tab(port, start_url)
        print(f"Reused CDP Chrome on http://127.0.0.1:{port}")
        return auto_login(config)

    chrome = find_chrome(config)
    launch_chrome(chrome, port, profile_dir, start_url)

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        version = read_cdp_version(port)
        if version is not None:
            print(
                f"Opened {version.get('Browser', 'Chrome')} with CDP on "
                f"http://127.0.0.1:{port}"
            )
            return auto_login(config)
        time.sleep(0.25)

    print(f"Chrome opened, but CDP did not respond on port {port}.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
