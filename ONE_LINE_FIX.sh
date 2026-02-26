#!/bin/bash
# UVIS 레이아웃 원라인 수정 스크립트
# 사용법: bash ONE_LINE_FIX.sh

cd /root/uvis && \
echo "🔧 OrdersPage.tsx 수정..." && \
python3 -c "f='/root/uvis/frontend/src/pages/OrdersPage.tsx';c=open(f).read();c=c.replace('      )}\n  );','      )}\n    </>\n  );');open(f,'w').write(c);print('✅ OK')" && \
echo "🔧 .dockerignore 수정..." && \
sed -i '/^dist$/d;/^build$/d;/^# Build output/d' frontend/.dockerignore && \
echo "✅ OK" && \
echo "🔨 빌드 중..." && \
cd frontend && npm run build > /tmp/build.log 2>&1 && cd .. && \
echo "✅ OK" && \
echo "🐳 Docker 재빌드..." && \
docker-compose stop frontend > /dev/null 2>&1 && \
docker-compose rm -f frontend > /dev/null 2>&1 && \
docker rmi uvis-frontend > /dev/null 2>&1 && \
docker-compose build --no-cache frontend > /tmp/docker-build.log 2>&1 && \
echo "✅ OK" && \
echo "🚀 배포 중..." && \
docker-compose up -d frontend && \
sleep 15 && \
echo "✅ OK" && \
echo "" && \
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" && \
echo "🎉 배포 완료!" && \
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" && \
echo "" && \
echo "📊 CSS 파일 확인:" && \
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/*.css 2>/dev/null && \
echo "" && \
echo "✅ 성공! 이제 브라우저 캐시를 삭제하고 테스트하세요:" && \
echo "   1. Ctrl+Shift+Delete → 전체 기간 → 캐시 삭제" && \
echo "   2. Chrome 재시작" && \
echo "   3. http://139.150.11.99/login 접속" && \
echo ""
