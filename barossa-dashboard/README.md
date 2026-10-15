# Barossa 운영 대시보드 (v0)

`index.html` 한 파일로 동작하는 정적 대시보드입니다. 데이터는 들어 있지 않고, 열 때마다 엑셀 워크북을 직접 읽습니다.

## 사용법
1. `index.html`을 브라우저로 엽니다 (파일 더블클릭 또는 웹서버). SheetJS를 `cdn.jsdelivr.net`에서 받으므로 인터넷 연결이 필요합니다.
2. **Ledger 워크북**과 **체크리스트 워크북 (Dashboard)**을 버튼으로 고르거나 끌어다 놓습니다. 시트 이름으로 종류를 자동 판별하며, 하나만 불러와도 됩니다.
3. 상단 **기준일**(기본값: 오늘)이 D-day·지연 판정의 기준입니다.
4. **PDF 출력**은 현재 탭만 인쇄하고, **엑셀 내보내기**는 현재 탭의 표(필터 적용 상태)를 새 .xlsx로 저장합니다.

## 읽는 시트·헤더 (헤더 텍스트로 위치를 찾습니다)
| 탭 | 시트 | 헤더 |
|---|---|---|
| Production | Feed Gas | `Date`, `Actual` 아래 단위행 `MMscf` (실적) |
| Production | Forecast | `Date`+`Feed Gas` 헤더 블록 중 날짜 행이 가장 많은 블록 (현재 `* Daily Production` 블록) |
| Production | Ledger_ADP 및 SDS / Condensate Ledger | 같은 행의 `Date`·`Production`·`Inventory` |
| Production | ADP 및 SDS / LP | `Slot Number`, `Lifting Slot`, `Lifter`, `Cargo Size (Planned_…)`, `Cargo Size (Actual_…)`, `Proposed Vessel`, `Issue`, `last confirmed SDS slot` |
| Production | Operation Daily | `Barossa & DLNG Production` 표의 `Actual` / `Plan…` / `Actual vs Plan` |
| Production | BrentnJKM | `날짜`, `Brent가격`, `JKM가격`, `월`, `Brent 월평균`, `JKM 월평균` |
| Checklist | ADP Process / Annual / Monthly | `Contract`…`Actual`, CY는 `CY Start` 오른쪽 날짜 |
| Cargo | 일정 / Cargo / History (연단위) | `Slot Number` 등, Cargo는 `Slot No.` 행·`Due` 행의 `Due Date`/`Actual` 열 쌍 |

## 실적과 예측의 구분
- **최신 보고일** = Feed Gas 시트에서 `Actual MMscf` 숫자가 있는 마지막 날짜. 이날까지가 실적, 이후가 예측입니다.
- Feed Gas 예측: Forecast 시트의 일별 블록(`Feed Gas` = DLNG Nomination, Mmscf). 우측 `* Maintenance` 블록은 기간이 짧아 쓰지 않습니다.
- LNG·Condensate 예측: 원장 시트가 최신 보고일 이후 행을 Forecast 값으로 채우므로, 같은 원장의 이후 행을 그대로 예측으로 그립니다.
- 그래프 범위: 최근 실적 30일 + 예측(기준일 이후 30일까지).

## 상태 규칙
Actual 있음 → 완료 / Due Date < 기준일 → 지연 / 0~7일 → D-7 임박 / 8~30일 → D-30 / 그 이후 → 예정 / Due Date가 날짜가 아님 → 수시/규칙.

## 데이터 점검
시트·헤더가 없거나 셀이 `#REF!`·`#DIV/0!` 같은 오류값이면 값을 지어내지 않고 "–"로 표시한 뒤, 화면 아래 **데이터 점검**에 시트·헤더·사유를 남깁니다.

## 개인정보
파일은 이 브라우저 안에서만 읽고, 어디에도 전송·저장하지 않습니다 (테마 선택만 브라우저에 기억). 이 폴더의 `.xlsx/.xls/.csv`는 `.gitignore`로 커밋되지 않습니다.
