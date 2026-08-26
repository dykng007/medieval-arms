#!/usr/bin/env python3
"""
갑옷 레이어 텍스처가 몸에 입혀졌을 때 어떻게 보이는지 정면에서 미리 본다.

실행:  python tools/preview_armor.py
결과:  화면에 경로가 찍히고 그 위치에 png 가 생긴다 (저장소에는 커밋하지 않는다)

레이어 텍스처는 전개도라 파일만 봐서는 몸에 어떻게 발리는지 알 수 없다.
게임을 켜고 갑옷을 실제로 입어봐야 하는데, 그 전에 앞모습만이라도
확인하려고 만든 도구다. 각 부위의 '앞면' 칸만 떼어 사람 모양으로 붙인다.

옆면과 뒷면은 보이지 않으므로, 여기서 멀쩡해 보여도 게임에서 확인은 필요하다.
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow 가 필요합니다:  pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMOR = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "models", "armor")
OUT = os.path.join(ROOT, "build", "armor-preview.png")

SCALE = 2      # 레이어 텍스처가 바닐라의 몇 배인지 (gen_armor_layers.py 의 SCALE)
ZOOM = 14      # 미리보기 확대 배율

# 각 부위의 '앞면' 칸 (바닐라 64x32 기준 좌표)와, 사람 모양에서의 위치.
# 사람 앞모습은 가로 16, 세로 32 칸이다.
FRONT = [
    # (레이어, 텍스처 x, y, 너비, 높이,  놓을 x, y, 좌우반전)
    (2, 4, 20, 4, 12,  4, 20, False),   # 오른다리 - 각반
    (2, 4, 20, 4, 12,  8, 20, True),    # 왼다리  - 각반
    (2, 20, 20, 8, 12, 4, 8,  False),   # 허리    - 각반
    (1, 4, 20, 4, 12,  4, 20, False),   # 오른다리 - 장화(아래쪽만 채워져 있다)
    (1, 4, 20, 4, 12,  8, 20, True),    # 왼다리  - 장화
    (1, 20, 20, 8, 12, 4, 8,  False),   # 몸통    - 흉갑
    (1, 44, 20, 4, 12, 0, 8,  False),   # 오른팔  - 흉갑
    (1, 44, 20, 4, 12, 12, 8, True),    # 왼팔    - 흉갑
    (1, 8, 8, 8, 8,    4, 0,  False),   # 머리    - 투구
    (1, 40, 8, 8, 8,   4, 0,  False),   # 모자칸  - 투구 바깥층
]


def build(set_name):
    layers = {}
    for n in (1, 2):
        path = os.path.join(ARMOR, "%s_layer_%d.png" % (set_name, n))
        if not os.path.exists(path):
            return None
        layers[n] = Image.open(path).convert("RGBA")

    body = Image.new("RGBA", (16 * ZOOM, 32 * ZOOM), (0, 0, 0, 0))
    for layer, tx, ty, tw, th, px, py, flip in FRONT:
        crop = layers[layer].crop((tx * SCALE, ty * SCALE,
                                   (tx + tw) * SCALE, (ty + th) * SCALE))
        if flip:
            crop = crop.transpose(Image.FLIP_LEFT_RIGHT)
        crop = crop.resize((tw * ZOOM, th * ZOOM), Image.NEAREST)
        body.alpha_composite(crop, (px * ZOOM, py * ZOOM))
    return body


def main():
    sets = ["squire", "knight"]
    shots = [(s, build(s)) for s in sets]
    shots = [(s, im) for s, im in shots if im is not None]
    if not shots:
        print("레이어 텍스처가 없습니다. 먼저 tools/gen_armor_layers.py 를 돌리세요.")
        return 2

    pad = 20
    w = sum(im.width for _, im in shots) + pad * (len(shots) + 1)
    h = shots[0][1].height + pad * 2
    sheet = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # 투명한 곳을 알아보기 위한 체크무늬
    for y in range(h):
        for x in range(w):
            c = 200 if ((x // 10) + (y // 10)) % 2 == 0 else 160
            sheet.putpixel((x, y), (c, c, c, 255))

    x = pad
    for _, im in shots:
        sheet.alpha_composite(im, (x, pad))
        x += im.width + pad

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print("미리보기:", OUT)
    print("왼쪽부터:", ", ".join(s for s, _ in shots))
    return 0


if __name__ == "__main__":
    sys.exit(main())
