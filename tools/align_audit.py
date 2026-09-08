#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""정렬 검사 — 슬라이드를 넘길 때 생기는 '출렁거림'을 잡는다.

제목·아이브로우·본문 시작·하단 밴드·푸터의 y 좌표가 슬라이드마다 다르면
넘길 때 요소가 위아래로 흔들린다. 기준값에서 벗어난 장을 찾아낸다.
"""
import io, json, os, sys
from collections import Counter
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'template', 'design', 'build')
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
TOL = 2          # 2px 이내는 같은 것으로 본다

JS = r"""
() => {
  const y = sel => {
    const e = document.querySelector(sel);
    if (!e) return null;
    const r = e.getBoundingClientRect();
    return { top: Math.round(r.top), left: Math.round(r.left),
             right: Math.round(1332 - r.right), bottom: Math.round(r.bottom) };
  };
  return {
    eyebrow: y('.eyebrow'), title: y('.title'), runner: y('.runner'),
    body: y('.body') || y('.cols') || y('.table') || y('.tbl') || y('.cards') || y('.list'),
    verify: y('.verify'), footer: y('.footer'), note: y('.note'),
  };
}
"""


def main():
    m = json.load(io.open(os.path.join(BUILD, 'canvas.json'), encoding='utf-8'))
    rows = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        pg = br.new_page(viewport={'width': 1332, 'height': 750})
        for i, a in enumerate(m['artboards'], 1):
            p = os.path.join(BUILD, a['file'])
            if not os.path.exists(p):
                continue
            pg.goto('file://' + p)
            pg.wait_for_timeout(150)
            rows.append((i, a['file'].replace('.dc.html', ''), pg.evaluate(JS)))
        br.close()

    # 본문 슬라이드(제목이 있는 장)만 기준을 잡는다. 표지·간지는 성격이 다르다
    content = [r for r in rows if r[2].get('title')]
    print('본문 슬라이드 %d장 / 전체 %d장\n' % (len(content), len(rows)))

    checks = [('eyebrow', 'top', '아이브로우 상단'), ('title', 'top', '제목 상단'),
              ('title', 'left', '제목 좌측'), ('runner', 'top', '러너 상단'),
              ('body', 'top', '본문 시작'), ('body', 'left', '본문 좌측'),
              ('verify', 'top', '하단 밴드 상단'), ('footer', 'top', '푸터 상단')]

    bad = 0
    for key, axis, label in checks:
        vals = [(i, n, d[key][axis]) for i, n, d in content if d.get(key)]
        if not vals:
            continue
        base, cnt = Counter(v for _, _, v in vals).most_common(1)[0]
        off = [(i, n, v) for i, n, v in vals if abs(v - base) > TOL]
        mark = 'OK ' if not off else '!! '
        print('%s%-14s 기준 %4dpx  (%d/%d장 일치)' % (mark, label, base, cnt, len(vals)))
        for i, n, v in off[:6]:
            print('      %02d %-26s %4dpx  (%+d)' % (i, n, v, v - base))
        if len(off) > 6:
            print('      … 외 %d장' % (len(off) - 6))
        bad += len(off)
    print('\n어긋난 항목 %d건' % bad)


if __name__ == '__main__':
    main()
