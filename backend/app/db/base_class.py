from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    SQLAlchemy 모델의 기본 클래스
    
    모든 모델 클래스가 상속받는 기본 클래스입니다.
    테이블 이름을 자동으로 생성하고 공통 속성을 제공합니다.
    """
    id: Any
    __name__: str
    
    # 클래스 이름을 소문자로 변환하여 테이블 이름으로 사용
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() 