#!/usr/bin/env python3
"""Manage Google/NotebookLM authentication state via saved browser session."""
import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = DATA_DIR / "browser_state.json"
AUTH_FLAG = DATA_DIR / ".authenticated"


def cmd_status():
    if AUTH_FLAG.exists() and STATE_FILE.exists():
        print("authenticated: Google session is valid and saved.")
    else:
        print("not authenticated: Run 'setup' to log in.")


def cmd_setup():
    import os
    import subprocess

    # If no display, re-launch self under xvfb-run so the headed browser can open
    if not os.environ.get("DISPLAY"):
        xvfb = subprocess.run(["which", "xvfb-run"], capture_output=True)
        if xvfb.returncode == 0:
            print("No display detected — launching via xvfb-run (virtual display)...")
            result = subprocess.run(
                ["xvfb-run", "--auto-servernum", sys.executable, __file__, "setup"],
                env={**os.environ, "DISPLAY": ""},
            )
            sys.exit(result.returncode)
        else:
            print("ERROR: No display and xvfb-run not found.", file=sys.stderr)
            print("Options:", file=sys.stderr)
            print("  1. Run on a machine with a display and copy skills/data/browser_state.json here.", file=sys.stderr)
            print("  2. Install xvfb: apt-get install xvfb", file=sys.stderr)
            sys.exit(1)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright is not installed. Run: pip install playwright", file=sys.stderr)
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Opening browser for Google login...")
    print("Please log in with your Google account and wait for NotebookLM to load.")
    print("(You have 120 seconds)")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path="/opt/pw-browsers/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://notebooklm.google.com/")

        try:
            page.wait_for_url("https://notebooklm.google.com/**", timeout=120_000)
        except Exception:
            print("WARNING: Timed out waiting for login. Saving whatever state exists.")

        state = context.storage_state()
        STATE_FILE.write_text(json.dumps(state))
        AUTH_FLAG.touch()
        browser.close()

    print("Authentication saved successfully.")


def cmd_import_cookies(cookies_file: str):
    """
    Import cookies exported from a browser extension (e.g. Cookie-Editor).
    Accepts a JSON file containing a list of cookie objects.
    """
    path = Path(cookies_file)
    if not path.exists():
        print(f"ERROR: File not found: {cookies_file}", file=sys.stderr)
        sys.exit(1)

    raw = json.loads(path.read_text())

    # Cookie-Editor exports a flat list; Playwright storage_state expects
    # {"cookies": [...], "origins": []}
    # Normalise both formats.
    if isinstance(raw, list):
        cookies = raw
    elif isinstance(raw, dict) and "cookies" in raw:
        cookies = raw["cookies"]
    else:
        print("ERROR: Unrecognised cookie format. Export as JSON from Cookie-Editor.", file=sys.stderr)
        sys.exit(1)

    # Playwright cookie fields: name, value, domain, path, expires, httpOnly, secure, sameSite
    SAME_SITE_MAP = {
        "no_restriction": "None",
        "lax": "Lax",
        "strict": "Strict",
        "none": "None",
    }

    playwright_cookies = []
    for c in cookies:
        raw_ss = c.get("sameSite") or "Lax"
        same_site = SAME_SITE_MAP.get(raw_ss.lower(), "Lax") if isinstance(raw_ss, str) else "Lax"
        pc = {
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ".google.com"),
            "path": c.get("path", "/"),
            "expires": c.get("expirationDate", c.get("expires", -1)),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", True),
            "sameSite": same_site,
        }
        playwright_cookies.append(pc)

    state = {"cookies": playwright_cookies, "origins": []}
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state))
    AUTH_FLAG.touch()
    print(f"Imported {len(playwright_cookies)} cookies. Authentication saved.")


def cmd_clear():
    STATE_FILE.unlink(missing_ok=True)
    AUTH_FLAG.unlink(missing_ok=True)
    print("Authentication cleared.")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status")
    sub.add_parser("setup")
    sub.add_parser("clear")
    imp = sub.add_parser("import-cookies")
    imp.add_argument("--file", required=True, help="Path to exported cookies JSON file")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "setup":
        cmd_setup()
    elif args.command == "import-cookies":
        cmd_import_cookies(args.file)
    elif args.command == "clear":
        cmd_clear()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
