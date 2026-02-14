from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..models.bookmark import Bookmark
from ..services.scraping_service import generate_summary
import logging
import re
import uuid as uuid_module
from html import unescape

logger = logging.getLogger(__name__)

# 쓰레드 풀 생성
executor = ThreadPoolExecutor(max_workers=3)

def clean_html_tags_from_text(text: str) -> str:
    """
    키워드/분류에서 HTML 태그만 제거하는 함수
    (요약 본문에는 사용하지 않음)
    
    Args:
        text: 정리할 텍스트
        
    Returns:
        HTML 태그가 제거된 텍스트
    """
    if not text:
        return ""
    
    # HTML 태그 제거 (예: <small>, </small>, <span>, </span> 등)
    text = re.sub(r'<[^>]+>', '', text)
    
    # HTML 엔티티 디코딩 (예: &lt; -> <, &gt; -> >)
    text = unescape(text)
    
    # 연속된 공백 정리 (줄바꿈은 유지하지 않음 - 키워드/분류는 한 줄이므로)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_category_keywords(text):
    """
    요약 텍스트에서 분류와 키워드를 추출하는 함수
    다양한 형식을 지원:
    - 📌️ 분류: 값
    - 📌️ **분류**: 값
    - 📌 키워드: 값
    - 📌 **키워드**: 값
    """
    # 분류 추출 - 다양한 형식 지원
    # 실제 형식: 📌️ **분류**: 블로그\n 또는 📌️ 분류: 블로그\n
    category_patterns = [
        r'📌️\s*\*\*분류\*\*:\s*([^\n]+?)(?:\s*\n|\s+📌|$)',
        r'📌️\s*분류:\s*([^\n]+?)(?:\s*\n|\s+📌|$)',
        r'📌️\s*\*\*분류\*\*\s+([^\n]+?)(?:\s*\n|\s+📌|$)',
        r'📌️\s*분류\s+([^\n]+?)(?:\s*\n|\s+📌|$)',
    ]
    
    catergory = ""
    for pattern in category_patterns:
        category_match = re.search(pattern, text, re.MULTILINE)
        if category_match:
            catergory = category_match.group(1).strip().replace('*', '')
            break
    
    # 키워드 추출 - 다양한 형식 지원
    # 실제 형식: 📌 **키워드**: Docker, ...\n 또는 📌 키워드: Docker, ...\n
    keyword_patterns = [
        r'📌\s*\*\*키워드\*\*:\s*([^\n]+?)(?:\s*\n|$)',
        r'📌\s*키워드:\s*([^\n]+?)(?:\s*\n|$)',
        r'📌\s*\*\*키워드\*\*\s+([^\n]+?)(?:\s*\n|$)',
        r'📌\s*키워드\s+([^\n]+?)(?:\s*\n|$)',
    ]
    
    keywords = ""
    for pattern in keyword_patterns:
        keyword_match = re.search(pattern, text, re.MULTILINE)
        if keyword_match:
            keywords = keyword_match.group(1).strip().replace('*', '')
            break
    
    # 앞뒤 공백 한번 더 제거
    catergory = catergory.strip()
    keywords = keywords.strip()
    
    return catergory, keywords

def update_bookmark_summary(bookmark_id: str, content: str):
    """쓰레드에서 북마크 요약을 생성하고 업데이트하는 함수"""
    db = None
    try:
        # Bookmark.id는 UUID 타입이므로 문자열을 UUID로 변환 (조회 실패 방지)
        try:
            bid = uuid_module.UUID(bookmark_id) if isinstance(bookmark_id, str) else bookmark_id
        except (ValueError, TypeError) as e:
            logger.error(f"요약 태스크 bookmark_id 변환 실패: bookmark_id={bookmark_id!r}, 오류: {e}")
            return

        # 새로운 DB 세션 생성
        db = SessionLocal()

        # DB에서 북마크 조회 (UUID로 조회)
        bookmark = db.query(Bookmark).filter(Bookmark.id == bid).first()
        if not bookmark:
            logger.warning(f"요약 업데이트할 북마크를 찾을 수 없음: id={bid}")
            return

        # OpenAI 요약 생성
        summary = generate_summary(content)

        # 요약 생성 실패 시 오류 문구를 DB에 저장하지 않음 (기존 '요약 생성 중...' 유지)
        if not summary or not summary.strip():
            logger.warning(f"요약 생성 실패 - 북마크 ID: {bid}, summary 컬럼은 갱신하지 않음")
            return

        catergory, keywords = extract_category_keywords(summary)
        logger.info(f"분류: {catergory}, 키워드: {keywords}")

        # DB 업데이트 (성공한 경우만)
        bookmark.summary = summary
        bookmark.catergory = catergory
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
            bookmark.tags = keyword_list
        else:
            bookmark.tags = []
        db.commit()
        db.refresh(bookmark)
        logger.info(f"북마크 요약 업데이트 완료 - ID: {bid}")
    except Exception as e:
        logger.error(f"북마크 요약 업데이트 실패: {str(e)}")
        logger.exception("상세:")
    finally:
        if db:
            db.close()

def submit_summary_task(bookmark_id: str, content: str):
    """요약 태스크를 쓰레드 풀에 제출"""
    return executor.submit(update_bookmark_summary, bookmark_id, content) 