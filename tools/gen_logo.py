#!/usr/bin/env python3
"""
CurseForge 프로젝트 아바타(정사각 아이콘)를 만든다.

실행:  python tools/gen_logo.py
원본:  art/icon.png
결과:  docs/avatar.png (800x800)  docs/avatar-small.png (400x400, 100KB 미만)

CurseForge 는 최소 400x400, 가로세로 1:1 을 요구한다. webp 는 제출 시 오류가 나므로
png 로 낸다.

두 장을 만드는 이유는 용량 제한 때문이다. 이 사이트의 그림 항목들은 100KB 제한이
붙어 있는 경우가 있는데(실제로 배너 항목이 그랬다) 아바타 항목이 얼마인지는
올려봐야 안다. 그래서 화질이 좋은 800 짜리와, 어디에 올려도 통과하는 작은 것을
같이 만들어 둔다. avatar.png 가 거부되면 avatar-small.png 를 올리면 된다.

제출 화면의 Logo 항목은 이것이 아니라 104x40 배너다 — tools/gen_banner.py 를 쓴다.

── 왜 아이템 텍스처를 쓰지 않는가 ────────────────────────────────────────
예전에는 게임에 들어가는 32x32 장검 텍스처를 그대로 25배 확대해서 썼다. 모드와
아이콘이 저절로 같이 바뀌는 장점이 있었지만, 결과가 계단처럼 뭉개지고 무엇보다
"모드 로고"가 아니라 "아이템 하나"로 읽혔다. 목록에서 다른 모드들 사이에 놓으면
눈에 띄지 않았다.

지금은 아이콘용 그림을 따로 그려 art/icon.png 에 두고 여기서는 크기만 맞춘다.
아이콘을 바꾸고 싶으면 그 파일을 교체하고 이 스크립트를 다시 돌리면 된다.

필요:  pip install pillow
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow 가 필요합니다:  pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "art", "icon.png")
DOCS = os.path.join(ROOT, "docs")

# 작은 쪽이 반드시 지켜야 할 용량. 색 수를 줄여가며 여기에 맞춘다.
SMALL_LIMIT_BYTES = 100 * 1024


def save_under_limit(icon, path, size, limit):
    """색 수를 줄여가며 용량 제한 안에 들어오는 png 를 저장한다.

    아이콘은 금속 회색과 파랑이 대부분이라 색을 꽤 줄여도 눈에 잘 띄지 않는다.
    화질을 조금 버리더라도 업로드가 거부되지 않는 쪽이 낫다.
    """
    resized = icon.resize((size, size), Image.LANCZOS)
    for colours in (256, 192, 128, 96, 64, 48, 32):
        # RGB 로 바꾼 뒤 팔레트로 줄인다. 배경이 꽉 차 있어 투명도는 필요 없다.
        reduced = resized.convert("RGB").quantize(colors=colours, method=Image.MEDIANCUT)
        reduced.save(path, "PNG", optimize=True)
        if os.path.getsize(path) <= limit:
            return colours
    return None


def main():
    if not os.path.exists(SOURCE):
        print("아이콘 원본이 없습니다:", os.path.relpath(SOURCE, ROOT))
        print("정사각형 png 를 그 자리에 두고 다시 실행하세요.")
        return 2

    icon = Image.open(SOURCE).convert("RGBA")
    if icon.width != icon.height:
        # 정사각이 아니면 가운데를 잘라낸다. CurseForge 가 1:1 만 받는다.
        side = min(icon.size)
        left = (icon.width - side) // 2
        top = (icon.height - side) // 2
        icon = icon.crop((left, top, left + side, top + side))
        print("정사각이 아니라 가운데 %dx%d 를 잘라 썼습니다." % (side, side))

    os.makedirs(DOCS, exist_ok=True)

    # 화질 우선. 사진 같은 그림이라 LANCZOS 로 줄여야 가장자리가 깔끔하다.
    # 예전처럼 픽셀아트를 확대할 때만 NEAREST 가 맞았다.
    big = os.path.join(DOCS, "avatar.png")
    icon.resize((800, 800), Image.LANCZOS).save(big, "PNG", optimize=True)
    print("%-18s 800x800  %7.1f KB   화질 우선" % ("avatar.png", os.path.getsize(big) / 1024.0))

    # 용량 우선.
    small = os.path.join(DOCS, "avatar-small.png")
    colours = save_under_limit(icon, small, 400, SMALL_LIMIT_BYTES)
    size_kb = os.path.getsize(small) / 1024.0
    if colours is None:
        print("%-18s 400x400  %7.1f KB   경고: 100KB 아래로 못 줄였습니다"
              % ("avatar-small.png", size_kb))
    else:
        print("%-18s 400x400  %7.1f KB   색 %d개로 줄임"
              % ("avatar-small.png", size_kb, colours))

    print()
    print("업로드: https://authors.curseforge.com/#/projects/1663275/settings")
    print("avatar.png 가 용량으로 거부되면 avatar-small.png 를 올리세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
