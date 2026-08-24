#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""캔버스 빌드 — 210 옴니고딕을 서브셋해 아트보드에 인라인한 뒤 시드한다.

소스 .dc.html은 base64 없이 깨끗하게 유지하고, 빌드 시점에 폰트를 주입한
사본을 template/design/build/ 에 만든다. 새 단지 텍스트가 들어오면 다시
실행하기만 하면 서브셋이 그 텍스트에 맞춰 갱신된다.

  python3 tools/build_canvas.py            # 빌드만
  python3 tools/build_canvas.py --seed     # 빌드 + seed-canvas 실행
"""
import base64, glob, io, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(ROOT, 'template', 'design')
BUILD = os.path.join(DESIGN, 'build')
FONTS = os.path.join(ROOT, 'assets', 'fonts')

# CSS 굵기 -> 옴니고딕 파일. 5종이 각각 별도 패밀리이고 전부 usWeightClass 400이라
# 이렇게 명시하지 않으면 브라우저가 가짜 볼드를 합성한다.
WEIGHTS = [('400', 'OmniGothic030.ttf'),
           ('600', 'OmniGothic040.ttf'),
           ('700', 'OmniGothic050.ttf')]
FAMILY = 'JL옴니고딕'


def artboards():
    return sorted(glob.glob(os.path.join(DESIGN, '*.dc.html')))


def used_chars():
    """아트보드 본문에서 실제로 쓰인 문자만 모은다 (style/script 제외)."""
    chars = set()
    for p in artboards():
        s = io.open(p, encoding='utf-8').read()
        s = re.sub(r'<style[^>]*>.*?</style>', ' ', s, flags=re.S)
        s = re.sub(r'<script[^>]*>.*?</script>', ' ', s, flags=re.S)
        chars |= set(re.sub(r'<[^>]*>', ' ', s))
    # 가변 슬롯이 어떤 글자로 치환되든 최소한 숫자·영문·기본 문장부호는 보장
    chars |= set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 'abcdefghijklmnopqrstuvwxyz .,·()[]%~/:-')
    return ''.join(sorted(c for c in chars if c.strip()))


def subset(text):
    """굵기별 woff2 서브셋을 만들어 base64로 돌려준다."""
    os.makedirs(BUILD, exist_ok=True)
    txt = os.path.join(BUILD, '_charset.txt')
    io.open(txt, 'w', encoding='utf-8').write(text)
    out = []
    for weight, fname in WEIGHTS:
        src = os.path.join(FONTS, fname)
        dst = os.path.join(BUILD, '_%s.woff2' % weight)
        subprocess.run(['pyftsubset', src, '--text-file=' + txt,
                        '--flavor=woff2', '--output-file=' + dst],
                       check=True, capture_output=True)
        b64 = base64.b64encode(open(dst, 'rb').read()).decode()
        out.append((weight, b64, os.path.getsize(dst)))
        os.remove(dst)
    os.remove(txt)
    return out


def face_block(faces):
    css = []
    for weight, b64, _ in faces:
        css.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
                   "font-display:block;src:url(data:font/woff2;base64,%s) format('woff2');}"
                   % (FAMILY, weight, b64))
    return '\n'.join(css)


def build():
    text = used_chars()
    faces = subset(text)
    total = sum(sz for _, _, sz in faces)
    print('서브셋 문자 %d자 · woff2 %.1f KB (%s)'
          % (len(text), total / 1024,
             ', '.join('%s=%.1fKB' % (w, sz / 1024) for w, _, sz in faces)))

    block = face_block(faces)
    os.makedirs(BUILD, exist_ok=True)
    for p in artboards():
        s = io.open(p, encoding='utf-8').read()
        # 본문 폰트 스택을 옴니고딕 우선으로 교체
        s = s.replace('"Pretendard","Malgun Gothic",sans-serif',
                      "'%s','Pretendard','Malgun Gothic',sans-serif" % FAMILY)
        # SVG 등에 남은 구 패밀리 지정도 통일
        s = re.sub(r"'210 옴니고딕 0[1-5]0'", "'%s'" % FAMILY, s)
        # @font-face를 style 맨 앞에 주입
        s = s.replace('<style>', '<style>\n' + block + '\n', 1)
        io.open(os.path.join(BUILD, os.path.basename(p)), 'w',
                encoding='utf-8').write(s)

    # 이미지는 build 루트에 평면으로 복사한다. .dc.html이 파일명만으로
    # 참조하므로 캔버스(files 키 = 파일명)와 로컬 프리뷰 렌더가 모두 맞는다.
    for sub in ('graphics', 'lawyers'):
        for f in glob.glob(os.path.join(DESIGN, sub, '*')):
            shutil.copy(f, os.path.join(BUILD, os.path.basename(f)))
    for f in ('cover-photo.jpg', 'jl-logo.png', 'canvas.json'):
        shutil.copy(os.path.join(DESIGN, f), os.path.join(BUILD, f))

    biggest = max(glob.glob(os.path.join(BUILD, '*.dc.html')), key=os.path.getsize)
    print('아트보드 %d개 · 최대 %s %.0f KB (항목 상한 2MB)'
          % (len(artboards()), os.path.basename(biggest),
             os.path.getsize(biggest) / 1024))
    return BUILD


SKILL = ('/tmp/claude-0/bundled-skills/2.1.236/'
         'f2e9088448f5b996ffd8d0644f6b57c0/design')


def seed():
    boards = sorted(glob.glob(os.path.join(BUILD, '*.dc.html')),
                    key=lambda p: (os.path.basename(p) != 'Main.dc.html',
                                   os.path.basename(p)))
    imgs = sorted(glob.glob(os.path.join(BUILD, '*.jpg'))
                  + glob.glob(os.path.join(BUILD, '*.png')))
    cmd = ['node', os.path.join(SKILL, 'seed-canvas.mjs'),
           '--template', os.path.join(SKILL, 'payload.template.html'),
           '--out', 'jl-hazard-litigation-proposal-full.html',
           '--title', '법무법인 제이엘 하자소송 기본제안서']
    for b in boards:
        cmd += ['--artboard', os.path.relpath(b, BUILD)]
    for i in imgs:
        cmd += ['--image', os.path.relpath(i, BUILD)]
    cmd += ['--canvas', 'canvas.json']
    r = subprocess.run(cmd, cwd=BUILD, capture_output=True, text=True)
    sys.stderr.write(r.stderr)
    print(r.stdout.strip()[:120])
    if r.returncode:
        sys.exit(r.returncode)
    out = os.path.join(BUILD, 'jl-hazard-litigation-proposal-full.html')
    shutil.copy(out, os.path.join(DESIGN, 'jl-hazard-litigation-proposal-full.html'))
    print('시드 완료 %.2f MB (페이지 상한 16MB)' % (os.path.getsize(out) / 1024 / 1024))


if __name__ == '__main__':
    build()
    if '--seed' in sys.argv:
        seed()
