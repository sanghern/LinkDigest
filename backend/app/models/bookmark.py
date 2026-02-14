from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from .user import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    source_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    is_deleted = Column(Boolean, default=False)
    tags = Column(ARRAY(String))
    catergory = Column(String)
    read_count = Column(Integer, default=0, nullable=False) 