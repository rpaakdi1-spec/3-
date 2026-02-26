# 🚀 서버 배포 가이드 - OrdersPage.tsx 수정

## ⚡ 즉시 적용 방법 (권장)

서버에서 직접 파일을 수정하는 방법입니다.

### 1️⃣ OrdersPage.tsx 수정

```bash
# 서버에 SSH 접속
ssh root@139.150.11.99

# 파일 백업
cd /root/uvis/frontend/src/pages
cp OrdersPage.tsx OrdersPage.tsx.backup

# 파일 수정 (방법 A: sed 명령 사용 - 추천)
# Layout import 추가 (6번째 줄 뒤에)
sed -i '5a import Layout from '\''../components/common/Layout'\'';' OrdersPage.tsx

# loading return 수정 (251-253줄)
sed -i '251,253s/return (<Loading \/>\n  );\n  }/return <Loading \/>;/' OrdersPage.tsx

# Fragment를 Layout으로 변경 (255줄)
sed -i '255s/return (<>/return (\n    <Layout>/' OrdersPage.tsx

# 닫는 태그 수정 (669줄)
sed -i 's/    <\/>/    <\/Layout>/' OrdersPage.tsx

# 또는 (방법 B: vi 편집기 사용)
vi OrdersPage.tsx

# vi에서 다음 변경사항 적용:
# 1. 6번째 줄에 추가:
#    import Layout from '../components/common/Layout';
#
# 2. 251-253줄을:
#    if (loading) {
#      return <Loading />;
#    }
#
# 3. 255-256줄을:
#    return (
#      <Layout>
#
# 4. 마지막에서 8번째 줄을:
#      </Layout>
#    );
```

### 2️⃣ Dockerfile 간소화

```bash
cd /root/uvis/frontend

# 백업
cp Dockerfile Dockerfile.backup.$(date +%Y%m%d_%H%M%S)

# 새 Dockerfile 생성
cat > Dockerfile << 'DOCKERFILE_END'
FROM nginx:alpine
LABEL maintainer="UVIS Team"
LABEL description="UVIS Logistics Frontend"

# Copy pre-built dist folder
COPY dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE_END

echo "✅ Dockerfile 업데이트 완료"
```

### 3️⃣ 빌드 및 배포

```bash
# 기존 빌드 삭제 및 새로 빌드
cd /root/uvis/frontend
rm -rf dist/
npm run build

# 빌드 결과 확인
echo "=== CSS 파일 확인 ==="
ls -lh dist/assets/*.css

echo ""
echo "=== index.html stylesheet 확인 ==="
cat dist/index.html | grep stylesheet

# Docker 이미지 재빌드
cd /root/uvis

# 기존 컨테이너 중지 및 삭제
docker-compose stop frontend
docker-compose rm -f frontend

# 기존 이미지 삭제
docker rmi uvis-frontend || echo "이미지가 이미 삭제됨"

# 새 이미지 빌드
echo "Docker 이미지 빌드 시작..."
docker-compose build --no-cache frontend

# 컨테이너 시작
echo "컨테이너 시작..."
docker-compose up -d frontend

# 시작 대기
echo "컨테이너 시작 대기 중 (15초)..."
sleep 15

# 검증
echo ""
echo "=== 배포 검증 ==="
echo "1. CSS 파일:"
docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.css"

echo ""
echo "2. index.html stylesheet 참조:"
docker exec uvis-frontend cat /usr/share/nginx/html/index.html | grep stylesheet

echo ""
echo "3. JS 파일 개수:"
JS_COUNT=$(docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js | wc -l")
echo "   JavaScript 파일: $JS_COUNT 개"

if [ "$JS_COUNT" -lt 80 ]; then
    echo "   ⚠️  경고: JS 파일이 예상보다 적습니다 (기대: ~90개)"
else
    echo "   ✅ JS 파일 정상"
fi

echo ""
echo "✅ 배포 완료!"
```

## 📝 수정 내용 요약

### OrdersPage.tsx 변경사항

#### Before (오류)
```typescript
import Loading from '../components/common/Loading';
// ... (Layout import 없음)

if (loading) {
  return (<Loading />
);
}

return (<>
  <div className="space-y-6">
    ...
  </div>
  </Layout>  // ← 열지 않은 태그를 닫음
);
```

#### After (수정)
```typescript
import Loading from '../components/common/Loading';
import Layout from '../components/common/Layout';  // ← 추가

if (loading) {
  return <Loading />;  // ← 괄호 수정
}

return (
  <Layout>  // ← Fragment 대신 Layout 사용
    <div className="space-y-6">
      ...
    </div>
  </Layout>  // ← 올바른 닫기
);
```

## ✅ 성공 확인

### 1. 서버 측 검증
```bash
# CSS 파일 확인 (3개, 각 13-15KB)
docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.css"

# 기대 결과:
# -rw-r--r-- 1 root root 13K ... OrderCalendarPage-D0RJcmxZ.css
# -rw-r--r-- 1 root root 15K ... index-BjMybcaV.css
# -rw-r--r-- 1 root root 15K ... leaflet-Dgihpmma.css

# index.html 확인
docker exec uvis-frontend cat /usr/share/nginx/html/index.html | grep stylesheet

# 기대 결과:
#     <link rel="stylesheet" crossorigin href="/assets/index-BjMybcaV.css">

# JS 파일 개수 확인
docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js | wc -l"

# 기대 결과: 80 이상
```

### 2. 브라우저 테스트

#### 캐시 완전 삭제
1. **모든 Edge 창 닫기**
   - 작업 표시줄에서 Edge 아이콘 우클릭
   - "모든 창 닫기" 선택
   
2. **작업 관리자에서 확인**
   - Ctrl + Shift + Esc
   - "Microsoft Edge" 프로세스 모두 종료
   
3. **Edge 재시작 후 캐시 삭제**
   - Ctrl + Shift + Delete
   - "기간" → **전체 기간** 선택
   - ✅ 쿠키 및 기타 사이트 데이터
   - ✅ 캐시된 이미지 및 파일
   - "지금 지우기" 클릭
   
4. **Edge 완전 재시작**

#### Incognito 모드 테스트
```
1. Ctrl + Shift + N (InPrivate 창 열기)
2. http://139.150.11.99/login 입력
3. admin / admin123 로그인
4. 대시보드 확인
```

### 3. 예상 결과

#### ✅ 정상적인 레이아웃
- **로그인 페이지**: 중앙에 흰색 로그인 박스, 파란색 그라데이션 배경
- **대시보드**:
  - 왼쪽: 회색 사이드바 (아이콘 + 메뉴 텍스트)
  - 상단: 흰색 헤더 (알림 아이콘)
  - 본문: 4개 통계 카드 (2x2 그리드)
  - 아래: 차트 및 빠른 작업 버튼
- **주문 관리**: 테이블, 필터, 검색창 정상 배치
- **배송 캘린더**: 달력 UI 정상 표시

#### DevTools 확인 (F12)
```
Console 탭:
  ✅ 빨간색 에러 없음
  (ServiceWorker 경고는 무시 가능)

Network 탭 (CSS 필터):
  ✅ index-BjMybcaV.css → Status: 200, Size: ~4KB
  ✅ OrderCalendarPage-D0RJcmxZ.css → Status: 200
  ✅ leaflet-Dgihpmma.css → Status: 200
```

## 🔧 문제 해결

### ❌ 빌드 실패: TypeScript 오류
```bash
# 오류 확인
cd /root/uvis/frontend
npm run build 2>&1 | grep "error TS"

# OrdersPage.tsx 다시 확인
head -20 src/pages/OrdersPage.tsx
tail -10 src/pages/OrdersPage.tsx

# 수정 후 재빌드
npm run build
```

### ❌ CSS 로드 안됨 (404 에러)
```bash
# CSS 파일 직접 접근 테스트
curl -I http://139.150.11.99/assets/index-BjMybcaV.css

# 컨테이너 내부 파일 확인
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/

# Nginx 재시작
docker exec uvis-frontend nginx -s reload

# 또는 컨테이너 재시작
docker-compose restart frontend
```

### ❌ 레이아웃이 여전히 깨짐
```bash
# 1. 브라우저 강력 새로고침
Ctrl + Shift + R (5번 반복)

# 2. 브라우저 캐시 강제 삭제
edge://settings/clearBrowserData
→ "고급" 탭
→ "전체 기간" 선택
→ 모든 항목 체크
→ "지금 지우기"

# 3. 다른 브라우저 테스트
Chrome Incognito 모드로 확인

# 4. 서버 측 완전 재배포
cd /root/uvis
docker-compose down frontend
docker rmi uvis-frontend
docker-compose up -d frontend
```

### ❌ 컨테이너 시작 실패
```bash
# 로그 확인
docker logs uvis-frontend --tail 50

# 일반적인 원인:
# 1. 포트 충돌 → 다른 프로세스가 80 포트 사용 중
# 2. dist 폴더 없음 → npm run build 다시 실행
# 3. Nginx 설정 오류 → nginx.conf 확인

# Nginx 설정 테스트
docker exec uvis-frontend nginx -t
```

## 📊 예상 소요 시간

| 단계 | 소요 시간 |
|------|-----------|
| OrdersPage.tsx 수정 | 1-2분 |
| Dockerfile 수정 | 30초 |
| npm run build | 15-20초 |
| Docker 이미지 빌드 | 15-20초 |
| 컨테이너 시작 | 10초 |
| 브라우저 캐시 삭제 | 30초 |
| **총 소요 시간** | **약 3-4분** |

## 📞 추가 지원

배포 중 문제가 발생하면:
1. `docker logs uvis-frontend --tail 100` 로그 확인
2. `npm run build` 오류 메시지 확인
3. 브라우저 DevTools Console 확인

---
**작성일**: 2026-02-25  
**버전**: 1.0 최종
