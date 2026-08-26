#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""아이콘 세트 — 48x48 라인 아이콘을 SVG로 직접 그린다.

생성 이미지는 선 굵기가 제각각이라 24개를 나란히 놓으면 티가 난다.
규격은 S21에서 쓰던 것을 그대로 따른다.
  네이비 #0D2162 stroke 2.9 · 골드 #B08D4F 강조 1획 · round cap · fill none

  python3 tools/make_icons.py            # graphics/icons/*.svg
  python3 tools/make_icons.py --sheet    # 확인용 대조표 PNG도
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'graphics', 'icons')
N, G = '#0D2162', '#B08D4F'
SW, SG = '2.9', '3.1'
HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none" '
        'stroke-linecap="round" stroke-linejoin="round">')


def p(d, gold=False):
    return '<path d="%s" stroke="%s" stroke-width="%s"/>' % (d, G if gold else N, SG if gold else SW)


def c(cx, cy, r, gold=False):
    return '<circle cx="%s" cy="%s" r="%s" stroke="%s" stroke-width="%s"/>' % (
        cx, cy, r, G if gold else N, SG if gold else SW)


ICONS = {
    # ── 하자 유형 8 ──
    'defect-wallpad':    [p('M6 10h20v18H6z'), p('M11 33h10'), p('M16 28v5'),
                          p('M32 12h12v24H32z'), p('M32 12l-6 4v16l6 4'),
                          p('M36 19h4M36 25h4', True)],
    'defect-tile':       [p('M6 14h16v14H6z'), p('M26 14h16v14H26z'), p('M6 34h36'),
                          p('M29 17l10 8M39 17l-10 8', True)],
    'defect-waterproof': [p('M6 32h36'), p('M6 25h36', True), p('M6 25v9M42 25v9'),
                          p('M15 9v11M23 9v11'), p('M11 9h16')],
    'defect-firedoor':   [p('M10 6h20v36H10z'), p('M25 24h2'),
                          p('M37 20c3 3 4 6 2 9s-6 2-7-1 2-6 5-8z', True)],
    'defect-crack':      [p('M8 8h32v32H8z'), p('M21 8l4 10-5 8 6 8-3 6', True),
                          p('M32 30h6M35 27v6')],
    'defect-mortar':     [p('M8 34h32'), p('M8 27h32', True), p('M8 27v7M40 27v7'),
                          p('M18 8l10 10-4 4-10-10z'), p('M28 18l6-6')],
    'defect-insulation': [p('M8 8h18v32H8z'), p('M14 8v32M20 8v32'),
                          p('M35 17c3 4 5 7 5 10a5 5 0 0 1-10 0c0-3 2-6 5-10z', True)],
    'defect-common':     [p('M6 12h36'), p('M12 12v28M24 12v28M36 12v28'),
                          p('M6 40h36'), p('M6 21h36', True)],
    # ── 절차 8 ──
    'step-survey':       [p('M14 8h20v34H14z'), p('M19 5h10v6H19z'), p('M20 23l4 4 8-8', True)],
    'step-drawing':      [p('M8 12h24v22H8z'), p('M8 12c-3 0-3 22 0 22'), p('M15 20h11M15 26h8'),
                          c(35, 33, 7, True), p('M40 38l4 4', True)],
    'step-assign':       [p('M12 6h16l8 8v28H12z'), p('M28 6v8h8'), p('M18 34h12', True),
                          c(24, 25, 5)],
    'step-file':         [p('M6 18L24 8l18 10'), p('M11 18v18M20 18v18M28 18v18M37 18v18'),
                          p('M6 40h36', True)],
    'step-appraise':     [p('M8 26L26 8l8 8-18 18z'), p('M14 20l4 4M20 14l4 4'),
                          c(35, 33, 7, True), p('M40 38l4 4', True)],
    'step-judgment':     [p('M24 8v30'), p('M12 14h24'), p('M12 14L6 28h12zM36 14l-6 14h12', True),
                          p('M16 40h16')],
    'step-execute':      [p('M10 8h18l6 6v11'), p('M28 8v6h6'), p('M10 8v32h13'),
                          p('M28 34h14M36 28l6 6-6 6', True)],
    'step-repair':       [p('M8 10h16v28H8z'), p('M8 24h16', True),
                          p('M32 12a6 6 0 0 0 8 8l-4 14a4 4 0 0 1-8 0l4-14a6 6 0 0 1 0-8z')],
    # ── 개념 8 ──
    'idea-period':       [p('M8 12h26v26H8z'), p('M14 6v10M28 6v10'), p('M8 21h26', True),
                          c(37, 33, 8), p('M37 28v5l4 2')],
    'idea-law':          [p('M10 8h28v32H10z'), p('M17 8v32'), p('M23 17h10M23 23h10', True),
                          p('M23 29h6')],
    'idea-spec':         [p('M6 14h24v22H6z'), p('M18 8h24v22H18z'), p('M24 16h12', True),
                          p('M24 22h8')],
    'idea-stat':         [p('M8 40h34'), p('M8 40V10'), p('M15 40V28h6v12zM26 40V20h6v20z'),
                          p('M37 40V14h5v26z', True)],
    'idea-cost':         [p('M12 6h24v36H12z'), p('M17 12h14v7H17z'), p('M18 27h4M26 27h4', True),
                          p('M18 35h4M26 35h4')],
    'idea-report':       [p('M8 8h18l6 6v20H8z'), p('M26 8v6h6'), p('M14 21h12M14 27h8'),
                          p('M30 28h12v10h-6l-4 4v-4h-2z', True)],
    'idea-agree':        [p('M6 22l8-6 10 6'), p('M42 22l-8-6-8 5'),
                          p('M14 26l6 6 4-3 5 5', True), p('M6 22v10M42 22v10')],
    'idea-verify':       [p('M24 6l16 6v14c0 8-7 14-16 16-9-2-16-8-16-16V12z'),
                          p('M17 24l5 5 10-10', True)],
}


def build():
    os.makedirs(OUT, exist_ok=True)
    for name, parts in ICONS.items():
        open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
            HEAD + ''.join(parts) + '</svg>')
    print('아이콘 %d종 → %s' % (len(ICONS), OUT))


def sheet():
    """확인용 대조표 — 24개를 한 판에 늘어놓고 눈으로 본다."""
    import io as _io
    import cairosvg
    from PIL import Image, ImageDraw, ImageFont
    names = sorted(ICONS)
    cols, cell = 6, 150
    rows = (len(names) + cols - 1) // cols
    sh = Image.new('RGB', (cols * cell, rows * cell), 'white')
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Pretendard-Medium.ttf'), 13)
    for i, n in enumerate(names):
        png = cairosvg.svg2png(url=os.path.join(OUT, n + '.svg'),
                               output_width=96, output_height=96, background_color='white')
        sh.paste(Image.open(_io.BytesIO(png)).convert('RGB'),
                 ((i % cols) * cell + 27, (i // cols) * cell + 14))
        d.text(((i % cols) * cell + 10, (i // cols) * cell + 118), n, font=f, fill='#333')
    o = os.path.join(OUT, '_sheet.png')
    sh.save(o); print('대조표', o, sh.size)


if __name__ == '__main__':
    build()
    if '--sheet' in sys.argv:
        sheet()
