# Personal Knowledge Graph

Obsidian에서 읽고 Git으로 보존하며, Codex·Claude·Gemini가 같은 위키와 스킬을 조회하는 개인용 knowledge graph입니다.

핵심 구조는 단순합니다.

- `raw/`: 새 원본을 그대로 추가하는 보존층
- `wiki/`: LLM과 사람이 함께 관리하는 큐레이션층
- `tools/`: 검색·링크·레지스트리 health
- `tools/agent-hub/`: 세 AI 런타임이 공유하는 skill 원본

## 시작

```powershell
git clone https://github.com/Logoib/personal-knowledge-graph.git
cd personal-knowledge-graph
pwsh -File tools/install-git-hooks.ps1
pwsh -File tools/agent-hub/scripts/sync-agent-hub.ps1
py -3 tools/kb_index_build.py
```

Kiwi 형태소 검색은 선택 사항입니다.

```powershell
py -3 -m pip install kiwipiepy
```

Kiwi나 색인이 없어도 `kb_lookup.py`는 substring 검색으로 자동 폴백합니다.

## 사용

```powershell
py -3 tools/kb_lookup.py --query "context rot" --limit 6
py -3 tools/kb_health.py
```

위키를 수정하면 `wiki/_index.md`, `wiki/_summaries.md`, `wiki/_backlinks.md`를 함께 갱신합니다. Git 동작 전에는 `GIT_GUIDE.md`를 따릅니다.
