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
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright is not installed. Run: pip install playwright", file=sys.stderr)
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Opening browser for Google login...")
    print("Please log in with your Google account and wait for NotebookLM to load.")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path="/opt/pw-browsers/chromium",
            args=["--no-sandbox"],
        )
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://notebooklm.google.com/")

        print("Waiting for you to log in... (up to 120 seconds)")
        try:
            # Wait until we're past the login page (URL changes after auth)
            page.wait_for_url("https://notebooklm.google.com/**", timeout=120_000)
        except Exception:
            print("WARNING: Timed out waiting for login. Saving whatever state exists.")

        # Save full browser state (cookies + localStorage)
        state = context.storage_state()
        STATE_FILE.write_text(json.dumps(state))
        AUTH_FLAG.touch()
        browser.close()

    print("Authentication saved successfully.")


def cmd_clear():
    STATE_FILE.unlink(missing_ok=True)
    AUTH_FLAG.unlink(missing_ok=True)
    print("Authentication cleared.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["status", "setup", "clear"])
    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "setup":
        cmd_setup()
    elif args.command == "clear":
        cmd_clear()


if __name__ == "__main__":
    main()
