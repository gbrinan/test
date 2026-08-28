# Tasks: soloforce paperthin 재설계

## Goal

paperthin 5축 철학(아티팩트 신뢰·SSOT·절제·재귀 검증·negatives-as-corpus)을 soloforce의 문서·구조·운영 규약에 이식한다. 동작은 보존한다.

## Current Phase

🔄 Phase 1: Requirements & Discovery

## Phases

### Phase 1: Requirements & Discovery 🔄

- [x] paperthin 28개 스킬 정독 (findings.md)
- [x] fbpw 워크플로우 구조 세팅
- [x] 스킬 설치 (hate, re0-plan, ssotize)
- [x] 스펙 초안 작성 (spec.md)
- [ ] /hate — 재설계 계획 공격 (root 반론 + first nail)
- [ ] 스펙 리뷰 및 승인

### Phase 2: Planning & Structure ⏸️

- [ ] /re0-plan — 사이클 casebook 개설
- [ ] /ssotize — README 4종 + 설정값 SSOT 감사 (읽기 전용)
- [ ] apps/ 생사 판정 기준 정의
- [ ] 구현 계획 작성 (plan.md)

### Phase 3: Implementation ⏸️

- [ ] SSOT 통합 실행 (승인된 계획만)
- [ ] apps/ 아카이브 이동 (cause of death 기록)
- [ ] 핵심 문서 re0 패스
- [ ] 운영 규약 CLAUDE.md 반영

### Phase 4: Testing ⏸️

- [ ] 콜드리드(shower) 검증 — README·온보딩
- [ ] 동작 보존 확인 (npm start·핵심 플로우)
- [ ] 성공 기준 4항 점검 (spec.md)
- [ ] pr 리모트(soloforce2)로 PR 제출
