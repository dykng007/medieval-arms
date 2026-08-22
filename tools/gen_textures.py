#!/usr/bin/env python3
"""
Medieval Arms 텍스처 생성기.

외부 라이브러리(Pillow 등) 없이 표준 라이브러리만으로 PNG를 쓴다.
실행:  python tools/gen_textures.py

아이템 텍스처는 아래 SPRITES 딕셔너리에 16x16 ASCII 격자로 정의되어 있다.
글자 하나가 픽셀 하나이고, 의미는 PALETTE에 있다.
마음에 안 드는 모양은 격자 글자만 바꾸고 다시 실행하면 된다.
직접 그린 png로 덮어써도 되고, 그 경우 이 스크립트를 다시 실행하지만 않으면 된다.
"""

import os
import struct
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEM_DIR = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "item")
ARMOR_DIR = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "models", "armor")

# ── 팔레트 ────────────────────────────────────────────────────────────────
# 글자 -> (R, G, B, A).  '.' 은 투명.
PALETTE = {
    ".": (0, 0, 0, 0),
    "k": (26, 22, 20, 255),      # 외곽선 (완전한 검정보다 살짝 갈색끼)
    # 나무 자루
    "w": (86, 60, 36, 255),      # 어두운 나무
    "W": (124, 90, 56, 255),     # 밝은 나무
    # 철 (일반 무기 / Squire 갑옷)
    "i": (108, 116, 124, 255),   # 어두운 철
    "s": (150, 158, 166, 255),   # 중간 철
    "I": (196, 204, 212, 255),   # 밝은 철 (하이라이트)
    # 강청색 (다이아 급 무기 / Knight 갑옷)
    "d": (44, 96, 118, 255),     # 어두운
    "e": (72, 148, 176, 255),    # 중간
    "D": (128, 208, 232, 255),   # 밝은
    # 금 장식
    "g": (196, 152, 48, 255),
    "G": (240, 208, 104, 255),
    # 가죽 끈 / 천
    "l": (92, 62, 44, 255),
    "L": (140, 104, 72, 255),
}


def write_png(path, width, height, pixels):
    """RGBA 픽셀 리스트(행 우선)를 PNG 파일로 쓴다."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # 각 스캔라인의 필터 타입 = None
        for x in range(width):
            raw.extend(pixels[y * width + x])

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    # 비트깊이 8, 컬러타입 6 (RGBA)
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def grid_to_png(path, grid):
    """16줄 x 16글자 ASCII 격자를 PNG로 변환."""
    if len(grid) != 16:
        raise ValueError(f"{path}: 행이 16개가 아니라 {len(grid)}개")
    pixels = []
    for y, row in enumerate(grid):
        if len(row) != 16:
            raise ValueError(f"{path}: {y}번 행의 길이가 16이 아니라 {len(row)} -> {row!r}")
        for ch in row:
            if ch not in PALETTE:
                raise ValueError(f"{path}: 팔레트에 없는 글자 {ch!r}")
            pixels.append(PALETTE[ch])
    write_png(path, 16, 16, pixels)


# ── 무기 스프라이트 ──────────────────────────────────────────────────────
# 16줄 x 16글자. 글자 뜻은 위 PALETTE 참고.
SPRITES = {
    # 창 — 긴 자루에 작은 나뭇잎 모양 촉
    "spear": [
        "..............k.",
        ".............kIk",
        "............kIIk",
        "...........kIIk.",
        "..........kIIk..",
        ".........kIsk...",
        "........kwIk....",
        ".......kwWk.....",
        "......kwWk......",
        ".....kwWk.......",
        "....kwWk........",
        "...kwWk.........",
        "..kwWk..........",
        ".kwWk...........",
        ".kwk............",
        ".kk.............",
    ],
    # 미늘창 — 자루 끝에 도끼날 + 찌르는 촉
    "halberd": [
        "............k...",
        "...........kIk..",
        "......kkk..kIk..",
        ".....kIIIkkIsk..",
        "....kIIIIIIIsk..",
        ".....kIIIkkIsk..",
        "......kkk..kwk..",
        "..........kwWk..",
        "..........kwWk..",
        ".........kwWk...",
        "........kwWk....",
        ".......kwWk.....",
        "......kwWk......",
        ".....kwWk.......",
        "....kwWk........",
        "....kwk.........",
    ],
    # 철퇴 — 짧은 자루에 가시 달린 둥근 머리
    "mace": [
        ".....k.k.k......",
        "....kIkIkIk.....",
        "...kkIIIIIkk....",
        "..kIIIsIIsIIk...",
        "..kIIsIIIIsIk...",
        ".kkIIIIIIIIkk...",
        "..kIIsIIIIsIk...",
        "..kIIIsIIsIIk...",
        "...kkIIIIIkk....",
        "....kIkIkIk.....",
        ".....kkwkk......",
        "......kwWk......",
        ".....kwWk.......",
        "....kwWk........",
        "...kwWk.........",
        "...kwk..........",
    ],
    # 워해머 — 다이아 급. 육중한 사각 망치머리
    "warhammer": [
        ".....kkkkkk.....",
        "....kDDDDDDk....",
        "...kDeeeeeeDk...",
        "...kDeddddeDk...",
        "...kDeddddeDk...",
        "...kDeeeeeeDk...",
        "....kDDDDDDk....",
        ".....kkdwkk.....",
        ".......kwWk.....",
        "......kwWk......",
        "......kwWk......",
        ".....kwWk.......",
        ".....kwWk.......",
        "....kwWk........",
        "....kwWk........",
        "....kwk.........",
    ],
    # 전부 — 초승달 모양 큰 날
    "battleaxe": [
        "........kkk.....",
        "......kkIIIk....",
        ".....kIIIIIk....",
        "....kIIIIsIk....",
        "...kIIIIIsIk....",
        "...kIIIIIsIk....",
        "...kIIIIsIk.....",
        "....kIIIIk......",
        ".....kkkwk......",
        ".......kwWk.....",
        "......kwWk......",
        "......kwWk......",
        ".....kwWk.......",
        ".....kwWk.......",
        "....kwWk........",
        "....kwk.........",
    ],
    # 장검 — 다이아 급. 금 십자가드 + 가죽 손잡이
    "longsword": [
        "..............k.",
        ".............kDk",
        "............kDek",
        "...........kDek.",
        "..........kDek..",
        ".........kDek...",
        "........kDek....",
        ".......kDek.....",
        "......kDek......",
        ".....kgGgk......",
        "....kgGkgk......",
        "...kgGk.kk......",
        "..klLk..........",
        ".klLk...........",
        ".klLk...........",
        ".kGk............",
    ],
}

# ── 갑옷 스프라이트 ─────────────────────────────────────────────────────
# 모양은 두 세트가 공유하고 색만 다르다.
# 1 = 어두운색, 2 = 중간색, 3 = 밝은색, 4 = 장식색.
ARMOR_SHAPES = {
    "helmet": [
        "....kkkkkkkk....",
        "..k3333333333k..",
        "..k3222222223k..",
        "..k3222222223k..",
        "..k3211111123k..",
        "..k32kkkkkk23k..",
        "..k32kkkkkk23k..",
        "..k3211111123k..",
        "..k3222222223k..",
        "..k3444444443k..",
        "..kkkkkkkkkkkk..",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "chestplate": [
        ".kkk........kkk.",
        ".k33k......k33k.",
        ".k33kkkkkkkk33k.",
        ".k332222222233k.",
        ".k332211112233k.",
        ".k332214412233k.",
        ".k332211112233k.",
        ".k332222222233k.",
        ".k333444444333k.",
        ".k332222222233k.",
        ".kkkkkkkkkkkkkk.",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "leggings": [
        "..kkkkkkkkkkkk..",
        "..k3322222233k..",
        "..k3322222233k..",
        "..k3344444433k..",
        "..k3322222233k..",
        "..k3311111133k..",
        "..k33......33k..",
        "..k22......22k..",
        "..k22......22k..",
        "..kkk......kkk..",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "boots": [
        "................",
        "................",
        "................",
        "................",
        "..kkk......kkk..",
        "..k33......33k..",
        "..k33......33k..",
        "..k22......22k..",
        "..k22......22k..",
        "..k44......44k..",
        "..k1111..1111k..",
        "..kkkkk..kkkkk..",
        "................",
        "................",
        "................",
        "................",
    ],
}

# 세트별 색 대응. 1/2/3/4 를 실제 팔레트 글자로 바꾼다.
ARMOR_SETS = {
    "squire": {"1": "i", "2": "s", "3": "I", "4": "s"},   # 철 급
    "knight": {"1": "d", "2": "e", "3": "D", "4": "g"},   # 다이아 급 + 금장식
}


def build_armor_layer(width, height, rects, dark, mid, light):
    """
    갑옷을 '입었을 때' 플레이어 몸에 덧씌워지는 레이어 텍스처를 만든다.

    아이템 아이콘과 달리 이건 플레이어 모델에 감기는 전개도라서
    ASCII로 그리기엔 너무 넓다(64x32). 대신 필요한 사각 영역만
    단색으로 채우고 테두리를 어둡게 해서 입체감만 준다.
    나중에 제대로 그린 png로 덮어쓰면 된다.
    """
    transparent = (0, 0, 0, 0)
    pixels = [transparent] * (width * height)
    for (x0, y0, x1, y1) in rects:
        for y in range(y0, y1):
            for x in range(x0, x1):
                on_edge = x in (x0, x1 - 1) or y in (y0, y1 - 1)
                # 위쪽 절반은 밝게, 아래쪽은 어둡게 해서 광원이 위에 있는 느낌
                if on_edge:
                    color = dark
                elif y < y0 + (y1 - y0) // 3:
                    color = light
                else:
                    color = mid
                pixels[y * width + x] = color
    return pixels


# 바닐라 갑옷 레이어의 UV 배치에 맞춘 영역.
# layer_1 = 투구 + 상체 + 팔 + 부츠,  layer_2 = 각반(다리)
LAYER_1_RECTS = [
    (0, 0, 32, 16),    # 머리(투구)
    (16, 16, 40, 32),  # 몸통
    (40, 16, 56, 32),  # 팔
]
LAYER_2_RECTS = [
    (0, 16, 16, 32),   # 다리
    (16, 16, 40, 32),  # 허리
]


def main():
    made = []

    # 무기 아이템 아이콘
    for name, grid in SPRITES.items():
        path = os.path.join(ITEM_DIR, f"{name}.png")
        grid_to_png(path, grid)
        made.append(path)

    # 갑옷 아이템 아이콘 (모양 4가지 x 세트 2개 = 8개)
    for set_name, mapping in ARMOR_SETS.items():
        for piece, shape in ARMOR_SHAPES.items():
            grid = ["".join(mapping.get(ch, ch) for ch in row) for row in shape]
            path = os.path.join(ITEM_DIR, f"{set_name}_{piece}.png")
            grid_to_png(path, grid)
            made.append(path)

    # 갑옷 착용 레이어 (세트당 2장)
    layer_colors = {
        "squire": (PALETTE["i"], PALETTE["s"], PALETTE["I"]),
        "knight": (PALETTE["d"], PALETTE["e"], PALETTE["D"]),
    }
    for set_name, (dark, mid, light) in layer_colors.items():
        for layer_no, rects in ((1, LAYER_1_RECTS), (2, LAYER_2_RECTS)):
            path = os.path.join(ARMOR_DIR, f"{set_name}_layer_{layer_no}.png")
            write_png(path, 64, 32, build_armor_layer(64, 32, rects, dark, mid, light))
            made.append(path)

    for p in made:
        print("생성:", os.path.relpath(p, ROOT))
    print(f"\n총 {len(made)}개 텍스처 생성 완료.")


if __name__ == "__main__":
    main()
