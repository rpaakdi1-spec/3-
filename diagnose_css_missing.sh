#!/bin/bash
# CSS 파일 사라지는 근본 원인 진단

echo "========================================="
echo "🔍 CSS 파일 사라지는 근본 원인 진단"
echo "========================================="
echo ""

cd /root/uvis

# 1. 호스트에 CSS 파일이 있는지 확인
echo "=== 1. 호스트 dist 폴더 CSS 파일 ==="
echo "CSS 파일 수:"
find frontend/dist/assets -name "*.css" -type f 2>/dev/null | wc -l
echo ""
echo "CSS 파일 목록:"
ls -lh frontend/dist/assets/*.css 2>/dev/null || echo "❌ 호스트에 CSS 파일 없음!"
echo ""

# 2. 컨테이너 내부 CSS 파일
echo "=== 2. 컨테이너 내부 CSS 파일 ==="
echo "CSS 파일 수:"
docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css" -type f 2>/dev/null | wc -l
echo ""
echo "CSS 파일 목록:"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/*.css 2>/dev/null || echo "❌ 컨테이너에 CSS 파일 없음!"
echo ""

# 3. 볼륨 마운트가 실제로 작동하는지 확인
echo "=== 3. 볼륨 마운트 실제 작동 확인 ==="
echo "호스트의 특정 파일 생성:"
touch frontend/dist/TEST_MOUNT_CHECK.txt
echo "test content" > frontend/dist/TEST_MOUNT_CHECK.txt

echo "컨테이너에서 해당 파일 보이는지:"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/TEST_MOUNT_CHECK.txt 2>/dev/null && echo "✅ 볼륨 마운트 작동 중!" || echo "❌ 볼륨 마운트 문제!"

# 정리
rm -f frontend/dist/TEST_MOUNT_CHECK.txt
echo ""

# 4. dist 폴더 전체 구조 확인
echo "=== 4. 호스트 dist 폴더 전체 구조 ==="
echo "모든 파일 타입별 개수:"
echo "  JS: $(find frontend/dist/assets -name "*.js" 2>/dev/null | wc -l)"
echo "  CSS: $(find frontend/dist/assets -name "*.css" 2>/dev/null | wc -l)"
echo "  기타: $(find frontend/dist/assets -type f ! -name "*.js" ! -name "*.css" 2>/dev/null | wc -l)"
echo ""
echo "샘플 파일들:"
ls -lh frontend/dist/assets/ | head -20
echo ""

# 5. 마운트 세부 정보
echo "=== 5. 볼륨 마운트 세부 정보 ==="
docker inspect uvis-frontend --format='{{json .Mounts}}' | python3 -m json.tool
echo ""

# 6. 컨테이너 내부 실제 파일 시스템
echo "=== 6. 컨테이너 내부 파일 시스템 ==="
echo "assets 폴더 내용 (처음 20개):"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/ 2>/dev/null | head -20
echo ""

# 7. 파일 권한 확인
echo "=== 7. 파일 권한 확인 ==="
echo "호스트 CSS 권한:"
ls -la frontend/dist/assets/*.css 2>/dev/null | head -3 || echo "없음"
echo ""
echo "컨테이너 assets 폴더 권한:"
docker exec uvis-frontend ls -ld /usr/share/nginx/html/assets/ 2>/dev/null
echo ""

# 8. 최근 빌드 로그 확인
echo "=== 8. 최근 npm build 결과 ==="
if [ -f frontend/package.json ]; then
    echo "package.json 존재 - 빌드 스크립트:"
    cat frontend/package.json | grep -A3 '"build"'
    echo ""
    
    echo "Vite 설정 확인:"
    if [ -f frontend/vite.config.ts ]; then
        echo "vite.config.ts의 build 설정:"
        grep -A10 "build:" frontend/vite.config.ts 2>/dev/null || echo "build 설정 없음"
    fi
fi
echo ""

# 9. 최근 빌드 실행해보기 (실제 빌드는 안하고 dry-run)
echo "=== 9. 빌드 명령어 테스트 ==="
echo "현재 Node 버전:"
cd frontend && node --version 2>/dev/null || echo "Node.js 없음"
echo ""
echo "npm 버전:"
npm --version 2>/dev/null || echo "npm 없음"
cd ..
echo ""

# 10. CSS가 생성되지 않는 이유 분석
echo "=== 10. CSS 생성 여부 분석 ==="
if [ -f frontend/dist/assets/index-BjMybcaV.css ]; then
    echo "✅ 호스트에 CSS 존재: index-BjMybcaV.css"
    echo "파일 크기: $(stat -c%s frontend/dist/assets/index-BjMybcaV.css) bytes"
    echo "수정 시간: $(stat -c%y frontend/dist/assets/index-BjMybcaV.css)"
else
    echo "❌ 호스트에 CSS 없음!"
    echo ""
    echo "가능한 원인:"
    echo "  1. npm build가 CSS를 생성하지 않음 (Vite 설정 문제)"
    echo "  2. 빌드는 되었지만 다른 위치에 저장"
    echo "  3. 빌드 후 파일이 삭제됨"
    echo ""
    echo "확인: 빌드 출력 디렉토리"
    if [ -f frontend/vite.config.ts ]; then
        grep -E "outDir|build.outDir" frontend/vite.config.ts
    fi
fi
echo ""

# 11. 컨테이너와 호스트 파일 비교
echo "=== 11. 호스트 vs 컨테이너 파일 비교 ==="
HOST_JS=$(find frontend/dist/assets -name "*.js" 2>/dev/null | wc -l)
HOST_CSS=$(find frontend/dist/assets -name "*.css" 2>/dev/null | wc -l)
CONTAINER_JS=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.js" 2>/dev/null | wc -l)
CONTAINER_CSS=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css" 2>/dev/null | wc -l)

echo "파일 비교:"
echo "  호스트    JS: $HOST_JS, CSS: $HOST_CSS"
echo "  컨테이너  JS: $CONTAINER_JS, CSS: $CONTAINER_CSS"
echo ""

if [ "$HOST_JS" -eq "$CONTAINER_JS" ] && [ "$HOST_CSS" -eq "$CONTAINER_CSS" ]; then
    echo "✅ 파일 수 일치 - 볼륨 마운트 정상"
elif [ "$HOST_CSS" -gt 0 ] && [ "$CONTAINER_CSS" -eq 0 ]; then
    echo "🔴 호스트에는 CSS 있지만 컨테이너에 없음!"
    echo "   → 볼륨 마운트 문제 또는 권한 문제"
elif [ "$HOST_CSS" -eq 0 ]; then
    echo "🔴 호스트에 CSS 파일이 없음!"
    echo "   → npm build가 CSS를 생성하지 않음"
else
    echo "⚠️ 파일 수 불일치"
fi
echo ""

# 12. 마운트 타입 확인 (bind vs volume)
echo "=== 12. 마운트 타입 상세 ==="
docker inspect uvis-frontend --format='{{range .Mounts}}Type: {{.Type}}, Source: {{.Source}}, Destination: {{.Destination}}, RW: {{.RW}}
{{end}}'
echo ""

# 최종 진단
echo "========================================="
echo "=== 🎯 근본 원인 진단 결과 ==="
echo "========================================="
echo ""

if [ "$HOST_CSS" -eq 0 ]; then
    echo "🔴 근본 원인: 호스트에 CSS 파일이 없음"
    echo ""
    echo "원인 분석:"
    echo "  1. npm build가 CSS를 생성하지 않거나"
    echo "  2. CSS가 다른 위치에 저장되거나"
    echo "  3. 빌드 후 삭제됨"
    echo ""
    echo "해결책:"
    echo "  A) 재빌드: cd /root/uvis/frontend && npm run build"
    echo "  B) Vite 설정 확인: cat vite.config.ts | grep -A10 build"
    echo "  C) 빌드 로그 확인: npm run build 2>&1 | tee build.log"
elif [ "$HOST_CSS" -gt 0 ] && [ "$CONTAINER_CSS" -eq 0 ]; then
    echo "🔴 근본 원인: 볼륨 마운트 문제"
    echo ""
    echo "호스트에는 CSS 있지만 컨테이너에 안 보임"
    echo ""
    echo "가능한 원인:"
    echo "  1. 마운트가 읽기 전용(ro)이지만 권한 문제"
    echo "  2. SELinux 또는 AppArmor 차단"
    echo "  3. 심볼릭 링크 문제"
    echo ""
    echo "해결책:"
    echo "  A) 재시작: docker-compose restart frontend"
    echo "  B) 권한 확인: ls -la /root/uvis/frontend/dist/assets/"
    echo "  C) 마운트 재설정: docker-compose down frontend && docker-compose up -d frontend"
else
    echo "✅ CSS 파일이 정상적으로 있음"
    echo ""
    echo "다른 원인 가능성:"
    echo "  1. 브라우저 캐시 문제"
    echo "  2. Nginx 캐시 문제"
    echo "  3. 잘못된 CSS 파일명 참조"
fi

echo ""
echo "진단 완료!"
