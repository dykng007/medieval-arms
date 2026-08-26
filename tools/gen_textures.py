#!/usr/bin/env python3
"""
갑옷을 입었을 때 몸에 덧씌워지는 레이어 텍스처를 만든다.

실행:  python tools/gen_textures.py

── 이 파일이 만들지 않는 것 ────────────────────────────────────────────
아이템 아이콘(인벤토리에 보이는 그림)은 여기서 만들지 않는다.
그건 GPT로 그린 뒤 tools/import_art.py 가 16x16으로 변환한다.
예전에는 여기서 ASCII 격자로 아이콘까지 그렸는데, 손으로 그린 결과가
게임에서 알아보기 어려웠다. 그 격자와 팔레트는 레이어 텍스처의 색을
정하는 데 아직 쓰이므로 아래 SPRITES/PALETTE 는 남겨둔다.

이 파일을 실행해도 아이템 아이콘은 건드리지 않는다.

외부 라이브러리 없이 표준 라이브러리만 쓴다.
"""

import os
import struct
import zlib

# 레이어 텍스처의 배율. 바닐라 갑옷 레이어는 64x32 이고, 여기에 이 값을 곱한다.
# 아이템 아이콘이 32x32(바닐라의 2배)라 레이어도 2배로 맞춰 화질을 통일한다.
# tools/import_art.py 의 SIZE 를 바꾸면 이 값도 같이 맞춰야 한다.
LAYER_SCALE = 2
LAYER_W, LAYER_H = 64 * LAYER_SCALE, 32 * LAYER_SCALE

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
#
# 그리는 규칙 세 가지:
#  1. 자루는 왼쪽 아래, 날/머리는 오른쪽 위. 손에 비스듬히 쥔 모습이 되도록.
#  2. 날은 자루와 나란한 방향으로 각지게. 가로로 퍼진 둥근 덩어리는
#     16x16에서 "막대 끝에 뭔가 붙은 것"으로만 보이고 무기로 읽히지 않는다.
#  3. 실루엣만으로 구분되어야 한다. 안쪽 명암은 확대해야 보이므로 형태에 기대면 안 된다.
SPRITES = {
    # 창 — 자루와 나란한 가늘고 긴 촉
    "spear": [
        ".............k..",
        "............kIk.",
        "...........kIsk.",
        "..........kIIsk.",
        ".........kIIsk..",
        "........kIIsk...",
        "........kIsk....",
        ".......kksk.....",
        ".......kwk......",
        "......kwWk......",
        ".....kwWk.......",
        "....kwWk........",
        "...kwWk.........",
        "..kwWk..........",
        "..kwk...........",
        "..kk............",
    ],
    # 미늘창 — 위로 뻗은 촉 + 자루 옆에 붙은 도끼날
    "halberd": [
        "..........k.....",
        ".........kIk....",
        ".........kIk....",
        "...kkkkk.kIk....",
        "..kIIIIIkkIk....",
        "..kIIIIIIIIk....",
        "..kIIIIIkkIk....",
        "...kkkkk.kwk....",
        ".........kwk....",
        "........kwWk....",
        ".......kwWk.....",
        "......kwWk......",
        ".....kwWk.......",
        "....kwWk........",
        "...kwWk.........",
        "...kwk..........",
    ],
    # 철퇴 — 세로 능선(플랜지)이 드러난 머리
    "mace": [
        ".....kkkkk......",
        "....kIIsIIk.....",
        "...kIIIsIIIk....",
        "..kIIIIsIIIIk...",
        "..kIIIIsIIIIk...",
        "...kIIIsIIIk....",
        "....kIIsIIk.....",
        ".....kkkkk......",
        "......kwWk......",
        ".....kwWk.......",
        "....kwWk........",
        "...kwWk.........",
        "..kwWk..........",
        ".kwWk...........",
        ".kwk............",
        ".kk.............",
    ],
    # 전투도끼 — 왼쪽으로 벌어진 날, 오른쪽에 자루
    "battleaxe": [
        "...kkkkkk.......",
        "..kIIIIIIk......",
        ".kIIIIIIIk......",
        "kIIIIIIIsk......",
        "kIIIIIIIsk......",
        ".kIIIIIIsk......",
        "..kIIIIIsk......",
        "...kkkkkkk......",
        ".......kwWk.....",
        "......kwWk......",
        ".....kwWk.......",
        "....kwWk........",
        "...kwWk.........",
        "..kwWk..........",
        "..kwk...........",
        "..kk............",
    ],
    # 워해머 — 다이아 급. 육중한 사각 머리
    "warhammer": [
        "....kkkkkkk.....",
        "...kDDDDDDDk....",
        "...kDeeeeeDk....",
        "...kDeddddDk....",
        "...kDeeeeeDk....",
        "...kDDDDDDDk....",
        "....kkkkkkk.....",
        "......kwWk......",
        ".....kwWk.......",
        "....kwWk........",
        "....kwWk........",
        "...kwWk.........",
        "..kwWk..........",
        ".kwWk...........",
        ".kwk............",
        ".kk.............",
    ],
    # 장검 — 다이아 급. 금 십자가드 + 가죽 손잡이
    "longsword": [
        ".............kk.",
        "............kDk.",
        "...........kDek.",
        "..........kDek..",
        ".........kDek...",
        "........kDek....",
        ".......kDek.....",
        "......kDek......",
        ".....kDek.......",
        "....kgGgk.......",
        "...kgGkGgk......",
        "....kklkk.......",
        ".....klLk.......",
        "....klLk........",
        "....klk.........",
        "....kGk.........",
    ],
}

# ── 갑옷 스프라이트 ─────────────────────────────────────────────────────
# 모양은 두 세트가 공유하고 색만 다르다.
# 1 = 어두운색, 2 = 중간색, 3 = 밝은색, 4 = 장식색.
#
# 상자처럼 보이지 않으려면 부위별 실루엣이 분명해야 한다.
# 투구는 위가 좁아지는 돔에 눈구멍, 흉갑은 어깨가 몸통보다 넓게 튀어나온 T자,
# 각반과 장화는 두 다리로 갈라진 형태다.
ARMOR_SHAPES = {
    "helmet": [
        "......kkkk......",
        "....kk3333kk....",
        "...k33333333k...",
        "..k3333333333k..",
        "..k3322222233k..",
        "..k32kkkkkk23k..",
        "..k32kkkkkk23k..",
        "..k3222222223k..",
        "..k3222222223k..",
        "..k3322222233k..",
        "..k3344444433k..",
        "...kkkkkkkkkk...",
        "................",
        "................",
        "................",
        "................",
    ],
    "chestplate": [
        "kkkk........kkkk",
        "k33k........k33k",
        "k33kkkkkkkkkk33k",
        "k33322222222333k",
        "k33322111122333k",
        "k33322144122333k",
        "k33322111122333k",
        ".kk3222222223kk.",
        "..k4444444444k..",
        "..k2222222222k..",
        "..kkkkkkkkkkkk..",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "leggings": [
        "...kkkkkkkkkk...",
        "..kk44444444kk..",
        "..k3322222233k..",
        "..k3322222233k..",
        "...k22222222k...",
        "...k22kkkk22k...",
        "...k22....22k...",
        "...k11....11k...",
        "...k11....11k...",
        "...k11....11k...",
        "...kkk....kkk...",
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
        "..k11......11k..",
        ".kk11k....k11kk.",
        ".k1111k..k1111k.",
        ".kkkkkk..kkkkkk.",
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
# 좌표는 바닐라 64x32 기준으로 적고, 쓸 때 LAYER_SCALE 을 곱한다.
_LAYER_1_RECTS = [
    (0, 0, 32, 16),    # 머리(투구)
    (16, 16, 40, 32),  # 몸통
    (40, 16, 56, 32),  # 팔
]
_LAYER_2_RECTS = [
    (0, 16, 16, 32),   # 다리
    (16, 16, 40, 32),  # 허리
]


def _scaled(rects):
    return [tuple(v * LAYER_SCALE for v in r) for r in rects]


LAYER_1_RECTS = _scaled(_LAYER_1_RECTS)
LAYER_2_RECTS = _scaled(_LAYER_2_RECTS)


def main():
    made = []

    # 갑옷 착용 레이어 (세트당 2장)
    layer_colors = {
        "squire": (PALETTE["i"], PALETTE["s"], PALETTE["I"]),
        "knight": (PALETTE["d"], PALETTE["e"], PALETTE["D"]),
    }
    for set_name, (dark, mid, light) in layer_colors.items():
        for layer_no, rects in ((1, LAYER_1_RECTS), (2, LAYER_2_RECTS)):
            path = os.path.join(ARMOR_DIR, f"{set_name}_layer_{layer_no}.png")
            write_png(path, LAYER_W, LAYER_H,
                      build_armor_layer(LAYER_W, LAYER_H, rects, dark, mid, light))
            made.append(path)

    for p in made:
        print("생성:", os.path.relpath(p, ROOT))
    print()
    print("갑옷 레이어 %d장 생성 완료." % len(made))
    print("아이템 아이콘은 tools/import_art.py 가 담당한다.")


if __name__ == "__main__":
    main()
