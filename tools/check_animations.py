#!/usr/bin/env python3
"""
휘두르기 애니메이션 JSON을 검사한다.

실행:  python tools/check_animations.py
       (먼저 tools/gen_animations.py 로 파일을 만들어 둬야 한다)

── 왜 필요한가 ──────────────────────────────────────────────────────────
이 형식은 틀려도 게임이 죽지 않는다. 조용히 아무 일도 일어나지 않을 뿐이다.
뼈대 이름을 rightarm 이라고 쓰면 (맞는 이름은 rightArm) 라이브러리는 그 항목을
그냥 건너뛴다. 오른팔이 안 움직이는 걸 게임을 켜서 눈으로 알아채야 한다.
게임 한 번 켜는 데 몇 분씩 걸리므로 그 전에 여기서 잡는다.

검사하는 것.

  이름     뼈대·채널·감속 이름이 실제로 존재하는 것인가.
           틀리면 그 부분만 조용히 무시된다.
  단위     각도가 라디안인가. 도 단위 값을 그대로 넣으면 (예: 90)
           라디안 90 = 5156도로 해석돼 몸이 미친 듯이 돈다.
  복귀     마지막 틱에서 모든 값이 0인가.
           하나라도 남으면 공격이 끝난 뒤 그 자세로 굳는다.
  시작     첫 틱에서 모든 값이 0인가. 아니면 공격 시작이 튄다.
  구분     모션끼리 눈에 띄게 다른가.
           예전에 여섯 무기가 게임에서 전부 똑같아 보인 적이 있다.
"""

import io
import itertools
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIM = os.path.join(ROOT, "src", "main", "resources", "assets",
                    "medievalarms", "player_animations")
MOTIONS = os.path.join(ROOT, "src", "main", "java", "com", "dykng",
                       "medievalarms", "weapon", "SwingMotion.java")

# 라이브러리가 아는 뼈대 이름. 이 목록에 없는 이름은 조용히 무시된다.
BONES = {"head", "body", "torso",
         "rightArm", "leftArm", "rightLeg", "leftLeg",
         "rightItem", "leftItem"}

ANGLE_CHANNELS = {"pitch", "yaw", "roll", "bend"}
CHANNELS = ANGLE_CHANNELS | {"x", "y", "z", "axis"}

EASINGS = {
    "LINEAR", "CONSTANT", "STEP", "CATMULLROM",
    "INSINE", "OUTSINE", "INOUTSINE", "INCUBIC", "OUTCUBIC", "INOUTCUBIC",
    "INQUAD", "OUTQUAD", "INOUTQUAD", "INQUART", "OUTQUART", "INOUTQUART",
    "INQUINT", "OUTQUINT", "INOUTQUINT", "INEXPO", "OUTEXPO", "INOUTEXPO",
    "INCIRC", "OUTCIRC", "INOUTCIRC", "INBACK", "OUTBACK", "INOUTBACK",
    "INELASTIC", "OUTELASTIC", "INOUTELASTIC",
    "INBOUNCE", "OUTBOUNCE", "INOUTBOUNCE",
}

# 라디안으로 이 값을 넘으면 도 단위 값을 잘못 넣은 것으로 본다.
# 4.0 라디안은 229도. 가장 큰 동작인 내리치기가 -200도(-3.5라디안)를 쓴다.
MAX_RADIANS = 4.0

# 이 정도는 넘어야 화면에서 구분된다고 본다.
MIN_DIFFERENCE_DEGREES = 25.0


def load(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def curves(emote):
    """{(뼈대, 채널): {틱: 값}} 로 정리한다."""
    out = {}
    for move in emote["moves"]:
        tick = move["tick"]
        for key, value in move.items():
            if isinstance(value, dict):
                for channel, number in value.items():
                    out.setdefault((key, channel), {})[tick] = number
    return out


def sample(points, tick):
    """키프레임 사이를 직선으로 이어 그 시점의 값을 구한다."""
    ticks = sorted(points)
    if tick <= ticks[0]:
        return points[ticks[0]]
    if tick >= ticks[-1]:
        return points[ticks[-1]]
    for a, b in zip(ticks, ticks[1:]):
        if a <= tick <= b:
            if b == a:
                return points[a]
            ratio = (tick - a) / (b - a)
            return points[a] + (points[b] - points[a]) * ratio
    return 0.0


def main():
    if not os.path.isdir(ANIM):
        print("애니메이션 폴더가 없습니다. 먼저 tools/gen_animations.py 를 돌리세요.")
        return 2

    problems = []
    loaded = {}

    print("%-10s %6s %6s %8s %s" % ("모션", "길이", "채널", "최대각도", "판정"))

    for filename in sorted(os.listdir(ANIM)):
        if not filename.endswith(".json"):
            continue
        name = filename[:-5]
        emote = load(os.path.join(ANIM, filename))["emote"]

        if str(emote.get("degrees", "false")).lower() != "false":
            problems.append("%s: degrees 가 true 입니다. 이 검사기는 라디안을 전제합니다" % name)

        tracks = curves(emote)
        loaded[name] = tracks
        notes = []
        biggest = 0.0

        for (bone, channel), points in sorted(tracks.items()):
            where = "%s.%s" % (bone, channel)

            if bone not in BONES:
                notes.append("뼈대 이름")
                problems.append("%s: 뼈대 이름 '%s' 는 없는 이름이라 조용히 무시됩니다" % (name, bone))
            if channel not in CHANNELS:
                notes.append("채널 이름")
                problems.append("%s: 채널 이름 '%s' 는 없는 이름이라 조용히 무시됩니다" % (name, channel))

            ticks = sorted(points)
            if channel in ANGLE_CHANNELS:
                peak = max(abs(v) for v in points.values())
                biggest = max(biggest, math.degrees(peak))
                if peak > MAX_RADIANS:
                    notes.append("단위")
                    problems.append("%s: %s 의 값 %.1f 은 라디안치고 너무 큽니다. "
                                    "도 단위를 그대로 넣지 않았는지 확인하세요" % (name, where, peak))

            if abs(points[ticks[0]]) > 1e-6:
                notes.append("시작 안 맞음")
                problems.append("%s: %s 가 첫 틱부터 0이 아니라 공격 시작이 튑니다" % (name, where))
            if abs(points[ticks[-1]]) > 1e-6:
                notes.append("복귀 안 함")
                problems.append("%s: %s 가 마지막 틱에서 0으로 돌아오지 않아 "
                                "그 자세로 굳습니다" % (name, where))

        print("%-10s %5d틱 %5d개 %7.0f도  %s"
              % (name, emote["endTick"], len(tracks), biggest,
                 ", ".join(sorted(set(notes))) if notes else "정상"))

    # SwingMotion 의 모든 상수에 파일이 있는지.
    source = io.open(MOTIONS, encoding="utf-8").read()
    for line in source.splitlines():
        stripped = line.strip().rstrip(",;")
        if stripped.isupper() and stripped.isalpha() and len(stripped) > 2:
            if stripped.lower() not in loaded:
                problems.append("SwingMotion.%s 에 해당하는 %s.json 이 없습니다"
                                % (stripped, stripped.lower()))

    # 모션끼리 구분되는지.
    print()
    print("모션 쌍별 최대 차이 (기준 %.0f도)" % MIN_DIFFERENCE_DEGREES)
    for a, b in itertools.combinations(sorted(loaded), 2):
        worst = 0.0
        for key in set(loaded[a]) | set(loaded[b]):
            if key[1] not in ANGLE_CHANNELS:
                continue
            for tick in range(0, 21):
                va = sample(loaded[a][key], tick) if key in loaded[a] else 0.0
                vb = sample(loaded[b][key], tick) if key in loaded[b] else 0.0
                worst = max(worst, abs(math.degrees(va - vb)))
        ok = worst > MIN_DIFFERENCE_DEGREES
        print("  %-9s vs %-9s  %6.0f도  %s" % (a, b, worst, "구분됨" if ok else "너무 비슷함"))
        if not ok:
            problems.append("%s 와 %s 가 화면에서 구분되지 않을 만큼 비슷합니다" % (a, b))

    print()
    if problems:
        print("문제가 있습니다:")
        for item in problems:
            print("  -", item)
        print()
        print("tools/gen_animations.py 의 각도를 고치고 다시 실행하세요.")
        return 1

    print("모든 애니메이션이 정상입니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
