from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional
import logging
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.bookmark import Bookmark
from app.schemas.bookmark import BookmarkCreate, BookmarkUpdate, BookmarkResponse, BookmarkListResponse, ShareRequest, ShareResponse
from uuid import UUID
from datetime import datetime
from app.models.log import Log
from app.crud.crud_bookmark import bookmark as crud_bookmark
from app.services.scraping_service import ScrapingService
from app.tasks.summary_tasks import submit_summary_task
from app.services.share_service import share_to_slack, share_to_notion
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# 스크래핑 서비스 인스턴스 생성
scraping_service = ScrapingService()

@router.post("/", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    새 북마크 생성 엔드포인트
    
    Args:
        bookmark: 생성할 북마크 데이터 (필수: URL, 선택: 제목, 태그)
        db: 데이터베이스 세션
        current_user: 현재 인증된 사용자
        
    Returns:
        BookmarkResponse: 생성된 북마크 정보
        
    Note:
        - URL 중복 체크
        - 태그 처리
    """
    try:
        url_str = str(bookmark.url).strip()
        if not url_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL을 입력해주세요.",
            )
        # 전체 사용자 기준 URL 중복 체크 (DUPLICATE_URL_CHECK_ENABLED=True일 때만)
        if settings.DUPLICATE_URL_CHECK_ENABLED:
            existing = crud_bookmark.get_by_url(db, url=url_str)
            if existing:
                logger.info(f"북마크 URL 중복 - 사용자: {current_user.username}, URL: {url_str}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 동일한 URL이 저장되어 있습니다.",
                )

        # URL 스크래핑 (보안뉴스 모바일 URL은 scrape 내부에서 데스크톱 URL로 정규화됨)
        scraped_data = scraping_service.scrape(url_str)

        #logger.info(f"스크래핑 결과: {scraped_data}")  # 스크래핑 결과 로깅
        
        # 북마크 데이터 준비
        bookmark_data = bookmark.model_dump()
        bookmark_data['url'] = url_str
        
        # 제목이 없으면 스크래핑한 제목 사용
        if not bookmark_data.get('title'):
            #logger.info(f"스크래핑한 제목 사용: {scraped_data['title']}")
            bookmark_data['title'] = scraped_data['title']
            
        # content는 저장하고 summary는 비동기로 처리
        bookmark_data.update({
            'source_name': scraped_data['source_name'],
            'content': scraped_data['content'],
            'summary': '요약 생성 중...',  # 임시 메시지
            'user_id': current_user.id
        })
        # 요약 모델은 DB 컬럼이 아니므로 저장 전 제거
        summary_model = bookmark_data.pop("summary_model", None) or settings.OLLAMA_MODEL
        if summary_model not in settings.OLLAMA_SUMMARY_MODEL_LIST:
            summary_model = settings.OLLAMA_MODEL
        
        # 북마크 생성
        db_bookmark = Bookmark(**bookmark_data)
        db.add(db_bookmark)
        db.commit()
        db.refresh(db_bookmark)
        
        # 비동기 요약 태스크 실행 (선택된 모델 또는 기본 모델 사용)
        submit_summary_task(str(db_bookmark.id), scraped_data["content"], model=summary_model)
        
        logger.info(f"북마크 생성 완료 - ID: {db_bookmark.id}")
        return db_bookmark
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"북마크 생성 실패: {str(e)}")
        logger.exception("상세 에러:")  # 스택 트레이스 로깅
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"북마크 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/", response_model=BookmarkListResponse)
def get_bookmarks(
    page: int = 1,
    per_page: int = 10,
    tags: Optional[List[str]] = Query(None, description="필터링할 태그/키워드 목록 (AND 조건)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    북마크 목록 조회 (페이지네이션)
    
    Args:
        page: 페이지 번호 (기본값: 1)
        per_page: 페이지당 항목 수 (기본값: 10)
        tags: 필터링할 태그/키워드 목록 (선택사항, AND 조건)
            - 여러 태그를 전달하면 AND 조건으로 검색 (예: tags=AI&tags=코딩)
            - 각 태그 내부에서 공백, '·', ','로 구분된 키워드는 OR 조건으로 검색
            - 각 키워드는 부분 일치로 검색됨 (예: "AI" 검색 시 "AI", "AI coding", "chatbot AI" 모두 검색)
            - 예: tags=["AI 코딩", "Python"] → ("AI" OR "코딩") AND ("Python" OR "Python3")
    """
    skip = (page - 1) * per_page
    
    # 디버깅: tags 파라미터 확인
    #logger.debug(f"[API] get_bookmarks 호출됨 - tags 파라미터: {tags}, 타입: {type(tags)}")
    #logger.debug(f"[API] get_bookmarks - page: {page}, per_page: {per_page}, 사용자: {current_user.username}")
    
    # 태그가 제공된 경우 태그로 필터링
    if tags and len(tags) > 0:
        #logger.info(f"[API] 태그 필터 검색 요청 - 사용자: {current_user.username}, 태그: {tags}, 페이지: {page}")
        
        # 전체 아이템 수 조회 (태그 필터링, AND 조건)
        total = crud_bookmark.count_by_owner_with_tags(
            db=db, 
            owner_id=current_user.id,
            tags=tags
        )
        
        #logger.info(f"[API] 태그 필터 검색 결과 - 총 개수: {total}")
        
        # 페이지 아이템 조회 (태그 필터링, AND 조건)
        bookmarks = crud_bookmark.get_multi_by_owner_with_tags(
            db=db,
            owner_id=current_user.id,
            tags=tags,
            skip=skip,
            limit=per_page
        )
        
        #logger.info(f"[API] 태그 필터 검색 완료 - 반환된 북마크 수: {len(bookmarks)}")
    else:
        # 태그가 없는 경우 일반 조회
        #logger.debug(f"[API] 태그 없음 - 일반 조회 모드")
        # 전체 아이템 수 조회
        total = crud_bookmark.count_by_owner(
            db=db, 
            owner_id=current_user.id
        )
        
        # 페이지 아이템 조회
        bookmarks = crud_bookmark.get_multi_by_owner(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=per_page
        )
    
    return {
        "items": bookmarks,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/summary-models")
def get_summary_models(current_user: User = Depends(get_current_user)):
    """요약에 사용 가능한 모델 목록 반환 (OLLAMA_MODEL_LISTS 기반)."""
    return {"models": settings.OLLAMA_SUMMARY_MODEL_LIST}


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
def read_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bookmark = crud_bookmark.get(db, id=bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark

@router.put("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: UUID,
    bookmark_in: BookmarkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """북마크 정보 업데이트"""
    try:
        #logger.info(f"북마크 수정 시도 - ID: {bookmark_id}, 사용자: {current_user.username}")
        
        # 1. 기존 북마크 조회
        bookmark = crud_bookmark.get(db, id=bookmark_id)
        if not bookmark:
            logger.warning(f"북마크를 찾을 수 없음 - ID: {bookmark_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="북마크를 찾을 수 없습니다."
            )
        
        # 2. 권한 확인
        if bookmark.user_id != current_user.id:
            logger.warning(f"북마크 수정 권한 없음 - ID: {bookmark_id}, 요청 사용자: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 북마크를 수정할 권한이 없습니다."
            )

        # 3. URL 유효성 검사
        if bookmark_in.url:
            try:
                str(bookmark_in.url)  # URL을 문자열로 변환 가능한지 확인
            except Exception:
                logger.error(f"잘못된 URL 형식 - ID: {bookmark_id}, URL: {bookmark_in.url}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="올바른 URL 형식이 아닙니다."
                )

        # 4. 북마크 업데이트
        updated_bookmark = crud_bookmark.update(
            db,
            db_obj=bookmark,
            obj_in=bookmark_in
        )
        
        # 로그 저장
        log_entry = Log(
            level="INFO",
            message=f"북마크 수정 - ID: {bookmark_id}",
            source="backend",
            user_id=current_user.id,
            meta_data={
                "bookmark_id": str(bookmark_id),
                "title": updated_bookmark.title,
                "url": str(updated_bookmark.url)
            }
        )
        
        try:
            db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"로그 저장 실패: {str(e)}")
            # 로그 저장 실패는 북마크 수정 실패로 처리하지 않음
            
        logger.info(f"북마크 수정 성공 - ID: {bookmark_id}")
        return updated_bookmark
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"북마크 수정 실패 - ID: {bookmark_id}, 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"북마크 수정 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """북마크 삭제"""
    logger.info(f"북마크 삭제 시도 - ID: {bookmark_id}, 사용자: {current_user.username}")
    
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        logger.warning(f"북마크를 찾을 수 없음 - ID: {bookmark_id}")
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(bookmark)
    db.commit()
    
    logger.info(f"북마크 삭제 성공 - ID: {bookmark_id}")
    return {"message": "Bookmark deleted successfully"}

@router.post("/{bookmark_id}/increase-read-count")
async def increase_read_count(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"조회수 증가 요청 - 북마크 ID: {bookmark_id}, 사용자: {current_user.username}")
    try:
        bookmark = crud_bookmark.get(db, id=bookmark_id)
        if not bookmark:
            logger.error(f"북마크를 찾을 수 없음 - ID: {bookmark_id}")
            raise HTTPException(status_code=404, detail="Bookmark not found")

        # db와 bookmark_id를 모두 전달
        updated_bookmark = crud_bookmark.increase_read_count(db=db, bookmark_id=bookmark_id)
        logger.info(f"조회수 증가 성공 - 현재 조회수: {updated_bookmark.read_count}")
        return updated_bookmark
    except Exception as e:
        logger.error(f"조회수 증가 실패: {str(e)}")
        raise


@router.post("/{bookmark_id}/share", response_model=ShareResponse)
def share_bookmark(
    bookmark_id: UUID,
    body: ShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """북마크 요약을 Slack 또는 Notion으로 공유. 성공 시 공유한 북마크 제목 반환."""
    bookmark = crud_bookmark.get(db, id=bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    if bookmark.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    try:
        if body.target == "slack":
            title = share_to_slack(bookmark)
        else:
            title = share_to_notion(bookmark)
        return ShareResponse(success=True, title=title or bookmark.title or "")
    except Exception as e:
        logger.exception(f"공유 실패 bookmark_id={bookmark_id} target={body.target}")
        raise HTTPException(status_code=500, detail="공유 처리 중 오류가 발생했습니다.")
