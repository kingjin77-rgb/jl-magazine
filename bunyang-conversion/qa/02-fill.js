const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1332, height: 750 } });
  await p.goto('file:///home/user/jl-magazine/bunyang-conversion/index.html');
  await p.waitForTimeout(2600);
  await p.addStyleTag({ content: `*{transition:none!important;animation:none!important}
    .slide{transform:none!important;opacity:1!important;visibility:visible!important}
    [data-anim],[data-step],.kw>i,.mask>span{opacity:1!important;transform:none!important;filter:none!important;clip-path:none!important}` });
  await p.evaluate(() => document.querySelectorAll('.slide').forEach(s => {
    s.classList.add('is-active');
    s.querySelectorAll('[data-step]').forEach(e => e.classList.add('step-in'));
  }));
  await p.waitForTimeout(600);
  const rows = await p.evaluate(() => {
    const GX = 60, GY = 34;
    const out = [];
    document.querySelectorAll('.slide').forEach((sl, i) => {
      const body = sl.querySelector('.s-body');
      if (!body) return;
      const br = body.getBoundingClientRect();
      if (br.width < 10) return;
      const cell = new Uint8Array(GX * GY);
      const mark = r => {
        const x0 = Math.max(0, Math.floor((r.left - br.left) / br.width * GX));
        const x1 = Math.min(GX - 1, Math.ceil((r.right - br.left) / br.width * GX) - 1);
        const y0 = Math.max(0, Math.floor((r.top - br.top) / br.height * GY));
        const y1 = Math.min(GY - 1, Math.ceil((r.bottom - br.top) / br.height * GY) - 1);
        for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) cell[y * GX + x] = 1;
      };
      body.querySelectorAll('*').forEach(e => {
        const cs = getComputedStyle(e);
        if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
        const hasInk = (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)')
          || cs.borderTopWidth !== '0px' || cs.borderLeftWidth !== '0px'
          || [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
        if (!hasInk) return;
        const r = e.getBoundingClientRect();
        if (r.width < 3 || r.height < 3) return;
        mark(r);
      });
      let f = 0; for (let k = 0; k < cell.length; k++) f += cell[k];
      out.push({ i: i + 1, t: sl.dataset.title, fill: Math.round(f / cell.length * 100) });
    });
    return out;
  });
  rows.sort((a, b) => a.fill - b.fill);
  console.log('본문 영역 채움률 (낮은 것부터 = 여백 많은 장)');
  rows.slice(0, 16).forEach(r => console.log(`  ${String(r.i).padStart(2)}장  ${String(r.fill).padStart(3)}%   ${r.t}`));
  const avg = Math.round(rows.reduce((a, r) => a + r.fill, 0) / rows.length);
  console.log(`\n평균 채움률 ${avg}% · 70% 미만 ${rows.filter(r => r.fill < 70).length}장 / ${rows.length}장`);
  await b.close();
})();
