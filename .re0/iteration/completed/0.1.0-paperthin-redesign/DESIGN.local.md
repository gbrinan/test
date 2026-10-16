# DESIGN — soloforce paperthin 재설계 (0.1.0, 버전 잠정)

## Thesis

soloforce(MyCrew)의 문서·구조·운영 규약에 paperthin 5축 철학을 이식한다. 기능 동작은 보존한다. 정본 스펙: docs/paperthin-redesign/spec.md (이 파일은 사이클 케이스북 — 스펙의 사본이 아니라 실행 관점 기록).

## Scope

- In: README 4종 SSOT 통합, apps/ 생사 판정·아카이브, 핵심 문서 re0 패스, 운영 규약 CLAUDE.md 반영
- Out: 신규 기능, src 리팩토링(2차 사이클), soloforce2 병합 전략

## Quality Gates

1. SSOT: 임의 운영 사실 5개 → 정본 1곳으로 답해짐
2. 콜드리드: zero-context 서브세션이 README만으로 설치~실행 재서술
3. apps/ 판정표 미분류 0건, archive는 이동+사유 기록
4. 감사→승인→실행 흔적이 커밋에 남음
5. CLAUDE.md/README 반영 게이트: 메커니즘은 CLAUDE.md, 사용자 대면은 README — 레지스터 혼입 금지
