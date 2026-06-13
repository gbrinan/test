#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval_routing.py — tests/eval_questions.yaml 을 온톨로지에 돌려 라우팅 가능성을 점검한다.

라이브 텔레그램 세션 없이 검증 가능한 부분만 확인한다:
  - in_book      : expect_nodes 가 실제 노드로 존재하는가(오타 방지) +
                   질문 토큰이 기대 노드의 별칭/요약/id 로 라우팅 가능한가
  - out_of_book  : 매칭되는 노드가 없어야(=책밖) 정상 — 노드가 잡히면 경고
  - guardrail    : 차단 트리거 키워드 포함 여부 표시(실제 차단은 harness가 수행)

실제 답변 품질(S2 환각억제·S3 근거표기·S5 개인화)은 라이브 세션 평가가 필요하다.

실행: uv run --with pyyaml python scripts/eval_routing.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML 필요: uv run --with pyyaml python scripts/eval_routing.py\n")
    sys.exit(2)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_index import load_nodes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GUARDRAIL_KEYS = ["진단", "불면증", "mg", "복용", "수면제", "처방", "치료제", "약"]
CRISIS_KEYS = ["그만두고", "힘들어", "죽", "자해"]


def tokens(text: str) -> list[str]:
    # 한글/영문/숫자 덩어리로 분절 (2글자 이상)
    return [t for t in re.findall(r"[가-힣A-Za-z0-9]+", text) if len(t) >= 2]


def route(q: str, nodes: dict) -> list[str]:
    """질문 토큰을 노드의 id/별칭/요약과 매칭해 후보 노드 id 반환(점수순)."""
    qtok = tokens(q)
    scored: list[tuple[int, str]] = []
    for nid, n in nodes.items():
        hay = " ".join([
            nid,
            " ".join(str(a) for a in (n.get("aliases") or [])),
            str(n.get("summary", "")),
        ])
        htok = set(tokens(hay))
        score = 0
        for t in qtok:
            if t in htok:
                score += 2
            elif any(t in h or h in t for h in htok):
                score += 1
        if score > 0:
            scored.append((score, nid))
    scored.sort(reverse=True)
    return [nid for _, nid in scored[:5]]


def main() -> int:
    nodes = load_nodes(ROOT / "ontology" / "nodes")
    data = yaml.safe_load((ROOT / "tests" / "eval_questions.yaml").read_text(encoding="utf-8"))
    ids = set(nodes)

    in_book = data.get("in_book", [])
    out_book = data.get("out_of_book", [])

    print(f"노드 {len(nodes)}개 · in_book {len(in_book)} · out_of_book/guardrail {len(out_book)}\n")

    # --- in_book ---
    print("=== in_book 라우팅 점검 ===")
    miss_node = 0
    route_hit = 0
    for i, item in enumerate(in_book, 1):
        q = item["q"]
        exp = item.get("expect_nodes", [])
        bad = [e for e in exp if e not in ids]
        cand = route(q, nodes)
        hit = [e for e in exp if e in cand]
        ok_route = len(hit) > 0
        if not bad:
            pass
        else:
            miss_node += 1
        if ok_route:
            route_hit += 1
        flag = "OK " if (ok_route and not bad) else "!! "
        print(f"{flag}Q{i:02d} 라우팅매칭={hit if hit else '없음'}  후보={cand[:3]}")
        if bad:
            print(f"      [오타] 존재하지 않는 expect_nodes: {bad}")
    print(f"  → 기대노드 라우팅 성공 {route_hit}/{len(in_book)}, expect_nodes 오타 {miss_node}건\n")

    # --- out_of_book / guardrail ---
    print("=== out_of_book / guardrail 점검 ===")
    leak = 0
    for i, item in enumerate(out_book, 1):
        q = item["q"]
        kind = item.get("expect", "out_of_book")
        cand = route(q, nodes)
        has_guard = any(k in q for k in GUARDRAIL_KEYS)
        has_crisis = any(k in q for k in CRISIS_KEYS)
        note = ""
        if kind == "guardrail":
            note = "차단키워드O" if has_guard or has_crisis else "차단키워드X(검토)"
        else:  # out_of_book
            if cand:
                note = f"노드매칭됨(검토): {cand[:2]}"
                leak += 1
            else:
                note = "매칭없음(정상)"
        print(f"  {kind:11s} Q{i:02d} [{note}]  {q}")
    print(f"  → out_of_book 오매칭 {leak}건\n")

    # --- 판정 ---
    ok = (miss_node == 0)
    print("=== 판정 ===")
    print(f"  expect_nodes 무결성: {'PASS' if miss_node==0 else 'FAIL('+str(miss_node)+')'}")
    print(f"  in_book 라우팅 도달: {route_hit}/{len(in_book)}")
    print("  (S2 환각억제·S3 근거표기·S5 개인화의 최종 판정은 라이브 세션 평가 필요)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
