#!/bin/bash

# 설정 페이지 가로 탭 수정 배포 스크립트
# 이중 사이드바 문제 해결

echo "======================================"
echo "설정 페이지 가로 탭 배포 시작"
echo "======================================"
echo ""

# 1. 서버 정보
echo "📍 서버: root@139.150.11.99"
echo "📂 경로: /root/uvis/frontend"
echo ""

# 2. 배포 명령어
echo "🚀 다음 명령어를 서버에서 실행하세요:"
echo ""
cat << 'EOF'
# 1. 프론트엔드 디렉토리로 이동
cd /root/uvis/frontend

# 2. 최신 코드 가져오기
git fetch origin main
git reset --hard origin/main

# 3. 최신 커밋 확인 (f74be44 이어야 함)
echo "=== 현재 커밋 확인 ==="
git log --oneline -1

# 4. 변경사항 확인
echo ""
echo "=== 설정 페이지 탭 변경 확인 ==="
grep -n "Horizontal Tabs" src/pages/SettingsPage.tsx

# 5. 프론트엔드 빌드
echo ""
echo "=== 프론트엔드 빌드 시작 ==="
npm run build

# 6. 빌드 결과물을 컨테이너에 복사
echo ""
echo "=== 컨테이너에 복사 ==="
docker cp dist/. uvis-frontend:/usr/share/nginx/html/

# 7. 프론트엔드 컨테이너 재시작
echo ""
echo "=== 프론트엔드 컨테이너 재시작 ==="
docker restart uvis-frontend

# 8. 10초 대기
sleep 10

# 9. 컨테이너 상태 확인
echo ""
echo "=== 컨테이너 상태 ==="
docker ps | grep uvis-frontend

# 10. 최근 로그 확인
echo ""
echo "=== 최근 로그 ==="
docker logs uvis-frontend --tail 20
EOF

echo ""
echo "======================================"
echo "배포 완료 후 브라우저 테스트"
echo "======================================"
echo ""
echo "🧪 테스트 절차:"
echo "1. 브라우저 캐시 완전 삭제 (Ctrl+Shift+Delete)"
echo "   - 전체 기간 선택"
echo "   - 캐시된 이미지 및 파일 삭제"
echo ""
echo "2. InPrivate/시크릿 모드로 접속"
echo "   - URL: http://139.150.11.99/settings"
echo ""
echo "3. 확인 사항:"
echo "   ✅ 왼쪽 사이드바가 1개만 표시됨 (메인 네비게이션)"
echo "   ✅ 설정 페이지 상단에 가로 탭이 표시됨"
echo "   ✅ 탭: 프로필 | 알림 설정 | 보안 | 시스템"
echo "   ✅ 각 탭 클릭 시 컨텐츠가 바뀜"
echo "   ✅ 활성화된 탭은 파란색 밑줄로 표시됨"
echo ""
echo "======================================"
echo "문제가 계속되면 다음을 확인:"
echo "======================================"
echo ""
echo "1. F12 개발자 도구 열기"
echo "2. Console 탭에서 에러 확인"
echo "3. Network 탭에서 SettingsPage 파일 확인"
echo "   - 예상 파일: SettingsPage-XXXXX.js"
echo "   - 상태: 200 OK"
echo ""
echo "======================================"
