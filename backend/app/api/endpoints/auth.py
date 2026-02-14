from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Optional
from app.core.security import (
    create_access_token,
    get_current_user,
    authenticate_user,
    oauth2_scheme
)
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.token import Token
from app.schemas.user import User
from app.core.logging import setup_logger
from uuid import UUID
from app.models.log import Log
from app.models.session import Session  # Session 모델 import 추가
from sqlalchemy.exc import IntegrityError
from jose import jwt

router = APIRouter()
logger = setup_logger(__name__)

def validate_uuid(uuid_string: Optional[str]) -> Optional[UUID]:
    """UUID 문자열을 검증하고 변환하는 함수"""
    if not uuid_string:
        return None
    try:
        return UUID(uuid_string)
    except ValueError:
        return None

@router.post("/login", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """로그인 처리 및 토큰 발급"""
    try:
        # 1. 사용자 인증
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"로그인 실패 - 사용자: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # 2. 기존 세션 삭제
            db.query(Session).filter(
                Session.user_id == user.id,
                Session.is_active == True
            ).delete()
            
            # 3. 토큰 생성
            access_token = create_access_token(
                data={"sub": user.username},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            # 4. 새 세션 생성
            new_session = Session(
                user_id=user.id,
                token=access_token,  # 토큰 저장
                expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                user_agent=request.headers.get("user-agent"),
                ip_address=request.client.host if request.client else None,
                is_active=True
            )
            
            db.add(new_session)
            db.commit()
            
            # 5. 로그 저장
            log_entry = Log(
                level="INFO",
                message=f"로그인 성공 - 사용자: {user.username}",
                source="backend",
                user_id=user.id,
                meta_data={
                    "session_id": str(new_session.id),
                    "ip": request.client.host,
                    "user_agent": request.headers.get("user-agent")
                }
            )
            db.add(log_entry)
            db.commit()

            logger.info(f"로그인 성공 - 사용자: {user.username}-{user.id}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user.id),
                    "username": user.username
                }
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"세션/로그 처리 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="로그인 처리 중 오류가 발생했습니다."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그인 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다."
        )

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: UserModel = Depends(get_current_user)
) -> Any:
    """현재 로그인한 사용자 정보 조회"""
    # UserModel을 User 스키마 형식으로 변환
    return {
        "id": str(current_user.id),
        "username": current_user.username
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Any:
    """로그아웃 처리"""
    try:
        # 1. 현재 세션 찾기
        result = db.query(Session).filter(
            Session.token == token,
            Session.user_id == current_user.id,
            Session.is_active == True
        ).delete()
        
        if result > 0:
            # 2. 로그 저장
            log_entry = Log(
                level="INFO",
                message=f"로그아웃 - 사용자: {current_user.username}",
                source="backend",
                user_id=current_user.id,
                meta_data={
                    "user_id": str(current_user.id),
                    "username": current_user.username
                }
            )
            db.add(log_entry)
            
            try:
                db.commit()
                logger.info(f"로그아웃 성공 - 사용자: {current_user.username}")
                return {"message": "Successfully logged out"}
            except Exception as e:
                db.rollback()
                logger.error(f"로그아웃 로그 저장 실패: {str(e)}")
                raise
                
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
            
    except Exception as e:
        logger.error(f"로그아웃 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다."
        ) 