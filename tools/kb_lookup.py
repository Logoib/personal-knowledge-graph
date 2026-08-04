#!/usr/bin/env python3
"""Ranked, low-context lookup over the personal knowledge graph."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_paths import resolve_kb_root


ROOT = resolve_kb_root()
WIKI = ROOT / "wiki"


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def substring_hits(query: str, limit: int, include_raw: bool) -> list[dict]:
    paths = [WIKI / "_summaries.md", WIKI / "_index.md", WIKI / "glossary.md"]
    for folder in ("concepts", "articles", "connections"):
        paths.extend(sorted((WIKI / folder).glob("*.md")))
    if include_raw and (ROOT / "raw").exists():
        paths.extend(sorted((ROOT / "raw").rglob("*.md")))

    needle = query.casefold()
    found: list[dict] = []
    for path in paths:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            snippet = clean(line)
            if not snippet or needle not in snippet.casefold():
                continue
            score = (60 if needle in rel.casefold() else 0) + (50 if snippet.casefold().startswith(needle) else 0)
            score += 40 if rel.endswith("_summaries.md") else 0
            found.append({"path": rel, "snippet": snippet, "score": score})

    found.sort(key=lambda item: (-item["score"], item["path"], item["snippet"]))
    unique: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for item in found:
        key = (item["path"], item["snippet"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
        if len(unique) == limit:
            break
    return unique


def lookup(query: str, limit: int, engine: str, include_raw: bool) -> tuple[str, list[dict]]:
    if engine == "fts":
        try:
            import kb_index_build

            hits = kb_index_build.search(query, limit, root=ROOT, include_raw=include_raw)
        except Exception:
            hits = None
        if hits is not None:
            return "fts", hits
    return "substr", substring_hits(query, limit, include_raw)


def demo() -> int:
    assert clean(" a  b\n c ") == "a b c"
    print("kb_lookup selftest OK")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--engine", choices=("fts", "substr"), default="fts")
    parser.add_argument("--include-raw", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return demo()
    if not args.query:
        parser.error("--query is required")

    engine, hits = lookup(args.query, args.limit, args.engine, args.include_raw)
    print(f"Query: {args.query}\n\nKG hits (engine={engine}):")
    if not hits:
        print("  none")
        return 0
    for index, item in enumerate(hits, start=1):
        print(f"  [{index}] {item['path']}")
        print(f"      {item['snippet']}")
    if not args.include_raw:
        print("\n  > Curated wiki only. Add --include-raw when original provenance is needed.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
