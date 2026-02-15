# Frontend 문서

## 목차
1. [소스코드 구조](#소스코드-구조)
2. [주요 기능](#주요-기능)
3. [사용자 가이드](#사용자-가이드)
4. [컴포넌트 설명](#컴포넌트-설명)
5. [환경 설정](#환경-설정)
6. [실행 방법](#실행-방법)

---

## 소스코드 구조

### 디렉토리 구조

```
frontend/
├── public/                      # 정적 파일
│   ├── index.html              # HTML 템플릿
│   ├── manifest.json           # PWA 매니페스트
│   └── robots.txt              # 검색 엔진 설정
├── src/
│   ├── components/             # React 컴포넌트
│   │   ├── AddBookmark.js      # 북마크 추가 컴포넌트
│   │   ├── BookmarkList.js     # 북마크 목록 컴포넌트
│   │   ├── BookmarkDetail.js   # 북마크 상세보기 컴포넌트
│   │   ├── EditBookmark.js     # 북마크 수정 컴포넌트
│   │   ├── DeleteBookmark.js   # 북마크 삭제 컴포넌트
│   │   ├── Login.js            # 로그인 컴포넌트
│   │   ├── Navigation.js       # 네비게이션 바 컴포넌트
│   │   ├── ProtectedRoute.js   # 인증 보호 라우트 컴포넌트
│   │   ├── ErrorBoundary.js    # 에러 경계 컴포넌트
│   │   ├── ErrorMessage.js     # 에러 메시지 컴포넌트
│   │   ├── ErrorDisplay.js     # 에러 표시 컴포넌트
│   │   ├── LoadingSpinner.js   # 로딩 스피너 컴포넌트
│   │   ├── Pagination.js       # 페이지네이션 컴포넌트
│   │   ├── LogViewer.js        # 로그 뷰어 메인 컴포넌트
│   │   ├── LogTable.js         # 로그 테이블 컴포넌트
│   │   ├── LogFilter.js        # 로그 필터 컴포넌트
│   │   ├── LogStats.js         # 로그 통계 컴포넌트
│   │   ├── LogDetailModal.js   # 로그 상세 모달 컴포넌트
│   │   └── AutoRefresh.js      # 자동 새로고침 컴포넌트
│   ├── contexts/               # React Context
│   │   └── AuthContext.js      # 인증 컨텍스트
│   ├── hooks/                  # Custom Hooks
│   │   └── useDebounce.js      # 디바운스 훅
│   ├── utils/                  # 유틸리티 함수
│   │   ├── api.js              # API 통신 유틸리티
│   │   ├── axios.js            # Axios 설정 (사용 안 함)
│   │   ├── dateUtils.js        # 날짜 포맷 유틸리티
│   │   └── logger.js           # 로깅 유틸리티
│   ├── types/                  # TypeScript 타입 정의
│   │   └── bookmark.ts         # 북마크 타입 정의
│   ├── App.js                  # 메인 앱 컴포넌트
│   ├── index.js                # 진입점
│   ├── index.css               # 전역 스타일
│   └── reportWebVitals.js      # 성능 측정
├── scripts/                    # 유틸리티 스크립트
│   └── verify-backend.js       # Docker 백엔드 연결 검증
├── docker/                     # Docker 관련 설정
│   └── nginx.conf              # SPA 정적 서빙용 Nginx 설정
├── Dockerfile                  # 프론트엔드 Docker 이미지 (멀티 스테이지: Node 빌드 → Nginx)
├── docker-compose.yml          # 프론트엔드 단독 Compose (Backend와 분리)
├── .dockerignore
├── DOCKER_DEPLOY.md            # Docker 배포 매뉴얼 (독립 실행)
├── .env                        # 환경 변수 설정
├── .env.docker.example         # Docker 백엔드 연결 시 환경 변수 예시
├── package.json                # 패키지 의존성 및 스크립트 (proxy, start:docker, verify-backend)
├── tailwind.config.js          # Tailwind CSS 설정
└── .eslintrc.js               # ESLint 설정
```

### 아키텍처 패턴

이 프로젝트는 **컴포넌트 기반 아키텍처(Component-Based Architecture)** 패턴을 따릅니다:

1. **Presentation Layer**: React 컴포넌트로 UI 렌더링
2. **State Management Layer**: Context API를 통한 전역 상태 관리
3. **Service Layer**: API 유틸리티를 통한 백엔드 통신
4. **Routing Layer**: React Router를 통한 라우팅 관리

---

## 주요 기능

### 1. 사용자 인증

- **JWT 기반 인증**: 로컬 스토리지에 토큰 저장
- **자동 인증 확인**: 앱 시작 시 토큰 검증
- **보호된 라우트**: 인증되지 않은 사용자 접근 차단
- **자동 로그아웃**: 401 에러 시 자동 로그아웃

**주요 기능:**
- 로그인/로그아웃
- 인증 상태 관리 (Context API)
- 토큰 자동 갱신 (요청 인터셉터)

### 2. 북마크 관리

- **북마크 목록**: 페이지네이션 지원
- **북마크 추가**: URL 입력으로 자동 스크래핑
- **북마크 수정**: 제목, URL, 태그, 요약 수정
- **북마크 삭제**: 확인 모달과 함께 삭제
- **북마크 상세보기**: 마크다운 형식으로 콘텐츠 표시
- **조회수 추적**: 북마크 조회 시 자동 증가
- **다중 키워드 필터 검색**: 여러 키워드를 AND 조건으로 필터링 (부분 일치 지원)

**주요 기능:**
- 실시간 북마크 목록 업데이트
- 태그 필터링 및 표시
- **다중 키워드 선택**: 여러 키워드를 동시에 선택하여 AND 조건으로 검색
- **키워드 추가/제거**: 클릭으로 키워드 추가, 다시 클릭하거나 X 버튼으로 제거
- **필터 시각화**: 선택된 키워드를 파란색 배경으로 표시
- 마크다운 렌더링 (react-markdown)
- 이미지 및 링크 자동 렌더링

### 3. 로그 뷰어

- **로그 목록**: 페이지네이션 지원
- **로그 필터링**: 레벨(INFO, WARN, ERROR), 소스(frontend/backend) 필터
- **로그 검색**: 메시지 내용 검색
- **로그 통계**: 전체 통계 및 최근 24시간 통계
- **자동 새로고침**: 설정 가능한 간격으로 자동 업데이트
- **로그 상세보기**: 모달을 통한 상세 정보 표시

**주요 기능:**
- 실시간 로그 업데이트
- 로그 레벨별 색상 구분
- 로그 소스별 필터링
- 통계 대시보드

### 4. 에러 처리

- **Error Boundary**: React Error Boundary를 통한 에러 캐칭
- **에러 로깅**: 프론트엔드 에러를 백엔드로 전송
- **사용자 친화적 에러 메시지**: 명확한 에러 메시지 표시
- **자동 복구**: 에러 발생 시 새로고침 옵션 제공

### 5. UI/UX 기능

- **반응형 디자인**: Tailwind CSS를 사용한 모던한 UI
- **로딩 상태 표시**: 비동기 작업 중 로딩 스피너
- **모달 다이얼로그**: 북마크 추가/수정/삭제 시 모달 사용
- **페이지네이션**: 대량 데이터를 효율적으로 표시
- **자동 새로고침**: 로그 뷰어에서 자동 업데이트

---

## 사용자 가이드

### 1. 환경 설정

#### 필수 요구사항

- Node.js 16 이상
- npm 또는 yarn

#### 환경 변수 설정

`.env` 파일 생성 또는 환경 변수 설정:

```bash
# 포트 설정
PORT=3000

# 호스트 설정 (원격 접속 시)
HOST=192.168.7.88
# 또는
# HOST=localhost  # 로컬 개발 시

# 백엔드 API URL
REACT_APP_API_URL=http://192.168.7.88:8000/api
# 또는
# REACT_APP_API_URL=http://localhost:8000/api

# 디버그 모드
REACT_APP_DEBUG=true
```

### 2. 패키지 설치

```bash
cd frontend
npm install
```

또는

```bash
yarn install
```

### 3. 개발 서버 실행

#### 로컬 개발

```bash
npm start
```

기본적으로 `http://localhost:3000`에서 실행됩니다.

#### 원격 접속 (192.168.7.88)

```bash
npm run start:192.168.7.88
```

또는

```bash
PORT=3000 HOST=192.168.7.88 npm start
```

#### 다른 IP 사용

```bash
npm run start:remote
```

또는 `.env` 파일에서 `HOST` 설정

### 4. 프로덕션 빌드

```bash
npm run build
```

빌드된 파일은 `build/` 디렉토리에 생성됩니다.

### 5. 테스트 실행

```bash
npm test
```

---

## 컴포넌트 설명

### App.js

메인 애플리케이션 컴포넌트로, 라우팅과 전역 상태 관리를 담당합니다.

**주요 기능:**
- React Router를 통한 라우팅 설정
- AuthProvider를 통한 인증 상태 관리
- ErrorBoundary를 통한 에러 처리

**라우트:**
- `/login`: 로그인 페이지
- `/` 또는 `/bookmarks`: 북마크 목록 페이지
- `/add-bookmark`: 북마크 추가 페이지
- `/logs`: 로그 뷰어 페이지

### AuthContext.js

인증 관련 전역 상태를 관리하는 Context입니다.

**제공하는 값:**
- `user`: 현재 로그인한 사용자 정보
- `loading`: 인증 확인 중 여부
- `login(username, password)`: 로그인 함수
- `logout()`: 로그아웃 함수

**사용 예시:**
```javascript
import { useAuth } from '../contexts/AuthContext';

const MyComponent = () => {
    const { user, login, logout } = useAuth();
    // ...
};
```

### api.js

백엔드 API와 통신하는 유틸리티 모듈입니다.

**주요 기능:**
- Axios 인스턴스 생성 및 설정
- 요청/응답 인터셉터 설정
- JWT 토큰 자동 추가
- 401 에러 시 자동 로그아웃
- 커스텀 `paramsSerializer`: FastAPI 배열 쿼리 파라미터 형식 지원 (`tags=AI&tags=코딩`)

**API 엔드포인트:**
- `auth.login()`: 로그인
- `auth.logout()`: 로그아웃
- `auth.me()`: 현재 사용자 정보 조회
- `bookmarks.create()`: 북마크 생성 (선택: `summary_model` 요약 모델 지정)
- `bookmarks.getSummaryModels()`: 요약에 사용 가능한 모델 목록 조회
- `bookmarks.getList()`: 북마크 목록 조회
- `bookmarks.update()`: 북마크 수정
- `bookmarks.delete()`: 북마크 삭제
- `bookmarks.getDetail()`: 북마크 상세 조회
- `bookmarks.increaseReadCount()`: 조회수 증가
- `bookmarks.share()`: 북마크 공유 (Slack/Notion)
- `logs.getList()`: 로그 목록 조회
- `logs.getStats()`: 로그 통계 조회
- `logs.save()`: 로그 저장

### BookmarkList.js

북마크 목록을 표시하는 메인 컴포넌트입니다.

**주요 기능:**
- 북마크 목록 조회 및 표시
- 페이지네이션 (상단/하단)
- 북마크 추가/수정/삭제 모달 관리
- 북마크 상세보기 (인라인 표시)
- 태그 표시 및 다중 키워드 필터 검색
- 반응형 디자인 (모바일/PC 최적화)

**상태 관리:**
- `bookmarks`: 북마크 목록
- `currentPage`: 현재 페이지
- `totalPages`: 전체 페이지 수
- `totalItems`: 전체 북마크 개수 (필터링된 결과 포함)
- `selectedTags`: 선택된 키워드 배열 (다중 필터)
- `showAddModal`: 추가 모달 표시 여부
- `showEdit`: 수정 모달 표시 여부
- `showDetail`: 상세보기 표시 여부

**필터 검색 기능:**
- 다중 키워드 선택: 여러 키워드를 동시에 선택하여 AND 조건으로 검색
- 키워드 토글: 키워드 클릭 시 추가/제거 토글
- 개별 제거: 각 필터 키워드에 X 버튼으로 개별 제거
- 전체 제거: "전체 제거" 버튼으로 모든 필터 한 번에 제거
- 시각적 표시: 선택된 키워드는 파란색 배경으로 표시
- 키워드 구분자 지원: 백엔드에서 하나의 키워드 내부 구분자(공백, ',', '-', '·')를 OR 조건으로 처리
- 총 개수 표시: 북마크 목록 제목에 필터링된 결과의 총 개수 표시 (예: "북마크 목록(100개)")

### BookmarkDetail.js

북마크 상세 정보를 표시하는 컴포넌트입니다.

**주요 기능:**
- 마크다운 형식으로 콘텐츠 렌더링
- 요약/원본 콘텐츠 전환
- 이미지 및 링크 자동 렌더링
- 조회수 증가

**사용 라이브러리:**
- `react-markdown`: 마크다운 렌더링
- `remark-gfm`: GitHub Flavored Markdown 지원
- `rehype-raw`: HTML 태그 렌더링

### LogViewer.js

로그 뷰어 메인 컴포넌트입니다.

**주요 기능:**
- 로그 목록 조회 및 표시
- 로그 필터링 (레벨, 소스, 검색)
- 로그 통계 표시
- 자동 새로고침
- 페이지네이션

**상태 관리:**
- `logs`: 로그 목록
- `filter`: 필터 설정
- `autoRefresh`: 자동 새로고침 활성화 여부
- `refreshInterval`: 새로고침 간격 (초)
- `stats`: 로그 통계

### ProtectedRoute.js

인증이 필요한 라우트를 보호하는 컴포넌트입니다.

**동작 방식:**
- 사용자가 로그인하지 않았으면 `/login`으로 리다이렉트
- 로딩 중이면 로딩 메시지 표시
- 인증된 사용자만 자식 컴포넌트 렌더링

### ErrorBoundary.js

React 컴포넌트 에러를 캐치하는 에러 경계입니다.

**주요 기능:**
- 컴포넌트 트리에서 발생한 에러 캐치
- 에러 정보를 백엔드로 전송
- 사용자 친화적인 에러 메시지 표시
- 페이지 새로고침 옵션 제공

### logger.js

프론트엔드 로깅 유틸리티입니다.

**주요 기능:**
- 콘솔 로깅
- 백엔드로 로그 전송
- 로그 레벨 관리 (INFO, WARN, ERROR)
- 사용자 ID 및 타임스탬프 자동 추가

**사용 예시:**
```javascript
import logger from './utils/logger';

logger.info('정보 메시지', { data: '추가 데이터' });
logger.warn('경고 메시지');
logger.error('에러 메시지', { error: errorObject });
```

---

## 환경 설정

### Tailwind CSS 설정

`tailwind.config.js`에서 Tailwind CSS 설정:

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

**플러그인:**
- `@tailwindcss/forms`: 폼 스타일링
- `@tailwindcss/typography`: 타이포그래피 유틸리티

### API URL 설정

**모든 설정값은 `.env` 파일에서 관리됩니다.**

`.env` 파일에서 백엔드 API URL 설정:

```bash
PORT=3000
HOST=192.168.7.88

# API URL 설정
REACT_APP_API_URL=/api
REACT_APP_DEBUG=true
```

**중요 사항:**
- React 앱은 다음 순서로 환경 변수를 로드합니다:
  1. 시스템 환경 변수 (최우선)
  2. `.env` 파일의 값
  3. 기본값 (fallback)
- `src/utils/api.js`와 `src/utils/axios.js`는 모두 `.env` 파일의 `REACT_APP_API_URL` 값을 사용합니다.
- 코드에는 하드코딩된 기본값만 있으며, 실제 설정은 `.env` 파일에서 관리합니다.

### CORS 설정

백엔드에서 CORS가 올바르게 설정되어 있어야 합니다. 프론트엔드 URL이 백엔드의 `BACKEND_CORS_ORIGINS`에 포함되어 있어야 합니다.

---

## 실행 방법

### 개발 환경

```bash
# 1. 패키지 설치
npm install

# 2. 환경 변수 설정
# .env 파일 생성 또는 환경 변수 설정

# 3. 개발 서버 실행
npm start
```

개발 서버는 기본적으로 `http://localhost:3000`에서 실행됩니다.

### 프로덕션 빌드

```bash
# 1. 빌드
npm run build

# 2. 빌드된 파일 서빙
# build/ 디렉토리의 파일을 웹 서버에 배포
```

### 특정 IP에서 실행

```bash
# 방법 1: npm 스크립트 사용
npm run start:192.168.7.88

# 방법 2: 환경 변수 설정
PORT=3000 HOST=192.168.7.88 npm start

# 방법 3: .env 파일 설정
HOST=192.168.7.88
PORT=3000
```

### Docker 배포 (독립 실행)

프론트엔드는 **Backend와 별도**로 Docker로 실행합니다. frontend 디렉터리에서만 Compose를 사용합니다.

- **실행**: `cd frontend && docker compose up -d` → http://localhost:3000 에서 서빙. 빌드 시 `REACT_APP_API_URL=/api` 가 주입됩니다.
- **중지**: `cd frontend && docker compose down`
- **상세**: [DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md) 참고.

백엔드도 Docker로 띄울 때는 `cd backend && docker compose up -d` 로 별도 실행하고, Nginx에서 `/` → 3000, `/api` → 8000 으로 프록시하면 됩니다.

### Docker 백엔드 연결 (개발 시)

- **package.json proxy**: 개발 서버가 `/api` 요청을 백엔드(기본 `http://localhost:8000`)로 전달합니다. `http://192.168.7.88:3000` 접속 시 로그인 등 API가 동작하려면 같은 호스트에서 백엔드를 8000으로 띄워 두어야 합니다.
- **도메인 접속(digest.aiground.ai)**: Nginx로 접속할 때 "Invalid Host header"가 나지 않도록 `.env`에 `DANGEROUSLY_DISABLE_HOST_CHECK=true` 설정이 필요합니다. (별도 Nginx가 `/` → 3000, `/api` → 8000으로 프록시하는 구성)
- **Docker 백엔드 검증**: `npm run verify-backend` (8000 직접), `npm run verify-backend:nginx` (8080 경유). 백엔드가 Docker로 8000에서 동작 중일 때 사용합니다.
- **Docker 백엔드 전용 기동**: `npm run start:docker` → `REACT_APP_API_URL=http://localhost:8000/api` 로 프론트만 띄워 Docker 백엔드에 연결할 때 사용합니다.
- **환경 예시**: `.env.docker.example` 에 Docker 백엔드 연결용 `REACT_APP_API_URL` 예시가 있습니다.

---

## 주요 기술 스택

- **UI 프레임워크**: React 18.2.0
- **라우팅**: React Router DOM 6.22.1
- **HTTP 클라이언트**: Axios 1.6.7
- **스타일링**: Tailwind CSS 3.4.17
- **마크다운 렌더링**: react-markdown 9.0.3
- **날짜 처리**: date-fns 2.30.0
- **아이콘**: Heroicons React 2.2.0
- **빌드 도구**: React Scripts 5.0.1

---

## 주요 기능 상세 설명

### 1. 북마크 추가 플로우

1. 북마크 추가 모달에서 **요약 모델** 선택 (드롭다운, `GET /api/bookmarks/summary-models` 연동)
2. 사용자가 URL 입력 (필수), 제목·키워드(선택)
3. 백엔드로 북마크 생성 요청 (선택한 `summary_model` 포함)
4. 백엔드에서 웹 스크래핑 수행
5. 제목 자동 추출 및 번역
6. 북마크 생성 완료
7. 백그라운드에서 요약 생성 시작 (선택된 모델 사용)
8. 프론트엔드에서 북마크 목록 업데이트

### 2. 인증 플로우

1. 사용자가 로그인 페이지에서 자격 증명 입력
2. 백엔드로 로그인 요청
3. JWT 토큰 수신
4. 로컬 스토리지에 토큰 저장
5. 모든 API 요청에 토큰 자동 추가
6. 401 에러 시 자동 로그아웃

### 3. 로그 뷰어 플로우

1. 로그 뷰어 페이지 진입
2. 필터 설정 (레벨, 소스, 검색어)
3. 백엔드로 로그 목록 요청
4. 로그 통계 조회
5. 자동 새로고침 설정 시 주기적 업데이트
6. 로그 클릭 시 상세 정보 모달 표시

---

## 스타일 가이드

### 컴포넌트 구조

```javascript
import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const MyComponent = () => {
    // 상태 선언
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    
    // 효과 훅
    useEffect(() => {
        // 데이터 로딩
    }, []);
    
    // 이벤트 핸들러
    const handleClick = () => {
        // 처리 로직
    };
    
    // 렌더링
    return (
        <div className="container">
            {/* JSX */}
        </div>
    );
};

export default MyComponent;
```

### API 호출 패턴

```javascript
try {
    setLoading(true);
    const response = await api.bookmarks.getList({ page: 1 });
    setData(response.items);
} catch (error) {
    setError(error.message);
} finally {
    setLoading(false);
}
```

### 에러 처리 패턴

```javascript
try {
    // API 호출
} catch (error) {
    logger.error('에러 발생', { error });
    setError('에러 메시지');
}
```

---

## 문제 해결

### CORS 오류

- 백엔드의 `BACKEND_CORS_ORIGINS`에 프론트엔드 URL이 포함되어 있는지 확인
- 브라우저 개발자 도구에서 실제 오리진 확인

### API 연결 실패

- `.env` 파일의 `REACT_APP_API_URL` 확인
- 백엔드 서버가 실행 중인지 확인
- 네트워크 연결 확인

### 빌드 오류

- Node.js 버전 확인 (16 이상 권장)
- `node_modules` 삭제 후 재설치:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

### 스타일이 적용되지 않음

- Tailwind CSS 설정 확인
- `tailwind.config.js`의 `content` 경로 확인
- 빌드 후 캐시 클리어

---

## 추가 리소스

- [React 문서](https://react.dev/)
- [React Router 문서](https://reactrouter.com/)
- [Tailwind CSS 문서](https://tailwindcss.com/)
- [Axios 문서](https://axios-http.com/)
- [react-markdown 문서](https://github.com/remarkjs/react-markdown)

---

## 개발 팁

### 1. 컴포넌트 최적화

- `useCallback`을 사용하여 함수 메모이제이션
- `useMemo`를 사용하여 계산 결과 메모이제이션
- 불필요한 리렌더링 방지

### 2. 상태 관리

- 로컬 상태는 `useState` 사용
- 전역 상태는 Context API 사용
- 복잡한 상태는 상태 관리 라이브러리 고려

### 3. 에러 처리

- 모든 API 호출에 try-catch 사용
- ErrorBoundary로 컴포넌트 에러 캐치
- 사용자 친화적인 에러 메시지 제공

### 4. 성능 최적화

- 코드 스플리팅 사용
- 이미지 최적화
- 불필요한 리렌더링 방지
- React DevTools Profiler 사용

---

## 수정 이력

### 2026-02-12: 북마크 상세보기 UI 개선

**수정 내용:**
- 팝업 모달 방식에서 메인 페이지 표시 방식으로 변경
- 상세보기 상단에 "리스트로 돌아가기" 버튼과 페이지네이션을 같은 라인에 배치
- 기존 로직(조회수 증가, 요약 확인 등) 유지

**수정된 파일:**

#### 1. `src/components/BookmarkList.js`

```javascript
import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import AddBookmark from './AddBookmark';
import EditBookmark from './EditBookmark';
import BookmarkDetail from './BookmarkDetail';
import ErrorMessage from './ErrorMessage';
import DeleteBookmark from './DeleteBookmark';
import { formatDate } from '../utils/dateUtils';
import LoadingSpinner from './LoadingSpinner';

// eslint-disable-next-line no-unused-vars
const EllipsisIcon = () => (
    <svg className="h-5 w-5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
    </svg>
);

const BookmarkList = () => {
    const [bookmarks, setBookmarks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showAddModal, setShowAddModal] = useState(false);
    const [selectedBookmark, setSelectedBookmark] = useState(null);
    const [showDetail, setShowDetail] = useState(false);
    const [showEdit, setShowEdit] = useState(false);
    const [showDelete, setShowDelete] = useState(false);
    
    // 페이지네이션 상태 관리
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    // totalItems는 실제로 사용되므로 유지하되 total_pages 계산에 사용
    // eslint-disable-next-line no-unused-vars
    const [totalItems, setTotalItems] = useState(0);
    const ITEMS_PER_PAGE = 10;

    // fetchBookmarks를 useCallback으로 메모이제이션
    const fetchBookmarks = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.bookmarks.getList({
                page: currentPage,
                per_page: ITEMS_PER_PAGE
            });
            
            const { items, total, total_pages } = response;
            
            setBookmarks(items);
            setTotalItems(total);
            setTotalPages(total_pages);
        } catch (err) {
            setError('북마크 목록을 불러오는데 실패했습니다.');
            console.error('북마크 목록 조회 실패:', err);
            setBookmarks([]);
            setTotalPages(1);
            setTotalItems(0);
        } finally {
            setLoading(false);
        }
    }, [currentPage, ITEMS_PER_PAGE]);

    // 페이지 변경 핸들러 개선
    const handlePageChange = (page) => {
        if (page !== currentPage) {
            setCurrentPage(page);
            // 페이지 변경 시 스크롤을 상단으로 이동
            window.scrollTo(0, 0);
        }
    };

    // 페이지 변경 시 데이터 다시 로드
    useEffect(() => {
        fetchBookmarks();
    }, [currentPage, fetchBookmarks]);

    const handleDelete = async (id) => {
        try {
            await api.bookmarks.delete(id);
            
            // 현재 페이지의 마지막 아이템을 삭제하는 경우
            if (bookmarks.length === 1 && currentPage > 1) {
                // 이전 페이지로 이동
                setCurrentPage(prev => prev - 1);
            } else {
                // 현재 페이지 새로고침
                fetchBookmarks();
            }
        } catch (err) {
            setError('북마크 삭제에 실패했습니다.');
            console.error('북마크 삭제 실패:', err);
        }
    };

    const handleUpdate = (updatedBookmark) => {
        fetchBookmarks();
    };

    const handleAdd = async (newBookmark) => {
        try {
            // 북마크 추가 후 항상 첫 페이지로 이동
            setCurrentPage(1);
            await fetchBookmarks();
            setShowAddModal(false);
        } catch (err) {
            setError('북마크 목록 갱신에 실패했습니다.');
            console.error('북마크 목록 갱신 실패:', err);
        }
    };

    // eslint-disable-next-line no-unused-vars
    const handleViewClick = async (e, bookmark) => {
        e.stopPropagation();
        if (!bookmark?.id) {
            console.error('유효하지 않은 북마크');
            return;
        }

        try {
            const updatedBookmark = await api.bookmarks.getById(bookmark.id);
            if (updatedBookmark) {
                setSelectedBookmark(updatedBookmark);
                setShowDetail(true);
            }
        } catch (error) {
            console.error('북마크 상세 정보 조회 실패:', error);
            setError('북마크 상세 정보를 불러오는데 실패했습니다.');
        }
    };

    // eslint-disable-next-line no-unused-vars
    const handleEditClick = (e, bookmark) => {
        e.stopPropagation();
        setSelectedBookmark(bookmark);
        setShowEdit(true);
    };

    // eslint-disable-next-line no-unused-vars
    const handleDeleteClick = (e, bookmark) => {
        e.stopPropagation();
        setSelectedBookmark(bookmark);
        setShowDelete(true);
    };

    // eslint-disable-next-line no-unused-vars
    const handleTitleClick = async (e, bookmark) => {
        e.preventDefault();
        try {
            const updatedBookmark = await api.bookmarks.getById(bookmark.id);
            setSelectedBookmark(updatedBookmark);
            setShowDetail(true);
        } catch (error) {
            console.error('북마크 상세 정보 조회 실패:', error);
            setError('북마크 상세 정보를 불러오는데 실패했습니다.');
        }
    };

    // 북마크 목록 새로고침 함수
    const refreshBookmarks = useCallback(async () => {
        try {
            // 토큰 유효성 먼저 확인
            await api.auth.me();  // 현재 사용자 정보 확인
            await fetchBookmarks();
        } catch (error) {
            if (error.response?.status === 401) {
                // 토큰이 만료된 경우 로그인 페이지로 리다이렉트
                window.location.href = '/login';
            } else {
                console.error('북마크 목록 새로고침 실패:', error);
                setError('북마크 목록을 새로고침하는데 실패했습니다.');
            }
        }
    }, [fetchBookmarks]);

    // 상세보기 닫기 핸들러 수정
    const handleDetailClose = async (openEdit = false) => {  // openEdit 파라미터 추가
        setShowDetail(false);
        if (openEdit) {
            // 수정 모달 열기
            setShowEdit(true);
        } else {
            setSelectedBookmark(null);
        }
        await refreshBookmarks();
    };

    if (loading) return <div className="text-center py-4">로딩 중...</div>;

    // 상세보기가 열려있으면 상세보기만 표시
    if (showDetail && selectedBookmark) {
        return (
            <div className="container mx-auto px-4 py-8">
                <BookmarkDetail
                    bookmark={selectedBookmark}
                    onClose={handleDetailClose}
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                />
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-xl font-bold">북마크 목록</h1>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="bg-blue-500 text-white px-3 py-1.5 rounded hover:bg-blue-600 text-sm"
                >
                    새 북마크
                </button>
            </div>

            {error && <ErrorMessage message={error} />}

            {loading ? (
                <LoadingSpinner />
            ) : (
                <>
                    {/* 북마크 목록 - 카드 형태로 변경 */}
                    <div className="grid gap-4">
                        {bookmarks.map(bookmark => (
                            <div key={bookmark.id} className="bg-white rounded-lg shadow p-4">
                                {/* 북마크 제목 */}
                                <h3 
                                    className="text-base font-semibold cursor-pointer hover:text-blue-600"
                                    onClick={(e) => handleTitleClick(e, bookmark)}
                                >
                                    {bookmark.title}
                                </h3>

                                {/* 메타 정보와 액션 버튼을 같은 라인에 배치 */}
                                <div className="mt-2 flex justify-between items-center">
                                    {/* 메타 정보 */}
                                    <div className="text-sm text-gray-500 flex items-center space-x-2 flex-grow">
                                        {/* 태그/키워드 */}
                                        {bookmark.tags && bookmark.tags.length > 0 && (
                                            <div className="flex items-center space-x-1">
                                                {bookmark.tags.map((tag, idx) => (
                                                    <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                                                        {tag}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                        <span className="text-gray-300">|</span>
                                        <span>조회수: {bookmark.read_count || 0}</span>
                                        <span className="text-gray-300">|</span>
                                        <span>{formatDate(bookmark.created_at)}</span>
                                        <span className="text-gray-300">|</span>
                                        <span>{bookmark.source_name || '-'}</span>
                                    </div>

                                    {/* 액션 버튼들 */}
                                    <div className="flex items-center space-x-3 ml-4">
                                        {/* 상세보기 버튼 */}
                                        <button 
                                            onClick={(e) => handleViewClick(e, bookmark)}
                                            className="text-blue-600 hover:text-blue-800"
                                            title="상세보기"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                            </svg>
                                        </button>
                                        {/* 수정 버튼 */}
                                        <button 
                                            onClick={(e) => handleEditClick(e, bookmark)}
                                            className="text-green-600 hover:text-green-800"
                                            title="수정"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                        </button>
                                        {/* 삭제 버튼 */}
                                        <button 
                                            onClick={(e) => handleDeleteClick(e, bookmark)}
                                            className="text-red-600 hover:text-red-800"
                                            title="삭제"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* 페이지네이션 */}
                    <div className="mt-4">
                        {totalPages > 1 && (
                            <div className="flex justify-center">
                                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px text-[10px]">
                                    {/* 이전 페이지 버튼 */}
                                    <button
                                        onClick={() => handlePageChange(currentPage - 1)}
                                        disabled={currentPage === 1}
                                        className={`relative inline-flex items-center px-2 py-2 rounded-l-md border text-[10px] font-medium ${
                                            currentPage === 1
                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                : 'bg-white text-gray-500 hover:bg-gray-50'
                                        }`}
                                    >
                                        이전
                                    </button>

                                    {/* 페이지 번호 */}
                                    {[...Array(totalPages)].map((_, i) => (
                                        <button
                                            key={i + 1}
                                            onClick={() => handlePageChange(i + 1)}
                                            className={`relative inline-flex items-center px-4 py-2 border text-[10px] font-medium ${
                                                currentPage === i + 1
                                                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                                            }`}
                                        >
                                            {i + 1}
                                        </button>
                                    ))}

                                    {/* 다음 페이지 버튼 */}
                                    <button
                                        onClick={() => handlePageChange(currentPage + 1)}
                                        disabled={currentPage === totalPages}
                                        className={`relative inline-flex items-center px-2 py-2 rounded-r-md border text-[10px] font-medium ${
                                            currentPage === totalPages
                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                : 'bg-white text-gray-500 hover:bg-gray-50'
                                        }`}
                                    >
                                        다음
                                    </button>
                                </nav>
                            </div>
                        )}
                    </div>
                </>
            )}

            {showAddModal && (
                <AddBookmark
                    onClose={() => setShowAddModal(false)}
                    onAdd={handleAdd}
                />
            )}
            {showEdit && selectedBookmark && (
                <EditBookmark
                    bookmark={selectedBookmark}
                    onClose={() => {
                        setShowEdit(false);
                        setSelectedBookmark(null);
                    }}
                    onUpdate={handleUpdate}
                />
            )}
            {showDelete && selectedBookmark && (
                <DeleteBookmark
                    bookmark={selectedBookmark}
                    onClose={() => {
                        setShowDelete(false);
                        setSelectedBookmark(null);
                    }}
                    onDelete={handleDelete}
                />
            )}
        </div>
    );
};

export default BookmarkList;
```

#### 2. `src/components/BookmarkDetail.js`

```javascript
import React, { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import { formatDate } from '../utils/dateUtils';
import api from '../utils/api';
import LoadingSpinner from './LoadingSpinner';

const BookmarkDetail = ({ bookmark, onClose, currentPage, totalPages, onPageChange }) => {
    // showContent의 초기값 설정을 안전하게 처리
    const [showContent, setShowContent] = useState(() => {
        if (!bookmark) return true;
        return !bookmark.summary || bookmark.summary === '요약 생성 중...';
    });
    
    const [currentBookmark, setCurrentBookmark] = useState(bookmark);
    const [isLoading, setIsLoading] = useState(false);
    const [isInitialLoading, setIsInitialLoading] = useState(true);

    // 요약 상태 확인 및 업데이트
    useEffect(() => {
        let intervalId;
        
        const checkSummary = async () => {
            if (!currentBookmark?.summary || currentBookmark.summary === '요약 생성 중...') {
                setIsLoading(true);
                try {
                    const response = await api.bookmarks.getBookmark(currentBookmark.id);
                    if (!response) {
                        console.error('북마크 정보를 가져올 수 없음');
                        return;
                    }
                    
                    setCurrentBookmark(response);
                    
                    // 요약이 완료되면 인터벌 중지 및 로딩 상태 해제
                    if (response.summary && response.summary !== '요약 생성 중...') {
                        clearInterval(intervalId);
                        setIsLoading(false);
                        setShowContent(false);  // 요약 보기로 전환
                    }
                } catch (error) {
                    console.error('요약 상태 확인 실패:', error);
                    // 에러 발생 시에도 인터벌은 유지하고 로딩 상태만 해제
                    setIsLoading(false);
                }
            }
        };

        // 북마크 ID가 있을 때만 인터벌 시작
        if (currentBookmark?.id) {
            checkSummary();  // 최초 1회 실행
            intervalId = setInterval(checkSummary, 2000);
        }
        
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [currentBookmark?.id, currentBookmark?.summary]);

    // 조회수 증가 기능 유지
    const increaseReadCount = useCallback(async () => {
        if (!currentBookmark?.id) return false;
        
        try {
            await api.bookmarks.increaseReadCount(currentBookmark.id);
            return true;
        } catch (error) {
            console.error('조회수 증가 실패:', error);
            return false;
        }
    }, [currentBookmark?.id]);

    // 컴포넌트 마운트 시 조회수 증가
    useEffect(() => {
        if (currentBookmark?.id) {
            increaseReadCount();
        }
    }, [currentBookmark?.id, increaseReadCount]);

    // 리스트로 돌아가기 핸들러
    const handleClose = () => {
        onClose();
    };

    // 수정 버튼 클릭 핸들러
    const handleEditClick = (e) => {
        e.stopPropagation();
        onClose(true);  // true를 전달하여 수정 모달을 열도록 함
    };

    useEffect(() => {
        if (bookmark) {
            setIsInitialLoading(false);
        }
    }, [bookmark]);

    // Early return을 hooks 호출 이후로 이동
    if (!bookmark || !currentBookmark) {
        return null;
    }

    if (isInitialLoading) {
        return (
            <div className="bg-white rounded-lg shadow-xl w-full p-6">
                <LoadingSpinner message="북마크 정보를 불러오는 중..." />
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-xl w-full flex flex-col">
            {/* 상단 섹션: 뒤로가기 버튼과 페이지네이션을 같은 라인에 배치 */}
            <div className="flex-none px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-center mb-4">
                    {/* 왼쪽: 리스트로 돌아가기 버튼 */}
                    <button 
                        onClick={handleClose} 
                        className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        <span>리스트로 돌아가기</span>
                    </button>

                    {/* 오른쪽: 페이지네이션 */}
                    {totalPages > 1 && (
                        <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px text-[10px]">
                            {/* 이전 페이지 버튼 */}
                            <button
                                onClick={() => onPageChange(currentPage - 1)}
                                disabled={currentPage === 1}
                                className={`relative inline-flex items-center px-2 py-2 rounded-l-md border text-[10px] font-medium ${
                                    currentPage === 1
                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                        : 'bg-white text-gray-500 hover:bg-gray-50'
                                }`}
                            >
                                이전
                            </button>

                            {/* 페이지 번호 */}
                            {[...Array(totalPages)].map((_, i) => (
                                <button
                                    key={i + 1}
                                    onClick={() => onPageChange(i + 1)}
                                    className={`relative inline-flex items-center px-4 py-2 border text-[10px] font-medium ${
                                        currentPage === i + 1
                                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                                    }`}
                                >
                                    {i + 1}
                                </button>
                            ))}

                            {/* 다음 페이지 버튼 */}
                            <button
                                onClick={() => onPageChange(currentPage + 1)}
                                disabled={currentPage === totalPages}
                                className={`relative inline-flex items-center px-2 py-2 rounded-r-md border text-[10px] font-medium ${
                                    currentPage === totalPages
                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                        : 'bg-white text-gray-500 hover:bg-gray-50'
                                }`}
                            >
                                다음
                            </button>
                        </nav>
                    )}
                </div>

                {/* 제목 및 메타 정보 */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center">
                        <h2 className="text-xl font-semibold text-gray-800">{currentBookmark.title}</h2>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                        {/* 왼쪽: 메타 정보 */}
                        <div className="flex items-center space-x-4">
                            <span>{formatDate(currentBookmark.created_at)}</span>
                            <span>·</span>
                            <span>{currentBookmark.source_name || '-'}</span>
                        </div>
                        
                        {/* 오른쪽: 버튼들 */}
                        <div className="flex items-center space-x-2">
                            {/* 요약/컨텐츠 토글 버튼 */}
                            <div className="inline-flex rounded-lg shadow-sm">
                                <button 
                                    onClick={() => setShowContent(false)}
                                    className={`px-3 py-1 text-xs font-medium rounded-l-lg border
                                        ${!showContent 
                                            ? 'bg-blue-50 text-blue-600 border-blue-600' 
                                            : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                                    disabled={isLoading}
                                >
                                    요약 {isLoading ? '(로딩중...)' : !currentBookmark.summary && '(클릭하여 확인)'}
                                </button>
                                <button 
                                    onClick={() => setShowContent(true)}
                                    className={`px-3 py-1 text-xs font-medium rounded-r-lg border-t border-r border-b
                                        ${showContent 
                                            ? 'bg-blue-50 text-blue-600 border-blue-600' 
                                            : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                                >
                                    컨텐츠
                                </button>
                            </div>

                            {/* 구분선 */}
                            <div className="h-4 w-px bg-gray-300 mx-2"></div>

                            {/* 수정 버튼 */}
                            <button 
                                onClick={handleEditClick}
                                className="text-green-600 hover:text-green-800"
                                title="수정"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    {bookmark.tags && bookmark.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                            {bookmark.tags.map((tag, index) => (
                                <span key={index} className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-sm">
                                    {tag}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* 중앙 컨텐츠 영역 */}
            <div className="flex-1 overflow-y-auto min-h-0 p-6">
                <div className="prose max-w-none">
                    <ReactMarkdown 
                        rehypePlugins={[rehypeRaw]} 
                        remarkPlugins={[remarkGfm]}
                        className="markdown-body"
                    >
                        {showContent 
                            ? (currentBookmark.content || '컨텐츠가 없습니다.') 
                            : (currentBookmark.summary || '요약이 생성중입니다...')}
                    </ReactMarkdown>
                </div>
            </div>

            {/* 하단 섹션 */}
            <div className="flex-none px-6 py-4 border-t border-gray-200">
                <div className="space-y-2">
                    {/* 첫 번째 줄: 출처, URL */}
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                            <span className="font-medium mr-2">출처:</span>
                            <span>{currentBookmark.source_name || '-'}</span>
                        </div>
                        <span className="text-gray-300">|</span>
                        <div className="flex items-center overflow-hidden">
                            <span className="font-medium mr-2">URL:</span>
                            <a 
                                href={currentBookmark.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="truncate text-blue-600 hover:text-blue-800 hover:underline"
                            >
                                {currentBookmark.url}
                            </a>
                        </div>
                    </div>

                    {/* 두 번째 줄: 생성일, 수정일, 조회수 */}
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                            <span className="font-medium mr-2">생성일:</span>
                            <span>{formatDate(currentBookmark.created_at)}</span>
                        </div>
                        <span className="text-gray-300">|</span>
                        <div className="flex items-center">
                            <span className="font-medium mr-2">수정일:</span>
                            <span>{currentBookmark.updated_at ? formatDate(currentBookmark.updated_at) : '-'}</span>
                        </div>
                        <span className="text-gray-300">|</span>
                        <div className="flex items-center">
                            <span className="font-medium mr-2">조회수:</span>
                            <span>{currentBookmark.read_count || 0}회</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BookmarkDetail;
```

**주요 변경 사항:**

1. **BookmarkList.js**:
   - `showDetail`이 `true`일 때 조건부 렌더링으로 상세보기만 표시
   - `BookmarkDetail`에 `currentPage`, `totalPages`, `onPageChange` props 전달
   - 모달 렌더링 제거 (상세보기는 메인 페이지에 표시)

2. **BookmarkDetail.js**:
   - 모달 스타일 제거 (`fixed inset-0` 등)
   - 일반 컴포넌트로 변경
   - 상단 헤더에 "리스트로 돌아가기" 버튼과 페이지네이션을 같은 라인에 배치
   - 조회수 증가 로직을 컴포넌트 마운트 시 실행하도록 변경
   - `currentPage`, `totalPages`, `onPageChange` props 추가

---

### 2026-02-13: UI/UX 개선 및 버그 수정

**수정 내용:**
- 모바일 반응형 최적화
- PC 환경 본문 가로 사이즈 최적화
- 본문 글자 크기 조정
- 로그인 페이지 입력창 위치 조정
- 본문 링크 새 탭에서 열기
- 북마크 목록 상단에 페이지네이션 추가
- 본문 하단에 되돌아가기 버튼 추가
- 되돌아가기 버튼 스타일 개선
- 조회수 중복 증가 문제 해결

**수정된 파일:**

#### 1. `src/components/BookmarkList.js`

**주요 변경사항:**
- 모바일 반응형 최적화: 헤더, 카드 레이아웃, 메타 정보, 페이지네이션
- PC 환경 최적화: 컨테이너 너비 확대 (`max-w-7xl` → `w-full`)
- 상단 헤더에 페이지네이션 추가 (새 북마크 버튼과 같은 라인)
- 페이지네이션 모바일/PC 반응형 크기 조정

**코드 변경:**
```javascript
// 상단 헤더 레이아웃 수정
<div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 sm:mb-6 gap-3 sm:gap-0">
    <h1 className="text-lg sm:text-xl font-bold">북마크 목록</h1>
    <div className="flex flex-col sm:flex-row items-end sm:items-center gap-2 sm:gap-3 w-full sm:w-auto">
        {/* 상단 페이지네이션 */}
        {totalPages > 1 && (
            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px text-[8px] sm:text-[10px] order-2 sm:order-1">
                {/* 페이지네이션 버튼들 */}
            </nav>
        )}
        {/* 새 북마크 버튼 */}
        <button onClick={() => setShowAddModal(true)} className="...">
            새 북마크
        </button>
    </div>
</div>

// 컨테이너 너비 최적화
<div className="w-full px-2 sm:px-4 lg:px-8 py-4 sm:py-8">
    <div className="max-w-7xl mx-auto">
        {/* 내용 */}
    </div>
</div>
```

#### 2. `src/components/BookmarkDetail.js`

**주요 변경사항:**
- 모바일 반응형 최적화: 헤더, 페이지네이션, 제목/메타, 버튼, 컨텐츠 영역
- PC 환경 본문 가로 사이즈 최적화: `max-width: none` 설정, 패딩 조정
- 본문 글자 크기 조정: 2단계 작게 (`text-xs sm:text-sm lg:text-base xl:text-lg`)
- 본문 링크 새 탭에서 열기: ReactMarkdown `components` prop 사용
- 상단/하단 되돌아가기 버튼 추가 및 스타일 개선 (그라데이션 박스)
- 조회수 중복 증가 문제 해결: `useRef`로 중복 실행 방지

**코드 변경:**
```javascript
// 조회수 중복 증가 방지
const readCountIncreasedRef = useRef(null);
const isIncreasingRef = useRef(false);

useEffect(() => {
    if (bookmark?.id && readCountIncreasedRef.current !== bookmark.id && !isIncreasingRef.current) {
        isIncreasingRef.current = true;
        const increaseReadCount = async () => {
            try {
                await api.bookmarks.increaseReadCount(bookmark.id);
                readCountIncreasedRef.current = bookmark.id;
            } catch (error) {
                console.error('조회수 증가 실패:', error);
                isIncreasingRef.current = false;
            } finally {
                if (readCountIncreasedRef.current === bookmark.id) {
                    isIncreasingRef.current = false;
                }
            }
        };
        increaseReadCount();
    }
}, [bookmark?.id]);

// 본문 링크 새 탭에서 열기
<ReactMarkdown 
    components={{
        a: ({ node, ...props }) => (
            <a {...props} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 hover:underline">
                {props.children}
            </a>
        ),
    }}
>
    {showContent ? currentBookmark.content : currentBookmark.summary}
</ReactMarkdown>

// 되돌아가기 버튼 스타일 (상단/하단)
<button 
    onClick={handleClose} 
    className="flex items-center justify-center w-6 h-6 sm:w-7 sm:h-7 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
    title="리스트로 돌아가기"
    aria-label="리스트로 돌아가기"
>
    <svg className="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" strokeWidth="2.5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
    </svg>
</button>

// 본문 가로 사이즈 최적화
<div className="w-full prose prose-sm sm:prose-sm lg:prose xl:prose-lg" style={{ maxWidth: 'none' }}>
    {/* 컨텐츠 */}
</div>

// 코드 블록 커스텀 컴포넌트 - 다크 테마 적용
<ReactMarkdown
    components={{
        pre: ({ node, children, ...props }) => (
            <pre 
                {...props} 
                className="bg-gray-900 text-gray-100 p-4 rounded-lg mb-4 overflow-x-auto border border-gray-700 font-mono"
                style={{
                    WebkitOverflowScrolling: 'touch',
                    whiteSpace: 'pre'
                }}
            >
                {children}
            </pre>
        ),
        code: ({ node, inline, className, children, ...props }) => {
            const isBlockCode = !inline;
            if (isBlockCode) {
                return (
                    <code 
                        {...props} 
                        className="bg-transparent text-gray-100 p-0 font-mono"
                        style={{ whiteSpace: 'pre' }}
                    >
                        {children}
                    </code>
                );
            }
            return (
                <code 
                    {...props} 
                    className="bg-gray-100 text-gray-900 px-1 rounded font-mono"
                >
                    {children}
                </code>
            );
        },
    }}
>
    {content}
</ReactMarkdown>
```

#### 3. `src/components/Login.js`

**주요 변경사항:**
- 로그인 페이지 입력창 위치 조정: 상단으로 이동 (`justify-center` → `justify-start`)
- 상단 패딩 추가: `pt-12 sm:pt-16 lg:pt-20`

**코드 변경:**
```javascript
// 레이아웃 조정
<div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col justify-start pt-12 sm:pt-16 lg:pt-20 py-4 sm:px-6 lg:px-8">
    {/* 로그인 폼 */}
</div>
```

**주요 변경 사항:**

1. **모바일 반응형 최적화**:
   - 모든 컴포넌트에 모바일/태블릿/PC 반응형 클래스 적용
   - 텍스트 크기, 패딩, 간격 등 화면 크기별 조정
   - 페이지네이션 모바일에서 가로 스크롤 지원

2. **PC 환경 최적화**:
   - 본문 가로 사이즈 최적화 (`max-width: none`)
   - 컨테이너 너비 확대
   - 패딩 및 텍스트 크기 조정

3. **UX 개선**:
   - 북마크 목록 상단에 페이지네이션 추가
   - 본문 하단에 되돌아가기 버튼 추가
   - 되돌아가기 버튼 그라데이션 박스 스타일 적용
   - 본문 링크 새 탭에서 열기

4. **버그 수정**:
   - 조회수 중복 증가 문제 해결 (비동기 경쟁 조건 방지)
   - 로그인 페이지 입력창 위치 조정

---

## 최근 업데이트

### 2026-02-14: 코드 블록 스타일 개선 및 환경 변수 관리 개선

#### 코드 블록 스타일 개선
- **다크 테마 적용**: 코드 블록 배경을 `bg-gray-900`, 텍스트를 `text-gray-100`으로 변경하여 가독성 향상
- **모바일 최적화**: 터치 스크롤 지원 (`-webkit-overflow-scrolling: touch`)
- **인라인 코드**: 밝은 배경(`bg-gray-100`) 유지로 본문과 구분
- **스타일 위치**: `src/index.css`와 `src/components/BookmarkDetail.js`에 적용

#### 환경 변수 관리 개선
- **완전한 .env 파일 기반 설정**: 모든 설정값을 `.env` 파일에서 관리
- **하드코딩 제거**: `src/utils/api.js`와 `src/utils/axios.js`에서 하드코딩된 기본값 제거
- **일관성 유지**: Backend와 동일한 방식으로 환경 변수 관리

---

### 2026-02-14: 키워드 검색 기능 개선 및 Axios 파라미터 직렬화 수정

**수정 내용:**
- Axios의 기본 배열 파라미터 직렬화 방식을 커스텀 `paramsSerializer`로 변경
- FastAPI가 기대하는 배열 파라미터 형식(`tags=AI&tags=코딩`)으로 변환
- 키워드 구분자 지원 (백엔드에서 처리)

**수정된 파일:**

#### 1. `frontend/src/utils/api.js`

**주요 변경사항:**
- 커스텀 `paramsSerializer` 함수 구현
- FastAPI 배열 쿼리 파라미터 형식에 맞게 변환 (`tags=AI&tags=코딩` 형식)

**코드 변경:**
```javascript
// FastAPI 배열 쿼리 파라미터 형식에 맞게 변환하는 함수
// tags=AI&tags=코딩 형식으로 변환 (기본값: tags[]=AI&tags[]=코딩)
const paramsSerializer = (params) => {
    const searchParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
        const value = params[key];
        if (value === null || value === undefined) {
            return; // null/undefined 값은 제외
        }
        
        if (Array.isArray(value)) {
            // 배열인 경우 각 요소를 반복하여 추가 (tags=AI&tags=코딩 형식)
            value.forEach(item => {
                if (item !== null && item !== undefined) {
                    searchParams.append(key, item);
                }
            });
        } else {
            // 일반 값인 경우 그대로 추가
            searchParams.append(key, value);
        }
    });
    
    return searchParams.toString();
};

const axiosInstance = axios.create({
    baseURL: getApiBaseURL(),
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true,
    paramsSerializer: paramsSerializer  // 커스텀 직렬화 함수 적용
});
```

**문제 해결:**
- 이전에는 Axios의 기본 배열 직렬화 방식(`tags[]=AI&tags[]=코딩`)이 FastAPI와 호환되지 않아 `tags` 파라미터가 `None`으로 전달됨
- 커스텀 `paramsSerializer`로 `tags=AI&tags=코딩` 형식으로 변환하여 해결

### 2026-02-14: 북마크 목록 총 개수 표시 기능 추가

**수정 내용:**
- 북마크 목록 제목에 필터링된 결과의 총 개수 표시
- 필터 적용 여부와 관계없이 항상 총 개수 표시

**수정된 파일:**

#### 1. `frontend/src/components/BookmarkList.js`

**주요 변경사항:**
- 제목에 총 개수 표시 추가 (`totalItems` 상태 활용)
- 형식: "북마크 목록(100개)"

**코드 변경:**
```javascript
<h1 className="text-lg sm:text-xl font-bold">
    북마크 목록{totalItems > 0 && `(${totalItems}개)`}
</h1>
```

**표시 예시:**
- 필터 없을 때: "북마크 목록(100개)"
- 필터 있을 때: "북마크 목록(23개) 필터 : 키워드A, 키워드B, 전체제거"

**사용자 경험 개선:**
- 필터링된 결과의 총 개수를 한눈에 확인 가능
- 검색 결과의 규모를 즉시 파악 가능

### 2026-02-13: 키워드 검색 기능 추가

**수정 내용:**
- 북마크 목록에서 키워드 클릭 시 해당 키워드로 필터링된 목록 표시
- 다중 키워드 선택/제거 지원 (AND 조건 검색)
- 필터 표시 및 제거 기능 추가
- 기존 기능 및 UI 유지

**수정된 파일:**

#### 1. `frontend/src/utils/api.js`

**주요 변경사항:**
- `getList` 함수에 `tags` 배열 파라미터 지원 추가 (AND 조건 검색)

**코드 변경:**
```javascript
getList: async ({ page, per_page, tags }) => {
    const params = { page, per_page };
    // 여러 태그를 배열로 전달 (FastAPI Query 파라미터 배열 형식)
    if (tags && tags.length > 0) {
        params.tags = tags;
    }
    const response = await axiosInstance.get('/bookmarks/', {
        params
    });
    return response.data;
},
```

#### 4. `frontend/src/components/BookmarkList.js`

**주요 변경사항:**
- 키워드 검색 상태를 단일 값에서 배열로 변경 (`selectedTag` → `selectedTags`)
- 다중 키워드 선택/제거 지원
- 키워드 클릭 시 토글 방식으로 추가/제거
- 각 필터 키워드에 개별 제거 버튼 추가
- 선택된 키워드 시각적 표시 (파란색 배경)
- "전체 제거" 버튼 추가

**코드 변경:**
```javascript
// 키워드 검색 상태 관리 (다중 선택 지원)
const [selectedTags, setSelectedTags] = useState([]);

// 키워드 클릭 핸들러 (다중 선택/제거 지원)
const handleTagClick = (e, tag) => {
    e?.stopPropagation();
    setSelectedTags(prev => {
        // 이미 선택된 키워드면 제거, 없으면 추가
        if (prev.includes(tag)) {
            return prev.filter(t => t !== tag);
        } else {
            return [...prev, tag];
        }
    });
    setCurrentPage(1); // 검색 시 첫 페이지로 이동
};

// 개별 키워드 제거 핸들러
const handleRemoveTag = (e, tagToRemove) => {
    e?.stopPropagation();
    setSelectedTags(prev => prev.filter(t => t !== tagToRemove));
    setCurrentPage(1);
};

// 검색 필터 전체 초기화 핸들러
const handleClearFilter = () => {
    setSelectedTags([]);
    setCurrentPage(1);
};

// fetchBookmarks에 태그 배열 파라미터 추가
const fetchBookmarks = useCallback(async () => {
    // 여러 키워드를 배열로 전달 (AND 조건으로 검색됨)
    const tagsParam = selectedTags.length > 0 ? selectedTags : undefined;
    const response = await api.bookmarks.getList({
        page: currentPage,
        per_page: ITEMS_PER_PAGE,
        tags: tagsParam
    });
    // ...
}, [currentPage, ITEMS_PER_PAGE, selectedTags]);

// 키워드 태그 클릭 가능하게 변경 (선택 상태 표시)
{bookmark.tags.map((tag, idx) => {
    const isSelected = selectedTags.includes(tag);
    return (
        <span 
            key={idx} 
            onClick={(e) => handleTagClick(e, tag)}
            className={`text-xs px-1.5 sm:px-2 py-0.5 rounded cursor-pointer transition-colors ${
                isSelected 
                    ? 'bg-blue-500 text-white hover:bg-blue-600' 
                    : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
            }`}
            title={isSelected ? `${tag} 필터 제거` : `${tag} 필터 추가`}
        >
            {tag}
        </span>
    );
})}

// 헤더에 다중 필터 표시
{selectedTags.length > 0 && (
    <div className="flex items-center gap-2 flex-wrap">
        <span className="text-sm text-gray-600">필터:</span>
        {selectedTags.map((tag, idx) => (
            <span 
                key={idx}
                className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded flex items-center gap-1"
            >
                {tag}
                <button
                    onClick={(e) => handleRemoveTag(e, tag)}
                    className="text-blue-600 hover:text-blue-800 text-sm ml-1"
                    title={`${tag} 필터 제거`}
                >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </span>
        ))}
        <button
            onClick={handleClearFilter}
            className="text-sm text-gray-500 hover:text-gray-700 px-2 py-1 rounded border border-gray-300 hover:bg-gray-50"
            title="모든 필터 제거"
        >
            전체 제거
        </button>
    </div>
)}
```

**주요 변경 사항:**

1. **Backend API**:
   - 키워드 검색 엔드포인트 개선 (`tag` → `tags` 배열 파라미터)
   - 다중 키워드를 AND 조건으로 검색
   - 각 키워드 내부의 구분자(공백, ',', '-', '·')로 구분된 키워드는 OR 조건으로 검색
   - PostgreSQL ARRAY 타입에서 부분 일치 검색 지원 (LIKE 검색)
   - SQL 로깅 기능 추가 (생성된 SQL과 파라미터 로깅)

2. **Frontend UI**:
   - 다중 키워드 선택 지원 (배열 상태 관리)
   - 키워드 클릭 시 토글 방식으로 추가/제거
   - 선택된 키워드 시각적 표시 (파란색 배경)
   - 각 필터 키워드에 개별 제거 버튼
   - "전체 제거" 버튼으로 모든 필터 한 번에 제거
   - 필터링된 결과에도 페이지네이션 적용
   - 북마크 목록 제목에 총 개수 표시 (예: "북마크 목록(100개)")

3. **Axios 파라미터 직렬화**:
   - 커스텀 `paramsSerializer` 함수 구현
   - FastAPI가 기대하는 배열 파라미터 형식으로 변환 (`tags=AI&tags=코딩`)
   - Axios 기본 직렬화 방식과의 호환성 문제 해결

4. **사용자 경험**:
   - 키워드에 hover 효과 추가
   - 선택된 키워드와 미선택 키워드 구분
   - 개별 필터 제거 및 전체 제거 기능
   - 필터 상태 시각적 표시
   - 키워드 구분자 지원으로 더 유연한 검색 가능
   - 필터링된 결과의 총 개수를 한눈에 확인 가능

---

**문서 버전**: 1.1  
**최종 업데이트**: 2026-02-14  
**작성자**: LinkDigest 개발팀
