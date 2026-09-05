# -*- coding: utf-8 -*-
"""사진을 구할 수 없는 자리를 '정보를 담은 도해'로 채운다.

법인만 가진 자료(사무소·법원·서류·시험 장면)는 지금 확보할 수 없다.
빈 상자로 두거나 장식용 아이콘을 넣는 대신, 그 자리에서 설명해야 할 내용을
도형으로 그린다. 사진이 아니므로 사진인 척하지 않는다.
"""
import io, os
import cairosvg

DST = 'template/design/photos'
NAVY, FILL, DARK = '#223D5B', '#385783', '#2A3B4F'
CARD, LINE, GOLD, INK = '#E9EDF8', '#C6CFE0', '#B08D4F', '#111418'
W, H = 800, 600
# fc-list에 등록된 실제 패밀리명이어야 한다. 이름이 틀리면 한글이 전부 두부가 된다.
FONT = "Gmarket Sans TTF"

def svg(body, w=W, h=H, bg='#FFFFFF'):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d"><rect width="%d" height="%d" fill="%s"/>%s</svg>'
            % (w, h, w, h, w, h, bg, body))

def t(x, y, s, size=19, fill=INK, weight=700, anchor='start'):
    return ('<text x="%g" y="%g" font-family="%s" font-size="%g" font-weight="%s" '
            'fill="%s" text-anchor="%s">%s</text>' % (x, y, FONT, size, weight, fill, anchor, s))

def rect(x, y, w, h, fill='#FFFFFF', stroke=LINE, sw=1.6, top=None):
    o = '<rect x="%g" y="%g" width="%g" height="%g" fill="%s" stroke="%s" stroke-width="%g"/>' \
        % (x, y, w, h, fill, stroke, sw)
    if top:
        o += '<rect x="%g" y="%g" width="%g" height="4" fill="%s"/>' % (x, y, w, top[0] if isinstance(top, tuple) else 0, '')
    return o

def band(x, y, w, h, color):
    return '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (x, y, w, h, color)

def lines(x, y, w, n, gap=15, color=LINE, sw=3, last=0.6):
    o = []
    for i in range(n):
        ww = w * (last if i == n - 1 else 1)
        o.append('<rect x="%g" y="%g" width="%g" height="%g" rx="1.5" fill="%s"/>'
                 % (x, y + i * gap, ww, sw, color))
    return ''.join(o)

# ── 1. 설계도서 3종 세트 ────────────────────────────────────────────
def doc_set(title, items, accent=FILL):
    o = [band(0, 0, W, 74, NAVY), t(36, 46, title, 24, '#FFFFFF')]
    x0, gap, cw = 44, 26, (W - 88 - 2 * 26) / 3
    for i, (nm, sub) in enumerate(items):
        x = x0 + i * (cw + gap)
        o += [rect(x, 120, cw, 330, '#FFFFFF'),
              band(x, 120, cw, 5, accent),
              band(x + 22, 160, 34, 34, CARD),
              t(x + 22, 232, nm, 20, NAVY),
              t(x + 22, 260, sub, 14.5, INK, 500),
              lines(x + 22, 292, cw - 44, 7)]
    o.append(t(44, 512, '세 문서를 나란히 놓고 대조할 때 비로소 하자 여부를 말할 수 있습니다',
               17, NAVY))
    o.append(band(44, 530, 120, 4, GOLD))
    return svg(''.join(o))

# ── 2. 서식(동의서·계약서) ──────────────────────────────────────────
def form_sheet(title, fields, stamp=None):
    o = [band(0, 0, W, 74, NAVY), t(36, 46, title, 24, '#FFFFFF')]
    o += [rect(120, 112, 560, 430, '#FFFFFF'), band(120, 112, 560, 5, FILL)]
    o.append(t(152, 168, title.split(' · ')[0], 21, NAVY))
    o.append(band(152, 182, 90, 3, GOLD))
    y = 220
    for k, v in fields:
        o += [t(152, y, k, 15.5, FILL),
              '<rect x="272" y="%g" width="368" height="30" fill="%s"/>' % (y - 21, CARD),
              t(286, y, v, 15, INK, 500)]
        y += 48
    if stamp:
        o += ['<circle cx="596" cy="486" r="38" fill="none" stroke="%s" stroke-width="3"/>' % GOLD,
              t(596, 480, stamp[0], 14, GOLD, 800, 'middle'),
              t(596, 500, stamp[1], 14, GOLD, 800, 'middle')]
    return svg(''.join(o))

# ── 3. 건물(사무소·법원) ────────────────────────────────────────────
def building(title, sub, kind='office'):
    o = [band(0, 0, W, 74, NAVY), t(36, 46, title, 24, '#FFFFFF')]
    o.append(band(0, 470, W, 130, CARD))
    if kind == 'court':
        o.append('<polygon points="400,130 640,236 160,236" fill="%s"/>' % NAVY)
        for i in range(6):
            x = 196 + i * 68
            o.append('<rect x="%g" y="248" width="30" height="190" fill="%s"/>' % (x, FILL))
        o.append('<rect x="160" y="438" width="480" height="32" fill="%s"/>' % NAVY)
        o.append('<rect x="140" y="466" width="520" height="14" fill="%s"/>' % DARK)
    else:
        o.append('<rect x="212" y="150" width="376" height="320" fill="%s"/>' % FILL)
        o.append('<rect x="212" y="150" width="376" height="46" fill="%s"/>' % NAVY)
        for r in range(5):
            for c in range(6):
                o.append('<rect x="%g" y="%g" width="42" height="34" fill="%s" opacity="%s"/>'
                         % (238 + c * 56, 220 + r * 50, '#FFFFFF', 0.86 if (r + c) % 3 else 0.5))
        o.append('<rect x="360" y="404" width="80" height="66" fill="%s"/>' % NAVY)
    o += [t(400, 524, sub, 20, NAVY, 800, 'middle'),
          '<rect x="340" y="540" width="120" height="4" fill="%s"/>' % GOLD]
    return svg(''.join(o))

# ── 4. 회의 ────────────────────────────────────────────────────────
def meeting(title, seats, caption):
    o = [band(0, 0, W, 74, NAVY), t(36, 46, title, 24, '#FFFFFF')]
    o.append('<ellipse cx="400" cy="330" rx="230" ry="112" fill="%s"/>' % CARD)
    o.append('<ellipse cx="400" cy="322" rx="230" ry="112" fill="#FFFFFF" stroke="%s" stroke-width="2"/>' % LINE)
    import math
    for i in range(seats):
        a = math.pi * 2 * i / seats - math.pi / 2
        cx, cy = 400 + 268 * math.cos(a), 322 + 150 * math.sin(a)
        o.append('<circle cx="%g" cy="%g" r="26" fill="%s"/>' % (cx, cy, FILL if i % 2 else NAVY))
        o.append('<rect x="%g" y="%g" width="52" height="26" rx="13" fill="%s"/>'
                 % (cx - 26, cy + 22, FILL if i % 2 else NAVY))
    o += [lines(330, 296, 140, 4, 14, LINE, 4),
          t(400, 528, caption, 18, NAVY, 800, 'middle'),
          '<rect x="340" y="544" width="120" height="4" fill="%s"/>' % GOLD]
    return svg(''.join(o))

# ── 5. 계측·시험 ───────────────────────────────────────────────────
# 실측값은 사건마다 다르고 아직 확보한 값이 없다. 없는 숫자를 지어내지 않는다.
# 기준값(문헌·법령에 있는 값)만 적고 실측 칸은 비워 둔다.
def gauge(title, spec, unit, source, note):
    o = [band(0, 0, W, 74, NAVY), t(36, 46, title, 24, '#FFFFFF')]
    o += [t(120, 152, '기준값', 16, FILL),
          t(120, 200, '%s%s' % (spec, unit), 44, NAVY),
          '<rect x="120" y="222" width="240" height="34" fill="%s"/>' % FILL,
          t(120, 276, source, 14, INK, 500)]
    o += [t(440, 152, '실측값', 16, INK),
          '<rect x="440" y="168" width="240" height="46" fill="none" stroke="%s" '
          'stroke-width="2" stroke-dasharray="7 5"/>' % LINE,
          t(560, 200, '조사 후 기입', 18, '#7F8CA6', 700, 'middle'),
          '<rect x="440" y="222" width="240" height="34" fill="none" stroke="%s" '
          'stroke-width="1.6" stroke-dasharray="7 5"/>' % LINE]
    o += ['<rect x="120" y="316" width="560" height="150" fill="%s"/>' % CARD,
          '<rect x="120" y="316" width="560" height="5" fill="%s"/>' % GOLD,
          t(148, 360, '판정 방법', 16, FILL), t(148, 400, note, 18, NAVY),
          lines(148, 420, 500, 2, 18)]
    o.append(t(120, 522, '기준값만 표기했습니다. 실측값은 해당 단지 조사·감정에서 확인한 뒤 채웁니다.',
               14.5, INK, 500))
    return svg(''.join(o))

# ── 6. 단지 외관 / 옥상 ─────────────────────────────────────────────
def complex_view(title, caption, roof=False):
    o = [band(0, 0, W, 74, NAVY), t(36, 46, title, 24, '#FFFFFF')]
    o.append(band(0, 452, W, 148, CARD))
    if roof:
        o += ['<polygon points="90,300 710,300 640,236 160,236" fill="%s"/>' % CARD,
              '<rect x="90" y="300" width="620" height="150" fill="%s"/>' % FILL,
              '<rect x="90" y="300" width="620" height="18" fill="%s"/>' % NAVY]
        for i in range(7):
            o.append('<rect x="%g" y="330" width="6" height="100" fill="#FFFFFF" opacity=".45"/>' % (130 + i * 88))
        o.append('<circle cx="400" cy="376" r="26" fill="%s"/>' % NAVY)
        o.append('<circle cx="400" cy="376" r="13" fill="#FFFFFF"/>')
    else:
        for i, (x, w, h) in enumerate([(110, 120, 300), (250, 150, 380), (420, 130, 330), (570, 120, 260)]):
            o.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (x, 452 - h, w, h, FILL if i % 2 else NAVY))
            for r in range(int(h / 46)):
                for c in range(int(w / 40)):
                    o.append('<rect x="%g" y="%g" width="22" height="22" fill="#FFFFFF" opacity="%s"/>'
                             % (x + 12 + c * 40, 452 - h + 20 + r * 46, 0.8 if (r + c) % 3 else 0.42))
    o += [t(400, 516, caption, 19, NAVY, 800, 'middle'),
          '<rect x="340" y="532" width="120" height="4" fill="%s"/>' % GOLD]
    return svg(''.join(o))

# ── 자리별 배정 ─────────────────────────────────────────────────────
JOBS = {
 'p-documents.jpg': doc_set('관리사무소가 보유한 자료', [
    ('하자 접수대장', '세대별 접수·처리 기록'),
    ('보수 요구 공문', '시공사 회신 포함'),
    ('관리규약 · 의결', '입대의 구성과 의결 자료')]),
 'p-logbook.jpg': doc_set('접수 기록이 곧 증거입니다', [
    ('최초 접수일', '발생 시점을 특정합니다'),
    ('반복 접수', '시공 원인을 가리킵니다'),
    ('미이행 이력', '보수 청구의 근거입니다')]),
 'p-logbook2.jpg': doc_set('공문과 회신은 함께 봅니다', [
    ('보수 요구 공문', '요구한 날짜와 범위'),
    ('시공사 회신', '이행 여부와 사유'),
    ('미이행 확인', '남은 하자의 목록')]),
 'p-report-adhoc.jpg': doc_set('수시 보고는 세 시점에 나갑니다', [
    ('소장 접수', '청구 범위와 금액'),
    ('감정서 도착', '인정·불인정 항목'),
    ('판결 선고', '주문과 다음 절차')]),
 'p-report-inside.jpg': doc_set('보고서에 담는 것', [
    ('진행 상황', '지금 어느 단계인지'),
    ('판단 근거', '왜 그렇게 보는지'),
    ('결정 사항', '무엇을 정해야 하는지')]),
 'p-supplement.jpg': doc_set('감정보완신청의 뼈대', [
    ('누락 항목', '조사되지 않은 부위'),
    ('기준 오적용', '설계도서와 다른 기준'),
    ('수량 오류', '면적·개소 산출 착오')]),
 'p-disclosure-form.jpg': doc_set('정보공개청구로 확보하는 것', [
    ('준공도면', '사업승인·준공 시점'),
    ('공사시방서', '두께·배합 기준'),
    ('형별성능관계내역', '자재 두께와 등급')]),

 'p-consent.jpg': form_sheet('채권양도 동의서 · 서식', [
    ('동  호  수', '○○○동 ○○○호'), ('구분소유자', '성명 · 생년월일'),
    ('양 도 내 용', '전유부분 하자 손해배상채권'),
    ('양  수  인', '입주자대표회의')], ('구분', '소유자')),
 'p-consent-blank.jpg': form_sheet('세대에서 받는 서류', [
    ('동  호  수', ''), ('구분소유자', ''), ('양 도 내 용', ''), ('서    명', '')],
    ('서명', '또는 인')),
 'p-consent-form.jpg': form_sheet('전유부분은 세대가 채권자입니다', [
    ('채  권  자', '구분소유자 (세대)'), ('양수인', '입주자대표회의'),
    ('필요 서류', '동의서 · 신분 확인'), ('확인 사항', '소유자 본인 여부')], None),
 'p-consent-check.jpg': form_sheet('받은 동의서는 이렇게 검수합니다', [
    ('1  서명 확인', '자필 여부와 누락'), ('2  인적사항 대조', '등기부상 소유자'),
    ('3  세대 명단 대조', '중복·누락 확인'), ('4  미회수 관리', '재징구 대상 정리')], None),
 'p-agreement.jpg': form_sheet('위임계약서에 적히는 것', [
    ('착  수  금', '[F-1 확인]'), ('성공보수율', '[F-2 확인]'),
    ('비용 부담', '감정료·인지대·송달료 대납'), ('패소 시 처리', '[F-5 확인]')],
    ('법무법인', '제이엘')),
 'p-receipt.jpg': form_sheet('절차 단계마다 나뉘어 발생합니다', [
    ('인  지  대', '소 제기 시'), ('송  달  료', '소 제기 시'),
    ('감  정  료', '감정 개시 시'), ('부담 방식', '법인 선지급 후 정산')], None),

 'p-court.jpg': building('청구는 법원에서 다툽니다', '관할 법원', 'court'),
 'p-courthouse.jpg': building('조정과 소송은 강제력이 다릅니다', '관할 법원', 'court'),
 'p-filing.jpg': building('소 제기로 기간이 멈춥니다', '소장 접수', 'court'),
 'p-judgment.jpg': building('판결은 끝이 아닙니다', '판결 선고', 'court'),
 'p-execution.jpg': building('지급하지 않으면 집행합니다', '채권압류 · 추심', 'court'),
 'p-firm.jpg': building('법무법인 제이엘', '서초 본사 · 동탄 분사무소', 'office'),
 'p-office-seoul.jpg': building('서울 서초 본사', '서울중앙지법 인접', 'office'),
 'p-office-dongtan.jpg': building('경기 화성 동탄 분사무소', '수원지법 관할 대응', 'office'),

 'p-meeting.jpg': meeting('입주자대표회의', 8, '의결로 정하는 것과 세대 동의가 필요한 것'),
 'p-briefing.jpg': meeting('주민 설명회', 10, '법인이 직접 방문해 설명드립니다'),
 'p-committee.jpg': meeting('하자심사·분쟁조정위원회', 7, '판정서 10건 중 약 7건이 하자로 인정'),
 'p-inhouse.jpg': meeting('변호사와 기술사가 같은 자리에서', 6, '외주가 아니라 법인 안에서 합니다'),
 'p-tech-review.jpg': meeting('도면 검토', 5, '건축시공기술사가 준공도면을 직접 읽습니다'),
 'p-appraisal-joint.jpg': meeting('원·피고 공동조사', 6, '이 자리에 들어가느냐가 결과를 좌우합니다'),
 'p-appraisal-record.jpg': doc_set('현장에서 그 자리에 기록합니다', [
    ('측정값', '어디를 얼마로 쟀는지'),
    ('위치 표기', '동·층·부위 특정'),
    ('사진 대장', '측정 장면과 눈금')]),

 'p-tile-test.jpg': gauge('타일 부착강도', '0.39', ' N/mm2',
                          '「2026 건설감정실무」 개정으로 새로 생긴 기준',
                          '현장에서 인장 시험기로 부착강도를 측정합니다'),
 'p-firedoor.jpg': gauge('방화문 차열·차염 성능', '설계도서 기재값', '',
                         '형별성능관계내역에 적힌 사양',
                         'KS 시험기관에 시료를 보내 성능을 확인합니다'),
 'p-wallpad.jpg': gauge('월패드 예비전원장치', '설치', '',
                        '사용승인도면·형별성능관계내역 기재',
                        '단자함을 열어 설치 여부를 확인합니다'),
 'p-wallpad-panel.jpg': gauge('홈게이트웨이', '설계도서 기재값', '',
                              '사용승인 당시 기준으로 판단',
                              '"장비가 없다"가 아니라 "기준을 충족했는가"로 다툽니다'),
 'p-book2026.jpg': doc_set('2026 건설감정실무', [
    ('발간', '서울중앙지방법원 건설소송실무연구회'),
    ('개정', '2016년판 이후 10년 만'),
    ('의미', '하자 판단의 사실상 표준')]),
 'p-book-page.jpg': doc_set('개정으로 달라진 것', [
    ('균열', '충전식 보수를 원칙으로'),
    ('타일', '부착강도 0.39N/㎟ 기준'),
    ('방수', '통일 기준을 제시하지 않음')]),
 'p-repair.jpg': doc_set('회수금은 보수공사로 이어집니다', [
    ('공사 발주', '입대의가 시공사를 선정'),
    ('감독', '판결 인정 항목대로 시공'),
    ('완료 확인', '하자가 실제로 없어졌는지')]),
 'p-site-exterior.jpg': complex_view('외벽에서 먼저 드러납니다', '균열 · 백화 · 타일 탈락'),
 'p-site-roof.jpg': complex_view('옥상 방수층과 배수구', '들뜸 · 갈라짐 · 고인 물', roof=True),
 'p-part1.jpg': building('', '', 'office'),
 'p-part6.jpg': form_sheet('비용과 조건', [
    ('착수 단계', '법인 선지급'), ('감정 단계', '법인 선지급'),
    ('판결 이후', '회수금에서 정산')], None),
 'p-part7.jpg': complex_view('', ''),
}

os.makedirs(DST, exist_ok=True)
for name, s in JOBS.items():
    w, h = (1332, 750) if name.startswith('p-part') else (800, 600)
    cairosvg.svg2png(bytestring=s.encode('utf-8'),
                     write_to=os.path.join(DST, name),
                     output_width=w, output_height=h)
    # PNG로 그려 JPG 확장자로 저장하면 브라우저는 내용으로 판별하지만
    # 캔버스는 확장자로 MIME을 정하므로 실제 JPEG로 다시 인코딩한다.
    from PIL import Image
    im = Image.open(os.path.join(DST, name)).convert('RGB')
    im.save(os.path.join(DST, name), 'JPEG', quality=84, optimize=True, progressive=True)
    print('%-26s %dx%d %4dKB' % (name, w, h, os.path.getsize(os.path.join(DST, name)) // 1024))
print(len(JOBS), '자리 도해로 채움')
