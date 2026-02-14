from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import Session
import logging
import warnings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# bcrypt 버전 경고 무시
warnings.filterwarnings("ignore", category=UserWarning, module="passlib.handlers.bcrypt")

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 인증 스키마 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    사용자 비밀번호 검증 함수
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
        
    Returns:
        bool: 비밀번호 일치 여부
        
    Note:
        - bcrypt로 해시된 비밀번호 검증
        - 보안을 위해 타이밍 어택 방지
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"비밀번호 검증 오류: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    비밀번호 해시 생성 함수
    
    Args:
        password: 평문 비밀번호
        
    Returns:
        str: bcrypt로 해시된 비밀번호
        
    Note:
        - 보안을 위해 bcrypt 알고리즘 사용
        - 자동 솔트 생성
    """
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """사용자 인증 함수"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성 함수
    
    Args:
        data: 토큰에 포함될 데이터
        expires_delta: 토큰 만료 시간
        
    Returns:
        str: 서명된 JWT 토큰
        
    Note:
        - HS256 알고리즘으로 서명
        - 만료 시간 자동 설정
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    """
    JWT 토큰 디코딩 함수
    
    Args:
        token: JWT 토큰
        
    Returns:
        dict: 디코딩된 토큰 데이터
        
    Raises:
        JWTError: 토큰이 유효하지 않은 경우
        
    Note:
        - 토큰 서명 검증
        - 만료 시간 검증
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(OperationalError),
    reraise=True
)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        # 토큰이 없는 경우 처리
        if not token:
            raise credentials_exception
            
        # 토큰 디코딩
        try:
            payload = decode_jwt_token(token)
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
            
        # 사용자 조회
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
            
        # 세션 유효성 검사 추가
        session = db.query(Session).filter(
            Session.token == token,
            Session.is_active == True
        ).first()
        if not session:
            raise credentials_exception
            
        return user
        
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database connection error"
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception 