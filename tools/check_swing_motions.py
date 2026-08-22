#!/usr/bin/env python3
"""
휘두르기 모션이 서로 구분되는지 검사한다.

실행:  python tools/check_swing_motions.py

── 왜 필요한가 ──────────────────────────────────────────────────────────
처음 만든 모션은 여섯 무기가 게임에서 전부 똑같아 보였다. 바닐라 궤적 하나에
각도만 조금씩 다르게 얹은 구조라, 지배적인 움직임이 모든 무기에서 같았기 때문이다.
숫자를 보면 분명히 달랐지만 화면에서는 구분되지 않았다.

이 스크립트는 SwingMotion.java의 값을 그대로 읽어 궤적을 계산하고,
모션 쌍마다 최대 차이를 재서 "눈에 띌 만큼 다른지"를 판정한다.
값을 조정한 뒤에는 게임을 켜기 전에 여기부터 돌리는 편이 빠르다.

계산식은 MedievalWeaponClientExtensions.applySwing 과 같아야 한다.
한쪽을 고치면 다른 쪽도 같이 고쳐야 한다.

종료 코드: 모두 구분되면 0, 비슷한 쌍이 있으면 1.
"""

import io
import itertools
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "src", "main", "java", "com", "dykng", "medievalarms", "weapon", "SwingMotion.java")

# applySwing 의 정규화 상수와 같아야 한다.
PHASE_PEAK = 0.58

# 이 정도는 넘어야 화면에서 구분된다고 본다. 경험적으로 정한 값이다.
MIN_MOVE_BLOCKS = 0.15
MIN_ANGLE_DEGREES = 20.0

FIELDS = ["windupPitch", "strikePitch", "windupPull", "strikeReach", "strikeYaw", "speedScale"]


def load_motions():
    src = io.open(SOURCE, encoding="utf-8").read()
    motions = {}
    for m in re.finditer(r"^\s{4}([A-Z_]+)\(([^)]*)\),?;?\s*$", src, re.M):
        raw = m.group(2).split(",")
        if len(raw) != len(FIELDS):
            continue
        try:
            values = [float(v.strip().rstrip("Ff")) for v in raw]
        except ValueError:
            continue
        motions[m.group(1)] = dict(zip(FIELDS, values))
    return motions


def state(mo, progress):
    """진행도에서의 (앞뒤 이동, 위아래 각도, 좌우 각도)."""
    p = min(max(progress, 0.0), 1.0)
    if p <= 0.0:
        return (0.0, 0.0, 0.0)
    p = p ** (1.0 / mo["speedScale"])
    bell = math.sin(p * math.pi)
    windup = bell * (1.0 - p) / PHASE_PEAK
    strike = bell * p / PHASE_PEAK
    return (
        mo["windupPull"] * windup - mo["strikeReach"] * strike,
        mo["windupPitch"] * windup - mo["strikePitch"] * strike,
        mo["strikeYaw"] * (windup - strike),
    )


def main():
    motions = load_motions()
    if len(motions) < 2:
        print("SwingMotion.java 에서 모션을 읽지 못했습니다.")
        return 2

    failures = []

    # 1. 끝점 검사: 진행도 0과 1에서 0이어야 동작이 끊기지 않는다.
    for name, mo in motions.items():
        for progress in (0.0, 1.0):
            if any(abs(v) > 1e-6 for v in state(mo, progress)):
                failures.append("%s: 진행도 %.0f 에서 자세가 평상시로 돌아오지 않습니다" % (name, progress))

    # 2. 구분 검사
    print("모션 쌍별 최대 차이 (기준: 이동 %.2f블록 또는 각도 %.0f도)" % (MIN_MOVE_BLOCKS, MIN_ANGLE_DEGREES))
    samples = [i / 40.0 for i in range(41)]
    for a, b in itertools.combinations(sorted(motions), 2):
        dz = dp = dy = 0.0
        for s in samples:
            za, pa, ya = state(motions[a], s)
            zb, pb, yb = state(motions[b], s)
            dz = max(dz, abs(za - zb))
            dp = max(dp, abs(pa - pb))
            dy = max(dy, abs(ya - yb))
        distinct = dz > MIN_MOVE_BLOCKS or dp > MIN_ANGLE_DEGREES or dy > MIN_ANGLE_DEGREES
        print("  %-9s vs %-9s  이동 %.2f  위아래 %5.1f도  좌우 %5.1f도  %s"
              % (a, b, dz, dp, dy, "구분됨" if distinct else "너무 비슷함"))
        if not distinct:
            failures.append("%s 와 %s 가 화면에서 구분되지 않을 만큼 비슷합니다" % (a, b))

    print()
    if failures:
        print("문제가 있습니다:")
        for f in failures:
            print("  -", f)
        print()
        print("SwingMotion.java 에서 두 모션이 서로 다른 축으로 크게 움직이도록 값을 벌리세요.")
        print("같은 축에서 각도만 조금 다르게 하면 화면에서는 같아 보입니다.")
        return 1

    print("모든 모션이 서로 구분됩니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
