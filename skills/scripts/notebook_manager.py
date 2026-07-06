#!/usr/bin/env python3
"""Local notebook library management (JSON store)."""
import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
LIBRARY_FILE = DATA_DIR / "notebooks.json"
ACTIVE_FILE = DATA_DIR / "active_notebook.txt"


def _load() -> list[dict]:
    if not LIBRARY_FILE.exists():
        return []
    return json.loads(LIBRARY_FILE.read_text())


def _save(notebooks: list[dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LIBRARY_FILE.write_text(json.dumps(notebooks, ensure_ascii=False, indent=2))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cmd_list():
    notebooks = _load()
    active_id = ACTIVE_FILE.read_text().strip() if ACTIVE_FILE.exists() else None
    for nb in notebooks:
        nb["is_active"] = nb["id"] == active_id
    print(json.dumps(notebooks, ensure_ascii=False))


def cmd_add(url: str, name: str, description: str, topics: str):
    notebooks = _load()
    # Prevent duplicates by URL
    for nb in notebooks:
        if nb["url"] == url:
            print(json.dumps({"id": nb["id"], "message": "Notebook already exists"}))
            return
    nb = {
        "id": str(uuid.uuid4())[:8],
        "url": url,
        "name": name,
        "description": description,
        "topics": [t.strip() for t in topics.split(",") if t.strip()] if topics else [],
        "created_at": _now(),
        "updated_at": _now(),
        "use_count": 0,
        "last_used": None,
    }
    notebooks.append(nb)
    _save(notebooks)
    print(json.dumps({"id": nb["id"], "message": f"Notebook '{name}' added successfully"}))


def cmd_remove(notebook_id: str):
    notebooks = _load()
    before = len(notebooks)
    notebooks = [nb for nb in notebooks if nb["id"] != notebook_id]
    if len(notebooks) == before:
        print(f"ERROR: Notebook {notebook_id} not found", file=sys.stderr)
        sys.exit(1)
    _save(notebooks)
    # Clear active if removed
    if ACTIVE_FILE.exists() and ACTIVE_FILE.read_text().strip() == notebook_id:
        ACTIVE_FILE.unlink()
    print(json.dumps({"message": f"Notebook {notebook_id} removed"}))


def cmd_activate(notebook_id: str):
    notebooks = _load()
    ids = [nb["id"] for nb in notebooks]
    if notebook_id not in ids:
        print(f"ERROR: Notebook {notebook_id} not found", file=sys.stderr)
        sys.exit(1)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_FILE.write_text(notebook_id)
    print(json.dumps({"message": f"Notebook {notebook_id} activated"}))


def cmd_search(query: str):
    notebooks = _load()
    q = query.lower()
    results = [
        nb for nb in notebooks
        if q in nb["name"].lower()
        or q in nb["description"].lower()
        or any(q in t.lower() for t in nb["topics"])
    ]
    print(json.dumps(results, ensure_ascii=False))


def cmd_stats():
    notebooks = _load()
    active_id = ACTIVE_FILE.read_text().strip() if ACTIVE_FILE.exists() else None
    stats = {
        "total": len(notebooks),
        "active_id": active_id,
        "most_used": sorted(notebooks, key=lambda x: x["use_count"], reverse=True)[:3],
    }
    print(json.dumps(stats, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list")

    add_p = sub.add_parser("add")
    add_p.add_argument("--url", required=True)
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--description", default="")
    add_p.add_argument("--topics", default="")

    rem_p = sub.add_parser("remove")
    rem_p.add_argument("--id", required=True)

    act_p = sub.add_parser("activate")
    act_p.add_argument("--id", required=True)

    search_p = sub.add_parser("search")
    search_p.add_argument("--query", required=True)

    sub.add_parser("stats")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list()
    elif args.command == "add":
        cmd_add(args.url, args.name, args.description, args.topics)
    elif args.command == "remove":
        cmd_remove(args.id)
    elif args.command == "activate":
        cmd_activate(args.id)
    elif args.command == "search":
        cmd_search(args.query)
    elif args.command == "stats":
        cmd_stats()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
