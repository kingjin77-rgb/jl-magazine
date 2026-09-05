#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""미리보기 페이지 — 67장을 브라우저에서 훑어보는 단일 HTML.

렌더 PNG를 축소·JPEG로 인라인한다. 발행하면 링크 하나로 공유된다.
  python3 tools/make_viewer.py <출력.html>
"""
import base64, glob, io, json, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, 'template', 'design', 'preview')
BUILD = os.path.join(ROOT, 'template', 'design', 'build')
W = 1000


def titles():
    t = {}
    for p in glob.glob(os.path.join(BUILD, '*.dc.html')):
        s = io.open(p, encoding='utf-8').read()
        m = (re.search(r'<div class="title"[^>]*>(.*?)</div>', s, re.S)
             or re.search(r'<div class="kr"[^>]*>(.*?)</div>', s, re.S)
             or re.search(r'<div class="big"[^>]*>(.*?)</div>', s, re.S))
        e = re.search(r'<div class="eyebrow"[^>]*>(.*?)</div>', s, re.S)
        clean = lambda x: ' '.join(re.sub(r'<[^>]+>', ' ', x).split()) if x else ''
        t[os.path.basename(p).replace('.dc.html', '')] = (
            clean(m.group(1) if m else ''), clean(e.group(1) if e else '').replace(' [고정]', ''))
    return t


def main(out):
    tm = titles()
    files = sorted(f for f in glob.glob(os.path.join(PREV, '*.png')) if 'contact' not in f)
    data = []
    for i, f in enumerate(files, 1):
        im = Image.open(f).convert('RGB').resize((W, int(W * 750 / 1332)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'JPEG', quality=78, optimize=True)
        stem = os.path.basename(f).split('_', 1)[1].replace('.png', '')
        ti, eb = tm.get(stem, ('', ''))
        data.append({'n': i, 'k': eb or stem, 't': ti,
                     'src': 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()})
    html = TPL.replace('__DATA__', json.dumps(data, ensure_ascii=False))
    io.open(out, 'w', encoding='utf-8').write(html)
    print('%s · %.1f MB · %d장' % (out, os.path.getsize(out) / 1e6, len(data)))


TPL = r'''<title>제이엘 하자소송 제안서 열람</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#F1F0EC; --surface:#FFFFFF; --edge:#DDDBD4;
  --ink:#16181C; --muted:#6B6E76; --accent:#0D2162; --gold:#8F7033;
  --shadow:0 1px 2px rgba(20,22,26,.06),0 8px 24px rgba(20,22,26,.08);
}
:root:not([data-theme="light"]){@media (prefers-color-scheme:dark){
  --ground:#131519; --surface:#1D2026; --edge:#2C3038;
  --ink:#E9EAEE; --muted:#9AA0AA; --accent:#8FA6DC; --gold:#C9AC74;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.45);
}}
:root[data-theme="dark"]{
  --ground:#131519; --surface:#1D2026; --edge:#2C3038;
  --ink:#E9EAEE; --muted:#9AA0AA; --accent:#8FA6DC; --gold:#C9AC74;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.45);
}
*{box-sizing:border-box;}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"IBM Plex Sans KR","Pretendard","Malgun Gothic",sans-serif;
  -webkit-font-smoothing:antialiased;}
.bar{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:18px;
  padding:14px 22px;background:color-mix(in srgb,var(--ground) 88%,transparent);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--edge);}
.bar h1{margin:0;font-size:15px;font-weight:600;letter-spacing:-.01em;}
.bar .sub{font-size:13px;color:var(--muted);}
.bar .sp{flex:1;}
.count{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--muted);
  font-variant-numeric:tabular-nums;}
button{font:inherit;color:inherit;background:var(--surface);border:1px solid var(--edge);
  border-radius:7px;padding:6px 13px;font-size:13px;cursor:pointer;transition:.15s;}
button:hover{border-color:var(--accent);color:var(--accent);}
button:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff;}

/* ── 전체 보기 ── */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
  gap:22px;padding:24px 22px 60px;}
.card{background:var(--surface);border:1px solid var(--edge);border-radius:10px;
  overflow:hidden;cursor:pointer;box-shadow:var(--shadow);transition:.18s;
  display:flex;flex-direction:column;}
.card:hover{transform:translateY(-2px);border-color:var(--accent);}
.card:focus-visible{outline:2px solid var(--accent);outline-offset:3px;}
.card img{width:100%;display:block;aspect-ratio:1332/750;object-fit:cover;
  border-bottom:1px solid var(--edge);}
.meta{padding:11px 13px 13px;display:flex;gap:11px;align-items:flex-start;}
.num{font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:500;
  color:var(--gold);padding-top:1px;font-variant-numeric:tabular-nums;flex:0 0 auto;}
.txt .k{font-size:11.5px;color:var(--muted);letter-spacing:.02em;}
.txt .t{margin-top:3px;font-size:13px;line-height:1.45;font-weight:500;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}

/* ── 한 장 보기 ── */
.one{display:none;padding:22px;}
.one.on{display:block;}
.stage{max-width:1180px;margin:0 auto;}
.stage img{width:100%;display:block;border:1px solid var(--edge);border-radius:10px;
  box-shadow:var(--shadow);background:var(--surface);}
.cap{display:flex;align-items:baseline;gap:14px;margin:16px 2px 0;}
.cap .n{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--gold);
  font-variant-numeric:tabular-nums;}
.cap .k{font-size:12.5px;color:var(--muted);}
.cap .t{font-size:16px;font-weight:600;line-height:1.4;text-wrap:balance;}
.nav{display:flex;justify-content:center;gap:10px;margin-top:20px;}
.hint{text-align:center;margin-top:14px;font-size:12px;color:var(--muted);}
kbd{font-family:"IBM Plex Mono",monospace;font-size:11px;border:1px solid var(--edge);
  border-bottom-width:2px;border-radius:4px;padding:1px 5px;background:var(--surface);}
@media (prefers-reduced-motion:reduce){*{transition:none!important;}}
</style>

<div class="bar">
  <h1>법무법인 제이엘 · 하자소송 기본제안서</h1>
  <span class="sub" id="mode">전체 보기</span>
  <span class="sp"></span>
  <span class="count" id="cnt"></span>
  <button id="tg" aria-pressed="false">한 장씩 보기</button>
</div>

<div class="grid" id="grid"></div>

<div class="one" id="one">
  <div class="stage">
    <img id="big" alt="">
    <div class="cap">
      <span class="n" id="bn"></span>
      <div><div class="k" id="bk"></div><div class="t" id="bt"></div></div>
    </div>
    <div class="nav">
      <button id="prev">← 이전</button>
      <button id="next">다음 →</button>
      <button id="back">전체 보기</button>
    </div>
    <div class="hint"><kbd>←</kbd> <kbd>→</kbd> 이동 · <kbd>Esc</kbd> 전체 보기</div>
  </div>
</div>

<script>
const S = __DATA__;
const $ = id => document.getElementById(id);
let cur = 0, single = false;

$('cnt').textContent = S.length + '장';
S.forEach((s, i) => {
  const c = document.createElement('div');
  c.className = 'card'; c.tabIndex = 0;
  c.innerHTML = '<img loading="lazy" src="' + s.src + '" alt="' + s.n + '쪽 ' + s.t + '">'
    + '<div class="meta"><span class="num">' + String(s.n).padStart(2, '0') + '</span>'
    + '<div class="txt"><div class="k">' + s.k + '</div><div class="t">' + s.t + '</div></div></div>';
  const open = () => { cur = i; setMode(true); };
  c.onclick = open;
  c.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } };
  $('grid').appendChild(c);
});

function draw() {
  const s = S[cur];
  $('big').src = s.src; $('big').alt = s.n + '쪽 ' + s.t;
  $('bn').textContent = String(s.n).padStart(2, '0') + ' / ' + S.length;
  $('bk').textContent = s.k; $('bt').textContent = s.t;
  $('prev').disabled = cur === 0; $('next').disabled = cur === S.length - 1;
}
function setMode(on) {
  single = on;
  $('one').classList.toggle('on', on);
  $('grid').style.display = on ? 'none' : '';
  $('tg').setAttribute('aria-pressed', on);
  $('tg').textContent = on ? '전체 보기' : '한 장씩 보기';
  $('mode').textContent = on ? '한 장씩 보기' : '전체 보기';
  if (on) { draw(); window.scrollTo(0, 0); }
}
$('tg').onclick = () => setMode(!single);
$('back').onclick = () => setMode(false);
$('prev').onclick = () => { if (cur > 0) { cur--; draw(); } };
$('next').onclick = () => { if (cur < S.length - 1) { cur++; draw(); } };
addEventListener('keydown', e => {
  if (!single) return;
  if (e.key === 'ArrowLeft' && cur > 0) { cur--; draw(); }
  else if (e.key === 'ArrowRight' && cur < S.length - 1) { cur++; draw(); }
  else if (e.key === 'Escape') setMode(false);
});
</script>'''

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'viewer.html')
