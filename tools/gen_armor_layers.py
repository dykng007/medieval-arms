#!/usr/bin/env python3
"""
갑옷을 입었을 때 몸에 씌워지는 레이어 텍스처를 만든다.

실행:  python tools/gen_armor_layers.py
입력:  art/armor-panels.png   부위별 갑옷 판이 한 줄로 늘어선 그림
출력:  .../textures/models/armor/<세트>_layer_{1,2}.png

필요:  pip install pillow numpy scipy

── 왜 갑옷 그림이 아니라 '판'을 받는가 ────────────────────────────────
레이어 텍스처는 갑옷 그림이 아니라 플레이어 모델에 감기는 UV 전개도다.
칸마다 어느 면이 오는지 고정되어 있어서, 갑옷처럼 생긴 그림을 통째로 넣으면
몸에 엉뚱하게 발린다. 그래서 면에 그대로 들어갈 직사각형 판을 받아 배치한다.

── 둥글게 보이는 이유 ─────────────────────────────────────────────────
플레이어 모델은 상자라 기하학적으로 둥글게 만들 수 없다. 둥글어 보이려면
면의 가운데가 밝고 좌우 가장자리가 그늘져야 한다.

앞서는 그 음영을 코드로 곱해봤는데, 판금 무늬와 아이콘 대비에 묻혀 효과가
거의 없었다. 그래서 음영을 계산하지 않고 판 그림 자체에 그려진 것을 쓴다.
art/armor-panels.png 의 여섯 판은 전부 원통에 빛이 닿은 것처럼 칠해져 있다.

── 앞판과 뒤판의 띠 높이를 맞추는 이유 ───────────────────────────────
한 부위의 네 옆면은 몸을 한 바퀴 두른다. 앞판의 금색 띠가 세로 89% 지점에
있는데 뒤판의 띠가 96% 지점에 있으면, 캐릭터를 돌려볼 때 모서리에서 띠가
툭 끊겨 보인다. 실제로 그래서 "모서리가 따로 논다"는 문제가 있었다.

판은 각각 그려지므로 띠 높이가 저절로 맞지 않는다. make_back() 이 앞판을 바탕으로
삼고 가운데 장식 구간만 뒤판의 민판으로 갈아끼운다. 띠는 앞판 것이 그대로 남으니
높이가 어긋날 수가 없다. 팔과 다리는 앞뒤가 같은 판이라 애초에 문제가 없다.

판을 다시 뽑을 때는 반드시 이렇게 요청해야 한다.
  - 여섯 판을 한 줄로, 사이를 넉넉히 띄우고, 배경은 투명하게
  - 각 판은 구멍 없이 꽉 찬 직사각형
  - 가운데는 밝게, 좌우 끝은 짙은 그늘로 (원통처럼)

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
    from scipy import ndimage
except ImportError as exc:
    sys.exit("필요한 패키지가 없습니다: %s\n  pip install pillow numpy scipy" % exc.name)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS = os.path.join(ROOT, "art", "armor-panels.png")
OUT = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "models", "armor")

# 바닐라 레이어는 64x32. 아이템 아이콘이 32x32(바닐라의 2배)라 여기도 2배로 맞춘다.
# tools/import_art.py 의 SIZE 를 바꾸면 여기도 같이 맞춰야 한다.
SCALE = 2
WIDTH, HEIGHT = 64 * SCALE, 32 * SCALE

# 그림에서 왼쪽부터 놓인 순서. 판을 다시 뽑으면 순서를 맞추거나 여기를 고친다.
PANEL_NAMES = ["helm_front", "helm_back", "chest_front", "chest_back", "arm", "leg"]

# 판의 위아래 끝은 원통의 뚜껑처럼 타원으로 그려져 있다. 그대로 쓰면 면 위아래에
# 둥근 띠가 생겨 이상하므로, 세로로 이 비율만큼 잘라내고 가운데만 쓴다.
TRIM_TOP, TRIM_BOTTOM = 0.04, 0.04


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

SETS = {
    "squire": None,                 # 강철 그대로
    "knight": (0.58, 0.86, 1.00),   # 다이아 등급이라 청색
}


def load_panels():
    """판 그림을 덩어리별로 잘라 이름표를 붙여 돌려준다."""
    if not os.path.exists(PANELS):
        return None
    arr = np.array(Image.open(PANELS).convert("RGBA"))
    mask = arr[:, :, 3] > 16
    labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=int))
    sizes = ndimage.sum(mask, labels, range(1, count + 1))
    boxes = ndimage.find_objects(labels)

    found = []
    for i in range(count):
        if sizes[i] >= 2000:
            found.append((boxes[i][1].start, boxes[i], i + 1))
    found.sort(key=lambda t: t[0])
    if len(found) != len(PANEL_NAMES):
        print("판을 %d개 찾았는데 %d개를 기대했습니다." % (len(found), len(PANEL_NAMES)))
        print("판끼리 붙어 있으면 하나로 뭉쳐 세어집니다. 사이를 띄워 다시 뽑으세요.")
        return None

    panels = {}
    for name, (_, box, label_id) in zip(PANEL_NAMES, found):
        piece = arr[box].copy()
        piece[labels[box] != label_id] = (0, 0, 0, 0)
        h = piece.shape[0]
        # 원통 뚜껑처럼 그려진 위아래 끝을 잘라낸다.
        piece = piece[int(h * TRIM_TOP):h - int(h * TRIM_BOTTOM)]
        panels[name] = Image.fromarray(piece, "RGBA")

    # 뒷면은 앞판을 바탕으로 가운데만 갈아끼워 만든다. 띠 높이가 어긋나지 않게 하려는 것.
    for part in ("helm", "chest"):
        panels[part + "_back"] = make_back(panels[part + "_front"],
                                           panels[part + "_back"],
                                           BACK_KEEP[part])
    return panels


def detect_bands(panel):
    """판에서 금색 띠가 세로 몇 지점(0~1)에 있는지 찾는다."""
    arr = np.array(panel)
    rgb = arr[:, :, :3].astype(np.int16)
    gold = ((rgb[:, :, 0] - rgb[:, :, 2]) > 40) & (rgb[:, :, 0] > 110) & (arr[:, :, 3] > 128)
    frac = gold.mean(axis=1)
    h = len(frac)

    bands, start = [], None
    for i in range(h):
        hit = frac[i] > 0.35
        if hit and start is None:
            start = i
        elif not hit and start is not None:
            if i - start >= 2:
                bands.append((start + i) / 2.0 / h)
            start = None
    if start is not None and h - start >= 2:
        bands.append((start + h) / 2.0 / h)
    return bands


# 뒷면을 만들 때 앞판에서 그대로 가져올 세로 구간의 바깥쪽 경계.
# 이 범위 '밖'(위아래 끝)은 앞판을 쓰고, 안쪽 가운데만 뒤판으로 갈아끼운다.
# 그래서 목깃과 허리띠 같은 띠는 앞뒤가 정확히 같은 높이에 온다.
BACK_KEEP = {
    "helm": (0.16, 0.78),    # 위 테두리와 목 띠는 앞판 것을 쓰고, 바이저만 지운다
    "chest": (0.22, 0.90),   # 목깃과 허리띠는 앞판 것을 쓰고, 가슴 장식만 지운다
}


def make_back(front, back, keep):
    """
    뒷면 판을 만든다.

    뒤판을 그대로 쓰면 띠 높이가 앞판과 달라 몸을 돌릴 때 모서리에서 끊긴다.
    판을 늘려 맞추는 것도 해봤는데, 가장자리에 붙은 띠가 뭉개져 완전히는 맞지 않았다.

    그래서 앞판을 바탕으로 삼고 가운데 장식 구간만 뒤판의 민판으로 갈아끼운다.
    띠는 앞판 것이 그대로 남으므로 높이가 어긋날 수가 없다.
    """
    w, h = front.size
    out = front.copy()
    y0, y1 = int(h * keep[0]), int(h * keep[1])
    if y1 <= y0:
        return out
    plain = back.resize((w, h), Image.NEAREST).crop((0, y0, w, y1))
    out.paste(plain, (0, y0))
    return out


def face_size(face, top_ratio=0.0):
    _, _, w, h = face
    W, H = w * SCALE, h * SCALE
    return W, H - int(H * top_ratio)


def write_face(canvas, panel, face, top_ratio=0.0, dim=1.0, flip=False, crop=None):
    """
    판을 면 크기에 맞춰 줄여 캔버스의 제자리에 써넣는다.

    crop 은 판에서 쓸 세로 구간 (시작 비율, 끝 비율).
    장화처럼 판의 아래쪽만 쓰고 싶을 때 지정한다.
    dim 은 밝기 배수. 옆면과 뒷면을 살짝 어둡게 해 정면이 도드라지게 한다.
    """
    x, y, w, h = face
    X, Y, W, H = x * SCALE, y * SCALE, w * SCALE, h * SCALE
    cut = int(H * top_ratio)
    fh = H - cut
    if fh <= 0:
        return

    src = panel
    if crop is not None:
        pw, ph = src.size
        src = src.crop((0, int(ph * crop[0]), pw, int(ph * crop[1])))
    if flip:
        src = src.transpose(Image.FLIP_LEFT_RIGHT)

    # 픽셀아트라 NEAREST 로 줄여야 가장자리가 뭉개지지 않는다.
    small = np.array(src.resize((W, fh), Image.NEAREST)).astype(np.float32)
    # 판은 꽉 찬 직사각형이지만, 혹시 남은 반투명 가장자리는 불투명으로 굳힌다.
    small[:, :, 3] = np.where(small[:, :, 3] >= 110, 255, 0)
    if dim != 1.0:
        small[:, :, :3] = np.clip(small[:, :, :3] * dim, 0, 255)
    canvas[Y + cut:Y + H, X:X + W] = small


def build_layer_1(p):
    canvas = np.zeros((HEIGHT, WIDTH, 4), dtype=np.float32)
    head, body, arm, leg = PARTS["head"], PARTS["body"], PARTS["arm"], PARTS["leg"]

    # ── 투구 ──
    write_face(canvas, p["helm_front"], head["front"])
    write_face(canvas, p["helm_back"], head["right"], dim=0.92)
    write_face(canvas, p["helm_back"], head["left"], dim=0.92, flip=True)
    write_face(canvas, p["helm_back"], head["back"], dim=0.86)
    # 정수리와 턱은 판의 위/아래 끝을 얇게 떠서 쓴다.
    write_face(canvas, p["helm_back"], head["top"], crop=(0.0, 0.18))
    write_face(canvas, p["helm_back"], head["bottom"], crop=(0.82, 1.0), dim=0.5)
    # hat 칸은 일부러 비운다. 채우면 투구가 두 겹으로 부푼다.

    # ── 흉갑 ──
    write_face(canvas, p["chest_front"], body["front"])
    write_face(canvas, p["chest_back"], body["right"], dim=0.9)
    write_face(canvas, p["chest_back"], body["left"], dim=0.9, flip=True)
    write_face(canvas, p["chest_back"], body["back"], dim=0.86)
    write_face(canvas, p["chest_back"], body["top"], crop=(0.0, 0.16))
    write_face(canvas, p["chest_back"], body["bottom"], crop=(0.84, 1.0), dim=0.5)

    # ── 팔 ──
    for name, flip, dim in (("front", False, 1.0), ("right", False, 0.92),
                            ("left", True, 0.92), ("back", True, 0.84)):
        write_face(canvas, p["arm"], arm[name], dim=dim, flip=flip)
    write_face(canvas, p["arm"], arm["top"], crop=(0.0, 0.2))
    write_face(canvas, p["arm"], arm["bottom"], crop=(0.8, 1.0), dim=0.5)

    # ── 장화 (다리 칸의 아래쪽만) ──
    # 위까지 채우면 정강이받이가 된다. 판의 아래쪽 구간만 떠서 쓴다.
    cut = 0.58
    for name, flip, dim in (("front", False, 1.0), ("right", False, 0.92),
                            ("left", True, 0.92), ("back", True, 0.84)):
        write_face(canvas, p["leg"], leg[name], top_ratio=cut, dim=dim, flip=flip,
                   crop=(0.62, 1.0))
    write_face(canvas, p["leg"], leg["bottom"], crop=(0.86, 1.0), dim=0.55)
    return canvas


def build_layer_2(p):
    canvas = np.zeros((HEIGHT, WIDTH, 4), dtype=np.float32)
    body, leg = PARTS["body"], PARTS["leg"]

    # ── 허리 (몸통 칸의 아래쪽만) ──
    cut = 0.58
    for name, flip, dim in (("front", False, 1.0), ("right", False, 0.9),
                            ("left", True, 0.9), ("back", True, 0.86)):
        write_face(canvas, p["chest_back"], body[name], top_ratio=cut, dim=dim, flip=flip,
                   crop=(0.7, 1.0))
    write_face(canvas, p["chest_back"], body["bottom"], crop=(0.84, 1.0), dim=0.5)

    # ── 각반 (다리 전체) ──
    write_face(canvas, p["leg"], leg["front"])
    write_face(canvas, p["leg"], leg["right"], dim=0.92)
    write_face(canvas, p["leg"], leg["left"], dim=0.92, flip=True)
    write_face(canvas, p["leg"], leg["back"], dim=0.86, flip=True)
    write_face(canvas, p["leg"], leg["top"], crop=(0.0, 0.16), dim=0.9)
    write_face(canvas, p["leg"], leg["bottom"], crop=(0.84, 1.0), dim=0.5)
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
    panels = load_panels()
    if panels is None:
        return 2

    os.makedirs(OUT, exist_ok=True)
    layers = {1: build_layer_1(panels), 2: build_layer_2(panels)}
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
