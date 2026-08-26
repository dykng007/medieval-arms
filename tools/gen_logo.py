#!/usr/bin/env python3
"""
CurseForge 프로젝트 아바타(정사각 아이콘)를 만든다.

실행:  python tools/gen_logo.py
결과:  docs/avatar.png (800x800)

CurseForge 는 최소 400x400, 가로세로 1:1 을 요구한다. 더 크면 알아서 축소되므로
넉넉하게 800 으로 만든다. webp 는 제출 시 오류가 나므로 png 로 낸다.

제출 화면의 Logo 항목은 이것이 아니라 104x40 배너다 — tools/gen_banner.py 를 쓴다.

게임에 실제로 들어가는 장검 텍스처를 그대로 확대해 쓴다. 아이템 그림을 바꾸고
tools/import_art.py 를 다시 돌린 뒤 이 스크립트를 실행하면 아이콘도 따라 바뀐다.

필요:  pip install pillow
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow 가 필요합니다:  pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms",
                    "textures", "item", "longsword.png")
OUT = os.path.join(ROOT, "docs", "avatar.png")

SIZE = 800
BG_TOP = (58, 62, 70)
BG_BOTTOM = (30, 32, 38)
BORDER = (150, 158, 166)
BORDER_PX = 12


def background():
    img = Image.new("RGBA", (SIZE, SIZE))
    px = img.load()
    for y in range(SIZE):
        t = y / (SIZE - 1)
        base = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(SIZE):
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if edge < BORDER_PX:
                px[x, y] = BORDER + (255,)
            elif edge < BORDER_PX + 8:
                px[x, y] = (base[0] // 2, base[1] // 2, base[2] // 2, 255)
            else:
                px[x, y] = base + (255,)
    return img


def main():
    if not os.path.exists(ICON):
        print("장검 텍스처가 없습니다:", os.path.relpath(ICON, ROOT))
        print("먼저 tools/import_art.py 를 돌리세요.")
        return 2

    icon = Image.open(ICON).convert("RGBA")
    # 테두리 안쪽에 여백을 두고 최대한 크게. NEAREST 라야 픽셀이 뭉개지지 않는다.
    inner = SIZE - (BORDER_PX + 24) * 2
    side = (inner // icon.width) * icon.width
    icon = icon.resize((side, side), Image.NEAREST)

    img = background()
    img.alpha_composite(icon, ((SIZE - side) // 2, (SIZE - side) // 2))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("생성: %s (%dx%d, %d바이트)"
          % (os.path.relpath(OUT, ROOT), SIZE, SIZE, os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
