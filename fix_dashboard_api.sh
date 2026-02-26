#!/bin/bash

cat << 'EOF'
=== 프론트엔드 API 경로 수정 ===

다음 명령어를 실행하세요:

cd /root/uvis/frontend

# 1. client.ts 수정 - /dispatches/dashboard → /dispatches/stats/summary
sed -i "s|'/dispatches/dashboard'|'/dispatches/stats/summary'|g" src/api/client.ts

# 2. 변경 확인
grep -n "dispatches/stats/summary" src/api/client.ts

# 3. 리빌드
npm run build

# 4. 배포
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker exec uvis-frontend nginx -s reload

# 5. 브라우저에서 테스트
echo ""
echo "✅ 수정 완료!"
echo "브라우저를 새로고침(Ctrl+F5)하세요."
echo "대시보드가 정상 표시되어야 합니다!"
EOF

