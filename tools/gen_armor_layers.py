#!/usr/bin/env python3
"""
갑옷을 입었을 때 몸에 씌워지는 레이어 텍스처를 만든다.

실행:  python tools/gen_armor_layers.py
입력:  art/plate-material.png   판금 재질 (이음새 없이 반복되는 그림)
출력:  .../textures/models/armor/<세트>_layer_1.png, _layer_2.png

필요:  pip install pillow numpy

── 왜 그림을 그대로 못 쓰는가 ──────────────────────────────────────────
레이어 텍스처는 갑옷 '그림'이 아니라 플레이어 모델에 감기는 UV 전개도다.
정해진 칸마다 어느 면이 오는지가 고정되어 있어서, 갑옷처럼 생긴 그림을
통째로 넣으면 몸에 엉뚱하게 발린다. 그래서 재질만 그림으로 받고
칸 배치는 여기서 계산한다.

── 어느 레이어가 어느 부위를 그리는가 ─────────────────────────────────
HumanoidArmorLayer.setPartVisibility 를 그대로 옮긴 것이다.

    투구  head + hat       layer_1
    흉갑  body + 양팔      layer_1
    각반  body + 양다리    layer_2
    장화  양다리           layer_1

장화와 흉갑이 같은 layer_1 을 쓰기 때문에, 다리 칸을 위까지 꽉 채우면
장화를 신었는데 정강이받이처럼 보인다. 그래서 다리 칸은 아래쪽만 채운다.
반대로 각반(layer_2)은 다리를 끝까지 채우고 몸통은 허리만 채운다.

예전 버전은 layer_1 에 다리 칸이 아예 없어서 장화를 신어도 아무것도
보이지 않았다.
"""

import os
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError as exc:
    sys.exit("필요한 패키지가 없습니다: %s\n  pip install pillow numpy" % exc.name)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATERIAL = os.path.join(ROOT, "art", "plate-material.png")
OUT = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "models", "armor")

# 바닐라 레이어는 64x32. 아이템 아이콘이 32x32(바닐라의 2배)라 여기도 2배로 맞춘다.
# tools/import_art.py 의 SIZE 를 바꾸면 여기도 같이 맞춰야 한다.
SCALE = 2
WIDTH, HEIGHT = 64 * SCALE, 32 * SCALE


def faces(u, v, w, h, d):
    """
    상자 하나의 UV 전개도. 마인크래프트가 정한 배치이고 바꿀 수 없다.
    돌려주는 값은 (이름, x, y, 너비, 높이).
    """
    return [
        ("top",    u + d,         v,     w, d),
        ("bottom", u + d + w,     v,     w, d),
        ("right",  u,             v + d, d, h),
        ("front",  u + d,         v + d, w, h),
        ("left",   u + d + w,     v + d, d, h),
        ("back",   u + d + w + d, v + d, w, h),
    ]


# HumanoidModel.createMesh 의 texOffs / addBox 값 그대로.
PARTS = {
    "head": faces(0, 0, 8, 8, 8),
    "hat":  faces(32, 0, 8, 8, 8),
    "body": faces(16, 16, 8, 12, 4),
    "arm":  faces(40, 16, 4, 12, 4),
    "leg":  faces(0, 16, 4, 12, 4),
}

# 세트별 색. 강철을 이 색조로 물들인다.
SETS = {
    "squire": {"tint": None},                       # 강철 그대로
    "knight": {"tint": (0.58, 0.86, 1.00)},         # 다이아 등급이라 청색
}


def load_material():
    img = Image.open(MATERIAL).convert("RGB")
    # 재질이 너무 크면 한 칸에 무늬가 하나도 안 들어간다. 칸 크기에 맞게 줄인다.
    side = 32 * SCALE
    return np.array(img.resize((side, side), Image.LANCZOS)).astype(np.float32)


SIDE_FACES = ("right", "front", "left", "back")


def fill(canvas, mat, x, y, w, h, src_x, src_y, top_cut=0):
    """
    칸 하나를 재질로 채운다.

    top_cut 은 위에서 몇 픽셀을 비울지다. 장화처럼 부위의 아래쪽만
    덮어야 할 때 쓴다. 좌표는 전부 배율이 곱해진 값이다.
    """
    mh, mw = mat.shape[:2]
    for j in range(top_cut, h):
        for i in range(w):
            px = mat[(src_y + j) % mh, (src_x + i) % mw]
            # 칸 가장자리를 살짝 어둡게 해 판과 판의 경계가 보이게 한다.
            # 너무 세게 주면 벽돌처럼 보이므로 한 픽셀만 은은하게.
            edge = min(i, j - top_cut, w - 1 - i, h - 1 - j)
            shade = 0.78 if edge == 0 else 1.0
            canvas[y + j, x + i, :3] = np.clip(px * shade, 0, 255)
            canvas[y + j, x + i, 3] = 255


def build(parts_spec, mat):
    canvas = np.zeros((HEIGHT, WIDTH, 4), dtype=np.float32)
    for part, top_cut_ratio in parts_spec.items():
        for name, x, y, w, h in PARTS[part]:
            X, Y, W, H = x * SCALE, y * SCALE, w * SCALE, h * SCALE

            # 위쪽을 비우는 건 옆면들만. 윗면/아랫면은 얇아서 그대로 둔다.
            cut = int(H * top_cut_ratio) if (top_cut_ratio and name in SIDE_FACES) else 0

            if name in SIDE_FACES:
                # 옆면 네 개는 세로 위치를 똑같이 맞춘다.
                # 그래야 재질의 금색 띠가 네 면에서 같은 높이에 놓여
                # 몸을 한 바퀴 두르는 띠처럼 이어져 보인다.
                # 면마다 다른 높이에서 떠오면 줄무늬가 어긋나 지저분해진다.
                src_y = 0
                # 가로만 면마다 어긋나게 해 같은 무늬가 반복되는 티를 줄인다.
                src_x = SIDE_FACES.index(name) * W
            else:
                src_x = len(part) * 3 * SCALE
                src_y = len(part) * 5 * SCALE

            fill(canvas, mat, X, Y, W, H, src_x, src_y, cut)
            carve(canvas, part, name, X, Y, W, H)
    return canvas


# 재질만 발라두면 투구가 그냥 금속 상자로 보인다.
# 얼굴 쪽에 바이저 틈과 통기구를 파서 투구로 읽히게 한다.
# 좌표는 각 면 안에서의 상대 위치이고 바닐라 64x32 기준이다.
VISOR_DARK = (18, 20, 24)

FACE_DETAILS = {
    # (부위, 면): [(면 안 x, y, 너비, 높이), ...]
    ("head", "front"): [
        (1, 3, 6, 1),          # 눈 틈
        (2, 5, 1, 1), (4, 5, 1, 1), (6, 5, 1, 1),   # 숨구멍
    ],
    ("hat", "front"): [
        (1, 3, 6, 1),
    ],
}


def carve(canvas, part, face_name, x, y, w, h):
    """면 위에 어두운 홈을 판다. 바이저 틈처럼 재질을 덮어써야 하는 부분."""
    for dx, dy, dw, dh in FACE_DETAILS.get((part, face_name), []):
        for j in range(dh * SCALE):
            for i in range(dw * SCALE):
                px, py = x + (dx * SCALE) + i, y + (dy * SCALE) + j
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    canvas[py, px, :3] = VISOR_DARK
                    canvas[py, px, 3] = 255


def tint(canvas, factors):
    if factors is None:
        return canvas
    out = canvas.copy()
    opaque = out[:, :, 3] > 0
    for c, f in enumerate(factors):
        out[:, :, c][opaque] = np.clip(out[:, :, c][opaque] * f, 0, 255)
    return out


def main():
    if not os.path.exists(MATERIAL):
        print("재질 그림이 없습니다:", os.path.relpath(MATERIAL, ROOT))
        return 2

    mat = load_material()
    os.makedirs(OUT, exist_ok=True)

    # layer_1: 투구(head+hat) + 흉갑(body+arm) + 장화(leg 아래쪽만)
    # layer_2: 각반(leg 전체 + body 허리만)
    layers = {
        1: {"head": 0, "hat": 0, "body": 0, "arm": 0, "leg": 0.62},
        2: {"body": 0.60, "leg": 0},
    }

    for set_name, cfg in SETS.items():
        for layer_no, spec in layers.items():
            canvas = tint(build(spec, mat), cfg["tint"])
            path = os.path.join(OUT, "%s_layer_%d.png" % (set_name, layer_no))
            Image.fromarray(canvas.astype(np.uint8), "RGBA").save(path)
            solid = int((canvas[:, :, 3] > 0).sum())
            print("  %-22s %dx%d  채운 픽셀 %5d" % (os.path.basename(path), WIDTH, HEIGHT, solid))

    print("\n갑옷 레이어 4장 생성 완료.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
