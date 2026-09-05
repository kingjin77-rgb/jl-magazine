#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""표지 히어로 밴드 아트 — 아파트 입면 도면 스타일 SVG.

납작한 도형 스카이라인(클립아트처럼 보인다)을 대신한다.
실사 사진을 받으면 이 자리에 그대로 갈아끼운다.

  python3 tools/make_cover_art.py > /dev/null   # graphics/cover_elevation.svg 생성
"""
import os

W, H = 1332, 352
GOLD = '#CBB27E'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'graphics', 'cover_elevation.svg')


def tower(x, y, w, floors, fh, op):
    """입면 한 동 — 층선·발코니 모듈·수직 멀리언."""
    h = floors * fh
    p = ['<g stroke="#FFFFFF" fill="none" stroke-opacity="%.2f" stroke-width="1">' % op]
    p.append('<rect x="%d" y="%d" width="%d" height="%d" stroke-opacity="%.2f"/>'
             % (x, y, w, h, op * 1.8))
    for i in range(1, floors):                       # 층선
        p.append('<line x1="%d" y1="%d" x2="%d" y2="%d"/>' % (x, y + i * fh, x + w, y + i * fh))
    bays = max(3, w // 34)
    bw = w / bays
    for j in range(1, bays):                         # 세로 멀리언
        p.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d"/>' % (x + j * bw, y, x + j * bw, y + h))
    p.append('</g>')
    # 발코니 — 층마다 한 베이씩 살짝 밝게
    p.append('<g fill="#FFFFFF" fill-opacity="%.3f">' % (op * 0.16))
    for i in range(floors):
        b = (i * 3 + x) % bays
        p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d"/>'
                 % (x + b * bw + 1, y + i * fh + 1, bw - 2, fh - 2))
    p.append('</g>')
    # 옥탑 파라펫
    p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-opacity=".55" stroke-width="1.6"/>'
             % (x - 4, y, x + w + 4, y, GOLD))
    return ''.join(p)


def build():
    s = ['<svg viewBox="0 0 %d %d" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">' % (W, H)]
    s.append('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#0B1B44"/><stop offset="1" stop-color="#060F2E"/>'
             '</linearGradient>'
             '<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#060F2E" stop-opacity="1"/>'
             '<stop offset=".42" stop-color="#060F2E" stop-opacity="0"/></linearGradient></defs>')
    s.append('<rect width="%d" height="%d" fill="url(#sky)"/>' % (W, H))

    # 청사진 그리드
    s.append('<g stroke="#FFFFFF" stroke-opacity=".045" stroke-width="1">')
    for x in range(0, W, 37):
        s.append('<line x1="%d" y1="0" x2="%d" y2="%d"/>' % (x, x, H))
    for y in range(0, H, 37):
        s.append('<line x1="0" y1="%d" x2="%d" y2="%d"/>' % (y, W, y))
    s.append('</g>')

    # 동 배치 — 뒤에서 앞으로
    s.append(tower(196, 150, 118, 8, 24, .13))
    s.append(tower(348, 104, 96, 10, 24, .17))
    s.append(tower(986, 128, 132, 9, 24, .15))
    s.append(tower(1160, 168, 108, 7, 24, .11))
    s.append(tower(506, 58, 150, 12, 24, .30))       # 주동
    s.append(tower(700, 86, 128, 11, 24, .24))
    s.append(tower(870, 142, 92, 8, 24, .19))

    # 치수선 — 주동 좌측
    s.append('<g stroke="%s" stroke-opacity=".62" stroke-width="1" fill="none">' % GOLD)
    s.append('<line x1="482" y1="58" x2="482" y2="346"/>')
    s.append('<line x1="474" y1="58" x2="490" y2="58"/>')
    s.append('<line x1="474" y1="346" x2="490" y2="346"/>')
    s.append('<path d="M482,58 l-4,10 h8 z" fill="%s" fill-opacity=".62" stroke="none"/>' % GOLD)
    s.append('<path d="M482,346 l-4,-10 h8 z" fill="%s" fill-opacity=".62" stroke="none"/>' % GOLD)
    s.append('</g>')

    # 단면 디테일 콜아웃 — 방수층 레이어
    cx, cy, r = 1052, 250, 54
    s.append('<g><circle cx="%d" cy="%d" r="%d" fill="#0B1B44" fill-opacity=".92" '
             'stroke="%s" stroke-opacity=".55" stroke-width="1.2"/>' % (cx, cy, r, GOLD))
    s.append('<g stroke="#FFFFFF" stroke-opacity=".42" stroke-width="1">')
    for i, dy in enumerate((-22, -12, -4, 6, 18)):
        s.append('<line x1="%d" y1="%d" x2="%d" y2="%d"/>' % (cx - 36, cy + dy, cx + 36, cy + dy))
    s.append('</g>')
    s.append('<rect x="%d" y="%d" width="72" height="8" fill="%s" fill-opacity=".38"/>'
             % (cx - 36, cy - 12, GOLD))
    s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-opacity=".45" stroke-width="1"/>'
             % (cx - 38, cy - 40, 962, 186, GOLD))
    s.append('</g>')

    # 지면 + 좌측 페이드(제목 쪽 정리)
    s.append('<rect x="0" y="346" width="%d" height="2" fill="%s" fill-opacity=".55"/>' % (W, GOLD))
    s.append('<rect width="%d" height="%d" fill="url(#fade)"/>' % (W, H))
    s.append('</svg>')
    return ''.join(s)


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(build())
    print(OUT, len(build()), 'bytes')
