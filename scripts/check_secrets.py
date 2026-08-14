"""Fail when tracked text files contain common committed-secret patterns."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\bgh[oprsu]_[A-Za-z0-9]{20,}\b"),
    "assigned OpenAI key": re.compile(
        r"OPENAI_API_KEY\s*=\s*(?!your_openai_api_key\b)[^\s#]{12,}"
    ),
}


def tracked_files() -> list[Path]:
    """Return files tracked by Git without following untracked dotenv files."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    return [PROJECT_ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def main() -> int:
    """Scan tracked UTF-8-compatible files and report likely secrets."""
    findings: list[str] = []
    for path in tracked_files():
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(f"{path.relative_to(PROJECT_ROOT)}:{line_number}: {label}")
    if findings:
        print("Potential committed secrets found:")
        print("\n".join(findings))
        return 1
    print("No common secret patterns found in tracked text files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
