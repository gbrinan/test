#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_index.py — nodes/ -> index.md 생성 + 검증 게이트 + S1 커버리지 리포트.

단일 진실원천은 ontology/nodes/*.md 이며, 이 스크립트가 index.md 를 파생 생성한다.
index.md 는 절대 손으로 편집하지 않는다 (DO NOT EDIT).

의존성: PyYAML (frontmatter 파싱).
  실행 예) uv run --with pyyaml python scripts/build_index.py
          또는  pip install pyyaml 후  python scripts/build_index.py

종료코드: 검증 실패 시 1 (비정상 종료). --strict 옵션 시 커버리지 결손도 실패.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "[build_index] PyYAML 이 필요합니다.\n"
        "  uv run --with pyyaml python scripts/build_index.py\n"
        "  또는  pip install pyyaml\n"
    )
    sys.exit(2)

# --- schema.md 와 동기화되는 상수 (단일 진실원천: schema.md) -----------------
TYPES = {"생리기전", "실천행동", "영향요인", "생애단계"}
EVIDENCE = {"일반원칙", "저자_개인경험", "논쟁중"}
# 닫힌 관계 어휘 8종 (능동) -> 역술어(표시 라벨)
REVERSE_PREDICATE = {
    "증가시킨다": "증가됨",
    "감소시킨다": "감소됨",
    "원료가_된다": "원료를_가짐",
    "선행한다": "후행함",
    "권장한다": "권장됨",
    "주의한다": "주의대상",
    "측정지표": "측정대상",
    "반례": "반례대상",
}
PREDICATES = set(REVERSE_PREDICATE)
ID_RE = re.compile(r"^[가-힣A-Za-z0-9_]+$")
# 본문 인용에서 절 식별: "260608 §6-1" / "260528 §5" -> ("260608", "6-1")
SECTION_RE = re.compile(r"(26060?8|260528)\s*§\s*([0-9]+(?:-[0-9]+)?)")

# S1 커버리지 대상 절 (본문 2~8장)
TARGET_SECTIONS = [
    "2-1", "2-2", "2-3",
    "3-1", "3-2", "3-3", "3-4", "3-5",
    "4-1", "4-2", "4-3",
    "5-1", "5-2", "5-3", "5-4",
    "6-1", "6-2",
    "7-1", "7-2", "7-3",
    "8",
]


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    """노드 파일에서 frontmatter(dict)와 본문(str)을 분리한다."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: frontmatter(---) 없음")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: frontmatter 구분자(---) 부족")
    data = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()
    return data, body


def load_nodes(nodes_dir: Path) -> dict[str, dict]:
    nodes: dict[str, dict] = {}
    for path in sorted(nodes_dir.glob("*.md")):
        data, body = parse_frontmatter(path)
        data["_file"] = path.name
        data["_stem"] = path.stem
        data["_body"] = body
        nodes[path.stem] = data
    return nodes


def validate(nodes: dict[str, dict]) -> list[str]:
    """검증 게이트. 위반 메시지 리스트 반환(비면 통과)."""
    errors: list[str] = []
    alias_owner: dict[str, str] = {}
    ids = set(nodes)

    for stem, n in nodes.items():
        nid = n.get("id")
        # 1) id 규칙 + 파일명 일치
        if nid is None:
            errors.append(f"{n['_file']}: id 누락")
            continue
        if not ID_RE.match(str(nid)):
            errors.append(f"{n['_file']}: id 정규식 위반 '{nid}'")
        if str(nid) != stem:
            errors.append(f"{n['_file']}: 파일명≠id (id={nid})")
        # 2) type
        if n.get("type") not in TYPES:
            errors.append(f"{n['_file']}: type 위반 '{n.get('type')}'")
        # 3) evidence
        if n.get("evidence") not in EVIDENCE:
            errors.append(f"{n['_file']}: evidence 위반 '{n.get('evidence')}'")
        # 4) aliases 중복
        for a in n.get("aliases") or []:
            key = str(a).strip()
            if key in alias_owner and alias_owner[key] != stem:
                errors.append(
                    f"{n['_file']}: alias 중복 '{key}' (이미 {alias_owner[key]} 소유)"
                )
            else:
                alias_owner[key] = stem
        # 5) relations: 술어 어휘 + 타깃 존재
        for rel in n.get("relations") or []:
            if not (isinstance(rel, list) and len(rel) == 2):
                errors.append(f"{n['_file']}: 관계 형식 오류 {rel!r}")
                continue
            pred, target = str(rel[0]).strip(), str(rel[1]).strip()
            if pred not in PREDICATES:
                errors.append(f"{n['_file']}: 닫힌 어휘 위반 술어 '{pred}'")
            if target not in ids:
                errors.append(f"{n['_file']}: 깨진 참조 '{pred}→{target}' (대상 노드 없음)")
    return errors


def build_reverse(nodes: dict[str, dict]) -> dict[str, list[tuple[str, str]]]:
    """대상 노드 -> [(역술어라벨, 출처노드)] 역관계 맵."""
    reverse: dict[str, list[tuple[str, str]]] = {k: [] for k in nodes}
    for stem, n in nodes.items():
        for rel in n.get("relations") or []:
            if isinstance(rel, list) and len(rel) == 2:
                pred, target = str(rel[0]).strip(), str(rel[1]).strip()
                if pred in REVERSE_PREDICATE and target in reverse:
                    reverse[target].append((REVERSE_PREDICATE[pred], stem))
    return reverse


def section_coverage(nodes: dict[str, dict]) -> dict[str, int]:
    """각 절(§)을 인용한 노드 수. 장 단위 인용(§5)은 그 장의 모든 절에 가산."""
    cov = {s: 0 for s in TARGET_SECTIONS}
    for n in nodes.values():
        cited: set[str] = set()
        for s in n.get("sources") or []:
            m = SECTION_RE.search(str(s))
            if not m:
                continue
            sec = m.group(2)
            if "-" in sec:  # 정확한 절
                cited.add(sec)
            else:  # 장 단위 -> 해당 장의 모든 타깃 절
                for t in TARGET_SECTIONS:
                    if t == sec or t.startswith(sec + "-"):
                        cited.add(t)
        for sec in cited:
            if sec in cov:
                cov[sec] += 1
    return cov


def render_index(nodes: dict[str, dict], reverse: dict) -> str:
    lines = ["# Ontology Index (AUTO-GENERATED by build_index.py — DO NOT EDIT)", ""]
    for stem in sorted(nodes):
        n = nodes[stem]
        lines.append(f"## {n['id']} [{n.get('type', '?')}]")
        aliases = ", ".join(str(a) for a in (n.get("aliases") or []))
        if aliases:
            lines.append(f"별칭: {aliases}")
        lines.append(f"요약: {n.get('summary', '')}")
        rels = n.get("relations") or []
        if rels:
            grouped: dict[str, list[str]] = {}
            for rel in rels:
                if isinstance(rel, list) and len(rel) == 2:
                    grouped.setdefault(str(rel[0]), []).append(str(rel[1]))
            parts = [f"{p}→{','.join(ts)}" for p, ts in grouped.items()]
            lines.append("관계: " + " · ".join(parts))
        rev = reverse.get(stem) or []
        if rev:
            parts = [f"{src}←({lbl})" for lbl, src in rev]
            lines.append("역관계: " + " · ".join(parts))
        srcs = " / ".join(str(s) for s in (n.get("sources") or []))
        lines.append(f"근거: {srcs} / {n.get('evidence', '')}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="ontology 루트 (기본: 스크립트의 ../ontology)")
    ap.add_argument("--check", action="store_true", help="index.md 생성 없이 검증만")
    ap.add_argument("--strict", action="store_true", help="커버리지 결손도 실패 처리")
    args = ap.parse_args()

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent / "ontology"
    nodes_dir = root / "nodes"
    if not nodes_dir.is_dir():
        sys.stderr.write(f"[build_index] nodes 디렉토리 없음: {nodes_dir}\n")
        return 2

    nodes = load_nodes(nodes_dir)
    print(f"[build_index] 노드 {len(nodes)}개 로드")

    errors = validate(nodes)
    if errors:
        sys.stderr.write(f"\n[검증 실패] {len(errors)}건:\n")
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        return 1
    print("[build_index] 검증 통과 (어휘·참조·id·evidence·alias)")

    # S1 커버리지 리포트
    cov = section_coverage(nodes)
    missing = [s for s, c in cov.items() if c == 0]
    print("\n[S1 커버리지] 절별 인용 노드 수:")
    print("  " + "  ".join(f"{s}:{cov[s]}" for s in TARGET_SECTIONS))
    if missing:
        print(f"[S1 경고] 인용 0인 절 {len(missing)}개: {', '.join(missing)}")
    else:
        print("[S1] 2~8장 전 절 커버 OK")

    if args.check:
        print("[build_index] --check: index.md 미생성")
        return 1 if (args.strict and missing) else 0

    reverse = build_reverse(nodes)
    index_text = render_index(nodes, reverse)
    (root / "index.md").write_text(index_text, encoding="utf-8")
    print(f"[build_index] index.md 생성 완료 ({len(nodes)} 노드)")

    if args.strict and missing:
        sys.stderr.write("[strict] 커버리지 결손으로 실패\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
