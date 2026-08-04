---
title: "Markdown Wiki vs Formal Ontology"
created: 2026-08-04
tags: [comparison, markdown, ontology, graph-database]
sources:
  - "repo:KG-SDSLab:wiki/connections/graph-studio-vs-sdslab-kg.md"
  - "repo:KG-SDSLab:wiki/concepts/ontology.md"
ontology:
  concept-type: artifact
  relations:
    - { type: related-to, target: ontology, note: "형식성 선택의 비용·효익 비교" }
    - { type: related-to, target: personal-knowledge-graph, note: "현재 Markdown 중심 구조의 근거" }
---

# Markdown Wiki vs Formal Ontology

두 방식은 대체 관계라기보다 서로 다른 층을 담당한다.

| Markdown/Git에 유지 | Formal ontology 후보 |
|---|---|
| 서술, 판단 근거, 실패 이유, 예외 | 안정된 객체·타입·관계 |
| raw provenance와 Git diff | RDF/URI와 기계 검증 |
| 낮은 기록 마찰 | 반복 query와 영향 분석 |
| ranked natural-language lookup | 계산 가능한 graph operation |

Markdown 위키는 암묵지와 변화하는 이해를 손실 없이 기록하는 데 강하다. Formal ontology는 다원천 엔터티 정합, 반복 관계 질의, 엄격한 영향 분석에서 강하지만 스키마 합의와 변경 관리 비용이 크다.

따라서 기본은 ontology-ready Markdown이다. [[wiki/glossary|Glossary]]로 용어를 맞추고 [[wiki/_ontology-schema|Ontology Frontmatter Schema]]로 가치가 분명한 관계만 typed한다. 실제 반복 query가 병목이 되면 그 core만 export하거나 formal layer를 붙인다.
