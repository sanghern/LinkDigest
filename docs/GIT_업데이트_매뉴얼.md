# Git 업데이트 매뉴얼

이 프로젝트에서 변경 사항을 Git에 반영하는 절차입니다.

---

## 0. 스크립트로 한 번에 하기 (권장)

작업 내용(커밋 메시지)만 입력하면 스테이징 → 커밋까지 자동으로 수행하는 스크립트를 사용할 수 있습니다.

```bash
# 프로젝트 루트에서 실행
./scripts/git-update.sh "feat: URL 전역 중복 체크"

# 커밋 후 원격까지 푸시하려면 -p 옵션
./scripts/git-update.sh "feat: URL 전역 중복 체크" -p

# 메시지를 입력하지 않으면 프롬프트로 입력받음
./scripts/git-update.sh
./scripts/git-update.sh -p
```

- **첫 번째 인자**: 커밋 메시지(작업 내용). 공백이 있으면 따옴표로 감싸세요.
- **`-p` / `--push`**: 커밋 후 `git push origin main` 실행

스크립트는 변경 사항이 없으면 커밋하지 않고, `git add -A` 로 수정/추가/삭제된 파일을 모두 스테이징합니다.

---

## 1. 사전 확인

- **Git 설치**: 터미널에서 `git --version` 으로 확인
- **저장소 위치**: 프로젝트 루트(`aiScrapping/`)에서 작업
- **원격 설정**: `git remote -v` 로 `origin` 이 올바른 저장소를 가리키는지 확인

```bash
cd /Users/shsong/mini-servers/aiScrapping   # 프로젝트 루트로 이동
git --version
git remote -v
```

---

## 2. 변경 사항 확인

작업 후 어떤 파일이 바뀌었는지 확인합니다.

```bash
# 요약 보기
git status

# 변경 내용 간단히 보기
git status -s

# 특정 파일 diff
git diff -- backend/app/api/endpoints/bookmarks.py
```

---

## 3. 스테이징 (Staging)

커밋에 포함할 파일만 선택합니다.

```bash
# 특정 파일만 스테이징
git add backend/app/api/endpoints/bookmarks.py
git add frontend/src/components/AddBookmark.js

# 특정 디렉터리 전체
git add backend/app/
git add frontend/src/
git add docs/

# 수정·추가된 모든 파일 (삭제 제외)
git add -u

# 모든 변경(추가/수정/삭제) 한 번에
git add -A
# 또는
git add .
```

**주의**: `.env` 등 민감 정보는 `.gitignore`에 포함되어 있으므로 `git add .` 해도 추적되지 않습니다.

---

## 4. 커밋 (Commit)

스테이징한 내용을 하나의 버전으로 기록합니다.

```bash
# 메시지와 함께 커밋
git commit -m "feat: URL 전역 중복 체크 추가"

# 여러 줄 메시지 (에디터 열림)
git commit
```

**커밋 메시지 예시**
- `feat: URL 전역 중복 체크 추가`
- `fix: 요약 태스크 UUID 변환 및 Docker Ollama URL 설정`
- `docs: Git 업데이트 매뉴얼 추가`

---

## 5. 원격 저장소로 푸시 (Push)

로컬 커밋을 원격(GitHub 등)에 올립니다.

```bash
# 기본 브랜치(main) 푸시
git push origin main

# 현재 브랜치 푸시 (업스트림이 이미 설정된 경우)
git push
```

**처음 푸시 시 업스트림 설정**
```bash
git push -u origin main
```
이후에는 `git push` 만 해도 됩니다.

---

## 6. 한 번에 진행하는 절차 (요약)

작업을 마친 뒤, 아래 순서로 실행하면 됩니다.

```bash
cd /Users/shsong/mini-servers/aiScrapping

# 1) 상태 확인
git status

# 2) 반영할 파일 스테이징
git add backend/ frontend/ docs/   # 필요한 경로만 지정

# 3) 커밋
git commit -m "feat: 기능 요약 메시지"

# 4) 원격 반영
git push origin main
```

---

## 7. 자주 쓰는 명령어

| 목적 | 명령어 |
|------|--------|
| 변경 파일 확인 | `git status` |
| 스테이징 취소 | `git restore --staged <파일>` |
| 작업 디렉터리 되돌리기 | `git restore <파일>` |
| 최근 커밋 메시지 수정 | `git commit --amend -m "새 메시지"` |
| 원격 최신 내용 가져오기 | `git pull origin main` |
| 커밋 이력 보기 | `git log --oneline -10` |

---

## 8. 주의 사항

- **커밋 전**: `git status` / `git diff` 로 불필요한 파일이 포함되지 않았는지 확인
- **푸시 전**: 팀 작업 시 `git pull origin main` 으로 최신 반영 후 `git push`
- **민감 정보**: `.env`, 비밀키, API 키 등은 절대 커밋하지 않음 (`.gitignore` 확인)

---

이 매뉴얼대로 진행하면 로컬 변경 사항을 Git에 안전하게 업데이트할 수 있습니다.
