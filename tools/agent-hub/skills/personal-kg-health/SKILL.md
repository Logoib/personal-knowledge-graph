---
name: personal-kg-health
description: Audit or repair the personal Obsidian knowledge graph, registry freshness, links, ontology frontmatter, Kiwi/BM25 index, and shared personal-kg skill wiring. Use for personal KG health checks, broken links, stale lookup, skill sync, or memory hygiene.
---

# Personal KG Health

Resolve the KG root from `PERSONAL_KG_ROOT`, `%USERPROFILE%\.personal-kg\root.txt`, or this skill's junction target.

1. Read `AGENTS.md`, `AGENT_SETUP.md`, and `AGENT_MEMORY_CHECKLIST.md`.
2. Audit runtime wiring with `pwsh -File tools/agent-hub/scripts/sync-agent-hub.ps1 -AuditOnly`.
3. Run `py -3 tools/kb_health.py`.
4. If repair was requested, run the sync script without `-AuditOnly`, then `py -3 tools/kb_health.py --repair`.
5. Report healthy checks, repairs, and any remaining manual follow-up.

Repair the shared source or junction wiring, not runtime-specific copies. Do not treat a missing optional Kiwi package as data loss; lookup will use substring fallback.
