# 수면 Q&A 에이전트 기획서
**소스: 「잘 자는 법」 (김성호·朴正模 엮음) MD 2종 (260528, 260608) · 작성일 2026-06-10**

---

## TL;DR

「잘 자는 법」 원고 2종을 **마크다운 네이티브 온톨로지**(개념 노드 + 타입드 관계 + 출처 표기)로 변환하고, **Anthropic 공식 Claude Code Channels의 Telegram 플러그인**으로 단체 채팅방에 연결하는 것을 추천한다. Channels는 Pro/Max 구독 인증으로 동작해 별도 API 비용이 없고, 그룹 채팅·멘션 트리거·멤버별 허용 목록을 공식 지원한다. 개인화는 Telegram 사용자 ID별 프로필 파일을 에이전트가 대화 중 갱신하는 메모리 패턴(Hermes 방식)으로 구현한다. 단, 상시 켜져 있는 PC 1대가 필요하고 Channels가 research preview라는 리스크가 있다.

---

## 1. 요구사항 정리

| 요구 | 해석 |
|---|---|
| MD → 온톨로지 | 책 내용을 개념·관계·근거 단위로 구조화, 환각 없는 답변의 기반 |
| Telegram 단체방 접속 | 그룹 채팅에서 여러 명이 질문 가능 |
| API 아닌 구독 동작 | Anthropic API 키 과금 없이 Claude Pro/Max 구독으로 추론 |
| 빠르고 정확한 답변 | 그룹 톤에 맞는 짧은 답 + 온톨로지 노드 인용 |
| Hermes식 개인화 | 대화를 통해 사용자별 수면 습관·시도 이력을 기억하고 반영 |

---

## 2. 리서치 요약 (Best Practices)

**Telegram 연결.** 2026년 현재 구독 기반으로 Telegram을 연결하는 검증된 경로는 두 갈래다. (1) **Claude Code Channels** — Anthropic 공식 research preview. Telegram 봇이 받은 메시지를 로컬에서 돌고 있는 Claude Code 세션에 push하고, 같은 채팅으로 답장한다. 그룹 채팅 등록(`group add`), 멘션 시에만 반응(`requireMention`), 멤버별 허용 목록, 타이핑 인디케이터, 4096자 자동 분할까지 공식 지원. claude.ai 구독 인증으로 동작한다. (2) **커뮤니티 브리지** — claude-code-telegram, cc-connect 등이 Telegram Bot API ↔ 로컬 Claude Code CLI(`claude -p`, 구독 OAuth)를 중계. 세션 영속·다중 사용자 큐잉 등 제어권이 크다.

**온톨로지 구축.** 소규모 도메인 문서(본 건 약 1,800줄)는 임베딩 기반 GraphRAG가 과투자라는 게 공통된 결론이다. 추론 품질 중심 설계에서는 "저장보다 인지 구조" — LLM이 직접 읽을 수 있는 경량 온톨로지(개념·관계·제약)를 만들어 모델이 근거 있는 관계만 따라가게 하는 것이 환각 억제에 효과적이다. 마크다운 + YAML frontmatter + 위키링크 형태가 Claude의 파일 도구(grep/read)와 가장 궁합이 좋다.

**개인화(Hermes 패턴).** 사용자별 프로필 파일을 두고, 매 대화 종료 시 에이전트가 "새로 알게 된 사실"을 파일에 추가하는 file-based memory가 표준 패턴. Claude Code의 CLAUDE.md + 메모리 디렉토리 구조를 그대로 활용할 수 있다.

---

## 3. 공통 기반: 온톨로지 설계

세 패턴 모두 아래 동일한 온톨로지를 사용한다. 책의 목차(수면 원리 → 과정 → 생애주기 → 도움 요소 → 환경 → 소도구 → 부작용)가 이미 분류 체계에 가까워 변환 비용이 낮다.

```
ontology/
├── schema.md            # 클래스·관계 정의 (온톨로지의 문법)
├── concepts/            # 노드: 멜라토닌, 세로토닌, 수면압력, REM, 심부체온…
├── actions/             # 노드: 아침 산책, 족욕, 저녁식사 시간, 청색광 차단…
├── factors/             # 노드: 카페인, 알코올, 온습도, 베개, 매트리스…
├── lifecycle/           # 노드: 아동기~노년기 수면 변화
└── claims.md            # 근거 문장 모음 (노드 간 관계 + 출처 + 신뢰 등급)
```

각 노드 형식 (예시):

```yaml
---
id: serotonin
type: 생리기전
relations:
  - [원료가_된다, melatonin]
  - [증가시킨다, 항중력근_긴장]
  - [촉진된다_by, 아침_산책, 햇빛, 리듬운동]
sources: ["아리타 히데호 『세로토닌 뇌 활성법』", "본문 6-1"]
evidence: 일반원칙   # 일반원칙 | 저자_개인경험 | 논쟁중
---
세로토닌은 낮 동안 햇빛·리듬운동으로 분비되며, 밤에 멜라토닌의 원료가 된다…
```

핵심 설계 원칙 3가지: ① 관계는 정해진 어휘만 사용(증가시킨다/억제한다/선행한다/권장된다/주의한다 등 10개 내외) → 모델이 관계를 지어내지 못함. ② 모든 주장에 출처와 `evidence` 등급 부착 → "책에 따르면 / 저자 개인 경험으로는"을 답변에서 구분. ③ 의학적 진단·약물 질문은 범위 외로 선언하고 전문의 안내(기존 sleep-coach 스킬의 가드레일 재사용).

---

## 4. 아키텍처 패턴 3안

### 패턴 A — 공식 Channels: Telegram 플러그인 + 상시 Claude Code 세션 ★추천

```
Telegram 단체방 ←→ telegram 플러그인(MCP, Bun) ←→ 상시 실행 Claude Code 세션 (구독 인증)
                                                      ├── ontology/  (위 구조)
                                                      ├── CLAUDE.md  (답변 프로토콜 harness)
                                                      └── profiles/<user_id>.md (개인화 메모리)
```

설치는 `/plugin install telegram@claude-plugins-official` → BotFather 토큰 등록 → `claude --channels plugin:telegram@…`으로 상시 세션 실행 → `/telegram:access group add <그룹ID>`. 멘션할 때만 반응(기본값)이라 단체방 소음이 없고, `mentionPatterns`로 "수면봇" 같은 한국어 호출어도 등록 가능. 개인화: 인바운드 메시지에 보낸 사람 ID가 포함되므로 CLAUDE.md에 "답변 전 profiles/<id>.md를 읽고, 대화에서 새 사실을 알게 되면 갱신하라"를 명시하면 Hermes식 누적 학습이 된다.

장점: 공식 지원이라 유지보수 코드 0줄, 구독 인증 충족, 그룹·멘션·허용목록 내장, 구축 반나절. 단점: research preview(스펙 변동 가능), 세션이 떠 있는 PC 필요, 단일 세션이라 동시 질문은 순차 처리, 무인 운영 시 권한 프롬프트 처리 설계 필요(`--dangerously-skip-permissions`는 신뢰 환경에서만).

### 패턴 B — 커스텀 브리지: Telegram Bot ↔ headless `claude -p`

```
Telegram Bot API ←→ 브리지 프로세스(Python/Node, 자작 또는 claude-code-telegram)
                       └→ 메시지마다 claude -p --resume <세션> 호출 (구독 OAuth)
                            └── 동일한 ontology/ + profiles/
```

브리지가 그룹 메시지를 받아 큐에 넣고, 채팅방(또는 사용자)별로 분리된 Claude 세션을 headless로 호출한다. 장점: 완전한 제어 — 사용자별 세션 격리(개인화 충돌 없음), 동시 질문 병렬 처리, 봇 명령어(/수면일지, /내프로필) 설계 자유, 자동 재시작 등 운영 안정성. 단점: 브리지 코드(약 200~400줄)를 직접 유지보수, `claude -p` 콜드 스타트로 응답이 패턴 A보다 수 초 느릴 수 있음, 커뮤니티 프로젝트 의존 시 품질 편차.

### 패턴 C — 컴파일형 지식팩: 경량 봇 + 야간 배치 학습

```
[빌드 타임] Cowork/Claude Code(구독)가 온톨로지 → FAQ 지식팩(질문 패턴별 답변 200~400개) 컴파일
[런타임]   경량 Telegram 봇이 키워드/유사도 매칭으로 즉답 (LLM 호출 없음)
[야간]     미응답 질문 로그를 Claude가 배치 처리 → 지식팩 증보
```

장점: 응답 0.1초·무인·무중단, PC 상시 가동 불필요(봇은 라즈베리파이/무료 서버), 구독 사용량 최소. 단점: 대화형 개인화가 사실상 불가(요구사항 미충족), 표현이 조금만 달라도 매칭 실패, "에이전트"라기보다 FAQ 봇.

---

## 5. 비교와 추천

| 기준 | A 공식 Channels | B 커스텀 브리지 | C 지식팩 봇 |
|---|---|---|---|
| 구독 내 동작 | ◎ 공식 보장 | ○ CLI OAuth | ◎ 빌드타임만 |
| 구축 난이도 | 반나절 | 2~4일 | 2~3일 |
| 답변 속도 | 수 초 | 수 초~십수 초 | 즉시 |
| 정확도(온톨로지 활용) | ◎ | ◎ | △ 매칭 의존 |
| 단체방 지원 | ◎ 내장 | ◎ 직접 구현 | ○ |
| Hermes식 개인화 | ○ 프로필 파일 | ◎ 세션 격리 | ✕ |
| 유지보수 | 거의 없음 | 코드 관리 필요 | 지식팩 갱신 |
| 리스크 | preview 스펙 변동 | 자작 코드 안정성 | 대화성 부족 |

**추천: 패턴 A.** 이유는 세 가지. ① 요구사항의 가장 까다로운 제약("API 아닌 구독")을 Anthropic이 공식 문서로 보장하는 유일한 경로다 — 커뮤니티 브리지는 동작하지만 약관·업데이트 변동에 더 취약하다. ② 그룹 채팅 운영에 필요한 것(멘션 트리거, 멤버 허용목록, 자동 분할, 타이핑 표시)이 이미 만들어져 있어, 우리 노력을 차별화 요소인 **온톨로지 품질과 개인화 harness**에 집중할 수 있다. ③ 나중에 패턴 B로 갈아타더라도 ontology/·profiles/·CLAUDE.md 자산이 100% 재사용되므로, A로 시작하는 것이 매몰비용 없는 최소 실험이다.

### 반대 관점 (counter-rational)

추천과 반대로 볼 근거도 있다. 첫째, Channels는 research preview라 `--channels` 플래그와 프로토콜이 예고 없이 바뀔 수 있고, 단체방 트래픽이 많으면 단일 세션 순차 처리가 병목이 된다 — 멤버가 10명 이상이고 질문이 잦다면 처음부터 B가 맞다. 둘째, 상시 세션은 구독 사용량(rate limit)을 그룹 전체가 공유하므로, 본인의 다른 Claude 작업 한도를 갉아먹는다. 셋째, 질문 대부분이 "카페인 언제까지 마셔도 돼?" 수준의 반복 질문이라면 C가 비용·속도에서 압도적이며, 굳이 LLM을 실시간으로 돌릴 이유가 없다. 운영 1~2주 후 질문 로그를 보고 A→B(트래픽 증가 시) 또는 A+C 하이브리드(반복 질문은 지식팩 선응답)로 진화시키는 것이 합리적이다.

---

## 6. 구현 로드맵 (패턴 A 기준)

1. **온톨로지 빌드 (1일)** — MD 2종 비교·병합(260608이 최신) → schema.md 확정 → 노드 추출(예상 60~100개) → claims.md 작성 → 빠진 관계 검수
2. **답변 harness 작성 (반일)** — CLAUDE.md: 답변 프로토콜(온톨로지 조회 → 근거 인용 → 3~5문장 → evidence 등급 명시), 가드레일(의료 진단 금지), 프로필 갱신 규칙. 800단어 이내
3. **Telegram 연결 (반일)** — BotFather 봇 생성 → 플러그인 설치·페어링 → 그룹 등록 → 호출어 설정
4. **개인화 검증 (반일)** — 2~3명이 그룹에서 테스트: 같은 질문에 프로필별로 다른 답이 나오는지, 프로필 파일이 누적되는지
5. **운영 (지속)** — 질문 로그 주간 리뷰 → 온톨로지 증보 / 패턴 전환 판단

## 7. 결정 필요 사항

- 상시 가동 PC: 본인 PC를 켜둘 수 있는가, 아니면 미니PC/서버 별도 운영인가
- 그룹 반응 방식: @멘션·호출어에만 반응(권장) vs 모든 메시지 반응(privacy mode 해제 필요, 소음 큼)
- 개인화 범위: 수면 습관·시도 이력만 vs 대화 전반 기억 (단체방 특성상 프라이버시 고지 필요)

---

**Sources:** [Claude Code Channels 공식 문서](https://code.claude.com/docs/en/channels) · [Telegram 플러그인 README](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram) · [Telegram 플러그인 ACCESS.md (그룹 지원)](https://github.com/anthropics/claude-plugins-official/blob/main/external_plugins/telegram/ACCESS.md) · [claude-code-telegram (커뮤니티)](https://github.com/RichardAtCT/claude-code-telegram) · [cc-connect](https://github.com/chenhg5/cc-connect) · [InfraNodus: KG for LLM Reasoning](https://infranodus.com/docs/knowledge-graphs-llm-reasoning) · [Awesome-GraphRAG](https://github.com/DEEP-PolyU/Awesome-GraphRAG)
