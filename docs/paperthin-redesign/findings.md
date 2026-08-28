# Findings & Decisions

> **기술적 발견, 중요한 결정이 있을 때마다 이 파일을 즉시 업데이트하세요.**

## Requirements

- paperthin 철학으로 soloforce 재설계
- 파일 기반 계획 워크플로우(ahastudio)로 계획·진행 관리
- PR은 `pr` 리모트(gbrinan/soloforce2)로 제출

## Research Findings

### paperthin 핵심 철학 (CLAUDE.md 정독)

- **Trust the artifact, not the author**: 만든 사람의 세션 내 판단은 최악의 심판. 스킬은 (1) 현재 진실로부터 재도출하거나 (2) 외부 시선(fresh sub-session)을 수입해 검증한다.
- **SSOT + 자기완결 스킬**: 사실은 한 곳에만 살고 나머지는 참조. 단, 스킬은 단독 설치·실행되므로 필요한 런타임 규칙은 인라인으로 품는다(두 원칙은 다른 레이어).
- **Restraint(절제)**: 개선할 게 없으면 아무것도 바꾸지 않는다. 적은 slop(노이즈·중복·패딩)이지 추가 자체가 아니다.
- **Recursive**: 스킬로 스킬을 유지보수한다. 모든 패스가 자기 도구로 감사받는다.
- **negatives-as-corpus**: "삭제"는 아카이브 이동. 실패한 가지는 훈련 데이터다.
- **Generic examples, not instances**: 영속 문서에는 실제 PR번호·SHA 대신 `(#123, @handle)` 류의 제네릭 예시만.

### 스킬 분류 체계: cardinality × time 4상한

| 폴더 | 역할 | 스킬 |
| --- | --- | --- |
| depth/ | 손에 든 것 하나를 정제·검증 | re0, readchk, aim, modelchk, hate, macrothink, feynman, autobahn, reorder, detool, dedash, debloat, shower, factchk, mandela, sip, re0-git, re0-release, re0-merge |
| breadth/ | 하나의 진실을 여러 파일·플랫폼에 걸쳐 정합 | ssotize, re0-upgrade |
| coil/ | 빌드 사이클 간 학습 전달 | re0-plan, re0-loop, re0-memo, re0-work, catchup, nba |
| mesh/ | 독립 시점들을 수렴 | prism |

### 스킬별 요점 (28개 라인 바이 라인 정독)

- **re0** (창립 스킬): 아티팩트를 "첫 깨끗한 v0"처럼 재작성. changelog 흔적 제거, "무엇이 바뀌었나"→"지금 무엇이 참인가"로 변환. 개선 없으면 무변경.
- **readchk**: 작업 전 지시 이해 검증. 패러프레이즈로 재진술, 컨텍스트가 해소하면 침묵 통과, 진짜 갈림길만 1개씩 질문.
- **aim**: 데이터만 오고 요청이 얇을 때, 질문 대신 "의도 제안"을 해 사용자가 yes로 답하게.
- **modelchk**: 실행 전 비용 산정 — capability tier(fast/standard/frontier) × reasoning effort(glance/measured/thorough/exhaustive). 권고만, 라우팅 권한 없음.
- **hate** (user-invoked): 계획을 죽이려는 관점에서 공격, 단 하나의 root 반론 + 가장 싼 반증 실험(first nail)만 반환. 체크리스트 금지.
- **macrothink** (user-invoked): 세션 프레이밍 제거 후 2~5개 fresh read 팬아웃. divergence가 신호, convergence는 안심일 뿐 증명 아님.
- **feynman** (user-invoked): 방금 내린 결정을 격리된 비평자가 압박 — 본인 말로 설명 못 하면 갭으로 명명. rationale을 먼저 제공하지 않음.
- **autobahn**: 가드레일 인접 스코프를 carve해 안전한 나머지만 fresh subagent에 전달(carved prompt만, 원본 금지). descope ledger로 가시화. 회피가 아니라 제거.
- **reorder** (user-invoked): 나열 순서를 단일 원칙으로 재정렬. 이동만, 문구 변경 금지.
- **detool**: 영속 문서에서 우발적 스택 결합(벤더·모델·경로 명사)을 메커니즘으로 치환. provenance·runbook·도구가 주어인 주장은 구체성 유지. "mechanism, not euphemism".
- **dedash** (user-invoked): em-dash를 문법 역할별로 치환(콤마/콜론/마침표/재작성). 범위는 사용자 소유, 범위 확장 금지.
- **debloat** (user-invoked): 축적된 패딩·과잉 한정·융합 문장 압축. load-bearing 주장은 전부 보존.
- **shower**: zero-context sub-session이 콜드리드해 자립성 진단. 진단만, 수정은 본 세션.
- **factchk**: 현실 근거 주장을 외부 소스로 양방향 검증(황당한 게 사실일 수도, 자명한 게 거짓일 수도). 메타인지적 의심이 트리거.
- **mandela**: 검증(eval/metric/실험)의 leakage 감사 — 8패턴(암기, 잘못된 귀무가설, 공유 환각, 동어반복, 검증자=설계자, 공유 풀 편향, 프레임 주입, 요구 특성). 읽기 전용.
- **sip**: 산출물 완성 직후 자기 스킬들로 맛보기 — shower→factchk/mandela→ssotize→detool→re0 오케스트레이션. user-invoked 스킬은 절대 자동 호출 안 함.
- **re0-git** (user-invoked): 커밋 메시지를 commit-economy로 재작성(진짜 변경당 불릿 1개, diff가 증명하는 것 생략, 트리 불변, gpg 서명, HEAD만 날짜 갱신).
- **re0-release** (user-invoked): 배포 체크리스트 — kind not size 버전 판정(fix→patch, 새 능력→minor), 2단 확인(커밋 / 태그+푸시), 워크플로우 소유 단계 수동 실행 금지.
- **re0-merge** (user-invoked): 외부 기여 착륙 — 기본 거절(default-deny), authorship 보존, land/pr-<n> 브랜치, 승인은 수락 시점에, 크레딧 코멘트로 종료.
- **ssotize**: 흩어진 사실을 감사(읽기 전용)→승인→통합. 정본 지정, 사본은 참조로 치환, 모순은 인간 판단으로 분리.
- **re0-upgrade** (user-invoked): 설치본을 전체 카탈로그로 수렴. rename SSOT 표, shadow install 감지, 확인 게이트 후에만 변경.
- **re0-plan** (user-invoked): 사이클 개시 시 `.re0/iteration/<version>-<workname>/` 생성과 동시에 내용 기록(빈 폴더 금지). lightweight→RETRO 씨앗, full→DESIGN/WORKFLOW/EVIDENCE.
- **re0-loop**: FRAME→BUILD→DRIVE→RE0-MEMO→HATE→RE0-WORK→BUILD AGAIN 사이클. 진행 단위는 시간·기능이 아니라 품질 통과 템플릿·재사용 모듈·제거된 안티패턴 수.
- **re0-memo**: 사이클을 이식 가능한 교훈·안티패턴·게이트로 변환. 개별 불만을 패턴으로 일반화(specifics는 증거로만), changelog 금지.
- **re0-work**: v0 재시작 — 계약·스키마·게이트·어휘·real-surface 테스트·negative corpus만 보존, 우발적 아키텍처는 복사 금지. 수직 루프 1개부터.
- **catchup**: 공백 후 복귀한 인간의 컨텍스트 재구축. 상태 기반(기억 아님), 결정 순서 구성(Needs you→Changed→New words), 읽기 전용.
- **nba**: 정체된 사이클의 단일 최고 레버리지 다음 행동 반환. 메뉴 금지, 상태 근거 필수, 회피 중인 행동을 반환.
- **prism** (user-invoked): 2~5개 독립 렌즈(고유 실패 모드당 1개)로 분할, 수렴/발산과 발산을 해소할 단일 질문 반환. 평균화 금지.

### 횡단 규약 3종 (인라인 복제, CLAUDE.md가 지도)

- **edit-safety**: 타깃 존재 확인(MISS 보고), unicode-safe(PYTHONUTF8=1), 발생 위치별 치환(일괄 스윕 금지), 구조 이동은 스크립트로.
- **negatives-as-corpus**: 삭제 대신 아카이브.
- **commit-economy**: re0-git이 정본, re0-release가 인라인 복제.

### invocation 이분법

- 기본은 model-invoked. `disable-model-invocation: true`는 (1) 트리거가 인간의 의도적 행동(commit/push/publish)이거나 (2) 존재 자체가 에이전트를 편향시킬 때만(hate, feynman 등).
- user-invoked 스킬은 model-invoked를 부를 수 있으나 user-invoked끼리 자동 호출 금지(유일 예외 페어링: re0-plan↔re0-release).

### file-based-planning-workflow (ahastudio) 구조

- 기능 폴더당 6문서: README(개요) / spec(PRD, 기술 배제) / plan(구현 계획, Critical Files, Outside-In 아키텍처) / tasks(Phase별 체크박스, Current Phase 표시) / findings(발견·결정 즉시 기록) / progress(세션별 시간순 로그).
- Phase: 1 Requirements & Discovery → 2 Planning & Structure → 3 Implementation → 4 Testing.

## Resources

### 문서

- [paperthin](https://github.com/LilMGenius/paperthin)
- [file-based-planning-workflow](https://github.com/ahastudio/file-based-planning-workflow)
- [워크플로우 원문 설명](https://github.com/ahastudio/til/blob/main/ai/file-based-planning-workflow.md)

### 코드 참조

- 리모트: origin=gbrinan/test, pr=gbrinan/soloforce2
- 스크래치패드 클론: paperthin / fbpw / soloforce (세션 임시)

## Decisions

- 이 리포에 `templates/`(fbpw 템플릿 원본)와 `docs/<기능명>/` 구조를 채택한다.
- 첫 기능 폴더는 `docs/paperthin-redesign/`로, soloforce 재설계 계획을 여기서 관리한다.
