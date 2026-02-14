from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from app.db.session import engine
from app.models import Base
from app.middleware.logging import LoggingMiddleware
from app.core.logging import setup_root_logger
from datetime import datetime
import logging

# 로깅 설정 초기화
setup_root_logger()
logger = logging.getLogger(__name__)

# Create database tables (연결 실패 시에도 서버 시작 가능하도록 예외 처리)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("데이터베이스 테이블 생성 완료")
except Exception as e:
    logger.warning(f"데이터베이스 테이블 생성 실패 (서버는 계속 시작됩니다): {str(e)}")
    logger.warning("데이터베이스 연결이 가능해지면 테이블이 자동으로 생성됩니다.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="LinkDigest API - 북마크 관리 및 AI 요약 서비스",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",  # Swagger UI 경로
    redoc_url=f"{settings.API_V1_STR}/redoc"  # ReDoc 경로
)

# CORS 미들웨어 설정 수정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 미들웨어는 CORS 미들웨어 이후에 추가
app.add_middleware(LoggingMiddleware)

# API 라우터
app.include_router(api_router, prefix=settings.API_V1_STR)

# CORS 디버깅 미들웨어 (디버그 모드에서만 활성화)
if settings.DEBUG:
    @app.middleware("http")
    async def debug_cors(request, call_next):
        logger.debug(f"Incoming request from origin: {request.headers.get('origin')}")
        response = await call_next(request)
        logger.debug(f"Response headers: {dict(response.headers)}")
        return response

@app.get("/")
async def root():
    """루트 경로 - API 정보 및 문서 링크 제공"""
    return {
        "message": "Welcome to LinkDigest API",
        "version": "1.0.0",
        "docs": {
            "swagger_ui": f"{settings.API_V1_STR}/docs",
            "redoc": f"{settings.API_V1_STR}/redoc",
            "openapi_json": f"{settings.API_V1_STR}/openapi.json"
        },
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "bookmarks": f"{settings.API_V1_STR}/bookmarks",
            "logs": f"{settings.API_V1_STR}/logs"
        }
    }

@app.get(settings.API_V1_STR)
async def api_root():
    """API 루트 경로 - API 문서로 리다이렉트"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok", "timestamp": datetime.utcnow()} 