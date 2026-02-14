#!/usr/bin/env bash
#
# Git 업데이트 스크립트
# 사용법:
#   ./scripts/git-update.sh "작업 내용(커밋 메시지)"
#   ./scripts/git-update.sh "feat: URL 중복 체크" -p   # 커밋 후 푸시
#   ./scripts/git-update.sh                            # 메시지 입력 프롬프트
#

set -e

# 스크립트 위치 기준으로 프로젝트 루트로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# 푸시 여부
PUSH=false
MSG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--push)
      PUSH=true
      shift
      ;;
    -*)
      echo "알 수 없는 옵션: $1" >&2
      echo "사용법: $0 [메시지] [-p|--push]" >&2
      exit 1
      ;;
    *)
      if [[ -z "$MSG" ]]; then
        MSG="$1"
      else
        MSG="$MSG $1"
      fi
      shift
      ;;
  esac
done

# 작업 내용(커밋 메시지) 입력
if [[ -z "$MSG" ]]; then
  echo "작업 내용(커밋 메시지)을 입력하세요:"
  read -r MSG
  if [[ -z "$MSG" ]]; then
    echo "메시지가 비어 있어 중단합니다." >&2
    exit 1
  fi
fi

echo "=========================================="
echo "프로젝트: $ROOT_DIR"
echo "커밋 메시지: $MSG"
echo "푸시: $PUSH"
echo "=========================================="

# 1) 상태 확인
echo ""
echo "[1/4] 변경 사항 확인..."
git status -s
if [[ -z $(git status -s) ]]; then
  echo "커밋할 변경 사항이 없습니다."
  exit 0
fi

# 2) 스테이징
echo ""
echo "[2/4] 스테이징 (git add -A)..."
git add -A

# 3) 커밋
echo ""
echo "[3/4] 커밋..."
git commit -m "$MSG"

# 4) 푸시 (옵션)
echo ""
echo "[4/4] 푸시..."
if $PUSH; then
  git push origin main
  echo "원격 저장소에 푸시했습니다."
else
  echo "푸시하지 않았습니다. 푸시하려면: git push origin main"
  echo "또는 다음에 -p 옵션으로 실행: $0 \"메시지\" -p"
fi

echo ""
echo "완료."
