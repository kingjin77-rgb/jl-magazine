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
MIN_PX = 13             # 인쇄 하한
GREYS = ('#7F8CA6', '#8289A3', '#9AA3B8', '#A8B0C4', '#888', '#999', '#aaa', '#AAA')

# 간지·표지는 전면 배경이라 본문 top 규칙에서 뺀다
EXEMPT_TOP = re.compile(r'(Main|D\d_Divider)\.dc\.html$')


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
    if EXEMPT_TOP.search(path):
        return None
    # 본문 컨테이너로 쓰이는 절대배치 top 값 중 헤더 바로 아래대(140~210)를 본다
    tops = [int(v) for v in re.findall(r'top:\s*(1[4-9]\d|20\d)px', s)]
    off = sorted({t for t in tops if t != BODY_TOP})
    return off or None


def check_check_marks(path, s):
    body = strip_style(s)
    n = body.count('✓') + body.count('✔')
    return n or None


def check_red_border(path, s):
    # 붉은 박스 테두리 강조는 구식 — 네이비 세로바로 대체
    hits = re.findall(r'border:\s*[0-9.]+px\s+solid\s*(#C0392B|var\(--alert\))', s)
    return len(hits) or None


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

    dups = dup_images()
    print(f"\n═══ 이미지 중복 (내용 기준) ═══")
    if dups:
        for g in dups:
            cnt = {n: used(n, texts.values()) for n in g}
            print("  " + " = ".join(f"{n}({cnt[n]}장)" for n in g))
    else:
        print("  중복 없음")

    print(f"\n요약: 규격 위반 {len(rows)}장 / 이미지 중복 {len(dups)}건")
    return 1 if (rows or dups) else 0


if __name__ == '__main__':
    sys.exit(main())
