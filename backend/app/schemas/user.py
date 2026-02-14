from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    """기본 사용자 스키마"""
    username: str
    email: str
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str

class UserUpdate(UserBase):
    """사용자 수정 스키마"""
    password: Optional[str] = None

class UserInDBBase(UserBase):
    """DB 사용자 기본 스키마"""
    id: UUID
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True  # SQLAlchemy 모델 -> Pydantic 모델 변환 허용

class User(BaseModel):
    """API 응답용 사용자 스키마"""
    id: str
    username: str

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, db_user):
        """DB 모델을 API 응답 형식으로 변환"""
        return cls(
            id=str(db_user.id),
            username=db_user.username
        ) 