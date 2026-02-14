from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.log import Log
from app.schemas.log import LogCreate, LogResponse, PaginatedLogResponse
import logging
from sqlalchemy import or_
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=LogResponse)
async def create_log(
    *,
    log: LogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LogResponse:
    """
    Create new log entry.
    """
    try:
        # 로그 데이터에 현재 사용자 ID 추가
        log_data = log.dict()
        log_data["user_id"] = current_user.id
        
        new_log = Log(**log_data)
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log
    except Exception as e:
        logger.error(f"로그 저장 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그 저장 중 오류가 발생했습니다."
        )

@router.get("/", response_model=PaginatedLogResponse)
async def get_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        skip = (page - 1) * per_page
        
        # 로그 조회
        logs = db.query(Log).order_by(Log.timestamp.desc())\
                 .offset(skip).limit(per_page).all()
                 
        # 전체 로그 수 조회
        total = db.query(Log).count()
        
        return {
            "items": logs,  # SQLAlchemy 모델이 자동으로 LogResponse로 변환됨
            "total": total,
            "page": page,
            "per_page": per_page
        }
        
    except Exception as e:
        logger.error(f"로그 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그 조회 중 오류가 발생했습니다."
        )

@router.get("/stats")
async def get_log_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """로그 통계 조회"""
    try:
        last_24h = datetime.utcnow() - timedelta(days=1)
        
        stats = {
            "total_logs": db.query(Log).count(),
            "error_count": db.query(Log).filter(Log.level == "ERROR").count(),
            "last_24h": db.query(Log).filter(Log.timestamp >= last_24h).count(),
            "by_level": {
                level: db.query(Log).filter(Log.level == level).count()
                for level in ["INFO", "WARN", "ERROR"]
            },
            "by_source": {
                source: db.query(Log).filter(Log.source == source).count()
                for source in ["frontend", "backend"]
            }
        }
        
        return stats

    except Exception as e:
        logger.error(f"로그 통계 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그 통계 조회 중 오류가 발생했습니다."
        ) 