#!/usr/bin/env python3
"""
사용자 계정 추가 스크립트

실행 방법 (backend 디렉터리에서):
  python scripts/add_user.py

또는 (모듈로 실행):
  python -m scripts.add_user

Docker 백엔드 컨테이너에서:
  docker compose exec backend python scripts/add_user.py
"""
import sys
import getpass


def main():
    print("=== 사용자 계정 추가 ===\n")

    try:
        from app.db.session import SessionLocal
        from app.models.user import User
        from app.core.security import get_password_hash
    except ImportError as e:
        print(f"[오류] import 실패: {e}")
        print("  backend 디렉터리에서 실행하세요: python scripts/add_user.py")
        return 1

    # 사용자명 입력
    username = input("사용자명: ").strip()
    if not username:
        print("[오류] 사용자명을 입력하세요.")
        return 1

    # 패스워드 입력 (입력 시 화면에 표시되지 않음)
    password = getpass.getpass("패스워드: ")
    if not password:
        print("[오류] 패스워드를 입력하세요.")
        return 1

    password_confirm = getpass.getpass("패스워드 확인: ")
    if password != password_confirm:
        print("[오류] 패스워드가 일치하지 않습니다.")
        return 1

    # 이메일은 사용자명 기반 기본값 (users 테이블에 email UNIQUE NOT NULL)
    email = f"{username}@local"

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"[오류] 사용자명 '{username}'이(가) 이미 존재합니다.")
            return 1

        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            # @local 충돌 시 다른 접미사 사용
            email = f"{username}+user@local"

        hashed = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"\n[완료] 사용자 '{username}' 계정이 생성되었습니다. (id: {user.id})")
        return 0
    except Exception as e:
        db.rollback()
        print(f"[오류] 계정 생성 실패: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
