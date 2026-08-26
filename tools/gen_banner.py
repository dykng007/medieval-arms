#!/usr/bin/env python3
"""
CurseForge 프로젝트 Logo(배너)를 만든다.

실행:  python tools/gen_banner.py
결과:  docs/banner.png (104x40)

CurseForge 프로젝트 제출 화면의 Logo 항목은 정사각 아바타가 아니라
가로로 긴 배너를 요구한다. 화면에 적힌 조건은 다음과 같다.

    Format      PNG, WEBP
    Size        100KB
    Resolution  104x40

104x40은 글자를 넣기엔 아주 좁아서, 왼쪽에 장검 아이콘을 두고
오른쪽에 모드 이름을 두 줄로 넣었다. 이 크기에 쓸 만한 폰트가 없으므로
필요한 글자(M E D I V A L R S)만 5x7 픽셀로 직접 그려 넣는다.

게임에 실제로 들어가는 장검 텍스처를 그대로 쓴다. 아이템 그림을 바꾸고
tools/import_art.py 를 다시 돌린 뒤 이 스크립트를 실행하면 배너도 따라 바뀐다.

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

WIDTH, HEIGHT = 104, 40
OUT = os.path.join(ROOT, "docs", "banner.png")

BG_TOP = (52, 56, 64)
BG_BOTTOM = (28, 30, 36)
BORDER = (120, 128, 138)
TEXT = (226, 232, 240)
TEXT_SHADOW = (16, 18, 22)

# "MEDIEVAL ARMS" 에 필요한 글자만. 5칸 x 7줄.
FONT = {
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
}
GLYPH_W, GLYPH_H, TRACKING = 5, 7, 1


def save(path, width, height, pixels):
    img = Image.new("RGBA", (width, height))
    img.putdata(pixels)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def put(pixels, x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        pixels[y * WIDTH + x] = color + (255,)


def text_width(s):
    return len(s) * (GLYPH_W + TRACKING) - TRACKING


def draw_text(pixels, s, x, y):
    """글자를 찍는다. 배경과 붙어 읽기 어려우므로 오른쪽 아래에 그림자를 깐다."""
    cx = x
    for ch in s:
        glyph = FONT[ch]
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == "#":
                    put(pixels, cx + gx + 1, y + gy + 1, TEXT_SHADOW)
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == "#":
                    put(pixels, cx + gx, y + gy, TEXT)
        cx += GLYPH_W + TRACKING


def main():
    pixels = []
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        base = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(WIDTH):
            on_edge = x == 0 or y == 0 or x == WIDTH - 1 or y == HEIGHT - 1
            pixels.append((BORDER if on_edge else base) + (255,))

    # 왼쪽: 실제 장검 텍스처를 배너 높이에 맞춰 넣는다.
    # 32x32 텍스처를 40픽셀 높이 배너에 넣어야 하므로 정수배가 안 나온다.
    # 픽셀이 뭉개지지 않도록 NEAREST 로 줄인다.
    icon_side = HEIGHT - 6
    icon = Image.open(ICON).convert("RGBA").resize((icon_side, icon_side), Image.NEAREST)
    ox, oy = 3, (HEIGHT - icon_side) // 2
    ip = icon.load()
    for iy in range(icon_side):
        for ix in range(icon_side):
            r, g, b, a = ip[ix, iy]
            if a > 128:
                put(pixels, ox + ix, oy + iy, (r, g, b))

    # 오른쪽: 모드 이름 두 줄. 남은 폭 가운데에 맞춘다.
    left = ox + icon_side + 3
    area = WIDTH - left - 2
    top = (HEIGHT - (GLYPH_H * 2 + 4)) // 2
    for i, line in enumerate(("MEDIEVAL", "ARMS")):
        draw_text(pixels, line, left + (area - text_width(line)) // 2, top + i * (GLYPH_H + 4))

    save(OUT, WIDTH, HEIGHT, pixels)
    size = os.path.getsize(OUT)
    print("생성: %s (%dx%d, %d바이트)" % (os.path.relpath(OUT, ROOT), WIDTH, HEIGHT, size))
    if size > 100 * 1024:
        print("경고: CurseForge 제한(100KB)을 넘었습니다.")


if __name__ == "__main__":
    main()
