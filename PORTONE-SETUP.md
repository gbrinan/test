# 클로드 완전정복 데모 — 테스트 게이트 + 포트원 결제 셋업

## 파일 구성
- `claude-guide-demo.html` — 학습 페이지(챕터→퀴즈→다음 잠금 해제 + 페이월)
- `api/verify-payment.js` — 포트원 결제 검증 서버리스 함수(Vercel)

## 동작 방식
1. 각 챕터 하단에 통과 테스트(객관식). **모두 정답이면** 다음 챕터가 열림(localStorage 저장).
2. 챕터마다 요구 **등급(tier)** 이 있어, 내 등급이 낮으면 **등급 페이월**이 뜸.
3. 결제 성공 → 서버 검증 통과 → `S.tier` 상향 → 해당 등급 이하 챕터 전체 잠금 해제.

## 등급 체계 (누적 — 상위가 하위를 포함)
| 등급(tier) | 가격(예시) | 열리는 구간 |
|---|---|---|
| 0 무료 맛보기 | ₩0 | PART 1 · AI 이해 |
| 1 초급 | ₩33,000 | PART 2 대화형 기본기 + PART 3 Cowork 셋업 |
| 2 중급 | ₩66,000 | + PART 4 스킬 만들기 + PART 5 에이전트 + PART 6 만들기 |
| 3 고급 | ₩150,000 | + PART 7 자동화 시스템 + 케이스 볼트 7종 |

- 가격은 `claude-guide-demo.html`의 `TIERS` 와 `api/verify-payment.js`의 `AMOUNT_TO_TIER` **두 곳을 반드시 일치**시킬 것.
- 서버는 실제 결제 금액으로 등급을 판정해 돌려줌(클라이언트가 보낸 등급을 신뢰하지 않음).

## 지금 바로 확인 (테스트 모드)
`claude-guide-demo.html`의 `PAY.TEST_MODE = true` 상태에서는 실제 결제 없이 성공을
시뮬레이션합니다. 파일을 브라우저로 열어 퀴즈 통과 → 페이월 → "결제" 흐름을 확인하세요.

## 실제 포트원 연동 (4단계)
1. **키 발급**: 포트원 관리자콘솔(admin.portone.io) → 상점/채널 생성 →
   `상점 ID(store-...)`, `채널 키(channel-key-...)`, `V2 API Secret` 확보.
2. **프론트 설정**: `claude-guide-demo.html`의 `PAY` 객체에서
   `STORE_ID`, `CHANNEL_KEY` 를 실제 값으로 바꾸고 `TEST_MODE = false`.
3. **서버 시크릿**: Vercel 프로젝트 → Settings → Environment Variables 에
   `PORTONE_API_SECRET` = (V2 API Secret) 등록. **이 값은 절대 프론트/깃에 넣지 말 것.**
4. **배포**: 저장소를 Vercel에 연결해 배포하면 `/api/verify-payment` 가 자동 활성화됨.

## 운영 전 반드시 보완할 것 (현재는 골자만)
- **중복 지급 방지**: 같은 `paymentId` 재사용 차단 — DB(예: Supabase)에 처리 기록.
- **사용자 계정 연동**: 지금은 entitlement 를 브라우저 localStorage 에만 저장해
  기기를 바꾸면 풀림. 실제로는 로그인 + 서버(Supabase 등)에 구매 상태를 저장해야 함.
- **웹훅**: 가상계좌 입금 등 지연 결제는 포트원 웹훅으로 별도 확정 처리 권장.
- 참고 문서: https://developers.portone.io/opi/ko/integration/start/v2/checkout

## 주의
결제 자격증명(계정·API Secret)은 사용자가 직접 발급·입력해야 합니다.
이 코드는 연동 구조(스캐폴드)이며, 실제 상점 키를 꽂고 위 보완 항목을 채워야 운영 가능합니다.
