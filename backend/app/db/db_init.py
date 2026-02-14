import os
import logging
from datetime import datetime
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.core.security import get_password_hash

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/db_init.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 초기 관리자 계정 설정 (settings에서 가져옴)
ADMIN_USERNAME = settings.ADMIN_USERNAME
ADMIN_EMAIL = settings.ADMIN_EMAIL
ADMIN_PASSWORD = settings.ADMIN_PASSWORD

# bcrypt 해시 생성
ADMIN_PASSWORD_HASH = get_password_hash(ADMIN_PASSWORD) if ADMIN_PASSWORD else None

def get_database_url():
    """
    데이터베이스 연결 URL을 생성하는 함수
    
    Returns:
        str: PostgreSQL 데이터베이스 연결 URL
        
    Note:
        - 환경변수 'AIGROUND_DB_URL'이 설정되어 있으면 해당 값을 사용
        - 없으면 config.py의 settings에서 가져옴
    """
    # AIGROUND_DB_URL이 직접 설정되어 있으면 우선 사용
    if os.getenv('AIGROUND_DB_URL'):
        return os.getenv('AIGROUND_DB_URL')
    
    # config.py의 settings에서 가져옴
    return settings.DATABASE_URL

def create_admin_user(connection):
    """관리자 계정 생성"""
    if not ADMIN_PASSWORD:
        logger.warning("ADMIN_PASSWORD가 설정되지 않아 관리자 계정을 생성하지 않습니다.")
        return
    
    try:
        # 관리자 계정 정보
        admin_data = {
            "username": ADMIN_USERNAME,
            "email": ADMIN_EMAIL,
            "hashed_password": ADMIN_PASSWORD_HASH,
            "is_superuser": True
        }
        
        # 기존 관리자 삭제
        connection.execute(
            text("DELETE FROM users WHERE username = :username"),
            {"username": admin_data["username"]}
        )
        
        # 새 관리자 추가
        connection.execute(
            text("""
                INSERT INTO users (username, email, hashed_password, is_superuser)
                VALUES (:username, :email, :hashed_password, :is_superuser)
            """),
            admin_data
        )
        connection.commit()
        logger.info(f"관리자 계정 생성 완료: {ADMIN_USERNAME}")
        
    except Exception as e:
        logger.error(f"관리자 계정 생성 실패: {str(e)}")
        raise

def init_db():
    """데이터베이스 초기화 함수"""
    start_time = datetime.now()
    logger.info("데이터베이스 초기화 시작")
    
    try:
        database_url = get_database_url()
        # 연결 타임아웃 및 재시도 설정
        # SSL 비활성화 (로컬 네트워크 환경)
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 30,  # 연결 타임아웃 30초로 증가
                "sslmode": "disable",   # SSL 비활성화
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5
            }
        )
        logger.info(f"데이터베이스 연결 시도 중...")
        
        with engine.connect() as connection:
            # 1. 기존 객체 정리
            logger.info("기존 객체 정리 시작")
            cleanup_sql = """
                DROP VIEW IF EXISTS active_bookmarks CASCADE;
                DROP TRIGGER IF EXISTS update_bookmarks_updated_at ON bookmarks CASCADE;
                DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
                DROP TABLE IF EXISTS logs CASCADE;
                DROP TABLE IF EXISTS bookmarks CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
            """
            connection.execute(text(cleanup_sql))
            connection.commit()
            
            # 2. 테이블 생성
            with open(os.path.join(os.path.dirname(__file__), 'init.sql'), 'r') as f:
                connection.execute(text(f.read()))
            connection.commit()
            
            # 3. 관리자 계정 생성
            create_admin_user(connection)
            
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print("\n=== 데이터베이스 초기화 완료 ===")
        print(f"관리자 계정: {ADMIN_USERNAME}")
        print(f"실행 시간: {execution_time:.2f}초")
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 