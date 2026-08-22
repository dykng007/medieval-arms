#!/usr/bin/env python3
"""
레시피 충돌 검사기.

실행:  python tools/check_recipe_conflicts.py
       (먼저 ./gradlew runData 를 돌려 레시피 JSON이 생성되어 있어야 한다)

── 왜 필요한가 ──────────────────────────────────────────────────────────
마인크래프트의 모양 있는(shaped) 레시피는 빈 행과 빈 열을 잘라낸 뒤 비교한다.
그래서 잘라낸 결과가 다른 레시피와 같아지면 둘 중 하나만 제작 가능해지고
나머지는 영원히 만들 수 없게 된다. 게임은 아무 경고도 주지 않는다.

실제로 이 모드를 만들 때 두 건이 걸렸다.
  - 워해머의 MMM / _S_ / _S_  가 바닐라 다이아 곡괭이와 같았다
  - 전투도끼의 MM_ / MS_ / _S_ 는 잘라내면 바닐라 도끼와 같았다
갑옷도 가운데에 가죽을 넣기 전에는 바닐라 철/다이아 갑옷과 정확히 같았다.

무기나 갑옷의 배치를 바꾼 뒤에는 반드시 이 검사를 다시 돌려야 한다.

종료 코드: 충돌이 없으면 0, 있으면 1.
"""

import glob
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_RECIPES = os.path.join(ROOT, "src", "generated", "resources", "data", "medievalarms", "recipe", "*.json")

# 바닐라 레시피는 마인크래프트 jar 안에 들어 있다.
# gradlew가 받아둔 것을 그대로 읽는다. 경로가 바뀌면 여기를 고친다.
VANILLA_JAR_GLOB = os.path.join(
    os.path.expanduser("~"), ".gradle", "caches", "neoformruntime", "artifacts", "minecraft_*_client.jar"
)


def trim(pattern):
    """빈 행과 빈 열을 잘라낸다. 마인크래프트가 레시피를 비교하는 방식과 같다."""
    rows = list(pattern)
    while rows and all(c == " " for c in rows[0]):
        rows.pop(0)
    while rows and all(c == " " for c in rows[-1]):
        rows.pop()
    if not rows:
        return ()
    while rows and all(len(r) > 0 and r[0] == " " for r in rows):
        rows = [r[1:] for r in rows]
    while rows and all(len(r) > 0 and r[-1] == " " for r in rows):
        rows = [r[:-1] for r in rows]
    return tuple(rows)


def ingredient_name(value):
    if isinstance(value, dict):
        return value.get("item") or value.get("tag") or json.dumps(value, sort_keys=True)
    if isinstance(value, list):
        return "|".join(sorted(ingredient_name(v) for v in value))
    return str(value)


def signature(recipe):
    """
    배치와 재료를 합친 지문.

    기호 글자(M, S 같은 것)가 무엇인지는 상관없고 각 칸에 실제로 무엇이 들어가는지만
    중요하다. 그래서 기호를 재료 이름으로 바꿔 비교한다.
    지문이 같은 두 레시피는 충돌한다.
    """
    if recipe.get("type") != "minecraft:crafting_shaped":
        return None
    pattern = trim(recipe.get("pattern", []))
    if not pattern:
        return None
    key = {k: ingredient_name(v) for k, v in recipe.get("key", {}).items()}
    return tuple(tuple(key.get(c) if c != " " else None for c in row) for row in pattern)


def load_vanilla():
    jars = glob.glob(VANILLA_JAR_GLOB)
    if not jars:
        return None
    recipes = {}
    with zipfile.ZipFile(jars[0]) as z:
        for name in z.namelist():
            if name.startswith("data/minecraft/recipe") and name.endswith(".json"):
                try:
                    recipes[name] = json.loads(z.read(name))
                except Exception:
                    pass
    return recipes


def main():
    vanilla = load_vanilla()
    if not vanilla:
        print("바닐라 레시피를 찾지 못했습니다.")
        print("먼저 ./gradlew build 를 한 번 돌려 마인크래프트를 내려받으세요.")
        return 2

    by_signature = {}
    for name, recipe in vanilla.items():
        sig = signature(recipe)
        if sig:
            by_signature.setdefault(sig, []).append(os.path.basename(name)[:-5])

    mod_files = sorted(glob.glob(MOD_RECIPES))
    if not mod_files:
        print("모드 레시피가 없습니다. 먼저 ./gradlew runData 를 돌리세요.")
        return 2

    problems = []
    seen = {}
    checked = 0
    for path in mod_files:
        name = os.path.basename(path)[:-5]
        with open(path, encoding="utf-8") as f:
            sig = signature(json.load(f))
        if sig is None:
            continue
        checked += 1
        if sig in by_signature:
            problems.append("바닐라와 충돌: %s  <->  %s" % (name, ", ".join(by_signature[sig])))
        if sig in seen:
            problems.append("모드 안에서 충돌: %s  <->  %s" % (name, seen[sig]))
        seen[sig] = name

    print("바닐라 레시피 %d개와 대조, 모드 레시피 %d개 검사" % (len(vanilla), checked))
    if problems:
        print("\n충돌이 있습니다:")
        for p in problems:
            print("  -", p)
        print("\nModRecipeProvider.java 에서 해당 배치를 바꾸고 runData 를 다시 돌리세요.")
        return 1
    print("충돌 없음.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
