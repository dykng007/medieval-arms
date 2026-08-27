#!/usr/bin/env python3
"""
무기 아이콘의 날이 제대로 붙었는지 검사한다.

실행:  python tools/check_weapon_art.py
       (먼저 tools/import_art.py 로 아이콘을 만들어 둬야 한다)

필요:  pip install pillow numpy scipy

── 왜 필요한가 ──────────────────────────────────────────────────────────
그림 생성기는 같은 요청에도 매번 다르게 그린다. 날이 자루 반대쪽에 붙거나,
자루 한가운데로 내려오거나, 아래로 처지거나, 낫처럼 가늘고 길어지는 일이
실제로 여러 번 있었다. 눈으로만 보면 놓치기 쉬워서 수치로 잡는다.

검사하는 것 세 가지.

  방향   날이 자루의 어느 쪽에 붙었는가. 게임에서 몸쪽을 향하면 휘둘러도
         날이 닿지 않는 것처럼 보인다.
  위치   날 위로 맨 자루가 얼마나 튀어나왔는가. 길면 날이 자루 중간에
         달린 것처럼 보인다.
  기울기 날이 자루에 직각으로 뻗었는가. 아래로 기울면 늘어져 보인다.
         날이 뻗은 길이에 대한 비율로 재서, 날 크기가 달라도 같은 기준이 되게 한다.
  형태   자루를 따라가는 길이와 자루에서 멀어지는 길이의 비.
         한쪽으로 납작하면 도끼가 아니라 낫처럼 보인다.

위치를 재는 기준을 두 번 바꿨다. 처음에는 "날 끝 한 점이 소켓보다 위인가"로 쟀는데,
머리 절반이 늘어졌는데도 끝점만 위라서 정상으로 나왔고, 반대로 머리를 자루 방향으로
길게 키웠더니 끝점이 내려가 처짐으로 오인했다. 다음에는 날 중심 위치로 쟀는데,
이것도 날이 자루 방향으로 길어질수록 중심이 내려가 같은 오판을 했다.

지금은 날 위로 맨 자루가 얼마나 튀어나왔는지만 본다. 날이 아무리 커져도 이 값은
변하지 않고, 날이 자루 중간에 달렸을 때만 커진다.

날을 찾을 때는 가장 큰 강철 덩어리만 쓴다. 자루 끝의 금속 캡 같은 점이
섞이면 측정이 통째로 어긋난다. 실제로 한 픽셀 때문에 기울기가 -1 대신
+23 으로 나온 적이 있다.
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
ITEMS = os.path.join(ROOT, "src", "main", "resources", "assets", "medievalarms", "textures", "item")

# 날이 한쪽으로 치우친 무기만 검사한다.
# 창이나 철퇴처럼 날이 자루와 나란하거나 좌우 대칭인 것은 방향을 따질 수 없다.
ASYMMETRIC = ["halberd", "battleaxe"]



def classify(arr):
    """픽셀을 강철과 나무로 나눈다."""
    rgb = arr[:, :, :3].astype(int)
    alpha = arr[:, :, 3]
    visible = alpha > 128
    steel = visible & (abs(rgb[:, :, 0] - rgb[:, :, 2]) < 30) & (rgb[:, :, 0] > 110)
    wood = visible & ((rgb[:, :, 0] - rgb[:, :, 2]) > 25) & (rgb[:, :, 0] < 200) & (rgb[:, :, 1] < 160)
    return steel, wood


def measure(path):
    arr = np.array(Image.open(path).convert("RGBA"))
    steel, wood = classify(arr)
    if not steel.any() or not wood.any():
        return None

    # 가장 큰 강철 덩어리만 날로 본다. 자루 끝 금속 캡 같은 점이 섞이면
    # 측정이 통째로 어긋난다. 실제로 한 픽셀 때문에 결과가 뒤집힌 적이 있다.
    #
    # 덩어리를 세기 전에 한 칸 부풀린다. 날 안쪽에 그어진 검은 윤곽선이 날을
    # 두 조각으로 갈라놓는 일이 있는데, 그러면 한 조각만 날로 잡혀 크기가
    # 실제의 절반으로 측정된다. 부풀려서 세면 갈라진 조각이 다시 붙는다.
    joined = ndimage.binary_dilation(steel, structure=np.ones((3, 3), dtype=bool))
    labels, count = ndimage.label(joined, structure=np.ones((3, 3), dtype=int))
    sizes = ndimage.sum(steel, labels, range(1, count + 1))
    blade = (labels == (int(np.argmax(sizes)) + 1)) & steel

    # 자루는 왼쪽 아래에서 오른쪽 위로 가는 대각선이다.
    #   along  자루를 따라가는 방향 (오른쪽 위가 양수)
    #   away   자루에서 멀어지는 방향 (왼쪽 위가 양수)
    along_dir = np.array([1.0, -1.0]) / np.sqrt(2.0)
    away_dir = np.array([-1.0, -1.0]) / np.sqrt(2.0)

    def project(mask):
        ys, xs = np.where(mask)
        pts = np.stack([xs.astype(float), ys.astype(float)], axis=1)
        return pts @ along_dir, pts @ away_dir

    haft_along, haft_away = project(wood)
    blade_along, blade_away = project(blade)

    # 날 위로 맨 자루가 얼마나 튀어나와 있는지. 이게 크면 날이 자루 중간에
    # 달린 것처럼 보인다. 날 중심 위치로 재면 날이 자루 방향으로 길어질수록
    # 중심이 내려가 오판하므로, 날의 위쪽 끝과 자루 끝 사이만 본다.
    lo, hi = haft_along.min(), haft_along.max()
    overhang = float(hi - blade_along.max())

    # 처짐. 자루에서 가장 먼 날 끝이 소켓보다 자루 아래쪽에 있으면 늘어져 보인다.
    # 날이 자루에 직각으로 뻗으면 두 값이 비슷해진다.
    tip_along = float(blade_along[blade_away.argmax()])
    droop = float(haft_along.max() - tip_along)

    span_along = float(blade_along.max() - blade_along.min())
    span_away = float(blade_away.max() - blade_away.min())

    return {
        "overhang": overhang,
        "droop": droop,
        "span_along": span_along,
        "span_away": span_away,
        "ratio": span_away / max(span_along, 1e-6),
        "side": "left" if blade_away.mean() > haft_away.mean() else "right",
        "pixels": int(blade.sum()),
    }


MAX_OVERHANG = 4.0  # 날 위로 맨 자루가 이보다 길게 튀어나오면 중간에 달린 것으로 본다
# 처짐은 날이 클수록 절대값이 자연스럽게 커진다. 그래서 칸 수가 아니라
# 날이 뻗은 길이에 대한 비율로 본다. 이 값이 곧 날이 기운 각도에 해당한다.
# 0.35 는 약 19도. 그보다 기울면 눈에 띄게 늘어져 보인다.
MAX_DROOP_RATIO = 0.35
MAX_RATIO = 2.2     # 자루에서 멀어지는 쪽이 이보다 길면 낫처럼 납작하다
MIN_RATIO = 0.45    # 반대로 너무 작으면 날이 아니라 자루를 감싼 고리로 보인다


def main():
    problems = []
    print("%-11s %8s %8s %7s %8s %8s %6s %s"
          % ("무기", "날 픽셀", "자루돌출", "기울기", "자루방향", "바깥방향", "붙은쪽", "판정"))

    for name in ASYMMETRIC:
        path = os.path.join(ITEMS, name + ".png")
        if not os.path.exists(path):
            print("  %s 아이콘이 없습니다. 먼저 import_art.py 를 돌리세요." % name)
            return 2

        m = measure(path)
        if m is None:
            problems.append("%s: 강철이나 나무를 찾지 못했습니다" % name)
            continue

        notes = []
        if m["overhang"] > MAX_OVERHANG:
            notes.append("자루 중간")
            problems.append("%s: 날 위로 맨 자루가 %.1f칸 튀어나와 날이 중간에 달려 보입니다"
                            % (name, m["overhang"]))
        droop_ratio = m["droop"] / max(m["span_away"], 1e-6)
        if droop_ratio > MAX_DROOP_RATIO:
            notes.append("날이 처짐")
            problems.append("%s: 날이 뻗은 길이의 %.0f%% 만큼 아래로 기울어 늘어져 보입니다"
                            % (name, droop_ratio * 100))
        if m["ratio"] > MAX_RATIO:
            notes.append("낫 모양")
            problems.append("%s: 자루 방향 길이에 비해 바깥으로 %.1f배 길어 납작합니다"
                            % (name, m["ratio"]))
        if m["ratio"] < MIN_RATIO:
            notes.append("날이 얕음")
            problems.append("%s: 자루에서 멀어지는 길이가 짧아 날처럼 보이지 않습니다" % name)
        if m["side"] != "left":
            notes.append("반대쪽")
            problems.append("%s: 날이 자루 오른쪽에 붙어 게임에서 몸쪽을 향합니다" % name)

        print("%-11s %8d %8.1f %7.0f%% %8.1f %8.1f %6s  %s"
              % (name, m["pixels"], m["overhang"], droop_ratio * 100,
                 m["span_along"], m["span_away"],
                 m["side"], ", ".join(notes) if notes else "정상"))

    print()
    if problems:
        print("문제가 있습니다:")
        for p in problems:
            print("  -", p)
        print()
        print("art/weapon-<이름>.png 를 다시 뽑아 고치세요. 요청할 때 넣을 조건:")
        print("  - 자루는 왼쪽 아래에서 오른쪽 위로 가는 대각선")
        print("  - 날은 자루의 위쪽 끝에 붙이고, 자루 왼쪽으로 뻗을 것")
        print("  - 소켓이 자루를 길게 감싸 날이 자루 방향으로도 두툼할 것")
        print("  - 날은 자루에 직각으로 뻗을 것. 대각선 자루에 놓인 T자를 떠올릴 것")
        return 1

    print("모든 무기 아이콘이 정상입니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
