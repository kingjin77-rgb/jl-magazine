---
name: 하자제안서
description: 법무법인 제이엘 하자소송 기본제안서(고정 60장)를 새 단지에 맞춰 찍어낸다. 표지 단지명·단지개요만 갈아끼우고 나머지는 고정이다. 트리거 — "○○아파트 제안서 만들어", "기본제안서 뽑아", "단지 바꿔서 다시", 단지 JSON 경로 제시.
---

# 하자소송 기본제안서 생성

**이 제안서는 고정본이다.** 매번 바뀌는 것은 표지의 단지명·단지개요와 몇 개의 가변 슬롯뿐이다.
새로 쓰지 말고 **갈아끼우고 다시 렌더**한다.

## 먼저 읽을 것

`CLAUDE.md` → `proposal/README.md` → `proposal/01_제안서_구성안.md` → `proposal/11_브랜드_스타일가이드.md`

## 절대 규칙

- **JL 실적은 판결문으로 확인된 18건이 전부다** (`proposal/10_JL_수행실적.md`).
  인터로 명의 실적(211단지·313억·채권양도율 87~99%·죽림부영·백석더샵·파주한양수자인·온천미소지움·
  남원 풍산누리안·아산 법곡코아루·대구 수성롯데캐슬·제일풍경채센트럴·운서SK)은 **쓰면 허위 기재다.**
- **회수 금액 단정 예측 금지 · 승소 보장 금지.** 변협 광고규정 확인 전까지 "승소" 대신 "수행"·"판결".
- `proposal/09`의 `[목차]` 등급 항목은 **수치·기준을 인용하지 않는다.** 조사 대상·방법까지만.
- 하자 사진·단지 전경·변호사 사진은 **실물만.** 생성·스톡·웹 수집 금지 (`proposal/12`).

## 실행

```bash
# 1) 단지 JSON을 template/data/에 둔다 (기존 파일을 복사해 값만 바꾼다)
cp template/data/예시단지.json template/data/<단지>.json

# 2) 담보책임기간 계산 — 표지·S05에 들어갈 남은 기간
python3 tools/timeline.py template/data/<단지>.json --asof $(date +%F)

# 3) 슬롯 채움 + 폰트 서브셋 + 빌드  (JL_DATA로 단지 지정)
JL_DATA=template/data/<단지>.json python3 tools/build_canvas.py

# 4) 렌더 (canvas.json 순서대로 60장 + 컨택트시트)
python3 tools/render_preview.py

# 5) 검수 — 둘 다 0이어야 한다
python3 tools/overflow_audit.py      # 넘침 0건
python3 tools/whitespace_audit.py    # 공백 120px 이상 0장

# 6) 편집 가능한 PPTX (배경 이미지 + 텍스트 상자)
python3 tools/export_pptx.py --check
```

산출물은 `template/design/preview/JL_하자소송_기본제안서.pptx`,
검증 오버레이는 `template/design/preview/_bg/_check_*.png`.

## 슬라이드를 새로 만들 때

`tools/slide_kit.py`의 프리미티브를 쓴다. 손으로 CSS를 다시 쓰지 않는다.

```python
import sys; sys.path.insert(0, 'tools')
from slide_kit import slide, cards, steps, tbl, kv, sec

s = slide('아이브로우 [고정]', '결론 문장형 제목',
    sec('구분선 딸린 소제목') + cards([...], 4) + tbl(head, rows, widths),
    [('핵심 내용', '...'), ('수치 강조', '...'), ('기한 경고', '...')],   # 하단 3단 밴드
    note='근거 출처', tight=True)                                        # tight = 여백 압축
```

`canvas.json` 편입은 `python3 tools/canvas_insert.py <새파일>.dc.html after <기준>.dc.html "표시제목"`.

## 자주 걸리는 것

- 슬롯을 채우기 **전에** 폰트를 서브셋하면 단지명 글자가 빠진다. `build_canvas.py`가 순서를 지킨다
- 옴니고딕에 `—`(em dash)·`−`(minus)가 없다. `·` `-`로 쓴다
- 렌더 후 **PNG를 눈으로 본다.** 겹침과 두부(□)는 코드만 봐서는 안 보인다
- 컨테이너 재생성 시 한글 폰트 재설치: `cp assets/fonts/*.ttf /usr/share/fonts/truetype/jl/ && fc-cache -f`
