# LinkDigest Frontend - Docker 이미지 (맥/리눅스)
# 1단계: React 빌드
FROM node:18-alpine AS build

WORKDIR /app

# 패키지 파일 복사 및 설치
COPY package*.json ./
RUN npm ci --only=production=false

# 소스 복사 (.dockerignore로 node_modules, build 등 제외)
COPY . .

# 빌드 시 API URL: /api (Nginx 또는 동일 호스트 백엔드 프록시 사용 시)
ARG REACT_APP_API_URL=/api
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# 2단계: Nginx로 정적 파일 서빙
FROM nginx:alpine

# SPA 라우팅: 없는 경로는 index.html 로
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# 빌드 결과물 복사
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
