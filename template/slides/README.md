# 슬라이드 렌더 파이프라인

## 캡처
```bash
mkdir -p /usr/share/fonts/truetype/jl && cp assets/fonts/*.ttf /usr/share/fonts/truetype/jl/ && fc-cache -f
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --disable-gpu --no-sandbox \
  --force-device-scale-factor=2 --window-size=1332,750 \
  --screenshot="template/slides/fixed/<파일>.png" "file://$(pwd)/template/slides/fixed/<파일>.html"
```
1332×750 아트보드, 2배(2664×1500) 캡처.

## 구조
- `_master.css` — 팔레트(11_브랜드_스타일가이드.md)·러너·제목마크·브랜드바 공통 정의
- `fixed/` — 고정 25장
- `variable/` — 가변 6장 (단지 JSON 슬롯)

## 상태
| 슬라이드 | 상태 |
|---|---|
| S9 이원구조 | 완성 (표+검토의견 카드) |
| 나머지 24장 | 예정 |

렌더 후 **PNG를 반드시 눈으로 확인**. 텍스트 겹침·두부는 코드로 안 보인다.
