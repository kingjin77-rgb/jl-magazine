#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""빌드된 아트보드를 1332x750 PNG로 캡처하고 컨택트시트를 만든다."""
import glob, os, subprocess, sys, shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'template', 'design', 'build')
OUT = os.path.join(ROOT, 'template', 'design', 'preview')
CHROME = (glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') or [None])[0]


def capture():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(BUILD, '*.dc.html')),
                   key=lambda p: (os.path.basename(p) != 'Main.dc.html',
                                  os.path.basename(p)))
    for i, f in enumerate(files):
        name = os.path.basename(f).replace('.dc.html', '')
        png = os.path.join(OUT, '%02d_%s.png' % (i + 1, name))
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                        '--hide-scrollbars', '--force-device-scale-factor=1',
                        '--window-size=1332,920',
                        '--screenshot=' + png, '--virtual-time-budget=3000',
                        '--user-data-dir=/tmp/cr-%d' % i,
                        'file://' + f], capture_output=True)
        shutil.rmtree('/tmp/cr-%d' % i, ignore_errors=True)
        # 크로미움 헤드리스가 뷰포트 하단 근처 요소를 그리지 않는 문제가 있어
        # 920으로 잡아 캡처한 뒤 750으로 잘라낸다.
        if os.path.exists(png):
            im = Image.open(png)
            if im.height > 750:
                im.crop((0, 0, 1332, 750)).save(png)
    made = sorted(glob.glob(os.path.join(OUT, '*.png')))
    print('캡처 %d장' % len(made))
    return made


def contact_sheet(files, cols=4, tw=560):
    th = int(tw * 750 / 1332)
    rows = (len(files) + cols - 1) // cols
    pad, lab = 12, 22
    W = cols * (tw + pad) + pad
    H = rows * (th + pad + lab) + pad
    sheet = Image.new('RGB', (W, H), '#E8EAEE')
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS)
        r, c = divmod(i, cols)
        sheet.paste(im, (pad + c * (tw + pad), pad + r * (th + pad + lab)))
    out = os.path.join(OUT, '_contact_sheet.png')
    sheet.save(out)
    print('컨택트시트', out, sheet.size)
    return out


if __name__ == '__main__':
    if not CHROME:
        sys.exit('크로미움을 찾지 못했다')
    contact_sheet(capture())
