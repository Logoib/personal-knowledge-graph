---
title: "Agent Skill Source of Truth — 세 런타임, 하나의 원본"
created: 2026-07-12
tags: [agent-skill, codex, claude, gemini, single-source, junction]
sources:
  - "repo:KG-SDSLab:wiki/articles/sds-skills-consolidation.md"
ontology:
  concept-type: process
  relations:
    - { type: part-of, target: personal-knowledge-graph, note: "KG 조회·ingest·health 절차의 공용 원본" }
---

# Agent Skill Source of Truth

Codex, Claude, Gemini용 skill 사본을 각각 유지하면 수정 시점이 달라져 행동 계약이 분기한다. 해결책은 `tools/agent-hub/skills/` 한 곳만 원본으로 두고 각 런타임 폴더는 junction으로 연결하는 것이다.

```text
tools/agent-hub/skills/personal-kg-lookup
  <- ~/.codex/skills/personal-kg-lookup
  <- ~/.claude/skills/personal-kg-lookup
  <- ~/.gemini/antigravity/skills/personal-kg-lookup
```

원본 repo를 pull하면 세 런타임이 동시에 갱신된다. runtime 폴더를 직접 편집하지 않는다. `sync-agent-hub.ps1 -AuditOnly`는 target drift를 읽기 전용으로 확인하고, repair 모드는 충돌하는 실제 폴더를 timestamp backup한 뒤 junction을 만든다.

개인 skill은 `personal-kg-*` namespace를 사용해 업무용 `kg-*` skill과 공존한다. skill 본문에는 모델이 이미 아는 일반 설명을 넣지 않고, 경로 해석·검사 순서·안전 경계처럼 실행에 필요한 계약만 둔다.
