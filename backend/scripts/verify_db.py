#!/usr/bin/env python3
"""
외부 PostgreSQL 연결 검증 스크립트
Docker 백엔드 컨테이너에서: docker compose exec backend python scripts/verify_db.py
로컬에서: backend 디렉터리에서 python scripts/verify_db.py (PYTHONPATH에 app 필요)
"""
import sys

def main():
    print("=== PostgreSQL 연결 검증 ===")
    try:
        from app.core.config import settings
        from app.db.session import engine
        from sqlalchemy import text
    except ImportError as e:
        print(f"[FAIL] import 오류: {e}")
        print("  backend 디렉터리에서 실행하거나, Docker: docker compose exec backend python scripts/verify_db.py")
        return 1

    # 설정값 출력 (비밀번호 제외)
    print(f"  DB_HOST: {settings.DB_HOST}")
    print(f"  DB_PORT: {settings.DB_PORT}")
    print(f"  DB_NAME: {settings.DB_NAME}")
    print(f"  DB_USER: {settings.DB_USER}")
    print("  연결 시도 중...")

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] DB 연결 성공 (SELECT 1)")
    except Exception as e:
        print(f"[FAIL] DB 연결 실패: {e}")
        return 1

    # users 테이블 존재 시 행 수 (인증 검증용)
    try:
        from app.models.user import User
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            count = db.query(User).count()
            print(f"[OK] users 테이블 조회 성공, 사용자 수: {count}")
            if count == 0:
                print("  [참고] 사용자가 없으면 로그인 불가. app.db.db_init 또는 관리자 생성 필요.")
        finally:
            db.close()
    except Exception as e:
        print(f"[WARN] users 조회 실패 (테이블 없을 수 있음): {e}")

    print("=== 검증 완료 ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
