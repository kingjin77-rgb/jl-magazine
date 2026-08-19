const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1332, height: 750 } });
  const errs=[]; p.on('pageerror',e=>errs.push('ERR: '+e.message));
  await p.goto('file:///home/user/jl-magazine/bunyang-conversion/index.html');
  await p.waitForTimeout(900);
  const r = await p.evaluate(() => [...document.querySelectorAll('.slide')]
      .map((s,i)=>`${String(i+1).padStart(2)}. ${s.dataset.title}  → ${s.dataset.steps||0}단계`));
  console.log(r.join('\n'));
  const tot = await p.evaluate(()=>[...document.querySelectorAll('.slide')]
      .reduce((a,s)=>a+Math.max(1,+(s.dataset.steps||0)),0));
  console.log('\n총 발표 비트:', tot, '(슬라이드 21장)');
  console.log('JS 오류:', errs.length?errs.join('\n'):'없음');
  await b.close();
})();
