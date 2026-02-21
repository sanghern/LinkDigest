"""
공개용 북마크 API (인증 불필요).
- is_public=True인 북마크 목록/단건 조회
"""
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.bookmark import BookmarkListResponse, BookmarkResponse
from app.crud.crud_bookmark import bookmark as crud_bookmark

router = APIRouter(tags=["bookmarks-public"])


@router.get("/", response_model=BookmarkListResponse)
def get_public_bookmarks(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """비로그인 사용자용: is_public=True인 북마크 목록만 조회 (인증 불필요)."""
    skip = (page - 1) * per_page
    total = crud_bookmark.count_public(db=db)
    bookmarks = crud_bookmark.get_multi_public(db=db, skip=skip, limit=per_page)
    return {
        "items": bookmarks,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page else 0,
    }


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
def get_public_bookmark(bookmark_id: UUID, db: Session = Depends(get_db)):
    """비로그인 사용자용: is_public=True인 북마크 단건 조회 (인증 불필요)."""
    bookmark = crud_bookmark.get_public_by_id(db=db, bookmark_id=bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Not Found")
    return bookmark
