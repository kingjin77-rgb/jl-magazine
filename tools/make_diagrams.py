#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""단면 모식도 — 사진으로는 안 보이는 것을 그린다.

방수 두께·타일 뒤채움·미장 두께·단열재 등급은 사진에 차이가 안 나타난다.
설계 기준선과 실측선을 겹쳐 그려야 부족분이 드러난다 (proposal/12 참조).

  python3 tools/make_diagrams.py          # graphics/dg_*.svg
  python3 tools/make_diagrams.py --png    # PNG도 함께
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'graphics')
N, G, R = '#0D2162', '#B08D4F', '#C0392B'
LINE, INK, MUT = '#C7CBD3', '#111418', '#5A5F68'
F = 'Pretendard, sans-serif'

W, H = 1220, 380          # 슬라이드 좌측 칼럼에 들어가는 표준 크기 (약 3.2:1)


def head(w=W, h=H):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'font-family="%s">' % (w, h, F))


def t(x, y, s, size=14, fill=INK, weight='400', anchor='start'):
    return ('<text x="%s" y="%s" font-size="%s" fill="%s" font-weight="%s" '
            'text-anchor="%s">%s</text>' % (x, y, size, fill, weight, anchor, s))


def rect(x, y, w, h, fill='none', stroke=LINE, sw=1.4, extra=''):
    return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="%s" %s/>' % (
        x, y, w, h, fill, stroke, sw, extra)


def hatch(idx, color='#D8DCE4'):
    """콘크리트 바탕 해칭."""
    return ('<defs><pattern id="h%d" width="8" height="8" patternUnits="userSpaceOnUse" '
            'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" '
            'stroke="%s" stroke-width="2.4"/></pattern></defs>' % (idx, color))


def dim(x1, y, x2, label, color=N, above=True):
    """치수선 — 양끝 화살표 + 라벨."""
    ty = y - 8 if above else y + 16
    return ('<g stroke="%s" stroke-width="1.3"><line x1="%s" y1="%s" x2="%s" y2="%s"/>'
            '<line x1="%s" y1="%s" x2="%s" y2="%s"/><line x1="%s" y1="%s" x2="%s" y2="%s"/></g>'
            % (color, x1, y, x2, y, x1, y - 5, x1, y + 5, x2, y - 5, x2, y + 5)
            + t((x1 + x2) / 2, ty, label, 14, color, '700', 'middle'))


# ── 1. 방수층 두께 ────────────────────────────────────────────────
def dg_waterproof():
    s = [head(), hatch(1)]
    s.append(t(0, 22, '설계 기준과 실측의 차이 — 방수층 단면', 16, N, '800'))
    for i, (x, title, th, col, note) in enumerate([
            (0, '설계도서 기준', 26, N, '상세도에 적힌 두께'),
            (640, '파취 후 실측', 11, R, '기준에 못 미치는 두께')]):
        y0 = 70
        s.append(t(x, y0 - 12, title, 15, col, '800'))
        s.append(rect(x, y0, 500, 90, 'url(#h1)', LINE))          # 콘크리트 슬래브
        s.append(t(x + 250, y0 + 55, '콘크리트 슬래브', 13, MUT, '400', 'middle'))
        s.append(rect(x, y0 - th, 500, th, col, col, 0))          # 방수층
        s.append(t(x + 250, y0 - th - 10, '방수층', 13, col, '700', 'middle'))
        s.append(rect(x, y0 - th - 26, 500, 26, '#F4F5F8', LINE)) # 마감
        s.append(t(x + 250, y0 - th - 32 + 22, '바닥 마감', 12, MUT, '400', 'middle'))
        # 두께 치수
        s.append('<g stroke="%s" stroke-width="1.3"><line x1="%s" y1="%s" x2="%s" y2="%s"/>'
                 '<line x1="%s" y1="%s" x2="%s" y2="%s"/><line x1="%s" y1="%s" x2="%s" y2="%s"/></g>'
                 % (col, x + 520, y0 - th, x + 520, y0, x + 514, y0 - th, x + 526, y0 - th,
                    x + 514, y0, x + 526, y0))
        s.append(t(x + 534, y0 - th / 2 + 5, 'T', 15, col, '800'))
        s.append(t(x, y0 + 118, note, 13.5, MUT))
    # 가운데 화살표
    s.append('<path d="M556 105 h60" stroke="%s" stroke-width="2" fill="none"/>' % MUT)
    s.append('<path d="M616 105 l-9 -5 v10 z" fill="%s"/>' % MUT)
    s.append(t(586, 92, '대조', 13, MUT, '700', 'middle'))
    s.append(rect(0, 250, W, 92, '#FBF7EE', '#E7D9BC'))
    s.append(t(22, 280, '차이가 곧 보수 범위입니다', 15, '#8F7033', '800'))
    s.append(t(22, 306, '사진으로는 이 두께 차이가 보이지 않습니다. 파취 후 계측기 눈금이 함께 찍힌 사진과', 13.5, INK))
    s.append(t(22, 328, '이 단면 모식도를 함께 제시해야 부족분이 드러납니다.', 13.5, INK))
    return ''.join(s) + '</svg>'


# ── 2. 타일 뒤채움 ────────────────────────────────────────────────
def dg_tile():
    s = [head(), hatch(2)]
    s.append(t(0, 22, '타일 뒤채움 — 배면을 열어야 보입니다', 16, N, '800'))
    for x, title, gaps, col, note in [
            (0, '정상 시공', [], N, '접착재가 배면 전체에 채워진 상태'),
            (640, '뒤채움 부족', [(60, 90), (210, 70), (350, 100)], R, '배면에 공극이 남아 들뜸·탈락으로 이어짐')]:
        y0 = 66
        s.append(t(x, y0 - 12, title, 15, col, '800'))
        s.append(rect(x, y0, 500, 40, 'url(#h2)', LINE))                 # 바탕면
        s.append(t(x + 250, y0 + 26, '바탕 모르타르', 12, MUT, '400', 'middle'))
        s.append(rect(x, y0 + 40, 500, 34, '#E9EDF8', LINE))             # 접착재
        for gx, gw in gaps:                                              # 공극
            s.append(rect(x + gx, y0 + 40, gw, 34, '#FFFFFF', R, 1.6, 'stroke-dasharray="4 3"'))
        s.append(t(x + 250, y0 + 63, '접착재(뒤채움)', 12, MUT, '400', 'middle'))
        for i in range(4):                                               # 타일
            s.append(rect(x + i * 125 + 3, y0 + 74, 119, 44, '#FFFFFF', N, 1.6))
        s.append(t(x + 250, y0 + 102, '타 일', 13, N, '700', 'middle'))
        s.append(t(x, y0 + 148, note, 13.5, MUT))
    s.append(rect(0, 250, W, 92, '#FBF7EE', '#E7D9BC'))
    s.append(t(22, 280, '2026 개정판이 처음으로 기준을 제시했습니다', 15, '#8F7033', '800'))
    s.append(t(22, 306, '인장 부착강도 0.39N/㎟ 미만이면 하자로 판정합니다. 시공 부위·바탕 접착 상태·들뜸 범위를', 13.5, INK))
    s.append(t(22, 328, '함께 보아 철거 후 재시공과 접착재 주입 보수 중 어느 쪽인지가 정해집니다.', 13.5, INK))
    return ''.join(s) + '</svg>'


# ── 3. 미장 바름 두께 ─────────────────────────────────────────────
def dg_mortar():
    s = [head(), hatch(3)]
    s.append(t(0, 22, '미장 바름 두께 — 법원 실무서가 예시로 든 하자', 16, N, '800'))
    for x, title, th, col, lab in [
            (0, '상세도 치수', 60, N, '18㎜'), (640, '현장 실측 평균', 40, R, '12㎜')]:
        y0 = 62
        s.append(t(x, y0 - 12, title, 15, col, '800'))
        s.append(rect(x, y0, 300, 140, 'url(#h3)', LINE))                 # 조적벽
        s.append(t(x + 150, y0 + 78, '조적 벽체', 13, MUT, '400', 'middle'))
        s.append(rect(x + 300, y0, th, 140, col, col, 0))                 # 미장층
        s.append(dim(x + 300, y0 + 158, x + 300 + th, lab, col, False))
        s.append(t(x + 300 + th + 16, y0 + 76, '미장', 13.5, col, '700'))
    s.append('<path d="M556 130 h60" stroke="%s" stroke-width="2" fill="none"/>' % MUT)
    s.append('<path d="M616 130 l-9 -5 v10 z" fill="%s"/>' % MUT)
    s.append(t(586, 117, '6㎜ 부족', 13, R, '800', 'middle'))
    s.append(rect(0, 250, W, 92, '#FBF7EE', '#E7D9BC'))
    s.append(t(22, 280, '산정 방식이 원문에 확정되어 있습니다', 15, '#8F7033', '800'))
    s.append(t(22, 306, '철거·재시공비가 아니라 하자 없이 시공했을 경우와 하자 있는 상태의 시공비용 차액입니다.', 13.5, INK))
    s.append(t(22, 328, '사용검사 전 변경시공으로 판단되면 5년 구간에 남습니다.', 13.5, INK))
    return ''.join(s) + '</svg>'


# ── 4. 단열재 변경시공 ────────────────────────────────────────────
def dg_insulation():
    s = [head(), hatch(4)]
    s.append(t(0, 22, '단열재 변경시공 — 벽 안이라 절개해야 보입니다', 16, N, '800'))
    for x, title, th, col, lab, grade in [
            (0, '설계도서 사양', 72, N, 'THK 85㎜', '가등급'),
            (640, '실제 시공', 48, R, 'THK 60㎜', '나등급')]:
        y0 = 62
        s.append(t(x, y0 - 12, title, 15, col, '800'))
        s.append(rect(x, y0, 120, 130, 'url(#h4)', LINE))                 # 외벽
        s.append(t(x + 60, y0 + 72, '외벽', 12, MUT, '400', 'middle'))
        s.append(rect(x + 120, y0, th, 130, col, col, 0))                 # 단열재
        s.append(t(x + 120 + th / 2, y0 + 72, grade, 12.5, '#FFFFFF', '700', 'middle'))
        s.append(rect(x + 120 + th, y0, 90, 130, '#F4F5F8', LINE))        # 내부 마감
        s.append(t(x + 165 + th, y0 + 72, '마감', 12, MUT, '400', 'middle'))
        s.append(dim(x + 120, y0 + 148, x + 120 + th, lab, col, False))
    # 결로 표시
    s.append(t(1000, 92, '결로·곰팡이', 14, R, '800'))
    s.append(t(1000, 114, '사용검사 이후 발생', 13, MUT))
    for i, dy in enumerate((132, 152, 172)):
        s.append('<path d="M1004 %d c3 4 5 6 5 8a5 5 0 0 1-10 0c0-2 2-4 5-8z" fill="%s" opacity=".7"/>'
                 % (dy, R))
    s.append(rect(0, 250, W, 92, '#FBF7EE', '#E7D9BC'))
    s.append(t(22, 280, '시공은 사용검사 전, 하자 현상은 사용검사 후입니다', 15, '#8F7033', '800'))
    s.append(t(22, 306, '단열재는 사용검사 이전에 바뀌었고 결로는 그 이후에 나타납니다. 원문은 이 경우', 13.5, INK))
    s.append(t(22, 328, '사용검사 이후 하자로 판단합니다. 보수청구 공문으로 발생 시점을 특정해 두어야 합니다.', 13.5, INK))
    return ''.join(s) + '</svg>'


DIAGRAMS = {'dg_waterproof': dg_waterproof, 'dg_tile': dg_tile,
            'dg_mortar': dg_mortar, 'dg_insulation': dg_insulation}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in DIAGRAMS.items():
        path = os.path.join(OUT, name + '.svg')
        open(path, 'w', encoding='utf-8').write(fn())
        print('  ', name + '.svg')
    print('단면 모식도 %d종 → %s' % (len(DIAGRAMS), OUT))
    if '--png' in sys.argv:
        import cairosvg
        for name in DIAGRAMS:
            cairosvg.svg2png(url=os.path.join(OUT, name + '.svg'),
                             write_to=os.path.join(OUT, name + '.png'),
                             output_width=W * 2, output_height=H * 2)
        print('PNG %d장 (2배)' % len(DIAGRAMS))


if __name__ == '__main__':
    main()
