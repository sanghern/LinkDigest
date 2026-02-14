# LinkDigest

웹 URL을 입력받아 콘텐츠를 스크래핑하고, AI로 요약·키워드 추출을 수행하는 북마크 관리 서비스입니다.

## 구성

| 디렉터리 | 설명 |
|----------|------|
| **backend/** | FastAPI 백엔드, PostgreSQL, Docker 배포 |
| **frontend/** | React 프론트엔드, Docker 배포 (독립) |

- 백엔드: [backend/DOCKER_DEPLOY.md](backend/DOCKER_DEPLOY.md)
- 프론트엔드: [frontend/DOCKER_DEPLOY.md](frontend/DOCKER_DEPLOY.md)
- 설계/요구사항: [linkdigest서비스.md](linkdigest서비스.md), [linkdigest_PRD.md](linkdigest_PRD.md)

## 로컬 실행 (Docker)

```bash
# 백엔드
cd backend && docker compose up -d

# 프론트엔드
cd frontend && docker compose up -d
```

- 프론트: http://localhost:3000  
- 백엔드 API: http://localhost:8000  

2026.02.14 by shsong
