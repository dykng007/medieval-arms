# Medieval Arms

[![Build](https://github.com/dykng007/medieval-arms/actions/workflows/build.yml/badge.svg)](https://github.com/dykng007/medieval-arms/actions/workflows/build.yml)

마인크래프트 **1.21.1 / NeoForge** 모드. 중세 무기와 갑옷을 추가하고,
**무기 종류에 따라 휘두르는 모션이 달라진다.**

## 설치

이 모드는 **[PlayerAnimator](https://www.curseforge.com/minecraft/mc-mods/playeranimator)를
함께 설치해야 한다.** 무기를 휘두르는 애니메이션을 그 라이브러리가 재생하기 때문에,
없으면 게임이 켜지지 않는다. CurseForge 페이지에도 필수 의존성으로 표시되어 있어
보통은 함께 받아진다.

| 넣을 것 | 어디서 |
|---|---|
| `medievalarms-<버전>.jar` | 이 저장소의 [Releases](https://github.com/dykng007/medieval-arms/releases) |
| `player-animation-lib-forge-<버전>.jar` | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/playeranimator) — 1.21.1 / NeoForge 용 |

---

## 개발 환경

| 필요한 것 | 버전 |
|---|---|
| JDK | 21 (`C:\Program Files\Java\jdk-21`) |
| Gradle | 설치 불필요 — `gradlew`가 알아서 받는다 |
| NeoForge | 21.1.248 |

### 자주 쓰는 명령

Windows PowerShell 기준. 모두 프로젝트 폴더에서 실행한다.

```powershell
.\gradlew build      # jar 빌드 → build/libs/medievalarms-<버전>.jar
.\gradlew runClient  # 모드가 적용된 마인크래프트를 띄운다 (개발용)
.\gradlew runData    # 아이템 모델/레시피/번역 JSON을 생성한다
.\gradlew runServer  # 개발용 서버를 띄운다
```

> **첫 `build`는 10~40분 걸린다.** 마인크래프트를 내려받아 디컴파일하기 때문이며,
> 최초 한 번만 그렇다. 두 번째부터는 수십 초로 끝난다.

### 무기를 추가하거나 수치를 바꾸려면

무기 스펙은 전부 `src/main/java/com/dykng/medievalarms/weapon/WeaponType.java`
**한 파일에 모여 있다.** 공격력·공격속도·리치·모션 종류가 상수 하나에 다 들어 있어서,
새 무기를 넣는 일은 거기에 한 줄을 더하고 텍스처 png 하나를 넣는 것으로 끝난다.
등록·모델·레시피·번역은 그 목록을 순회하며 자동으로 만들어진다.

수정한 뒤에는 이 두 가지를 반드시 해야 한다.

```powershell
.\gradlew runData                            # 모델/레시피/번역 JSON 다시 생성
python tools\check_recipe_conflicts.py       # 레시피가 바닐라와 겹치지 않는지 검사
```

**레시피 충돌 검사를 건너뛰지 말 것.** 마인크래프트는 모양 있는 레시피를 빈 행·열을
잘라낸 뒤 비교하기 때문에, 잘라낸 결과가 바닐라와 같아지면 둘 중 하나가 영영
제작 불가가 된다. 게임은 아무 경고도 주지 않는다. 실제로 이 모드를 만들 때
워해머가 바닐라 곡괭이와, 전투도끼가 바닐라 도끼와 겹쳐 배치를 다시 잡아야 했다.

### 휘두르는 모션을 조정하려면

`tools/gen_animations.py`의 각도만 고치고 다시 실행하면 된다. 자바 코드는 건드릴 필요가 없다.

```powershell
python tools\gen_animations.py    # 각도 -> assets/medievalarms/player_animations/*.json
python tools\check_animations.py  # 게임 켜기 전에 검사
```

모션은 **네 박자**로 되어 있다. 반대쪽으로 몸을 꼬아 힘을 모으고(준비), 꼬았던 몸이
풀리며 무기가 나가고(타격), 여세로 조금 더 갔다가(마무리), 평상시 자세로 돌아온다.

각도는 도 단위로 적고, 스크립트가 라디안으로 바꿔 넣는다.

| 채널 | 뜻 |
|---|---|
| `pitch` | 팔은 음수가 앞으로 올라감. −90이 수평 정면, −200쯤이 머리 위.<br>몸통은 양수가 뒤로 젖히기, 음수가 앞으로 숙이기 |
| `yaw` | 좌우 회전 |
| `roll` | 팔을 옆으로 벌리기. +90이면 완전히 옆 |
| `x` `y` `z` | 픽셀 단위 이동. `z`가 음수면 앞쪽 |

**가장 중요한 것은 팔이 아니라 몸통(`torso`)이다.** 처음에는 손에 든 아이템만
회전·이동시켰다. 팔도 몸도 그대로여서 무기만 허공에서 떠다니는 것처럼 보였고,
숫자를 아무리 맞춰도 그 한계는 넘지 못했다. 사람이 창을 지를 때 실제로 움직이는
것은 무기가 아니라 몸이다. 지금은 몸통이 좌우로 ±60도씩 돌고 머리가 그 60%를
따라간다. 머리를 100% 따라가게 하면 1인칭에서 화면이 심하게 흔들린다.

**검사를 건너뛰지 말 것.** 이 형식은 틀려도 게임이 죽지 않고 조용히 아무 일도
일어나지 않는다. 뼈대 이름을 `rightarm`이라고 쓰면(맞는 이름은 `rightArm`)
라이브러리가 그 항목을 그냥 건너뛴다. 오른팔이 안 움직이는 걸 게임을 켜서 눈으로
알아채야 하는데, 한 번 켜는 데 몇 분이 걸린다.

재생은 [PlayerAnimator](https://github.com/KosmX/minecraftPlayerAnimator)가 한다.
플레이어가 이 라이브러리를 **함께 설치해야 한다**(필수 의존성).

### 텍스처를 바꾸려면

아이템 아이콘은 GPT로 그린 그림을 줄여서 만든다. 원본은 `art/` 에 있다.

```powershell
python tools\import_art.py    # art/*.png -> 16x16 아이템 아이콘
python tools\gen_armor_layers.py  # 갑옷을 입었을 때 몸에 씌워지는 레이어
python tools\preview_armor.py     # 그 레이어가 몸에 어떻게 보이는지 미리보기
```

아이콘은 바닐라의 16x16 이 아니라 **32x32** 다. 마인크래프트는 2의 거듭제곱이면
받아주고, NeoForge 가 `SpriteLoader` 에서 밉맵 레벨을 낮추는 바닐라 동작까지 꺼놨다.
16x16 에서는 원본 그림의 세부가 너무 많이 날아갔다. 되돌리려면 `import_art.py` 의
`SIZE` 를 16으로, `gen_armor_layers.py` 의 `SCALE` 을 1로 바꾸면 된다.

**갑옷을 입었을 때** 몸에 씌워지는 레이어는 별개다. 그건 갑옷 그림이 아니라
플레이어 모델에 감기는 UV 전개도라, 칸마다 어느 면이 오는지 정해져 있다.
갑옷처럼 생긴 그림을 통째로 넣으면 몸에 엉뚱하게 발린다.

그래서 `art/armor-panels.png` 에 **면에 그대로 들어갈 직사각형 판** 여섯 장을 받아
`gen_armor_layers.py` 가 UV 칸에 배치한다. 판을 다시 뽑을 때는 이렇게 요청한다.

- 여섯 판을 한 줄로, 사이를 넉넉히 띄우고, 배경은 투명하게
- 각 판은 구멍 없이 꽉 찬 직사각형
- **가운데는 밝게, 좌우 끝은 짙은 그늘로** (원통처럼)

마지막 항목이 핵심이다. 플레이어 모델은 상자라 기하학적으로 둥글게 만들 수 없어서,
둥글어 보이려면 음영이 그렇게 칠해져 있어야 한다. 그 음영을 코드로 곱해보기도 했는데
판금 무늬에 묻혀 효과가 거의 없었다. 그림 자체에 그려져 있어야 한다.

결과가 몸에 어떻게 보이는지는 `preview_armor.py` 로 게임을 켜기 전에 확인할 수 있다.
앞면과 뒷면을 나란히 그려주는데, 앞면 그림을 뒷면에 재활용하면 뒤통수에 바이저가
생기는 식의 실수가 바로 보인다.

`import_art.py` 는 `art/weapons-source.png` 와 `art/armor-source.png` 를 읽어
무기 6종과 갑옷 8개(4부위 x 2세트)를 만든다. 기사 세트는 그림을 따로 뽑지 않고
종자 세트를 청색으로 물들여 쓴다. 두 세트의 형태가 정확히 같아야 한 벌로 보이기 때문이다.

그림을 새로 뽑을 때는 **무기나 부위를 한 줄로 나란히, 배경은 투명하게** 요청한다.
`import_art.py` 가 연결된 덩어리를 세어 아이템을 가르므로, 개수가 맞지 않으면
그 자리에서 알려준다.

**직접 그린 16x16 png로 덮어써도 된다.** 그 경우 `import_art.py` 를 다시
실행하지만 않으면 덮어쓴 그림이 유지된다.

---

## 릴리스하는 법

`gradle.properties`의 `mod_version`을 올리고, 같은 번호로 태그를 밀면 끝이다.

```bash
# 1. 버전 올리고 커밋
git commit -am "release 0.2.0"
git push

# 2. 태그 푸시 — 이후는 전부 자동
git tag v0.2.0
git push origin v0.2.0
```

태그가 올라가면 GitHub Actions가:

1. jar를 빌드하고 (버전은 태그에서 뽑아 쓴다)
2. GitHub Release를 만들어 jar를 첨부하고
3. CurseForge에 업로드한다 — **시크릿이 등록되어 있을 때만**

CurseForge 시크릿이 없으면 그 단계만 조용히 건너뛰고 나머지는 정상 진행된다.
연결 방법은 [`docs/CURSEFORGE.md`](docs/CURSEFORGE.md) 참고.

태그에 `-beta`나 `-alpha`가 들어 있으면 릴리스 종류도 자동으로 그렇게 표시된다.
예: `v0.3.0-beta.1` → beta 릴리스.

---

## 프로젝트 구조

```
build.gradle                  빌드 설정. MOD_VERSION 환경변수로 버전을 덮어쓸 수 있게 되어 있다
gradle.properties             ★ 모드 이름/버전/NeoForge 버전의 단일 출처
src/main/templates/           빌드할 때 ${...}가 치환되는 템플릿 (neoforge.mods.toml)
src/main/java/                자바 소스
  weapon/WeaponType.java        ★ 무기 스펙 표
  weapon/SwingMotion.java       ★ 모션 모양 표
  armor/ArmorSet.java           ★ 갑옷 세트 표
  client/                       1인칭 렌더링, 3인칭 들고 있는 자세
  datagen/                      모델/레시피/태그/번역 생성기
src/main/resources/           텍스처 등 직접 만든 리소스
src/generated/resources/      runData가 만들어낸 JSON (커밋함)
art/                          GPT로 그린 원본 그림 (아이콘과 갑옷 재질의 출처)
tools/import_art.py           art/*.png -> 16x16 아이템 아이콘
tools/gen_armor_layers.py     갑옷 착용 레이어 (UV 전개도에 재질 배치)
tools/preview_armor.py        착용 모습 정면 미리보기
tools/check_recipe_conflicts.py  레시피가 바닐라와 겹치는지 검사
tools/gen_animations.py          무기별 휘두르기 애니메이션 생성
tools/check_animations.py        애니메이션이 올바른지 검사
.github/workflows/build.yml   push/PR 마다 빌드 검사
.github/workflows/release.yml v* 태그 → 빌드·릴리스·업로드
```

## 라이선스

MIT
