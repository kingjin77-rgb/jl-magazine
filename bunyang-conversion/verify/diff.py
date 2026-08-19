import re, unicodedata, sys
def norm(s):
    s = unicodedata.normalize('NFKC', s).replace('Ｌ','L').replace('㎡','m2').replace('m²','m2')
    return re.sub(r'[\s,.\-–—·ㆍ:：/()（）\[\]"\'’‘“”%％+=*×÷~〜&]', '', s).lower()
orig = [l.strip() for l in open('original-text.txt', encoding='utf-8') if l.strip()]
mine = norm(open('mine-text.txt', encoding='utf-8').read())
ok = partial = 0; missing = []
for line in orig:
    n = norm(line)
    if len(n) < 3: continue
    if n in mine: ok += 1; continue
    toks = [norm(w) for w in re.split(r'[\s,·ㆍ()]+', line) if len(norm(w)) >= 2]
    if not toks: ok += 1; continue
    r = sum(1 for t in toks if t in mine) / len(toks)
    if r >= .85: ok += 1
    elif r >= .5: partial += 1
    else: missing.append((round(r,2), line))
print(f"원본 {ok+partial+len(missing)}줄 — 완전 {ok} · 부분 {partial} · 미반영 {len(missing)}")
for r, l in missing: print(f"  [{r:.2f}] {l[:95]}")
