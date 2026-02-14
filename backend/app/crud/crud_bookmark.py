from typing import Optional, Dict, Union, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import any_, or_, func, and_, text, select, exists, literal
from sqlalchemy.sql import column
from fastapi.encoders import jsonable_encoder
from datetime import datetime
import re
import logging

from app.crud.base import CRUDBase
from app.models.bookmark import Bookmark
from app.schemas.bookmark import BookmarkCreate, BookmarkUpdate

# 로거 설정: 다른 모듈과 동일한 방식으로 설정 (루트 로거의 핸들러 상속)
logger = logging.getLogger(__name__)
# 로거 레벨은 루트 로거에서 상속받음 (DEBUG)
# propagate=True로 설정하여 루트 로거의 핸들러 사용
logger.propagate = True

def split_keyword_by_delimiters(keyword: str) -> List[str]:
    """
    키워드를 구분자(공백, ',', '-', '·')로 분리하여 단어 리스트 반환
    
    Args:
        keyword: 분리할 키워드 문자열
        
    Returns:
        구분자로 분리된 단어 리스트 (빈 문자열 제외)
        
    Examples:
        split_keyword_by_delimiters("AI 코딩") -> ["AI", "코딩"]
        split_keyword_by_delimiters("AI,코딩") -> ["AI", "코딩"]
        split_keyword_by_delimiters("AI-코딩") -> ["AI", "코딩"]
        split_keyword_by_delimiters("AI·코딩") -> ["AI", "코딩"]
        split_keyword_by_delimiters("AI") -> ["AI"]  # 구분자가 없으면 그대로
    """
    if not keyword or not keyword.strip():
        return []
    
    # 구분자: 공백, 쉼표, 하이픈, 중간점(·)
    # 정규식으로 분리: 공백, 쉼표, 하이픈, 중간점 중 하나 이상
    parts = re.split(r'[\s,\-·]+', keyword.strip())
    
    # 빈 문자열 제거 및 공백 제거
    words = [part.strip() for part in parts if part.strip()]
    
    return words

class CRUDBookmark(CRUDBase[Bookmark, BookmarkCreate, BookmarkUpdate]):
    def update(
        self,
        db: Session,
        *,
        db_obj: Bookmark,
        obj_in: Union[BookmarkUpdate, Dict[str, Any]]
    ) -> Bookmark:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        # URL 객체를 문자열로 변환
        if 'url' in update_data and update_data['url']:
            update_data['url'] = str(update_data['url'])
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Bookmark]:
        return db.query(self.model)\
            .filter(Bookmark.user_id == owner_id)\
            .order_by(Bookmark.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def count_by_owner(self, db: Session, *, owner_id: int) -> int:
        return db.query(self.model)\
            .filter(Bookmark.user_id == owner_id)\
            .count()

    def get_multi_by_owner_with_tag(
        self, db: Session, *, owner_id: int, tag: str, skip: int = 0, limit: int = 100
    ) -> List[Bookmark]:
        """태그로 필터링된 북마크 목록 조회 (부분 일치 지원)
        
        단일 키워드로 검색하며, 부분 일치로 검색됨
        예: "AI" 검색 시 "AI", "AI coding", "chatbot AI" 모두 검색
        """
        keyword = tag.strip()
        
        if not keyword:
            # 키워드가 없으면 빈 결과 반환
            return []
        
        # 부분 일치 검색
        query = db.query(self.model)\
            .filter(Bookmark.user_id == owner_id)\
            .filter(Bookmark.tags.isnot(None))\
            .filter(func.array_length(Bookmark.tags, 1) > 0)
        
        # 키워드를 구분자로 분리하여 단어 리스트 생성
        words = split_keyword_by_delimiters(keyword)
        
        if not words:
            # 분리된 단어가 없으면 빈 결과 반환
            return []
        
        logger.info(f"[태그 검색] 키워드: '{keyword}', 분리된 단어: {words}")
        
        # 분리된 단어가 하나면 기존처럼 단일 패턴으로 검색
        # 여러 개면 OR 조건으로 검색
        if len(words) == 1:
            # 단일 단어: 기존 동작 유지
            search_pattern = f'%{words[0]}%'
            logger.info(f"[태그 검색] 단일 단어 패턴: '{search_pattern}'")
            query = query.filter(
                text("EXISTS (SELECT 1 FROM unnest(bookmarks.tags) AS tag WHERE tag LIKE :keyword)")
                .bindparams(keyword=search_pattern)
            )
        else:
            # 여러 단어: OR 조건으로 검색
            # 각 단어에 대해 EXISTS 조건을 생성하고 OR로 결합
            or_conditions = []
            for word_idx, word in enumerate(words):
                search_pattern = f'%{word}%'
                param_name = f'keyword_word_{word_idx}'
                logger.info(f"[태그 검색] 단어[{word_idx}]: '{word}', 패턴: '{search_pattern}'")
                or_conditions.append(
                    text(f"EXISTS (SELECT 1 FROM unnest(bookmarks.tags) AS tag WHERE tag LIKE :{param_name})")
                    .bindparams(**{param_name: search_pattern})
                )
            
            # OR 조건으로 결합
            if or_conditions:
                query = query.filter(or_(*or_conditions))
                logger.info(f"[태그 검색] OR 조건 개수: {len(or_conditions)}")
        
        # 생성된 SQL 확인을 위한 로깅 (INFO 레벨로 변경하여 확실히 기록)
        try:
            from sqlalchemy.dialects import postgresql
            compiled = query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
            sql_str = str(compiled)
            params = compiled.params
            logger.info(f"[태그 검색] 생성된 SQL: {sql_str}")
            logger.info(f"[태그 검색] SQL 파라미터: {params}")
        except Exception as e:
            logger.warning(f"[태그 검색] SQL 로깅 실패: {e}")
            import traceback
            logger.warning(f"[태그 검색] SQL 로깅 실패 상세: {traceback.format_exc()}")
        
        return query\
            .order_by(Bookmark.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def count_by_owner_with_tag(self, db: Session, *, owner_id: int, tag: str) -> int:
        """태그로 필터링된 북마크 개수 조회 (부분 일치 지원)
        
        단일 키워드로 검색하며, 부분 일치로 검색됨
        """
        keyword = tag.strip()
        
        if not keyword:
            # 키워드가 없으면 0 반환
            return 0
        
        # 부분 일치 검색
        query = db.query(self.model)\
            .filter(Bookmark.user_id == owner_id)\
            .filter(Bookmark.tags.isnot(None))\
            .filter(func.array_length(Bookmark.tags, 1) > 0)
        
        # 키워드를 구분자로 분리하여 단어 리스트 생성
        words = split_keyword_by_delimiters(keyword)
        
        if not words:
            # 분리된 단어가 없으면 0 반환
            return 0
        
        logger.info(f"[태그 검색 - Count] 키워드: '{keyword}', 분리된 단어: {words}")
        
        # 분리된 단어가 하나면 기존처럼 단일 패턴으로 검색
        # 여러 개면 OR 조건으로 검색
        if len(words) == 1:
            # 단일 단어: 기존 동작 유지
            search_pattern = f'%{words[0]}%'
            logger.info(f"[태그 검색 - Count] 단일 단어 패턴: '{search_pattern}'")
            query = query.filter(
                text("EXISTS (SELECT 1 FROM unnest(bookmarks.tags) AS tag WHERE tag LIKE :keyword)")
                .bindparams(keyword=search_pattern)
            )
        else:
            # 여러 단어: OR 조건으로 검색
            # 각 단어에 대해 EXISTS 조건을 생성하고 OR로 결합
            or_conditions = []
            for word_idx, word in enumerate(words):
                search_pattern = f'%{word}%'
                param_name = f'keyword_word_{word_idx}'
                logger.info(f"[태그 검색 - Count] 단어[{word_idx}]: '{word}', 패턴: '{search_pattern}'")
                or_conditions.append(
                    text(f"EXISTS (SELECT 1 FROM unnest(bookmarks.tags) AS tag WHERE tag LIKE :{param_name})")
                    .bindparams(**{param_name: search_pattern})
                )
            
            # OR 조건으로 결합
            if or_conditions:
                query = query.filter(or_(*or_conditions))
                logger.info(f"[태그 검색 - Count] OR 조건 개수: {len(or_conditions)}")
        
        # 생성된 SQL 확인을 위한 로깅 (INFO 레벨로 변경하여 확실히 기록)
        try:
            from sqlalchemy.dialects import postgresql
            compiled = query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
            sql_str = str(compiled)
            params = compiled.params
            logger.info(f"[태그 검색 - Count] 생성된 SQL: {sql_str}")
            logger.info(f"[태그 검색 - Count] SQL 파라미터: {params}")
        except Exception as e:
            logger.warning(f"[태그 검색 - Count] SQL 로깅 실패: {e}")
            import traceback
            logger.warning(f"[태그 검색 - Count] SQL 로깅 실패 상세: {traceback.format_exc()}")
        
        return query.count()

    def get_multi_by_owner_with_tags(
        self, db: Session, *, owner_id: int, tags: List[str], skip: int = 0, limit: int = 100
    ) -> List[Bookmark]:
        """여러 태그로 필터링된 북마크 목록 조회 (AND 조건)
        
        여러 태그를 AND 조건으로 검색하며, 각 태그는 부분 일치로 검색됨
        예: tags=["AI", "코딩"] → ("AI" 포함) AND ("코딩" 포함)
        """
        if not tags or len(tags) == 0:
            return []
        
        query = db.query(self.model)\
            .filter(Bookmark.user_id == owner_id)\
            .filter(Bookmark.tags.isnot(None))\
            .filter(func.array_length(Bookmark.tags, 1) > 0)
        
        # 각 태그에 대해 AND 조건으로 필터링
        tag_and_conditions = []
        
        logger.info(f"[다중 태그 검색] 입력 태그: {tags}")
        
        for idx, tag in enumerate(tags):
            if not tag or not tag.strip():
                continue
            
            keyword = tag.strip()
            
            # 키워드를 구분자로 분리하여 단어 리스트 생성
            words = split_keyword_by_delimiters(keyword)
            
            if not words:
                continue
            
            logger.info(f"[다중 태그 검색] 태그[{idx}]: '{keyword}', 분리된 단어: {words}")
            
            # 분리된 단어가 하나면 기존처럼 단일 패턴으로 검색
            # 여러 개면 OR 조건으로 검색한 후, 전체를 AND 조건에 추가
            if len(words) == 1:
                # 단일 단어: 기존 동작 유지
                search_pattern = f'%{words[0]}%'
                param_name = f'keyword_{idx}'
                logger.info(f"[다중 태그 검색] 태그[{idx}] 단일 단어 패턴: '{search_pattern}'")
                tag_and_conditions.append(
                    text(f"EXISTS (SELECT 1 FROM unnest(bookmarks.tags) AS tag WHERE tag LIKE :{param_name})")
                    .bindparams(**{param_name: search_pattern})
                )
            else:
                # 여러 단어: OR 조건으로 검색
                # 각 단어에 대해 EXISTS 조건을 생성하고 OR로 결합
                or_conditions = []
                for word_idx, word in enumerate(words):
                    search_pattern = f'%{word}%'
                    param_name = f'keyword_{idx}_word_{word_idx}'
                    logger.info(f"[다중 태그 검색] 태그[{idx}] 단어[{word_idx}]: '{word}', 패턴: '{search_pattern}'")
                    or_conditions.append(
                        text(f"EXISTS (SELECT 1 FROM unnest(bookmarks.tags) AS tag WHERE tag LIKE :{param_name})")
                        .bindparams(**{param_name: search_pattern})
                    )
                
                # OR 조건으로 결합하여 AND 조건 리스트에 추가
                if or_conditions:
                    tag_and_conditions.append(or_(*or_conditions))
                    logger.info(f"[다중 태그 검색] 태그[{idx}] OR 조건 개수: {len(or_conditions)}")
        
        # 모든 태그 조건을 AND 조건으로 결합
        if tag_and_conditions:
            logger.info(f"[다중 태그 검색] AND 조건 개수: {len(tag_and_conditions)}")
            
            # 생성된 SQL 확인을 위한 로깅
            try:
                from sqlalchemy.dialects import postgresql
                test_query = query.filter(and_(*tag_and_conditions))
                compiled = test_query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
                sql_str = str(compiled)
                params = compiled.params
                logger.info(f"[다중 태그 검색] 생성된 SQL: {sql_str}")
                logger.info(f"[다중 태그 검색] SQL 파라미터: {params}")
            except Exception as e:
                logger.warning(f"[다중 태그 검색] SQL 로깅 실패: {e}")
                import traceback
                logger.warning(f"[다중 태그 검색] SQL 로깅 실패 상세: {traceback.format_exc()}")
            
            query = query.filter(and_(*tag_and_conditions))
        else:
            logger.warning("[다중 태그 검색] 유효한 태그가 없어 빈 결과 반환")
            return []
        
        return query\
            .order_by(Bookmark.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def count_by_owner_with_tags(self, db: Session, *, owner_id: int, tags: List[str]) -> int:
        """여러 태그로 필터링된 북마크 개수 조회 (AND 조건)
        
        여러 태그를 AND 조건으로 검색하며, 각 태그는 부분 일치로 검색됨
        """
        if not tags or len(tags) == 0:
            return 0
        
        query = db.query(self.model)\
            .filter(Bookmark.user_id == owner_id)\
            .filter(Bookmark.tags.isnot(None))\
            .filter(func.array_length(Bookmark.tags, 1) > 0)
        
        # 각 태그에 대해 AND 조건으로 필터링
        tag_and_conditions = []
        
        logger.info(f"[다중 태그 검색 - Count] 입력 태그: {tags}")
        
        for idx, tag in enumerate(tags):
            if not tag or not tag.strip():
                continue
            
            keyword = tag.strip()
            
            # 키워드를 구분자로 분리하여 단어 리스트 생성
            words = split_keyword_by_delimiters(keyword)
            
            if not words:
                continue
            
            logger.info(f"[다중 태그 검색 - Count] 태그[{idx}]: '{keyword}', 분리된 단어: {words}")
            
            # 분리된 단어가 하나면 기존처럼 단일 패턴으로 검색
            # 여러 개면 OR 조건으로 검색한 후, 전체를 AND 조건에 추가
            if len(words) == 1:
                # 단일 단어: 기존 동작 유지
                search_pattern = f'%{words[0]}%'
                param_name = f'keyword_{idx}'
                logger.info(f"[다중 태그 검색 - Count] 태그[{idx}] 단일 단어 패턴: '{search_pattern}'")
                tag_and_conditions.append(
                    text(f"EXISTS (SELECT 1 FROM unnest(bookmarks.tags) AS tag WHERE tag LIKE :{param_name})")
                    .bindparams(**{param_name: search_pattern})
                )
            else:
                # 여러 단어: OR 조건으로 검색
                # 각 단어에 대해 EXISTS 조건을 생성하고 OR로 결합
                or_conditions = []
                for word_idx, word in enumerate(words):
                    search_pattern = f'%{word}%'
                    param_name = f'keyword_{idx}_word_{word_idx}'
                    logger.info(f"[다중 태그 검색 - Count] 태그[{idx}] 단어[{word_idx}]: '{word}', 패턴: '{search_pattern}'")
                    or_conditions.append(
                        text(f"EXISTS (SELECT 1 FROM unnest(bookmarks.tags) AS tag WHERE tag LIKE :{param_name})")
                        .bindparams(**{param_name: search_pattern})
                    )
                
                # OR 조건으로 결합하여 AND 조건 리스트에 추가
                if or_conditions:
                    tag_and_conditions.append(or_(*or_conditions))
                    logger.info(f"[다중 태그 검색 - Count] 태그[{idx}] OR 조건 개수: {len(or_conditions)}")
        
        # 모든 태그 조건을 AND 조건으로 결합
        if tag_and_conditions:
            logger.info(f"[다중 태그 검색 - Count] AND 조건 개수: {len(tag_and_conditions)}")
            
            # 생성된 SQL 확인을 위한 로깅 (INFO 레벨로 변경하여 확실히 기록)
            try:
                from sqlalchemy.dialects import postgresql
                test_query = query.filter(and_(*tag_and_conditions))
                compiled = test_query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
                sql_str = str(compiled)
                params = compiled.params
                logger.info(f"[다중 태그 검색 - Count] 생성된 SQL: {sql_str}")
                logger.info(f"[다중 태그 검색 - Count] SQL 파라미터: {params}")
            except Exception as e:
                logger.warning(f"[다중 태그 검색 - Count] SQL 로깅 실패: {e}")
                import traceback
                logger.warning(f"[다중 태그 검색 - Count] SQL 로깅 실패 상세: {traceback.format_exc()}")
            
            query = query.filter(and_(*tag_and_conditions))
        else:
            logger.warning("[다중 태그 검색 - Count] 유효한 태그가 없어 0 반환")
            return 0
        
        return query.count()

    def increase_read_count(self, db: Session, *, bookmark_id: int) -> Bookmark:
        """북마크 조회수 증가 및 최근 조회일시 업데이트"""
        bookmark = db.query(self.model).filter(self.model.id == bookmark_id).first()
        if bookmark:
            bookmark.read_count = (bookmark.read_count or 0) + 1
            bookmark.last_read_at = datetime.utcnow()
            db.add(bookmark)
            db.commit()
            db.refresh(bookmark)
        return bookmark

bookmark = CRUDBookmark(Bookmark)
