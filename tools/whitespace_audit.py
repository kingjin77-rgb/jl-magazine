#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""렌더된 슬라이드에서 빈 영역을 측정한다. 눈대중 대신 수치로 잡기 위한 도구."""
import glob, os, sys
from PIL import Image
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'template', 'design', 'preview')

def audit(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im, dtype=np.uint8)
    H, W = a.shape
    # 콘텐츠 영역만 본다 (상단 헤더밴드·하단 푸터 제외)
    body = a[150:H-46, 40:W-40]
    ink = body < 236                      # 흰 바탕이 아닌 화소
    coverage = ink.mean()
    rowink = ink.mean(axis=1)
    blank = rowink < 0.004                # 사실상 비어 있는 행
    # 가장 긴 연속 공백 구간
    best = cur = start = beststart = 0
    for i, b in enumerate(blank):
        if b:
            if cur == 0: start = i
            cur += 1
            if cur > best: best, beststart = cur, start
        else:
            cur = 0
    return coverage, best, beststart + 150

rows = []
for p in sorted(glob.glob(os.path.join(OUT, '*.png'))):
    if 'contact' in p: continue
    cov, gap, at = audit(p)
    rows.append((gap, cov, os.path.basename(p)[:34], at))

rows.sort(reverse=True)
print('%-36s %8s %8s %8s' % ('슬라이드', '최대공백', '잉크율', '위치y'))
print('-' * 64)
for gap, cov, name, at in rows:
    flag = ' ← 과다' if gap >= 120 else ('  주의' if gap >= 80 else '')
    print('%-36s %6dpx %7.1f%% %7d%s' % (name, gap, cov * 100, at, flag))
bad = [r for r in rows if r[0] >= 120]
print('\n공백 120px 이상: %d장 / %d장' % (len(bad), len(rows)))
