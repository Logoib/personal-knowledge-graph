---
name: personal-kg-lookup
description: Search and reference the user's personal Obsidian knowledge graph with ranked Kiwi/BM25 lookup and minimal context loading. Use for personal KG, personal wiki, saved reflections, prior decisions, or when current work may depend on knowledge captured there.
---

# Personal KG Lookup

Resolve the KG root from `PERSONAL_KG_ROOT`, `%USERPROFILE%\.personal-kg\root.txt`, or this skill's junction target. Confirm `wiki/_summaries.md` exists.

1. Run `py -3 <KG_ROOT>\tools\kb_lookup.py --query "<topic>" --limit 6`.
2. Open only the 1–3 ranked wiki notes needed for the request.
3. Add `--include-raw` only when provenance or original detail is necessary.
4. Treat the current user, live system, and target repository as more authoritative than saved notes. Surface stale or conflicting claims.
5. Return the answer and the KG-relative note paths used.

Do not read the whole `_summaries.md` or preload the vault. Rebuild a stale index with `py -3 <KG_ROOT>\tools\kb_index_build.py`.
