# Project conventions

- Keep Python code compliant with PEP 8 and use type hints for public functions.
- Prefer the Python standard library unless an external dependency is justified.
- When opening Chrome for this project, use `python scripts/open_chrome_cdp.py`.
- The Chrome launcher must use CDP on the port configured by
  `CHROME_CDP_PORT` (default: `9222`) and bind debugging to loopback only.
- Keep `CODYSSEY_AUTO_LOGIN=true` as the default so the launcher reuses an
  authenticated session or runs `scripts/login_codyssey.py` automatically.
- Do not use `Start-Process` to open Chrome unless the user explicitly requests
  that method.
