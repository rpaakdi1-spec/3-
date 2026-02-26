#!/bin/bash

cat << 'EOF'
=== 방법 1: src/config/api.ts 수정 ===

다음 명령어를 실행하세요:

cd /root/uvis/frontend

# BASE_URL을 /api/v1에서 /api로 변경
sed -i "s|BASE_URL: import.meta.env.VITE_API_URL || '/api/v1'|BASE_URL: import.meta.env.VITE_API_URL || '/api'|" src/config/api.ts

# 변경 확인
grep "BASE_URL" src/config/api.ts

# 리빌드
npm run build

# 배포
cd /root/uvis
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker exec uvis-frontend nginx -s reload

# 브라우저에서 테스트
echo "이제 브라우저에서 http://139.150.11.99 접속해서 로그인 테스트하세요!"
echo "admin / admin123"
EOF

