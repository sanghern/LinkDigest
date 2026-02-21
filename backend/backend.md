# Backend 문서

## 목차
1. [소스코드 구조](#소스코드-구조)
2. [주요 기능](#주요-기능)
3. [사용자 가이드](#사용자-가이드)
4. [API 엔드포인트](#api-엔드포인트)
5. [환경 설정](#환경-설정)
6. [실행 방법](#실행-방법)

---

## 소스코드 구조

### 디렉토리 구조

```
backend/
├── app/
│   ├── api/                    # API 라우터 및 엔드포인트
│   │   ├── api.py             # 메인 API 라우터
│   │   └── endpoints/         # 엔드포인트 모듈
│   │       ├── auth.py        # 인증 관련 엔드포인트
│   │       ├── bookmarks.py   # 북마크 관련 엔드포인트 (인증 필요)
│   │       ├── bookmarks_public.py  # 공개 북마크 엔드포인트 (인증 불필요)
│   │       └── logs.py        # 로그 관련 엔드포인트
│   ├── core/                   # 핵심 설정 및 유틸리티
│   │   ├── config.py          # 애플리케이션 설정
│   │   ├── logging.py         # 로깅 설정
│   │   └── security.py        # 보안 관련 (JWT, 비밀번호 해싱)
│   ├── crud/                   # CRUD 작업
│   │   ├── base.py            # 기본 CRUD 클래스
│   │   └── crud_bookmark.py   # 북마크 CRUD (단일/다중 태그 필터링 지원)
│   ├── db/                     # 데이터베이스 관련
│   │   ├── session.py         # 데이터베이스 세션 관리
│   │   ├── base.py            # SQLAlchemy Base 클래스
│   │   └── init.sql           # 초기화 SQL 스크립트
│   ├── middleware/             # 미들웨어
│   │   └── logging.py         # 요청/응답 로깅 미들웨어
│   ├── models/                 # 데이터베이스 모델
│   │   ├── user.py            # 사용자 모델
│   │   ├── bookmark.py        # 북마크 모델
│   │   ├── log.py             # 로그 모델
│   │   └── session.py         # 세션 모델
│   ├── schemas/                # Pydantic 스키마
│   │   ├── user.py            # 사용자 스키마
│   │   ├── bookmark.py        # 북마크 스키마
│   │   ├── token.py           # 토큰 스키마
│   │   └── log.py             # 로그 스키마
│   ├── services/               # 비즈니스 로직 서비스
│   │   └── scraping_service.py  # 웹 스크래핑 서비스
│   ├── tasks/                  # 백그라운드 작업
│   │   └── summary_tasks.py   # 요약 생성 태스크
│   ├── utils/                  # 유틸리티 함수
│   │   ├── summerise_openai.py  # Ollama 요약 유틸리티
│   │   ├── translate.py       # 번역 유틸리티
│   │   └── auth.py            # 인증 유틸리티
│   └── main.py                 # FastAPI 애플리케이션 진입점
├── tests/                       # 테스트 코드
│   ├── conftest.py             # pytest 설정 및 공통 fixture
│   ├── test_auth.py            # 인증 테스트
│   ├── test_bookmarks.py       # 북마크 테스트
│   ├── test_logs.py            # 로그 테스트
│   └── verify_search_query.py  # 검색 쿼리 검증 스크립트
├── logs/                        # 로그 파일
├── requirements.txt             # Python 패키지 의존성
├── pytest.ini                   # pytest 설정 파일
├── start.sh                     # 서버 시작 스크립트
├── main.py                      # 서버 실행 진입점
├── Dockerfile                   # Docker 이미지 빌드
├── docker-compose.yml           # Docker Compose (backend, postgres, nginx)
├── docker/                      # Docker 관련 설정
│   └── nginx.conf               # Nginx 프록시 설정 (profile 사용 시)
├── scripts/                     # 유틸리티 스크립트
│   └── verify_db.py             # 외부 PostgreSQL 연결 검증
├── DOCKER_DEPLOY.md             # Docker 배포 매뉴얼
└── .env.docker.example          # Docker 배포용 환경 변수 예시
```

### 아키텍처 패턴

이 프로젝트는 **레이어드 아키텍처(Layered Architecture)** 패턴을 따릅니다:

1. **API Layer** (`app/api/`): HTTP 요청/응답 처리
2. **Service Layer** (`app/services/`): 비즈니스 로직
3. **Data Layer** (`app/models/`, `app/crud/`): 데이터베이스 접근
4. **Infrastructure Layer** (`app/core/`, `app/db/`): 설정 및 인프라

---

## 주요 기능

### 1. 사용자 인증 및 권한 관리

- **JWT 기반 인증**: OAuth2 Password Flow 사용
- **세션 관리**: 사용자 세션 추적 및 관리
- **비밀번호 해싱**: bcrypt를 사용한 안전한 비밀번호 저장
- **토큰 만료 관리**: 30분 만료 시간 설정

**주요 기능:**
- 사용자 로그인/로그아웃
- 현재 사용자 정보 조회 (`/api/auth/me`)
- 세션 기반 인증 상태 관리

### 2. 북마크 관리 시스템

- **웹 스크래핑**: URL에서 자동으로 콘텐츠 추출
- **AI 기반 요약**: Ollama를 사용한 자동 요약 생성
- **자동 번역**: 영어 제목을 한글로 자동 번역
- **태그 및 분류**: 키워드 추출 및 분류

**주요 기능:**
- 북마크 생성 (URL 입력 시 자동 스크래핑)
- 북마크 조회 (페이지네이션 지원)
- 북마크 수정/삭제
- 조회수 추적
- 태그 관리
- **다중 키워드 필터 검색** (AND 조건, 부분 일치 지원)

### 3. 웹 스크래핑 서비스

**ScrapingService** 클래스가 제공하는 기능:

- **제목 추출**: 
  - og:title 메타 태그 우선
  - article 태그 내 h1 태그
  - 일반 h1 태그
  - title 태그
- **콘텐츠 추출**:
  - 메인 콘텐츠 영역 자동 감지
  - 불필요한 요소 제거 (script, style, nav 등)
  - 참조 링크 추출
  - 이미지 추출
- **제목 번역**:
  - 영어 제목 자동 감지
  - 한글로 번역 후 `한글(영문)` 형태로 저장
- **보안뉴스 예외 처리**:
  - 모바일 URL(`m.boannews.com/html/detail.html?idx=...`)은 스크래핑 시 데스크톱 URL(`www.boannews.com/media/view.asp?tab_type=1&idx=...`)로 자동 변환 (`_normalize_boannews_url`)
  - 본문 영역 선택자에 `#news_content` 포함

### 4. AI 요약 및 번역

**Ollama 모델 사용:**

- **요약 모델**: `gpt-oss:120b-cloud` (기본값)
  - 마크다운 형식으로 요약 생성
  - 분류 및 키워드 자동 추출 (형식: `📌 키워드:`, `📌 **키워드:**`, `📌️ **분류:**` 등 지원)
  - 핵심 요약 5줄 생성
  - **마크다운 헤딩 보정**: `## ##`, `### ###` 등 중복 헤딩을 하나로 치환 (스크래핑 본문·요약 결과 모두 적용, `summary_tasks.fix_markdown_heading_duplicates`)

- **번역 모델**: `translategemma:4b`
  - 한글/영어 자동 감지
  - 영어 → 한글 번역
  - 한글 → 영어 번역

**비동기 처리:**
- 요약 생성은 백그라운드 스레드 풀에서 처리
- ThreadPoolExecutor 사용 (최대 3개 워커)

### 5. 공개 북마크 API (인증 불필요)

- **목적**: 비로그인 사용자가 `is_public=True`인 북마크만 조회
- **경로**: `/api/public/bookmarks/` (목록), `/api/public/bookmarks/{bookmark_id}` (단건, UUID)
- **인증**: 없음 (Authorization 헤더 불필요)
- **CRUD**: `app/crud/crud_bookmark.py`의 `get_multi_public`, `count_public`, `get_public_by_id` 사용
- **엔드포인트**: `app/api/endpoints/bookmarks_public.py`에서 인증 의존성 없이 제공

### 6. 로그 관리 시스템

- **로그 저장**: 프론트엔드/백엔드 로그 저장
- **로그 조회**: 페이지네이션 지원
- **로그 필터링**: 레벨, 소스별 필터링
- **로그 통계**: 전체 통계 및 최근 24시간 통계

---

## 사용자 가이드

### 1. 환경 설정

#### 필수 요구사항

- Python 3.11 이상
- PostgreSQL 데이터베이스
- Ollama 서버 (로컬 또는 원격)

#### 환경 변수 설정

**모든 설정값은 `.env` 파일에서 관리됩니다.** `app/core/config.py`는 Pydantic Settings를 사용하여 환경 변수를 자동으로 로드합니다.

`.env` 파일 생성 및 설정:

```bash
# 프로젝트 기본 설정
PROJECT_NAME=Bookmark Manager
API_V1_STR=/api

# 데이터베이스 설정
# 방법 1: 전체 URL 직접 설정 (우선순위 높음)
# AIGROUND_DB_URL=postgresql://사용자명:비밀번호@호스트:포트/데이터베이스명?sslmode=disable

# 방법 2: 개별 설정값으로 구성
DB_USER=aiground
DB_PASSWORD=your-password
DB_HOST=192.168.7.89
DB_PORT=5432
DB_NAME=aiscrap
DB_SSLMODE=disable

# 보안 설정
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 설정 (쉼표로 구분된 문자열)
BACKEND_CORS_ORIGINS_STR=http://localhost:3000,http://192.168.7.88:3000,http://192.168.7.88:3001,http://100.89.194.30:3000,http://digest.aiground.ai,https://linkdigest.aiground.ai

# OpenAI 설정 (사용하지 않지만 호환성을 위해 유지)
OPENAI_API_KEY=

# Ollama 설정
OLLAMA_API_URL=http://localhost:11434/api/chat
OLLAMA_MODEL=gpt-oss:120b-cloud
# 요약용 선택 가능 모델 (쉼표 구분, 북마크 추가 시 프론트에서 선택)
OLLAMA_MODEL_LISTS=gpt-oss:120b-cloud, emma3:27b-cloud
TRANSLATE_MODEL=translategemma:4b

# URL 중복 등록 체크 (True: 중복 시 409 반환, False: 체크 생략)
DUPLICATE_URL_CHECK_ENABLED=True

# 초기 관리자 계정 설정 (db_init.py에서 사용)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
```

**중요 사항:**
- Pydantic Settings는 다음 순서로 값을 로드합니다:
  1. 시스템 환경 변수 (최우선)
  2. `.env` 파일의 값
  3. 클래스 필드의 기본값 (fallback)
- 모든 설정값은 `.env` 파일에서 관리하며, 코드에는 하드코딩된 값이 없습니다.
- 프로덕션 환경에서는 반드시 `SECRET_KEY`와 `DB_PASSWORD`를 안전하게 설정하세요.

### 2. 데이터베이스 설정

#### PostgreSQL 연결 설정

데이터베이스 연결은 `app/core/config.py`의 `Settings` 클래스에서 자동으로 구성됩니다:

```python
# AIGROUND_DB_URL이 설정되어 있으면 우선 사용
# 없으면 개별 설정값(DB_USER, DB_PASSWORD 등)으로 URL 자동 생성
DATABASE_URL = settings.DATABASE_URL
```

#### 테이블 자동 생성

서버 시작 시 자동으로 테이블이 생성됩니다:
- `users`: 사용자 테이블
- `bookmarks`: 북마크 테이블
- `logs`: 로그 테이블
- `sessions`: 세션 테이블

### 3. 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

### 4. 서버 실행

#### 방법 1: start.sh 스크립트 사용

```bash
chmod +x start.sh
./start.sh
```

#### 방법 2: 직접 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 방법 3: Python으로 실행

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. API 문서 확인

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/api/openapi.json
- **ReDoc**: http://localhost:8000/docs (FastAPI 기본 제공)

---

## API 엔드포인트

API는 **공개용**(인증 불필요)과 **인증용**(JWT 필요)으로 구분됩니다.

### 공개 북마크 (Public Bookmarks, 인증 불필요)

#### GET `/api/public/bookmarks/`
`is_public=True`인 북마크 목록 조회. 토큰 없이 호출 가능.

**Query Parameters:**
- `page`: 페이지 번호 (기본값: 1)
- `per_page`: 페이지당 항목 수 (기본값: 10, 최대 100)

**Response:** `BookmarkListResponse` (items, total, page, per_page, total_pages)

#### GET `/api/public/bookmarks/{bookmark_id}`
`is_public=True`인 북마크 단건 조회. `bookmark_id`는 UUID.

**Response:** `BookmarkResponse` (해당 북마크가 공개가 아니거나 없으면 404)

---

### 인증 (Authentication)

#### POST `/api/auth/login`
사용자 로그인 및 토큰 발급

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string"
  }
}
```

#### GET `/api/auth/me`
현재 로그인한 사용자 정보 조회

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "string"
}
```

#### POST `/api/auth/logout`
로그아웃 (세션 비활성화)

**Headers:**
```
Authorization: Bearer {access_token}
```

### 북마크 (Bookmarks, 인증 필요)

#### POST `/api/bookmarks/`
새 북마크 생성

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "url": "https://example.com",
  "title": "선택사항",
  "tags": ["tag1", "tag2"],
  "summary_model": "gpt-oss:120b-cloud"
}
```
- `summary_model`: (선택) 요약에 사용할 Ollama 모델명. 미지정 시 `OLLAMA_MODEL` 사용. `OLLAMA_MODEL_LISTS`에 포함된 값만 유효.

**동작 과정:**
1. URL에서 콘텐츠 스크래핑
2. 제목 자동 추출 (없는 경우)
3. 영어 제목 자동 번역
4. 북마크 생성
5. 백그라운드에서 요약 생성 시작 (선택된 모델 또는 기본 모델 사용)

#### GET `/api/bookmarks/summary-models`
요약에 사용 가능한 모델 목록 반환 (`OLLAMA_MODEL_LISTS` 기반). 북마크 추가 UI에서 모델 선택 시 사용.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "models": ["gpt-oss:120b-cloud", "emma3:27b-cloud"]
}
```

#### GET `/api/bookmarks/`
북마크 목록 조회 (페이지네이션)

**Query Parameters:**
- `page`: 페이지 번호 (기본값: 1)
- `per_page`: 페이지당 항목 수 (기본값: 10)
- `tags`: 필터링할 태그/키워드 목록 (선택사항, 배열)
  - 여러 태그를 전달하면 **AND 조건**으로 검색
  - 각 태그 내부에서 공백, '·', ','로 구분된 키워드는 **OR 조건**으로 검색
  - 각 키워드는 **부분 일치**로 검색됨

**Response:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "total_pages": 10
}
```

**예시:**
- 전체 목록: `GET /api/bookmarks/?page=1&per_page=10`
- 단일 키워드 필터링: `GET /api/bookmarks/?page=1&per_page=10&tags=AI`
- 다중 키워드 필터링 (AND 조건): `GET /api/bookmarks/?page=1&per_page=10&tags=AI&tags=코딩`
- 복합 필터 (태그 내부 OR 조건): `GET /api/bookmarks/?page=1&per_page=10&tags=AI 코딩&tags=Python`
  - 검색 조건: `("AI" OR "코딩") AND ("Python" OR "Python3")`

**검색 로직:**
- **다중 필터 (AND 조건)**: 여러 태그를 선택하면 모든 태그 조건을 만족하는 북마크만 검색
  - 예: `tags=["AI", "코딩"]` → `("AI" 포함) AND ("코딩" 포함)`
- **단일 필터 내부 (OR 조건)**: 하나의 태그 내에서 구분자(공백, ',', '-', '·')로 구분된 키워드는 OR 조건으로 검색
  - 예: `tags=["AI 코딩"]` → `("AI" 포함) OR ("코딩" 포함)`
  - 예: `tags=["AI,코딩"]` → `("AI" 포함) OR ("코딩" 포함)`
  - 예: `tags=["AI-코딩"]` → `("AI" 포함) OR ("코딩" 포함)`
  - 예: `tags=["AI·코딩"]` → `("AI" 포함) OR ("코딩" 포함)`
- **복합 검색**: 다중 필터와 단일 필터 내부 OR 조건을 결합
  - 예: `tags=["AI 코딩", "Python"]` → `(("AI" 포함) OR ("코딩" 포함)) AND ("Python" 포함)`
- **부분 일치**: 각 키워드는 LIKE 검색으로 부분 일치 지원
  - 예: "AI" 검색 시 "AI", "AI coding", "chatbot AI" 모두 검색됨

#### GET `/api/bookmarks/{bookmark_id}`
북마크 상세 조회

#### PUT `/api/bookmarks/{bookmark_id}`
북마크 수정

- **권한**: 등록자만 수정 가능. 등록자가 아니면 **403**, `detail: "권한 없음"` 반환.

**Request Body:**
```json
{
  "title": "수정된 제목",
  "url": "https://example.com",
  "tags": ["tag1", "tag2"],
  "summary": "요약 내용"
}
```

#### DELETE `/api/bookmarks/{bookmark_id}`
북마크 삭제

- **권한**: 북마크 ID로 조회 후 소유자 확인. 없으면 404, 등록자가 아니면 **403**, `detail: "권한 없음"` 반환. 등록자만 삭제 가능.

#### POST `/api/bookmarks/{bookmark_id}/increase-read-count`
조회수 증가

---

## 최근 업데이트

### 공개 북마크 API (2026-02)

- **공개용 API 분리**: 인증 없이 접근 가능한 엔드포인트를 `/api/public/bookmarks`로 분리.
- **GET /api/public/bookmarks/**: `is_public=True`인 북마크 목록 조회 (페이지네이션).
- **GET /api/public/bookmarks/{bookmark_id}**: `is_public=True`인 북마크 단건 조회 (bookmark_id는 UUID).
- **구현**: `app/api/endpoints/bookmarks_public.py`, CRUD `get_multi_public`, `count_public`, `get_public_by_id`.

### 북마크 수정·삭제 권한 검증 (2026-02-12)

- **PUT /api/bookmarks/{id}**: 등록자가 아니면 403, `detail: "권한 없음"` 반환.
- **DELETE /api/bookmarks/{id}**: ID로 북마크 조회 후, 없으면 404, 등록자가 아니면 403 `detail: "권한 없음"` 반환. 기존에는 소유자만 조회해 타인 글 삭제 시 404였으나, 이제 권한 없음 시 403으로 명확히 구분.

### 요약 모델 선택 및 설정 기능

**요약 모델 선택:**
- **환경 변수**: `.env`에 `OLLAMA_MODEL_LISTS` 추가 (쉼표 구분, 예: `gpt-oss:120b-cloud, emma3:27b-cloud`). 북마크 추가 시 선택 가능한 요약용 모델 목록.
- **API**: `GET /api/bookmarks/summary-models` — 지원 모델 목록 반환. `POST /api/bookmarks/` 요청 시 `summary_model`(선택)로 사용할 모델 지정. 미지정 시 `OLLAMA_MODEL` 사용.
- **프론트**: 북마크 추가 UI에 요약 모델 드롭다운 추가, 선택한 모델을 생성 요청에 포함.

**URL 중복 체크 on/off:**
- **환경 변수**: `DUPLICATE_URL_CHECK_ENABLED=True|False`. `True`(기본): 동일 URL 등록 시 409 반환. `False`: 중복 체크 생략.

**요약 프롬프트 외부 설정:**
- **파일**: `app/utils/prompt.conf` (JSON). `system`, `user_template`(배열 형식, 줄 단위 가독성)으로 요약용 시스템/유저 프롬프트 정의. `{text}`는 본문 치환용.

### 2026-02-14: 테스트 구조 개선 및 pytest 통일

**테스트 개선:**
- **pytest 통일**: 모든 테스트를 pytest 형식으로 통일
- **공통 Fixture 추가**: `conftest.py`에 `base_url`, `admin_token`, `auth_headers` fixture 추가
- **기존 코드 유지**: 독립 실행 가능한 기존 테스트 함수 유지
- **이중 실행 지원**: pytest로 실행하거나 독립 실행 스크립트로 실행 가능

**주요 변경 파일:**
- `tests/conftest.py`: 공통 fixture 추가 (base_url, admin_token, auth_headers)
- `tests/test_bookmarks.py`: pytest 형식 테스트 함수 추가
- `tests/test_logs.py`: pytest 형식 테스트 함수 추가
- `tests/test_auth.py`: pytest 형식 테스트 함수 추가
- `pytest.ini`: pytest 설정 파일 활용

**사용 방법:**
- pytest 실행: `pytest` 또는 `pytest tests/test_bookmarks.py`
- 독립 실행: `python tests/test_bookmarks.py` (기존 방식 유지)

### 2026-02-14: 환경 변수 관리 개선

**환경 변수 완전 분리:**
- **모든 설정값을 .env 파일로 이동**: 하드코딩된 값 제거
- **Pydantic Settings 활용**: 환경 변수 자동 로드 및 검증
- **설정 우선순위 명확화**: 시스템 환경 변수 → `.env` 파일 → 기본값
- **관리자 계정 설정**: `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`를 환경 변수로 관리
- **데이터베이스 설정**: 전체 URL 또는 개별 설정값으로 구성 가능

**주요 변경 파일:**
- `app/core/config.py`: Pydantic Settings로 환경 변수 관리
- `app/db/session.py`: `settings.DATABASE_URL` 사용
- `app/db/db_init.py`: 환경 변수에서 관리자 계정 정보 로드
- `app/utils/summerise_openai.py`: `settings`에서 Ollama 설정 로드
- `app/utils/translate.py`: `settings`에서 Ollama 설정 로드

### 2026-02-14: 키워드 구분자 지원 기능 추가

**추가된 기능:**
- 하나의 키워드가 구분자(공백, ',', '-', '·')로 구분된 여러 단어로 구성되어 있을 때 OR 조건으로 검색
- 기존 기능(단일 키워드 검색, 다중 키워드 AND 조건 검색) 유지

**기술적 세부사항:**
- `split_keyword_by_delimiters()` 헬퍼 함수 추가: 키워드를 구분자로 분리
- 단일 태그 검색 함수(`get_multi_by_owner_with_tag`, `count_by_owner_with_tag`) 수정:
  - 구분자가 없으면 기존처럼 단일 패턴으로 검색
  - 구분자가 있으면 분리된 단어들을 OR 조건으로 검색
- 다중 태그 검색 함수(`get_multi_by_owner_with_tags`, `count_by_owner_with_tags`) 수정:
  - 각 태그 내부에서 구분자가 있으면 OR 조건으로 검색
  - 여러 태그 간에는 AND 조건 유지
- PostgreSQL의 `EXISTS` 서브쿼리와 `unnest()` 함수를 사용하여 배열 요소 검색
- SQL 로깅 기능 추가: 생성된 SQL과 파라미터를 INFO 레벨로 로깅

**검색 예시:**
- `tags=["AI"]` → `%AI%` 패턴으로 검색 (기존 동작 유지)
- `tags=["AI 코딩"]` → `("AI" 포함) OR ("코딩" 포함)`
- `tags=["AI,코딩"]` → `("AI" 포함) OR ("코딩" 포함)`
- `tags=["AI-코딩"]` → `("AI" 포함) OR ("코딩" 포함)`
- `tags=["AI·코딩"]` → `("AI" 포함) OR ("코딩" 포함)`
- `tags=["AI 코딩", "Python"]` → `(("AI" 포함) OR ("코딩" 포함)) AND ("Python" 포함)`

### 2026-02-13: 다중 필터 검색 기능 개선 (AND 조건)

**개선된 기능:**
- 다중 키워드 필터를 **AND 조건**으로 검색하도록 개선
- `GET /api/bookmarks/` 엔드포인트의 `tag` 파라미터를 `tags` 배열 파라미터로 변경
- 여러 태그를 선택하면 모든 태그 조건을 만족하는 북마크만 검색
- 각 태그 내부의 공백/쉼표 구분 키워드는 **OR 조건**으로 검색
- 부분 일치(LIKE) 검색 지원 유지

**기술적 세부사항:**
- CRUD 함수에 `get_multi_by_owner_with_tags()`, `count_by_owner_with_tags()` 추가
- SQLAlchemy의 `and_()` 함수를 사용하여 여러 태그를 AND 조건으로 결합
- 각 태그 내부는 `or_()` 함수로 OR 조건 처리
- PostgreSQL의 `EXISTS` 서브쿼리와 `unnest()` 함수를 사용하여 배열 요소 검색
- FastAPI의 `Query` 파라미터를 사용하여 배열 파라미터 지원

### 2026-02-13: 키워드 검색 기능 추가

**추가된 기능:**
- 북마크 목록 조회 시 키워드로 필터링 기능 추가
- `GET /api/bookmarks/` 엔드포인트에 `tags` 배열 쿼리 파라미터 추가
- PostgreSQL ARRAY 타입에서 키워드 검색 지원

**기술적 세부사항:**
- CRUD 함수에 `get_multi_by_owner_with_tag`, `count_by_owner_with_tag` 추가 (단일 태그용, 하위 호환성 유지)
- PostgreSQL의 `EXISTS` 서브쿼리와 `unnest()` 함수를 사용하여 배열 요소 검색
- 페이지네이션과 함께 키워드 필터링 지원

### 로그 (Logs)

#### POST `/api/logs/`
로그 생성

**Request Body:**
```json
{
  "level": "INFO",
  "message": "로그 메시지",
  "source": "frontend",
  "meta_data": {}
}
```

#### GET `/api/logs/`
로그 목록 조회

**Query Parameters:**
- `page`: 페이지 번호
- `per_page`: 페이지당 항목 수
- `level`: 로그 레벨 필터 (INFO, WARN, ERROR)
- `source`: 소스 필터 (frontend, backend)

#### GET `/api/logs/stats`
로그 통계 조회

**Response:**
```json
{
  "total": 1000,
  "errors": 50,
  "last_24h": 100
}
```

---

## 환경 설정

### 환경 변수 관리

**모든 설정값은 `.env` 파일에서 관리됩니다.** `app/core/config.py`는 Pydantic Settings를 사용하여 환경 변수를 자동으로 로드합니다.

**설정 우선순위:**
1. 시스템 환경 변수 (최우선)
2. `.env` 파일의 값
3. 클래스 필드의 기본값 (fallback)

### CORS 설정

`.env` 파일에서 CORS 허용 오리진 설정:

```bash
BACKEND_CORS_ORIGINS_STR=http://localhost:3000,http://192.168.7.88:3000,http://192.168.7.88:3001,http://100.89.194.30:3000,http://digest.aiground.ai,https://linkdigest.aiground.ai
```

쉼표로 구분된 문자열로 설정하면 자동으로 리스트로 변환됩니다.

### 데이터베이스 연결 설정

연결 풀 설정 (`app/db/session.py`):

- `pool_pre_ping=True`: 연결 상태 확인
- `pool_recycle=3600`: 1시간마다 연결 재생성
- `connect_timeout=30`: 연결 타임아웃 30초
- `keepalives`: TCP keepalive 활성화

### 로깅 설정

로깅은 `app/core/logging.py`에서 설정됩니다:

- 파일 로깅: `logs/app.log`
- 콘솔 로깅: 표준 출력
- 요청/응답 로깅: 미들웨어를 통한 자동 로깅

---

## 실행 방법

### 개발 환경

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
# .env 파일 생성 또는 환경 변수 설정

# 4. 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 프로덕션 환경

```bash
# 1. start.sh 스크립트 사용
./start.sh

# 2. 또는 systemd 서비스로 등록
# uvicorn을 gunicorn과 함께 사용 권장
```

### Docker 배포 (Docker Compose)

Backend는 Docker Compose로 배포할 수 있으며, **외부 PostgreSQL**(`.env`의 `DB_HOST` 등) 사용이 기본입니다. 상세 절차는 **[DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md)**를 참고하세요.

**요약:**
- **실행**: `docker compose up -d` → backend만 기동 (별도 Nginx 사용 시). 실행 시 환경은 **`.env`** 파일 사용.
- **내부 DB 사용**: `.env`에 `DB_HOST=postgres` 로 두고 `docker compose --profile internal-db up -d`
- **Compose 내부 Nginx 사용**: `docker compose --profile with-nginx up -d` (로컬 8080 프록시)
- **외부 DB 연결 검증**: `docker compose exec backend python scripts/verify_db.py`
- **중지**: `docker compose down` (볼륨 유지), `docker compose down -v` (볼륨 포함 삭제)

프론트엔드는 **frontend/** 에서 독립 Docker로 실행 가능합니다. `cd frontend && docker compose up -d` → 포트 3000. 상세는 [frontend/DOCKER_DEPLOY.md](../frontend/DOCKER_DEPLOY.md) 참고.

---

## 주요 기술 스택

- **웹 프레임워크**: FastAPI 0.109.2
- **데이터베이스**: PostgreSQL (psycopg2-binary)
- **ORM**: SQLAlchemy 2.0.27
- **인증**: JWT (python-jose), OAuth2
- **비밀번호 해싱**: bcrypt (passlib)
- **웹 스크래핑**: BeautifulSoup4, requests
- **AI 모델**: Ollama API
- **비동기 처리**: ThreadPoolExecutor
- **데이터 검증**: Pydantic 2.6.1
- **로깅**: Python logging 모듈
- **테스트 프레임워크**: pytest 8.3.4

---

## 주의사항

1. **보안**: 프로덕션 환경에서는 반드시 `SECRET_KEY`를 안전하게 설정하세요.
2. **데이터베이스**: PostgreSQL 연결 정보를 안전하게 관리하세요.
3. **CORS**: 프로덕션에서는 필요한 오리진만 허용하세요.
4. **Ollama 서버**: Ollama 서버가 실행 중이어야 요약 및 번역 기능이 작동합니다.
5. **에러 처리**: 모든 API 엔드포인트는 적절한 에러 처리를 포함하고 있습니다.

---

## 문제 해결

### 데이터베이스 연결 실패

- PostgreSQL 서버가 실행 중인지 확인
- 연결 정보 (호스트, 포트, 사용자명, 비밀번호) 확인
- 방화벽 설정 확인

### Ollama API 오류

- Ollama 서버가 실행 중인지 확인
- `OLLAMA_API_URL` 환경 변수 확인
- 모델이 설치되어 있는지 확인 (`ollama list`)

### CORS 오류

- `BACKEND_CORS_ORIGINS`에 프론트엔드 URL이 포함되어 있는지 확인
- 브라우저 개발자 도구에서 실제 오리진 확인

---

## 테스트

### 테스트 프레임워크

이 프로젝트는 **pytest**를 사용하여 테스트를 작성합니다.

**설정 파일**: `pytest.ini`
```ini
[pytest]
pythonpath = .
asyncio_mode = auto
```

**주요 설정:**
- `pythonpath = .`: 프로젝트 루트를 Python 경로에 추가
- `asyncio_mode = auto`: 비동기 테스트 자동 모드

### 테스트 파일 구조

- **`tests/conftest.py`**: pytest 설정 및 공통 fixture 정의
  - `base_url`: API 기본 URL fixture
  - `admin_token`: 관리자 로그인 토큰 fixture
  - `auth_headers`: 인증 헤더 fixture
  - `async_client`: 비동기 HTTP 클라이언트 fixture
  - `db_session`: 데이터베이스 세션 fixture

- **`tests/test_auth.py`**: 인증 관련 테스트
  - `test_user_auth()`: 독립 실행 가능한 통합 테스트
  - `test_login_success()`: pytest 형식 테스트
  - `test_auth_admin_login()`: pytest 형식 테스트
  - `test_auth_me()`: pytest 형식 테스트

- **`tests/test_bookmarks.py`**: 북마크 관련 테스트
  - `test_bookmarks()`: 독립 실행 가능한 통합 테스트
  - `test_bookmark_create()`: pytest 형식 테스트
  - `test_bookmark_get_list()`: pytest 형식 테스트
  - `test_bookmark_read_count()`: pytest 형식 테스트

- **`tests/test_logs.py`**: 로그 관련 테스트
  - `test_logs()`: 독립 실행 가능한 통합 테스트
  - `test_log_create()`: pytest 형식 테스트
  - `test_log_get_list()`: pytest 형식 테스트
  - `test_log_get_stats()`: pytest 형식 테스트

- **`tests/verify_search_query.py`**: 검색 쿼리 검증 스크립트 (독립 실행)

### 테스트 실행 방법

#### pytest로 실행 (권장)

```bash
# 모든 테스트 실행
pytest

# 특정 파일만 실행
pytest tests/test_bookmarks.py

# 특정 테스트 함수만 실행
pytest tests/test_bookmarks.py::test_bookmark_create

# 상세 출력
pytest -v

# 실패한 테스트만 재실행
pytest --lf
```

#### 독립 실행 (기존 방식 유지)

```bash
# 기존 방식으로도 실행 가능
python tests/test_bookmarks.py
python tests/test_logs.py
python tests/test_auth.py
python tests/verify_search_query.py
```

### 테스트 전제 조건

1. **서버 실행**: 테스트 실행 전 백엔드 서버가 실행 중이어야 합니다.
2. **데이터베이스 연결**: PostgreSQL 데이터베이스가 접근 가능해야 합니다.
3. **환경 변수**: `.env` 파일에 필요한 설정값이 있어야 합니다.

### 테스트 Fixture 활용

pytest fixture를 사용하여 코드 중복을 제거하고 테스트를 간소화합니다:

```python
def test_bookmark_create(base_url, auth_headers):
    """북마크 생성 테스트 - fixture 사용"""
    bookmark_data = {
        "title": "Test Bookmark",
        "url": "https://example.com",
        "tags": ["test"]
    }
    
    response = requests.post(
        f"{base_url}/bookmarks/",
        headers=auth_headers,  # fixture에서 자동으로 토큰 포함
        json=bookmark_data
    )
    
    assert response.status_code == 200
```

---

## 추가 리소스

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [Ollama 문서](https://ollama.ai/docs)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [pytest 문서](https://docs.pytest.org/)
