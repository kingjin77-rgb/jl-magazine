const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1332, height: 750 } });
  await p.goto('file:///home/user/jl-magazine/bunyang-conversion/index.html');
  await p.waitForTimeout(1500);
  // 모든 전환 정지 후 전 슬라이드 동시 활성화
  await p.addStyleTag({ content: `*{transition:none!important;animation:none!important}
    .slide{transform:none!important;filter:none!important;opacity:1!important;visibility:visible!important}
    [data-anim],[data-step],.kw>i,.mask>span{opacity:1!important;transform:none!important;filter:none!important;clip-path:none!important}` });
  await p.evaluate(() => document.querySelectorAll('.slide').forEach(s => {
    s.classList.add('is-active');
    s.querySelectorAll('[data-step]').forEach(e => e.classList.add('step-in'));
  }));
  await p.waitForTimeout(500);
  const r = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('.slide').forEach((sl, i) => {
      const sr = sl.getBoundingClientRect();
      const bb = sl.querySelector('.brandbar').getBoundingClientRect();
      const LIMIT = bb.top - sr.top - 4;      // 브랜드바 위 4px 여유
      let worst = 0, who = '';
      sl.querySelectorAll('.s-body *').forEach(e => {
        if (e.closest('svg')) return;
        const r = e.getBoundingClientRect();
        if (!r.width || !r.height) return;
        const ov = (r.bottom - sr.top) - LIMIT;
        if (ov > worst) { worst = ov; who = (e.className||e.tagName) + ' :: ' + (e.textContent||'').trim().replace(/\s+/g,' ').slice(0,40); }
      });
      if (worst > 2) out.push('S' + String(i+1).padStart(2) + '  ' + Math.round(worst) + 'px  ' + sl.dataset.title + '  — ' + who);
    });
    return out;
  });
  console.log(r.length ? r.join('\n') : '넘침 없음');
  console.log('\n넘치는 슬라이드: ' + r.length + ' / 36장');
  await b.close();
})();
