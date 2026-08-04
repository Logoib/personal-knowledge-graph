---
title: "Knowledge Graph 운영 철학 — 작게 주입하고 오래 축적하기"
created: 2026-08-04
tags: [knowledge-graph, operating-philosophy, provenance, curation, context]
sources:
  - "repo:KG-SDSLab:wiki/concepts/kb-architecture-governance.md"
  - "repo:KG-SDSLab:AGENT_MEMORY_CHECKLIST.md"
ontology:
  concept-type: concept
  relations:
    - { type: part-of, target: personal-knowledge-graph, note: "개인 KG의 저장·회수·감사 원칙" }
    - { type: related-to, target: context-rot-agent-loop-design, note: "상시 주입 대신 fresh retrieval을 선호" }
---

# Knowledge Graph 운영 철학

## 1. 저장보다 선별이 어렵다

메모리는 많이 넣는다고 좋아지지 않는다. 중복, 오래된 주장, 근거 없는 요약은 회수 시 판단 비용을 키운다. 자동 수집보다 **무엇을 정본으로 승격할지 고르는 큐레이션**이 핵심이다.

## 2. 원본과 해석을 분리한다

`raw/`는 증거, `wiki/`는 현재 이해다. 해석이 바뀌어도 원본을 다시 확인할 수 있고, 위키는 새 근거에 맞춰 진화한다.

## 3. 회수는 just-in-time이다

vault를 시스템 프롬프트에 넣지 않는다. ranked lookup으로 후보를 고르고 1~3개 노트만 읽는다. 이 방식이 비용을 줄이는 동시에 [[wiki/articles/context-isolation-for-lookup|Lookup Context Isolation]]을 제공한다.

## 4. 기계는 계산 가능한 것만 고친다

도구는 파일 수, 누락 entry, 깨진 링크, 스키마를 검사한다. 한 줄 요약과 의미 관계는 사람이 검토한다. 자동화가 의미를 지어내기 시작하면 health tool이 또 하나의 저자가 된다.

## 5. 형식성은 필요한 만큼만 올린다

Markdown과 무타입 링크가 기본이다. glossary로 용어를 맞추고, 변경 영향처럼 가치가 분명한 관계만 typed frontmatter로 올린다. 자세한 경계는 [[wiki/concepts/ontology|Ontology]]에 있다.

## 6. 완료보다 신선한 근거가 우선이다

저장된 확신보다 최신 revision, 실행 결과, 사용자 확인이 우선한다. 완료는 느낌이 아니라 요구사항별 evidence의 논리곱이다.
