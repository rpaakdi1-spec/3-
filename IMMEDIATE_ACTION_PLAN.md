# 🚨 즉시 실행 액션 플랜

## 문제 진단
- ✅ 코드: ORD- 패턴 0건, max_weight_kg 0건 (CLEAN)
- ✅ Frontend 컨테이너: healthy
- ⚠️ Backend 컨테이너: unhealthy (16시간)
- ⚠️ 브라우저 캐시: 구 빌드 파일 캐시 가능성

## 즉시 실행 단계

### STEP 1: Backend 컨테이너 문제 해결 (서버에서 실행)
```bash
# 1. Backend 로그 확인
docker logs uvis-backend --tail 100 > backend_error.log
cat backend_error.log

# 2. Backend 재시작
docker-compose -f /root/uvis/docker-compose.prod.yml restart backend

# 3. 30초 대기 후 상태 확인
sleep 30
docker ps --filter "name=uvis-backend" --format "table {{.Names}}\t{{.Status}}"

# 4. Health 체크
docker inspect uvis-backend --format='{{.State.Health.Status}}'
```

### STEP 2: 브라우저 캐시 완전 삭제 (클라이언트에서 실행)

#### 방법 A: 시크릿 모드 (가장 빠름)
1. **Chrome/Edge**: `Ctrl + Shift + N`
2. **Firefox**: `Ctrl + Shift + P`
3. URL 입력: `http://139.150.11.99/orders`
4. 개발자 도구 열기: `F12`
5. Network 탭에서 "Disable cache" 체크
6. 페이지 새로고침: `Ctrl + Shift + R`

#### 방법 B: 캐시 완전 삭제 (권장)
1. `Ctrl + Shift + Delete` (Chrome/Edge)
2. 시간 범위: **전체 기간**
3. 체크 항목:
   - ☑️ 쿠키 및 기타 사이트 데이터
   - ☑️ 캐시된 이미지 및 파일
4. "데이터 삭제" 클릭
5. 브라우저 **완전히 종료** 후 재시작
6. `http://139.150.11.99/orders` 접속

### STEP 3: UI 검증 체크리스트

#### 주문 페이지 (`/orders`)
- [ ] "주문 등록" 버튼 클릭
- [ ] ❌ `ORD-20260130-001` 텍스트 없어야 함
- [ ] ❌ "주문 코드" 필드 없어야 함
- [ ] ❌ "주문번호" 필드 없어야 함
- [ ] ✅ "주문일자"가 첫 번째 필드로 표시
- [ ] ✅ "온도대", "거래처" 필드는 존재

#### 차량 페이지 (`/vehicles`)
- [ ] "차량 등록" 버튼 클릭
- [ ] ❌ "최대 적재중량(kg)" 필드 없어야 함
- [ ] ✅ "최대 팔레트 수" 필드는 존재
- [ ] ✅ "최대 CBM" 필드는 존재

#### 거래처 페이지 (`/clients`)
- [ ] "거래처 등록" 버튼 클릭
- [ ] ❌ "거래처 코드" 필드 없어야 함
- [ ] ✅ "거래처명"이 첫 번째 필드로 표시

## 🔧 추가 조치 (필요시)

### Backend가 여전히 unhealthy인 경우
```bash
# 서버에서 실행
cd /root/uvis

# 1. Backend 컨테이너 로그 상세 확인
docker logs uvis-backend --tail 200 | tee backend_full.log

# 2. 데이터베이스 연결 확인
docker exec uvis-backend python -c "
from sqlalchemy import create_engine
from backend.app.core.config import settings
engine = create_engine(settings.DATABASE_URL)
conn = engine.connect()
print('✅ DB Connection OK')
conn.close()
"

# 3. 강제 재빌드 (최후 수단)
./complete_cleanup_and_redeploy.sh
```

### 프론트엔드 캐시 문제가 지속되는 경우
```bash
# 서버에서 실행 - Nginx 캐시 삭제
docker exec uvis-nginx sh -c "rm -rf /var/cache/nginx/*"
docker-compose -f /root/uvis/docker-compose.prod.yml restart nginx
```

## 📋 예상 결과

### 성공 시나리오
```
✅ Backend: healthy
✅ 브라우저: 시크릿 모드에서 깨끗한 UI
✅ 주문 모달: ORD- 텍스트 없음
✅ 주문 모달: 주문 코드/번호 필드 없음
✅ 첫 필드: 주문일자
```

### 실패 시나리오 대응
| 증상 | 원인 | 해결책 |
|------|------|--------|
| Backend unhealthy 지속 | DB 연결 문제 | `docker logs uvis-backend` 확인 후 재시작 |
| UI에 여전히 ORD- 표시 | 브라우저 캐시 | 전체 기간 캐시 삭제 후 시크릿 모드 테스트 |
| 필드가 여전히 표시됨 | 빌드 파일 미반영 | Nginx 캐시 삭제 후 재시작 |

## 🎯 최우선 실행 명령어 (복사해서 실행)

### 서버 측
```bash
# Backend 재시작 및 상태 확인
cd /root/uvis
docker-compose -f docker-compose.prod.yml restart backend
sleep 30
./quick_status.sh
```

### 클라이언트 측
1. 브라우저를 **완전히 종료**
2. **시크릿 모드**로 재시작
3. `http://139.150.11.99/orders` 접속
4. `F12` (개발자 도구) → Network 탭 → "Disable cache" 체크
5. `Ctrl + Shift + R` (강제 새로고침)
6. "주문 등록" 버튼 클릭
7. ORD- 텍스트/주문 코드/주문번호 필드 존재 여부 확인

## 📞 보고 형식

아래 형식으로 결과를 공유해주세요:

```
Backend 상태: [healthy/unhealthy]
브라우저: [Chrome/Edge/Firefox] [일반/시크릿] 모드
주문 모달:
- ORD- 텍스트: [있음/없음]
- 주문 코드 필드: [있음/없음]
- 주문번호 필드: [있음/없음]
- 첫 번째 필드: [필드명]

스크린샷: [가능하면 첨부]
```
