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
    const out = [];
    document.querySelectorAll('.slide').forEach((sl, i) => {
      const body = sl.querySelector('.s-body');
      if (!body) return;
      const br = body.getBoundingClientRect();
      let maxB = br.top, minT = br.bottom;
      body.querySelectorAll('*').forEach(e => {
        if (e.closest('svg')) return;
        const r = e.getBoundingClientRect();
        if (!r.width || !r.height) return;
        const cs = getComputedStyle(e);
        if (cs.visibility === 'hidden' || cs.display === 'none') return;
        if (r.bottom > maxB) maxB = r.bottom;
        if (r.top < minT) minT = r.top;
      });
      const dead = Math.max(0, br.bottom - maxB);
      out.push({ i: i + 1, t: sl.dataset.title, avail: Math.round(br.height),
                 used: Math.round(maxB - br.top), dead: Math.round(dead),
                 pct: Math.round(dead / br.height * 100) });
    });
    return out;
  });
  rows.sort((a, b) => b.dead - a.dead);
  console.log('본문 영역 아래쪽 빈 공간 (큰 것부터)');
  console.log('  장  빈공간   비율   제목');
  rows.slice(0, 18).forEach(r => {
    if (r.dead < 12) return;
    console.log(`  ${String(r.i).padStart(2)}  ${String(r.dead).padStart(5)}px  ${String(r.pct).padStart(3)}%   ${r.t}`);
  });
  const bad = rows.filter(r => r.dead >= 40);
  console.log(`\n40px 이상 빈 장: ${bad.length} / ${rows.length}장`);
  await b.close();
})();
