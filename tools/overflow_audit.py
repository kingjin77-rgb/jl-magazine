#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""넘침 검사 — 내용이 슬라이드 밖으로 나가거나 하단 밴드에 가려지는지 본다.

렌더 PNG만 봐서는 '가려진 것'과 '원래 없는 것'을 구별할 수 없다. DOM에서 직접 잰다.
"""
import io, json, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'template', 'design', 'build')
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

JS = r"""
() => {
  const bad = [];
  const band = document.querySelector('.verify');
  const bt = band ? band.getBoundingClientRect().top : 1e9;
  const foot = document.querySelector('.footer');
  const ft = foot ? foot.getBoundingClientRect().top : 750;
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (!el.textContent.trim()) continue;
    if (el.closest('.verify') || el.closest('.footer')) continue;
    const r = el.getBoundingClientRect();
    if (r.height < 2) continue;
    if (r.top < 60 && r.height > 600) continue;   // 전면 장식 패널은 의도된 것
    if (r.bottom > 752) bad.push(['슬라이드 밖', el.className || el.tagName, Math.round(r.bottom)]);
    else if (r.top < bt && r.bottom > bt + 3) bad.push(['밴드에 가림', el.className || el.tagName, Math.round(r.bottom)]);
    else if (!band && r.top < ft && r.bottom > ft + 3) bad.push(['푸터에 가림', el.className || el.tagName, Math.round(r.bottom)]);
  }
  const seen = new Set(); const out = [];
  for (const b of bad) { const k = b[0] + b[2]; if (!seen.has(k)) { seen.add(k); out.push(b); } }
  return out.slice(0, 4);
}
"""


def main():
    m = json.load(io.open(os.path.join(BUILD, 'canvas.json'), encoding='utf-8'))
    n = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        pg = br.new_page(viewport={'width': 1332, 'height': 750})
        for i, a in enumerate(m['artboards'], 1):
            path = os.path.join(BUILD, a['file'])
            if not os.path.exists(path):
                continue
            pg.goto('file://' + path)
            pg.wait_for_timeout(180)
            for kind, cls, bottom in pg.evaluate(JS):
                print('%02d %-28s %s  .%s  bottom=%d'
                      % (i, a['file'].replace('.dc.html', ''), kind, str(cls)[:34], bottom))
                n += 1
        br.close()
    print('\n넘침 %d건' % n)


if __name__ == '__main__':
    main()
