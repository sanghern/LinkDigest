from fastapi import APIRouter
from app.api.endpoints import auth, bookmarks, bookmarks_public, logs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# 공개용 API (인증 불필요) → GET /api/public/bookmarks/
api_router.include_router(bookmarks_public.router, prefix="/public/bookmarks")
# 인증용 북마크 API
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"]) 