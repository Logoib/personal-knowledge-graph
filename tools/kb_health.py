#!/usr/bin/env python3
"""Run deterministic health checks for the personal KG."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

from kb_paths import resolve_kb_root


ROOT = resolve_kb_root()


def run(*args: str) -> int:
    return subprocess.run([sys.executable, *args], cwd=ROOT, check=False).returncode


def tri_files_match() -> bool:
    paths = [ROOT / name for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md")]
    hashes = {hashlib.sha256(path.read_bytes()).digest() for path in paths if path.exists()}
    return len(paths) == sum(path.exists() for path in paths) and len(hashes) == 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repair", action="store_true", help="Refresh computed registry fields and search index first.")
    args = parser.parse_args(argv)

    if args.repair:
        if run("tools/kb_compile_registry.py", "--write"):
            return 1
        run("tools/kb_index_build.py")

    failed = run("tools/kb_compile_registry.py", "--check")
    failed |= run("tools/kb_link_health.py", "--strict")
    if tri_files_match():
        print("tri-file rules: OK")
    else:
        print("tri-file rules: FAIL (AGENTS.md, CLAUDE.md, GEMINI.md differ)")
        failed = 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
