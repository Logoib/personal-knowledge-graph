---
title: "Kiwi + BM25 Retrieval — 한국어 KG의 낮은 컨텍스트 검색"
created: 2026-08-04
tags: [kiwi, bm25, sqlite, fts5, retrieval, korean]
sources:
  - "repo:KG-SDSLab:tools/kb_index_build.py"
  - "repo:KG-SDSLab:tools/kb_lookup.py"
ontology:
  concept-type: tool
  relations:
    - { type: part-of, target: personal-knowledge-graph, note: "필요한 노트만 읽게 하는 검색 계층" }
    - { type: related-to, target: context-isolation-for-lookup, note: "ranked top-k가 컨텍스트 격리의 1차 장치" }
---

# Kiwi + BM25 Retrieval

한국어는 조사와 어미 때문에 단순 substring 검색의 recall이 쉽게 떨어진다. Kiwi로 형태소를 토큰화하고 SQLite FTS5의 BM25로 문서를 정렬하면 작은 로컬 KG에 충분한 검색 품질을 얻을 수 있다.

## 구조

```text
wiki/raw Markdown -> Kiwi tokenization -> SQLite FTS5 -> BM25 top-k -> note open
```

- 색인 파일은 `tools/.cache/kb_fts.sqlite`이며 Git에 넣지 않는다.
- 기본 검색은 curated `wiki/`만 노출한다.
- provenance가 필요할 때만 `--include-raw`로 원본을 포함한다.
- note 집합이 바뀌어 signature가 달라지면 낡은 결과를 내지 않고 substring으로 폴백한다.

## 왜 embedding부터 시작하지 않는가

작은 Markdown vault에서는 로컬 lexical rank가 싸고 투명하며 citation path를 바로 준다. embedding은 paraphrase recall이 실제 병목이고 corpus가 충분히 커졌을 때 추가한다. 그 전에는 새 DB·모델·chunk 정책이 운영 부담만 만든다.

## Context 관점

검색 품질보다 중요한 계약은 corpus 전체를 agent context에 넣지 않는 것이다. 검색 결과는 경로와 짧은 snippet만 반환하고, 실제 본문은 필요한 1~3개만 연다. 자세한 방어선은 [[wiki/articles/context-isolation-for-lookup|Lookup Context Isolation]]에 있다.
