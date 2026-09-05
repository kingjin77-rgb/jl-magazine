#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""변호사 프로필 사진의 배경을 통일한다.

원본은 촬영 스튜디오가 제각각이라 배경이 흰색·회색·크림·검정으로 섞여 있다.
배경을 제거하고 브랜드 톤 그라데이션에 다시 올려 6인의 인상을 맞춘다.
원본(assets/lawyers/*)은 건드리지 않고 _normalized/ 에 산출한다.

  python3 tools/normalize_lawyer_photos.py
"""
import glob, os
from PIL import Image
from rembg import remove, new_session

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'lawyers')
NORM = os.path.join(SRC, '_normalized')
DECK = os.path.join(ROOT, 'template', 'design', 'lawyers')

# 파일명 -> 캔버스용 ASCII 이름 (seed-canvas가 한글 파일명을 받지 않는다)
NAMES = {'박종일': 'park-jongil', '오현진': 'oh-hyunjin', '이지훈': 'lee-jihoon',
         '임준규': 'lim-junkyu', '장우진': 'jang-woojin', '하혜용': 'ha-hyeyong'}
TOP, BOTTOM = (0xEF, 0xF2, 0xFB), (0xD4, 0xDD, 0xEE)


def gradient(w, h):
    bg = Image.new('RGB', (w, h))
    px = bg.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return bg


def main():
    os.makedirs(NORM, exist_ok=True)
    os.makedirs(DECK, exist_ok=True)
    sess = new_session('u2net')
    for f in sorted(glob.glob(os.path.join(SRC, '*.png'))
                    + glob.glob(os.path.join(SRC, '*.jpg'))):
        stem = os.path.splitext(os.path.basename(f))[0]
        if stem not in NAMES:
            continue
        cut = remove(Image.open(f).convert('RGBA'), session=sess)
        bg = gradient(*cut.size)
        bg.paste(cut, (0, 0), cut)
        bg.save(os.path.join(NORM, stem + '.jpg'), quality=92)

        # 덱용: 4:5 로 맞추고 300x375 로 통일
        im, (W, H) = bg, bg.size
        if W / H > 0.8:
            nw = int(H * 0.8)
            im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
        else:
            nh = int(W * 1.25)
            top = min(max(0, int(H * 0.02)), max(0, H - nh))
            im = im.crop((0, top, W, top + nh))
        im.resize((300, 375), Image.LANCZOS).save(
            os.path.join(DECK, NAMES[stem] + '.jpg'), quality=84, optimize=True)
        print('통일', stem, '->', NAMES[stem])


if __name__ == '__main__':
    main()
