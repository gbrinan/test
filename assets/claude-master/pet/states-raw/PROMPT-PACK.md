# 딴짓 상태 스프라이트 프롬프트 팩 (20장)

> 사용법: 이미지 생성 도구(ChatGPT 이미지 / Higgsfield / Midjourney 등)에서
> **참조 이미지를 첨부**하고 아래 프롬프트를 붙여넣어 생성 → 결과 PNG를 **지정 파일명**으로 이 폴더(`states-raw/`)에 저장.
> 이후 Claude에게 "상태 이미지 처리해줘"라고 하면 투명화·트리밍·배포까지 자동 진행됩니다.

## 공통 프롬프트 접두어 (모든 장에 사용)

```
Same character as the reference image — identical species, proportions, colors, and GBA-era pixel art style.
Full body, single character, centered, solid dark navy background (#0a1a35), no text, no frame.
Pose change only:
```

한 장이 이상하게 나오면 2~3회 재생성(가챠)하고 가장 캐릭터가 유지된 것을 고르세요.

## 생성 목록

| # | 파일명 (저장할 이름) | 참조 이미지 | 포즈 프롬프트 (접두어 뒤에 붙이기) |
|---|---|---|---|
| 1 | state-read-stage-1.png | pet-stage-1.png | reading a small book held in both hands, eyes looking down at the book, content expression |
| 2 | state-sleep-stage-1.png | pet-stage-1.png | sleeping curled up on the ground, eyes closed, peaceful expression |
| 3 | state-calm-stage-1.png | pet-stage-1.png | sitting relaxed, eyes gently closed, meditating peacefully |
| 4 | state-stretch-stage-1.png | pet-stage-1.png | stretching arms up high, mouth open in a yawn |
| 5 | state-hungry-stage-1.png | pet-stage-1.png | holding its round belly with both hands, drooling slightly, hungry pleading eyes |
| 6 | state-excited-stage-1.png | pet-stage-1.png | jumping with joy, arms raised, sparkling happy eyes, big smile |
| 7 | state-read-stage-2.png | pet-stage-2.png | reading a small book held in both hands, eyes looking down at the book, content expression |
| 8 | state-sleep-stage-2.png | pet-stage-2.png | sleeping curled up on the ground, eyes closed, peaceful expression |
| 9 | state-calm-stage-2.png | pet-stage-2.png | sitting relaxed, eyes gently closed, meditating peacefully |
| 10 | state-stretch-stage-2.png | pet-stage-2.png | stretching arms up high, mouth open in a yawn |
| 11 | state-hungry-stage-2.png | pet-stage-2.png | holding its round belly with both hands, drooling slightly, hungry pleading eyes |
| 12 | state-excited-stage-2.png | pet-stage-2.png | jumping with joy, arms raised, sparkling happy eyes, big smile |
| 13 | state-read-stage-3.png | pet-stage-3.png | reading a small book held in both hands, eyes looking down at the book, content expression (keep the backpack on) |
| 14 | state-sleep-stage-3.png | pet-stage-3.png | sleeping curled up on the ground using the backpack as a pillow, eyes closed |
| 15 | state-calm-stage-3.png | pet-stage-3.png | sitting relaxed leaning on the backpack, eyes gently closed |
| 16 | state-stretch-stage-3.png | pet-stage-3.png | stretching arms up high, mouth open in a yawn (keep the backpack on) |
| 17 | state-hungry-stage-3.png | pet-stage-3.png | holding its round belly with both hands, drooling slightly, hungry pleading eyes (keep the backpack on) |
| 18 | state-excited-stage-3.png | pet-stage-3.png | jumping with joy, arms raised, sparkling happy eyes, big smile (keep the backpack on) |
| 19 | state-sleep-stage-7.png | pet-stage-7.png | the legendary guardian dragon sleeping curled up majestically, leaf mane draped like a blanket, eyes closed |
| 20 | state-excited-stage-7.png | pet-stage-7.png | the legendary guardian dragon roaring joyfully to the sky, wings of leaves spread wide |

## 규칙 요약

- 파일명은 표 그대로 (`state-<상태>-stage-<단계>.png`) — 자동 처리 스크립트가 이 규칙을 읽습니다.
- 배경은 어두운 남색 단색이면 됩니다 (후처리에서 자동 투명화).
- 4~6단계는 생성하지 않습니다 — 그 단계에서는 자동으로 "기본 스프라이트+이모트" 방식으로 폴백됩니다.
- 꿈(dream) 상태는 sleep 이미지 + 💭 말풍선을 재사용하므로 별도 생성 불필요.
