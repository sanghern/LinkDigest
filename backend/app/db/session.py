from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 데이터베이스 URL은 config.py의 settings에서 가져옴
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 데이터베이스 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # settings.SQLALCHEMY_DATABASE_URI 대신 직접 URL 사용
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=3600,   # 1시간마다 연결 재생성
    connect_args={
        "connect_timeout": 30,  # 연결 타임아웃 30초로 증가
        "sslmode": "disable",   # SSL 비활성화 (로컬 네트워크)
        "keepalives": 1,       # TCP keepalive 활성화
        "keepalives_idle": 30, # 30초 동안 유휴 상태면
        "keepalives_interval": 10, # 10초 간격으로
        "keepalives_count": 5   # 5번 시도
    }
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    데이터베이스 세션 생성 함수
    
    Yields:
        Session: 데이터베이스 세션
        
    Note:
        - with 문 또는 FastAPI의 Depends와 함께 사용
        - 세션은 자동으로 닫힘
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 