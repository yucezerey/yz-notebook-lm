#!/usr/bin/env python3
"""
Ask a question about a notebook's content using Claude AI.

Flow:
1. Load the notebook's stored content from data/notebook_content/<id>.txt (or .md)
2. If no content exists, print guidance on how to add it.
3. Send question + content to Claude and return the answer.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
LIBRARY_FILE = DATA_DIR / "notebooks.json"
ACTIVE_FILE = DATA_DIR / "active_notebook.txt"
CONTENT_DIR = DATA_DIR / "notebook_content"


def _load_notebooks() -> list[dict]:
    if not LIBRARY_FILE.exists():
        return []
    return json.loads(LIBRARY_FILE.read_text())


def _resolve_notebook(notebook_id: str | None, notebook_url: str | None) -> dict:
    notebooks = _load_notebooks()

    if notebook_url:
        for nb in notebooks:
            if nb["url"] == notebook_url:
                return nb
        return {"id": "unknown", "url": notebook_url, "name": notebook_url}

    if notebook_id:
        for nb in notebooks:
            if nb["id"] == notebook_id:
                return nb
        print(f"ERROR: Notebook '{notebook_id}' not found in library", file=sys.stderr)
        sys.exit(1)

    if ACTIVE_FILE.exists():
        active_id = ACTIVE_FILE.read_text().strip()
        for nb in notebooks:
            if nb["id"] == active_id:
                return nb

    print("ERROR: No notebook specified and no active notebook set.", file=sys.stderr)
    sys.exit(1)


def _load_content(notebook: dict) -> str | None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    nb_id = notebook["id"]
    for ext in [".txt", ".md", ".json"]:
        path = CONTENT_DIR / f"{nb_id}{ext}"
        if path.exists():
            return path.read_text()
    return None


def _update_use_count(notebook: dict):
    if not LIBRARY_FILE.exists():
        return
    notebooks = json.loads(LIBRARY_FILE.read_text())
    for nb in notebooks:
        if nb["id"] == notebook["id"]:
            nb["use_count"] = nb.get("use_count", 0) + 1
            nb["last_used"] = datetime.now(timezone.utc).isoformat()
    LIBRARY_FILE.write_text(json.dumps(notebooks, ensure_ascii=False, indent=2))


def ask_with_claude(notebook: dict, question: str, content: str) -> str:
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic not installed. Run: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = f"""You are an AI assistant helping the user with questions about their NotebookLM notebook.

Notebook: {notebook.get('name', 'Unknown')}
Description: {notebook.get('description', '')}
Topics: {', '.join(notebook.get('topics', []))}

Below is the content of this notebook. Answer the user's question based on this content.
If the question cannot be answered from the content, say so clearly.

--- NOTEBOOK CONTENT ---
{content}
--- END OF CONTENT ---"""

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text


def no_content_guidance(notebook: dict) -> str:
    nb_id = notebook["id"]
    nb_name = notebook.get("name", nb_id)
    content_path = CONTENT_DIR / f"{nb_id}.txt"
    return f"""No content found for notebook '{nb_name}' (id: {nb_id}).

To enable question answering, add the notebook's content:

Option 1 — Paste text content:
  Create the file: {content_path}
  Paste your notebook sources (text from your documents) into it.

Option 2 — Export from NotebookLM:
  1. Open your notebook: {notebook.get('url', '')}
  2. From each source, copy the text content.
  3. Save it to: {content_path}

Option 3 — Use the add-content command:
  python skills/scripts/notebook_manager.py add-content --id {nb_id} --file /path/to/content.txt

Once content is added, re-run your question."""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--notebook-id", default=None)
    parser.add_argument("--notebook-url", default=None)
    args = parser.parse_args()

    notebook = _resolve_notebook(args.notebook_id, args.notebook_url)
    content = _load_content(notebook)

    if not content:
        print(no_content_guidance(notebook))
        sys.exit(0)

    answer = ask_with_claude(notebook, args.question, content)
    _update_use_count(notebook)
    print(answer)


if __name__ == "__main__":
    main()
