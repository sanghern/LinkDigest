from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID

class LogBase(BaseModel):
    """기본 로그 스키마"""
    level: str = Field(..., description="로그 레벨 (INFO, WARN, ERROR)")
    message: str = Field(..., description="로그 메시지")
    source: str = Field(..., description="로그 소스 (frontend, backend)")
    request_path: Optional[str] = Field(None, description="요청 경로")
    request_method: Optional[str] = Field(None, description="HTTP 메소드")
    response_status: Optional[int] = Field(None, description="HTTP 상태 코드")
    execution_time: Optional[float] = Field(None, description="실행 시간 (ms)")
    ip_address: Optional[str] = Field(None, description="클라이언트 IP")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="추가 메타데이터")
    user_id: Optional[UUID] = Field(None, description="사용자 ID")

    @validator('level')
    def validate_level(cls, v):
        allowed_levels = ['INFO', 'WARN', 'ERROR']
        if v.upper() not in allowed_levels:
            raise ValueError(f'로그 레벨은 {", ".join(allowed_levels)} 중 하나여야 합니다.')
        return v.upper()

    @validator('source')
    def validate_source(cls, v):
        allowed_sources = ['frontend', 'backend']
        if v.lower() not in allowed_sources:
            raise ValueError(f'로그 소스는 {", ".join(allowed_sources)} 중 하나여야 합니다.')
        return v.lower()

class LogCreate(LogBase):
    """로그 생성 스키마"""
    pass

class LogResponse(LogBase):
    """로그 응답 스키마"""
    id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_id: Optional[UUID] = None
    user_id: Optional[UUID] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda u: str(u)
        }

# 페이지네이션 응답 스키마 추가
class PaginatedLogResponse(BaseModel):
    """페이지네이션된 로그 응답 스키마"""
    items: List[LogResponse]
    total: int
    page: int
    per_page: int

    class Config:
        from_attributes = True 