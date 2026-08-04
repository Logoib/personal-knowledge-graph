---
title: "Unknowns Matrix와 지식 캡처"
created: 2026-07-13
tags: [unknowns-matrix, tacit-knowledge, blindspot, knowledge-capture]
sources:
  - "repo:KG-SDSLab:wiki/articles/thariq-unknowns-matrix-kg-mapping.md"
ontology:
  concept-type: concept
  relations:
    - { type: related-to, target: knowledge-graph-operating-philosophy, note: "암묵지를 반복 가능한 지식으로 승격" }
    - { type: related-to, target: loop-engineering-hitl-boundary, note: "unknown unknown 감지에는 사람 판단이 남음" }
---

# Unknowns Matrix와 지식 캡처

프롬프트는 지도이고 실제 코드·환경·사람의 기준이 영토라면, unknown은 둘의 간극에 있다.

| 분류 | 의미 | 싼 해소 방법 |
|---|---|---|
| Known known | 이미 명시된 사실 | 검증·실행 |
| Known unknown | 모른다는 것을 아는 질문 | 인터뷰, 문서, probe |
| Unknown known | 익숙해서 쓰지 않은 암묵지 | 예시, prototype, 회고 |
| Unknown unknown | 존재를 고려하지 못한 경계 | blindspot pass, premortem |

KG의 핵심 역할은 unknown known을 known known으로 바꾸는 것이다. 한 번 발생한 실패의 조건과 우회 이유를 기록하면 다음 작업에서는 known unknown 체크리스트로 시작할 수 있다.

Unknown unknown은 KG가 직접 제거하지 못한다. 대신 “이 작업이 닿는 외부 경계를 나열하고 검증하지 않은 가정을 물어라” 같은 blindspot pass, health의 모순·고아 탐지, 사람 review로 발견 가능성을 높인다.

수정 비용이 커지기 전에 질문, 작은 prototype, executable check로 unknown을 이동시키는 것이 가장 싸다.
