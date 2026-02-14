# LinkDigest 설계서 vs 구현 검토 (Backend / Frontend)

**검토일**: 2026-02-14  
**대상**: linkdigest_설계서.md 요구사항 대비 backend / frontend 소스코드 구현 여부

---

## 1. 종합 결과

| 구분 | 결과 | 비고 |
|------|------|------|
| **구현됨** | 대부분 | API 구조, 인증, 북마크 CRUD, 검색(AND/OR), 스크래핑, 요약(비동기 3워커), 로그, UI(선택 태그·전체 제거·개수 표시) 등 |
| **부분 구현** | 일부 | 에러 코드 400/409 미반영, 조회수 중복 방지(백엔드 미구현), URL 중복 체크 없음 |
| **불일치/오류** | 소수 | bookmarks 테이블 category 오타(catergory), last_read_at 등 |

---

## 2. Backend 구현 현황

### 2.1 API 구조 (설계서 §6.1)

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| 베이스 경로 | /api | `settings.API_V1_STR` = "/api" (main.py) | ✓ |
| POST /auth/login | 있음 | auth.py login_for_access_token | ✓ |
| POST /auth/logout | 있음 | auth.py logout | ✓ |
| GET /auth/me | 있음 | auth.py get_current_user_info | ✓ |
| GET/POST/PUT/DELETE /bookmarks | 있음 | bookmarks.py | ✓ |
| GET /bookmarks/{id} | 있음 | read_bookmark | ✓ |
| POST /bookmarks/{id}/increase-read-count | 있음 | increase_read_count | ✓ |
| GET/POST /logs, GET /logs/stats | 있음 | logs.py | ✓ |

### 2.2 API 에러 응답 (설계서 §6.3)

| HTTP 코드 | 설계서 | 구현 | 비고 |
|-----------|--------|------|------|
| 400 | 잘못된 URL 등 | **미구현** | 북마크 생성 시 URL 유효성 검사 후 400 반환 없음. 스크래핑 실패 시 500만 반환 |
| 401 | 인증 실패·토큰 만료 | auth 401, security get_current_user 401 | ✓ |
| 403 | 권한 없음 | bookmarks update/delete 403 | ✓ |
| 409 | 중복 URL | **미구현** | create_bookmark 전에 동일 user_id+url 조회 후 409 반환 없음 |
| 500 | 스크래핑/서버 오류 | create_bookmark, auth, logs 등 | ✓ |

**권장**: `create_bookmark`에서 (1) URL 형식 검사 후 실패 시 400, (2) 동일 사용자·동일 URL 존재 시 409 반환 추가.

### 2.3 조회수 증가 정책 (설계서 §6.4)

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| GET 상세 또는 POST increase-read-count | 상세 조회 시 증가 | 프론트: 상세 진입 시 POST increase-read-count 호출 | ✓ |
| 중복 증가 방지 (세션/사용자·시간) | 동일 세션 또는 사용자에 대해 일정 시간 내 1회만 | **백엔드 미구현** | increase_read_count는 호출 시마다 +1. 프론트는 useRef로 같은 bookmark.id당 1회만 호출 |
| last_read_at | - | crud에 `last_read_at = datetime.utcnow()` 설정 | Bookmark 모델에 `last_read_at` 컬럼 없음 → 런타임 오류 가능. 설계서 ERD에는 없음 |

**권장**: (1) 백엔드에서 세션/사용자+북마크+시간창 기준 중복 호출 시 200만 반환하고 조회수는 증가하지 않도록 처리 검토. (2) last_read_at 사용 시 Bookmark 모델·DB에 컬럼 추가하거나 해당 라인 제거.

### 2.4 데이터베이스 (설계서 §5)

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| users, bookmarks, logs, sessions | 있음 | models + init.sql | ✓ |
| CASCADE 삭제 | user 삭제 시 bookmark·session CASCADE | Bookmark: ForeignKey ondelete="CASCADE", Session: ondelete="CASCADE", init.sql ON DELETE CASCADE | ✓ |
| Pydantic 검증 | 입력 검증 | 스키마(BookmarkCreate 등) 사용 | ✓ |
| bookmarks.category | category | **catergory** (모델·summary_tasks 오타) | 설계서·PRD는 category. init.sql bookmarks에는 category/catergory 컬럼 없음 |

**권장**: `catergory` → `category` 로 통일하고, init.sql에 column 없으면 마이그레이션 또는 스키마 정리.

### 2.5 스크래핑·요약 (설계서 §11.1, §11.2)

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| 제목 추출 순서 | og:title → article h1 → h1 → title | scraping_service._extract_title 동일 순서 | ✓ |
| 콘텐츠 추출 | 메인 영역, script/style/nav 제거, 링크·이미지 | _extract_content | ✓ |
| 비동기 요약, 워커 3개 | ThreadPoolExecutor 최대 3개 | summary_tasks: `ThreadPoolExecutor(max_workers=3)` | ✓ |
| "요약 생성 중..." | 표시 | create 시 summary='요약 생성 중...' 저장 | ✓ |

### 2.6 보안 (설계서 §7)

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| JWT 30분 | 30분 만료 | config ACCESS_TOKEN_EXPIRE_MINUTES=30 | ✓ |
| bcrypt | 비밀번호 해싱 | security (passlib) | ✓ |
| 세션 DB 저장 | sessions 테이블 | auth 로그인 시 Session 생성, 로그아웃 시 비활성화 | ✓ |
| CORS | 허용 오리진만 | CORSMiddleware, settings.BACKEND_CORS_ORIGINS | ✓ |
| 민감 정보 로그 미기록 | 비밀번호·토큰 로그 금지 | 코드상 비밀번호/토큰 직접 로깅 없음 | ✓ |

### 2.7 북마크 목록·검색 (설계서 §6.2)

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| page, per_page, tags | 쿼리 파라미터 | get_bookmarks(page, per_page, tags) | ✓ |
| tags AND 조건 | 여러 태그 AND | get_multi_by_owner_with_tags, count_by_owner_with_tags | ✓ |
| 태그 내 구분자 OR | 공백, ',', '-', '·' | split_keyword_by_delimiters(r'[\s,\-·]+') | ✓ |
| 부분 일치 | LIKE | crud 태그 검색 부분 일치 | ✓ |
| 응답 형식 items/total/page/per_page/total_pages | 동일 | BookmarkListResponse | ✓ |

---

## 3. Frontend 구현 현황

### 3.1 아키텍처 (설계서 §4.2)

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| Context API (인증) | AuthContext | contexts/AuthContext.js | ✓ |
| API 레이어 | utils/api.js | axiosInstance, api.auth, api.bookmarks, api.logs | ✓ |
| 라우팅 | React Router | App.js 등 | ✓ |
| 컴포넌트 | BookmarkList, BookmarkDetail, Login, LogViewer 등 | components/ | ✓ |

### 3.2 검색·필터 UI (설계서 §11.3)

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| 선택된 키워드 파란색 배경 | 파란색 배경 | BookmarkList: 선택 태그 `bg-blue-500`, 미선택 `bg-blue-100` | ✓ |
| 필터 개별 제거 X 버튼 | 각 키워드 X | selectedTags.map + "X" 버튼 (className text-blue-600) | ✓ |
| "전체 제거" 버튼 | 전체 제거 | "전체 제거" 버튼 (line 289) | ✓ |
| 결과 개수 표시 | "북마크 목록(N개)" | "북마크 요약(totalItems개)" (line 262) | ✓ 표현만 "요약"으로 다름 |

### 3.3 조회수 증가

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| 상세 진입 시 조회수 증가 | GET 상세 또는 별도 증가 | BookmarkDetail useEffect에서 api.bookmarks.increaseReadCount(bookmark.id) 호출 | ✓ |
| 중복 방지 | 세션/사용자·시간 | useRef(readCountIncreasedRef, isIncreasingRef)로 같은 bookmark.id당 1회만 호출 | ✓ (클라이언트 기준) |

### 3.4 기타

| 항목 | 설계서 | 구현 | 비고 |
|------|--------|------|------|
| REACT_APP_API_URL | /api | api.js getApiBaseURL(), 기본 '/api' | ✓ |
| 로딩·에러 표시 | 로딩 상태, 에러 메시지 | LoadingSpinner, 에러 메시지 노출 | ✓ |
| 요약 생성 중 표시 | "요약 생성 중..." | BookmarkDetail에서 summary === '요약 생성 중...' 시 처리 | ✓ |

---

## 4. 미구현·불일치 요약 및 권장 조치

| 우선순위 | 항목 | 조치 |
|----------|------|------|
| **높음** | 북마크 생성 시 400(잘못된 URL)·409(중복 URL) | create_bookmark에서 URL 검증 후 400, 동일 user_id+url 조회 후 409 반환 추가 |
| **높음** | Bookmark 모델 last_read_at | 모델·DB에 last_read_at 추가하거나 crud에서 해당 대입 제거 (런타임 오류 방지) |
| **중간** | category 오타 | catergory → category 로 통일. init.sql에 컬럼 없으면 추가 또는 제거 후 마이그레이션 |
| **중간** | 조회수 중복 증가 방지 (서버) | (선택) increase_read_count에서 세션/사용자+북마크+시간창 기준 이미 증가했으면 스킵 |
| **낮음** | 목록 제목 문구 | "북마크 요약(N개)" → "북마크 목록(N개)" 로 통일 가능 (설계서 문구에 맞춤) |

---

## 5. 결론

- **전체적으로 설계서의 API 구조, 인증, 북마크 CRUD, 태그 검색(AND/OR·부분일치), 스크래핑 순서, 비동기 요약(3 워커), 로그, CORS, JWT 30분, CASCADE, Pydantic 등은 구현되어 있음.**
- **부족한 부분**: (1) API 에러 400/409 미사용, (2) 북마크 생성 전 URL 중복 체크 없음, (3) 조회수 서버 측 중복 방지 없음, (4) Bookmark 모델과 crud의 last_read_at 불일치, (5) category/catergory 오타 및 init.sql과의 정합성.

위 권장 조치를 반영하면 설계서와 구현이 더 잘 맞춰진다.
