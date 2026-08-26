#!/usr/bin/env python3
"""
갑옷을 입었을 때 몸에 씌워지는 레이어 텍스처를 만든다.

실행:  python tools/gen_armor_layers.py
입력:  .../textures/item/squire_{helmet,chestplate,leggings,boots}.png
출력:  .../textures/models/armor/<세트>_layer_{1,2}.png

필요:  pip install pillow numpy

── 왜 아이템 아이콘에서 떠오는가 ──────────────────────────────────────
앞서는 판금 재질을 칸마다 타일링해 만들었는데, 무늬만 있고 형태가 없어서
아이콘에 비해 초라해 보였다. 아이콘 쪽은 견갑과 바이저와 무릎받이가 그려진
조각된 갑옷인데, 착용 텍스처는 그냥 줄무늬 통이었던 셈이다.

아이콘 자체가 갑옷의 정면도이므로, 거기서 부위를 떼어 몸의 해당 면에 붙인다.
그러면 인벤토리에서 본 그림과 입었을 때가 같은 갑옷으로 보인다.

── 어느 레이어가 어느 부위를 그리는가 ────────────────────────────────
HumanoidArmorLayer.setPartVisibility 를 그대로 옮긴 것이다.

    투구  head + hat       layer_1
    흉갑  body + 양팔      layer_1
    각반  body + 양다리    layer_2
    장화  양다리           layer_1

hat 칸은 비워둔다. 바닐라 갑옷도 비워두는데, 채우면 투구 바깥에 껍데기가
한 겹 더 생겨 부풀어 보인다.

장화와 흉갑이 같은 layer_1 을 쓰기 때문에 다리 칸을 위까지 채우면 장화가
정강이받이처럼 보인다. 그래서 다리 칸은 아래쪽만 채운다.
"""

import os
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError as exc:
    sys.exit("필요한 패키지가 없습니다: %s\n  pip install pillow numpy" % exc.name)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "item")
OUT = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "models", "armor")

# 바닐라 레이어는 64x32. 아이템 아이콘이 32x32(바닐라의 2배)라 여기도 2배로 맞춘다.
# tools/import_art.py 의 SIZE 를 바꾸면 여기도 같이 맞춰야 한다.
SCALE = 2
WIDTH, HEIGHT = 64 * SCALE, 32 * SCALE

# 크롭에 구멍이 있어도 갑옷이 뚫려 보이지 않도록 깔아두는 바탕 강판 색.
BASE_LIGHT = (196, 202, 210)
BASE_DARK = (92, 98, 108)


def faces(u, v, w, h, d):
    """상자 하나의 UV 전개도. 마인크래프트가 정한 배치이고 바꿀 수 없다."""
    return {
        "top":    (u + d,         v,     w, d),
        "bottom": (u + d + w,     v,     w, d),
        "right":  (u,             v + d, d, h),
        "front":  (u + d,         v + d, w, h),
        "left":   (u + d + w,     v + d, d, h),
        "back":   (u + d + w + d, v + d, w, h),
    }


# HumanoidModel.createMesh 의 texOffs / addBox 값 그대로.
PARTS = {
    "head": faces(0, 0, 8, 8, 8),
    "body": faces(16, 16, 8, 12, 4),
    "arm":  faces(40, 16, 4, 12, 4),
    "leg":  faces(0, 16, 4, 12, 4),
}

# 아이콘에서 떼어낼 영역. 32x32 아이콘 안의 (좌, 상, 우, 하).
# 아이콘 위에 격자를 그려 눈으로 고른 값이다.
CROPS = {
    "helmet_front":  (5, 2, 27, 29),    # 투구 정면 전체 (십자 장식과 바이저)
    "helmet_side":   (7, 4, 17, 29),    # 옆면용. 십자 세로줄을 피한 왼쪽 절반
    "helmet_top":    (7, 2, 25, 10),    # 정수리
    "chest_front":   (10, 4, 22, 28),   # 견갑을 뺀 가운데 몸통
    "chest_side":    (11, 6, 16, 28),   # 몸통 옆면용 좁은 띠
    "chest_top":     (10, 3, 22, 9),    # 목깃
    "pauldron":      (3, 3, 13, 18),    # 왼쪽 견갑
    "leg_front":     (7, 3, 16, 30),    # 각반 왼쪽 다리
    "belt":          (7, 1, 25, 8),     # 각반 허리띠
    "boot":          (3, 11, 15, 29),   # 장화 한 짝의 아래쪽
}

SETS = {
    "squire": None,                 # 강철 그대로
    "knight": (0.58, 0.86, 1.00),   # 다이아 등급이라 청색
}


def load_icons():
    icons = {}
    for name in ("helmet", "chestplate", "leggings", "boots"):
        path = os.path.join(ITEMS, "squire_%s.png" % name)
        if not os.path.exists(path):
            return None
        icons[name] = Image.open(path).convert("RGBA")
    return icons


def base_plate(w, h):
    """면을 채울 바탕. 위가 밝고 아래가 어두워 입체감이 생긴다."""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(BASE_LIGHT[i] + (BASE_DARK[i] - BASE_LIGHT[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c + (255,)
    return img


def paste_face(canvas, icon, crop, face, top_ratio=0.0, dim=1.0, flip=False):
    """
    아이콘의 한 부분을 몸의 한 면에 붙인다.

    top_ratio 는 면의 위쪽 몇 할을 비울지다 (장화처럼 아래만 덮을 때).
    dim 은 밝기 배수. 옆면과 뒷면을 살짝 어둡게 해 정면이 도드라지게 한다.
    """
    x, y, w, h = face
    X, Y, W, H = x * SCALE, y * SCALE, w * SCALE, h * SCALE
    cut = int(H * top_ratio)
    fh = H - cut
    if fh <= 0:
        return

    piece = icon.crop(crop)
    if flip:
        piece = piece.transpose(Image.FLIP_LEFT_RIGHT)
    piece = piece.resize((W, fh), Image.NEAREST)

    # 크롭에 투명한 구멍이 있어도 갑옷이 뚫려 보이지 않게 바탕을 먼저 깐다.
    tile = base_plate(W, fh)
    tile.alpha_composite(piece)

    arr = np.array(tile).astype(np.float32)
    if dim != 1.0:
        arr[:, :, :3] = np.clip(arr[:, :, :3] * dim, 0, 255)
    canvas[Y + cut:Y + H, X:X + W] = arr


def build_layer_1(icons):
    canvas = np.zeros((HEIGHT, WIDTH, 4), dtype=np.float32)
    helm, chest, boots = icons["helmet"], icons["chestplate"], icons["boots"]

    # 투구 — 정면은 아이콘 그대로. 뒤통수는 바이저가 있으면 안 되므로 옆면 크롭을 쓴다.
    paste_face(canvas, helm, CROPS["helmet_front"], PARTS["head"]["front"])
    paste_face(canvas, helm, CROPS["helmet_side"], PARTS["head"]["right"], dim=0.88)
    paste_face(canvas, helm, CROPS["helmet_side"], PARTS["head"]["left"], dim=0.88, flip=True)
    paste_face(canvas, helm, CROPS["helmet_side"], PARTS["head"]["back"], dim=0.80)
    paste_face(canvas, helm, CROPS["helmet_top"], PARTS["head"]["top"])
    paste_face(canvas, helm, CROPS["helmet_top"], PARTS["head"]["bottom"], dim=0.55)
    # hat 칸은 일부러 비운다. 채우면 투구가 두 겹으로 부푼다.

    # 흉갑
    paste_face(canvas, chest, CROPS["chest_front"], PARTS["body"]["front"])
    paste_face(canvas, chest, CROPS["chest_front"], PARTS["body"]["back"], dim=0.78)
    paste_face(canvas, chest, CROPS["chest_side"], PARTS["body"]["right"], dim=0.86)
    paste_face(canvas, chest, CROPS["chest_side"], PARTS["body"]["left"], dim=0.86, flip=True)
    paste_face(canvas, chest, CROPS["chest_top"], PARTS["body"]["top"])
    paste_face(canvas, chest, CROPS["chest_top"], PARTS["body"]["bottom"], dim=0.55)

    # 팔 — 견갑을 팔 전체에 붙인다. 아이콘의 견갑이 위가 두툼하고 아래로
    # 좁아지는 모양이라, 늘려도 어깨에서 소매로 이어지는 느낌이 난다.
    for side, flip, dim in (("right", False, 1.0), ("left", True, 1.0),
                            ("front", False, 0.94), ("back", True, 0.80)):
        paste_face(canvas, chest, CROPS["pauldron"], PARTS["arm"][side], dim=dim, flip=flip)
    paste_face(canvas, chest, CROPS["pauldron"], PARTS["arm"]["top"])
    paste_face(canvas, chest, CROPS["pauldron"], PARTS["arm"]["bottom"], dim=0.55)

    # 장화 — 다리 칸의 아래쪽만. 위까지 채우면 정강이받이가 된다.
    for side, flip, dim in (("front", False, 1.0), ("right", False, 0.88),
                            ("left", True, 0.88), ("back", True, 0.80)):
        paste_face(canvas, boots, CROPS["boot"], PARTS["leg"][side],
                   top_ratio=0.58, dim=dim, flip=flip)
    paste_face(canvas, boots, CROPS["boot"], PARTS["leg"]["bottom"], dim=0.6)
    return canvas


def build_layer_2(icons):
    canvas = np.zeros((HEIGHT, WIDTH, 4), dtype=np.float32)
    legs = icons["leggings"]

    # 허리 — 몸통 칸의 아래쪽만 채워 벨트처럼 보이게 한다.
    for side, dim in (("front", 1.0), ("back", 0.78), ("right", 0.86), ("left", 0.86)):
        paste_face(canvas, legs, CROPS["belt"], PARTS["body"][side], top_ratio=0.58, dim=dim)
    paste_face(canvas, legs, CROPS["belt"], PARTS["body"]["bottom"], dim=0.55)

    # 각반 — 다리 전체
    for side, flip, dim in (("front", False, 1.0), ("right", False, 0.88),
                            ("left", True, 0.88), ("back", True, 0.80)):
        paste_face(canvas, legs, CROPS["leg_front"], PARTS["leg"][side], dim=dim, flip=flip)
    paste_face(canvas, legs, CROPS["leg_front"], PARTS["leg"]["top"], dim=0.9)
    paste_face(canvas, legs, CROPS["leg_front"], PARTS["leg"]["bottom"], dim=0.55)
    return canvas


def tint(canvas, factors):
    if factors is None:
        return canvas
    out = canvas.copy()
    opaque = out[:, :, 3] > 0
    for c, f in enumerate(factors):
        out[:, :, c][opaque] = np.clip(out[:, :, c][opaque] * f, 0, 255)
    return out


def main():
    icons = load_icons()
    if icons is None:
        print("갑옷 아이템 아이콘이 없습니다. 먼저 tools/import_art.py 를 돌리세요.")
        return 2

    os.makedirs(OUT, exist_ok=True)
    layers = {1: build_layer_1(icons), 2: build_layer_2(icons)}
    for set_name, factors in SETS.items():
        for no, canvas in layers.items():
            path = os.path.join(OUT, "%s_layer_%d.png" % (set_name, no))
            Image.fromarray(tint(canvas, factors).astype(np.uint8), "RGBA").save(path)
            solid = int((canvas[:, :, 3] > 0).sum())
            print("  %-22s %dx%d  채운 픽셀 %5d" % (os.path.basename(path), WIDTH, HEIGHT, solid))

    print()
    print("갑옷 레이어 4장 생성 완료.")
    print("몸에 어떻게 보이는지는 tools/preview_armor.py 로 확인한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
