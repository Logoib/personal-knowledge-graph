---
title: "Loop Engineering과 HITL 경계"
created: 2026-06-29
tags: [loop-engineering, human-in-the-loop, agent, verification, tacit-knowledge]
sources:
  - "repo:KG-SDSLab:wiki/concepts/loop-engineering-hitl-boundary.md"
ontology:
  concept-type: concept
  relations:
    - { type: related-to, target: context-rot-agent-loop-design, note: "장기 agent loop의 stop·refresh 계약" }
    - { type: related-to, target: unknowns-matrix-and-knowledge-capture, note: "판단 경계와 unknown 관리가 연결" }
---

# Loop Engineering과 HITL 경계

LLM agent loop는 반복을 자동화하지만, 시스템 밖에 있는 판단 기준까지 자동화하지는 못한다. 자동화 가능 경계는 **합격 기준을 기계가 실행할 수 있는가**로 나뉜다.

| Tier | 합격 기준 | 운영 방식 |
|---|---|---|
| A | 테스트·lint·수치 gate처럼 시스템 안에 있음 | 무인 실행 가능 |
| B | 완전성은 검사되지만 정오는 사람 판단 | 제안 후 승인 |
| C | 취향·책임·외부 심사처럼 gate가 없음 | 사람이 수행 |

HITL의 앞단인 의도 추출은 인터뷰로 줄일 수 있다. 하지만 후보를 보고 생기는 수용 판단은 완전히 제거할 수 없다. 따라서 Tier B/C를 실패로 보지 말고 agent 계약에 승인·에스컬레이션 상태로 넣는다.

암묵지 외부화는 gate를 정의하는 과정에서 일어난다. 체크 가능하면 도구와 테스트로, 판단이라면 위키의 gotcha와 사람 승인 조건으로 남긴다. 장기 실행의 context와 stop 기준은 [[wiki/articles/context-rot-agent-loop-design|Context Rot 대응 Agent Loop 설계]]를 따른다.
