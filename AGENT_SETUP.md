# Agent Setup

개인용 skill은 업무용 `kg-*`와 공존하도록 `personal-kg-*` 이름을 사용한다.

```powershell
pwsh -File tools/agent-hub/scripts/sync-agent-hub.ps1
pwsh -File tools/agent-hub/scripts/sync-agent-hub.ps1 -AuditOnly
```

스크립트는 clone 위치를 `%USERPROFILE%\.personal-kg\root.txt`에 기록하고, Codex·Claude·Gemini의 skill 폴더에 junction을 만든다. 런타임 폴더의 사본을 직접 수정하지 않는다.
