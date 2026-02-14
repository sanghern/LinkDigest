from typing import Optional
from pydantic import BaseModel
from app.schemas.user import User

class Token(BaseModel):
    """토큰 스키마"""
    access_token: str
    token_type: str
    user: User  # User 스키마 참조

class TokenPayload(BaseModel):
    """토큰 페이로드 스키마"""
    sub: Optional[str] = None  # username
    exp: Optional[int] = None  # 만료시간 