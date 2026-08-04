---
title: "Personal KG Glossary"
created: 2026-08-04
tags: [glossary, terminology, ontology]
sources:
  - "repo:KG-SDSLab:wiki/glossary.md"
---

# Personal KG Glossary

| Term | Definition | Description |
|---|---|---|
| Raw | 수정하지 않는 원본 보존층 | 웹 자료, 논문, 내보낸 대화 등 provenance의 출발점 |
| Wiki | 원본에서 컴파일한 큐레이션 지식층 | 개념, 판단, 비교, 실패 교훈의 현재 정본 |
| Registry | 위키 검색·탐색을 위한 사람이 검토한 목록 | `_index.md`, `_summaries.md`, `_backlinks.md` |
| Ranked lookup | query에 맞는 note 후보를 점수순으로 찾는 과정 | path와 snippet만 먼저 반환해 context를 절약 |
| BM25 | lexical term relevance 기반 랭킹 함수 | SQLite FTS5가 구현하며 작은 로컬 corpus에 적합 |
| Kiwi | 한국어 형태소 분석기 | 조사·어미 변형을 token으로 정규화 |
| Context rot | context가 길고 혼잡해지며 작업 신뢰성이 떨어지는 현상 | 단순 token 한도보다 정보 위치·distractor·단계 누적의 영향이 큼 |
| Context isolation | corpus와 작업 context를 분리하는 회수 규칙 | top-k path를 고른 뒤 필요한 1~3개 본문만 읽음 |
| Provenance | 주장이나 노트가 어디서 왔는지 추적하는 정보 | URL, vault path, `repo:name:path`, revision |
| Freshness | 저장된 주장이 현재 authority와 여전히 맞는 정도 | 날짜뿐 아니라 revision, hash, live execution으로 판단 |
| Ontology | 개념과 타입드 관계의 의미 계층 | 개인 KG에서는 선택적 frontmatter로만 적용 |
| HITL | Human in the Loop | 기계가 합격 기준을 판정할 수 없는 단계의 사람 승인 |
| Skill source of truth | 여러 runtime이 공유하는 단일 skill 원본 | runtime별 사본 대신 junction을 사용 |
