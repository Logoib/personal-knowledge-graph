---
name: personal-kg-lookup
description: >-
  개인 Obsidian 지식그래프. 코드·git·README·문서에는 없고
  본인 기록에만 있는 것들 — 과거에 내린 결정과 그 이유,
  직접 겪은 삽질과 해결, 도구·환경 설정 경위, 반복되는
  작업 절차, 사람·조직 맥락.
  Use when the user says 개인 KG, personal wiki, 위키에서 찾아줘,
  /personal-kg-lookup. ALSO use unprompted whenever grep·git·웹검색
  으로 답이 안 나오는 맥락에 막혔을 때, 예전에 정한 것 같은데
  기억이 안 날 때, 또는 확실하지 않다고 말하려는 순간.
---

# Personal KG Lookup

Resolve the KG root from `PERSONAL_KG_ROOT`, `%USERPROFILE%\.personal-kg\root.txt`, or this skill's junction target. Confirm `wiki/_summaries.md` exists.

1. Run `py -3 <KG_ROOT>\tools\kb_lookup.py --query "<topic>" --limit 6`.
2. Open only the 1–3 ranked wiki notes needed for the request.
3. Add `--include-raw` only when provenance or original detail is necessary.
4. Treat the current user, live system, and target repository as more authoritative than saved notes. Surface stale or conflicting claims.
5. Return the answer and the KG-relative note paths used.
6. One lookup does not settle the session. Look up again whenever the objective, the topic, or the evidence you need changes — an earlier lookup on a different topic is not an answer to the new fact. After a compaction or a long stretch of unrelated work, treat prior results as stale and look them up again rather than recalling them.

Do not read the whole `_summaries.md` or preload the vault. Rebuild a stale index with `py -3 <KG_ROOT>\tools\kb_index_build.py`.
