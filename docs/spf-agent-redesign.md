# SPF 에이전트 개선 설계서 — CMS 시스템 역설계 기반

> 작성일: 2026-07-27
> 대상: my crew (`C:\mycrew`) SPF 에이전트군 (spf-sales / spf-logistics / spf-news-scout)
> 근거: 영업 CMS 스크린샷 2종 역설계 + 웹 리서치(리캐치·Salesmap·Badger Maps·SPOTIO·HubSpot/Pipedrive) + my crew 현행 구조 전수 조사

---

## 1. 스크린샷 역설계: 이 CMS가 실제로 하는 일

### 화면 1 — 영업 활동 지도 (영업/매출 탭)

필드 영업 활동의 자동 기록 시스템.

- **데이터 소스**: 휴대폰 GPS(35건/일), 통화 기록(8건·통화시간), 문자 기록(17건)을 백그라운드 수집
- **처리**: GPS 궤적 → 체류지 감지(cluster) → "방문" 자동 판정(6곳), 체류시간 산출, 이동거리 합산(122.6km)
- **표현**: Leaflet+OSM 지도에 방향 화살표 궤적 + 번호 클러스터 마커, 우측 방문/통화/문자 통합 타임라인(전체/방문/통화/문자 필터), 날짜 네비게이션("오늘"/"최근 이동일")

### 화면 2 — 카카오톡 소통 탭

개인 카톡 전체를 주기 수집·분류하는 시스템.

- **수집**: 데이터 기간 10년치(2016~2026), "마지막 수집 2026-07-26 14:20" 표시 → 주기적 배치 수집 파이프라인 존재
- **분류**: 총 89,354건 중 "중요 메시지" 852건을 **기관·채무·사법** 규칙으로 자동 태깅. 삭제 메시지도 휴지통(14,887건)으로 보존
- **조회**: 내용·방·보낸이 검색 + 분류/기간 필터, 중요만 보기, 대화방 랭킹, 신규 유입 카운터(24h / 30일 949건)

### 핵심 통찰

이 시스템의 본질은 **"영업자의 디지털 발자국(카톡·GPS·통화·문자)을 전량 수집 → 규칙/분류로 중요한 것만 떠올리기"**다. 다만 이 CMS에 없는 것이 둘 있다:

1. 넥스트 액션(할 일) 자동 추출
2. 파이프라인 연결

개선 설계에서 이 둘이 my crew SPF의 차별점이 된다.

---

## 2. 현행 my crew SPF 진단 (As-Is)

| 구성요소 | 현재 상태 |
|---|---|
| 에이전트 3기 | `spf-sales`(리드 발굴·스코어링·콜드메일), `spf-logistics`(콜드체인 배송 상태머신), `spf-news-scout`(뉴스 정찰 워커) |
| 루프 4개 | 메일스캔(08:20) → 아침브리핑(08:40) → 주간뉴스(월 08:00) → 물류감시(14:00). 텔레그램/디스코드 발송, `[[QUIET]]` 센티넬 |
| 시스템 오브 레코드 | Notion 2개 DB — 영업 리드 ↔ 물류 배송 (relation 연결) |
| 관련 자산 | `apps/leads`(SQLite 칸반 미니 CRM, 포트 13208), `apps/mymaps`(Google My Maps 클론, 포트 13211, MapTiler+Google Maps), `apps/isenssign` 내 카카오 알림톡 클라이언트(`KakaoAlimtalkClient`) |

### 갭 분석 (스크린샷 CMS 대비)

1. **카카오톡 수집·분류 — 전무**. 알림톡(발신) 클라이언트만 있고 수신·수집은 없음
2. **지도** — mymaps는 "지도 그리기" 앱이지 영업활동(방문·체크인·타임라인) 지도가 아님
3. **대시보드** — `apps/spf` 콘솔은 외부 Vercel iframe이고 파이프라인 데이터(Notion)와 미연결. leads 앱과 SPF Notion DB는 서로 다른 저장소로 이원화

---

## 3. 개선 목표 아키텍처 (To-Be)

```
┌─ 수집 계층 ──────────────────────────────────────────┐
│ 카톡 내보내기(.txt) 업로드 → kakao-parser            │
│ (선택) Android 알림 리스너 → 실시간 보조 채널        │
│ Gmail(기존 spf-mail-scan) · GPS/방문 수동 체크인     │
└──────────────┬───────────────────────────────────────┘
┌─ 저장 계층 ──▼───────────────────────────────────────┐
│ apps/spf-hub/data/spf.sqlite  (메시지·방문·활동 원장)│
│  - 민감정보 마스킹(계좌·주민번호) 후 저장, 원문 암호화│
│ Notion 리드/배송 DB = 파이프라인 정본 (기존 유지)    │
└──────────────┬───────────────────────────────────────┘
┌─ 지능 계층 ──▼───────────────────────────────────────┐
│ spf-comms 에이전트(신설): 2단계 분류 → 라벨+긴급도   │
│  → 넥스트 액션 4유형 추출 → Notion 리드 '다음 액션'  │
│ spf-sales / spf-logistics (기존 유지, 입력 소스 확장)│
└──────────────┬───────────────────────────────────────┘
┌─ 표면 계층 ──▼───────────────────────────────────────┐
│ apps/spf-hub: ①소통 탭 ②지도 탭 ③파이프라인 대시보드 │
│ 루프: spf-kakao-brief(08:30) → 텔레그램 다이제스트   │
└──────────────────────────────────────────────────────┘
```

### 모듈 A — 카카오톡 인제스트 (요구사항 1)

개인 카톡에는 공식 API가 없어 상용 CRM 중에도 직접 수집하는 제품이 없다. 현실적 경로는 3단계:

| 단계 | 방식 | 실현성 |
|---|---|---|
| 1차 (즉시) | **대화 내보내기 .txt 업로드 → 파서**. 단톡방 포함, 방별 파일을 spf-hub에 드래그하면 증분 병합(마지막 수집 시각 이후만). PC 카톡 Ctrl+S로 반자동화 가능 | 높음 — CMS의 "마지막 수집" 모델을 동일하게 재현 |
| 2차 (보조) | Android 알림 리스너로 준실시간 유입 감지 → "신규 유입" 카운터용. 긴 메시지는 잘리므로 정본은 여전히 내보내기 파일 | 중간 — 약관 회색지대, 감지 전용 |
| 3차 (장기) | 신규 고객 대화를 **카카오톡 채널(상담톡)**로 이전 → 유일한 공식 양방향 API로 합법적 자동 수집 | 전략 과제 |

**파서**: 날짜/시간/발화자/본문 정규식 분리(OS별 포맷 3종), 방 이름·참여자 추출, 메시지 해시 중복 제거, "삭제된 메시지입니다" → 휴지통 플래그.

**분류 (spf-comms, 2단계 체이닝)**:

- 1단계: actionable 여부 판별(잡담 제거 — false positive 억제의 핵심)
- 2단계: 라벨 부여 — `계약`(견적·날인·조건협상) / `입금·정산`(입금확인·미수금·세금계산서) / `기관`(관공서·은행·공단) / `채무·사법`(내용증명·독촉·소송·압류) / `일정`(미팅·방문 약속) / `일반` + 긴급도 2축(`즉시`/`24h`/`주간`)
- 출력은 JSON Schema 구조화(자유 텍스트 파싱 금지), 키워드 프리필터 → LLM은 후보만 처리해 비용 절감

**넥스트 액션 추출 (4유형, 이메일 태스크 추출 업계 표준)**:

1. 상대가 나에게 요청한 것 (inbound request)
2. 내가 하겠다고 약속한 것 (outbound commitment)
3. 회신을 기다리는 것 (implicit follow-up)
4. 특정 시점 재확인할 것 (deferred decision)

각 태스크 = {출처 메시지 링크, 상대방, 마감일, 유형} 필수. 리드 매칭 시 Notion 리드 DB `다음 액션`/`다음 액션일` 필드에 기록(기존 spf-mail-scan 패턴 이식).

**발송 2계층**: `채무·사법`/`입금` 라벨은 실시간 텔레그램 알림, 나머지는 아침 다이제스트 루프.

```yaml
# loops/spf-kakao-brief.yaml (신규)
id: spf-kakao-brief
trigger: { type: cron, cron: "30 8 * * 1-5", timezone: Asia/Seoul }  # 08:20/08:40 사이 스태거
steps:
  - id: classify-and-digest
    agent: spf-comms
    model_tier: standard
    prompt: |
      spf.sqlite에서 미분류 메시지를 분류하고 넥스트 액션을 추출하라.
      리드 매칭 건은 Notion 리드 DB의 다음 액션에 기록.
      신규 없으면 [[QUIET]] 출력.
approval: { mode: draft_only }
delivery: { on_success: full }
```

**법적 가드(필수)**: 이루다 판례(2021, 과징금 1억여 원)상 카톡 대화는 개인정보. 저장 시 계좌·주민번호 자동 마스킹, 원문 암호화, 보유기간 설정, 외부 LLM 전송은 분류 후보만 최소 전송·요약/분류 결과만 장기 보관, 제3자 공유 금지 — spf-comms role-directive의 HARD 규칙으로 명문화.

### 모듈 B — 영업 지도 (요구사항 2)

**결정적 제약**: 구글맵은 한국 내 길찾기·고정밀 데이터가 제한(2026년 초 부분 허용 결정, 범위 유동적). 지도 엔진 이원화가 현실적:

- **국내**: 카카오맵 API(지오코딩·길찾기·장소검색 정확도 우위) 또는 네이버클라우드 Maps
- **해외**: Google Maps Platform (mymaps의 키·OAuth 배선 재사용)
- 렌더링은 MapTiler/Leaflet 단일 캔버스에 타일·라우팅 공급자만 스위칭

**기능 (Badger Maps / SPOTIO 베스트 프랙티스 이식)**:

1. **고객 핀 색상화** — Notion 리드 DB 동기화, 단계(Lead~Won)·스코어(HOT/WARM)·최근 접촉일별 색상. "30일 이상 미방문" 필터
2. **방문 체크인** — 모바일 웹에서 위치 검증 체크인 + 방문노트 폼 → 활동 타임라인·Notion 다음 액션 갱신. (GPS 상시 추적은 2차 과제로 미루고 체크인 기반으로 시작 — 개인정보·배터리 부담 없이 동일 가치의 80% 확보)
3. **경로 계획** — 당일 방문 목록 → 카카오내비/구글맵 딥링크 핸드오프 (자체 최적화 대신 핸드오프가 1인 영업엔 충분)
4. **활동 요약 바** — 방문 수·체류시간·이동거리(체크인 좌표 간 거리 합) + 일자 네비게이션

구현 위치: `apps/mymaps` 포크 대신 **`apps/spf-hub`의 지도 탭**으로 신설(mymaps의 `GoogleMapBody.tsx`·auth-google 배선 재사용). 리드 좌표는 지오코딩 배치(국내=카카오, 해외=구글)로 1회 캐시.

### 모듈 C — 파이프라인 대시보드 (요구사항 3)

리캐치의 2계층 리포트 구조(셀프서비스 리포트 + 고정 퍼널 리포트) + HubSpot/Pipedrive 표준 KPI 채택. 데이터 정본은 기존 Notion 리드/배송 DB 유지, spf-hub가 주기 동기화(읽기 전용 캐시).

**고정 퍼널 리포트**:

- 단계별 딜 수·금액: Lead → Contacted → Meeting → Won/Lost (기존 스키마 그대로)
- 단계별 전환율, 전체 승률(Win rate)
- 파이프라인 속도: (기회 수 × 평균 딜 크기 × 승률) ÷ 사이클 길이(일)
- 파이프라인 커버리지(총액 ÷ 목표, 3~4x 기준선 표시)

**위생·활동 위젯 (1인 영업에 특히 중요)**:

- 정체 딜(단계 체류일 초과 — leads 앱 rotting_days 로직 재사용), **다음 액션 없는 딜**, 다음 액션일 도래/연체(기존 아침브리핑 쿼리 동일)
- 활동 지표: 주간 카톡 응대 수·메일 회신 온도(HOT/WARM 분포)·방문 수 — 모듈 A/B가 자동 공급
- 물류 연계: EXCURSION/HELD_QA 배송 경고 카드(spf-logi-watch 동일 쿼리)

> 리드 DB에 `금액(₩)` 필드 1개만 추가하면 위 KPI 전부 계산 가능 (현재 스키마에 금액 없음).

---

## 4. 구현 계획 (my crew 아키텍처 맞춤)

| # | 작업 | 위치 |
|---|---|---|
| 1 | `spf-comms` 에이전트 등록 (adapter claude-code, mcp notion, WebSearch 불필요) | `history/agents.json` + `config/agents/spf-comms/role-directive.md` |
| 2 | 스킬 3종: `spf-kakao-parser`(파싱 규칙·OS별 포맷), `spf-comms-classify`(라벨·긴급도·JSON 스키마·마스킹), `spf-next-action`(4유형 추출·Notion 기록 규약) | `history/skills/` |
| 3 | `apps/spf-hub` 신설 (Next.js, 포트 13212, SQLite) — 소통·지도·대시보드 3탭. 기존 `apps/spf`(Vercel iframe) manifest 교체 | `apps/spf-hub/` |
| 4 | 루프 추가: `spf-kakao-brief.yaml`(08:30) — 텔레그램 스로틀(10초/카테고리) 회피 위한 시간 스태거 유지 | `loops/` |
| 5 | 아침브리핑 프롬프트 확장: 카톡 다이제스트 요약 1섹션 추가 | `loops/spf-daily-brief.yaml` |
| 6 | (선택) 카카오 알림톡 발송 채널 — isenssign `KakaoAlimtalkClient`를 loop runner delivery에 배선 | `src/server/loops/runner.ts` |

### SQLite 스키마 (요지)

```sql
messages(id, room, sender, sent_at, body_enc, body_masked, hash UNIQUE,
         deleted, label, urgency, lead_id)
rooms(name, participant_count, msg_count)
actions(id, type,          -- 4유형: inbound_request / commitment / follow_up / deferred
        due_date, counterpart, source_msg_id, status, notion_synced)
visits(id, lead_id, checkin_at, lat, lng, duration_min, note)
sync_log(source, last_ingested_at)
```

### 로드맵

| Phase | 기간 | 내용 |
|---|---|---|
| 1 | 1~2주 | 카톡 파서 + 분류 + 다이제스트 루프 |
| 2 | 2~3주 | spf-hub 대시보드 + 리드 동기화 + 금액 필드 |
| 3 | 3~4주 | 지도 탭 + 체크인 |
| 4 | 장기 | 카카오 채널 전환·알림 리스너·GPS 자동 궤적 |

---

## 5. 스크린샷 CMS 대비 우위 포인트

스크린샷 시스템은 "수집·조회"에서 멈추지만, 이 설계는:

1. 분류가 키워드가 아닌 LLM 2단계 체이닝(긴급도 2축 포함)
2. **넥스트 액션 자동 추출 → 파이프라인 '다음 액션' 필드 직결**
3. 카톡·메일·방문·물류가 하나의 리드 레코드로 수렴
4. 아침 브리핑·실시간 알림으로 능동 푸시

— 즉 "보는 시스템"이 아니라 "움직이게 하는 시스템"이 된다.

---

## Sources

WebFetch 검증 완료:

- https://www.recatch.cc/ko · https://guide.recatch.cc (리캐치 대시보드 3종 리포트)
- https://www.badgermapping.com/ (필드 영업 지도 기능)

WebSearch 경유 확인:

- https://salesmap.kr/ · https://salo.co.kr · https://www.shoplworks.com
- https://www.pipedrive.com/en/features/sales-dashboard · https://blog.hubspot.com/sales/sales-dashboard
- https://spotio.com/compare/badger-maps-vs-spotio/ · https://mapmycustomers.com
- https://developers.kakao.com/docs/latest/ko/kakaotalk-channel/common · https://bizmsg-web.kakaoenterprise.com/api-docs/
- https://github.com/miintto/KAKAO_TEXT_ANALYSIS (카톡 txt 파싱)
- https://m.boannews.com/html/detail.html?idx=96939 (이루다 과징금)
- https://blog.google/intl/ko-kr/company-news/inside-google/google-maps-data-export-qa-kr/ (구글 지도 반출)

미확인 사항: 구글맵 국내 길찾기 허용 범위는 2026년 진행 중 사안으로 유동적.
