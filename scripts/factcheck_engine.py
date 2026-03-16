#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

LIMITATION = "⚠️ 本查核基於公開可得資訊，無法涵蓋未公開或付費牆後的內容。"


def split_claims(text: str):
    parts = re.split(r'[。！？!?；;\n]+', text.strip())
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        sub = re.split(r'(?:，|,|且|並且|另外|同時|而且|但|但是|不過)', p)
        out.extend([s.strip() for s in sub if s.strip()])
    return out or [text.strip()]


def classify_claim(claim: str):
    c = claim.lower()
    if any(k in c for k in ["the onion", "babylon bee", "satire", "洋蔥新聞", "諷刺"]):
        return "satire"
    if any(k in claim for k in ["我覺得", "我認為", "應該", "最好", "希望", "建議"]) and not re.search(r'\d+\.?\d*%|營收|失業率|通膨|gdp|cpi', c):
        return "opinion"
    if any(k in claim for k in ["預測", "預估", "預計", "目標價", "未來", "明年", "將"]):
        return "prediction"
    if any(k in claim for k in ["導致", "造成", "因為", "由於", "因此", "引發"]):
        return "causal"
    if re.search(r'\d+\.?\d*%|營收|失業率|通膨|GDP|CPI|股價|年增|季增', claim, re.IGNORECASE):
        return "statistical"
    if any(k in claim for k in ["表示", "指出", "說過", "聲稱", "宣稱"]):
        return "attribution"
    return "event"


def build_query(claim: str):
    q = re.sub(r'(我覺得|我認為|應該|最好|其實|就是)', '', claim).strip()
    return q[:80]


def extract_cmd(args):
    claims = []
    for i, c in enumerate(split_claims(args.text), 1):
        t = classify_claim(c)
        claims.append({
            "id": i,
            "claim": c,
            "type": t,
            "query_zh": build_query(c),
            "query_en": build_query(c),
        })
    Path(args.output).write_text(json.dumps(claims, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(claims, ensure_ascii=False, indent=2))


def score_one(item):
    t = item.get("type", "event")
    if t == "prediction":
        return {**item, "internal_score": None, "band": "prediction"}
    if t in ("opinion", "satire"):
        return {**item, "internal_score": None, "band": t}

    # deterministic scoring from provided evidence summary
    e = item.get("evidence", {})
    official = int(e.get("official_count", 0))
    mainstream = int(e.get("mainstream_count", 0))
    independent = int(e.get("independent_count", 0))
    factcheck_true = bool(e.get("factcheck_true", False))
    factcheck_false = bool(e.get("factcheck_false", False))
    rebuttal_authority = bool(e.get("authority_rebuttal", False))
    stale = bool(e.get("outdated_presented_current", False))
    source_chain = int(e.get("source_chain_hops", 2))
    twitter_search_count = int(e.get("twitter_search_count", 0))
    twitter_verified_hits = int(e.get("twitter_verified_hits", 0))
    twitter_consensus = bool(e.get("twitter_consensus", False))

    # A source quality 20
    a = 0
    a += 8 if official >= 2 else (5 if official == 1 else 1 if mainstream > 0 else 0)
    a += 5 if mainstream >= 3 else 4 if mainstream == 2 else 2 if mainstream == 1 else 0
    a += 4 if independent >= 3 else 2 if independent == 2 else 0
    a = min(20, a)

    # B consistency 15
    contradiction = bool(e.get("core_contradiction", False))
    b = 15 if not contradiction else 5

    # C traceability 15
    c = 0
    c += 6 if official > 0 else 3
    c += 5 if source_chain <= 1 else 3 if source_chain <= 3 else 1
    c += 4 if e.get("has_timestamp", True) else 0

    # D counter evidence 20
    d = 0
    d += 0 if rebuttal_authority else 8
    if factcheck_false:
        d += 0
    elif factcheck_true:
        d += 5
    else:
        d += 2
    d += 7 if not e.get("strong_social_debunk", False) else 1

    # Slightly increase Twitter weight (internal only), without changing other source budgets.
    # Recommended workflow runs 3 X searches and rewards only when verified/accountable posts converge.
    tw_bonus = 0
    if twitter_search_count >= 3 and twitter_verified_hits >= 2 and twitter_consensus:
        tw_bonus = 2
    elif twitter_search_count >= 2 and twitter_verified_hits >= 1 and twitter_consensus:
        tw_bonus = 1
    d += tw_bonus

    d = min(20, d)

    # E context 15
    e_score = 15
    if stale:
        e_score -= 5
    if e.get("out_of_context", False):
        e_score -= 7
    e_score = max(0, e_score)

    # F transparency 15
    f = 15
    if e.get("headline_mismatch", False):
        f -= 6
    if e.get("missing_data_citation", False):
        f -= 5
    if e.get("fact_opinion_mixed", False):
        f -= 4
    f = max(0, f)

    total = min(100, a + b + c + d + e_score + f)
    if total >= 72:
        band = "true"
    elif total >= 36:
        band = "uncertain"
    else:
        band = "false"

    return {**item, "internal_score": total, "band": band}


def score_cmd(args):
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    arr = data if isinstance(data, list) else [data]
    scored = [score_one(x) for x in arr]
    Path(args.output).write_text(json.dumps(scored, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(scored, ensure_ascii=False, indent=2))


def compose_line(x):
    claim = x.get("claim", "")
    band = x.get("band")
    corr = x.get("correct_info", "")
    findings = x.get("findings", "")
    sources = x.get("sources", [])
    links = "、".join([f"[{s.get('name','來源')}]({s.get('url','')})" for s in sources if s.get('url')])

    if band == "true":
        base = f"「{claim}」查核後屬實，{findings}" if findings else f"「{claim}」查核後屬實。"
        if links:
            base += f" 參考來源：{links}。"
        return base
    if band == "false":
        base = f"「{claim}」與可得資料不符，{corr or findings or '已找到更可信的相反證據'}。"
        if links:
            base += f" 參考來源：{links}。"
        return base
    if band == "prediction":
        base = f"「{claim}」屬於預測性說法，目前無法證實或證偽，以下整理目前可查詢到的預測資訊：{findings or '尚無足夠一致資料'}。"
        if links:
            base += f" 參考來源：{links}。"
        return base
    if band == "satire":
        return f"「{claim}」來源屬於諷刺/虛構內容，不應視為真實新聞。"
    if band == "opinion":
        return f"「{claim}」屬於觀點陳述，無法以事實查核方式做真偽判定。"
    return f"「{claim}」目前資訊不足，暫無法確認。"


def compose_cmd(args):
    arr = json.loads(Path(args.input).read_text(encoding='utf-8'))
    if isinstance(arr, dict):
        arr = [arr]

    order = {"false": 0, "uncertain": 1, "true": 2, "prediction": 3, "satire": 4, "opinion": 5}
    arr.sort(key=lambda x: order.get(x.get("band", "uncertain"), 9))

    text = "\n\n".join(compose_line(x) for x in arr)
    text = text.strip() + "\n\n" + LIMITATION
    Path(args.output).write_text(text, encoding='utf-8')
    print(text)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)

    p1 = sub.add_parser('extract')
    p1.add_argument('--text', required=True)
    p1.add_argument('--output', required=True)
    p1.set_defaults(func=extract_cmd)

    p2 = sub.add_parser('score')
    p2.add_argument('--input', required=True)
    p2.add_argument('--output', required=True)
    p2.set_defaults(func=score_cmd)

    p3 = sub.add_parser('compose')
    p3.add_argument('--input', required=True)
    p3.add_argument('--output', required=True)
    p3.set_defaults(func=compose_cmd)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
