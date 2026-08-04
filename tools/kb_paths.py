#!/usr/bin/env python3
"""Resolve the personal KG root without assuming a clone location."""

import os
from pathlib import Path


def _is_root(path: Path) -> bool:
    return (path / "wiki" / "_summaries.md").exists()


def resolve_kb_root() -> Path:
    local = Path(__file__).resolve().parent.parent
    if _is_root(local):
        return local

    configured = os.environ.get("PERSONAL_KG_ROOT")
    if configured and _is_root(Path(configured)):
        return Path(configured)

    config = Path.home() / ".personal-kg" / "root.txt"
    if config.exists():
        lines = config.read_text(encoding="utf-8-sig").splitlines()
        if lines and _is_root(Path(lines[0].strip())):
            return Path(lines[0].strip())

    raise SystemExit(
        "Personal KG root not found. Run tools/agent-hub/scripts/sync-agent-hub.ps1 "
        "or set PERSONAL_KG_ROOT."
    )
