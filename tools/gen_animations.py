#!/usr/bin/env python3
"""
무기별 휘두르기 애니메이션 JSON을 만든다.

실행:  python tools/gen_animations.py
결과:  src/main/resources/assets/medievalarms/player_animations/*.json

── 왜 이 방식인가 ────────────────────────────────────────────────────────
처음에는 애니메이션 없이 손에 든 아이템만 회전·이동시켰다. 팔도 몸도 움직이지
않으니 무기만 허공에서 떠다니는 것처럼 보였고, 숫자를 아무리 맞춰도 그 한계는
넘지 못했다. 사람이 창을 지를 때 실제로 움직이는 것은 무기가 아니라 몸이다.

그래서 PlayerAnimator 라이브러리로 바꿨다. 이 스크립트는 그 라이브러리가 읽는
Emotecraft 형식의 JSON을 만든다.

JSON을 손으로 쓰지 않고 스크립트로 만드는 이유는 두 가지다. 하나는 JSON이
(뼈대 x 채널 x 시점)마다 항목이 하나씩이라 사람이 읽기 어렵기 때문이고, 다른
하나는 각도를 라디안으로 적어야 하기 때문이다. 여기서는 도 단위로 적고 변환은
스크립트가 한다.

── 좌표계 ────────────────────────────────────────────────────────────────
아래 규칙은 추측이 아니라 같은 형식으로 만들어진 기존 애니메이션에서 실제 값을
읽어 확인한 것이다.

  pitch   X축. 팔은 음수가 앞으로 올라간다. -90 이 수평 정면, -200 쯤이 머리 위.
          몸통은 양수가 뒤로 젖히기, 음수가 앞으로 숙이기.
  yaw     Y축. 좌우 회전. 오른팔은 양수가 바깥(오른쪽)으로 벌어진다.
  roll    Z축. 팔은 양수가 옆으로 벌어진다. +90 이면 팔이 완전히 옆으로 간다.
  x,y,z   픽셀 단위 이동. z 가 음수면 앞쪽이다.

뼈대 중 rightItem 은 팔이 아니라 손에 든 물건만 따로 돌린다. 팔은 제대로 나가는데
무기가 비스듬히 들려 있을 때 쓰는 것이다. 바닐라는 손에 든 물건을 대각선으로
기울여 보여주기 때문에(item/handheld 의 Z축 55도), 창처럼 끝으로 찔러야 하는
무기는 이 뼈대로 각도를 바로잡아야 한다.

가장 중요한 것은 몸통(torso)이다. 참고 애니메이션에서 몸통은 준비 동작에서
한쪽으로 60도 가까이 꼬였다가 타격에서 반대로 돌아나온다. 팔만 움직이면
아무리 잘 맞춰도 몸이 굳은 것처럼 보인다.

머리는 몸통을 따라간다. 다만 몸통과 똑같이 돌리면 1인칭에서 화면이 크게
휘둘려 어지러우므로 60%만 따라가게 했다.
"""

import io
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "main", "resources", "assets",
                   "medievalarms", "player_animations")

# 머리가 몸통 회전을 따라가는 비율.
# 1.0 이면 참고 애니메이션과 같지만 1인칭에서 화면이 심하게 흔들린다.
HEAD_FOLLOW = 0.6

# 각도 채널. 이 채널만 도 -> 라디안 변환 대상이다. x/y/z 는 픽셀이라 그대로 둔다.
ANGLE_CHANNELS = ("pitch", "yaw", "roll", "bend")


# ── 애니메이션 정의 ───────────────────────────────────────────────────────
#
# 각 항목은 {틱: {뼈대: {채널: 도}}} 형태다. 틱 20이 1초다.
#
# 모든 동작은 네 박자로 되어 있다.
#   0        평상시 자세 (전부 0)
#   준비     반대쪽으로 몸을 꼬아 힘을 모은다
#   타격     꼬았던 몸이 풀리며 무기가 나간다
#   마무리   여세로 조금 더 갔다가
#   끝       평상시 자세로 돌아온다
#
# 마지막 틱에서 모든 채널이 0으로 돌아와야 한다. 하나라도 남으면 그 자세가
# 그대로 굳는다.

ANIMATIONS = {}

# 창 — 찌르기.
# 몸을 옆으로 꼬았다가 풀면서 창을 정면으로 내지른다. 팔 각도(-92도)는 거의
# 수평이고, 실제로 창을 앞으로 보내는 힘은 몸통 회전(-50 -> +18)에서 나온다.
ANIMATIONS["thrust"] = {
    0:  {},
    5:  {"rightArm": {"pitch": -75, "yaw": 30, "z": 2},
         "leftArm":  {"pitch": -70, "yaw": 55},
         "torso":    {"yaw": -50, "pitch": -8}},
    8:  {"rightArm": {"pitch": -92, "yaw": -18, "z": -4},
         "leftArm":  {"pitch": -85, "yaw": 25, "z": -3},
         "torso":    {"yaw": 18, "pitch": -22},
         "rightItem": {"pitch": -105, "roll": 90, "yaw": -12}},
    11: {"rightArm": {"pitch": -80, "yaw": -25, "z": -2},
         "leftArm":  {"pitch": -75, "yaw": 20},
         "torso":    {"yaw": 8, "pitch": -14},
         "rightItem": {"pitch": -100, "roll": 92, "yaw": -14}},
    14: {"rightItem": {"pitch": -50, "roll": 46, "yaw": -7}},
    17: {},
}
# 창끝이 앞을 보게 하는 각도는 rightItem 에 있다.
#
# 팔은 제대로 앞으로 나가는데 창이 비스듬히 세워진 채로 질러지는 문제가 있었다.
# 바닐라가 손에 든 물건을 대각선으로 기울여 보여주기 때문이고, 팔 각도를 아무리
# 고쳐도 무기 자체의 기울기는 그대로 남는다.
#
# roll 90 이 그 기울기를 세우고, pitch -105 가 창끝을 정면으로 눕힌다.
# 두 값 모두 부호가 직관과 반대라(처음에 roll -55 로 짐작했다가 틀렸다)
# 같은 형식으로 만들어진 기존 찌르기 자세에서 축 방향을 확인해 잡았다.
#
# t14 는 중간 복귀 지점이다. 이게 없으면 마지막 3틱 만에 90도를 되돌아오느라
# 공격이 끝날 때 창이 손 안에서 팽 도는 것처럼 보인다.

# 미늘창 — 넓게 후리기.
# 위아래가 아니라 좌우로 크게 호를 그린다. 몸통이 -60 에서 +65 까지 125도를
# 돌아 무기가 몸을 감고 나가게 한다.
ANIMATIONS["sweep"] = {
    0:  {},
    6:  {"rightArm": {"pitch": -60, "roll": 70, "yaw": 60},
         "leftArm":  {"pitch": -40, "yaw": 40},
         "torso":    {"yaw": -60, "roll": 8}},
    9:  {"rightArm": {"pitch": -85, "roll": 15, "yaw": -55},
         "leftArm":  {"pitch": -60, "yaw": -30},
         "torso":    {"yaw": 65, "roll": -10}},
    13: {"rightArm": {"pitch": -70, "roll": 5, "yaw": -70},
         "leftArm":  {"pitch": -50, "yaw": -40},
         "torso":    {"yaw": 45, "roll": -6}},
    19: {},
}

# 철퇴·워해머 — 내리치기.
# 팔을 머리 뒤까지(-200도) 넘긴 뒤 몸을 앞으로 접으며 내리찍는다.
# 몸통이 +25(뒤로 젖힘)에서 -50(앞으로 숙임)으로 가는 게 무게감을 만든다.
ANIMATIONS["overhead"] = {
    0:  {},
    6:  {"rightArm": {"pitch": -200, "yaw": 15},
         "leftArm":  {"pitch": -195, "yaw": -15},
         "torso":    {"pitch": 25}},
    9:  {"rightArm": {"pitch": -70, "yaw": -8},
         "leftArm":  {"pitch": -68, "yaw": 8},
         "torso":    {"pitch": -50}},
    13: {"rightArm": {"pitch": -55, "yaw": -5},
         "leftArm":  {"pitch": -54, "yaw": 5},
         "torso":    {"pitch": -32}},
    20: {},
}

# 전투도끼 — 대각선 내려찍기.
# 내리치기에 몸통 회전을 섞어 오른쪽 어깨 위에서 왼쪽 아래로 지나가게 한다.
ANIMATIONS["chop"] = {
    0:  {},
    6:  {"rightArm": {"pitch": -185, "roll": 35, "yaw": 40},
         "leftArm":  {"pitch": -165, "yaw": 20},
         "torso":    {"yaw": -40, "pitch": 18}},
    9:  {"rightArm": {"pitch": -72, "roll": -20, "yaw": -30},
         "leftArm":  {"pitch": -70, "yaw": -12},
         "torso":    {"yaw": 35, "pitch": -40, "roll": -12}},
    13: {"rightArm": {"pitch": -55, "roll": -12, "yaw": -42},
         "leftArm":  {"pitch": -52, "yaw": -20},
         "torso":    {"yaw": 22, "pitch": -25, "roll": -7}},
    19: {},
}

# 장검 — 베기.
# 한 손 무기라 왼팔은 거의 두지 않는다. 칼을 오른쪽 뒤로 뺐다가
# 대각선으로 그어내린다. 다섯 중 가장 빠르다.
ANIMATIONS["slash"] = {
    0:  {},
    5:  {"rightArm": {"pitch": -30, "roll": 80, "yaw": 50},
         "leftArm":  {"pitch": -12, "yaw": 10},
         "torso":    {"yaw": -35}},
    8:  {"rightArm": {"pitch": -88, "roll": 12, "yaw": -35},
         "leftArm":  {"pitch": 10, "yaw": -8},
         "torso":    {"yaw": 45, "roll": -10}},
    11: {"rightArm": {"pitch": -70, "roll": 6, "yaw": -50},
         "leftArm":  {"pitch": 6, "yaw": -12},
         "torso":    {"yaw": 30, "roll": -6}},
    16: {},
}


def add_head_follow(frames):
    """머리가 몸통 회전을 따라가게 한다.

    플레이어 모델에서 머리는 몸통의 자식이 아니라서, 몸통만 돌리면 몸은
    돌아갔는데 머리는 정면을 본 채로 목이 꺾인 모습이 된다.
    """
    for bones in frames.values():
        torso = bones.get("torso")
        if not torso:
            continue
        head = {}
        for channel in ("yaw", "pitch", "roll"):
            if channel in torso:
                head[channel] = round(torso[channel] * HEAD_FOLLOW, 1)
        if head:
            bones["head"] = head


def build(frames):
    """{틱: {뼈대: {채널: 도}}} 를 Emotecraft 의 moves 배열로 바꾼다.

    참고 애니메이션과 예제가 모두 항목 하나에 뼈대 하나, 채널 하나만 담고 있다.
    여러 개를 한 항목에 넣어도 읽힐지 확인할 방법이 없어 같은 방식을 따른다.
    """
    ticks = sorted(frames)
    last = ticks[-1]

    # 어느 (뼈대, 채널) 이 이 애니메이션에서 쓰이는지 모은다.
    used = set()
    for bones in frames.values():
        for bone, channels in bones.items():
            for channel in channels:
                used.add((bone, channel))

    moves = []
    for bone, channel in sorted(used):
        # 이 채널이 실제로 값을 갖는 시점 + 처음과 끝.
        #
        # 모든 시점에 키프레임을 찍으면 안 된다. 그렇게 하면 어느 한 뼈대 때문에
        # 시점을 하나 추가했을 때 다른 뼈대들까지 그 시점에 0으로 끌려간다.
        # 창의 무기 각도를 다듬으려고 t14 를 넣었더니 팔과 몸통이 t14 에서
        # 평상시 자세로 튀어버린 적이 있다.
        #
        # 처음과 끝은 값이 없어도 반드시 넣는다. 그래야 동작이 평상시 자세에서
        # 시작해 평상시 자세로 끝나고, 자세가 굳는 일이 없다.
        defined = [t for t in ticks if channel in frames[t].get(bone, {})]
        for tick in sorted(set(defined) | {ticks[0], last}):
            value = frames[tick].get(bone, {}).get(channel, 0.0)
            if channel in ANGLE_CHANNELS:
                value = math.radians(value)
            moves.append({
                "tick": tick,
                # 타격으로 들어가는 구간만 빠르게 튀어나오도록 감속을 쓴다.
                "easing": "OUTQUAD" if tick == last else "INOUTSINE",
                "turn": 0,
                bone: {channel: round(value, 5)},
            })
    return moves, last


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, frames in sorted(ANIMATIONS.items()):
        add_head_follow(frames)
        moves, last = build(frames)
        document = {
            "name": name,
            "author": "dykng007",
            "description": "medievalarms %s attack" % name,
            "emote": {
                "beginTick": 0,
                "endTick": last,
                # 마지막 자세에서 평상시로 돌아갈 여유를 조금 준다.
                "stopTick": last + 3,
                "isLoop": False,
                "returnTick": 0,
                "nsfw": False,
                # 각도는 위에서 이미 라디안으로 바꿔 넣었다.
                "degrees": False,
                "moves": moves,
            },
        }
        path = os.path.join(OUT, name + ".json")
        with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(document, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print("%-9s 키프레임 %3d개  길이 %2d틱 (%.1f초)"
              % (name, len(moves), last, last / 20.0))
    print()
    print("결과: %s" % os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
