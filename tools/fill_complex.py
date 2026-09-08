#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""단지 JSON의 값으로 슬라이드의 {{슬롯}}을 채운다.

기본제안서의 핵심. 고정 슬라이드는 그대로 두고 가변 슬라이드의 슬롯만
치환한다. 값이 없는 슬롯은 '[자료 미제출]'로 남겨 빈칸을 숨기지 않는다.

  python3 tools/fill_complex.py template/data/<단지>.json --dir template/design/build
"""
import argparse, glob, io, json, os, re

MISSING = '[자료 미제출]'


def flatten(data):
    """슬롯 이름 -> 값. 중첩 dict는 키 이름 그대로 평탄화한다."""
    v = {}
    for k, val in data.items():
        if k.startswith('_'):
            continue
        if isinstance(val, dict):
            for k2, v2 in val.items():
                v[k2] = v2
                v['%s_%s' % (k, k2)] = v2
        elif not isinstance(val, list):
            v[k] = val

    # 하자 접수 집계
    agg = data.get('하자접수집계') or {}
    for name, cnt in (agg.get('유형별') or {}).items():
        v['%s_건수' % name.split('·')[0].replace(' ', '')] = '{:,}'.format(cnt)
    for dong, cnt in (agg.get('동별') or {}).items():
        v[dong] = '{:,}'.format(cnt)

    # 미이행 이력 (최대 4행 + 흐름 4단계)
    hist = data.get('하자보수요청이력') or []
    for i, row in enumerate(hist[:4], start=1):
        v['일자%d' % i] = row.get('일자', MISSING)
        v['내용%d' % i] = row.get('내용', MISSING)
    if len(hist) >= 1: v['공문1_일자'] = hist[0].get('일자', MISSING)
    if len(hist) >= 2: v['회신1_일자'] = hist[1].get('일자', MISSING)
    if len(hist) >= 3: v['공문2_일자'] = hist[2].get('일자', MISSING)
    if len(hist) >= 4: v['현재'] = hist[3].get('일자', MISSING)

    # 광고 대비 시공
    ad = data.get('광고대비시공') or {}
    v['공고문_인용문'] = ad.get('인용문', MISSING)
    v['공고문_출처_면수'] = ad.get('출처_면수', MISSING)
    v['실측_대조_내용'] = ad.get('대조_내용', MISSING)
    v['실측_확인일'] = ad.get('확인일', MISSING)

    for k in ('총세대수', '동수'):
        if isinstance(v.get(k), int):
            v[k] = '{:,}'.format(v[k])
    return v


def fill(text, values, used):
    def sub(m):
        key = m.group(1).strip()
        used.add(key)
        val = values.get(key)
        return MISSING if val in (None, '') else str(val)
    return re.sub(r'\{\{([^}]+)\}\}', sub, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data')
    ap.add_argument('--dir', default='template/design/build')
    a = ap.parse_args()
    values = flatten(json.load(io.open(a.data, encoding='utf-8')))
    used, filled, missing = set(), 0, set()
    for p in sorted(glob.glob(os.path.join(a.dir, '*.dc.html'))):
        s = io.open(p, encoding='utf-8').read()
        if '{{' not in s:
            continue
        out = fill(s, values, used)
        io.open(p, 'w', encoding='utf-8').write(out)
        filled += 1
    missing = {k for k in used if values.get(k) in (None, '')}
    print('슬롯 채움: %d개 슬라이드 · 슬롯 %d종' % (filled, len(used)))
    if missing:
        print('값 없음(미제출로 표기): %s' % ', '.join(sorted(missing)))


if __name__ == '__main__':
    main()
