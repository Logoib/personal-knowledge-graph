---
name: personal-kg-ingest
description: Import reusable personal knowledge, reflections, decisions, and source material into the personal Obsidian knowledge graph while preserving provenance and registry integrity. Use when asked to save, remember, ingest, or add something to the personal KG.
---

# Personal KG Ingest

Resolve the KG root from `PERSONAL_KG_ROOT`, `%USERPROFILE%\.personal-kg\root.txt`, or this skill's junction target.

1. Add new source material under `raw/` without editing existing originals.
2. Search for related notes with `tools/kb_lookup.py` before creating a new note.
3. Update or create the minimum useful note under `wiki/concepts`, `wiki/articles`, or `wiki/connections`.
4. Include `title`, `created`, `tags`, and `sources` frontmatter. Use vault-relative links and `repo:<name>:<path>` for external Git sources.
5. Update `_index.md`, `_summaries.md`, and `_backlinks.md` together.
6. Run `py -3 tools/kb_health.py --repair` and report the changed paths.

Prefer durable conclusions, decisions, failure lessons, and reusable procedures. Do not save transient chat filler or secrets.
