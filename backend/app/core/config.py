from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache
from urllib.parse import quote_plus
import os

class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    
    Pydantic Settings는 다음 순서로 값을 로드합니다:
    1. 시스템 환경 변수 (최우선)
    2. .env 파일의 값
    3. 클래스 필드의 기본값 (fallback)
    
    모든 설정값은 .env 파일에서 관리하며, 
    .env 파일에 값이 없을 때만 기본값을 사용합니다.
    """
    
    # 프로젝트 기본 설정
    PROJECT_NAME: str = "LinkDigest"
    API_V1_STR: str = "/api"
    
    # 데이터베이스 설정
    # 방법 1: 전체 URL 직접 설정 (우선순위 높음)
    # .env 파일에서 AIGROUND_DB_URL을 설정하면 이 값을 사용
    AIGROUND_DB_URL: str = ""
    
    # 방법 2: 개별 설정값으로 구성
    # .env 파일에서 다음 값들을 설정 (없으면 기본값 사용)
    DB_USER: str = "aiground"  # .env의 DB_USER 값이 있으면 우선 사용
    DB_PASSWORD: str = ""  # .env의 DB_PASSWORD 값이 있으면 우선 사용
    DB_HOST: str = "192.168.7.89"  # .env의 DB_HOST 값이 있으면 우선 사용
    DB_PORT: str = "5432"  # .env의 DB_PORT 값이 있으면 우선 사용
    DB_NAME: str = "aiscrap"  # .env의 DB_NAME 값이 있으면 우선 사용
    DB_SSLMODE: str = "disable"  # .env의 DB_SSLMODE 값이 있으면 우선 사용
    
    def get_database_url(self) -> str:
        """
        데이터베이스 연결 URL을 생성하는 함수
        
        Returns:
            str: PostgreSQL 데이터베이스 연결 URL
        """
        # AIGROUND_DB_URL이 직접 설정되어 있으면 우선 사용
        if self.AIGROUND_DB_URL:
            return self.AIGROUND_DB_URL
        
        # 개별 설정값으로 URL 구성
        encoded_password = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        if self.DB_PASSWORD:
            return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"
        else:
            return f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"
    
    @property
    def DATABASE_URL(self) -> str:
        """데이터베이스 연결 URL (property로 접근)"""
        return self.get_database_url()
    
    # 보안 설정
    SECRET_KEY: str = ""  # JWT 토큰 암호화 키 (환경 변수 필수)
    ALGORITHM: str = "HS256"  # JWT 암호화 알고리즘
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 토큰 만료 시간(분)
    
    # CORS 설정 (쉼표로 구분된 문자열을 리스트로 변환)
    BACKEND_CORS_ORIGINS_STR: str = "http://localhost:3000,http://192.168.7.88:3000,http://192.168.7.88:3001,http://100.89.194.30:3000,http://digest.aiground.ai,https://linkdigest.aiground.ai"
    
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """CORS 허용 오리진 리스트"""
        return [
            origin.strip() 
            for origin in self.BACKEND_CORS_ORIGINS_STR.split(",")
            if origin.strip()
        ]

    # OpenAI 설정
    OPENAI_API_KEY: str = ""
    
    # Ollama 설정
    OLLAMA_API_URL: str = "http://localhost:11434/api/chat"
    OLLAMA_MODEL: str = "gpt-oss:120b-cloud"
    TRANSLATE_MODEL: str = "translategemma:4b"
    
    # 초기 관리자 계정 설정 (db_init.py에서 사용)
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = ""
    
    # 디버그 모드 설정
    DEBUG: bool = False  # 프로덕션에서는 False로 설정

    # URL 중복 등록 체크 (on: 중복 시 409 반환, off: 체크 생략)
    DUPLICATE_URL_CHECK_ENABLED: bool = True

    model_config = SettingsConfigDict(
        case_sensitive=True,  # 대소문자 구분
        env_file=".env",  # 환경변수 파일 경로
        extra="ignore"  # 정의되지 않은 필드는 무시
    )

@lru_cache()
def get_settings():
    """
    설정 객체를 생성하고 캐시하는 함수
    
    Returns:
        Settings: 애플리케이션 설정 객체
        
    Note:
        - @lru_cache 데코레이터로 설정 객체를 캐시
        - 성능 최적화를 위해 재사용
    """
    return Settings()

settings = get_settings()  # 전역 설정 객체 