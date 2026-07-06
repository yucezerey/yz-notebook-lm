#!/usr/bin/env python3
"""Send a question to a NotebookLM notebook and return the answer."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = DATA_DIR / "browser_state.json"
LIBRARY_FILE = DATA_DIR / "notebooks.json"
ACTIVE_FILE = DATA_DIR / "active_notebook.txt"

NOTEBOOKLM_BASE = "https://notebooklm.google.com"


def _load_notebooks() -> list[dict]:
    if not LIBRARY_FILE.exists():
        return []
    return json.loads(LIBRARY_FILE.read_text())


def _resolve_notebook_url(notebook_id: str | None, notebook_url: str | None) -> str:
    if notebook_url:
        return notebook_url

    notebooks = _load_notebooks()

    if notebook_id:
        for nb in notebooks:
            if nb["id"] == notebook_id:
                return nb["url"]
        print(f"ERROR: Notebook '{notebook_id}' not found in library", file=sys.stderr)
        sys.exit(1)

    # Fall back to active notebook
    if ACTIVE_FILE.exists():
        active_id = ACTIVE_FILE.read_text().strip()
        for nb in notebooks:
            if nb["id"] == active_id:
                return nb["url"]

    print("ERROR: No notebook specified and no active notebook set.", file=sys.stderr)
    sys.exit(1)


def _update_use_count(url: str):
    if not LIBRARY_FILE.exists():
        return
    notebooks = json.loads(LIBRARY_FILE.read_text())
    for nb in notebooks:
        if nb["url"] == url:
            nb["use_count"] = nb.get("use_count", 0) + 1
            nb["last_used"] = datetime.now(timezone.utc).isoformat()
    LIBRARY_FILE.write_text(json.dumps(notebooks, ensure_ascii=False, indent=2))


def ask_notebooklm(url: str, question: str) -> str:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright", file=sys.stderr)
        sys.exit(1)

    if not STATE_FILE.exists():
        print("ERROR: Not authenticated. Run auth_manager.py setup first.", file=sys.stderr)
        sys.exit(1)

    storage_state = json.loads(STATE_FILE.read_text())

    print(f"Opening notebook: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/opt/pw-browsers/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()

        print("Loading notebook...")
        page.goto(url, wait_until="networkidle", timeout=30_000)

        # Check for login redirect
        if "accounts.google.com" in page.url or "signin" in page.url.lower():
            print("ERROR: Session expired. Run auth_manager.py setup to re-authenticate.", file=sys.stderr)
            browser.close()
            sys.exit(1)

        print("Waiting for chat input...")
        # NotebookLM chat textarea
        chat_selectors = [
            "textarea[placeholder*='Ask']",
            "textarea[placeholder*='Message']",
            "textarea[aria-label*='chat']",
            ".chat-input textarea",
            "rich-textarea",
        ]
        input_el = None
        for sel in chat_selectors:
            try:
                input_el = page.wait_for_selector(sel, timeout=10_000)
                if input_el:
                    break
            except PWTimeout:
                continue

        if not input_el:
            # Try a broader search
            inputs = page.query_selector_all("textarea")
            if inputs:
                input_el = inputs[-1]

        if not input_el:
            print("ERROR: Could not find chat input on the page.", file=sys.stderr)
            browser.close()
            sys.exit(1)

        print(f"Sending question: {question[:80]}...")
        input_el.click()
        input_el.fill(question)
        page.keyboard.press("Enter")

        print("Waiting for response...")
        # Wait for response to appear — poll for new assistant message
        answer = _wait_for_answer(page)

        browser.close()
        return answer


def _wait_for_answer(page, timeout_s: int = 90) -> str:
    """Poll until a new assistant response appears and stops loading."""
    from playwright.sync_api import TimeoutError as PWTimeout

    # Response selectors used by NotebookLM
    response_selectors = [
        ".response-text",
        "[data-message-role='model']",
        ".model-response",
        ".chat-response",
        "chat-turn[role='model']",
        ".message-content",
    ]

    start = time.time()
    last_text = ""

    while time.time() - start < timeout_s:
        time.sleep(2)

        for sel in response_selectors:
            elements = page.query_selector_all(sel)
            if elements:
                # Get the last (most recent) response
                last_el = elements[-1]
                text = last_el.inner_text().strip()
                if text and text != last_text:
                    last_text = text
                    # Wait a bit more to make sure streaming is done
                    time.sleep(3)
                    # Re-check for the same element
                    refreshed = page.query_selector_all(sel)
                    if refreshed:
                        final_text = refreshed[-1].inner_text().strip()
                        if final_text == text:
                            return final_text
                        last_text = final_text

    # If we have something, return it even if incomplete
    if last_text:
        return last_text + "\n[Note: Response may be truncated — timeout reached]"

    return "ERROR: No response received from NotebookLM within timeout."


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--notebook-id", default=None)
    parser.add_argument("--notebook-url", default=None)
    args = parser.parse_args()

    url = _resolve_notebook_url(args.notebook_id, args.notebook_url)
    answer = ask_notebooklm(url, args.question)
    _update_use_count(url)
    print(answer)


if __name__ == "__main__":
    main()
