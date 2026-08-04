---
title: "KG 운영 자동화 도구 — Registry, Lookup, Health"
created: 2026-07-06
tags: [knowledge-graph, tooling, registry, lookup, health]
sources:
  - "repo:KG-SDSLab:wiki/articles/kg-operations-tooling.md"
ontology:
  concept-type: tool
  relations:
    - { type: part-of, target: personal-knowledge-graph, note: "개인 KG의 결정론적 운영 도구" }
    - { type: related-to, target: kiwi-bm25-retrieval, note: "한국어 ranked lookup 구현" }
---

# KG 운영 자동화 도구

원본 Markdown은 정본으로 유지하고, 그 위에 다시 만들 수 있는 registry·검색 색인·검사를 얹는다.

## Registry compiler

`tools/kb_compile_registry.py`는 `_index.md`, `_summaries.md`, `_backlinks.md`를 통째로 생성하지 않는다. 파일 수와 날짜처럼 기계가 안전하게 계산할 수 있는 값만 갱신하고, 누락·삭제 entry를 보고한다. 사람이 쓴 요약과 관계 설명은 보존한다.

## Ranked lookup

`tools/kb_index_build.py`는 Kiwi 형태소 분석 결과를 SQLite FTS5에 넣고 BM25로 정렬한다. `tools/kb_lookup.py`는 색인이나 Kiwi가 없으면 substring으로 자동 폴백한다. 설계 이유는 [[wiki/articles/kiwi-bm25-retrieval|Kiwi BM25 Retrieval]]에 있다.

## Link and schema health

`tools/kb_link_health.py --strict`는 빈 노트, 깨진 위키링크와 Markdown 링크, 허용되지 않은 ontology frontmatter를 막는다. `tools/kb_health.py`는 registry, link/schema, tri-file 규칙을 한 번에 검사한다.

## Git gate

pre-commit hook은 다음을 commit 전에 강제한다.

- registry가 현재 파일 집합과 맞음
- wiki 본문 변경 시 `_summaries.md`도 함께 staged됨
- link·ontology health 통과
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 동일

이 자동화는 의미를 생성하지 않는다. 의미 결정은 위키 저자에게 남겨 둔다.
