# 딴짓 상태 스프라이트 후처리 — states-raw/*.png → troam/states/ (배경 투명화 + 트리밍)
# 실행: uv run --with pillow python scripts-process-pet-states.py
# 규칙: state-<상태>-stage-<단계>.png 파일명 유지. 처리 후 로밍 코드가 자동 인식(404 폴백 내장).
from PIL import Image
import os, collections, glob

SRC = "assets/claude-master/pet/states-raw"
DST = "assets/claude-master/pet/troam/states"
os.makedirs(DST, exist_ok=True)

def key_bg(im):
    w, h = im.size
    cs = [im.getpixel(p)[:3] for p in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]
    return tuple(sum(c[i] for c in cs)//4 for i in range(3))

def close(c, bg, tol=45):
    return abs(c[0]-bg[0])+abs(c[1]-bg[1])+abs(c[2]-bg[2]) < tol

def process(path):
    im = Image.open(path).convert("RGBA"); w, h = im.size
    px = im.load(); bg = key_bg(im)
    seen = [[False]*h for _ in range(w)]; q = collections.deque()
    for x in range(w):
        for y in (0, h-1):
            if close(px[x,y][:3], bg): q.append((x,y)); seen[x][y] = True
    for y in range(h):
        for x in (0, w-1):
            if not seen[x][y] and close(px[x,y][:3], bg): q.append((x,y)); seen[x][y] = True
    while q:
        x, y = q.popleft(); px[x,y] = (0,0,0,0)
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[nx][ny] and close(px[nx,ny][:3], bg):
                seen[nx][ny] = True; q.append((nx,ny))
    im = im.crop(im.getbbox())
    out = os.path.join(DST, os.path.basename(path))
    im.save(out)
    print(os.path.basename(path), "->", im.size)

files = sorted(glob.glob(os.path.join(SRC, "state-*.png")))
if not files:
    print("states-raw/ 에 state-*.png 파일이 없습니다. PROMPT-PACK.md 참조.")
for f in files:
    process(f)
print("완료:", len(files), "장 →", DST)
