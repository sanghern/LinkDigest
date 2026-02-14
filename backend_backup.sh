#!/bin/bash

# 백업 디렉토리 생성
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# PostgreSQL 데이터베이스 백업
docker-compose exec -T db pg_dump -U user bookmarks > $BACKUP_DIR/database.sql

# 환경 변수 백업
cp .env $BACKUP_DIR/

# 7일 이상 된 백업 삭제
find /backup -type d -mtime +7 -exec rm -rf {} \;

# 컨테이너 상태 확인
docker ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f backend

# 시스템 리소스 사용량 확인
docker stats

# UFW 방화벽 설정
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# SSL 인증서 설치 (Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.your-domain.com 