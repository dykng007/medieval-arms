#!/usr/bin/env python3
"""
GPT로 만든 고해상도 그림을 아이템 텍스처로 변환한다.

실행:  python tools/import_art.py
입력:  art/weapons-source.png   무기 6종이 한 줄로 늘어선 그림
       art/armor-source.png     갑옷 4부위가 한 줄로 늘어선 그림
       art/weapon-<이름>.png           (선택) 그 무기 하나만 따로 그린 그림
       art/weapon-<이름>-upright.png   (선택) 자루를 수직으로 그린 그림

무기 하나만 다시 그리고 싶을 때 여섯 개를 통째로 다시 뽑을 필요는 없다.
art/weapon-halberd.png 처럼 두면 시트 대신 그 파일을 쓴다.

── -upright 가 필요한 이유 ─────────────────────────────────────────────
마인크래프트 도구는 자루를 대각선으로 그리는데, 그림 생성기에 대각선 자루를
요구하면 도끼 머리를 자루에 직각으로 붙이지 못한다. 머리를 수직 자루 기준으로
그려놓고 대각선 자루에 얹어버려서, 머리만 45도 어긋나 아래로 처져 보인다.
프롬프트로 각도를 못 박아도 잘 고쳐지지 않았다.

그래서 자루를 수직으로 그리게 하고 여기서 45도 돌린다. 수직 자루에 직각으로
붙은 머리는 회전해도 직각을 유지하므로 처질 수가 없다.
출력:  src/main/resources/assets/medievalarms/textures/item/*.png

필요:  pip install pillow numpy scipy

── 줄이는 방식에 대해 ──────────────────────────────────────────────────
그림 생성기는 정해진 크기의 픽셀아트를 만들어주지 못한다. 픽셀아트처럼 보이는
큰 그림을 줄 뿐이라 직접 줄여야 하는데, 방식에 따라 결과가 크게 달랐다.

  LANCZOS / BOX : 주변 색을 평균 낸다. 원본의 굵은 검은 윤곽이 회색으로 녹아
                  줄인 뒤 형체가 뭉갠 것처럼 보인다.
  팔레트 축소   : 색을 12색으로 줄여봤더니 median cut이 갈색과 금색에 치우쳐
                  강철 회색을 잃고 전부 베이지가 됐다.
  NEAREST       : 각 칸의 한 점을 그대로 집는다. 색이 섞이지 않아 윤곽과
                  금색 장식이 살아남는다. 셋 중 이게 확실히 낫다.

── 무기를 나누는 방식 ──────────────────────────────────────────────────
x좌표로 자르지 않는다. 무기가 대각선이라 서로 x범위가 겹쳐 완전히 빈 세로줄이
없기 때문이다. 대신 연결 요소로 덩어리를 찾는다.

다만 덩어리 하나가 곧 한 아이템은 아니다. 장화는 두 짝이 떨어져 있어 덩어리가
둘로 잡힌다. 그래서 가로 간격이 좁은 덩어리끼리는 한 아이템으로 묶는다.
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
ART = os.path.join(ROOT, "art")
OUT = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "item")

# 아이템 아이콘 한 변의 픽셀 수.
# 바닐라는 16이지만 마인크래프트는 더 큰 것도 받는다. NeoForge가 밉맵 제약까지
# 풀어놨기 때문에(SpriteLoader의 "Do not lower the mipmap level" 패치) 32도 문제없다.
# 16에서는 원본 그림의 세부가 너무 많이 날아가 32로 올렸다.
# 2의 거듭제곱이어야 하고, 바꾸면 갑옷 레이어 배율(gen_armor_layers.py 의 SCALE)도 같이 맞춰야 한다.
SIZE = 32

ALPHA_BACKGROUND = 16   # 이보다 흐리면 배경으로 본다
ALPHA_CUTOFF = 110      # 줄인 뒤 이보다 흐리면 완전 투명으로. 반투명 테두리는 게임에서 지저분하다
MIN_BLOB = 500          # 이보다 작은 덩어리는 부스러기


def find_items(arr, merge_gap):
    """
    연결 요소를 찾아 아이템 단위로 묶어 왼쪽부터 돌려준다.

    merge_gap 은 가로로 이만큼 이내에 붙어 있는 덩어리를 한 아이템으로 볼지 정한다.
    갑옷 장화는 두 짝이 떨어져 있어 묶어야 하므로 양수를 준다.
    무기는 대각선이라 이웃끼리 x범위가 서로 겹친다. 여기에 양수를 주면
    여섯 자루가 통째로 하나가 되어버리므로 None 을 줘서 묶지 않는다.
    """
    mask = arr[:, :, 3] > ALPHA_BACKGROUND
    labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=int))
    sizes = ndimage.sum(mask, labels, range(1, count + 1))
    boxes = ndimage.find_objects(labels)

    blobs = []
    for i in range(count):
        if sizes[i] >= MIN_BLOB:
            box = boxes[i]
            blobs.append({"x0": box[1].start, "x1": box[1].stop,
                          "y0": box[0].start, "y1": box[0].stop, "ids": [i + 1]})
    blobs.sort(key=lambda b: b["x0"])

    if merge_gap is None:
        return blobs, labels

    merged = []
    for b in blobs:
        if merged and b["x0"] - merged[-1]["x1"] <= merge_gap:
            prev = merged[-1]
            prev["x1"] = max(prev["x1"], b["x1"])
            prev["y0"] = min(prev["y0"], b["y0"])
            prev["y1"] = max(prev["y1"], b["y1"])
            prev["ids"] += b["ids"]
        else:
            merged.append(dict(b))
    return merged, labels


def to_sprite(arr, labels, item):
    """아이템 하나를 잘라 정사각으로 맞춘 뒤 SIZE x SIZE 로 줄인다."""
    box = (slice(item["y0"], item["y1"]), slice(item["x0"], item["x1"]))
    piece = arr[box].copy()
    # 이 사각형 안에 이웃 아이템이 걸쳐 있을 수 있으므로 내 덩어리만 남긴다.
    keep = np.isin(labels[box], item["ids"])
    piece[~keep] = (0, 0, 0, 0)

    height, width = piece.shape[:2]
    side = max(width, height)
    square = np.zeros((side, side, 4), dtype=np.uint8)
    top, left = (side - height) // 2, (side - width) // 2
    square[top:top + height, left:left + width] = piece

    small = np.array(Image.fromarray(square, "RGBA").resize((SIZE, SIZE), Image.NEAREST))
    small[:, :, 3] = np.where(small[:, :, 3] >= ALPHA_CUTOFF, 255, 0)
    small[small[:, :, 3] == 0] = (0, 0, 0, 0)
    return small


def tint_steel_to_blue(rgba):
    """
    강철 회색을 청색으로 바꾼다. 금색 장식과 검은 윤곽은 그대로 둔다.

    기사 세트는 다이아 등급이라 종자 세트와 색으로 구분되어야 하는데,
    그림을 한 장 더 뽑는 대신 같은 그림을 물들여 쓴다. 그래야 두 세트의
    형태가 정확히 같아 한 벌처럼 보인다.
    """
    out = rgba.copy()
    rgb = out[:, :, :3].astype(np.int16)
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    sat = mx - mn
    opaque = out[:, :, 3] > 0
    # 채도가 낮으면 강철, 높으면 금색으로 본다. 아주 어두우면 윤곽이라 건드리지 않는다.
    steel = opaque & (sat < 45) & (mx >= 40)
    lum = mx[steel].astype(np.float32) / 255.0
    out[:, :, 0][steel] = np.clip(lum * 150, 0, 255).astype(np.uint8)
    out[:, :, 1][steel] = np.clip(60 + lum * 165, 0, 255).astype(np.uint8)
    out[:, :, 2][steel] = np.clip(90 + lum * 165, 0, 255).astype(np.uint8)
    return out


SHEETS = [
    {"file": "weapons-source.png",
     "names": ["spear", "halberd", "mace", "battleaxe", "warhammer", "longsword"],
     "merge_gap": None,
     "variants": [("", None)]},
    {"file": "armor-source.png",
     "names": ["helmet", "chestplate", "leggings", "boots"],
     "merge_gap": 40,
     # 같은 그림으로 두 세트를 만든다. 종자는 강철 그대로, 기사는 청색으로 물들인다.
     "variants": [("squire_", None), ("knight_", tint_steel_to_blue)]},
]


UPRIGHT_ROTATION = -45      # 수직 자루를 오른쪽 위 대각선으로 눕히는 각도


def rotate_upright(img):
    """
    수직으로 그린 무기를 마인크래프트의 대각선 자세로 돌린다.

    시계 방향 45도. 위를 향하던 자루가 오른쪽 위를 향하게 되고,
    자루에 직각으로 붙어 있던 머리도 같이 돌아 직각을 유지한다.
    원본이 큰 그림이라 회전 계단이 생겨도 16이나 32로 줄이면 묻힌다.
    """
    return img.rotate(UPRIGHT_ROTATION, resample=Image.BICUBIC, expand=True)


def load_override(name):
    """
    무기 하나만 따로 그린 그림이 있으면 그것을 읽어 SIZE x SIZE 로 만든다.

    없으면 None 을 돌려줘 시트에서 잘라낸 것을 쓰게 한다.
    무기 하나를 고치려고 여섯 개를 다시 뽑는 건 낭비라 이 길을 열어뒀다.
    """
    upright = os.path.join(ART, "weapon-%s-upright.png" % name)
    plain = os.path.join(ART, "weapon-%s.png" % name)

    if os.path.exists(upright):
        path, needs_rotation = upright, True
    elif os.path.exists(plain):
        path, needs_rotation = plain, False
    else:
        return None

    img = Image.open(path).convert("RGBA")
    if needs_rotation:
        img = rotate_upright(img)
    arr = np.array(img)
    mask = arr[:, :, 3] > ALPHA_BACKGROUND
    if not mask.any():
        print("  %-20s 그림이 비어 있어 건너뜁니다: %s" % (name, os.path.relpath(path, ROOT)))
        return None

    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    piece = arr[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]

    height, width = piece.shape[:2]
    side = max(width, height)
    square = np.zeros((side, side, 4), dtype=np.uint8)
    top, left = (side - height) // 2, (side - width) // 2
    square[top:top + height, left:left + width] = piece

    small = np.array(Image.fromarray(square, "RGBA").resize((SIZE, SIZE), Image.NEAREST))
    small[:, :, 3] = np.where(small[:, :, 3] >= ALPHA_CUTOFF, 255, 0)
    small[small[:, :, 3] == 0] = (0, 0, 0, 0)
    return small


def main():
    os.makedirs(OUT, exist_ok=True)
    failed = False

    for sheet in SHEETS:
        path = os.path.join(ART, sheet["file"])
        if not os.path.exists(path):
            print("원본 그림이 없습니다:", os.path.relpath(path, ROOT))
            failed = True
            continue

        arr = np.array(Image.open(path).convert("RGBA"))
        items, labels = find_items(arr, sheet["merge_gap"])
        names = sheet["names"]
        print("%s -> 덩어리 %d개 / 기대 %d개" % (sheet["file"], len(items), len(names)))
        if len(items) != len(names):
            print("  개수가 맞지 않습니다. 그림에서 아이템끼리 붙어 있거나 너무 떨어져 있습니다.")
            print("  merge_gap(%s)을 조정하거나 그림을 다시 뽑으세요." % sheet["merge_gap"])
            failed = True
            continue

        for name, item in zip(names, items):
            override = load_override(name)
            base = override if override is not None else to_sprite(arr, labels, item)
            if override is not None:
                print("  %-20s (따로 그린 그림 사용)" % name)
            for prefix, recolor in sheet["variants"]:
                pixels = base if recolor is None else recolor(base)
                out_name = prefix + name
                Image.fromarray(pixels, "RGBA").save(os.path.join(OUT, out_name + ".png"))
                solid = int((pixels[:, :, 3] > 0).sum())
                print("  %-20s 불투명 %4d/%d" % (out_name, solid, SIZE * SIZE))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
