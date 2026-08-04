---
title: "Knowledge Capture에서 Agent Execution까지"
created: 2026-08-04
tags: [knowledge-capture, agent-execution, skill, verification]
sources:
  - "repo:KG-SDSLab:wiki/concepts/loop-engineering-hitl-boundary.md"
  - "repo:KG-SDSLab:wiki/articles/thariq-unknowns-matrix-kg-mapping.md"
ontology:
  concept-type: process
  relations:
    - { type: depends-on, target: unknowns-matrix-and-knowledge-capture, note: "실패·암묵지를 재사용 가능한 지식으로 변환" }
    - { type: depends-on, target: skill-source-of-truth, note: "반복 절차를 runtime skill로 전달" }
---

# Knowledge Capture에서 Agent Execution까지

지식이 쌓였다는 사실만으로 agent 행동이 좋아지지는 않는다. 정제된 지식이 검색되고, 반복 절차가 skill 계약으로 변환되며, 결과가 verifier를 통과해야 한다.

```text
failure / insight
  -> raw evidence
  -> curated concept or gotcha
  -> ranked lookup
  -> repeatable workflow in skill
  -> deterministic check or human gate
  -> new reusable lesson
```

모든 노트를 skill로 만들지 않는다. 설명과 판단 근거는 wiki에 남기고, 여러 번 반복되는 실행 순서와 안전 경계만 skill로 승격한다. 체크 가능한 부분은 도구로, 판단이 필요한 부분은 [[wiki/concepts/loop-engineering-hitl-boundary|HITL Tier B/C]]로 남긴다.

이 루프가 닫히면 KG는 단순 archive가 아니라 실패 비용을 다음 작업에서 줄이는 운영 시스템이 된다.
