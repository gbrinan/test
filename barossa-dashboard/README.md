# Barossa 운영 대시보드 (v0)

`index.html` 한 파일로 동작하는 정적 대시보드입니다. 데이터는 들어 있지 않고, 열 때마다 엑셀 워크북을 직접 읽습니다.

## 사용법
1. `index.html`을 브라우저로 엽니다 (파일 더블클릭 또는 웹서버). SheetJS를 `cdn.jsdelivr.net`에서 받으므로 인터넷 연결이 필요합니다.
2. **Ledger 워크북**과 **체크리스트 워크북 (Dashboard)**을 버튼으로 고르거나 끌어다 놓습니다. 시트 이름으로 종류를 자동 판별하며, 하나만 불러와도 됩니다.
3. 상단 **기준일**(기본값: 오늘)이 D-day·지연 판정의 기준입니다.
4. 파일이 없으면 **샘플 데이터로 보기**로 화면 구성을 볼 수 있습니다. 시드 고정 난수와 기준일 기준 상대 날짜로 만든 임의 값(Partner A/B/C, Vessel Alpha… 등)이며 실제 값이 아닙니다. 샘플도 실제 파일과 똑같이 .xlsx로 만들어 같은 경로로 읽고, 실제 파일을 불러오면 해당 워크북의 샘플을 대체합니다.
5. **PDF 출력**은 현재 탭만 인쇄하고, **엑셀 내보내기**는 현재 탭의 표(필터 적용 상태)를 새 .xlsx로 저장합니다.

## 읽는 시트·헤더 (헤더 텍스트로 위치를 찾습니다)
| 탭 | 시트 | 헤더 |
|---|---|---|
| Production | Feed Gas | `Date`, `Actual` 아래 단위행 `MMscf` (실적), 같은 헤더 행 `Nomination` 아래 `MMscf` (Nomination 선) |
| Production | Forecast | `Date`+`Feed Gas` 헤더 블록 중 날짜 행이 가장 많은 블록 (현재 `* Daily Production` 블록) |
| Production | Ledger_ADP 및 SDS / Condensate Ledger | 같은 행의 `Date`·`Production`·`Inventory`. 재고 기준선은 헤더 위 블록의 `Working Capacity`·`Tank Top`·`Unpumpable` 라벨 오른쪽 값 (`LC 기준` 열이 있으면 그 값) |
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

카고만 예외: Lifting 창(끝, 없으면 시작)이 기준일 전에 끝난 카고는 지난 마감에 Actual이 비어 있으면 **실적 미입력**(회색)으로 보고, 알림 배너·팝업에서 뺍니다. 상태는 색과 함께 모양 아이콘·글자로 표시합니다.

그래프 보조 표시: 재고 그래프의 ▲는 Lifting 날짜(ADP 및 SDS / LP, 툴팁에 Lifter), 붉은 띠는 예측 재고가 0 미만이거나 Tank Top을 넘는 구간입니다(선은 자르지 않음).

## 체크리스트 수정·저장 (ADP Process / Annual / Monthly)
- 행의 ✎ 버튼으로 Due Date·Actual(날짜, 비우기 가능)·Event·Items covered·Due 규칙·사용자가 추가한 열을 고치고, **+ 행 추가**·**행 삭제**를 할 수 있습니다. 상태·D-day·타임라인·알림이 바로 다시 계산되고, 행은 Due Date 순(날짜 없는 행은 뒤)으로 다시 정렬됩니다.
- 고친 행에는 "● 수정됨"이 붙고, 도구줄의 **수정 N건 / 수정 취소(전체)** 로 확인·되돌릴 수 있습니다.
- **브라우저에는 저장되지 않습니다.** 창을 닫기 전에 **수정본 엑셀 저장**을 누르세요. 불러온 원본을 바탕으로 `<원본이름>_수정_YYYYMMDD.xlsx`를 새로 만들며, 고친 시트의 표 영역만 정렬된 순서로 다시 쓰고 다른 시트와 표 밖 셀은 그대로 둡니다. 날짜는 엑셀 날짜로 저장됩니다.
- 주의: SheetJS 무료판은 **셀 서식(색·테두리·글꼴)을 보존하지 않습니다** — 값과 시트 구조만 남습니다. 다시 쓴 표 영역의 수식은 계산된 값으로 저장되고, 문자열 줄바꿈은 LF로 통일됩니다.

## 데이터 점검
수기 편집도 받아들입니다: 텍스트 날짜(`2026-10-20`, `2026/10/20`, `20/10/2026`, `20.10.2026` — 빗금·점은 일-월-연, 일/월이 모호하면 셀을 참고로 기록), 텍스트 숫자(`"1,234"`)는 변환하고 건수를 남깁니다. 뒤에 글자가 붙은 날짜(`1/20 +`)는 규칙 텍스트로 둡니다. 시트가 없으면 해당 카드에 "필요한 시트 '…'를 찾지 못했습니다", 헤더가 없으면 경고를 띄우고, 사용자가 추가한 체크리스트 열은 표 끝에 보여 줍니다.

시트·헤더가 없거나 셀이 `#REF!`·`#DIV/0!` 같은 오류값이면 값을 지어내지 않고 "–"로 표시한 뒤, 화면 아래 **데이터 점검**에 시트·헤더·사유를 남깁니다.

## 개인정보
파일은 이 브라우저 안에서만 읽고, 어디에도 전송·저장하지 않습니다 (테마 선택만 브라우저에 기억). 이 폴더의 `.xlsx/.xls/.csv`는 `.gitignore`로 커밋되지 않습니다.
