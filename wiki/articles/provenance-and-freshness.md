---
title: "Provenance와 Freshness — 저장된 지식을 현재 판단에 쓰는 법"
created: 2026-08-04
tags: [provenance, freshness, authority, stale, evidence]
sources:
  - "repo:KG-SDSLab:AGENTS.md"
  - "repo:KG-SDSLab:tools/agent-hub/skills/kg-lookup/SKILL.md"
ontology:
  concept-type: process
  relations:
    - { type: part-of, target: knowledge-graph-operating-philosophy, note: "저장된 주장과 live authority의 경계" }
    - { type: related-to, target: context-isolation-for-lookup, note: "조회 결과를 routing lead로 사용하는 기준" }
---

# Provenance와 Freshness

지식 노트는 과거 시점의 검증된 이해일 수 있지만 현재 상태 자체는 아니다. 안전한 재사용에는 출처와 신선도 경계가 모두 필요하다.

## Authority 순서

1. 현재 사용자 지시와 실행 중인 시스템
2. 대상 저장소의 코드, 테스트, revision, 공식 최신 문서
3. curated wiki의 해석과 결정 기록
4. raw 원본과 과거 조사

위키가 live evidence와 충돌하면 조용히 하나를 고르지 않는다. 충돌을 드러내고 최신 상태를 확인한 뒤 노트를 갱신한다.

## Source 표현

- 같은 vault 원본: vault 상대 경로
- 다른 Git repo: `repo:<name>:<repo-relative-path>`
- Git 밖 로컬 파일: `local-only:<absolute-path>`
- 웹: 원문 URL

clone 위치에 묶인 절대경로를 repo source로 쓰지 않는다.

## Freshness 신호

- note의 review date가 지남
- 대상 revision이나 파일 hash가 바뀜
- 검색 색인의 note signature가 달라짐
- 같은 개념의 두 노트가 모순됨
- 실행 결과가 저장된 절차와 다름

freshness 검사는 자동 ingest가 아니다. 변경을 감지한 뒤 사람이 의미 영향을 검토하고, 필요한 경우에만 wiki와 summary를 갱신한다.
