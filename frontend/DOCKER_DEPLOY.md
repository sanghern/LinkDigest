# LinkDigest Frontend - Docker 배포 (독립 실행)

프론트엔드를 백엔드와 별도로 Docker로 실행하는 방법입니다.

---

## 1. 요구 사항

- **Docker Desktop** 설치 및 실행 중
- 터미널에서 `docker`, `docker compose` 사용 가능

---

## 2. 구성

```
frontend/
├── Dockerfile              # 멀티 스테이지: Node 빌드 → Nginx 서빙
├── docker-compose.yml      # frontend 서비스만 정의
├── docker/
│   └── nginx.conf          # SPA 정적 서빙 (try_files → index.html)
├── .dockerignore
└── DOCKER_DEPLOY.md        # 본 매뉴얼
```

- 빌드 시 **REACT_APP_API_URL=/api** 로 주입됩니다. 배포 시 Nginx 등에서 `/api`를 백엔드로 프록시하면 됩니다.

---

## 3. 실행

```bash
cd frontend
docker compose up -d
```

- 첫 실행 시 이미지 빌드로 2~5분 정도 걸릴 수 있습니다.
- **접속**: http://localhost:3000

---

## 4. 로그 / 상태 / 중지

```bash
# 로그
docker compose logs -f

# 상태
docker compose ps

# 중지 및 컨테이너 제거
docker compose down
```

---

## 5. 소스 수정 후 반영

이미지는 빌드 시점의 코드가 포함되므로, 수정 후에는 다시 빌드해야 합니다.

```bash
cd frontend
docker compose up -d --build
```

---

## 6. 백엔드와 함께 사용

- **백엔드**: `cd backend && docker compose up -d` → http://localhost:8000
- **프론트엔드**: `cd frontend && docker compose up -d` → http://localhost:3000

동일 호스트에서 Nginx로 묶어 쓰는 경우, `/` → 3000, `/api` → 8000 으로 프록시하면 됩니다.
