from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.models.log import Log
from app.db.session import SessionLocal
import logging
from app.utils.auth import get_current_user_sync
from app.core.logging import setup_logger
from uuid import UUID
from typing import Optional
from datetime import datetime
import traceback
import uuid

logger = setup_logger(__name__)

def validate_uuid(uuid_string: Optional[str]) -> Optional[UUID]:
    if not uuid_string:
        return None
    try:
        return UUID(uuid_string)
    except ValueError:
        return None

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        API 요청/응답 로깅 미들웨어
        
        Args:
            request: FastAPI Request 객체
            call_next: 다음 미들웨어 또는 엔드포인트
            
        Returns:
            response: FastAPI Response 객체
            
        Note:
            - 모든 API 호출을 DB에 기록
            - 실행 시간 측정
            - 에러 발생 시 에러 정보도 기록
            - 인증된 사용자 ID 저장
        """
        # CORS 프리플라이트 요청은 로깅하지 않음
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # 나머지 요청 로깅
        start_time = time.time()
        
        # 사용자 ID 가져오기 및 UUID 검증
        user_id = None
        db = SessionLocal()
        try:
            if "Authorization" in request.headers:
                try:
                    token = request.headers["Authorization"].split(" ")[1]
                    user = get_current_user_sync(token, db)
                    # UUID 검증 - 유효하지 않으면 None 반환
                    user_id = validate_uuid(str(user.id)) if user else None
                except:
                    pass  # 예외 발생 시 user_id는 None 유지
        finally:
            db.close()
        
        try:
            # API 호출 처리
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 로그 저장 - user_id는 UUID 또는 None
            db = SessionLocal()
            try:
                log = Log(
                    level="INFO",
                    message=f"{request.method} /api{request.url.path.replace('/api', '')}",
                    source="backend",
                    request_path=str(request.url.path),
                    request_method=request.method,
                    response_status=response.status_code,
                    execution_time=process_time,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    user_id=user_id,
                    meta_data={
                        "logger_name": __name__,
                        "function_name": request.url.path.split('/')[-1],
                        "line_number": None,  # 미들웨어에서는 의미 없음
                        "thread_name": None,
                        "process_name": None,
                        "created_timestamp": datetime.utcnow().isoformat(),
                        "query_params": str(request.query_params),
                        "path_params": str(request.path_params),
                        "headers": {k:v for k,v in request.headers.items() if k not in ['authorization']}
                    },
                    trace=None,  # 정상 요청에서는 trace 없음
                    trace_id=uuid.uuid4()  # 요청별 고유 ID 생성
                )
                db.add(log)
                db.commit()
            except Exception as e:
                logger.error(f"로그 저장 실패: {str(e)}")
            finally:
                db.close()
                
            logger.info(
                f"{request.method} {request.url.path}",
                extra={
                    "process_time": process_time,
                    "status_code": response.status_code,
                    "client_host": request.client.host
                }
            )
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # 에러 로그 저장 - user_id는 UUID 또는 None
            db = SessionLocal()
            try:
                log = Log(
                    level="ERROR",
                    message=str(e),
                    source="backend",
                    request_path=str(request.url.path),
                    request_method=request.method,
                    response_status=500,
                    execution_time=process_time,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    user_id=user_id,
                    meta_data={
                        "logger_name": __name__,
                        "function_name": request.url.path.split('/')[-1],
                        "line_number": getattr(e, '__traceback__', None) and e.__traceback__.tb_lineno,
                        "thread_name": None,
                        "process_name": None,
                        "created_timestamp": datetime.utcnow().isoformat(),
                        "error": str(e),
                        "query_params": str(request.query_params),
                        "path_params": str(request.path_params),
                        "headers": {k:v for k,v in request.headers.items() if k not in ['authorization']}
                    },
                    trace=traceback.format_exc(),  # 에러 발생 시 스택 트레이스 저장
                    trace_id=uuid.uuid4()
                )
                db.add(log)
                db.commit()
            except Exception as log_error:
                logger.error(f"에러 로그 저장 실패: {str(log_error)}")
            finally:
                db.close()
                
            raise 