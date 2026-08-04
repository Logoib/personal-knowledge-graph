#!/usr/bin/env python3
"""Audit Obsidian link integrity for the personal KG vault.

Default scope is intentionally strict for curated knowledge:
- root *.md files
- wiki/**/*.md

raw/, tools/, outputs/, docs/, and .obsidian are skipped by default because they
may contain imported source material, generated outputs, tool documentation, or
planning scaffolding (docs/superpowers/) that intentionally references not-yet-
created files.
Use --include-raw when you want to inspect raw source notes too.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


WIKILINK_RE = re.compile(r"(?P<embed>!)?\[\[(?P<body>[^\]\n]+)\]\]")
MDLINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\((?P<target>[^)\n]+)\)")
TITLE_RE = re.compile(r"^title:\s*(?P<title>.+?)\s*$")
CODE_SPAN_RE = re.compile(r"`[^`]*`")

# --- 온톨로지 스키마 검사 (wiki/_ontology-schema.md 기준) ---
CONCEPT_TYPE_ENUM = {"concept", "term", "system", "process", "artifact", "tool"}
RELATION_VOCAB = {"is-a", "part-of", "depends-on", "related-to"}
ONTOLOGY_KEY_RE = re.compile(r"^ontology:\s*$")
CONCEPT_TYPE_RE = re.compile(r"^\s+concept-type:\s*(?P<v>[^\s#]+)")
ONTOLOGY_CHILD_RE = re.compile(r"^  (?P<key>[A-Za-z0-9_-]+):")
RELATIONS_KEY_RE = re.compile(r"^  relations:\s*$")
RELATION_ITEM_RE = re.compile(
    r"^\s{4}-\s*\{\s*type:\s*(?P<type>[^,}]+),\s*"
    r"target:\s*(?P<target>[^,}]+),\s*note:\s*(?P<note>.+?)\s*\}\s*$"
)
RELATION_CANDIDATE_RE = re.compile(r"^\s{4}-\s*")


@dataclass
class Issue:
    kind: str
    file: str
    line: int
    target: str
    message: str
    suggestion: str = ""


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def iter_markdown(root: Path, include_raw: bool) -> list[Path]:
    ignored_dirs = {".git", ".obsidian", "tools", "outputs", "docs", "__pycache__"}
    if not include_raw:
        ignored_dirs.add("raw")

    files: list[Path] = []
    for path in root.rglob("*.md"):
        parts = set(path.relative_to(root).parts[:-1])
        if parts & ignored_dirs:
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_title(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    for line in lines[1:80]:
        if line.strip() == "---":
            break
        match = TITLE_RE.match(line)
        if match:
            return strip_quotes(match.group("title"))
    return None


def title_aliases(title: str) -> set[str]:
    aliases = {title.strip()}
    for separator in (" (", " — ", " - ", ": "):
        if separator in title:
            aliases.add(title.split(separator, 1)[0].strip())
    # Common case: target omits a trailing qualifier after the first dash.
    if "—" in title:
        aliases.add(title.split("—", 1)[0].strip())
    return {alias for alias in aliases if alias}


def split_wikilink_body(body: str) -> str:
    target = body.split("|", 1)[0].strip()
    target = re.split(r"[#^]", target, maxsplit=1)[0].strip()
    if target.endswith(".md"):
        target = target[:-3]
    return target.replace("\\", "/")


def split_markdown_target(target: str) -> str:
    target = target.strip().split("?", 1)[0]
    target = target.split("#", 1)[0]
    return target.replace("\\", "/")


def is_external(target: str) -> bool:
    lower = target.lower()
    return (
        "://" in lower
        or lower.startswith("mailto:")
        or lower.startswith("app://")
        or lower.startswith("#")
    )


def candidate_existing(path: Path) -> Path | None:
    candidates = [path]
    if path.suffix.lower() != ".md":
        candidates.append(path.with_suffix(".md"))
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    return None


def resolve_wikilink(
    target: str,
    current: Path,
    root: Path,
    by_stem: dict[str, list[Path]],
) -> tuple[str, list[Path]]:
    if not target:
        return "missing", []

    has_path = "/" in target
    if has_path:
        paths = [
            root / target,
            current.parent / target,
        ]
        matches: list[Path] = []
        for path in paths:
            found = candidate_existing(path)
            if found and found not in matches:
                matches.append(found)
        if len(matches) == 1:
            return "ok", matches
        if len(matches) > 1:
            return "ambiguous", matches
        return "missing", []

    matches = by_stem.get(target.casefold(), [])
    if len(matches) == 1:
        return "ok", matches
    if len(matches) > 1:
        return "ambiguous", matches
    return "missing", []


def resolve_markdown_link(target: str, current: Path) -> tuple[str, list[Path]]:
    if not target or is_external(target):
        return "ignored", []
    cleaned = split_markdown_target(target)
    if not cleaned.lower().endswith(".md"):
        return "ignored", []
    found = candidate_existing(current.parent / cleaned)
    if found:
        return "ok", [found]
    return "missing", []


def build_indexes(
    files: Iterable[Path], root: Path
) -> tuple[dict[str, list[Path]], dict[str, list[Path]], dict[Path, str]]:
    by_stem: dict[str, list[Path]] = {}
    by_title: dict[str, list[Path]] = {}
    text_by_path: dict[Path, str] = {}
    for path in files:
        text = read_text(path)
        text_by_path[path.resolve()] = text
        by_stem.setdefault(path.stem.casefold(), []).append(path.resolve())
        title = parse_title(text)
        if title:
            for alias in title_aliases(title):
                by_title.setdefault(alias.casefold(), []).append(path.resolve())
    return by_stem, by_title, text_by_path


def format_target(path: Path, root: Path, display: str) -> str:
    note = rel(path, root)
    if note.endswith(".md"):
        note = note[:-3]
    return f"[[{note}|{display}]]"


def audit_ontology(text: str, display_path: str) -> list[Issue]:
    """frontmatter의 `ontology:` 블록을 스키마와 대조한다.
    - concept-type 이 enum 밖 → ontology-schema-drift
    - ontology 직속 `related-to:` 키(오용, relations[]로 가야 함) → ontology-schema-drift
    - relations[] 항목의 type/target/note 모양·어휘 위반 → ontology-schema-drift
    """
    issues: list[Issue] = []
    if not text.startswith("---"):
        return issues
    lines = text.splitlines()
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return issues

    in_ont = False
    in_relations = False
    for idx in range(1, end):
        line = lines[idx]
        line_no = idx + 1
        if ONTOLOGY_KEY_RE.match(line):
            in_ont = True
            in_relations = False
            continue
        if not in_ont:
            continue
        if line and not line[0].isspace():  # 새 top-level 키 → ontology 블록 종료
            in_ont = False
            in_relations = False
            continue
        if RELATIONS_KEY_RE.match(line):
            in_relations = True
            continue
        if in_relations and RELATION_CANDIDATE_RE.match(line):
            relation = RELATION_ITEM_RE.match(line)
            if not relation:
                issues.append(Issue(
                    kind="ontology-schema-drift", file=display_path, line=line_no,
                    target=line.strip(),
                    message="relations[] 항목은 {type, target, note} 인라인 형식이어야 함",
                ))
                continue
            values = {
                key: strip_quotes(relation.group(key)).strip()
                for key in ("type", "target", "note")
            }
            if values["type"] not in RELATION_VOCAB:
                issues.append(Issue(
                    kind="ontology-schema-drift", file=display_path, line=line_no,
                    target=values["type"],
                    message=f"relation type '{values['type']}' 는 어휘 밖 {sorted(RELATION_VOCAB)}",
                ))
            for key in ("target", "note"):
                if not values[key]:
                    issues.append(Issue(
                        kind="ontology-schema-drift", file=display_path, line=line_no,
                        target=key,
                        message=f"relations[].{key} 는 비어 있을 수 없음",
                    ))
            continue
        if in_relations and line.startswith("  ") and not line.startswith("    "):
            in_relations = False
        m = CONCEPT_TYPE_RE.match(line)
        if m and m.group("v") not in CONCEPT_TYPE_ENUM:
            issues.append(Issue(
                kind="ontology-schema-drift", file=display_path, line=line_no,
                target=m.group("v"),
                message=f"concept-type '{m.group('v')}' 는 enum 밖 {sorted(CONCEPT_TYPE_ENUM)}",
            ))
        mc = ONTOLOGY_CHILD_RE.match(line)
        if mc and mc.group("key") in RELATION_VOCAB:
            key = mc.group("key")
            issues.append(Issue(
                kind="ontology-schema-drift", file=display_path, line=line_no,
                target=key,
                message=f"ontology 직속 {key} 키 오용 → relations[] 의 {{type: {key}, target, note}} 로 이관",
            ))
    return issues


def audit(root: Path, include_raw: bool) -> list[Issue]:
    root = root.resolve()
    files = iter_markdown(root, include_raw=include_raw)
    by_stem, by_title, text_by_path = build_indexes(files, root)
    issues: list[Issue] = []

    for path in files:
        resolved_path = path.resolve()
        text = text_by_path[resolved_path]
        display_path = rel(path, root)
        if not text.strip():
            issues.append(
                Issue(
                    kind="empty-file",
                    file=display_path,
                    line=1,
                    target="",
                    message="Markdown file is empty or whitespace only.",
                )
            )

        issues.extend(audit_ontology(text, display_path))

        for line_no, line in enumerate(text.splitlines(), start=1):
            line_without_code = CODE_SPAN_RE.sub("", line)
            for match in WIKILINK_RE.finditer(line_without_code):
                raw_body = match.group("body").strip()
                target = split_wikilink_body(raw_body)
                state, matches = resolve_wikilink(target, path, root, by_stem)
                if state == "ok":
                    linked_text = text_by_path.get(matches[0])
                    if linked_text is None:
                        # raw/ 등 인덱스 밖 파일은 디스크에서 직접 읽어 판정한다
                        linked_text = read_text(matches[0])
                    if not linked_text.strip():
                        suggestion = ""
                        title_matches = [
                            item
                            for item in by_title.get(target.casefold(), [])
                            if item != matches[0]
                            and text_by_path.get(item, "").strip()
                        ]
                        if len(title_matches) == 1:
                            suggestion = format_target(title_matches[0], root, target)
                        issues.append(
                            Issue(
                                kind="empty-target",
                                file=display_path,
                                line=line_no,
                                target=raw_body,
                                message=f"Wikilink resolves to empty note: {rel(matches[0], root)}",
                                suggestion=suggestion,
                            )
                        )
                elif state == "ambiguous":
                    choices = ", ".join(rel(item, root) for item in matches)
                    issues.append(
                        Issue(
                            kind="ambiguous-wikilink",
                            file=display_path,
                            line=line_no,
                            target=raw_body,
                            message=f"Wikilink matches multiple notes: {choices}",
                        )
                    )
                else:
                    suggestion = ""
                    title_matches = by_title.get(target.casefold(), [])
                    if len(title_matches) == 1:
                        suggestion = format_target(title_matches[0], root, target)
                    issues.append(
                        Issue(
                            kind="missing-wikilink",
                            file=display_path,
                            line=line_no,
                            target=raw_body,
                            message="Wikilink target does not resolve to a markdown file.",
                            suggestion=suggestion,
                        )
                    )

            for match in MDLINK_RE.finditer(line_without_code):
                raw_target = match.group("target").strip()
                state, _ = resolve_markdown_link(raw_target, path)
                if state == "missing":
                    issues.append(
                        Issue(
                            kind="missing-markdown-link",
                            file=display_path,
                            line=line_no,
                            target=raw_target,
                            message="Markdown link target does not resolve relative to the current file.",
                        )
                    )

    return issues


def print_report(issues: list[Issue], as_json: bool) -> None:
    if as_json:
        print(json.dumps([asdict(issue) for issue in issues], ensure_ascii=False, indent=2))
        return

    if not issues:
        print("KG link health: OK")
        return

    print(f"KG link health: {len(issues)} issue(s)")
    grouped: dict[str, list[Issue]] = {}
    for issue in issues:
        grouped.setdefault(issue.kind, []).append(issue)

    for kind in sorted(grouped):
        print(f"\n[{kind}] {len(grouped[kind])}")
        for issue in grouped[kind]:
            location = f"{issue.file}:{issue.line}"
            print(f"- {location} target={issue.target!r} - {issue.message}")
            if issue.suggestion:
                print(f"  suggestion: {issue.suggestion}")


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Vault root. Defaults to the parent of tools/.",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Also scan raw/**/*.md imported source notes.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any issue is found.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--selftest", action="store_true", help="Run parser regression checks.")
    args = parser.parse_args(argv)

    if args.selftest:
        return demo()
    issues = audit(args.root, include_raw=args.include_raw)
    print_report(issues, as_json=args.json)
    return 1 if args.strict and issues else 0


def demo() -> int:
    valid = """---
ontology:
  concept-type: concept
  relations:
    - { type: part-of, target: kb-governance, note: "근거" }
---
"""
    assert audit_ontology(valid, "valid.md") == []
    invalid = """---
ontology:
  concept-type: concept
  relations:
    - { type: invented, target: x, note: "" }
    - { type: related-to, target: x }
---
"""
    kinds = [issue.kind for issue in audit_ontology(invalid, "invalid.md")]
    assert kinds == ["ontology-schema-drift"] * 3, kinds
    print("kb_link_health selftest OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
