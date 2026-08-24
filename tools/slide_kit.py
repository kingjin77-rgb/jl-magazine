#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""슬라이드 생성 키트 — 확립된 레이아웃 패턴을 재사용해 .dc.html을 찍어낸다.

기존 슬라이드와 같은 크롬(네이비 헤더 밴드 · 골드 라인 · 푸터)과 같은 조판을 쓴다.
본문 블록은 아래 프리미티브를 조합한다.

  cards(items)     카드 그리드          steps(items)   번호 흐름
  tbl(head, rows)  표                   split(l, r)    좌우 분할
  band(items)      핵심 내용·수치 강조·기한 경고 3단 밴드
  kv(items)        라벨-값 목록          note(text)     하단 주석
"""
import html

NAVY, GOLD = '#0D2162', '#B08D4F'

CORE = """
  *{box-sizing:border-box;margin:0;padding:0;}
  :root{--navy:#0D2162;--navy-deep:#081541;--gold:#B08D4F;--gold-ink:#8F7033;
    --ink:#111418;--muted:#111418;--card:#F4F5F8;--line:#C7CBD3;--bg:#fff;--alert:#C0392B;--warn:#E67E22;}
  html,body{width:1332px;height:750px;overflow:hidden;background:var(--bg);
    font-family:"Pretendard","Malgun Gothic",sans-serif;color:var(--ink);position:relative;}
  .runner{position:absolute;top:28px;left:56px;right:56px;display:flex;justify-content:space-between;
    font-size:15px;color:var(--muted);}
  .eyebrow{position:absolute;left:56px;top:70px;font-size:15px;letter-spacing:.02em;color:var(--gold-ink);
    font-weight:700;display:flex;align-items:center;gap:10px;}
  .eyebrow::before{content:"";width:32px;height:1px;background:var(--gold-ink);}
  .title{position:absolute;left:56px;top:96px;right:56px;font-size:24px;font-weight:800;
    color:var(--navy);letter-spacing:-.02em;line-height:1.4;}
  .footer{position:absolute;bottom:0;left:0;right:0;height:36px;display:flex;align-items:center;
    justify-content:space-between;padding:0 56px;border-top:1.4px solid var(--line);
    font-size:14px;color:var(--muted);}
  .footer .firm{color:var(--navy);font-weight:700;}

  /* ── 본문 프리미티브 ── */
  .body{position:absolute;left:56px;right:56px;top:168px;bottom:%(bottom)dpx;}
  .sec{font-size:13px;font-weight:800;color:var(--gold-ink);letter-spacing:.02em;
    padding-bottom:6px;border-bottom:1.6px solid var(--navy);margin-bottom:11px;}
  .sec+.sec,.blk+.sec{margin-top:16px;}

  .cards{display:grid;gap:14px;}
  .c{border:1px solid var(--line);border-top:3px solid var(--navy);background:#fff;padding:14px 17px;}
  .c .ck{font-size:15.5px;font-weight:800;color:var(--navy);letter-spacing:-.01em;}
  .c .cv{margin-top:8px;font-size:13.5px;line-height:1.62;color:var(--ink);}
  .c .cn{font-size:12px;font-weight:800;color:var(--gold-ink);letter-spacing:.12em;margin-bottom:6px;}
  .c b{color:var(--navy);font-weight:800;}

  .flow{display:grid;gap:0;}
  .step{position:relative;border:1px solid var(--line);background:#fff;padding:13px 15px 14px;}
  .step+.step{border-left:0;}
  .step .num{font-size:12px;font-weight:800;color:#fff;background:var(--navy);
    width:22px;height:22px;display:flex;align-items:center;justify-content:center;margin-bottom:8px;}
  .step .t{font-size:14.5px;font-weight:800;color:var(--ink);line-height:1.35;}
  .step .b{margin-top:7px;font-size:12.5px;line-height:1.55;color:var(--ink);}

  .tbl{border:1px solid var(--line);}
  .tbl .th{display:flex;background:var(--navy);color:#fff;font-size:14px;font-weight:700;}
  .tbl .th div{padding:10px 15px;}
  .tbl .tr{display:flex;border-top:1px solid var(--line);font-size:13.5px;line-height:1.5;}
  .tbl .tr div{padding:9px 15px;}
  .tbl .tr b{color:var(--navy);font-weight:800;}

  .kv .r{display:flex;gap:10px;font-size:13.5px;line-height:1.55;padding:7px 0;
    border-bottom:1px solid var(--line);}
  .kv .r:last-child{border-bottom:0;}
  .kv .r span{flex:0 0 118px;color:var(--navy);font-weight:700;}
  .kv .r em{flex:1;font-style:normal;}

  .split{display:flex;gap:26px;height:100%%;}
  .split>div{flex:1;}

  .verify{position:absolute;left:56px;right:56px;bottom:%(band)dpx;height:152px;
    display:grid;grid-template-columns:1fr 1fr 1fr;
    border:1.4px solid var(--line);border-top:3px solid var(--navy);background:#fff;}
  .verify>div{padding:13px 18px 12px;border-left:1px solid var(--line);}
  .verify>div:first-child{border-left:0;}
  .verify .vk{font-size:14.5px;font-weight:800;color:var(--navy);margin-bottom:7px;
    display:flex;align-items:center;gap:7px;letter-spacing:-.01em;}
  .verify .vk::before{content:"";width:4px;height:15px;background:var(--gold);}
  .verify .vv{font-size:13.5px;line-height:1.6;color:var(--ink);}
  .verify .warnk{color:#C0392B;}
  .verify .warnk::before{background:#C0392B!important;}
  .verify *{background:transparent;}

  .note{position:absolute;left:56px;right:56px;bottom:%(note)dpx;font-size:13px;line-height:1.6;color:var(--ink);}

  /* ── 법무법인 제안서 헤더 밴드 ── */
  body::before{content:"";position:absolute;left:0;top:0;right:0;height:142px;
    background:linear-gradient(150deg,#0D2162 0%%,#081541 100%%);z-index:0;}
  body::after{content:"";position:absolute;left:0;top:142px;right:0;height:4px;
    background:var(--gold);z-index:1;}
  .runner{z-index:2;color:rgba(255,255,255,.66)!important;}
  .eyebrow{z-index:2;color:#CBB27E!important;}
  .eyebrow::before{background:#CBB27E!important;}
  .title{z-index:2;color:#FFFFFF!important;}
  html,body{background:#FFFFFF!important;}
  body>*:not(.runner):not(.eyebrow):not(.title):not(.footer){z-index:1;}
  .footer{background:#fff;border-top:2px solid var(--navy)!important;z-index:2;}
"""

E = html.escape


def sec(t):
    return '<div class="sec">%s</div>' % t


def cards(items, cols=None, style=''):
    cols = cols or len(items)
    o = ['<div class="cards blk" style="grid-template-columns:repeat(%d,1fr);%s">' % (cols, style)]
    for it in items:
        n = '<div class="cn">%s</div>' % it['n'] if it.get('n') else ''
        o.append('<div class="c">%s<div class="ck">%s</div><div class="cv">%s</div></div>'
                 % (n, it['k'], it['v']))
    o.append('</div>')
    return ''.join(o)


def steps(items, style='', start=1):
    o = ['<div class="flow blk" style="grid-template-columns:repeat(%d,1fr);%s">' % (len(items), style)]
    for i, it in enumerate(items, start):
        o.append('<div class="step"><div class="num">%d</div><div class="t">%s</div>'
                 '<div class="b">%s</div></div>' % (i, it['t'], it['b']))
    o.append('</div>')
    return ''.join(o)


def tbl(head, rows, widths, style=''):
    w = lambda i: 'style="width:%s"' % widths[i] if widths[i] else 'style="flex:1"'
    o = ['<div class="tbl blk" style="%s"><div class="th">' % style]
    o += ['<div %s>%s</div>' % (w(i), h) for i, h in enumerate(head)]
    o.append('</div>')
    for r in rows:
        o.append('<div class="tr">' + ''.join('<div %s>%s</div>' % (w(i), c)
                                              for i, c in enumerate(r)) + '</div>')
    o.append('</div>')
    return ''.join(o)


def kv(items):
    return ('<div class="kv blk">' +
            ''.join('<div class="r"><span>%s</span><em>%s</em></div>' % (a, b) for a, b in items) +
            '</div>')


def band(items):
    o = ['<div class="verify">']
    for i, (k, v) in enumerate(items):
        o.append('<div><div class="vk%s">%s</div><div class="vv">%s</div></div>'
                 % (' warnk' if i == 2 else '', k, v))
    o.append('</div>')
    return ''.join(o)


TIGHT = """
  /* 촘촘 모드 — 내용이 하단 밴드에 닿을 때 여백만 줄인다 */
  .tbl .tr div{padding:6.6px 15px;}
  .tbl .th div{padding:8px 15px;}
  .kv .r{padding:4.6px 0;}
  .sec{margin-bottom:9px;}
  .sec+.sec,.blk+.sec{margin-top:12px;}
  .c{padding:12px 16px;}
"""


def slide(eyebrow, title, body, footer_band=None, note=None, bottom=None, tight=False):
    # 밴드와 주석이 함께 있으면 밴드를 위로 올려 주석 자리를 만든다
    bb = 78 if (footer_band and note) else 52
    nb = 44 if note else 52
    bottom = bottom if bottom is not None else ((bb + 168) if footer_band else 56)
    css = CORE % {'bottom': bottom, 'note': nb, 'band': bb}
    if tight:
        css += TIGHT
    parts = ['<!doctype html>', '<html>', '<head>', '<meta charset="utf-8">',
             '<script src="./support.js"></script>', '<style>' + css + '</style>',
             '</head>', '<body>',
             '  <div class="runner"><span>법무법인 제이엘 하자소송 수행 제안서</span></div>',
             '  <div class="eyebrow">%s</div>' % eyebrow,
             '  <div class="title">%s</div>' % title,
             '  <div class="body">%s</div>' % body]
    if footer_band:
        parts.append('  ' + band(footer_band))
    if note:
        parts.append('  <div class="note">%s</div>' % note)
    parts += ['  <div class="footer"><span class="firm">법무법인 제이엘</span><span>JL LAWFIRM</span></div>',
              '</body>', '</html>', '']
    return '\n'.join(parts)
