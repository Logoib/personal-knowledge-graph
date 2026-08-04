#!/usr/bin/env python3
"""한국어 검색 색인 (Kiwi 형태소 + SQLite FTS5/BM25).

DB화가 아니다. 원본 마크다운은 불변이고, 이 색인은 **커밋하지 않는** 산출물
(`tools/.cache/kb_fts.sqlite`)로 각 머신에서 재생성한다. `kb_lookup.py`가 이 모듈의
`search()`를 호출해 substring 대신 BM25 랭킹을 쓴다.

Kiwi 미설치 환경에서는 build가 친절한 메시지로 실패하고, `search()`는 None을 돌려
호출측(kb_lookup)이 기존 substring 경로로 degrade한다 — 하드 실패 없음.

standalone: `py -3 tools/kb_index_build.py [--include-raw]`  → 색인 재생성.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_paths import resolve_kb_root

INDEX_REL = Path("tools") / ".cache" / "kb_fts.sqlite"

# 검색 토큰으로 쓸 형태소 태그: 명사류·외래어(SL)·한자(SH)·숫자(SN)·용언어근(VV/VA)·어근(XR)
KEEP_TAG_PREFIXES = ("N", "SL", "SH", "SN", "VV", "VA", "XR")
FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)
TAGS_BLOCK_RE = re.compile(r"^tags:\s*\n((?:\s*-\s*.+\n)+)", re.MULTILINE)

_kiwi = None


def kiwi():
    """Kiwi 싱글턴. 미설치면 ImportError 전파."""
    global _kiwi
    if _kiwi is None:
        from kiwipiepy import Kiwi  # noqa: import 지연 — 미설치 폴백을 위해
        _kiwi = Kiwi()
    return _kiwi


def kiwi_available() -> bool:
    try:
        import kiwipiepy  # noqa: F401
        return True
    except Exception:
        return False


def tokenize(text: str) -> str:
    """텍스트를 검색 토큰(공백 구분 문자열)으로. Kiwi 형태소 → 태그 필터 → 소문자."""
    if not text.strip():
        return ""
    out = []
    for tok in kiwi().tokenize(text):
        if tok.tag.startswith(KEEP_TAG_PREFIXES):
            form = tok.form.strip().lower()
            if form:
                out.append(form)
    return " ".join(out)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def strip_quotes(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def parse_note(path: Path):
    """(title, tags_text, body) 반환."""
    text = read_text(path)
    fm = ""
    m = FRONTMATTER_RE.match(text)
    body = text
    title = path.stem
    tags_text = ""
    if m:
        fm = m.group(0)
        body = text[m.end():]
        tm = TITLE_RE.search(fm)
        if tm:
            title = strip_quotes(tm.group(1))
        gm = TAGS_BLOCK_RE.search(fm)
        if gm:
            tags_text = " ".join(
                line.strip().lstrip("-").strip() for line in gm.group(1).splitlines()
            )
    return title, tags_text, body


def iter_notes(root: Path):
    """(path, source) 산출. source ∈ {'wiki','raw'}. 항상 둘 다 색인하고
    검색 시 source로 필터(기본 wiki-only, --include-raw 로 raw 노출)."""
    wiki = root / "wiki"
    for path in sorted(wiki.rglob("*.md")):
        # 레지스트리·스키마 메타파일(_ 접두)은 색인 제외 — 노트 본문만
        if path.name.startswith("_"):
            continue
        yield path, "wiki"
    raw = root / "raw"
    if raw.exists():
        for path in sorted(raw.rglob("*.md")):
            yield path, "raw"


def excerpt_of(body: str, n: int = 200) -> str:
    flat = re.sub(r"\s+", " ", re.sub(r"^#.*$", "", body, flags=re.MULTILINE)).strip()
    return flat[:n]


def _signature(root: Path) -> str:
    """색인 대상 노트 집합의 지문: 파일수 + 최대 mtime(ns).
    노트가 추가/삭제/수정되면 값이 바뀐다 → search()가 stale 색인을 감지해 폴백."""
    count = 0
    max_mtime = 0
    for path, _source in iter_notes(root):
        count += 1
        try:
            m = path.stat().st_mtime_ns
        except OSError:
            continue
        if m > max_mtime:
            max_mtime = m
    return f"{count}:{max_mtime}"


def build_index(root: Path) -> int:
    index_path = root / INDEX_REL
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if index_path.exists():
        index_path.unlink()
    con = sqlite3.connect(str(index_path))
    con.execute(
        "CREATE VIRTUAL TABLE notes USING fts5("
        " relpath UNINDEXED, title UNINDEXED, excerpt UNINDEXED, source UNINDEXED, content,"
        " tokenize='unicode61')"
    )
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    count = 0
    for path, source in iter_notes(root):
        title, tags_text, body = parse_note(path)
        title_tok = tokenize(title)
        # 제목 토큰을 3배 반복해 가중(별도 bm25 컬럼 가중 대신 단순 반복)
        content = " ".join([title_tok, title_tok, title_tok, tokenize(tags_text), tokenize(body)])
        con.execute(
            "INSERT INTO notes (relpath, title, excerpt, source, content) VALUES (?,?,?,?,?)",
            (path.relative_to(root).as_posix(), title, excerpt_of(body), source, content),
        )
        count += 1
    # 빌드 시점의 노트 집합 지문을 저장 — 검색 때 현재와 비교해 신선도 검증.
    con.execute("INSERT INTO meta (key, value) VALUES ('signature', ?)", (_signature(root),))
    con.commit()
    con.close()
    return count


def _index_path(root: Path) -> Path:
    return root / INDEX_REL


def _run_match(con: sqlite3.Connection, match_expr: str, limit: int, include_raw: bool):
    """MATCH SELECT 한 곳. 기본은 wiki-only, include_raw면 raw까지."""
    sql = "SELECT relpath, title, excerpt, bm25(notes) AS s FROM notes WHERE notes MATCH ?"
    params: list = [match_expr]
    if not include_raw:
        sql += " AND source = 'wiki'"
    sql += " ORDER BY s LIMIT ?"
    params.append(limit)
    return con.execute(sql, params).fetchall()


def search(query: str, limit: int, root: Path | None = None, include_raw: bool = False):
    """BM25 검색. 색인/Kiwi 없으면 None(호출측이 substring 폴백).
    기본 wiki-only; include_raw=True면 raw/ 원본도 결과에 포함."""
    root = (root or resolve_kb_root()).resolve()
    index_path = _index_path(root)
    if not index_path.exists() or not kiwi_available():
        return None
    q_tokens = [t for t in tokenize(query).split() if t]
    if not q_tokens:
        return None
    # 각 토큰 OR — recall 우선, BM25가 랭킹. 토큰은 큰따옴표로 감싸 FTS5 연산자화 방지.
    match_expr = " OR ".join(f'"{t}"' for t in dict.fromkeys(q_tokens))
    con = sqlite3.connect(str(index_path))
    try:
        cur = con.execute("SELECT value FROM meta WHERE key='signature'")
        row = cur.fetchone()
        if (row[0] if row else None) != _signature(root):
            # 색인이 현재 노트 집합보다 오래됨(stale) → 그럴듯한 낡은 결과 대신 폴백.
            print("kb_lookup: 색인 stale — substring 폴백. 재빌드: py -3 tools/kb_index_build.py",
                  file=sys.stderr)
            return None
        rows = _run_match(con, match_expr, limit, include_raw)
    except sqlite3.OperationalError:
        return None
    finally:
        con.close()
    hits = []
    for relpath, title, excerpt, s in rows:
        # kb_lookup 렌더 호환: {path, snippet, score}. bm25는 작을수록 좋음 → 부호 반전.
        hits.append({"path": relpath, "snippet": title or relpath, "score": -float(s), "excerpt": excerpt})
    return hits


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--include-raw", action="store_true",
                        help="(호환용, 무시됨) 색인은 항상 wiki+raw 둘 다 포함. "
                             "raw 노출은 검색 시 kb_lookup --include-raw 로.")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return demo()

    if not kiwi_available():
        print("kiwipiepy 미설치 — 색인을 만들 수 없습니다. 설치: py -3 -m pip install kiwipiepy")
        print("(kb_lookup 은 색인 없이 substring 경로로 계속 동작합니다.)")
        return 1

    root = (args.root or resolve_kb_root()).resolve()
    n = build_index(root)
    print(f"indexed {n} notes → {(_index_path(root)).relative_to(root).as_posix()}")
    return 0


def demo() -> int:
    """자체 검사: (1) 프론트매터 파싱·발췌, (2) source 필터(wiki-우선/raw-opt-in) 회귀."""
    title, tags, body = parse_note_from_text(
        "---\ntitle: \"가스 분산 안전성\"\ntags:\n  - safety\n  - gas\n---\n# 헤더\n본문 내용입니다.\n"
    )
    assert title == "가스 분산 안전성", title
    assert "safety" in tags and "gas" in tags, tags
    assert body.strip().startswith("# 헤더"), body
    assert excerpt_of(body).startswith("본문 내용"), excerpt_of(body)

    # source 필터: 같은 토큰을 가진 wiki/raw 노트를 넣고, 기본은 wiki만·include_raw는 둘 다.
    # Kiwi 없이 결정적으로 검증하려고 in-memory FTS 인덱스를 직접 만든다.
    con = sqlite3.connect(":memory:")
    con.execute(
        "CREATE VIRTUAL TABLE notes USING fts5("
        " relpath UNINDEXED, title UNINDEXED, excerpt UNINDEXED, source UNINDEXED, content,"
        " tokenize='unicode61')"
    )
    con.executemany(
        "INSERT INTO notes (relpath, title, excerpt, source, content) VALUES (?,?,?,?,?)",
        [
            ("wiki/articles/w.md", "wiki drm note", "", "wiki", "drm drm"),
            ("raw/articles/r.md", "raw drm note", "", "raw", "drm drm"),
        ],
    )
    wiki_only = _run_match(con, '"drm"', 10, include_raw=False)
    both = _run_match(con, '"drm"', 10, include_raw=True)
    con.close()
    assert [r[0] for r in wiki_only] == ["wiki/articles/w.md"], wiki_only
    assert {r[0] for r in both} == {"wiki/articles/w.md", "raw/articles/r.md"}, both

    # staleness: 노트가 바뀌면 signature가 바뀌어 색인 재빌드가 트리거된다.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        (r / "wiki").mkdir()
        (r / "wiki" / "a.md").write_text("---\ntitle: x\n---\nbody", encoding="utf-8")
        s1 = _signature(r)
        (r / "wiki" / "b.md").write_text("---\ntitle: y\n---\nbody", encoding="utf-8")
        assert s1 != _signature(r), "노트 추가 후 signature가 그대로 — stale 감지 실패"

    print("selftest OK")
    return 0


def parse_note_from_text(text: str):
    """demo 용 — parse_note 의 문자열 버전."""
    m = FRONTMATTER_RE.match(text)
    title, tags_text, body = "untitled", "", text
    if m:
        fm = m.group(0)
        body = text[m.end():]
        tm = TITLE_RE.search(fm)
        if tm:
            title = strip_quotes(tm.group(1))
        gm = TAGS_BLOCK_RE.search(fm)
        if gm:
            tags_text = " ".join(l.strip().lstrip("-").strip() for l in gm.group(1).splitlines())
    return title, tags_text, body


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
