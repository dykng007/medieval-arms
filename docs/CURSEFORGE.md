# CurseForge 업로드 연결하기

릴리스 워크플로는 이미 CurseForge 업로드까지 포함해 작성되어 있다.
다만 **시크릿 두 개가 등록되기 전까지는 CurseForge 단계를 조용히 건너뛴다.**
따라서 아래 절차는 급하지 않으며, 준비되면 그때 하면 된다. 워크플로 파일은 고칠 필요가 없다.

## 왜 자동으로 못 만드는가

CurseForge 업로드 API는 `POST /api/projects/{projectId}/upload-file` 하나뿐이고,
**이미 존재하고 승인까지 끝난 프로젝트에만** 파일을 올릴 수 있다.
프로젝트 생성 자체는 API가 없고, 만든 뒤에도 CurseForge 스태프의 수동 승인을 기다려야 한다.
그래서 이 부분만은 사람이 한 번 해줘야 한다.

## 절차

### 1. 프로젝트 생성

<https://legacy.curseforge.com/minecraft/mc-mods> 에서 로그인 후 프로젝트를 만든다.
입력할 값:

- **Name**: Medieval Arms
- **Summary**: 중세 무기와 갑옷을 추가하고, 무기 종류별로 휘두르는 모션이 달라지는 모드
- **Category**: Armor, Tools, and Weapons
- **License**: MIT
- **Source URL**: https://github.com/dykng007/medieval-arms
- **Issues URL**: https://github.com/dykng007/medieval-arms/issues

제출하면 승인 대기 상태가 된다. 보통 1~2일 걸린다.

### 2. Project ID 확인

승인되면 프로젝트 페이지 오른쪽 "About Project" 박스에 **Project ID**가 숫자로 표시된다.
(주소창의 슬러그가 아니라 이 숫자여야 한다.)

### 3. API 토큰 발급

<https://legacy.curseforge.com/account/api-tokens> 에서 새 토큰을 만든다.
**토큰은 발급 직후 한 번만 보여진다.** 이 화면을 벗어나기 전에 복사해 둔다.

### 4. GitHub 시크릿 등록

저장소 폴더에서:

```bash
gh secret set CURSEFORGE_ID     # 프롬프트에 Project ID 숫자를 붙여넣는다
gh secret set CURSEFORGE_TOKEN  # 프롬프트에 API 토큰을 붙여넣는다
```

웹에서 하려면 저장소 → Settings → Secrets and variables → Actions → New repository secret.

### 5. 확인

다음 태그를 밀면 CurseForge에도 올라간다.

```bash
git tag v0.1.1
git push origin v0.1.1
```

Actions 로그의 Publish 단계에서 CurseForge 파일 링크가 출력되면 성공이다.

## 참고

- 첫 업로드는 CurseForge가 파일 자체도 한 번 검토할 수 있어 즉시 공개되지 않을 수 있다.
- 나중에 Modrinth에도 올리고 싶다면 `MODRINTH_ID` / `MODRINTH_TOKEN` 시크릿을 추가하고
  `release.yml`의 Publish 단계에 `modrinth-id` / `modrinth-token` 두 줄만 넣으면 된다.
  Modrinth는 CurseForge와 달리 승인 절차가 없어 훨씬 간단하다.
