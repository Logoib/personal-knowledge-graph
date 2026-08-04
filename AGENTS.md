# Personal Knowledge Graph Agent Rules

이 저장소는 Obsidian 기반 개인 knowledge graph이자 Codex, Claude, Gemini가 함께 참조하는 지식 저장소다. `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`는 항상 동일 내용으로 유지한다.

## 구조

- `raw/` — 원본 소스. 기존 파일은 직접 고치지 않는다.
- `wiki/` — LLM이 컴파일하고 사람이 검토하는 위키.
- `wiki/_index.md` — 전체 인덱스.
- `wiki/_summaries.md` — ranked lookup의 검색 진입점.
- `wiki/_backlinks.md` — 문서 간 참조 레지스트리.
- `wiki/concepts/`, `wiki/articles/`, `wiki/connections/` — 개념, 자료 요약, 관계 문서.
- `outputs/` — 생성 가능한 파생 산출물. 기본적으로 Git에 넣지 않는다.
- `tools/` — 조회·검사 도구와 공용 agent 자산.

## 위키 규칙

1. `wiki/` 본문을 수정하면 `_index.md`, `_summaries.md`, `_backlinks.md`를 함께 확인·갱신한다.
2. 새 wiki 문서는 YAML frontmatter의 `title`, `created`, `tags`, `sources`를 포함한다.
3. 내부 링크는 vault 기준 경로를 쓴다. 예: `[[wiki/concepts/ontology|Ontology]]`.
4. basename과 일치하지 않는 제목형 링크와 빈 Markdown 노트를 만들지 않는다.
5. 외부 Git 소스는 `repo:<repo-name>:<repo-relative-path>` 형식을 우선한다. Git 밖 파일만 `local-only:<absolute-path>`로 적는다.
6. 기존 `raw/` 원본은 읽기 전용이다. 새 원본 추가는 허용한다.
7. 상세 원문이 꼭 필요하지 않으면 `raw/`보다 `wiki/`를 먼저 읽는다.

## 조회·컨텍스트 규칙

1. 조회는 `_summaries.md` 전체 읽기가 아니라 `py -3 tools/kb_lookup.py --query "<topic>" --limit 6`에서 시작한다.
2. ranked hit 중 필요한 1~3개 노트만 연다. 원문이 필요할 때만 `--include-raw`를 쓴다.
3. 자동 주입 메모리는 최소화하고, 현재 질문에 필요한 지식만 just-in-time으로 회수한다.
4. 현재 사용자·실행 상태·대상 저장소가 live authority다. 위키의 오래된 주장과 충돌하면 충돌을 드러내고 최신 상태를 검증한다.

## 검사·Git 규칙

1. 변경 후 `py -3 tools/kb_health.py`를 실행한다.
2. 모든 Git 동작 전 `GIT_GUIDE.md`를 먼저 읽는다.
3. `git add -A`, force push, hook 우회를 하지 않는다. 바꾼 파일만 명시적으로 stage한다.
4. `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 중 하나를 수정하면 셋을 byte-identical하게 맞춘다.

## Skill 운영

- 공용 skill 원본은 `tools/agent-hub/skills/` 한 곳에서만 수정한다.
- 런타임 skill 폴더는 원본을 가리키는 junction으로 유지한다.
- 개인용 skill 이름은 업무용 KG와 충돌하지 않도록 `personal-kg-*`를 쓴다.
