#!/usr/bin/env python3
"""블로그 본문 삽입용 정보 카드(1080×1080 PNG)를 생성한다.

사진이 아니라 본문 내용을 그대로 조판한 카드다. 이미지 생성 모델은
한글 자형을 정확히 그리지 못하므로, 텍스트는 브라우저로 렌더링해
캡처한다. 숫자와 인용은 모두 2026.8.13 정부 발표 원문에서 온 것이다.

사용법:  python3 tools/make_cards.py [출력 디렉터리]
"""
import json, os, subprocess, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else 'docs/images'
CHROME = '/opt/pw-browsers/chromium'
SIZE = 1080
SCALE = 2  # 2160×2160으로 출력해 모바일에서도 또렷하게

# ── 카드 내용 ───────────────────────────────────────────────
def cover(label, title, sub):
    return dict(kind='cover', label=label, title=title, body=f'<p class="sub">{sub}</p>')

def card(label, title, body, foot=''):
    return dict(kind='card', label=label, title=title, body=body, foot=foot)

def table(rows, head=None, wide=False):
    h = '<thead><tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr></thead>' if head else ''
    b = '<tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody>'
    return f'<table class="{"w" if wide else ""}">{h}{b}</table>'

def points(items):
    return '<ol class="pts">' + ''.join(f'<li>{t}</li>' for t in items) + '</ol>'

def bullets(items):
    return '<ul class="bul">' + ''.join(f'<li>{t}</li>' for t in items) + '</ul>'

def arrow(before, after, cap=''):
    return (f'<div class="arw"><div class="b"><span>현행</span><b>{before}</b></div>'
            f'<div class="ar">→</div><div class="a"><span>개선</span><b>{after}</b></div></div>'
            + (f'<p class="cap">{cap}</p>' if cap else ''))

def big(n, unit, cap):
    return f'<div class="big"><b>{n}</b><span>{unit}</span></div><p class="cap">{cap}</p>'

BLOG1 = [
    cover('①편 · 공급·정비',
          '8·13 대책,<br>재개발·빌라·택지에서<br>실제로 달라지는 것',
          '정부 발표 원문 107면을 읽고 정리했습니다'),
    card('01 · 가장 먼저', '발표와 시행은 다릅니다',
         table([['내규·내부방침', '정부·공공기관', '낮음'],
                ['행정지도·시행세칙', '금융당국', '낮음'],
                ['시행령·시행규칙', '정부', '중간'],
                ['<b>법률 개정</b>', '<b>국회</b>', '<b class="r">높음</b>']],
               ['조치 유형', '누가 결정하나', '불확실성']),
         '조치사항이 “법률 개정”이면 국회 통과 전까지 시행일을 특정할 수 없습니다'),
    card('02 · 오해 정정', '지금 시점에서<br>동의율은 여전히 75%입니다',
         big('75', '%', '재개발 조합설립 동의율 (현행 유지)')
         + '<p class="note">동의율 70% 완화는 <b>도시정비법 개정 사항</b>입니다.<br>'
           '정부는 개정안을 <b>2026년 9월 발의</b>하겠다고 밝혔습니다.<br>'
           '현금청산 취득세 감면, 외부 전문가 조합장, 중재위원회도 같습니다.</p>'),
    card('03 · 정비사업', '인센티브에는<br>날짜 조건이 두 개씩 있습니다',
         table([['현금청산 취득세', '2027년 면제<br>2028년 75% 감면', '발표일 후 관리처분인가<br>+ 취득일부터 2년 내 착공'],
                ['임대주택 인수가격', '기본형건축비<br>80% → 100%', '발표일 후 관리처분인가<br>+ 2028년 내 착공'],
                ['기부채납 공원·녹지', '3 → 2㎡/세대', '소형 2/3 이상 + 1천세대 이상<br>+ 5년 내 사업시행인가 신청']],
               ['항목', '내용', '조건'], wide=True),
         '이미 관리처분인가를 받은 사업장은 일부 항목에서 대상 밖입니다'),
    card('04 · 8월 31일 시행', '이주비 대출 담보가치<br>산정 기준이 바뀝니다',
         arrow('종전자산평가액', '종전·종후 중<br>큰 금액',
               '종후자산은 신축 후 가치라 통상 종전보다 큽니다 → 같은 LTV 40%라도 한도 상승')
         + '<p class="note">함께 시행 · <b>추가 이주비대출 보증상품</b> 신설(2027.1)<br>'
           '<b>이주비·중도금·잔금대출 총량 별도 관리</b>(2026 하반기)</p>'),
    card('05 · 동의율', '반대하는 분의 지위가<br>직접 바뀝니다',
         table([['조합설립 동의율', '75%', '<b class="r">70%</b>'],
                ['공공 시행자 지정', '67%', '<b class="r">60%</b>'],
                ['반대 측 저지선', '25%', '<b class="r">30%</b>'],
                ['조합설립인가 전 통지기한', '60일', '<b class="r">30일</b>']],
               ['구분', '현행', '개선안']),
         '토지면적 요건 50%는 그대로 · 도시정비법 개정 사항'),
    card('06 · 비아파트', '빌라 건축기준 3종<br>일조 규제만 국회를 통과했습니다',
         table([['건축면적', '660㎡ → 1,000㎡ 미만', '시행령 · 2026.12'],
                ['다가구 층수', '3개층 → 4개층', '시행령 · 2026.12'],
                ['<b>일조 규제</b>', '<b>10~17m 구간 5m 고정</b>', '<b class="r">법 통과 · 연내 시행</b>']],
               ['항목', '내용', '시행'], wide=True),
         '다가구 4개층 허용 시 같은 면적에 가구를 약 33% 더 공급할 수 있습니다'),
    card('07 · 신규 택지', '입지가 공개된 세 곳',
         table([['서울 강서 염창동', '5.1만㎡', '1,000호', '2029년 착공'],
                ['경기 남양주 와부읍', '228만㎡', '21,700호', '2030년 상반기'],
                ['경기 광주 장지동', '48만㎡', '4,500호', '2030년 상반기']],
               ['지구', '면적', '세대수', '착공'], wide=True),
         '남양주는 고려대 덕소농장 일대 그린벨트 · 7.3만호+α는 연내 추가 발표'),
    card('08 · 보상', '가장 크게 줄인 구간은<br>보상 단계입니다',
         arrow('44개월', '24개월', '부지확보(보상·이주·퇴거) 단계 · 전체 단축분의 최대 항목')
         + '<p class="note">협의 기간 <b>60일 → 30일</b> · 중토위 재결 전담팀 신설<br>'
           '조사 거부 시 <b>사진 등 객관적 자료로 갈음</b><br>'
           '<b class="r">수용개시 2개월 경과 시 인도소송 원칙</b></p>'),
    card('09 · 시한', '혜택은 2027년에 최대,<br>2029년에 사라집니다',
         table([['PF 대출금리 재정지원', '<b class="r">1%p</b>', '0.5%p', '—'],
                ['주거시설 개발부담금', '<b class="r">100% 면제</b>', '50% 감면', '—'],
                ['기부채납(수도권)', '<b class="r">△4%p</b>', '△2%p', '—'],
                ['매입임대 취득세', '<b class="r">70% 감면</b>', '50% 감면', '15%'],
                ['현금청산 취득세', '<b class="r">면제</b>', '75% 감면', '—']],
               ['항목', '~2027년', '2028년', '2029년~'], wide=True),
         '2027년 착공 예정 물량이 24.9만호로 5년 중 가장 적기 때문입니다'),
]

BLOG2 = [
    cover('②편 · 금융·대출',
          '8·13 대책,<br>내 대출은<br>언제 어떻게 바뀌나',
          '완화가 먼저 오고, 규제가 나중에 옵니다'),
    card('01 · 순서', '2026년 하반기에 열리고<br>2027년 초에 조여집니다',
         table([['2026. 8. 31', '장래소득 고지 의무화, 생애최초 예외', '<b>완화</b>'],
                ['2026. 10', '결혼 페널티 해소, 청년 전세보증 확대', '<b>완화</b>'],
                ['2026 하반기', '이주비·중도금·잔금 총량 별도 관리', '<b>완화</b>'],
                ['<b>2027. 1. 1</b>', '<b>전세대출보증 제한, 보증비율 축소</b>', '<b class="r">규제</b>'],
                ['<b>2027. 1</b>', '청년 3종 세트 / DSR 소득산정 변경', '<b class="r">혼재</b>']],
               ['시기', '내용', '방향'], wide=True)),
    card('02 · 8월 31일', '은행이 ‘장래소득’을<br>먼저 알려줘야 합니다',
         big('12.5', '%', '연소득 4,000만원·만 30세·30년 만기 시 한도 상승폭 (정부 예시)')
         + '<p class="note">2021년부터 있던 제도지만 <b>은행 자율 사항</b>이라<br>'
           '차주가 요청하지 않으면 적용되지 않는 경우가 많았습니다.<br>'
           '앞으로는 <b>고지가 의무</b>입니다.</p>'),
    card('03 · 전세대출', '세 가지를 모두 충족해야<br>규제 대상입니다',
         points(['수도권·규제지역 내 <b>아파트</b>를 보유한 1주택자 (부부합산)',
                 '그 집을 <b>남에게 임대</b> 중일 것 (직계존비속 제외)',
                 '본인도 배우자도 <b>한 번도 실거주한 적이 없을 것</b>']),
         '2027년 1월 1일 시행 · 하나라도 빠지면 대상이 아닙니다'),
    card('04 · 전세대출', '이런 경우는<br>대상이 아닙니다',
         bullets(['비아파트(빌라·오피스텔 등)를 보유한 경우',
                  '비수도권·비규제지역 아파트를 보유한 경우',
                  '부모나 자녀에게 세를 준 경우',
                  '<b>과거에 잠시라도 실거주하고 전입신고를 했던 경우</b>']),
         '금융당국 “한 번이라도 살았고 주소이전이 됐으면 규제 대상이 아니다”'),
    card('05 · 전세대출', '예외 사유도<br>다섯 가지가 있습니다',
         table([['법적 의무로 실거주가 예정된 경우', '신규·연장 허용'],
                ['세입자 계약이 안 끝나 못 들어가는 경우', '계약 종료일까지 연장'],
                ['임대인이 보증금을 안 돌려주는 경우', '만기연장 허용'],
                ['퇴거 예정이나 일정 조정이 필요한 경우', '6개월 내 단기 연장'],
                ['<b>여신심사위원회가 불가피성을 인정</b>', '<b class="r">신규·연장 허용</b>']],
               ['상황', '허용 범위'], wide=True),
         '마지막 항목이 사실상 개별 구제 창구가 됩니다'),
    card('06 · 전세대출', '보증비율이 낮아집니다',
         table([['1주택자 (수도권·규제지역)', '80%', '<b class="r">70%</b>'],
                ['1주택자 (그 외 지역)', '90%', '<b class="r">80%</b>'],
                ['<b>무주택자</b>', '80% / 90%', '<b>현행 유지</b>']],
               ['구분', '현행', '개선']),
         '2027년 1월 1일 시행 · 무주택자는 영향이 없습니다'),
    card('07 · DSR', '오르면 평균 내서 깎고,<br>내리면 그대로 반영합니다',
         table([['상승률 20% 이하', '최근 1년', '변화 없음'],
                ['상승률 20% 초과', '<b class="r">최근 2년 평균</b>', '한도 축소'],
                ['상승률 30% 초과', '<b class="r">최근 3년 평균</b>', '한도 더 축소'],
                ['<b>소득 감소</b>', '<b>최근 1년</b>', '평균 없이 그대로']],
               ['소득 변화', '개선 후 산정', '효과'], wide=True),
         '성과급 비중이 크거나 승진·이직으로 소득이 뛴 분이 직접 영향을 받습니다'),
    card('08 · 결혼 페널티', '부부 중 한 명만<br>기준을 충족하면 됩니다',
         '<p class="ex">소득 <b>5,000만원</b> + 소득 <b>7,000만원</b> 부부가<br>혼인신고 후 디딤돌대출을 신청하면</p>'
         + arrow('합산 1.2억으로 심사<br>대출 불가', '5,000만원 기준 심사<br>대출 가능')
         + '<p class="note">보금자리론 7,000 · 디딤돌 6,000 · 버팀목 5,000만원<br>'
           '보금자리론은 <b>2026년 10월</b> 시행</p>'),
    card('09 · 청년', '청년미래보금자리론의<br>핵심은 마지막 줄입니다',
         table([['대상주택', '6억 이하 주택', '<b>4억 이하 비아파트</b>'],
                ['LTV', '아파트 70% / 기타 65%', '<b>최대 80%</b>'],
                ['소득요건', '7,000만원 이하', '7,000만원 이하'],
                ['<b>생애최초 LTV 우대</b>', '<b>이용 시 소멸</b>', '<b class="r">이용 시에도 유지</b>']],
               ['구분', '일반 보금자리론', '청년미래보금자리론'], wide=True),
         '비아파트로 먼저 들어간 뒤 아파트를 살 때 생애최초 혜택을 다시 쓸 수 있습니다'),
]

# ── 조판 ────────────────────────────────────────────────────
CSS = '''
*{box-sizing:border-box;margin:0;padding:0}
body{background:#8A9199}
.card{
  width:1080px;height:1080px;background:#fff;color:#1A1C20;
  font-family:'Noto Sans CJK KR','Noto Sans KR',NanumBarunGothic,sans-serif;
  padding:82px 84px 74px;display:flex;flex-direction:column;
  word-break:keep-all;position:relative;overflow:hidden;
}
.card + .card{margin-top:40px}
.label{font-size:25px;font-weight:700;letter-spacing:.14em;color:#C0392B;line-height:1.4}
.rule{height:3px;background:#12203A;margin:22px 0 40px}
h2{font-family:NanumMyeongjo,'Noto Serif CJK KR',serif;font-size:60px;font-weight:800;
   line-height:1.38;letter-spacing:-.035em;color:#0F2548}
.card.cover h2{font-size:74px;line-height:1.36}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;padding:44px 0 0}
.card.cover .body{justify-content:flex-start;padding-top:46px}
.sub{font-size:34px;line-height:1.7;color:#4C525B;letter-spacing:-.02em}
.botrow{display:flex;align-items:flex-end;gap:44px;margin-top:34px;padding-top:24px;
        border-top:1px solid #E3E6EB}
.foot{flex:1;min-width:0;font-size:25px;line-height:1.65;color:#6B7480;letter-spacing:-.015em}
.mark{flex:none;font-size:23px;letter-spacing:.1em;color:#8A9199;white-space:nowrap;padding-bottom:2px}
.card.cover .mark{color:#0F2548;font-weight:700}

table{border-collapse:collapse;width:100%;font-size:31px;line-height:1.5}
table.w{font-size:27px}
th,td{padding:19px 20px 19px 0;text-align:left;vertical-align:top;border-bottom:1px solid #EFF1F4}
th:first-child,td:first-child{padding-left:0}
thead th{font-size:22px;letter-spacing:.1em;color:#8A9199;font-weight:700;
         border-bottom:2px solid #12203A;padding-bottom:15px;white-space:nowrap}
tbody tr:last-child td{border-bottom:2px solid #12203A}
td b{font-weight:800;color:#0F2548}
b.r{color:#C0392B}

.pts{list-style:none;counter-reset:p}
.pts li{counter-increment:p;position:relative;padding-left:82px;font-size:35px;line-height:1.6;
        color:#4C525B;letter-spacing:-.02em}
.pts li + li{margin-top:34px}
.pts li::before{content:counter(p);position:absolute;left:0;top:2px;width:52px;height:52px;
  background:#0F2548;color:#fff;font-size:27px;font-weight:700;
  display:flex;align-items:center;justify-content:center}
.pts li b{color:#0F2548;font-weight:800}

.bul{list-style:none}
.bul li{position:relative;padding-left:44px;font-size:34px;line-height:1.6;color:#4C525B;letter-spacing:-.02em}
.bul li + li{margin-top:30px}
.bul li::before{content:'';position:absolute;left:4px;top:.62em;width:20px;height:3px;background:#3E6CB5}
.bul li b{color:#0F2548;font-weight:800}

.arw{display:flex;align-items:stretch;gap:28px}
.arw .b,.arw .a{flex:1;padding:28px 28px;border:2px solid #E3E6EB;min-width:0}
.arw .a{border-color:#C0392B;background:#FBF1C7}
.arw span{display:block;font-size:22px;font-weight:700;letter-spacing:.12em;color:#8A9199;margin-bottom:16px}
.arw .a span{color:#C0392B}
.arw b{display:block;font-size:38px;font-weight:800;line-height:1.35;letter-spacing:-.03em;color:#0F2548}
.arw .ar{display:flex;align-items:center;font-size:46px;color:#C0392B;font-weight:700}
.cap{margin-top:28px;font-size:27px;line-height:1.7;color:#6B7480;letter-spacing:-.015em}

.big{display:flex;align-items:baseline;gap:14px;justify-content:center;margin:0 0 4px}
.big b{font-family:'Noto Sans Mono CJK KR',monospace;font-size:158px;font-weight:800;
       line-height:1;letter-spacing:-.05em;color:#C0392B}
.big span{font-size:48px;font-weight:700;color:#C0392B}
.big + .cap{text-align:center;font-size:29px;color:#4C525B}
.note{margin-top:30px;padding:26px 30px;background:#F5F6F8;border-left:4px solid #3E6CB5;
      font-size:28px;line-height:1.68;color:#4C525B;letter-spacing:-.018em}
.note b{color:#0F2548;font-weight:800}
.ex{font-size:31px;line-height:1.6;color:#4C525B;margin-bottom:24px;letter-spacing:-.02em}
.ex b{color:#0F2548;font-weight:800}
'''

def render(cards):
    out = []
    for c in cards:
        cls = 'card cover' if c['kind'] == 'cover' else 'card'
        out.append(
            f'<div class="{cls}"><div class="label">{c["label"]}</div><div class="rule"></div>'
            f'<h2>{c["title"]}</h2><div class="body">{c["body"]}</div>'
            f'<div class="botrow"><div class="foot">{c.get("foot","")}</div>'
            f'<div class="mark">리걸매거진 · 법무법인 JL</div></div></div>')
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            f'<style>{CSS}</style></head><body>' + ''.join(out) + '</body></html>')


def shoot(html, outdir, prefix):
    os.makedirs(outdir, exist_ok=True)
    src = os.path.join(outdir, '_cards.html')
    open(src, 'w', encoding='utf-8').write(html)
    script = f'''
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch({{ executablePath: {json.dumps(CHROME)} }});
  const p = await b.newPage({{ viewport: {{ width: {SIZE}, height: {SIZE} }}, deviceScaleFactor: {SCALE} }});
  await p.goto('file://' + {json.dumps(os.path.abspath(src))});
  await p.waitForTimeout(900);
  const n = await p.locator('.card').count();
  for (let i = 0; i < n; i++) {{
    const f = {json.dumps(outdir)} + '/' + {json.dumps(prefix)} + String(i + 1).padStart(2, '0') + '.png';
    await p.locator('.card').nth(i).screenshot({{ path: f }});
    // 넘침 검사
    const ov = await p.locator('.card').nth(i).evaluate(e => e.scrollHeight - e.clientHeight);
    if (ov > 2) console.log('OVERFLOW card ' + (i + 1) + ' by ' + ov + 'px');
  }}
  console.log('rendered ' + n + ' cards -> ' + {json.dumps(outdir)});
  await b.close();
}})();
'''
    sp = os.path.join(outdir, '_shot.js')
    open(sp, 'w').write(script)
    r = subprocess.run(['node', sp], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip()[-800:])
    os.remove(sp); os.remove(src)


if __name__ == '__main__':
    shoot(render(BLOG1), os.path.join(OUT, 'blog1'), 'b1-')
    shoot(render(BLOG2), os.path.join(OUT, 'blog2'), 'b2-')
