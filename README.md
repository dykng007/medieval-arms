# Medieval Arms

[![Build](https://github.com/dykng007/medieval-arms/actions/workflows/build.yml/badge.svg)](https://github.com/dykng007/medieval-arms/actions/workflows/build.yml)

마인크래프트 **1.21.1 / NeoForge** 모드. 중세 무기와 갑옷을 추가하고,
**무기 종류에 따라 휘두르는 모션이 달라진다.**

외부 라이브러리 의존성이 없다. 이 jar 하나만 넣으면 동작한다.

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

`weapon/SwingMotion.java`의 숫자만 고치면 된다. 렌더링 코드는 건드릴 필요가 없다.

| 값 | 뜻 | 크게 하면 |
|---|---|---|
| `pitchDegrees` | 위아래 회전 | 더 크게 내리친다 |
| `yawDegrees` | 좌우 회전 | 옆으로 넓게 후린다 |
| `thrustDistance` | 앞으로 내밀기 | 찌르는 느낌이 강해진다 |
| `dropDistance` | 아래로 내려가기 | 내려찍는 느낌이 강해진다 |
| `speedScale` | 완급 | 1보다 크면 날렵하게, 작으면 묵직하게 |

같은 값이 1인칭과 3인칭 양쪽에 쓰인다. 3인칭은 팔이 과장되게 꺾이지 않도록
절반만 반영된다.

**텍스처를 직접 그리고 싶다면** `src/main/resources/assets/medievalarms/textures/`
아래 png를 그냥 덮어쓰면 된다. `tools/gen_textures.py`를 다시 실행하지만 않으면
덮어쓴 그림이 그대로 유지된다.

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
  mixin/                        3인칭 휘두르기 (믹스인)
  datagen/                      모델/레시피/태그/번역 생성기
src/main/resources/           텍스처 등 직접 만든 리소스
src/generated/resources/      runData가 만들어낸 JSON (커밋함)
tools/gen_textures.py         텍스처 생성 스크립트 (Pillow 불필요, 표준 라이브러리만)
tools/check_recipe_conflicts.py  레시피가 바닐라와 겹치는지 검사
.github/workflows/build.yml   push/PR 마다 빌드 검사
.github/workflows/release.yml v* 태그 → 빌드·릴리스·업로드
```

## 라이선스

MIT
