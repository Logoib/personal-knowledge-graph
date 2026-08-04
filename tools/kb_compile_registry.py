#!/usr/bin/env python3
"""레지스트리 신선도 유지 + 드리프트 검출 (계산형 뷰).

`_index.md`·`_summaries.md`·`_backlinks.md`는 **손으로 큐레이션한** 한 줄 요약,
Recent Changes changelog, backlink 관계 주석을 담고 있다. 따라서 frontmatter에서
통째로 재생성하면 그 큐레이션을 파괴한다. 이 도구는 그렇게 하지 않는다.

대신 **기계로 안전하게 정할 수 있는 것만** 다룬다:
- 자동 갱신(--write): `_index.md` 개요 통계표의 Concepts/Articles/Connections 수,
  `_index.md`의 "Last compiled" 날짜, `_backlinks.md`의 "Last updated" 날짜.
  (Raw Sources 수는 큐레이션된 값이라 건드리지 않는다 — 파일 수 ≠ 소스 세트 수.)
- 드리프트 검출(--check): 통계 불일치(hard), 레지스트리 항목이 삭제된 파일을 가리킴
  (hard, dangling), 디스크에 있으나 레지스트리에 없는 노트(warn, 사람이 요약 작성 필요).

exit code: --check에서 hard 이슈가 있으면 1, 아니면 0. --write는 항상 0(쓰기 성공 시).

ponytail: 요약은 사람이 쓴다. 이 도구는 요약을 지어내지 않는다 — 통계만 맞추고
빠진 곳을 지목한다.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_paths import resolve_kb_root

# _index.md / _summaries.md 어디서든 [concepts/foo.md] 또는 [Title](articles/foo.md) 형태의
# vault 상대 .md 경로를 뽑는다.
MD_PATH_RE = re.compile(r"\((?:\.\./)*((?:concepts|articles|connections|glossary[^)]*)[^)]*?\.md)\)")
SUMMARY_PATH_RE = re.compile(r"\[((?:concepts|articles|connections)/[^\]]+?\.md)\]")
STAT_ROW_RE = re.compile(r"^(\|\s*(Concepts|Articles|Connections|Raw Sources)\s*\|\s*)(\d+)(\s*\|)\s*$")
LAST_COMPILED_RE = re.compile(r"^(>\s*Last compiled:\s*)(.+?)\s*$")
LAST_UPDATED_RE = re.compile(r"^(>\s*Last updated:\s*)(.+?)\s*$")

CATEGORIES = ("concepts", "articles", "connections")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def count_notes(wiki: Path) -> dict[str, int]:
    """디렉토리별 실제 .md 노트 수 (기계적 진실)."""
    return {cat: len(sorted((wiki / cat).glob("*.md"))) for cat in CATEGORIES}


def note_stems(wiki: Path, cat: str) -> set[str]:
    return {p.stem for p in (wiki / cat).glob("*.md")}


def registered_paths(text: str, pattern: re.Pattern) -> set[str]:
    """레지스트리 텍스트에서 참조된 vault 상대 .md 경로 집합."""
    out: set[str] = set()
    for m in pattern.finditer(text):
        rel = m.group(1).replace("\\", "/")
        # glossary-todo.md 등 reference 파일은 카테고리 밖 — 멤버십 검사 대상 아님
        out.add(rel)
    return out


def registry_shape_issues(name: str, text: str, pattern: re.Pattern) -> list["Issue"]:
    """한 줄 다중 항목과 중복 경로를 거부한다."""
    issues: list[Issue] = []
    seen: dict[str, int] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        paths = [m.group(1).replace("\\", "/") for m in pattern.finditer(line)]
        if len(paths) > 1:
            issues.append(Issue(
                "error", "multi-entry-line",
                f"{name}:{line_no} 한 줄에 레지스트리 항목 {len(paths)}개가 붙어 있음: {paths}",
            ))
        for path in paths:
            if path in seen:
                issues.append(Issue(
                    "error", "duplicate-entry",
                    f"{name}:{line_no} 의 [{path}]가 {seen[path]}행과 중복.",
                ))
            else:
                seen[path] = line_no
    return issues


def stat_table_values(index_text: str) -> dict[str, int]:
    vals: dict[str, int] = {}
    for line in index_text.splitlines():
        m = STAT_ROW_RE.match(line)
        if m:
            vals[m.group(2)] = int(m.group(3))
    return vals


def rewrite_stats(index_text: str, counts: dict[str, int], today: str) -> str:
    """개요 통계표의 Concepts/Articles/Connections + Last compiled 를 in-place 갱신.
    Raw Sources 는 손대지 않는다."""
    label_to_count = {
        "Concepts": counts["concepts"],
        "Articles": counts["articles"],
        "Connections": counts["connections"],
    }
    out = []
    for line in index_text.splitlines():
        m = STAT_ROW_RE.match(line)
        if m and m.group(2) in label_to_count:
            line = f"{m.group(1)}{label_to_count[m.group(2)]}{m.group(4)}"
        else:
            mc = LAST_COMPILED_RE.match(line)
            if mc:
                line = f"{mc.group(1)}{today}"
        out.append(line)
    return "\n".join(out) + ("\n" if index_text.endswith("\n") else "")


def rewrite_last_updated(text: str, today: str) -> str:
    out = []
    for line in text.splitlines():
        m = LAST_UPDATED_RE.match(line)
        if m:
            line = f"{m.group(1)}{today}"
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


class Issue:
    def __init__(self, level: str, kind: str, message: str):
        self.level = level  # "error" | "warn"
        self.kind = kind
        self.message = message


def audit(root: Path) -> list[Issue]:
    wiki = root / "wiki"
    index_text = read_text(wiki / "_index.md")
    summaries_text = read_text(wiki / "_summaries.md")

    counts = count_notes(wiki)
    issues: list[Issue] = []
    issues.extend(registry_shape_issues("_index.md", index_text, MD_PATH_RE))
    issues.extend(registry_shape_issues("_summaries.md", summaries_text, SUMMARY_PATH_RE))

    # 1) 통계표 불일치 (hard)
    table = stat_table_values(index_text)
    for label, cat in (("Concepts", "concepts"), ("Articles", "articles"), ("Connections", "connections")):
        if table.get(label) != counts[cat]:
            issues.append(Issue(
                "error", "stat-drift",
                f"_index.md 개요 {label}={table.get(label)} 이나 실제 {counts[cat]}개. --write 로 갱신.",
            ))

    # 2) 멤버십: 디스크 노트 ↔ 레지스트리 항목
    disk = {cat: note_stems(wiki, cat) for cat in CATEGORIES}
    for name, text, pat in (
        ("_index.md", index_text, MD_PATH_RE),
        ("_summaries.md", summaries_text, SUMMARY_PATH_RE),
    ):
        reg = registered_paths(text, pat)
        reg_by_cat: dict[str, set[str]] = {cat: set() for cat in CATEGORIES}
        for rel in reg:
            cat = rel.split("/", 1)[0]
            if cat in reg_by_cat:
                reg_by_cat[cat].add(Path(rel).stem)
        for cat in CATEGORIES:
            # dangling: 레지스트리 항목이 존재하지 않는 파일을 가리킴 (hard)
            for stem in sorted(reg_by_cat[cat] - disk[cat]):
                issues.append(Issue(
                    "error", "dangling-entry",
                    f"{name} 의 [{cat}/{stem}.md] 항목이 존재하지 않는 파일을 가리킴.",
                ))
            # missing: 디스크에 있으나 레지스트리에 없음 (warn — 사람이 요약 작성 필요)
            for stem in sorted(disk[cat] - reg_by_cat[cat]):
                issues.append(Issue(
                    "warn", "missing-entry",
                    f"{cat}/{stem}.md 가 {name} 에 없음 — 한 줄 요약을 손으로 추가하세요.",
                ))

    return issues


def do_write(root: Path, today: str) -> list[str]:
    wiki = root / "wiki"
    changed: list[str] = []
    counts = count_notes(wiki)

    index_path = wiki / "_index.md"
    index_text = read_text(index_path)
    new_index = rewrite_stats(index_text, counts, today)
    if new_index != index_text:
        index_path.write_text(new_index, encoding="utf-8")
        changed.append("wiki/_index.md")

    backlinks_path = wiki / "_backlinks.md"
    bl_text = read_text(backlinks_path)
    new_bl = rewrite_last_updated(bl_text, today)
    if new_bl != bl_text:
        backlinks_path.write_text(new_bl, encoding="utf-8")
        changed.append("wiki/_backlinks.md")

    return changed


def print_issues(issues: list[Issue]) -> None:
    if not issues:
        print("KG registry: OK (통계·멤버십 일치)")
        return
    errors = [i for i in issues if i.level == "error"]
    warns = [i for i in issues if i.level == "warn"]
    print(f"KG registry: {len(errors)} error / {len(warns)} warn")
    for i in issues:
        tag = "ERR " if i.level == "error" else "warn"
        print(f"  [{tag}] {i.kind}: {i.message}")


def resolve_today(arg: str | None) -> str:
    if arg:
        return arg
    # datetime.now() 는 CLAUDE.md 규칙과 무관; 로컬 날짜 사용. 테스트는 --date 로 주입.
    return datetime.now(timezone.utc).astimezone().date().isoformat()


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="Vault root. 기본은 자동 해석.")
    parser.add_argument("--check", action="store_true", help="드리프트 검출만; hard 이슈 시 exit 1.")
    parser.add_argument("--write", action="store_true", help="통계·날짜 in-place 갱신.")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (테스트 재현용).")
    parser.add_argument("--selftest", action="store_true", help="내장 자체 검사 실행.")
    args = parser.parse_args(argv)

    if args.selftest:
        return demo()

    root = args.root or resolve_kb_root()
    root = root.resolve()
    today = resolve_today(args.date)

    if args.write:
        changed = do_write(root, today)
        if changed:
            print("갱신:", ", ".join(changed))
        else:
            print("변경 없음 (이미 최신)")

    issues = audit(root)
    print_issues(issues)

    if args.check:
        return 1 if any(i.level == "error" for i in issues) else 0
    return 0


def demo() -> int:
    """자체 검사: 파서·통계 재작성 로직이 깨지면 실패한다."""
    # 통계표 파싱
    idx = "\n".join([
        "> Last compiled: 2026-01-01",
        "| 항목 | 수량 |",
        "|------|------|",
        "| Concepts | 5 |",
        "| Articles | 9 |",
        "| Connections | 1 |",
        "| Raw Sources | 62 |",
    ])
    vals = stat_table_values(idx)
    assert vals == {"Concepts": 5, "Articles": 9, "Connections": 1, "Raw Sources": 62}, vals

    # 재작성: Concepts/Articles/Connections 만 바뀌고 Raw Sources·기타 보존
    new = rewrite_stats(idx, {"concepts": 20, "articles": 53, "connections": 1}, "2026-07-06")
    assert "| Concepts | 20 |" in new, new
    assert "| Articles | 53 |" in new, new
    assert "| Raw Sources | 62 |" in new, "Raw Sources must be preserved"
    assert "Last compiled: 2026-07-06" in new, new

    # 레지스트리 모양: 줄바꿈 누락과 중복을 hard error로 잡는다.
    joined = "- [concepts/a.md] — x (#t)- [concepts/b.md] — y (#t)"
    shape = registry_shape_issues("_summaries.md", joined, SUMMARY_PATH_RE)
    assert [issue.kind for issue in shape] == ["multi-entry-line"], shape
    dup = registry_shape_issues(
        "_summaries.md",
        "- [concepts/a.md] — x\n- [concepts/a.md] — y",
        SUMMARY_PATH_RE,
    )
    assert [issue.kind for issue in dup] == ["duplicate-entry"], dup

    # _index 형태 링크 추출
    idxline = "- [Title](concepts/a.md) — summary\n- [T2](../articles/b.md) — s2"
    got2 = registered_paths(idxline, MD_PATH_RE)
    assert "concepts/a.md" in got2 and "articles/b.md" in got2, got2

    print("selftest OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
