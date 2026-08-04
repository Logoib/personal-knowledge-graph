---
title: "Lookup Context Isolation — Context Rot을 막는 회수 계약"
created: 2026-08-04
tags: [lookup, context-isolation, context-rot, top-k, retrieval]
sources:
  - "repo:KG-SDSLab:tools/agent-hub/skills/kg-lookup/SKILL.md"
ontology:
  concept-type: process
  relations:
    - { type: depends-on, target: kiwi-bm25-retrieval, note: "ranked path와 snippet으로 후보를 축소" }
    - { type: related-to, target: context-rot-agent-loop-design, note: "fresh context capsule의 지식 회수 규칙" }
---

# Lookup Context Isolation

KG 조회가 context rot을 만들지 않으려면 저장소 전체를 읽는 대신 검색과 본문 읽기를 분리해야 한다.

## 기본 계약

1. query를 원문 그대로 유지한다.
2. ranked lookup은 path, title/snippet만 top-k로 반환한다.
3. 실제로 필요한 1~3개 note body만 연다.
4. provenance가 필요한 경우에만 raw를 opt-in한다.
5. 답에는 사용한 note path와 불확실성을 남긴다.

`_summaries.md`를 통째로 읽는 것은 검색용 계산을 context window에 떠넘기는 일이다. Kiwi/BM25는 이 계산을 context 밖에서 수행한다.

## 언제 새 context를 쓰는가

한두 노트의 후속 질문이 예상되면 같은 context에서 읽는 편이 낫다. 반대로 탐색적 주제이거나 3개 이상 본문을 합성해야 하면 fresh worker나 별도 세션에 검색을 맡기고, 본문 대신 사실·출처 경로만 돌려받는다.

## 신선도 경계

위키는 저장된 이해이고 live state가 아니다. 현재 코드, 실행 결과, 최신 문서와 충돌하면 조회 결과를 routing lead로 취급하고 [[wiki/articles/provenance-and-freshness|Provenance와 Freshness]] 규칙으로 재검증한다.
