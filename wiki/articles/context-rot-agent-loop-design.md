---
title: "Context Rot 대응 Agent Loop 설계"
created: 2026-07-21
tags: [context-rot, long-context, agent-loop, checkpoint, stop-criteria]
sources:
  - "repo:KG-SDSLab:wiki/articles/context-rot-agent-loop-design.md"
ontology:
  concept-type: process
  relations:
    - { type: related-to, target: loop-engineering-hitl-boundary, note: "사람 승인과 기계 검증의 stop 경계" }
    - { type: related-to, target: context-isolation-for-lookup, note: "fresh context에 필요한 지식만 회수" }
---

# Context Rot 대응 Agent Loop 설계

긴 context는 용량 한도에 닿기 전에도 정보 위치, distractor, 대화 이력, 과제 복잡도 때문에 신뢰성이 불균일하게 떨어진다. 따라서 고정 token 절단보다 evidence 기반 refresh가 필요하다.

## 세 길이

- `W_claimed`: 입력 가능한 광고상 최대 길이
- `W_effective`: 대표 과제에서 품질 하한을 지키는 길이
- `W_working`: 안전 여유를 둔 일상 목표 길이

needle retrieval만으로 유효 길이를 판단하지 않는다. contract recall, evidence 사용, 금지 행동, patch/test 성공, unsupported claim, latency를 함께 본다.

## Fresh context capsule

전체 transcript 대신 다음만 넘긴다.

- objective와 현재 slice
- acceptance와 verifier
- provenance가 있는 verified facts
- frozen decisions와 decision-changing unknowns
- scoped paths와 authority
- decisive evidence, 실패한 접근, 정확히 하나의 next action

## Refresh 신호

- discovery에서 implementation처럼 단계가 바뀜
- 같은 탐색이나 verifier 실패가 반복됨
- 저장된 fact와 live evidence가 충돌함
- revision/hash가 stale함
- compaction 또는 대량 tool output으로 핵심 계약이 흐려짐
- acceptance, authority, next action을 잃음

완료는 자신감이 아니라 acceptance별 최신 evidence의 논리곱이다. 안전, 성공, 결정 불가능한 불확실성, 예산, refresh, recovery 순서로 상태를 평가한다. 사람 판단이 필요한 위치는 [[wiki/concepts/loop-engineering-hitl-boundary|Loop Engineering과 HITL 경계]]를 따른다.
