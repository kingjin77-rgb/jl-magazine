# 검수 스크립트

```bash
npm install playwright        # 최초 1회
node 01-overflow.js   # 브랜드바를 침범하는 요소 (반드시 0)
node 02-fill.js       # 본문 채움률 (평균 95% 이상, 70% 미만 장 없어야 함)
node 03-steps.js      # 슬라이드별 등장 단계 수 · JS 오류
node 04-deadspace.js  # 본문 아래쪽 빈 공간 (40px 이상 없어야 함)
node 05-content.js    # 원본 전문 대조 (미반영 0)
```
