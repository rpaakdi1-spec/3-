# ─────────────────────────────────────────────
# Pre-built: dist/는 CI/로컬에서 빌드 후 git에 포함
# 서버에서는 npm install / vite build 없이 nginx만 실행
# → 빌드 시간: ~200s → ~3s
# ─────────────────────────────────────────────
FROM nginx:alpine

LABEL maintainer="UVIS Team"
LABEL description="UVIS Logistics Frontend"

# 사전 빌드된 정적 파일 복사
COPY dist/ /usr/share/nginx/html/

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
