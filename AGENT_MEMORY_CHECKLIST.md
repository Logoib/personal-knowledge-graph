# Agent Memory Checklist

## 주입 전

- 이 정보가 현재 요청의 결정에 실제로 필요한가?
- live 상태나 현재 저장소가 더 권위 있는가?
- 오래된 스냅샷이면 날짜·revision을 드러냈는가?

## 조회

- `kb_lookup.py`로 ranked 검색했는가?
- top hit 중 필요한 1~3개만 열었는가?
- 원문은 provenance가 필요할 때만 `--include-raw`로 열었는가?

## 기록

- 반복해서 재사용될 사실·판단·실패 교훈인가?
- 원본은 `raw/`, 재사용 지식은 `wiki/`에 분리했는가?
- `sources`와 내부 링크를 남겼는가?
- 세 registry와 health를 갱신했는가?

## 폐기·갱신

- 오래된 사실을 삭제하기보다 현재 정본과 교체 이유를 기록했는가?
- stale 정보가 자동 주입되지 않도록 summary와 skill을 최소화했는가?
