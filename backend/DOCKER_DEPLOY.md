# LinkDigest Backend - Docker Compose 배포 매뉴얼 (맥 환경)

Docker Compose를 사용한 백엔드 실행/중지 방법과 Nginx 연결 방법을 안내합니다.

---

## 1. 요구 사항

- **맥 환경**: macOS (Apple Silicon / Intel)
- **Docker Desktop for Mac** 설치 및 실행 중
- 터미널에서 `docker`, `docker compose` 사용 가능

```bash
docker --version
docker compose version
```

---

## 2. 배포 패키지 구성

```
backend/
├── Dockerfile              # 백엔드 이미지 빌드
├── docker-compose.yml      # 서비스 정의 (backend, postgres, nginx)
├── docker/
│   └── nginx.conf          # Nginx 프록시 설정
├── .env.docker.example     # 환경 변수 예시
└── DOCKER_DEPLOY.md        # 본 매뉴얼
```

---

## 3. 환경 변수 설정

Compose 전용으로 처음 세팅하는 경우:

```bash
cd backend
cp .env.docker.example .env
# .env 파일을 열어 DB_PASSWORD, SECRET_KEY, ADMIN_PASSWORD 등 수정
```

기존 `.env`를 쓰는 경우:

- **외부 PostgreSQL 사용 (권장)**: `.env`에 `DB_HOST=192.168.7.89` 등 실제 DB 서버를 두면, Docker 백엔드는 해당 DB로 연결합니다. `docker compose up -d` 시 **backend만** 기동됩니다 (별도 Nginx 사용 시 Compose 내부 nginx는 profile로 제외됨).
- **Compose 내부 PostgreSQL 사용**: `.env`에 `DB_HOST=postgres`, `DB_PORT=5432` 로 두고, `docker compose --profile internal-db up -d` 로 기동하면 postgres 컨테이너도 함께 올라갑니다.

---

## 4. Docker Compose Up (실행)

### 4.1 백그라운드로 전체 실행

```bash
cd backend
docker compose up -d
```

- **외부 DB 사용 시**(`.env`에 `DB_HOST=192.168.7.89` 등): **backend만** 기동됩니다 (별도 Nginx 사용 시 Compose nginx는 기동하지 않음).
- **내부 DB 사용 시**: `docker compose --profile internal-db up -d` 로 postgres 포함 기동.
- **Compose 내부 Nginx까지 사용 시** (로컬 8080 프록시): `docker compose --profile with-nginx up -d`
- 첫 실행 시 빌드로 인해 1~3분 정도 걸릴 수 있습니다.

### 4.2 로그 확인

```bash
# 전체 로그 (실시간)
docker compose logs -f

# 서비스별 로그
docker compose logs -f backend
docker compose logs -f postgres
docker compose logs -f nginx
```

### 4.3 상태 확인

```bash
docker compose ps
```

모든 서비스가 `running`이고 backend가 `healthy`이면 정상입니다.

### 4.4 동작 확인

- **백엔드 직접**: http://localhost:8000/api/health  
- **Nginx 경유**: http://localhost:8080/api/health  
- **API 문서**: http://localhost:8080/api/docs (Nginx 경유)

### 4.5 외부 PostgreSQL 연결 검증

Docker 백엔드가 `.env`에 설정한 외부 DB(예: 192.168.7.89)에 정상 접속하는지 확인하려면:

```bash
cd backend
docker compose exec backend python scripts/verify_db.py
```

- 연결 성공 시: `[OK] DB 연결 성공`, `[OK] users 테이블 조회 성공, 사용자 수: N` 출력.
- 연결 실패 시: `[FAIL] DB 연결 실패`와 오류 메시지가 출력됩니다 (방화벽, DB_HOST/비밀번호, 네트워크 등 확인).
- **이미지를 다시 빌드한 뒤** 검증하려면: `docker compose build backend && docker compose up -d && docker compose exec backend python scripts/verify_db.py`

### 4.6 소스 코드 수정 후 반영

백엔드 소스를 수정한 뒤 **`docker compose down` 후 `up`만 하면 변경 내용이 적용되지 않습니다.** 이미지는 빌드 시점의 코드가 포함되므로, 수정 후에는 **이미지를 다시 빌드**해야 합니다.

```bash
cd backend
# 방법 1: 빌드 후 기동
docker compose build backend
docker compose up -d

# 방법 2: 한 번에 빌드 후 기동 (권장)
docker compose up -d --build
```

- `--build`: 이미지가 없거나 Dockerfile/소스가 바뀌었을 때 backend 이미지를 다시 빌드한 뒤 컨테이너를 띄웁니다.
- `.env` 변경만 한 경우에는 **재빌드 없이** `docker compose up -d`만 해도 됩니다 (실행 시 env_file로 주입됨).

---

## 5. Docker Compose Down (중지)

### 5.1 컨테이너만 중지

```bash
cd backend
docker compose stop
```

- 데이터(PostgreSQL 볼륨)는 유지됩니다.

### 5.2 컨테이너 + 네트워크 제거 (볼륨 유지)

```bash
docker compose down
```

- `postgres_data` 볼륨은 그대로 있어서 DB 데이터는 유지됩니다.

### 5.3 컨테이너 + 네트워크 + 볼륨까지 삭제

```bash
docker compose down -v
```

- **주의**: PostgreSQL 데이터가 모두 삭제됩니다. 필요 시 백업 후 실행하세요.

---

## 6. Nginx에서 연결하기

Compose로 띄운 백엔드는 아래 두 방식으로 Nginx에서 연결할 수 있습니다.

### 6.1 Compose 내부 Nginx 사용 (선택)

- **별도 Nginx**(digest.aiground.ai 등)를 쓰는 경우에는 Compose의 nginx 서비스를 띄우지 않아도 됩니다. 기본 `docker compose up -d`는 **backend만** 기동합니다.
- Compose에 포함된 nginx를 쓰려면: `docker compose --profile with-nginx up -d` 로 기동합니다. Nginx는 `backend:8000`으로 프록시하며, 호스트에서는 **8080** 포트로 접속합니다.

### 6.2 호스트(맥)에 설치된 Nginx에서 연결

호스트에서 Nginx를 쓰고, Docker 백엔드로 프록시하려면:

1. 백엔드 포트 노출: `docker-compose.yml`의 backend 서비스에 이미 `ports: "8000:8000"` 이 있으므로, 맥에서 `http://127.0.0.1:8000` 으로 접근 가능합니다.
2. 호스트 Nginx 설정 예시:

```nginx
# /usr/local/etc/nginx/nginx.conf 또는 sites-enabled 등
server {
    listen 80;
    server_name digest.aiground.ai;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- `proxy_pass http://127.0.0.1:8000` 만으로 Nginx에서 Docker 백엔드로 연결 가능합니다.

### 6.3 다른 Docker Compose/호스트에서 연결

- 같은 맥에서 다른 Compose 프로젝트: 해당 프로젝트와 `linkdigest-net`을 연결하거나, 호스트 IP로 `http://host.docker.internal:8000` 사용.
- 다른 서버의 Nginx: 백엔드가 떠 있는 맥의 IP와 포트 8000(또는 8080)으로 `proxy_pass` 설정하면 됩니다.

---

## 7. 프론트엔드에서 Docker 백엔드 연결 검증

프론트엔드는 **독립 Docker**로도 실행할 수 있습니다. `cd frontend && docker compose up -d` → 포트 3000. 상세는 **[frontend/DOCKER_DEPLOY.md](../frontend/DOCKER_DEPLOY.md)** 참고.

프론트엔드(로컬 npm 실행)가 Docker 백엔드에 연결되는지 확인하려면:

1. **백엔드 실행**: `cd backend && docker compose up -d`
2. **검증 스크립트 실행** (프론트엔드 디렉터리):
   ```bash
   cd frontend
   npm run verify-backend
   ```
   - 백엔드 직접(8000): `npm run verify-backend`
   - Nginx 경유(8080): `npm run verify-backend:nginx`
3. **프론트엔드 기동 후 연결**: Docker 백엔드 전용 API URL로 기동한 뒤 로그인/API 호출 확인:
   ```bash
   npm run start:docker
   ```
   브라우저에서 http://localhost:3000 접속 후 로그인 및 북마크 목록 등 동작을 확인하면 됩니다.

---

## 8. 관리자 계정 초기화 (선택)

Compose 내부 PostgreSQL을 처음 쓸 때, 관리자 계정을 만들려면:

```bash
docker compose exec backend python -m app.db.db_init
```

- `.env`의 `ADMIN_USERNAME`, `ADMIN_PASSWORD` 등이 사용됩니다.
- 이미 테이블/관리자가 있으면 스킵하거나, 필요 시 스크립트 내용을 참고해 수동으로 처리할 수 있습니다.

---

## 9. 문제 해결

### 9.1 backend가 unhealthy 일 때

```bash
docker compose logs backend
```

- DB 연결 실패: `DB_HOST=postgres`, `DB_USER`/`DB_PASSWORD`/`DB_NAME`이 postgres 서비스와 일치하는지 확인.
- 포트 충돌: 맥에서 8000/5432/8080 사용 중인 프로세스 확인 후 중지하거나, `docker-compose.yml`의 `ports`를 변경 (예: "8001:8000").

### 9.2 Nginx 502 Bad Gateway

- backend가 기동 완료될 때까지 수 초 대기 후 다시 접속.
- `docker compose ps`로 backend가 `healthy`인지 확인.
- `docker compose logs backend`로 앱 에러 확인.

### 9.3 Ollama 연결 (AI 요약)

- Ollama를 **맥 호스트**에서 실행 중이어야 합니다.
- `.env`에 `OLLAMA_API_URL=http://host.docker.internal:11434/api/chat` 설정 (맥에서는 `host.docker.internal` 사용).
- 리눅스에서는 `host.docker.internal`이 없을 수 있으므로, 호스트 IP로 바꾸거나 `extra_hosts`로 호스트명을 지정해 사용하세요.

---

## 10. 요약 명령어

| 작업 | 명령어 |
|------|--------|
| 백그라운드 실행 | `docker compose up -d` |
| 로그 보기 | `docker compose logs -f` |
| 상태 확인 | `docker compose ps` |
| 중지 | `docker compose stop` |
| 중지 후 컨테이너 제거 | `docker compose down` |
| 볼륨까지 삭제 | `docker compose down -v` |
| 관리자 초기화 | `docker compose exec backend python -m app.db.db_init` |

---

이 매뉴얼대로 진행하면 맥 환경에서 Docker Compose로 백엔드를 띄우고, Nginx(Compose 내부 또는 호스트)에서 연결할 수 있습니다.
