---
title: "Curated Knowledge vs Runtime Memory"
created: 2026-08-04
tags: [agent-memory, curated-knowledge, runtime-memory, comparison]
sources:
  - "repo:KG-SDSLab:wiki/articles/agent-memory-buy-vs-build.md"
ontology:
  concept-type: artifact
  relations:
    - { type: related-to, target: personal-knowledge-graph, note: "장기 큐레이션 메모리 계층" }
    - { type: related-to, target: context-isolation-for-lookup, note: "회수 시 필요한 사실만 context에 적재" }
---

# Curated Knowledge vs Runtime Memory

“Agent memory”는 하나의 기능이 아니다.

| 계층 | 목적 | 장점 | 위험 |
|---|---|---|---|
| Curated KG | 장기 지식, 결정, provenance | 검토 가능, Git history, 높은 신뢰 | 기록 마찰 |
| Runtime memory | 대화 중 사실·선호 자동 회수 | 저마찰, 빠른 개인화 | 오염, stale fact, 출처 약함 |
| Session context | 현재 작업 상태 | 즉시성 | context rot, 세션 종료 시 소실 |

개인 KG는 curated layer다. runtime memory를 나중에 더하더라도 자동 추출 결과를 곧바로 wiki 정본으로 승격하지 않는다. 반복 확인된 사실이나 장기 선호만 provenance와 함께 ingest한다.

저장 계층을 분리하면 session context를 작게 유지하면서도 장기 지식을 잃지 않는다. 회수는 [[wiki/articles/context-isolation-for-lookup|Lookup Context Isolation]]을 따르고, 실행 상태는 current task artifact가 소유한다.
