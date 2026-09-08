#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""canvas.json에 아트보드를 끼워 넣고 좌표·번호를 다시 매긴다.

  python3 tools/canvas_insert.py <넣을파일> after <기준파일> "표시제목"
"""
import io, json, os, re, sys

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'template', 'design', 'canvas.json')


def load():
    return json.load(io.open(P, encoding='utf-8'))


def renumber(m):
    for k, a in enumerate(m['artboards']):
        a['x'], a['y'] = k * 1452, 0
        a['title'] = '%02d %s' % (k + 1, re.sub(r'^\d+\s+', '', a.get('title', '')))
    return m


def insert(new, anchor, title):
    m = load(); ab = m['artboards']
    if any(a['file'] == new for a in ab):
        print('이미 있음', new); return
    i = next(k for k, a in enumerate(ab) if a['file'] == anchor)
    ab.insert(i + 1, {'file': new, 'x': 0, 'y': 0, 'w': 1332, 'h': 750, 'title': title})
    json.dump(renumber(m), io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('+ %s (%s 뒤) · 총 %d장' % (new, anchor, len(ab)))


if __name__ == '__main__':
    insert(sys.argv[1], sys.argv[3], sys.argv[4])
