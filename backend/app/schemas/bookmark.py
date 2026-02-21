from typing import Optional, List, Literal
from pydantic import BaseModel, HttpUrl, model_validator
from datetime import datetime
from uuid import UUID

class BookmarkBase(BaseModel):
    title: str
    url: HttpUrl
    source_name: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = []

class BookmarkCreate(BaseModel):
    url: Optional[HttpUrl] = None  # URL 입력 시 사용 (컨텐츠 직접 입력 시 생략 가능)
    content: Optional[str] = None  # 요약할 컨텐츠 직접 입력 (URL 미입력 시 사용)
    title: Optional[str] = None  # 선택 입력값 (컨텐츠만 입력 시 제목 없으면 본문 첫 줄 사용)
    tags: Optional[List[str]] = []  # 선택 입력값
    summary_model: Optional[str] = None  # 요약에 사용할 모델 (미지정 시 기본 모델 사용)

    @model_validator(mode="after")
    def url_or_content_required(self):
        has_url = self.url is not None and str(self.url).strip() != ""
        has_content = self.content is not None and self.content.strip() != ""
        if not has_url and not has_content:
            raise ValueError("URL 또는 요약할 컨텐츠를 입력해주세요.")
        return self

class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None  # 빈 문자열 허용(URL 미등록 북마크 수정용)
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
    is_public: Optional[bool] = False

class BookmarkListResponse(BaseModel):
    items: List[BookmarkResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    class Config:
        from_attributes = True


class ShareRequest(BaseModel):
    target: Literal["slack", "notion", "users"]
    public: Optional[bool] = None  # target=users일 때만 사용. True=공개, False=비공개. 생략 시 True


class ShareResponse(BaseModel):
    success: bool = True
    title: str
