# Personal Knowledge Graph Index

> Last compiled: 2026-08-04

| Category | Count |
|---|---:|
| Concepts | 4 |
| Articles | 7 |
| Connections | 3 |
| Raw Sources | 0 |

## Concepts

- [Personal Knowledge Graph](concepts/personal-knowledge-graph.md) — Markdown, Git, Obsidian, Agent skill을 연결하는 개인 지식 시스템
- [Knowledge Graph 운영 철학](concepts/knowledge-graph-operating-philosophy.md) — 원본/해석 분리, just-in-time 회수, 최소 자동화 원칙
- [Ontology](concepts/ontology.md) — 자연어 위키 위에 선택적으로 더하는 의미·관계 계층
- [Loop Engineering과 HITL 경계](concepts/loop-engineering-hitl-boundary.md) — 기계 검증과 사람 판단의 자동화 경계

## Articles

- [KG 운영 자동화 도구](articles/kg-operations-tooling.md) — registry, ranked lookup, link/schema health, Git gate
- [Kiwi + BM25 Retrieval](articles/kiwi-bm25-retrieval.md) — 한국어 형태소와 SQLite FTS5를 이용한 낮은 컨텍스트 검색
- [Context Rot 대응 Agent Loop 설계](articles/context-rot-agent-loop-design.md) — fresh capsule과 evidence 기반 stop/refresh 계약
- [Lookup Context Isolation](articles/context-isolation-for-lookup.md) — top-k path 뒤 필요한 본문만 읽는 회수 규칙
- [Agent Skill Source of Truth](articles/skill-source-of-truth.md) — 세 런타임이 하나의 skill 원본을 공유하는 구조
- [Unknowns Matrix와 지식 캡처](articles/unknowns-matrix-and-knowledge-capture.md) — 암묵지와 blindspot을 재사용 지식으로 바꾸는 프레임
- [Provenance와 Freshness](articles/provenance-and-freshness.md) — 저장된 주장과 live authority의 우선순위

## Connections

- [Markdown Wiki vs Formal Ontology](connections/markdown-wiki-vs-formal-ontology.md) — 서술형 지식과 형식 그래프의 역할 경계
- [Curated Knowledge vs Runtime Memory](connections/curated-knowledge-vs-runtime-memory.md) — 장기 큐레이션, 자동 메모리, session context의 분리
- [Knowledge Capture에서 Agent Execution까지](connections/knowledge-capture-to-agent-execution.md) — 실패 기록이 lookup, skill, verifier로 이어지는 루프

## Reference

- [Personal KG Glossary](glossary.md)
- [Ontology-ready Frontmatter Schema](_ontology-schema.md)
