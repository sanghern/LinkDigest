# Docker Compose 실행 시 요약 미동작 원인 분석

## 현상
- **로컬 실행** (`backend/start.py` + `frontend/npm start`): 요약 정상 생성
- **Docker Compose 실행** (`docker compose up`): 요약이 생성되지 않음

---

## 원인: Ollama 접속 주소 차이

### 로컬 실행 (start.py)
- 백엔드 프로세스가 **호스트(맥)에서** 실행됨.
- `OLLAMA_API_URL` 기본값: `http://localhost:11434/api/chat`
- 이때 **localhost = 호스트 자신**이므로, 호스트에서 떠 있는 Ollama에 접속 가능 → 요약 정상 동작.

### Docker Compose 실행
- 백엔드 프로세스가 **컨테이너 안**에서 실행됨.
- `.env`에 `OLLAMA_API_URL`을 두지 않으면 기본값 `http://localhost:11434/api/chat` 사용.
- 컨테이너 안에서 **localhost = 컨테이너 자신**을 가리킴.
- Ollama는 **호스트**에서 실행 중이므로, 컨테이너의 localhost:11434에는 아무 서비스도 없음 → **연결 실패** → `summarize_article()`이 빈 문자열 반환 → 요약이 DB에 저장되지 않음.

정리하면, **Docker 환경에서는 “localhost”가 호스트가 아니라 컨테이너를 가리키기 때문에** Ollama에 연결되지 않는 것이 원인입니다.

---

## 해결 방법

### 1) Docker 전용으로 Ollama URL 지정 (권장)
Ollama를 **호스트(맥)**에서 실행 중이라면, Docker에서 호스트로 나가려면 다음 주소를 씁니다.

- **맥 / Windows Docker Desktop**: `http://host.docker.internal:11434/api/chat`
- **리눅스**: `host.docker.internal`이 없을 수 있으므로, 호스트 IP를 쓰거나 `extra_hosts`로 호스트명 지정 후 `http://그호스트명:11434/api/chat` 사용.

**방법 A – docker-compose 기본값 사용**  
- `backend/docker-compose.yml`의 backend 서비스에  
  `OLLAMA_API_URL: http://host.docker.internal:11434/api/chat`  
  를 두면, **.env에 값을 안 넣었을 때** Docker만 쓸 경우 요약이 동작합니다.
- **같은 .env를 로컬(start.py)과 Docker에서 같이 쓸 때**:  
  - 로컬에서는 `localhost`를 쓰고, Docker에서는 `host.docker.internal`을 쓰려면  
  - **Docker 실행 시에만** 이 값이 적용되도록 compose에 위 기본값을 두고,  
  - 로컬용 `.env`에는 `OLLAMA_API_URL`을 넣지 않거나, 로컬 전용 `.env.local` 등에서만 `localhost`를 두면 됩니다.

**방법 B – .env에서 직접 지정**  
- `.env`에 다음 한 줄 추가:
  ```bash
  OLLAMA_API_URL=http://host.docker.internal:11434/api/chat
  ```
- 이렇게 하면 **로컬 start.py**에서도 같은 URL을 쓰게 됩니다.  
  - 맥/Windows Docker Desktop에서는 `host.docker.internal`이 호스트를 가리키므로, 로컬에서도 Ollama가 호스트에 있으면 동작할 수 있습니다.  
  - 로컬에서만 `localhost`를 쓰고 싶다면, Docker용과 로컬용으로 `.env`를 나누거나, compose에서만 override하는 방식(방법 A)을 쓰는 것이 좋습니다.

### 2) 요약 실패 시 로그 확인
- 백엔드 로그에 `Ollama API 요청 실패` / `요약 생성 실패` 등이 나오면, 위 URL이 Docker에서 호스트의 Ollama를 제대로 가리키는지 다시 확인하면 됩니다.

---

## 요약
- **원인**: Docker 컨테이너 안에서 `localhost`는 호스트가 아니라 컨테이너 자신이라, 호스트에서 돌아가는 Ollama에 접속하지 못함.
- **해결**: Docker 실행 시 `OLLAMA_API_URL`을 `http://host.docker.internal:11434/api/chat`(맥/Windows) 또는 호스트 주소로 설정.
