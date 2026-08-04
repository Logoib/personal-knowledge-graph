---
title: "Ontology-ready Frontmatter Schema"
created: 2026-08-04
tags: [ontology, frontmatter, schema]
sources:
  - "repo:KG-SDSLab:wiki/_ontology-schema.md"
---

# Ontology-ready Frontmatter Schema

Ontology 블록은 선택적이며 기존 필수 frontmatter 아래에 더한다. 자연어와 위키링크가 기본이고, 타입이 실제 가치를 갖는 관계만 기록한다.

```yaml
ontology:
  concept-type: <enum>
  taxonomy-parent: <note-or-term>
  relations:
    - { type: <relation>, target: <note-or-term>, note: "<why>" }
```

## `concept-type`

| 값 | 의미 |
|---|---|
| `concept` | 추상 개념 |
| `term` | glossary 용어 |
| `system` | 시스템·서비스 |
| `process` | 절차·운영 방식 |
| `artifact` | 문서·데이터·비교 산출물 |
| `tool` | 실행 도구·라이브러리 |

## 관계 어휘

| 타입 | 의미 |
|---|---|
| `is-a` | 하위 분류 |
| `part-of` | 부분과 전체 |
| `depends-on` | 변경·실행 의존 |
| `related-to` | 약한 일반 연관 |

관계를 모두 typed하지 않는다. 무타입 연결은 본문 위키링크로 충분하다. 새로운 관계어는 실제 반복 사용처가 생긴 뒤 이 표와 검사 도구를 함께 갱신한다.
