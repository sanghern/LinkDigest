from fastapi import APIRouter
from app.api.endpoints import auth, bookmarks, logs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"]) 