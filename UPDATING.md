# 콘텐츠·정보 업데이트 가이드

> 2026-07-21 lazy-protected 적용 이후 기준. **콘텐츠가 두 곳에 나뉘어 있다는 것**이 핵심:
> 무료(PART 1) = `claude-guide-demo.html`의 CHAPTERS 인라인 / 프리미엄(29챕터) = `api/_premium.js` (서버 전용).

## 공통 배포 절차 (모든 변경의 마지막 단계)

```bash
cd anandara-claude-course
git add -A && git commit -m "..." && git push        # git push 는 인자 없이 (TROUBLESHOOTING §3-1)
vercel build --prod --yes --scope ananks-projects-378bc31c
vercel deploy --prebuilt --prod --yes --scope ananks-projects-378bc31c  # prebuilt 필수 (서버 빌드 큐 정체 — §4-3)
# 2026-07-24 프로젝트를 jijife 팀 → Anank's projects 팀 "anandara" 프로젝트로 이전 (URL: anandara.vercel.app)
# (해결됨 2026-07-24) 커밋 작성자 이메일이 GitHub 계정에 없으면 배포가 UNKNOWN으로 멈춤.
#   GitHub Settings → Emails 에 arinan@naver.com 추가로 해결. 재발 시 .git 제외 복사본에서 deploy로 우회 가능.
```

배포 후 스모크: `curl -s -X POST <site>/api/lesson -d '{"id":"5-1"}' -H 'Content-Type: application/json'` → `login_required` 나오면 정상.

## 유형별 업데이트 방법

### 1. 무료 챕터(1-1~1-4) 본문·퀴즈 수정
- `claude-guide-demo.html`의 `const CHAPTERS = [` 안에서 해당 id 객체를 직접 수정 (JSON 직렬화 형태).
- 주의: 퀴즈 정답 인덱스(`a`)는 보기(`opts`) 순서와 일치해야 함.

### 2. 프리미엄 챕터(2-1~CV-7) 본문·퀴즈 수정
- **`api/_premium.js`의 `PREMIUM["<id>"]`** 를 수정 (HTML엔 메타데이터만 있음 — 건드릴 필요 없음).
- 제목·리드·PART·tier 등 **메타데이터 변경은 HTML 쪽** CHAPTERS에서.

### 3. 새 챕터 추가
1. HTML CHAPTERS에 메타 항목 추가 — 무료면 body/quiz 포함, 프리미엄이면 `"body":"","quiz":[],"remote":true`.
2. 프리미엄이면 `api/_premium.js`에 `{tier, body, quiz}` 추가.
3. 순서 = 배열 순서(잠금 규칙이 "직전 챕터 통과" 기준). PART 그룹명이 새로우면 진화 단계(EVO_STEPS)와 partTierMap 영향 검토.

> 대량 개편 시: git 히스토리에서 전체본 HTML을 복원해 수정한 뒤 `node scripts-split-content.js <html> api` 로 재분리하는 방법도 있음.

### 4. 버전 종속 정보 (모델명·요금·통계)
- 본문에 직접 쓰지 말고 **master-curriculum.md 부록 A(팩트 시트)** 를 먼저 갱신 → 해당 챕터(⚠ 버전 종속 표시된 곳)에 반영.
- 갱신 주기 권장: 분기 1회 또는 주요 모델 발표 시. WebSearch+WebFetch 검증(확실/불확실 표기) 관행 유지.

### 5. 가격 변경
- **세 곳 동시 수정 필수**: HTML `TIERS` price / `api/verify-payment.js` `AMOUNT_TO_TIER` / 문서(README·PORTONE-SETUP).
- 불일치 시 결제 검증이 `invalid_amount`로 전부 거부됨 — 의도된 안전장치.

### 6. 등급명·구간 변경
- 이름: HTML `TIERS`의 `name` 한 곳 (페이월·뱃지·진화 문구 자동 전파).
- 구간(PART↔tier): HTML CHAPTERS의 각 챕터 `tier` + `api/_premium.js`의 `tier` + EVO_STEPS `needTier` 함께 검토.

### 7. 에셋 (이미지·오디오)
- 레슨 도식: `assets/claude-master/learning/lesson-<챕터id>.png` 로 넣으면 **코드 수정 없이 자동 노출**.
- BGM 추가: 파일을 `assets/audio/tracks/`에 넣고 HTML `BGM_TRACKS`에 한 줄 추가. CC 곡은 크레딧(홈 하단 + audio/README) 필수.
- 효과음 교체: `assets/audio/sfx/` 동일 파일명으로 덮어쓰기.

### 8. 다국어 (I18N.md 참조)
- UI 문구 변경 시 `i18n/ko.json`·`en.json` 키 동기화 (키 불일치 검증: 두 파일 Object.keys 비교).

## 검증 루틴 (배포 전 1분)

```bash
# 스크립트 문법
node -e "const h=require('fs').readFileSync('claude-guide-demo.html','utf8');const s=h.lastIndexOf('<scr'+'ipt>');require('fs').writeFileSync('/tmp/c.js',h.slice(s+8,h.indexOf('</scr'+'ipt>',s)))" && node --check /tmp/c.js
node --check api/_premium.js && node --check api/lesson.js && node --check api/verify-payment.js
# 챕터 무결성 (개수·퀴즈 정답 범위) — 과거 CH 2-3 유실을 잡아낸 검증
node -e "const h=require('fs').readFileSync('claude-guide-demo.html','utf8');const s=h.indexOf('const CHAPTERS');const C=eval(h.slice(s,h.indexOf('];',s)+2)+';CHAPTERS');console.log('chapters',C.length);C.forEach(c=>c.quiz.forEach((q,i)=>{if(q.a==null||q.a>=q.opts.length)throw c.id+':q'+i}))"
```

## 원칙 요약

1. **프리미엄 본문은 절대 HTML로 돌아가지 않는다** (C1 재발 방지).
2. 가격·등급은 프론트/서버/문서 동기화가 깨지면 결제가 멈추도록 설계돼 있다 — 에러가 나면 불일치부터 의심.
3. 수치·버전 정보는 팩트 시트를 거쳐서만.
4. 배포는 항상 prebuilt, 푸시는 인자 없이.
