#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""단지 JSON에서 담보책임기간 타임라인 SVG를 생성한다.

슬라이드의 이미지 슬롯(가로로 긴 4:1)에 꼭 맞는 비율로 그린다.
기존 2400x1200 도해는 슬롯이 4:1이라 위아래 흰 여백이 생겼다.

  python3 tools/make_timeline_svg.py template/data/<단지>.json --asof 2026-08-24
"""
import argparse, datetime as dt, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import compute, parse_date          # 기존 계산 로직 재사용

W, H = 1220, 300
L, R, TOP, BOT = 250, 210, 62, 48                  # 라벨열 / 우측 / 상하 여백
NAVY, GOLD, INK, LINE = '#0D2162', '#B08D4F', '#111418', '#C7CBD3'
ALERT, WARN, SAFE = '#C0392B', '#E67E22', '#0D2162'
ESC = {'&': '&amp;', '<': '&lt;', '>': '&gt;'}


def esc(s):
    return ''.join(ESC.get(c, c) for c in str(s))


def build(data, asof):
    insp = parse_date(data['사용검사일'])
    hand = parse_date(data['입주개시일']) if data.get('입주개시일') else None
    rows = compute(insp, hand, asof)
    span_end = max(parse_date(r['expiry']) for r in rows)
    span_end = max(span_end, asof)
    lo = insp.year
    hi = span_end.year + 1
    plot_w = W - L - R
    yrs = max(1, hi - lo)

    def x_of(d):
        t = ((d.year - lo) * 365.25 + d.timetuple().tm_yday) / (yrs * 365.25)
        return L + min(1.0, max(0.0, t)) * plot_w

    band_h = (H - TOP - BOT) / len(rows)
    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="Pretendard,\'Malgun Gothic\',sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>']

    # 연도 눈금
    for y in range(lo, hi + 1):
        gx = x_of(dt.date(y, 1, 1))
        out.append(f'<line x1="{gx:.1f}" y1="{TOP-14}" x2="{gx:.1f}" y2="{H-BOT+6}" '
                   f'stroke="{LINE}" stroke-width="1"/>')
        out.append(f'<text x="{gx:.1f}" y="{H-BOT+24}" font-size="12.5" fill="{INK}" '
                   f'text-anchor="middle" opacity=".75">{y}</text>')

    for i, r in enumerate(rows):
        cy = TOP + band_h * i + band_h / 2
        col = {'도과': ALERT, '임박': WARN}.get(r['status'], SAFE)
        x0, x1 = x_of(parse_date(r['start'])), x_of(parse_date(r['expiry']))
        bh = 22
        # 연차 배지
        out.append(f'<rect x="8" y="{cy-14:.1f}" width="46" height="28" fill="#EFF2FB"/>')
        out.append(f'<text x="31" y="{cy+5:.1f}" font-size="14" font-weight="700" '
                   f'fill="{NAVY}" text-anchor="middle">{r["years"]}년</text>')
        # 공종 라벨
        label = r['label'].split(' (')[0]
        out.append(f'<text x="66" y="{cy-1:.1f}" font-size="14" font-weight="700" '
                   f'fill="{NAVY}">{esc(label[:24])}</text>')
        out.append(f'<text x="66" y="{cy+15:.1f}" font-size="11.5" fill="{INK}" '
                   f'opacity=".72">{esc(r["basis"])}</text>')
        # 기간 막대
        out.append(f'<rect x="{x0:.1f}" y="{cy-bh/2:.1f}" width="{max(2,x1-x0):.1f}" '
                   f'height="{bh}" fill="{col}"/>')
        # 만료일 · 계산식
        out.append(f'<text x="{x1+9:.1f}" y="{cy-3:.1f}" font-size="13" '
                   f'font-weight="700" fill="{col}">{r["expiry"]} {r["status"]}</text>')
        out.append(f'<text x="{x0+8:.1f}" y="{cy+bh/2+14:.1f}" font-size="10.5" '
                   f'fill="{INK}" opacity=".60">{esc(r["formula"])}</text>')

    # 오늘 기준선
    tx = x_of(asof)
    out.append(f'<line x1="{tx:.1f}" y1="{TOP-20}" x2="{tx:.1f}" y2="{H-BOT+6}" '
               f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    out.append(f'<text x="{tx:.1f}" y="{TOP-26}" font-size="12" font-weight="700" '
               f'fill="{INK}" text-anchor="middle">오늘 {asof.isoformat()}</text>')
    # 범례
    lx = L
    for name, c in (('여유', SAFE), ('임박', WARN), ('도과', ALERT)):
        out.append(f'<rect x="{lx}" y="{H-18}" width="11" height="11" fill="{c}"/>')
        out.append(f'<text x="{lx+16}" y="{H-8}" font-size="11.5" fill="{INK}">{name}</text>')
        lx += 66
    out.append(f'<text x="{W-R+40}" y="{H-8}" font-size="10.5" fill="{INK}" opacity=".6" '
               f'text-anchor="end">집합건물법 제9조의2 · 시행령 제5조</text>')
    out.append('</svg>')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data')
    ap.add_argument('--asof')
    ap.add_argument('--out', default='graphics/s05_담보책임기간_타임라인.svg')
    a = ap.parse_args()
    data = json.load(open(a.data, encoding='utf-8'))
    asof = parse_date(a.asof) if a.asof else dt.date.today()
    svg = build(data, asof)
    open(a.out, 'w', encoding='utf-8').write(svg)
    print('생성', a.out, '%dx%d' % (W, H))


if __name__ == '__main__':
    main()
