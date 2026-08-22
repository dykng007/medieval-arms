#!/usr/bin/env python3
"""
CurseForge 프로젝트 아바타(정사각 아이콘)를 만든다.

실행:  python tools/gen_logo.py
결과:  docs/avatar.png (800x800)

프로젝트 페이지의 정사각 아바타용이다. CurseForge는 최소 400x400, 1:1을 요구한다.
제출 화면의 Logo 항목은 이것이 아니라 104x40 배너다 — tools/gen_banner.py 를 쓴다.
장검 스프라이트를 그대로 확대해 쓰므로, 아이템 텍스처를 바꾸면
이 스크립트를 다시 돌리는 것만으로 아이콘도 따라 바뀐다.

gen_textures.py와 마찬가지로 외부 라이브러리 없이 표준 라이브러리만 쓴다.
"""

import os
import struct
import sys
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from gen_textures import PALETTE, SPRITES  # noqa: E402

# CurseForge 요구사항: 최소 400x400, 가로세로 같은 비율(1:1).
# 더 크면 알아서 축소되므로 넉넉하게 800으로 만든다.
SIZE = 800
OUT = os.path.join(ROOT, "docs", "avatar.png")

# 배경: 어두운 석재 느낌의 세로 그라데이션
BG_TOP = (58, 62, 70)
BG_BOTTOM = (30, 32, 38)
BORDER = (150, 158, 166)


def write_png(path, width, height, pixels):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    # PNG 시그니처. 이스케이프 문자가 도중에 풀리는 사고를 막으려고
    # 바이트 값을 직접 적는다.
    png = bytes([137, 80, 78, 71, 13, 10, 26, 10])
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def blit(pixels, grid, scale, ox, oy, mirror=False, dim=1.0):
    """
    스프라이트를 확대해 캔버스에 찍는다.

    mirror=True 면 좌우를 뒤집는다. 두 무기를 X자로 겹치려면 하나는 뒤집어야 한다.
    dim 은 밝기 배수. 뒤에 깔리는 무기를 살짝 어둡게 해 앞뒤를 구분한다.
    """
    for sy, row in enumerate(grid):
        cells = list(row)
        if mirror:
            cells.reverse()
        for sx, ch in enumerate(cells):
            r, g, b, a = PALETTE[ch]
            if a == 0:
                continue
            r, g, b = (int(v * dim) for v in (r, g, b))
            for dy in range(scale):
                for dx in range(scale):
                    px = ox + sx * scale + dx
                    py = oy + sy * scale + dy
                    if 0 <= px < SIZE and 0 <= py < SIZE:
                        pixels[py * SIZE + px] = (r, g, b, 255)


def main():
    pixels = []
    for y in range(SIZE):
        t = y / (SIZE - 1)
        base = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(SIZE):
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if edge < 12:
                pixels.append(BORDER + (255,))
            elif edge < 20:
                pixels.append((base[0] // 2, base[1] // 2, base[2] // 2, 255))
            else:
                pixels.append(base + (255,))

    # 장검 하나만 크게 얹는다.
    # 도끼를 뒤집어 X자로 겹쳐도 봤는데, 16x16 스프라이트 두 장이 겹치니
    # 뒤에 깔린 날이 배경 상자처럼 보여 오히려 알아보기 어려웠다.
    scale = 48
    span = 16 * scale
    offset = (SIZE - span) // 2
    blit(pixels, SPRITES["longsword"], scale, offset, offset)

    write_png(OUT, SIZE, SIZE, pixels)
    print("생성:", os.path.relpath(OUT, ROOT), "(%dx%d)" % (SIZE, SIZE))


if __name__ == "__main__":
    main()
