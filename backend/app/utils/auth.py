from sqlalchemy.orm import Session
from app.core.security import decode_jwt_token
from app.models.user import User
from app.models.session import Session as DbSession

def get_current_user_sync(token: str, db: Session) -> User:
    """
    동기 방식으로 현재 사용자 정보 조회
    
    Args:
        token: JWT 토큰
        db: 데이터베이스 세션
        
    Returns:
        User: 사용자 정보
        
    Raises:
        ValueError: 토큰이 유효하지 않은 경우
    """
    try:
        # 토큰 디코딩
        payload = decode_jwt_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise ValueError("Invalid token")

        # 세션 확인
        session = db.query(DbSession)\
            .filter(
                DbSession.token == token,
                DbSession.is_active == True
            ).first()
        if not session:
            raise ValueError("Invalid or expired session")

        # 사용자 조회
        user = db.query(User)\
            .filter(User.username == username)\
            .first()
        if user is None:
            raise ValueError("User not found")

        return user

    except Exception as e:
        raise ValueError(f"Token validation failed: {str(e)}") 