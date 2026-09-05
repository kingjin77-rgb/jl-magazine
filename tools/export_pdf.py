#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""검토용 PDF — 슬라이드 아래에 페이지 번호 띠를 붙인다.

덱 자체에는 번호를 넣지 않기로 했으므로(사용자 지시), 검토본에만 붙인다.
"12페이지 셋째 줄" 식으로 지적할 수 있어야 검토가 된다.

  python3 tools/export_pdf.py
"""
import glob, io, json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, 'template', 'design', 'preview')
BUILD = os.path.join(ROOT, 'template', 'design', 'build')
FONTS = os.path.join(ROOT, 'assets', 'fonts')
OUT = os.path.join(PREV, 'JL_하자소송_기본제안서_검토본.pdf')

W, H, STRIP = 1332, 750, 34


def titles():
    """빌드 결과에서 각 장의 제목을 뽑아 번호 띠에 함께 적는다."""
    import re
    t = {}
    for p in glob.glob(os.path.join(BUILD, '*.dc.html')):
        s = io.open(p, encoding='utf-8').read()
        m = (re.search(r'<div class="title"[^>]*>(.*?)</div>', s, re.S)
             or re.search(r'<div class="kr"[^>]*>(.*?)</div>', s, re.S))
        if m:
            txt = re.sub(r'<[^>]+>', ' ', m.group(1))
            t[os.path.basename(p).replace('.dc.html', '')] = ' '.join(txt.split())
    return t


def main():
    files = sorted(f for f in glob.glob(os.path.join(PREV, '*.png'))
                   if 'contact' not in os.path.basename(f) and '_bg' not in f)
    tmap = titles()
    font = ImageFont.truetype(os.path.join(FONTS, 'Pretendard-Medium.ttf'), 17)
    bold = ImageFont.truetype(os.path.join(FONTS, 'Pretendard-SemiBold.ttf'), 17)
    pages = []
    for i, f in enumerate(files, 1):
        im = Image.open(f).convert('RGB')
        if im.size != (W, H):
            im = im.resize((W, H), Image.LANCZOS)
        page = Image.new('RGB', (W, H + STRIP), '#FFFFFF')
        page.paste(im, (0, 0))
        d = ImageDraw.Draw(page)
        d.line([(0, H), (W, H)], fill='#C7CBD3', width=1)
        stem = os.path.basename(f).split('_', 1)[1].replace('.png', '')
        title = tmap.get(stem, '')
        if len(title) > 52:
            title = title[:52] + '…'
        d.text((56, H + 9), title, font=font, fill='#5A5F68')
        num = '%d / %d' % (i, len(files))
        w = d.textlength(num, font=bold)
        d.text((W - 56 - w, H + 9), num, font=bold, fill='#0D2162')
        pages.append(page)
    pages[0].save(OUT, save_all=True, append_images=pages[1:], resolution=96.0)
    print('PDF %s · %.1f MB · %d쪽' % (OUT, os.path.getsize(OUT) / 1024 / 1024, len(pages)))


if __name__ == '__main__':
    main()
