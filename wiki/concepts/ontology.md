---
title: "Ontology — 자연어 위키 위의 선택적 의미 계층"
created: 2026-06-09
tags: [ontology, semantic-layer, taxonomy, knowledge-modeling]
sources:
  - "repo:KG-SDSLab:wiki/concepts/ontology.md"
  - "repo:KG-SDSLab:wiki/articles/ontology-essence-webinar.md"
ontology:
  concept-type: concept
  relations:
    - { type: part-of, target: personal-knowledge-graph, note: "선택적 의미·관계 계층" }
    - { type: related-to, target: knowledge-graph-operating-philosophy, note: "형식성 비용을 가치에 맞춰 제한" }
---

# Ontology

온톨로지는 데이터 위에 의미를 정의하는 계층이다. 데이터 모델이 무엇을 저장하는지 정한다면, 온톨로지는 그것이 무엇을 의미하고 다른 개념과 어떤 관계인지 정한다.

## 개념 형성 경로

```text
추상화 -> 개념화 -> glossary -> taxonomy -> typed relation -> ontology
```

- Glossary는 이름과 정의를 맞춘다.
- Taxonomy는 `is-a`, `part-of` 같은 분류를 만든다.
- Ontology는 관계의 종류와 의미까지 다룬다.

## 어려운 이유

- 객체보다 관계가 빠르게 늘어나며 모든 edge를 관리할 수 없다.
- 좋은 관계는 도메인 이해와 합의가 필요하다.
- 현재 업무를 그대로 모델링하면 변화에 쉽게 깨진다.
- 엄격한 스키마는 모호성을 줄이지만 기록 마찰과 유지비를 높인다.

## 개인 KG의 선택

자연어 Markdown을 기본으로 유지하고 [[wiki/glossary|Glossary]]와 [[wiki/_ontology-schema|Ontology Frontmatter Schema]]만 선택적으로 더한다. 무타입 연결은 본문 위키링크로 충분하다. 그래프 DB 전환은 반복되는 결정론적 영향 분석이 실제 병목이 된 뒤에 검토한다.
