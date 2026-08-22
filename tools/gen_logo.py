#!/usr/bin/env python3
"""
CurseForge 프로젝트 아이콘을 만든다.

실행:  python tools/gen_logo.py
결과:  docs/logo.png (400x400)

CurseForge 프로젝트 페이지의 아바타로 쓴다. 권장 크기가 400x400이다.
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

SIZE = 400
OUT = os.path.join(ROOT, "docs", "logo.png")

# 배경: 어두운 석재 느낌의 세로 그라데이션
BG_TOP = (58, 62, 70)
BG_BOTTOM = (34, 36, 42)
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

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def main():
    pixels = []
    for y in range(SIZE):
        t = y / (SIZE - 1)
        base = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(SIZE):
            # 바깥쪽 테두리
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            if edge < 6:
                pixels.append(BORDER + (255,))
            elif edge < 10:
                pixels.append((base[0] // 2, base[1] // 2, base[2] // 2, 255))
            else:
                pixels.append(base + (255,))

    # 장검 스프라이트를 확대해 가운데 배치.
    # 16px 스프라이트에 24배를 곱해 384px, 양옆에 8px씩 여백이 남는다.
    grid = SPRITES["longsword"]
    scale = 24
    offset = (SIZE - 16 * scale) // 2
    for sy, row in enumerate(grid):
        for sx, ch in enumerate(row):
            r, g, b, a = PALETTE[ch]
            if a == 0:
                continue
            for dy in range(scale):
                for dx in range(scale):
                    px = offset + sx * scale + dx
                    py = offset + sy * scale + dy
                    if 0 <= px < SIZE and 0 <= py < SIZE:
                        pixels[py * SIZE + px] = (r, g, b, 255)

    write_png(OUT, SIZE, SIZE, pixels)
    print("생성:", os.path.relpath(OUT, ROOT), "(%dx%d)" % (SIZE, SIZE))


if __name__ == "__main__":
    main()
