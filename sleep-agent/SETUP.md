# SETUP — 수면 Q&A 텔레그램 봇 연결 가이드

이 봇은 **Anthropic API 키 없이 claude.ai Pro/Max 구독 인증으로만** 동작합니다. 아래 절차는 1회 셋업이며, 토큰 발급은 사용자가 직접 해야 합니다.

## 사전 준비
- Claude Code 설치 + claude.ai Pro/Max 구독 로그인 (API 키 불필요)
- 이 프로젝트 폴더에서 `python scripts/build_index.py`가 정상 종료(`index.md` 생성)되는지 먼저 확인

## 연결 절차

```
1) 텔레그램에서 @BotFather → /newbot → 봇 토큰 발급
2) /plugin install telegram@claude-plugins-official  →  /reload-plugins
3) /telegram:configure <봇토큰>
4) claude --channels plugin:telegram@claude-plugins-official     (상시 세션 시작)
5) 봇에게 DM → 페어링 코드 수신 → /telegram:access pair <코드>
6) /telegram:access group add <그룹ID>      (그룹ID는 @RawDataBot을 그룹에 잠깐 넣어 -100… 확인)
7) /telegram:access set mentionPatterns '["수면봇","잘자는법","\\b수면\\b"]'
8) /telegram:access policy allowlist
```

- 기본값 `requireMention: true`를 유지하세요(단체방 소음 0). `--no-mention`은 쓰지 않습니다.
- 호출어(`수면봇`·`잘자는법`·`수면`) 중 하나라도 메시지에 있으면 봇이 반응합니다.

## 상시 운영 (D3)
- **봇은 이 PC에서 Claude Code 세션이 떠 있는 동안에만 응답합니다.** 세션을 닫으면 봇도 멈춥니다.
- PC 절전/재부팅 후 재기동:
  1. 터미널에서 프로젝트 폴더로 이동
  2. `claude --channels plugin:telegram@claude-plugins-official` 다시 실행
  3. (필요 시) `python scripts/build_index.py`로 인덱스 최신화
- 절전 방지: 전원 옵션에서 "절전 안 함"을 권장(세션 유지를 위해).

## 프라이버시 고지 (R4)
- 이 봇은 개인화를 위해 단체방 **대화 전반**을 `profiles/<user_id>.md`에 기억합니다.
- 봇은 신규 사용자 첫 응답 시 이 사실을 1회 고지합니다.
- 건강 민감정보는 사용자가 명시적으로 말한 것만 저장합니다.
- `profiles/`와 `logs/`는 git에 커밋되지 않습니다(.gitignore).

## 동작 확인 체크리스트
- [ ] API 키 없이 기동됨 (env에 ANTHROPIC_API_KEY 없음, S6)
- [ ] 그룹에서 호출어 멘션 시에만 반응, 비멘션 무반응 (S4)
- [ ] 답변이 3~5문장 + 근거 한 줄 표기
- [ ] 책 밖 질문에 추측하지 않고 "다루지 않는 내용" 응답
- [ ] 프로필이 다른 두 사용자가 같은 질문 → 답이 갈림 (S5)
