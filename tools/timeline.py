#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""담보책임 존속기간 자동 계산.

근거: 집합건물의 소유 및 관리에 관한 법률 제9조의2 + 같은 법 시행령 제5조
      (proposal/02_법률프레임.md에서 확정된 값)

기산점
  - 전유부분: 구분소유자에게 인도한 날 (입주개시일)
  - 공용부분: 사용검사일 또는 사용승인일

사용법
  python3 tools/timeline.py template/data/_example_이스트힐.json
  python3 tools/timeline.py <json> --asof 2026-08-18
"""
import argparse
import json
import sys
from datetime import date

# (키, 표시명, 연수, 기산 대상)
#   기산 대상 'common' = 공용부분(사용검사일), 'private' = 전유부분(인도일)
CATEGORIES = [
    ("structural_10y", "주요구조부 · 지반공사", 10, "common"),
    ("safety_5y", "구조상·안전상 (철근콘크리트·조적·지붕·방수 등)", 5, "common"),
    ("function_3y", "기능상·미관상 (건축설비·목공사·창호·조경 등)", 3, "common"),
    ("finish_2y", "마감공사 등 발견·교체·보수가 용이한 하자", 2, "common"),
]

# 05_디자인사양.md 팔레트
COLOR_EXPIRED = "#C0392B"   # 도과
COLOR_SOON = "#E67E22"      # 12개월 내 도과
COLOR_SAFE = "#0F2548"      # 여유

SOON_MONTHS = 12


def parse_date(s):
    y, m, d = (int(x) for x in s.split("-"))
    return date(y, m, d)


def add_years(d, years):
    """N년 후 같은 날짜. 2/29 기산은 평년에 2/28로 내린다."""
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, month=2, day=28)


def months_between(a, b):
    """a에서 b까지의 개월 수 (일자 미달분은 내림). b가 과거면 음수."""
    m = (b.year - a.year) * 12 + (b.month - a.month)
    if b.day < a.day:
        m -= 1
    return m


def compute(inspection_date, handover_date, asof):
    rows = []
    for key, label, years, basis in CATEGORIES:
        start = inspection_date if basis == "common" else (handover_date or inspection_date)
        expiry = add_years(start, years)
        remaining = months_between(asof, expiry)

        if expiry <= asof:
            status, color = "도과", COLOR_EXPIRED
        elif remaining < SOON_MONTHS:
            status, color = "임박", COLOR_SOON
        else:
            status, color = "여유", COLOR_SAFE

        rows.append({
            "key": key,
            "label": label,
            "years": years,
            "basis": "공용부분(사용검사일)" if basis == "common" else "전유부분(인도일)",
            "start": start.isoformat(),
            "expiry": expiry.isoformat(),
            "remaining_months": remaining,
            "status": status,
            "color": color,
            # 슬라이드에 그대로 실어 검산 가능하게 하는 계산식
            "formula": f"{start.isoformat()} + {years}년 = {expiry.isoformat()}",
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", help="단지 데이터 JSON 경로")
    ap.add_argument("--asof", help="기준일 YYYY-MM-DD (기본: 오늘)")
    ap.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    insp = data.get("사용검사일")
    if not insp:
        sys.exit("오류: '사용검사일'이 없습니다. 이 값 없이는 타임라인을 만들 수 없습니다.")

    inspection_date = parse_date(insp)
    handover = data.get("입주개시일")
    handover_date = parse_date(handover) if handover else None
    asof = parse_date(args.asof) if args.asof else date.today()

    rows = compute(inspection_date, handover_date, asof)

    if args.json:
        print(json.dumps({"기준일": asof.isoformat(), "단지명": data.get("단지명"), "구간": rows},
                         ensure_ascii=False, indent=2))
        return

    print(f"\n단지: {data.get('단지명', '(미입력)')}")
    print(f"사용검사일: {insp}   입주개시일: {handover or '(미입력 — 사용검사일로 대체)'}")
    print(f"기준일: {asof.isoformat()}\n")
    print(f"{'구분':<46} {'만료일':<12} {'잔여':>8}  상태")
    print("-" * 82)
    for r in rows:
        rem = f"{r['remaining_months']}개월" if r["remaining_months"] >= 0 else f"{-r['remaining_months']}개월 경과"
        print(f"{r['label']:<46} {r['expiry']:<12} {rem:>8}  {r['status']}")
    print()
    if not handover:
        print("※ 입주개시일 미입력 — 전유부분 기산이 필요한 항목은 사용검사일로 대체 계산했다. 실제 제안서에는 반드시 입주개시일을 넣는다.\n")


if __name__ == "__main__":
    main()
