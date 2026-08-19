/* 본문 채움률 두 가지를 잰다.
   ① 박스 채움률 — 배경·테두리가 있는 요소가 덮은 면적.  칸을 크게 만들면 100% 가 나오므로 이것만 보면 속는다.
   ② 글자 채움률 — 실제 글자 줄상자(Range.getClientRects) 가 덮은 면적.  청중이 읽을 것이 실제로 얼마나 있는지.
   ② 가 낮으면 "칸은 큰데 안이 텅 빈" 슬라이드다.  글자를 키우거나 정보를 넣어야 한다. */
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
    const GX = 96, GY = 54;
    const out = [];
    document.querySelectorAll('.slide').forEach((sl, i) => {
      const body = sl.querySelector('.s-body');
      if (!body) return;
      const br = body.getBoundingClientRect();
      if (br.width < 10) return;
      const box = new Uint8Array(GX * GY), ink = new Uint8Array(GX * GY);
      const mark = (grid, r) => {
        if (r.width < 1 || r.height < 1) return;
        const x0 = Math.max(0, Math.floor((r.left - br.left) / br.width * GX));
        const x1 = Math.min(GX - 1, Math.ceil((r.right - br.left) / br.width * GX) - 1);
        const y0 = Math.max(0, Math.floor((r.top - br.top) / br.height * GY));
        const y1 = Math.min(GY - 1, Math.ceil((r.bottom - br.top) / br.height * GY) - 1);
        for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) grid[y * GX + x] = 1;
      };
      /* ① 박스 */
      body.querySelectorAll('*').forEach(e => {
        const cs = getComputedStyle(e);
        if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
        const hasInk = (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)')
          || cs.borderTopWidth !== '0px' || cs.borderLeftWidth !== '0px'
          || [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
        if (!hasInk) return;
        const r = e.getBoundingClientRect();
        if (r.width < 3 || r.height < 3) return;
        mark(box, r);
      });
      /* ② 글자 + 그림 */
      const walk = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
      let n;
      while ((n = walk.nextNode())) {
        if (!n.textContent.trim()) continue;
        const par = n.parentElement;
        if (!par) continue;
        const cs = getComputedStyle(par);
        if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
        const rg = document.createRange(); rg.selectNodeContents(n);
        [...rg.getClientRects()].forEach(r => mark(ink, r));
      }
      /* 사진 자리는 채워질 것이므로 비어 있어도 읽을거리로 센다 */
      body.querySelectorAll('figure.ph,svg,canvas').forEach(e => mark(ink, e.getBoundingClientRect()));
      const sum = g => { let f = 0; for (let k = 0; k < g.length; k++) f += g[k]; return Math.round(f / g.length * 100); };
      out.push({ i: i + 1, t: sl.dataset.title, box: sum(box), ink: sum(ink) });
    });
    return out;
  });
  const LOW_INK = 14;   /* 글자 채움률 하한 — 이보다 낮으면 "칸만 큰" 장 */
  rows.sort((a, b) => a.ink - b.ink);
  console.log('본문 채움률   박스 = 칸이 덮은 면적 · 글자 = 실제 읽을거리가 덮은 면적');
  console.log('  장   박스   글자   제목');
  rows.slice(0, 18).forEach(r => console.log(
    `  ${String(r.i).padStart(2)}  ${String(r.box).padStart(4)}%  ${String(r.ink).padStart(4)}%${r.ink < LOW_INK ? ' ◀' : '  '} ${r.t}`));
  const avgB = Math.round(rows.reduce((a, r) => a + r.box, 0) / rows.length);
  const avgI = Math.round(rows.reduce((a, r) => a + r.ink, 0) / rows.length);
  const thin = rows.filter(r => r.ink < LOW_INK);
  console.log(`\n평균 박스 ${avgB}% · 평균 글자 ${avgI}%`);
  console.log(`박스 70% 미만 ${rows.filter(r => r.box < 70).length}장 · 글자 ${LOW_INK}% 미만 ${thin.length}장 / ${rows.length}장`);
  if (thin.length) console.log('글자가 얇은 장: ' + thin.map(r => r.i + '장(' + r.ink + '%)').join(' · '));
  await b.close();
})();
