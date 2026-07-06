#!/usr/bin/env python3
"""Entry point: python run.py <script_name> [args...]"""
import sys
import importlib.util
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def main():
    if len(sys.argv) < 2:
        print("Usage: run.py <script> [args...]", file=sys.stderr)
        sys.exit(1)

    script_name = sys.argv[1]
    # Remaining args are passed to the script
    sys.argv = sys.argv[1:]

    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Script not found: {script_name}", file=sys.stderr)
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("__main__", script_path)
    module = importlib.util.module_from_spec(spec)
    module.__spec__.name = "__main__"
    spec.loader.exec_module(module)


if __name__ == "__main__":
    main()
