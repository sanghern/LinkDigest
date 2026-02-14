from app.models.log import Log
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from typing import Optional
import logging
import logging.handlers
from pathlib import Path
from app.db.session import get_db, SessionLocal
from app.utils.auth import get_current_user_sync

# 로그 디렉토리 생성
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app.log"

# 로그 포맷 설정 수정
log_format = logging.Formatter(
    '%(asctime)s [%(levelname)s] [user:%(user_id)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 파일 핸들러 설정 (로그 파일 저장용)
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10485760,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.DEBUG)  # 개발/테스트 단계이므로 DEBUG 레벨까지 출력

# 콘솔 핸들러 설정 (터미널 출력용)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.DEBUG)  # 개발/테스트 단계이므로 DEBUG 레벨까지 출력

class CustomLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = getattr(self, 'user_id', None)
        self.timestamp = datetime.utcnow()

class CustomLogger(logging.Logger):
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        if extra is None:
            extra = {}
        if 'user_id' not in extra:
            extra['user_id'] = None
        return CustomLogRecord(name, level, fn, lno, msg, args, exc_info, func, sinfo)

# 커스텀 로거 등록
logging.setLoggerClass(CustomLogger)

class DatabaseHandler(logging.Handler):
    """
    데이터베이스 로그 핸들러
    
    로그 메시지를 데이터베이스에 저장하는 커스텀 핸들러입니다.
    """
    
    def emit(self, record):
        """
        로그 레코드를 DB에 저장
        
        Args:
            record: 로그 레코드 객체
            
        Note:
            - 로그 레벨, 메시지, 타임스탬프 저장
            - 에러 발생 시 트레이스백도 저장
            - 사용자 ID 저장 (가능한 경우)
            - 데이터베이스 연결 실패 시 조용히 실패 (서버 동작에 영향 없음)
        """
        db = None
        try:
            db = SessionLocal()
            
            # 사용자 ID 가져오기 시도
            user_id = getattr(record, 'user_id', None)
            if not user_id and hasattr(record, 'request'):
                try:
                    if "Authorization" in record.request.headers:
                        token = record.request.headers["Authorization"].split(" ")[1]
                        user = get_current_user_sync(token, db)
                        user_id = user.id if user else None
                except:
                    pass

            # 로그 생성
            log = Log(
                level=record.levelname,
                message=record.getMessage(),
                source='backend',
                timestamp=getattr(record, 'timestamp', datetime.utcnow()),
                trace=record.exc_text if record.exc_text else None,
                user_id=user_id,
                meta_data={
                    'logger_name': record.name,
                    'function_name': record.funcName,
                    'line_number': record.lineno,
                    'thread_name': record.threadName,
                    'process_name': record.processName,
                    'created_timestamp': datetime.fromtimestamp(record.created).isoformat()
                }
            )
            
            # 추가 컨텍스트 정보가 있으면 meta_data에 추가
            if hasattr(record, 'request_path'):
                log.request_path = record.request_path
            if hasattr(record, 'request_method'):
                log.request_method = record.request_method
            if hasattr(record, 'response_status'):
                log.response_status = record.response_status
            if hasattr(record, 'execution_time'):
                log.execution_time = record.execution_time
            if hasattr(record, 'ip_address'):
                log.ip_address = record.ip_address
            if hasattr(record, 'user_agent'):
                log.user_agent = record.user_agent

            db.add(log)
            db.commit()
            
        except Exception as e:
            # 데이터베이스 연결 실패는 조용히 무시 (서버 동작에 영향 없음)
            # 디버깅을 위해 첫 번째 실패만 출력
            pass
        finally:
            if db is not None:
                try:
                    db.close()
                except:
                    pass

# DB 핸들러 설정
db_handler = DatabaseHandler()
db_handler.setFormatter(log_format)
db_handler.setLevel(logging.DEBUG)  # 개발/테스트 단계이므로 DEBUG 레벨까지 출력

def setup_logger(name):
    logger = logging.getLogger(name)
    
    # 로그 포맷 수정
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [user:%(user_id)s] %(name)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    
    # 로그 레코드에 user_id가 없을 경우 None으로 처리
    class CustomAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            if 'user_id' not in kwargs.get('extra', {}):
                kwargs.setdefault('extra', {})['user_id'] = None
            return msg, kwargs
    
    return CustomAdapter(logger, {})

def log_api_request(
    level: str,
    message: str,
    source: str,
    request_path: str = None,
    request_method: str = None,
    response_status: int = None,
    execution_time: float = None,
    ip_address: str = None,
    user_agent: str = None,
    trace: str = None,
    meta_data: dict = None
):
    """
    API 요청 로깅 함수
    
    Args:
        level: 로그 레벨 (INFO, WARNING, ERROR)
        message: 로그 메시지
        source: 로그 소스 (frontend/backend)
        request_path: 요청 경로
        request_method: HTTP 메소드
        response_status: HTTP 상태 코드
        execution_time: 실행 시간
        ip_address: 클라이언트 IP
        user_agent: 사용자 에이전트
        trace: 에러 트레이스
        meta_data: 추가 메타데이터
        
    Note:
        - DB와 파일에 동시 저장
        - 에러 발생 시 로깅 실패를 기록
    """
    logger = setup_logger("api")
    
    try:
        # DB에 로그 저장
        log = Log(
            level=level,
            message=message,
            source=source,
            request_path=request_path,
            request_method=request_method,
            response_status=response_status,
            execution_time=execution_time,
            ip_address=ip_address,
            user_agent=user_agent,
            trace=trace,
            meta_data=meta_data
        )
        
        db = SessionLocal()
        try:
            db.add(log)
            db.commit()
        finally:
            db.close()
        
        # 파일과 콘솔에도 로그 출력
        log_message = f"{message} | {request_method} {request_path} | Status: {response_status}"
        if level.upper() == "ERROR":
            logger.error(log_message, exc_info=bool(trace))
        elif level.upper() == "WARNING":
            logger.warning(log_message)
        else:
            logger.info(log_message)
            
    except Exception as e:
        error_msg = f"로그 저장 실패: {str(e)}"
        logger.error(error_msg)

def setup_root_logger():
    """
    루트 로거 설정
    
    Note:
        - 모든 로거의 기본 설정
        - 파일, 콘솔, DB 핸들러 설정
        - 개발/테스트 단계이므로 DEBUG 레벨까지 출력
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 개발/테스트 단계이므로 DEBUG 레벨까지 출력
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 핸들러 추가
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(db_handler)

# 애플리케이션 시작 시 루트 로거 설정
setup_root_logger()

# 로거 사용 예시
def log_with_user(logger, level, message, user_id=None, **kwargs):
    """
    사용자 ID와 함께 로그를 기록하는 헬퍼 함수
    """
    extra = {'user_id': user_id if user_id else 'anonymous', **kwargs}
    if level.upper() == 'ERROR':
        logger.error(message, extra=extra)
    elif level.upper() == 'WARNING':
        logger.warning(message, extra=extra)
    else:
        logger.info(message, extra=extra) 