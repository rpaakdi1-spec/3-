# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install --legacy-peer-deps

# 소스 복사 및 빌드
COPY . .
# Build for production using .env.production
ENV NODE_ENV=production
RUN npm run build

# Production stage
FROM nginx:alpine

LABEL maintainer="UVIS Team"
LABEL description="UVIS Logistics Frontend"

# 빌드 결과물 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 80

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
