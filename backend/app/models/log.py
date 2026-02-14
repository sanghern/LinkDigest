from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from .user import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(String(10), nullable=False)  # INFO, WARN, ERROR
    message = Column(Text, nullable=False)
    source = Column(String(50), nullable=False)  # frontend, backend
    request_path = Column(String(255))
    request_method = Column(String(10))
    response_status = Column(Integer)
    execution_time = Column(Float)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    meta_data = Column(JSON)
    trace = Column(Text, nullable=True)  # 에러 스택 트레이스
    trace_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) 