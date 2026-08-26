# CurseForge 업로드 연결하기

릴리스 워크플로에는 CurseForge 업로드가 이미 들어가 있다.
다만 **시크릿 두 개가 등록되기 전까지는 그 단계를 조용히 건너뛴다.**
그래서 아래 절차는 급하지 않고, 준비되면 그때 하면 된다. 워크플로 파일은 고칠 필요가 없다.

## 왜 이 부분만 손으로 해야 하는가

CurseForge 업로드 API는 `POST /api/projects/{projectId}/upload-file` 하나뿐이고,
**이미 존재하는 프로젝트에만** 파일을 올릴 수 있다.
프로젝트를 만드는 API는 없고, 만든 뒤에도 CurseForge 쪽 검토를 기다려야 한다.
그래서 프로젝트 생성만은 사람이 웹에서 한 번 해줘야 한다.

---

## 1. 프로젝트 만들기

**주소를 정확히 확인할 것.** CurseForge에는 비슷하게 생긴 사이트가 둘 있는데
용도가 완전히 다르다. 실제로 이걸 헷갈려서 한참 헤맸다.

| 사이트 | 누구를 위한 곳인가 |
|---|---|
| **authors**.curseforge.com | **모드 제작자.** 여기가 우리가 쓸 곳이다 |
| **console**.curseforge.com | 게임 개발사. 자기 *게임*을 CurseForge에 등록하는 곳 |

스튜디오 콘솔에 들어가면 게임과 카테고리를 편집하는 화면이 나오는데,
거기 보이는 숫자는 게임 ID이지 프로젝트 ID가 아니다. 거기 있는 Logo 항목도
게임 로고라 모드 아이콘 규격과 다르다.

모드 프로젝트는 아래 주소에서 만든다.

    https://authors.curseforge.com/#/projects/create/choose-game

게임으로 **Minecraft**를 고른 뒤 아래 값을 넣는다. 그대로 복사해 쓰면 된다.

| 항목 | 값 |
|---|---|
| Name | `Medieval Arms` |
| Summary | 중세 무기와 갑옷을 추가합니다. 무기 종류에 따라 휘두르는 모션이 달라집니다. |
| Category | Armor, Tools, and Weapons |
| Game Versions | 1.21.1 |
| Mod Loader | NeoForge |
| License | MIT |
| Source URL | https://github.com/dykng007/medieval-arms |
| Issues URL | https://github.com/dykng007/medieval-arms/issues |

### 이미지 두 종류를 헷갈리지 말 것

CurseForge 제출 화면의 **Logo** 항목은 정사각 아이콘이 아니라 **가로로 긴 배너**다.
화면에 적힌 조건이 `PNG,WEBP / 100KB / 104x40` 이다. 정사각 이미지를 넣으면 거부된다.

| 쓰는 곳 | 파일 | 크기 | 만드는 스크립트 |
|---|---|---|---|
| 제출 화면의 **Logo** | `docs/banner.png` | 104x40 | `tools/gen_banner.py` |
| 프로젝트 **아바타** | `docs/avatar.png` | 800x800 | `tools/gen_logo.py` |

아바타 쪽 조건은 최소 400x400에 가로세로가 같아야 하고, 더 크면 알아서 축소된다.
webp는 제출 시 Internal Server Error가 나므로 쓰지 않는다.

두 스크립트 모두 게임에 실제로 들어가는 장검 텍스처를 그대로 확대해 쓴다.
아이템 그림을 바꾸고 `tools/import_art.py` 를 돌린 뒤 다시 실행하면 함께 갱신된다.

**설명(Description)** 란에는 아래 정도면 충분하다.

```
중세 무기와 갑옷을 추가하는 모드입니다.

무기 6종
- 창 / 미늘창 / 철퇴 / 전투도끼 / 워해머 / 장검
- 무기마다 공격력, 공격 속도, 닿는 거리가 다릅니다.
- 창과 미늘창은 더 멀리 닿습니다.

갑옷 2세트
- 종자 갑옷 (철 등급)
- 기사 갑옷 (다이아 등급, 넉백 저항 있음)

무기 종류에 따라 휘두르는 모션이 달라집니다.
창은 앞으로 내지르고, 철퇴는 위에서 아래로 내리치고,
미늘창은 옆으로 크게 후립니다.

다른 모드에 의존하지 않습니다. 이 파일 하나만 넣으면 동작합니다.
```

제출하면 검토 대기 상태가 된다. 보통 하루이틀 걸린다.

## 2. Project ID 확인

두 가지 방법이 있다.

**승인 전** — 작성자 포털에서 프로젝트를 열면 주소가 이렇게 된다.

    https://authors.curseforge.com/#/projects/1234567
                                              ^^^^^^^ 이 숫자

**승인 후** — 공개 페이지의 Details 상자에 `Project ID` 항목으로 표시된다.

주소창의 슬러그(`medieval-arms` 같은 글자)가 아니라 **숫자**여야 한다.
틀린 숫자를 넣으면 업로드가 `errorCode 1005 — Invalid projectID` 로 거부된다.

## 3. API 토큰 발급

<https://authors-old.curseforge.com/account/api-tokens> 에서 새 토큰을 만든다.
(토큰 페이지는 아직 구버전 포털에 있다. 스튜디오 콘솔이 아니다.)

**토큰은 발급 직후 한 번만 보인다.** 화면을 벗어나기 전에 복사해 둔다.

## 4. GitHub 시크릿 등록

저장소 폴더에서 아래 두 줄을 실행하고, 각각 프롬프트에 값을 붙여넣는다.

```bash
gh secret set CURSEFORGE_ID      # 2번에서 확인한 숫자
gh secret set CURSEFORGE_TOKEN   # 3번에서 발급한 토큰
```

웹에서 하려면 저장소 → Settings → Secrets and variables → Actions → New repository secret.

등록 여부만 확인하려면 (값은 보이지 않는다):

```bash
gh secret list
```

## 5. 확인

다음 태그를 밀면 CurseForge에도 올라간다.

```bash
git tag v0.1.1
git push origin v0.1.1
```

Actions 로그의 Publish 단계에 CurseForge 파일 링크가 찍히면 성공이다.
시크릿이 없을 때는 그 줄 없이 GitHub 발행만 하고 넘어간다.

## 참고

- 첫 업로드는 CurseForge가 파일 자체도 한 번 검토할 수 있어 곧바로 공개되지 않을 수 있다.
- Modrinth에도 올리고 싶다면 승인 절차가 없어 훨씬 간단하다.
  `MODRINTH_ID` / `MODRINTH_TOKEN` 시크릿을 추가하고 `release.yml`의 Publish 단계에
  `modrinth-id` / `modrinth-token` 두 줄만 넣으면 된다.
