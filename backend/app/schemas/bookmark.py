from typing import Optional, List, Literal
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from uuid import UUID

class BookmarkBase(BaseModel):
    title: str
    url: HttpUrl
    source_name: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = []

class BookmarkCreate(BaseModel):
    url: HttpUrl  # 필수 입력값
    title: Optional[str] = None  # 선택 입력값
    tags: Optional[List[str]] = []  # 선택 입력값

class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    source_name: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None

class BookmarkInDB(BookmarkBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    read_count: int = 0
    last_read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BookmarkResponse(BaseModel):
    id: UUID
    title: str
    url: str
    summary: Optional[str]
    content: Optional[str]  # content 필드가 있는지 확인
    source_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    user_id: UUID
    tags: Optional[List[str]]
    read_count: int

class BookmarkListResponse(BaseModel):
    items: List[BookmarkResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    class Config:
        from_attributes = True


class ShareRequest(BaseModel):
    target: Literal["slack", "notion"]


class ShareResponse(BaseModel):
    success: bool = True
    title: str
