# Git Guide

원격 정본은 private GitHub 저장소 `Logoib/personal-knowledge-graph`다.

## 기본 흐름

```powershell
git pull --ff-only
py -3 tools/kb_health.py
git add <바꾼 파일들>
git commit -m "docs(kg): 변경 이유"
git push
```

## 규칙

1. Git 동작 전에 이 문서를 읽는다.
2. 작업 시작 시 `git pull --ff-only`로 동기화한다. 실패하면 stash/reset/merge를 자동 수행하지 않는다.
3. commit 전 `py -3 tools/kb_health.py`를 통과한다.
4. `git add -A`, `--no-verify`, force push를 쓰지 않는다.
5. `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`는 byte-identical해야 한다.
6. 위키 본문 변경에는 `wiki/_summaries.md` 갱신을 함께 stage한다.
7. 작은 개인 콘텐츠 변경은 `main`에 직접 반영해도 된다. 도구·규칙의 큰 변경은 branch와 PR을 사용한다.
