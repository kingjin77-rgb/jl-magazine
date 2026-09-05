# -*- coding: utf-8 -*-
"""하자 실사 사진을 덱에 쓸 형태로 만든다.

처리: 4:3 크롭 -> 휘도 기준 계조 보정 -> 대비 1.05 -> 언샤프 -> 760px 축소.
채널별 보정은 쓰지 않는다. 한 번 썼더니 콘크리트가 청록색으로 변했다.
합성·업스케일·생성은 하지 않는다. (proposal/13_하자사진_대장.md 참조)

원본은 깃허브에 올리지 않는다(내부자료). 초기화 뒤에는 드라이브에서
다시 받아 /tmp/photos 에 두고 이 스크립트를 돌린다.
"""
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

SRC, DST = '/tmp/photos', 'template/design/photos'

def level(im, lo=0.5, hi=99.5):
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    p1, p2 = np.percentile(lum, [lo, hi])
    if p2 - p1 < 12:
        return im
    return Image.fromarray(np.clip((a - p1) * 255.0 / (p2 - p1), 0, 255).astype(np.uint8))

def crop43(im, vpos=0.5, hpos=0.5, pre=None):
    if pre:                                   # (상, 하) 비율만큼 먼저 잘라낸다
        w, h = im.size
        im = im.crop((0, int(h * pre[0]), w, int(h * (1 - pre[1]))))
    w, h = im.size
    if w / h >= 4 / 3: nh, nw = h, int(round(h * 4 / 3))
    else:              nw, nh = w, int(round(w * 3 / 4))
    x = int(round((w - nw) * hpos)); y = int(round((h - nh) * vpos))
    return im.crop((x, y, x + nw, y + nh))

def make(src, out, vpos=0.5, hpos=0.5, pre=None, crop=True, wide=760):
    im = Image.open(os.path.join(SRC, src)).convert('RGB')
    im = crop43(im, vpos, hpos, pre) if crop else im
    im = level(im)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=95, threshold=3))
    if im.size[0] > wide:
        im = im.resize((wide, int(round(im.size[1] * wide / im.size[0]))), Image.LANCZOS)
    im.save(os.path.join(DST, out), quality=82, subsampling='4:2:0',
            optimize=True, progressive=True)
    print('%-24s %dx%d %4dKB' % (out, im.size[0], im.size[1],
                                 os.path.getsize(os.path.join(DST, out)) // 1024))

os.makedirs(DST, exist_ok=True)

# 도면은 자르지 않는다. 치수와 범례가 잘리면 안 된다.
im = level(Image.open(os.path.join(SRC, 'D01_dwg.jpg')).convert('RGB'), 1.0, 99.0)
im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=2))
# 도면 우하단 표제란에 설계사무소 상호와 기술사 도장이 찍혀 있다.
# 대장에 마스킹 필수로 적어 둔 항목이므로 그 구역만 덮는다.
from PIL import ImageDraw
d = ImageDraw.Draw(im)
w, h = im.size
d.rectangle([int(w * 0.855), int(h * 0.855), w, h], fill=(238, 238, 238))
d.rectangle([int(w * 0.855), int(h * 0.855), w - 1, h - 1], outline=(190, 190, 190))
im.save(os.path.join(DST, 'dwg-heating.jpg'), quality=88, optimize=True, progressive=True)
print('%-24s %dx%d %4dKB · 크롭 없음' % ('dwg-heating.jpg', im.size[0], im.size[1],
      os.path.getsize(os.path.join(DST, 'dwg-heating.jpg')) // 1024))

make('P04.jpg', 'act-heating.jpg')
make('P15.jpg', 'ins-foam.jpg', vpos=0.42)
make('P13.jpg', 'slab-brick.jpg')
make('P08.jpg', 'gal-mold.jpg')
make('P14.jpg', 'gal-insul.jpg')
make('P16.jpg', 'gal-window.jpg', pre=(0.26, 0.0), vpos=1.0)   # 창호 제조사 스티커 제외
make('P01.jpg', 'gal-waterproof.jpg')
# 되메우기 광각은 인접 동·타워크레인이 찍혀 단지가 식별될 수 있다.
# 하늘과 건물이 있는 위쪽을 잘라내고 토사면만 남긴다.
make('P02.jpg', 'gal-backfill.jpg', pre=(0.38, 0.0), vpos=1.0)
make('P12.jpg', 'gal-basement.jpg')
make('P11.jpg', 'gal-floor-insul.jpg')
make('P05.jpg', 'gal-pipe-point.jpg')
make('P17.jpg', 'gal-prefinish.jpg')
make('P20.jpg', 'gal-stain.jpg')
make('P10.jpg', 'gal-opening.jpg')
# 천장 폼 충전은 작업자가 함께 찍혔다. 인물이 들어간 왼쪽을 잘라낸다.
make('P21.jpg', 'gal-foam-work.jpg', hpos=1.0, pre=(0.0, 0.06))
