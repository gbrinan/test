# anandara.ai 이식용 권한 구조 설계 (미적용 · 설정으로 결정)

> 상태: **설계만**. anandara 코드에 아직 아무것도 넣지 않음.
> 원칙: "어떻게 적용할지"는 전부 `access.config`의 토글/어댑터 선택으로 **나중에 결정**한다.
> 참고 제약: anandara는 Next.js + 프록시 환경이며 프록시가 **Server Action을 차단**한 이력이 있음
> → 서버 강제는 Server Action이 아니라 **Route Handler(`app/api/...`)** 기준으로 설계.

---

## 1. 권한 모델 (개념)

두 개의 **독립된 게이트**가 곱해져 접근을 결정한다.

| 게이트 | 질문 | 근거 데이터 | 위변조 위험 |
|---|---|---|---|
| A. 진행 게이트 | "직전 챕터 테스트를 통과했나?" | `progress.passed[]` | 낮음(학습 순서일 뿐) |
| B. 등급 게이트 | "내 등급 ≥ 챕터 요구 등급인가?" | `entitlement.tier` | **높음(결제 자산)** |

접근 가능 = `A && B`. 게이트 A는 클라이언트에 둬도 무방(무단 진도는 손해가 아님). **게이트 B는 반드시 서버가 최종 판정**해야 함(돈).

### 등급 ↔ 구간 매핑 (현재 확정본)
| tier | 이름 | 가격(예시) | 구간 |
|---|---|---|---|
| 0 | 무료 맛보기 | ₩0 | PART 1 |
| 1 | 초급 | ₩33,000 | PART 2·3 |
| 2 | 중급 | ₩66,000 | PART 4·5·6 |
| 3 | 고급 | ₩150,000 | PART 7 + 케이스 볼트 |

누적: 상위 등급은 하위 포함.

---

## 2. 적용을 뒤로 미루는 설정 (`access.config`)

이식 시점에 이 객체의 값만 정하면 "어떻게 적용되는지"가 결정된다. 코드 재작성 불필요.

```jsonc
{
  // 어디서 잠그나: 데모는 client, 실서비스는 server 권장
  "enforcement": "client" | "server",

  // 프리미엄 본문을 어떻게 내려주나
  //  inline          = 지금 데모(모든 본문이 HTML에 있음, 소스에 노출됨)
  //  lazy-protected  = 잠긴 본문은 서버가 등급 확인 후 API로 내려줌(권장)
  "contentDelivery": "inline" | "lazy-protected",

  // 로그인 주체 — 실제 값은 anandara 것으로 결정
  "authAdapter": "none" | "anandara-session" | "supabase" | "custom",

  // 등급(구매 자산) 저장소
  "entitlementStore": "localStorage" | "server-db",

  // 결제 게이트웨이
  "paymentProvider": "portone",

  // 진행 상태 저장소 (게이트 A)
  "progressStore": "localStorage" | "server-db",

  // 데이터
  "tiers": [ /* 위 표 */ ],
  "partTierMap": { "PART 1": 0, "PART 2": 1, "PART 3": 1, "PART 4": 2, "PART 5": 2, "PART 6": 2, "PART 7": 3, "CASE VAULT": 3 }
}
```

### 권장 프리셋
- **demo** (지금): `enforcement:client · contentDelivery:inline · authAdapter:none · entitlementStore:localStorage`
- **anandara-prod**: `enforcement:server · contentDelivery:lazy-protected · authAdapter:anandara-session · entitlementStore:server-db · progressStore:server-db`

---

## 3. 어댑터 인터페이스 (구현체는 나중에 선택)

각 어댑터는 계약(시그니처)만 고정하고, 구체 구현은 config 선택으로 갈아끼운다.

```ts
interface AuthAdapter {
  getUser(): Promise<{ id: string } | null>;   // 비로그인 null
  requireLogin(): Promise<void>;               // 필요 시 로그인 유도
}
interface EntitlementAdapter {
  getTier(userId?: string): Promise<0|1|2|3>;         // 서버 판정값
  grantTier(userId: string, tier: 0|1|2|3): Promise<void>; // 누적 저장
}
interface ProgressAdapter {
  getPassed(userId?: string): Promise<string[]>;
  markPassed(userId: string, chapterId: string): Promise<void>;
}
interface ContentAdapter {
  // lazy-protected 일 때만 서버 왕복. inline 이면 로컬 데이터 반환.
  getChapter(id: string, userTier: number): Promise<ChapterBody | { locked: true }>;
}
interface PaymentAdapter {
  start(tier: number): Promise<{ paymentId: string } | { failed: string }>;
  verify(paymentId: string, expectedAmount: number): Promise<{ ok: boolean; tier?: number }>;
}
```

데모의 현재 코드는 이 인터페이스의 `*-localStorage`, `portone` 구현에 해당한다.
anandara 적용 = 같은 인터페이스의 `*-server` 구현을 골라 config에서 지정하는 것.

---

## 4. anandara(Next.js) 바인딩 옵션 — **선택 미정**

| 항목 | 옵션 A (권장) | 옵션 B | 결정 |
|---|---|---|---|
| 인증 | anandara 기존 세션 재사용 | 별도 Supabase Auth | ☐ |
| 잠금 지점 | Route Handler `app/api/lesson/[id]` 에서 등급 확인 후 본문 반환 | 미들웨어에서 라우트 통째 차단 | ☐ |
| 등급 저장 | anandara DB의 `entitlements` 테이블 | Supabase 테이블 | ☐ |
| 결제 검증 | `app/api/verify-payment` Route Handler (Server Action 아님 — 프록시 차단 회피) | 외부 함수 | ☐ |
| 콘텐츠 위치 | 프리미엄 본문 = 서버 전용(빌드 시 클라 번들 제외) | 클라 포함(비권장) | ☐ |
| 진입 방식 | anandara 하위 라우트 `/learn` 로 신규 페이지 | 기존 페이지에 임베드 | ☐ |

⚠ 재확인 항목: 프록시 basePath / Origin 허용목록 / 정적 자산 경로 — anandara 프록시 설정과 충돌 없는지 이식 직전 점검(과거 Server Action 차단 사례 참고).

---

## 5. 콘텐츠 노출 위험 표 (지금 데모 → 실서비스 갭)

| 위험 | 현재(demo) | 실서비스 요구 |
|---|---|---|
| 프리미엄 본문이 페이지 소스에 노출 | 있음(inline) | lazy-protected 로 제거 |
| 등급을 클라가 자칭 | localStorage 조작 가능 | 서버가 결제금액→등급 판정(이미 verify에 반영) |
| 진행상태 기기 간 유지·환불 대응 | 불가(localStorage) | server-db 필요 |
| paymentId 중복 지급 | 미처리 | DB 멱등 처리 필요 |

---

## 6. 결정 체크리스트 (여기만 채우면 적용 가능)

- [ ] enforcement: client / **server**
- [ ] contentDelivery: inline / **lazy-protected**
- [ ] authAdapter: anandara-session / supabase / custom
- [ ] entitlementStore & progressStore: server-db 스키마 확정
- [ ] 가격 확정: ₩33,000 / 66,000 / 150,000 (2026-07-20 고급 인상 확정) → 프론트 TIERS + 서버 AMOUNT_TO_TIER 동기화
- [ ] 케이스 볼트를 고급 포함 vs 별도 애드온으로 팔지
- [ ] anandara 진입 라우트 경로(/learn 등)
