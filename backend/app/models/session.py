from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import uuid

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    user_agent = Column(String(255))
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)

    # User 모델과의 관계 정의 (문자열로 참조)
    user = relationship("User", back_populates="sessions") 