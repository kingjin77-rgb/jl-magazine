# -*- coding: utf-8 -*-
"""캔버스 배치를 다시 짠다.

99장을 한 줄로 늘어놓으면(기존) 가로 14만 px라 훑어보기가 어렵다.
간지(D*_Divider)를 기준으로 PART별 페이지를 만들고, 페이지 안에서는
한 줄에 6장씩 격자로 놓는다."""
import io, json, os, re

P = 'template/design/canvas.json'
m = json.load(io.open(P, encoding='utf-8'))
abs_ = m['artboards']

W, H = 1332, 750
GAPX, GAPY, COLS = 140, 260, 6      # 이름 띠와 조절 칩이 프레임 위에 앉는다

# 간지에서 PART 이름을 읽어 페이지를 만든다
def part_name(f):
    s = io.open('template/design/' + f, encoding='utf-8').read()
    pn = re.search(r'<div class="pn">([^<]*)</div>', s)
    kr = re.search(r'<div class="kr">([^<]*)</div>', s)
    a = pn.group(1).strip() if pn else ''
    b = re.sub(r'<br>', ' ', kr.group(1)).strip() if kr else ''
    return ('%s · %s' % (a, b)).strip(' ·')

pages, cur = [], None
groups = []
for a in abs_:
    f = a['file']
    if f.startswith('D') and '_Divider' in f:
        cur = {'id': 'page-%d' % (len(pages) + 1), 'name': part_name(f)}
        pages.append(cur); groups.append([])
    elif cur is None:                     # 간지 앞(표지·요약·목차)
        cur = {'id': 'page-1', 'name': '표지 · 개요'}
        pages.append(cur); groups.append([])
    groups[-1].append(a)

# 페이지 번호를 다시 매기고 좌표를 배치한다
for k, (pg, items) in enumerate(zip(pages, groups), 1):
    pg['id'] = 'page-%d' % k
    for i, a in enumerate(items):
        a['page'] = pg['id']
        a['x'] = (i % COLS) * (W + GAPX)
        a['y'] = (i // COLS) * (H + GAPY)
        a['w'], a['h'] = W, H

m['artboards'] = [a for g in groups for a in g]
m['pages'] = pages
m['launch'] = {'view': 'canvas', 'page': 'page-1'}
m.pop('annotations', None)

json.dump(m, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
for pg, items in zip(pages, groups):
    print('%-9s %-28s %2d장' % (pg['id'], pg['name'], len(items)))
print('총', len(m['artboards']), '장 ·', len(pages), '페이지')
