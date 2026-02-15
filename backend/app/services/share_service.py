"""
북마크 요약 공유 서비스 (Slack, Notion)
- 인터페이스만 정의. Slack/Notion 세부 구현은 추후 진행.
"""
import logging
from typing import Optional
from app.models.bookmark import Bookmark

logger = logging.getLogger(__name__)


def share_to_slack(bookmark: Bookmark) -> str:
    """
    북마크 요약을 Slack으로 전송.
    세부 구현(Webhook/API 호출)은 추후 진행.
    성공 시 공유한 북마크의 제목을 반환.
    """
    # TODO: Slack Webhook 또는 Web API 연동
    logger.info(f"[share_service] share_to_slack 스텁 - 북마크 제목: {bookmark.title}")
    return bookmark.title or ""


def share_to_notion(bookmark: Bookmark) -> str:
    """
    북마크 요약을 Notion으로 전송.
    세부 구현(Integration API)은 추후 진행.
    성공 시 공유한 북마크의 제목을 반환.
    """
    # TODO: Notion API 연동
    logger.info(f"[share_service] share_to_notion 스텁 - 북마크 제목: {bookmark.title}")
    return bookmark.title or ""
