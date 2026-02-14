# LinkDigest 서비스 설계서

## 1. 개요

### 1.1 프로젝트 소개
LinkDigest는 웹 URL을 입력받아 자동으로 콘텐츠를 스크래핑하고, AI를 활용하여 요약 및 키워드 추출을 수행하는 북마크 관리 서비스입니다.

### 1.2 주요 기능
- **웹 스크래핑**: URL에서 자동으로 콘텐츠 추출
- **AI 기반 요약**: Ollama를 사용한 자동 요약 생성
- **자동 번역**: 영어 제목을 한글로 자동 번역
- **태그 관리**: 키워드 추출 및 분류
- **다중 키워드 필터 검색**: AND/OR 조건 지원, 부분 일치 검색
- **사용자 인증**: JWT 기반 인증 시스템
- **로그 관리**: 프론트엔드/백엔드 로그 통합 관리

---

## 2. 시스템 구성도

### 2.1 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        클라이언트 (브라우저)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React Frontend (Port 3000)                         │  │
│  │  - BookmarkList, BookmarkDetail                     │  │
│  │  - Login, LogViewer                                 │  │
│  │  - Context API (인증 상태 관리)                       │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
                        │ (JWT Token)
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer                                           │  │
│  │  - /api/auth (인증)                                  │  │
│  │  - /api/bookmarks (북마크 CRUD)                       │  │
│  │  - /api/logs (로그 관리)                             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Service Layer                                       │  │
│  │  - ScrapingService (웹 스크래핑)                      │  │
│  │  - SummaryTasks (비동기 요약 생성)                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Layer                                         │  │
│  │  - CRUD Operations (SQLAlchemy ORM)                 │  │
│  │  - Models (User, Bookmark, Log, Session)           │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  PostgreSQL  │ │   Ollama    │ │   Web      │
│  Database    │ │   API       │ │   Sites    │
│  (Port 5432) │ │  (LLM 서버) │ │  (스크래핑) │
└──────────────┘ └─────────────┘ └────────────┘
```

### 2.2 데이터 흐름도

#### 북마크 생성 플로우
```
사용자 URL 입력
    ↓
Frontend → POST /api/bookmarks/
    ↓
Backend: ScrapingService.scrape()
    ↓
웹 사이트 스크래핑 (제목, 콘텐츠 추출)
    ↓
제목 번역 (Ollama translate API)
    ↓
북마크 DB 저장
    ↓
비동기 요약 태스크 시작 (ThreadPoolExecutor)
    ↓
Ollama 요약 API 호출
    ↓
요약, 키워드, 분류 추출
    ↓
DB 업데이트 (summary, tags, category)
    ↓
Frontend: 북마크 목록 업데이트
```

#### 검색 플로우
```
사용자 키워드 선택
    ↓
Frontend: selectedTags 상태 업데이트
    ↓
GET /api/bookmarks/?tags=AI&tags=코딩
    ↓
Backend: CRUD 필터링 로직
    ↓
PostgreSQL: EXISTS 서브쿼리 (LIKE 검색)
    ↓
결과 반환 (페이지네이션)
    ↓
Frontend: 북마크 목록 렌더링
```

---

## 3. 기술 스택

### 3.1 Backend 기술 스택

| 카테고리 | 기술 | 버전 | 용도 |
|---------|------|------|------|
| **웹 프레임워크** | FastAPI | 0.109.2 | REST API 서버 |
| **데이터베이스** | PostgreSQL | - | 관계형 데이터베이스 |
| **ORM** | SQLAlchemy | 2.0.27 | 데이터베이스 ORM |
| **인증** | python-jose | 3.3.0 | JWT 토큰 처리 |
| **비밀번호 해싱** | bcrypt (passlib) | 3.2.2 | 비밀번호 암호화 |
| **웹 스크래핑** | BeautifulSoup4 | 4.12.3 | HTML 파싱 |
| **HTTP 클라이언트** | requests | 2.31.0 | HTTP 요청 |
| **비동기 처리** | ThreadPoolExecutor | - | 백그라운드 작업 |
| **데이터 검증** | Pydantic | 2.6.1 | 스키마 검증 |
| **서버 실행** | Uvicorn | 0.27.1 | ASGI 서버 |
| **로깅** | Python logging | - | 로그 관리 |

### 3.2 Frontend 기술 스택

| 카테고리 | 기술 | 버전 | 용도 |
|---------|------|------|------|
| **UI 프레임워크** | React | 18.2.0 | 사용자 인터페이스 |
| **라우팅** | React Router DOM | 6.22.1 | 클라이언트 사이드 라우팅 |
| **HTTP 클라이언트** | Axios | 1.6.7 | API 통신 |
| **스타일링** | Tailwind CSS | 3.4.17 | CSS 프레임워크 |
| **마크다운 렌더링** | react-markdown | 9.0.3 | 마크다운 콘텐츠 표시 |
| **마크다운 플러그인** | remark-gfm | 4.0.0 | GitHub Flavored Markdown |
| **마크다운 플러그인** | rehype-raw | 7.0.0 | HTML 렌더링 |
| **날짜 처리** | date-fns | 2.30.0 | 날짜 포맷팅 |
| **아이콘** | Heroicons React | 2.2.0 | 아이콘 컴포넌트 |
| **빌드 도구** | React Scripts | 5.0.1 | 빌드 및 개발 서버 |

### 3.3 AI/ML 기술 스택

| 카테고리 | 기술 | 모델 | 용도 |
|---------|------|------|------|
| **LLM 서버** | Ollama | - | 로컬 LLM 서버 |
| **요약 모델** | Ollama | gpt-oss:120b-cloud | 콘텐츠 요약 생성 |
| **번역 모델** | Ollama | translategemma:4b | 제목 번역 |

### 3.4 인프라 및 도구

| 카테고리 | 기술 | 용도 |
|---------|------|------|
| **버전 관리** | Git | 소스 코드 관리 |
| **패키지 관리** | pip / npm | 의존성 관리 |
| **환경 변수** | python-dotenv | 환경 설정 관리 |
| **로깅** | Python logging | 로그 파일 관리 |

---

## 4. 시스템 아키텍처

### 4.1 Backend 아키텍처 (레이어드 아키텍처)

```
┌─────────────────────────────────────────────────────────┐
│              API Layer (app/api/)                       │
│  - FastAPI Router                                      │
│  - Request/Response 처리                                │
│  - 인증 미들웨어                                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│          Service Layer (app/services/)                  │
│  - ScrapingService (웹 스크래핑 비즈니스 로직)           │
│  - 비동기 태스크 관리                                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│          Data Layer (app/models/, app/crud/)           │
│  - SQLAlchemy Models                                   │
│  - CRUD Operations                                     │
│  - 데이터베이스 쿼리                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│      Infrastructure Layer (app/core/, app/db/)         │
│  - 설정 관리 (config.py)                                │
│  - 데이터베이스 연결 (session.py)                        │
│  - 로깅 설정 (logging.py)                               │
│  - 보안 설정 (security.py)                              │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Frontend 아키텍처 (컴포넌트 기반 아키텍처)

```
┌─────────────────────────────────────────────────────────┐
│        Presentation Layer (components/)                │
│  - React 컴포넌트 (UI 렌더링)                           │
│  - BookmarkList, BookmarkDetail 등                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│     State Management Layer (contexts/)                 │
│  - Context API (전역 상태 관리)                         │
│  - AuthContext (인증 상태)                              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│          Service Layer (utils/api.js)                  │
│  - Axios 인스턴스                                       │
│  - API 호출 함수                                        │
│  - 요청/응답 인터셉터                                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│          Routing Layer (App.js)                        │
│  - React Router                                         │
│  - 라우트 정의 및 보호                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 5. 데이터베이스 설계

### 5.1 ERD (Entity Relationship Diagram)

```
┌─────────────┐         ┌──────────────┐
│    User     │         │   Session    │
├─────────────┤         ├──────────────┤
│ id (PK)     │◄──┐     │ id (PK)      │
│ username    │   │     │ user_id (FK) │
│ email       │   │     │ token        │
│ password    │   │     │ expires_at   │
│ created_at  │   │     └──────────────┘
│ last_login  │   │
│ is_active   │   │
└─────────────┘   │
                  │
                  │      ┌──────────────┐
                  │      │   Bookmark   │
                  └─────►├──────────────┤
                         │ id (PK)      │
                         │ user_id (FK) │
                         │ title        │
                         │ url          │
                         │ summary      │
                         │ content      │
                         │ tags[]       │
                         │ category     │
                         │ read_count   │
                         │ created_at   │
                         │ updated_at   │
                         └──────────────┘
                                  │
                                  │
                         ┌────────▼────────┐
                         │      Log        │
                         ├─────────────────┤
                         │ id (PK)         │
                         │ user_id (FK)    │
                         │ level           │
                         │ message         │
                         │ source          │
                         │ timestamp       │
                         │ request_path    │
                         │ response_status │
                         └─────────────────┘
```

### 5.2 주요 테이블 구조

#### users 테이블
- `id`: UUID (Primary Key)
- `username`: String(50), Unique, Index
- `email`: String(100), Unique, Index
- `hashed_password`: String(200)
- `created_at`: DateTime
- `last_login`: DateTime
- `is_active`: Boolean

#### bookmarks 테이블
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → users.id)
- `title`: String(255)
- `url`: Text
- `summary`: Text
- `content`: Text
- `source_name`: String(100)
- `tags`: ARRAY(String) - PostgreSQL 배열 타입
- `category`: String
- `read_count`: Integer
- `is_deleted`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

#### logs 테이블
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → users.id, Nullable)
- `level`: String(10) - INFO, WARN, ERROR
- `message`: Text
- `source`: String(50) - frontend, backend
- `timestamp`: DateTime
- `request_path`: String(255)
- `request_method`: String(10)
- `response_status`: Integer
- `execution_time`: Float
- `meta_data`: JSONB

#### sessions 테이블
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → users.id)
- `token`: String
- `expires_at`: DateTime

---

## 6. API 설계

### 6.1 API 엔드포인트 구조

```
/api
├── /auth
│   ├── POST /login          # 로그인
│   ├── POST /logout         # 로그아웃
│   └── GET  /me             # 현재 사용자 정보
│
├── /bookmarks
│   ├── GET    /             # 북마크 목록 조회 (페이지네이션, 필터링)
│   ├── POST   /             # 북마크 생성
│   ├── GET    /{id}         # 북마크 상세 조회
│   ├── PUT    /{id}         # 북마크 수정
│   ├── DELETE /{id}         # 북마크 삭제
│   └── POST   /{id}/increase-read-count  # 조회수 증가
│
└── /logs
    ├── GET  /               # 로그 목록 조회 (페이지네이션, 필터링)
    ├── POST /               # 로그 생성
    └── GET  /stats          # 로그 통계
```

### 6.2 주요 API 상세

#### GET /api/bookmarks/
**쿼리 파라미터:**
- `page`: 페이지 번호 (기본값: 1)
- `per_page`: 페이지당 항목 수 (기본값: 10)
- `tags`: 필터링할 태그/키워드 목록 (배열, 선택사항)
  - 여러 태그: AND 조건
  - 태그 내부 구분자(공백, ',', '-', '·'): OR 조건
  - 부분 일치 검색 지원

**응답 예시:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "제목",
      "url": "https://example.com",
      "summary": "요약 내용",
      "tags": ["AI", "코딩"],
      "read_count": 10,
      "created_at": "2026-02-14T00:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "total_pages": 10
}
```

---

## 7. 보안 설계

### 7.1 인증 및 권한 관리

- **JWT 기반 인증**: OAuth2 Password Flow
- **토큰 만료 시간**: 30분
- **비밀번호 해싱**: bcrypt (passlib)
- **세션 관리**: 데이터베이스에 세션 정보 저장
- **CORS 설정**: 허용된 오리진만 접근 가능

### 7.2 데이터 보안

- **SQL Injection 방지**: SQLAlchemy ORM 사용
- **XSS 방지**: React의 자동 이스케이핑
- **CSRF 방지**: SameSite 쿠키 설정
- **비밀번호 저장**: 해시화하여 저장 (원문 저장 안 함)

---

## 8. 성능 최적화

### 8.1 Backend 최적화

- **비동기 처리**: 요약 생성은 ThreadPoolExecutor로 백그라운드 처리
- **데이터베이스 연결 풀**: SQLAlchemy 연결 풀 사용
- **인덱싱**: username, email, user_id에 인덱스 설정
- **쿼리 최적화**: EXISTS 서브쿼리로 배열 검색 최적화

### 8.2 Frontend 최적화

- **컴포넌트 메모이제이션**: useCallback, useMemo 사용
- **코드 스플리팅**: React Router의 lazy loading
- **이미지 최적화**: 필요시 이미지 최적화 적용
- **페이지네이션**: 대량 데이터를 효율적으로 표시

---

## 9. 로깅 및 모니터링

### 9.1 로깅 구조

- **파일 로깅**: `backend/logs/app.log`
- **콘솔 로깅**: 개발 환경 디버깅
- **데이터베이스 로깅**: 로그를 DB에 저장하여 조회 가능
- **로그 레벨**: DEBUG, INFO, WARN, ERROR

### 9.2 로그 수집

- **프론트엔드 로그**: 브라우저에서 발생한 에러를 백엔드로 전송
- **백엔드 로그**: API 요청/응답, 에러, 비즈니스 로직 로그
- **로그 필터링**: 레벨, 소스, 검색어로 필터링 가능

---

## 10. 배포 및 운영

### 10.1 환경 요구사항

**Backend:**
- Python 3.11 이상
- PostgreSQL 데이터베이스
- Ollama 서버 (로컬 또는 원격)

**Frontend:**
- Node.js 16 이상
- npm 또는 yarn

### 10.2 배포 구성

```
┌─────────────────────────────────────────┐
│         Nginx (Reverse Proxy)           │
│  - SSL/TLS 종료                         │
│  - 정적 파일 서빙 (Frontend)            │
│  - API 프록시 (Backend)                 │
│  - 도메인: digest.aiground.ai            │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐         ┌─────▼────┐
│Frontend│         │ Backend  │
│(React) │         │(FastAPI) │
│Port 3000│        │Port 8000 │
└─────────┘         └──────────┘
```

### 10.2.1 Backend Docker 배포 (선택)

Backend는 Docker Compose로 **독립** 배포하며, **별도 Nginx**를 사용하는 경우 Compose의 Nginx는 띄우지 않아도 됩니다.

- **실행**: `cd backend && docker compose up -d` → backend만 기동. 환경 변수는 **`.env`** 파일 사용 (빌드 시에는 .env 미포함).
- **외부 DB**: `.env`에 `DB_HOST=192.168.7.89` 등 실제 DB 호스트를 두면 해당 PostgreSQL에 연결.
- **내부 Postgres**: `.env`에 `DB_HOST=postgres` 로 두고 `docker compose --profile internal-db up -d`
- **Compose Nginx**: 로컬 8080 프록시가 필요할 때만 `docker compose --profile with-nginx up -d`
- **DB 연결 검증**: `docker compose exec backend python scripts/verify_db.py`
- **상세 매뉴얼**: [backend/DOCKER_DEPLOY.md](./backend/DOCKER_DEPLOY.md)

### 10.2.2 Frontend Docker 배포 (선택)

Frontend는 Backend와 **별도**로 Docker 실행하며, frontend 디렉터리에서만 Compose를 사용합니다.

- **실행**: `cd frontend && docker compose up -d` → 포트 3000에서 React 앱 서빙 (빌드 시 `REACT_APP_API_URL=/api` 주입).
- **중지**: `cd frontend && docker compose down`
- **상세 매뉴얼**: [frontend/DOCKER_DEPLOY.md](./frontend/DOCKER_DEPLOY.md)

백엔드와 함께 사용할 때는 각각 `cd backend && docker compose up -d`, `cd frontend && docker compose up -d` 로 기동한 뒤, Nginx에서 `/` → 3000, `/api` → 8000 으로 프록시하면 됩니다.

### 10.3 Nginx 프록시 서버 설정

Nginx는 리버스 프록시 역할을 수행하며, 프론트엔드와 백엔드를 통합하여 단일 도메인으로 서비스합니다.

#### 설정 파일 위치
- `/etc/nginx/sites-available/digest.aiground.ai`
- 또는 해당 서버의 Nginx 설정 디렉토리

#### Nginx 설정 예시 (`nginx.conf.example`)

```nginx
# Nginx 설정 예시
# /etc/nginx/sites-available/digest.aiground.ai 또는 해당 위치에 설정

server {
    listen 80;
    server_name digest.aiground.ai;

    # 프론트엔드 정적 파일 및 React 앱
    location / {
        proxy_pass http://192.168.7.88:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # 백엔드 API 프록시
    location /api {
        proxy_pass http://192.168.7.88:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_buffering off;
        
        # CORS 헤더 (백엔드에서 처리하지만 추가 보안)
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Credentials true always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
        
        # OPTIONS 요청 처리
        if ($request_method = OPTIONS) {
            return 204;
        }
    }
}
```

#### 설정 설명

**프론트엔드 프록시 (`location /`):**
- `proxy_pass`: React 개발 서버 또는 빌드된 정적 파일 서버로 프록시
- `Upgrade` 및 `Connection` 헤더: WebSocket 연결 지원 (HMR 등)
- `X-Real-IP`, `X-Forwarded-For`: 클라이언트 실제 IP 전달
- `X-Forwarded-Proto`: 프로토콜 정보 전달

**백엔드 API 프록시 (`location /api`):**
- `proxy_pass`: FastAPI 백엔드 서버로 프록시
- `proxy_buffering off`: 실시간 응답을 위한 버퍼링 비활성화
- CORS 헤더: 백엔드에서 처리하지만 추가 보안을 위해 Nginx에서도 설정
- OPTIONS 요청 처리: CORS preflight 요청 처리

#### SSL/TLS 설정 (프로덕션)

프로덕션 환경에서는 SSL/TLS를 설정해야 합니다:

```nginx
server {
    listen 443 ssl http2;
    server_name digest.aiground.ai;

    # SSL 인증서 설정
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 프론트엔드 및 백엔드 프록시 설정 (위와 동일)
    # ...
}

# HTTP를 HTTPS로 리다이렉트
server {
    listen 80;
    server_name digest.aiground.ai;
    return 301 https://$server_name$request_uri;
}
```

#### Nginx 설정 적용 방법

```bash
# 설정 파일 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/digest.aiground.ai /etc/nginx/sites-enabled/

# 설정 파일 검증
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
# 또는
sudo service nginx restart
```

### 10.4 환경 변수 설정

**모든 설정값은 `.env` 파일에서 관리됩니다.** 코드에는 하드코딩된 값이 없으며, Pydantic Settings(Backend)와 React 환경 변수(Frontend)를 통해 자동으로 로드됩니다.

**Backend (.env):**
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
TRANSLATE_MODEL=translategemma:4b

# 초기 관리자 계정 설정 (db_init.py에서 사용)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
```

**Frontend (.env):**
```bash
PORT=3000
HOST=192.168.7.88

# API URL 설정
REACT_APP_API_URL=/api
REACT_APP_DEBUG=true
```

**설정 우선순위:**
- Backend: 시스템 환경 변수 → `.env` 파일 → 기본값
- Frontend: 시스템 환경 변수 → `.env` 파일 → 기본값

---

## 11. 주요 기능 상세

### 11.1 웹 스크래핑 기능

- **제목 추출 우선순위**:
  1. og:title 메타 태그
  2. article 태그 내 h1 태그
  3. 일반 h1 태그
  4. title 태그

- **콘텐츠 추출**:
  - 메인 콘텐츠 영역 자동 감지
  - 불필요한 요소 제거 (script, style, nav 등)
  - 참조 링크 및 이미지 추출

### 11.2 AI 요약 기능

- **요약 생성**: Ollama API를 통한 비동기 요약 생성
- **키워드 추출**: 자동 키워드 추출 및 태그 생성
- **분류**: 콘텐츠 분류 자동 생성
- **형식**: 마크다운 형식으로 요약 생성

### 11.3 검색 기능

- **다중 키워드 필터**: AND 조건으로 여러 키워드 검색
- **키워드 구분자 지원**: 공백, ',', '-', '·'로 구분된 키워드는 OR 조건
- **부분 일치**: LIKE 검색으로 부분 일치 지원
- **페이지네이션**: 대량 데이터 효율적 처리

---

## 12. 향후 개선 사항

### 12.1 기능 개선
- [ ] 북마크 카테고리 관리 기능 강화
- [ ] 북마크 공유 기능
- [ ] 북마크 내보내기/가져오기 기능
- [ ] 북마크 즐겨찾기 기능
- [ ] 북마크 검색 기능 강화 (전체 텍스트 검색)

### 12.2 성능 개선
- [ ] Redis 캐싱 도입
- [ ] CDN을 통한 정적 파일 서빙
- [ ] 데이터베이스 쿼리 최적화
- [ ] 프론트엔드 번들 크기 최적화

### 12.3 보안 강화
- [ ] Rate Limiting 구현
- [ ] API 키 기반 인증 추가
- [ ] 로그 보안 강화 (민감 정보 마스킹)

---

## 13. 참고 문서

- [Backend 문서](./backend/backend.md)
- [Frontend 문서](./frontend/frontend.md)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [React 공식 문서](https://react.dev/)
- [Ollama 공식 문서](https://ollama.ai/docs)

---

---

## 최근 업데이트

### 2026-02-14: 환경 변수 관리 개선 및 코드 블록 스타일 개선

#### 환경 변수 관리 개선
- **완전한 .env 파일 기반 설정**: 모든 설정값을 `.env` 파일에서 관리
- **하드코딩 제거**: Backend와 Frontend 코드에서 하드코딩된 값 제거
- **Pydantic Settings 활용**: Backend에서 환경 변수 자동 로드 및 검증
- **설정 우선순위 명확화**: 시스템 환경 변수 → `.env` 파일 → 기본값

#### 코드 블록 스타일 개선
- **다크 테마 적용**: 코드 블록 배경을 다크 그레이(`bg-gray-900`), 텍스트를 밝은 색상(`text-gray-100`)으로 변경
- **모바일 최적화**: 터치 스크롤 지원 및 반응형 스타일
- **인라인 코드**: 밝은 배경 유지로 본문과 구분

### 2026-02-14: Docker 배포 문서화
- **Backend Docker Compose**: Dockerfile, docker-compose.yml, DOCKER_DEPLOY.md 추가. 외부 PostgreSQL 사용 기본, 실행 시 `.env` 사용. postgres/nginx는 profile(internal-db, with-nginx)로 선택 기동. DB 연결 검증 스크립트(scripts/verify_db.py) 추가.
- **Frontend**: Docker 백엔드 연결 검증(verify-backend), start:docker, proxy 설정. 도메인(digest.aiground.ai) 접속 시 Invalid Host header 방지(DANGEROUSLY_DISABLE_HOST_CHECK) 반영.

### 2026-02-14: Frontend Docker 독립 구성
- **Frontend Docker**: frontend 폴더에 독립 구성 (Dockerfile, docker-compose.yml, docker/nginx.conf, DOCKER_DEPLOY.md). Backend Compose와 분리하여 `cd frontend && docker compose up -d` 로 단독 실행. 빌드 시 REACT_APP_API_URL=/api 주입.

---

**문서 버전**: 1.1  
**최종 업데이트**: 2026-02-14  
**작성자**: LinkDigest 개발팀
