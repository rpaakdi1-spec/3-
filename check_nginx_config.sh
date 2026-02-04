#!/bin/bash
# Nginx 설정 확인 스크립트

echo "🔍 Nginx 컨테이너 내부 설정 파일 확인..."
echo ""

echo "1️⃣ Nginx 설정 파일 위치 확인:"
docker exec uvis-nginx ls -la /etc/nginx/

echo ""
echo "2️⃣ Nginx 메인 설정 내용 (HTTP 서버 블록):"
docker exec uvis-nginx cat /etc/nginx/nginx.conf | grep -A 30 "server {" | head -40

echo ""
echo "3️⃣ API 프록시 설정 확인:"
docker exec uvis-nginx cat /etc/nginx/nginx.conf | grep -A 15 "location /api/"

echo ""
echo "4️⃣ Nginx 설정 문법 검사:"
docker exec uvis-nginx nginx -t

echo ""
echo "5️⃣ Nginx 프로세스 확인:"
docker exec uvis-nginx ps aux | grep nginx
