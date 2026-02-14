# digest.aiground.ai 프록시 연결 가이드

192.168.7.88:3000 은 되는데 digest.aiground.ai 로는 연결이 안 될 때 점검할 내용입니다.

---

## 1. 수정한 내용 (프론트엔드 Docker Nginx)

- **server_name**: `localhost` → `_` + `listen 80 default_server`  
  → 프록시가 `Host: digest.aiground.ai` 로 넘겨도 수락.
- **Cache-Control**: `no-cache, no-store, must-revalidate` → `max-age=0, must-revalidate`  
  → 일부 프록시/캐시와의 충돌 가능성을 줄임.

**반영 방법**: 프론트 이미지 재빌드 후 재기동.

```bash
cd frontend
docker compose build --no-cache
docker compose up -d
```

---

## 2. 프록시 서버(호스트 Nginx) 점검

digest.aiground.ai 를 서빙하는 **호스트 Nginx**에서 아래를 확인하세요.

1. **proxy_pass 주소**
   - 프론트: `http://192.168.7.88:3000;` (끝에 `/` 없음)
   - API: `http://192.168.7.88:8000;`

2. **헤더**
   - `proxy_set_header Host $host;`
   - `proxy_set_header X-Forwarded-Proto $scheme;` (HTTPS 쓰면 필수)

3. **설정 예시**
   - `docs/nginx_proxy_digest.aiground.ai.example.conf` 참고.

4. **테스트**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   curl -I http://digest.aiground.ai
   ```

---

## 3. 네트워크/방화벽

- 프록시 서버에서 `192.168.7.88` 로 **3000, 8000** 포트 접속 가능한지 확인.
  ```bash
  curl -I http://192.168.7.88:3000
  curl -I http://192.168.7.88:8000/api/health
  ```
- 방화벽에서 80/443(프록시), 3000/8000(백엔드·프론트) 허용 여부 확인.

---

## 4. 증상별로 보는 경우

| 증상 | 확인할 것 |
|------|------------|
| 502 Bad Gateway | 프록시 → 192.168.7.88:3000/8000 연결 실패. 포트·방화벽·서비스 기동 여부 확인. |
| 빈 화면 | 브라우저 개발자도구 네트워크 탭에서 JS/CSS 404 여부 확인. |
| 연결 거부/타임아웃 | DNS(digest.aiground.ai → 프록시 서버 IP), 방화벽, 서비스 리스닝 포트 확인. |

위 수정 후에도 digest.aiground.ai 가 안 되면,  
프록시 서버의 실제 Nginx 설정 파일 경로와 `curl -I http://digest.aiground.ai` 결과를 알려주시면 다음 단계 제안이 가능합니다.
