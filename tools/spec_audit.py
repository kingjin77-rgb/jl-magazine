#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""규격서(proposal/15_슬라이드_규격서.md) 위반을 전수 검출한다.

감으로 고치면 고칠 때마다 다른 장과 어긋난다. 숫자로 검사한다.
"""
import glob, hashlib, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'template', 'design')

BODY_TOP = 186          # 본문 시작 통일값
MIN_PX = 15             # 인쇄 하한 (2026-09-08 사용자 지시)
GREYS = ('#7F8CA6', '#8289A3', '#9AA3B8', '#A8B0C4', '#888', '#999', '#aaa', '#AAA')

# 간지·표지는 전면 배경이라 본문 top 규칙에서 뺀다
EXEMPT_TOP = re.compile(r'(_Cover|Part\dDivider)\.dc\.html$')


def slides():
    fs = sorted(glob.glob(os.path.join(D, '*.dc.html')))
    return [f for f in fs if not os.path.basename(f).startswith('_')]


def strip_style(s):
    return re.sub(r'<style>.*?</style>', '', s, flags=re.S)


def check_font_size(path, s):
    bad = []
    for m in re.finditer(r'font-size:\s*([0-9.]+)px', s):
        v = float(m.group(1))
        if v < MIN_PX:
            bad.append(v)
    return sorted(set(bad))


def check_grey(path, s):
    return sorted({g for g in GREYS if g.lower() in s.lower()})


def check_body_top(path, s):
    """헤더 금선 아래로 내려오지 않은 본문 블록을 찾는다.

    body::before(밴드)와 body::after(금선)는 골격이므로 제외한다.
    이 둘을 세면 금선의 top:160이 본문 위반으로 잡히는 오탐이 난다.
    """
    if EXEMPT_TOP.search(path):
        return None
    m = re.search(r'body::before\{[^}]*height:(\d+)px', s)
    if not m:
        return None
    gold_end = int(m.group(1)) + 4
    bad = []
    for r in re.finditer(r'([.#][\w.\- >]+)\{([^}]*)\}', s):
        sel, decl = r.group(1).strip(), r.group(2)
        if 'position:absolute' not in decl:
            continue
        t = re.search(r'(?<![\w-])top:\s*(\d+)px', decl)
        if t and 100 <= int(t.group(1)) < gold_end:
            bad.append(f"{sel}@{t.group(1)}")
    return bad or None


def check_check_marks(path, s):
    body = strip_style(s)
    n = body.count('✓') + body.count('✔')
    return n or None


def check_red_border(path, s):
    # 붉은 박스 테두리 강조는 구식 — 네이비 세로바로 대체
    hits = re.findall(r'border:\s*[0-9.]+px\s+solid\s*(#C0392B|var\(--alert\))', s)
    return len(hits) or None


def check_bullets(path, s):
    """단순 나열용 점 불릿 금지 — 박스·배지·화살표로."""
    body = strip_style(s)
    n = len(re.findall(r'>\s*[•▪]\s', body))  # 문장 안 구분점(·)은 제외
    return n or None


LAYOUT_KEYS = [('flow', 'flow'), ('tbl', 'table'), ('table', 'table'), ('cards', 'cards'),
               ('kv', 'kv'), ('gal', 'gallery'), ('duo', 'gallery'), ('verify', 'verify')]


def layout_kind(s):
    body = strip_style(s)
    counts = {}
    for cls, kind in LAYOUT_KEYS:
        c = len(re.findall(r'class="[^"]*\b%s\b' % cls, body))
        if c:
            counts[kind] = counts.get(kind, 0) + c
    return max(counts, key=counts.get) if counts else None


def check_rhythm(texts):
    """덱 순서로 연속 두 장이 같은 지배 구조면 리듬 위반."""
    import json
    cj = os.path.join(D, 'canvas.json')
    order = [a['file'] for a in json.load(open(cj, encoding='utf-8'))['artboards']] if os.path.exists(cj) else []
    prev = None; hits = []
    for f in order:
        p = os.path.join(D, f)
        if p not in texts or re.search(r'(Cover|Divider)', f):
            prev = None; continue
        k = layout_kind(texts[p])
        if k and prev and k == prev[1] and k != 'verify':
            hits.append((prev[0], f, k))
        prev = (f, k)
    return hits


def dup_images():
    """파일명이 달라도 내용이 같으면 중복이다."""
    try:
        from PIL import Image
    except ImportError:
        return []
    h = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(D, 'photos', '*.jpg'))
                    + glob.glob(os.path.join(D, 'photos', '*.png'))):
        try:
            im = Image.open(f).convert('L').resize((16, 16))
            h[hashlib.md5(im.tobytes()).hexdigest()].append(os.path.basename(f))
        except Exception:
            pass
    return [v for v in h.values() if len(v) > 1]


def used(name, texts):
    return sum(1 for t in texts if name in t)


def main():
    fs = slides()
    texts = {f: open(f, encoding='utf-8').read() for f in fs}
    rows = []
    for f, s in texts.items():
        b = os.path.basename(f).replace('.dc.html', '')
        issues = []
        v = check_font_size(f, s)
        if v:
            issues.append(f"작은 글자 {v}px")
        v = check_grey(f, s)
        if v:
            issues.append(f"회색 글씨 {','.join(v)}")
        v = check_body_top(f, s)
        if v:
            issues.append(f"본문 top {v} (규격 {BODY_TOP})")
        v = check_check_marks(f, s)
        if v:
            issues.append(f"체크표시 {v}개")
        v = check_red_border(f, s)
        if v:
            issues.append(f"붉은 테두리 {v}곳")
        v = check_bullets(f, s)
        if v:
            issues.append(f"점 불릿 {v}개")
        if issues:
            rows.append((b, issues))

    print(f"═══ 규격 검사 · 슬라이드 {len(fs)}장 ═══\n")
    if rows:
        for b, iss in rows:
            print(f"  {b}")
            for i in iss:
                print(f"      - {i}")
    else:
        print("  위반 없음")

    rh = check_rhythm(texts)
    print(f"\n═══ 리듬 · 연속 동일 구조 ═══")
    for a, b, k in rh:
        print(f"  {a.replace('.dc.html','')} → {b.replace('.dc.html','')}  ({k})")
    if not rh:
        print("  없음")

    dups = dup_images()
    print(f"\n═══ 이미지 중복 (내용 기준) ═══")
    if dups:
        for g in dups:
            cnt = {n: used(n, texts.values()) for n in g}
            print("  " + " = ".join(f"{n}({cnt[n]}장)" for n in g))
    else:
        print("  중복 없음")

    print(f"\n요약: 규격 위반 {len(rows)}장 / 리듬 {len(rh)}곳 / 이미지 중복 {len(dups)}건")
    return 1 if (rows or dups) else 0


if __name__ == '__main__':
    sys.exit(main())
