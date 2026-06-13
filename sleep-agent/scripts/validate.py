#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate.py — 무결성 체크 단독 실행용 (index.md 생성 없이 검증만).

build_index.py 의 검증 게이트를 재사용한다. CI/pre-commit 에서 빠르게 호출.
  실행 예) uv run --with pyyaml python scripts/validate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_index import load_nodes, validate  # noqa: E402


def main() -> int:
    nodes_dir = Path(__file__).resolve().parent.parent / "ontology" / "nodes"
    if not nodes_dir.is_dir():
        sys.stderr.write(f"[validate] nodes 디렉토리 없음: {nodes_dir}\n")
        return 2
    nodes = load_nodes(nodes_dir)
    errors = validate(nodes)
    if errors:
        sys.stderr.write(f"[검증 실패] {len(errors)}건:\n")
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        return 1
    print(f"[validate] 노드 {len(nodes)}개 — 검증 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
