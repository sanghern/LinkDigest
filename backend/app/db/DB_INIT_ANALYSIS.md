# 데이터베이스 초기화 분석 문서

## 개요

이 문서는 `backend/app/db` 디렉토리의 데이터베이스 초기화 과정을 상세히 분석합니다.

## 디렉토리 구조

```
backend/app/db/
├── session.py          # 데이터베이스 연결 및 세션 관리
├── base.py             # 모델 Base 클래스 통합
├── base_class.py        # SQLAlchemy Base 클래스 정의
├── db_init.py           # 데이터베이스 초기화 스크립트
├── init_script.py       # 초기화 스크립트 실행 래퍼
└── init.sql             # SQL 스크립트 (테이블 생성)
```

## 파일별 역할 분석

### 1. `session.py` - 데이터베이스 연결 관리

**주요 기능:**
- PostgreSQL 데이터베이스 연결 설정
- SQLAlchemy 엔진 및 세션 팩토리 생성
- 데이터베이스 세션 생성 함수 제공

**핵심 코드:**
```python
# 데이터베이스 연결 URL
SQLALCHEMY_DATABASE_URL = "postgresql://aiground:{비밀번호}@192.168.7.89:5432/aiscrap"

# 엔진 생성 (연결 풀 설정 포함)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,      # 연결 상태 확인
    pool_recycle=3600,       # 1시간마다 연결 재생성
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**연결 풀 설정:**
- `pool_pre_ping=True`: 연결 전 상태 확인 (끊어진 연결 감지)
- `pool_recycle=3600`: 1시간마다 연결 재생성 (데이터베이스 타임아웃 방지)
- `connect_timeout=10`: 연결 타임아웃 10초
- `keepalives`: TCP keepalive 설정으로 연결 유지

**세션 생성 함수:**
```python
def get_db():
    """FastAPI의 Depends와 함께 사용되는 세션 생성 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. `base_class.py` - Base 클래스 정의

**역할:**
- SQLAlchemy의 `as_declarative()` 데코레이터를 사용한 Base 클래스
- 모든 모델이 상속받는 기본 클래스
- 테이블 이름 자동 생성 (클래스 이름을 소문자로 변환)

**코드:**
```python
@as_declarative()
class Base:
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
```

### 3. `base.py` - 모델 통합

**역할:**
- 모든 모델을 import하여 Base에 등록
- `Base.metadata`에 모든 테이블 정보가 포함됨

**코드:**
```python
from app.db.base_class import Base
from app.models.user import User
from app.models.session import Session
from app.models.bookmark import Bookmark
from app.models.log import Log
```

**중요:** 모델을 import하면 자동으로 `Base.metadata`에 등록됩니다.

### 4. `init.sql` - SQL 스크립트

**역할:**
- 데이터베이스 스키마 정의
- 테이블, 인덱스, 트리거, 함수, 뷰 생성

**주요 내용:**

#### 4.1 확장(Extensions) 활성화
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID 생성 함수
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- 텍스트 검색 (GIN 인덱스용)
```

#### 4.2 테이블 생성

**users 테이블:**
- `id`: UUID (Primary Key)
- `username`: VARCHAR(50), UNIQUE
- `email`: VARCHAR(100), UNIQUE
- `hashed_password`: VARCHAR(255)
- `created_at`, `last_login`: TIMESTAMP
- `is_active`, `is_superuser`: BOOLEAN

**bookmarks 테이블:**
- `id`: UUID (Primary Key)
- `title`: VARCHAR(255)
- `url`: TEXT
- `content`, `summary`: TEXT
- `source_name`: VARCHAR(100)
- `created_at`, `updated_at`: TIMESTAMP
- `user_id`: UUID (Foreign Key → users.id, CASCADE DELETE)
- `is_deleted`: BOOLEAN
- `tags`: TEXT[] (배열)
- `read_count`: INTEGER

**logs 테이블:**
- `id`: UUID (Primary Key)
- `level`: VARCHAR(10) (INFO, WARN, ERROR)
- `message`: TEXT
- `source`: VARCHAR(50) (frontend, backend)
- `timestamp`: TIMESTAMP
- `trace`: TEXT (에러 스택 트레이스)
- `request_path`, `request_method`: HTTP 요청 정보
- `response_status`: INTEGER
- `execution_time`: FLOAT
- `ip_address`, `user_agent`: 클라이언트 정보
- `meta_data`: JSONB (추가 메타데이터)
- `trace_id`: UUID
- `user_id`: UUID (Foreign Key → users.id, SET NULL on DELETE)

**sessions 테이블:**
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → users.id, CASCADE DELETE)
- `token`: TEXT, UNIQUE
- `created_at`, `expires_at`: TIMESTAMP
- `is_active`: BOOLEAN
- `user_agent`, `ip_address`: 클라이언트 정보

#### 4.3 인덱스 생성

**성능 최적화를 위한 인덱스:**
- `idx_users_username`, `idx_users_email`: 사용자 검색
- `idx_bookmarks_user_id`: 사용자별 북마크 조회
- `idx_bookmarks_created_at`: 날짜순 정렬
- `idx_bookmarks_url`, `idx_bookmarks_title`: 검색
- `idx_bookmarks_tags`: GIN 인덱스 (배열 검색)
- `idx_logs_timestamp`: 시간순 정렬
- `idx_logs_level`, `idx_logs_source`: 필터링
- `idx_logs_trace_id`: 트레이스 추적
- `idx_logs_meta_data`: GIN 인덱스 (JSONB 검색)
- `idx_sessions_user_id`, `idx_sessions_token`: 세션 조회

#### 4.4 트리거 및 함수

**자동 업데이트 트리거:**
```sql
CREATE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_bookmarks_updated_at
    BEFORE UPDATE ON bookmarks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

북마크 업데이트 시 `updated_at` 필드가 자동으로 갱신됩니다.

#### 4.5 뷰 생성

**active_bookmarks 뷰:**
```sql
CREATE VIEW active_bookmarks AS
SELECT 
    b.*,
    u.username as owner_username
FROM bookmarks b
JOIN users u ON b.user_id = u.id
WHERE NOT b.is_deleted;
```

삭제되지 않은 북마크와 소유자 정보를 함께 조회하는 뷰입니다.

### 5. `db_init.py` - 초기화 스크립트

**역할:**
- 데이터베이스 초기화 프로세스 실행
- 기존 테이블 정리 및 재생성
- 초기 관리자 계정 생성

**초기화 프로세스:**

#### 5.1 단계별 실행 순서

1. **데이터베이스 연결**
   ```python
   database_url = get_database_url()
   engine = create_engine(database_url)
   ```

2. **기존 객체 정리**
   ```python
   cleanup_sql = """
       DROP VIEW IF EXISTS active_bookmarks CASCADE;
       DROP TRIGGER IF EXISTS update_bookmarks_updated_at ON bookmarks CASCADE;
       DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
       DROP TABLE IF EXISTS logs CASCADE;
       DROP TABLE IF EXISTS bookmarks CASCADE;
       DROP TABLE IF EXISTS users CASCADE;
   """
   ```
   - CASCADE 옵션으로 의존성 있는 객체도 함께 삭제
   - 완전히 깨끗한 상태로 시작

3. **테이블 생성**
   ```python
   with open('init.sql', 'r') as f:
       connection.execute(text(f.read()))
   ```
   - `init.sql` 파일의 모든 SQL 문 실행
   - 테이블, 인덱스, 트리거, 함수, 뷰 생성

4. **관리자 계정 생성**
   ```python
   create_admin_user(connection)
   ```
   - 기존 관리자 계정 삭제 후 재생성
   - 초기 로그인 정보:
     - 사용자명: `admin`
     - 이메일: `admin@example.com`
     - 비밀번호: `tkdgjsl1234!@#$`
     - 비밀번호는 bcrypt로 해시되어 저장

#### 5.2 관리자 계정 생성 함수

```python
def create_admin_user(connection):
    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": ADMIN_PASSWORD_HASH,  # bcrypt 해시
        "is_superuser": True
    }
    
    # 기존 관리자 삭제
    connection.execute(
        text("DELETE FROM users WHERE username = :username"),
        {"username": admin_data["username"]}
    )
    
    # 새 관리자 추가
    connection.execute(
        text("INSERT INTO users (...) VALUES (...)"),
        admin_data
    )
    connection.commit()
```

**특징:**
- 기존 관리자 계정이 있으면 삭제 후 재생성 (항상 최신 상태 유지)
- 비밀번호는 `app.core.security.get_password_hash()`로 해시
- `is_superuser=True`로 설정

## 초기화 실행 방법

### ⚠️ 중요: 실행 위치
**반드시 `backend` 디렉토리에서 실행해야 합니다.**

### 방법 1: 모듈로 실행 (권장)
```bash
cd backend
source venv/bin/activate  # 가상환경 활성화 (필수)
python -m app.db.db_init
```

### 방법 2: 스크립트로 실행
```bash
cd backend
source venv/bin/activate  # 가상환경 활성화 (필수)
python app/db/init_script.py
```

### 방법 3: Python 인터프리터에서 직접 실행
```bash
cd backend
source venv/bin/activate  # 가상환경 활성화 (필수)
python
>>> from app.db.db_init import init_db
>>> init_db()
```

### 방법 4: 환경 변수와 함께 실행
```bash
cd backend
source venv/bin/activate
export AIGROUND_DB_URL="postgresql://사용자:비밀번호@호스트:5432/데이터베이스"
python -m app.db.db_init
```

### ❌ 잘못된 실행 방법
```bash
# 이렇게 실행하면 안 됩니다!
python app/db/db_init.py  # ModuleNotFoundError 발생
```

**이유:** Python이 `app` 모듈을 찾을 수 없습니다. `backend` 디렉토리가 Python 경로에 있어야 합니다.

## 초기화 프로세스 흐름도

```
시작
  ↓
데이터베이스 URL 생성
  ↓
엔진 생성 및 연결
  ↓
기존 객체 정리 (DROP)
  ├─ 뷰 삭제
  ├─ 트리거 삭제
  ├─ 함수 삭제
  └─ 테이블 삭제
  ↓
init.sql 실행
  ├─ 확장 활성화
  ├─ 테이블 생성
  │   ├─ users
  │   ├─ bookmarks
  │   ├─ logs
  │   └─ sessions
  ├─ 인덱스 생성
  ├─ 트리거 생성
  ├─ 함수 생성
  └─ 뷰 생성
  ↓
관리자 계정 생성
  ├─ 기존 관리자 삭제
  └─ 새 관리자 추가
  ↓
완료
```

## 주의사항

### 1. 데이터 손실
- `init_db()` 실행 시 **모든 기존 데이터가 삭제**됩니다
- 프로덕션 환경에서는 주의해서 사용해야 합니다

### 2. 환경 변수
- `AIGROUND_DB_URL` 환경 변수가 설정되어 있으면 해당 URL 사용
- 없으면 기본값 사용: `postgresql://aiground:{비밀번호}@192.168.7.89:5432/aiscrap`

### 3. 비밀번호 인코딩
- 비밀번호는 URL 인코딩되어 사용됩니다
- 특수문자(`!@#$`)가 포함되어 있어 `quote_plus()`로 인코딩 필요

### 4. 연결 실패 처리
- 데이터베이스 연결 실패 시 예외 발생
- 로그 파일(`logs/db_init.log`)에 기록됨

## 로깅

초기화 과정은 다음 위치에 로깅됩니다:
- **콘솔 출력**: 진행 상황 및 결과
- **로그 파일**: `logs/db_init.log`
- **형식**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## 서버 시작 시 자동 초기화

`app/main.py`에서 서버 시작 시 테이블을 자동 생성하려고 시도합니다:

```python
try:
    Base.metadata.create_all(bind=engine)
    logger.info("데이터베이스 테이블 생성 완료")
except Exception as e:
    logger.warning(f"데이터베이스 테이블 생성 실패: {str(e)}")
```

**특징:**
- 연결 실패 시에도 서버는 시작됨
- 테이블이 없으면 자동으로 생성
- 기존 테이블은 유지됨 (DROP하지 않음)

## 모델과 SQL 스크립트의 관계

### SQLAlchemy 모델 (Python)
- `app/models/user.py` → `users` 테이블
- `app/models/bookmark.py` → `bookmarks` 테이블
- `app/models/log.py` → `logs` 테이블
- `app/models/session.py` → `sessions` 테이블

### SQL 스크립트
- `init.sql`에 모든 테이블 정의가 포함됨
- 모델과 SQL 스크립트가 일치해야 함

**권장 사항:**
- 모델 변경 시 `init.sql`도 함께 수정
- 또는 SQLAlchemy의 `Base.metadata.create_all()`만 사용 (모델 기반)

## 문제 해결

### 연결 실패 시
1. 데이터베이스 서버 실행 확인
2. 네트워크 연결 확인 (`ping`, `nc`)
3. 인증 정보 확인 (사용자명, 비밀번호, 데이터베이스명)
4. `pg_hba.conf` 설정 확인

### 테이블 생성 실패 시
1. 기존 테이블/뷰/트리거가 있는지 확인
2. 권한 확인 (CREATE TABLE 권한)
3. 확장(extension) 설치 확인

### 관리자 계정 생성 실패 시
1. `users` 테이블이 생성되었는지 확인
2. `is_superuser` 컬럼이 있는지 확인
3. 비밀번호 해시 함수가 정상 작동하는지 확인

## 요약

데이터베이스 초기화는 다음 단계로 이루어집니다:

1. **연결 설정**: `session.py`에서 엔진 및 세션 팩토리 생성
2. **모델 등록**: `base.py`에서 모든 모델을 Base에 등록
3. **초기화 실행**: `db_init.py`의 `init_db()` 함수 실행
4. **스키마 생성**: `init.sql` 실행으로 테이블/인덱스/트리거 생성
5. **초기 데이터**: 관리자 계정 생성

이 과정을 통해 완전히 초기화된 데이터베이스가 준비됩니다.
