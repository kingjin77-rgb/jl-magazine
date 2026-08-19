// 원본 전문(verify/original-text.txt) 과 덱 텍스트를 대조합니다. 미반영 0 이어야 합니다.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const norm = s => s.normalize('NFKC').replace(/Ｌ/g,'L').replace(/㎡|m²/g,'m2')
  .replace(/[\s,.\-–—·ㆍ:：/()（）\[\]"'’‘“”%％+=*×÷~〜&]/g,'').toLowerCase();
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, '../index.html'));
  await p.waitForTimeout(1800);
  const mine = norm(await p.evaluate(() =>
    [...document.querySelectorAll('.slide')].map(s => s.textContent).join('\n')));
  await b.close();
  const orig = fs.readFileSync(path.resolve(__dirname, '../verify/original-text.txt'), 'utf8')
    .split('\n').map(l => l.trim()).filter(Boolean);
  let ok = 0, part = 0; const miss = [];
  for (const line of orig) {
    const n = norm(line);
    if (n.length < 3) continue;
    if (mine.includes(n)) { ok++; continue; }
    const toks = line.split(/[\s,·ㆍ()]+/).map(norm).filter(t => t.length >= 2);
    if (!toks.length) { ok++; continue; }
    const r = toks.filter(t => mine.includes(t)).length / toks.length;
    if (r >= .85) ok++; else if (r >= .5) part++; else miss.push(line);
  }
  console.log(`원본 ${ok + part + miss.length}줄 → 완전 ${ok} · 부분 ${part} · 미반영 ${miss.length}`);
  miss.forEach(l => console.log('   ', l.slice(0, 90)));
  process.exit(miss.length ? 1 : 0);
})();
