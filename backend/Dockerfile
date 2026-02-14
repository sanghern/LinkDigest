# LinkDigest Backend - Docker 이미지 (맥/리눅스)
# Python 3.12 기반
FROM python:3.12-slim

# 작업 디렉터리
WORKDIR /app

# 시스템 의존성 (psycopg2 등)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사 (실제 앱은 app/main.py)
COPY app ./app
COPY scripts ./scripts

# 로그 디렉터리 (db_init 등에서 사용)
RUN mkdir -p /app/logs

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')" || exit 1

# uvicorn 실행 (0.0.0.0으로 수신해 컨테이너 외부/nginx에서 접근 가능)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
