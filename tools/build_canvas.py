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
# 사용자 요청으로 서체를 210 옴니고딕으로 통일한다.
# 다만 본문까지 050(굵은 제목용)을 쓰면 14px에서 획이 뭉치므로
# 제목·숫자는 050, 본문은 030/040을 써서 같은 가족 안에서 굵기만 나눈다.
DISPLAY = 'JL디스플레이'
TEXT = 'JL본문'
# 사용자 지정 서체 — 지마켓 산스. 굵은 인상을 위해 제목은 Bold,
# 본문은 Medium을 쓴다(Light는 회색처럼 흐려 보여 쓰지 않는다).
FACES = [(DISPLAY, '400', 'GmarketSansBold.ttf'),
         (DISPLAY, '700', 'GmarketSansBold.ttf'),
         (DISPLAY, '800', 'GmarketSansBold.ttf'),
         (TEXT,    '400', 'GmarketSansMedium.ttf'),
         (TEXT,    '600', 'GmarketSansBold.ttf'),
         (TEXT,    '700', 'GmarketSansBold.ttf'),
         (TEXT,    '800', 'GmarketSansBold.ttf')]
FAMILY = TEXT


def artboards():
    return sorted(glob.glob(os.path.join(DESIGN, '*.dc.html')))


def used_chars(where=None):
    """아트보드 본문에서 실제로 쓰인 문자만 모은다 (style/script 제외)."""
    chars = set()
    src = (sorted(glob.glob(os.path.join(where, '*.dc.html'))) if where
           else artboards())
    for p in src:
        s = io.open(p, encoding='utf-8').read()
        s = re.sub(r'<style[^>]*>.*?</style>', ' ', s, flags=re.S)
        s = re.sub(r'<script[^>]*>.*?</script>', ' ', s, flags=re.S)
        chars |= set(re.sub(r'<[^>]*>', ' ', s))
    # 가변 슬롯이 어떤 글자로 치환되든 최소한 숫자·영문·기본 문장부호는 보장
    chars |= set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 'abcdefghijklmnopqrstuvwxyz .,·()[]%~/:-')
    return ''.join(sorted(c for c in chars if c.strip()))


def canvas_order():
    """canvas.json에 적힌 아트보드 순서를 1부터 매긴 표로 돌려준다."""
    path = os.path.join(DESIGN, 'canvas.json')
    if not os.path.exists(path):
        return {}
    import json
    m = json.load(io.open(path, encoding='utf-8'))
    return {a['file']: i + 1 for i, a in enumerate(m.get('artboards', []))
            if isinstance(a, dict) and 'file' in a}


def subset(text):
    """서체별 woff2 서브셋을 만들어 base64로 돌려준다. 같은 파일은 한 번만."""
    os.makedirs(BUILD, exist_ok=True)
    txt = os.path.join(BUILD, '_charset.txt')
    io.open(txt, 'w', encoding='utf-8').write(text)
    cache = {}
    out = []
    for fam, weight, fname in FACES:
        if fname not in cache:
            dst = os.path.join(BUILD, '_%s.woff2' % fname)
            subprocess.run(['pyftsubset', os.path.join(FONTS, fname),
                            '--text-file=' + txt, '--flavor=woff2',
                            '--output-file=' + dst], check=True, capture_output=True)
            cache[fname] = (base64.b64encode(open(dst, 'rb').read()).decode(),
                            os.path.getsize(dst))
            os.remove(dst)
        b64, sz = cache[fname]
        out.append((fam, weight, b64, fname, sz))
    os.remove(txt)
    return out


def face_block(faces):
    css = [("@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
            "font-display:block;src:url(data:font/woff2;base64,%s) format('woff2');}"
            % (fam, weight, b64)) for fam, weight, b64, _, _ in faces]
    # 제목과 숫자만 브랜드 서체로. 나머지는 본문 서체가 받는다.
    css.append(".title,.n{font-family:'%s','%s',sans-serif !important;}" % (DISPLAY, TEXT))
    return '\n'.join(css)


def build():
    stage()                       # 사본 생성 + 슬롯 채움
    text = used_chars(BUILD)      # 채워진 결과에서 문자셋을 뽑는다
    faces = subset(text)
    uniq = {fn: sz for _, _, _, fn, sz in faces}
    print('서브셋 문자 %d자 · woff2 %.1f KB (%s)'
          % (len(text), sum(uniq.values()) / 1024,
             ', '.join('%s=%.1fKB' % (fn.split('.')[0], sz / 1024)
                       for fn, sz in uniq.items())))

    block = face_block(faces)
    for p in sorted(glob.glob(os.path.join(BUILD, '*.dc.html'))):
        s = io.open(p, encoding='utf-8').read()
        s = s.replace('<style>', '<style>\n' + block + '\n', 1)
        io.open(p, 'w', encoding='utf-8').write(s)

    uniq = {fn: sz for _, _, _, fn, sz in faces}
    print('서브셋 문자 %d자 · woff2 %.1f KB (%s)'
          % (len(text), sum(uniq.values()) / 1024,
             ', '.join('%s=%.1fKB' % (fn.split('.')[0], sz / 1024)
                       for fn, sz in uniq.items())))
    biggest = max(glob.glob(os.path.join(BUILD, '*.dc.html')), key=os.path.getsize)
    print('아트보드 %d개 · 최대 %s %.0f KB (항목 상한 2MB)'
          % (len(artboards()), os.path.basename(biggest),
             os.path.getsize(biggest) / 1024))
    return BUILD


def stage():
    """소스를 build/ 로 복사하고 페이지 번호 부여 + 슬롯 채움까지 한다."""
    os.makedirs(BUILD, exist_ok=True)
    order = canvas_order()
    total = len(order)
    for p in artboards():
        s = io.open(p, encoding='utf-8').read()
        # 페이지 번호는 canvas.json 순서로 빌드 때 부여한다.
        # 장수가 바뀌어도 각 슬라이드를 고칠 필요가 없다.
        # 슬라이드 번호는 표기하지 않는다(사용자 요청). canvas 순서만 유지한다.
        # 본문 폰트 스택을 옴니고딕 우선으로 교체
        s = s.replace('"Pretendard","Malgun Gothic",sans-serif',
                      "'%s','Pretendard','Malgun Gothic',sans-serif" % FAMILY)
        # SVG 등에 남은 구 패밀리 지정도 통일
        s = re.sub(r"'210 옴니고딕 0[1-5]0'", "'%s'" % FAMILY, s)
        # @font-face를 style 맨 앞에 주입
        io.open(os.path.join(BUILD, os.path.basename(p)), 'w',
                encoding='utf-8').write(s)

    # 이미지는 build 루트에 평면으로 복사한다. .dc.html이 파일명만으로
    # 참조하므로 캔버스(files 키 = 파일명)와 로컬 프리뷰 렌더가 모두 맞는다.
    for sub in ('graphics', 'lawyers', 'photos'):
        for f in glob.glob(os.path.join(DESIGN, sub, '*')):
            shutil.copy(f, os.path.join(BUILD, os.path.basename(f)))
    for f in (glob.glob(os.path.join(DESIGN, '*.jpg'))
              + glob.glob(os.path.join(DESIGN, '*.png'))
              + [os.path.join(DESIGN, 'canvas.json')]):
        shutil.copy(f, os.path.join(BUILD, os.path.basename(f)))

    # 단지 데이터가 있으면 {{슬롯}}을 채운다 (기본제안서 -> 단지별 제안서)
    data = os.environ.get('JL_DATA') or os.path.join(ROOT, 'template', 'data',
                                                     '_example_이스트힐.json')
    if os.path.exists(data):
        subprocess.run(['python3', os.path.join(ROOT, 'tools', 'fill_complex.py'),
                        data, '--dir', BUILD], check=False)

    biggest = max(glob.glob(os.path.join(BUILD, '*.dc.html')), key=os.path.getsize)
    print('아트보드 %d개 · 최대 %s %.0f KB (항목 상한 2MB)'
          % (len(artboards()), os.path.basename(biggest),
             os.path.getsize(biggest) / 1024))
    return BUILD


SKILL = next(iter(sorted(glob.glob(
    '/tmp/claude-0/bundled-skills/*/*/design/seed-canvas.mjs'),
    key=os.path.getmtime, reverse=True)), '')
SKILL = os.path.dirname(SKILL)


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


def build_slim():
    """캔버스 시드용. 서체를 장마다 그 장 글자만 서브셋해 넣는다.

    기본 빌드는 FACES 7줄을 모두 넣어 같은 base64가 파일마다 5~7번 반복된다
    (장당 768KB · 99장이면 76MB로 페이지 상한 16MB를 넘는다).
    여기서는 장별 서브셋 + @font-face 2줄로 줄인다."""
    stage()
    os.makedirs(BUILD, exist_ok=True)
    txt = os.path.join(BUILD, '_charset.txt')
    tot = 0
    for p in sorted(glob.glob(os.path.join(BUILD, '*.dc.html'))):
        s = io.open(p, encoding='utf-8').read()
        body = re.sub(r'<style[^>]*>.*?</style>', ' ', s, flags=re.S)
        body = re.sub(r'<script[^>]*>.*?</script>', ' ', body, flags=re.S)
        chars = set(re.sub(r'<[^>]*>', ' ', body))
        chars |= set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                     'abcdefghijklmnopqrstuvwxyz .,·()[]%~/:-')
        io.open(txt, 'w', encoding='utf-8').write(
            ''.join(sorted(c for c in chars if c.strip())))
        css = []
        for weight, fname in (('400', 'GmarketSansMedium.ttf'),
                              ('700', 'GmarketSansBold.ttf')):
            dst = os.path.join(BUILD, '_slim.woff2')
            subprocess.run(['pyftsubset', os.path.join(FONTS, fname),
                            '--text-file=' + txt, '--flavor=woff2',
                            '--output-file=' + dst], check=True, capture_output=True)
            b64 = base64.b64encode(open(dst, 'rb').read()).decode()
            tot += os.path.getsize(dst)
            os.remove(dst)
            css.append("@font-face{font-family:'%s';font-style:normal;"
                       "font-weight:%s;font-display:block;"
                       "src:url(data:font/woff2;base64,%s) format('woff2');}"
                       % (FAMILY, weight, b64))
        css.append(".title,.n{font-family:'%s',sans-serif !important;}" % FAMILY)
        s = s.replace('<style>', '<style>\n' + '\n'.join(css) + '\n', 1)
        io.open(p, 'w', encoding='utf-8').write(s)
    if os.path.exists(txt):
        os.remove(txt)

    # 캔버스에 실리는 사진은 base64로 문서에 통째로 들어간다.
    # 저장할 때마다 문서 전체가 다시 올라가므로 캔버스 사본만 줄인다.
    # (PDF·PPTX가 쓰는 template/design/photos 원본은 건드리지 않는다)
    from PIL import Image
    for q in sorted(glob.glob(os.path.join(BUILD, '*.jpg'))):
        im = Image.open(q)
        if im.size[0] > 640:
            im = im.convert('RGB').resize(
                (640, int(round(im.size[1] * 640 / im.size[0]))), Image.LANCZOS)
        im.save(q, quality=76, subsampling='4:2:0', optimize=True, progressive=True)
    big = max(glob.glob(os.path.join(BUILD, '*.dc.html')), key=os.path.getsize)
    print('슬림 빌드 · 서체 합계 %.1f KB · 최대 아트보드 %s %.0f KB'
          % (tot / 1024, os.path.basename(big), os.path.getsize(big) / 1024))
    return BUILD

if __name__ == '__main__':
    if '--slim' in sys.argv:
        build_slim()
    else:
        build()
    if '--seed' in sys.argv:
        seed()
