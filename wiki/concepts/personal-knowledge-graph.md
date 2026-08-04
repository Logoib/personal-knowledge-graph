---
title: "Personal Knowledge Graph — Markdown, Git, Agent Skills"
created: 2026-08-04
tags: [personal-kg, obsidian, markdown, git, agent-memory]
sources:
  - "repo:KG-SDSLab:README.md"
  - "repo:KG-SDSLab:wiki/concepts/kb-architecture-governance.md"
ontology:
  concept-type: system
  relations:
    - { type: depends-on, target: knowledge-graph-operating-philosophy, note: "운영 원칙이 저장·검색·갱신 방식을 결정" }
    - { type: related-to, target: ontology, note: "선택적 타입드 관계만 채택" }
---

# Personal Knowledge Graph

개인 자료와 고찰을 Markdown으로 장기 보존하고, 사람이 Obsidian으로 읽으며, AI agent가 필요한 순간에만 검색하는 시스템이다. 목표는 대화 전체를 기억시키는 것이 아니라 **재사용 가치가 있는 지식의 정본을 작고 검증 가능하게 유지하는 것**이다.

## 세 층

1. `raw/`: 웹 자료, 논문, 대화 내보내기 같은 원본. 추가는 하되 기존 원본은 고치지 않는다.
2. `wiki/`: 원본에서 컴파일한 개념, 판단, 비교, 실패 교훈. 사람이 읽고 고칠 수 있는 정본이다.
3. 규칙·도구: frontmatter, registry, link health, lookup skill이 저장과 회수 계약을 지킨다.

검색 색인은 네 번째 정본이 아니라 다시 만들 수 있는 계산 산출물이다. 자세한 운영 도구는 [[wiki/articles/kg-operations-tooling|KG 운영 자동화 도구]]를 본다.

## 지식의 순환

```text
source -> raw -> curated wiki -> ranked lookup -> task decision -> reusable lesson -> wiki
```

각 단계에서 provenance를 잃지 않고, 현재 실행 상태와 충돌하면 live evidence를 우선한다. 이 경계는 [[wiki/articles/provenance-and-freshness|Provenance와 Freshness]]에 정리한다.

## 하지 않는 것

- 모든 대화와 파일의 자동 수집
- 자연어 위키 전체의 DB·RDF 재구축
- 거대한 시스템 프롬프트로 vault 상시 주입
- 검색 색인을 source of truth로 취급

이 선택은 [[wiki/concepts/knowledge-graph-operating-philosophy|Knowledge Graph 운영 철학]]의 저마찰·검증 가능성 원칙을 따른다.
