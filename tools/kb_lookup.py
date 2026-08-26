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
FOLDERS = ("concepts", "articles", "connections")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
SUMMARY_LINE_RE = re.compile(r"^- \[((?:concepts|articles|connections)/[^\]]+?\.md)\]\s*[—-]\s*(.+)$")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def substring_hits(query: str, limit: int, include_raw: bool) -> list[dict]:
    paths = [WIKI / "_summaries.md", WIKI / "_index.md", WIKI / "glossary.md"]
    for folder in FOLDERS:
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


# --- 1-hop traversal -------------------------------------------------------
# A hit note usually links to the note that actually holds the answer. Offer
# those links as candidates (path + one-line summary, body not loaded) so the
# caller can take one more hop instead of guessing. Links come from note
# bodies, not a backlink registry, so unregistered notes still participate.


def note_paths() -> list[Path]:
    return [p for folder in FOLDERS for p in sorted((WIKI / folder).glob("*.md"))]


def summary_lines() -> dict[str, str]:
    """'wiki/articles/x.md' -> one-line summary, tag tail stripped."""
    path = WIKI / "_summaries.md"
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        match = SUMMARY_LINE_RE.match(clean(line))
        if match:
            out[f"wiki/{match.group(1)}"] = re.sub(r"\s*\(#[^)]*\)\s*$", "", match.group(2)).strip()
    return out


def link_graph() -> tuple[dict[str, set], dict[str, set]]:
    """One scan of the wiki -> (outbound, inbound), keyed by 'wiki/<folder>/<name>.md'.

    ponytail: rescans every call. Add an mtime cache if the vault reaches thousands of notes.
    """
    by_stem = {p.stem: p.relative_to(ROOT).as_posix() for p in note_paths()}
    out_map: dict[str, set] = {}
    in_map: dict[str, set] = {}
    for path in note_paths():
        src = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        targets = {by_stem[stem] for stem in
                   (n.strip().split("/")[-1].removesuffix(".md") for n in WIKILINK_RE.findall(text))
                   if stem in by_stem}
        targets.discard(src)
        for dst in targets:
            out_map.setdefault(src, set()).add(dst)
            in_map.setdefault(dst, set()).add(src)
    return out_map, in_map


def neighbors(rel: str, out_map: dict, in_map: dict, summaries: dict, cap: int) -> list[dict]:
    """1-hop candidates: outbound first, inbound fills the rest."""
    if cap <= 0 or not rel.startswith("wiki/"):
        return []
    picked: list[dict] = []
    seen = {rel}
    for arrow, source in (("->", out_map), ("<-", in_map)):
        for dst in sorted(source.get(rel, ())):
            if dst in seen:
                continue
            seen.add(dst)
            picked.append({"arrow": arrow, "path": dst, "summary": summaries.get(dst, "")})
            if len(picked) == cap:
                return picked
    return picked


def demo() -> int:
    assert clean(" a  b\n c ") == "a b c"

    out_map = {"wiki/articles/a.md": {"wiki/articles/b.md", "wiki/concepts/c.md"}}
    in_map = {"wiki/articles/a.md": {"wiki/articles/z.md"}}
    summaries = {"wiki/articles/b.md": "B summary"}

    got = neighbors("wiki/articles/a.md", out_map, in_map, summaries, 4)
    assert [n["path"] for n in got] == ["wiki/articles/b.md", "wiki/concepts/c.md", "wiki/articles/z.md"], got
    assert [n["arrow"] for n in got] == ["->", "->", "<-"], got
    assert got[0]["summary"] == "B summary" and got[1]["summary"] == ""
    # cap fills outbound first so inbound-only notes never crowd out real links
    assert [n["path"] for n in neighbors("wiki/articles/a.md", out_map, in_map, summaries, 2)] == [
        "wiki/articles/b.md", "wiki/concepts/c.md"]
    assert neighbors("wiki/articles/a.md", out_map, in_map, summaries, 0) == []
    assert neighbors("raw/articles/a.md", out_map, in_map, summaries, 4) == []
    # a note linking to itself is not its own neighbour
    assert neighbors("wiki/articles/b.md", {"wiki/articles/b.md": {"wiki/articles/b.md"}}, {}, {}, 4) == []

    assert WIKILINK_RE.findall("see [[machine-inventory]] and [[a|alias]]") == ["machine-inventory", "a"]
    assert WIKILINK_RE.findall("[[wiki/concepts/x#section]]") == ["wiki/concepts/x"]
    match = SUMMARY_LINE_RE.match("- [articles/x.md] — body text (#tag1 #tag2)")
    assert match and match.group(1) == "articles/x.md"
    assert re.sub(r"\s*\(#[^)]*\)\s*$", "", match.group(2)).strip() == "body text"

    print("kb_lookup selftest OK")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--engine", choices=("fts", "substr"), default="fts")
    parser.add_argument("--include-raw", action="store_true")
    parser.add_argument("--neighbors", type=int, default=4, metavar="N",
                        help="show up to N 1-hop neighbour candidates per hit (0 disables)")
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
    summaries = summary_lines() if args.neighbors > 0 else {}
    out_map, in_map = link_graph() if args.neighbors > 0 else ({}, {})
    for index, item in enumerate(hits, start=1):
        print(f"  [{index}] {item['path']}")
        print(f"      {item['snippet']}")
        for neighbour in neighbors(item["path"], out_map, in_map, summaries, args.neighbors):
            summary = neighbour["summary"]
            if len(summary) > 100:
                summary = summary[:100] + "..."
            print(f"      {neighbour['arrow']} {neighbour['path']}{f' - {summary}' if summary else ''}")
    if not args.include_raw:
        print("\n  > Curated wiki only. Add --include-raw when original provenance is needed.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
