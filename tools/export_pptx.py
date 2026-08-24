#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""렌더된 슬라이드를 PPTX로 묶는다.

각 장을 16:9 슬라이드에 전면 배치하고, 제목은 편집 가능한 텍스트 상자로
따로 얹는다. 배경 그래픽은 이미지라 PPT에서 다시 그릴 수는 없다.

  python3 tools/export_pptx.py
"""
import glob, os, re, io
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, 'template', 'design', 'preview')
BUILD = os.path.join(ROOT, 'template', 'design', 'build')
OUT = os.path.join(PREV, 'JL_하자소송_기본제안서.pptx')
W, H = Emu(12192000), Emu(6858000)          # 16:9


def titles():
    """빌드 결과에서 슬라이드 제목을 뽑아 텍스트 상자로 얹는다."""
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
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    tmap = titles()
    files = [f for f in sorted(glob.glob(os.path.join(PREV, '*.png')))
             if 'contact' not in f]
    for f in files:
        s = prs.slides.add_slide(prs.slide_layouts[6])       # 빈 레이아웃
        s.shapes.add_picture(f, 0, 0, width=W, height=H)
        stem = re.sub(r'^\d+_', '', os.path.basename(f)).replace('.png', '')
        title = tmap.get(stem)
        if title:
            # 화면에는 안 보이게 두되 편집·검색이 가능하도록 얹는다
            box = s.shapes.add_textbox(Emu(400000), Emu(6300000),
                                       Emu(11000000), Emu(400000))
            tf = box.text_frame
            tf.text = title
            r = tf.paragraphs[0].runs[0]
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        s.notes_slide.notes_text_frame.text = title or stem
    prs.save(OUT)
    print('PPTX', OUT, '%.1f MB · %d장' % (os.path.getsize(OUT) / 1024 / 1024, len(files)))


if __name__ == '__main__':
    main()
