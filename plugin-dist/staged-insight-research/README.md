# staged-insight-research

단계형 소비자 인사이트 리서치 파이프라인 플러그인 — **1차 광범위 조사 → 2차 확장 검증 → 3차 포커스 인터뷰**를 GOAL→KNOWLEDGE→SEGMENT→QUESTION 역산 프레임으로 설계하고, 모든 단계 결과를 `research/{project-id}/` 디렉터리(manifest.json + phase 파일 + summary.md)에 저장해 **다음 세션·다른 에이전트가 이어받을 수 있게** 만듭니다.

## 구성

| Surface | 이름 | 역할 |
|---|---|---|
| Skill | `staged-insight-research:staged-insight-research` | 방법론 정본 — 저장 규약([HARD]), 역산 설계 프레임, 3단계 절차, 품질 게이트 |
| Agent | `staged-insight-research:insight-researcher` | 프로젝트 매니저 서브에이전트 — 프로젝트 생성/재개/마감, manifest 생애주기 관리 |

## 설치

로컬 디렉터리에서:

```
/plugin marketplace add <이 저장소 또는 로컬 경로>
/plugin install staged-insight-research@<marketplace-name>
```

또는 압축을 풀어 프로젝트의 `.claude/skills/`, `.claude/agents/`에 각 파일을 직접 복사해도 됩니다.

## 사용 예

```
"신제품 X의 2030 유입 컨셉 리서치 프로젝트를 시작해줘. project-id는 x-2030-acquisition"
→ insight-researcher가 GOAL 확정 → K 분해 → 세그먼트 표 → phase1 설문 → research/x-2030-acquisition/에 저장

(다음 세션에서)
"x-2030 리서치 이어서 해줘"
→ manifest.json을 읽고 첫 미완료 phase부터 재개
```

## 페르소나 응답자 (선택)

[`nemotron-personas-korea`](https://github.com/cjunekim/claude-plugins) 플러그인이 설치되어 있으면 100만 합성 한국인 페르소나를 응답자로 자동 활용합니다. 없으면 수동 설계 가상 페르소나 또는 실사용자 데이터로 동작합니다.

가상 페르소나 결과에는 항상 디스클레이머가 붙습니다: *"본 결과는 가상 페르소나 시뮬레이션입니다. 실제 사용자 검증을 대체하지 않습니다."*

## 라이선스

MIT
