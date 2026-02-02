# ⭐ 여기서 시작하세요! - UVIS 필드 제거 최종 가이드

## 🎯 현재 상황 요약

```
✅ 코드 상태: ORD- 패턴 0건, max_weight_kg 0건 (완벽하게 제거됨)
✅ Frontend: healthy (16시간 정상 실행 중)
⚠️ Backend: unhealthy (16시간 - 재시작 필요)
⚠️ 브라우저: 캐시 문제로 구 UI 표시 가능성
```

## 📋 준비된 도구 (총 4개 스크립트 + 4개 가이드)

### 🔧 실행 스크립트 (서버 `/root/uvis/`에 배치)

| 파일 | 크기 | 용도 | 실행 시간 |
|------|------|------|----------|
| **quick_status.sh** | 1.6K | 빠른 상태 확인 | ~5초 |
| **verify_current_state.sh** | 2.1K | 전체 상태 검증 | ~10초 |
| **diagnose_backend_health.sh** | 4.4K | Backend 문제 진단 ⭐ NEW | ~30초 |
| **complete_cleanup_and_redeploy.sh** | 4.0K | 완전 재배포 | ~5분 |

### 📚 참고 가이드

| 파일 | 크기 | 내용 |
|------|------|------|
| **EXECUTE_NOW.md** | 7.6K | 즉시 실행 가이드 (가장 중요) |
| **IMMEDIATE_ACTION_PLAN.md** | 4.7K | 문제 해결 액션 플랜 |
| **COPY_TO_SERVER.txt** | 5.4K | 서버 업로드용 스크립트 |
| **BROWSER_CACHE_GUIDE.md** | 4.6K | 브라우저 캐시 삭제 가이드 |

---

## 🚀 3단계 즉시 실행 (총 4분 소요)

### ✅ STEP 1: 서버 진단 및 재시작 (2분)

#### 1-1. 서버 접속
```bash
ssh root@139.150.11.99
cd /root/uvis
```

#### 1-2. NEW 스크립트 생성 (diagnose_backend_health.sh)

**방법 A: 파일 직접 복사**
- 로컬에서 `COPY_TO_SERVER.txt` 열기
- "방법 2" 섹션의 전체 명령어 복사
- 서버 터미널에 붙여넣기

**방법 B: SCP 업로드**
```bash
# 로컬 머신에서 실행
scp diagnose_backend_health.sh root@139.150.11.99:/root/uvis/
```

#### 1-3. Backend 진단 및 재시작
```bash
# 진단 실행
./diagnose_backend_health.sh

# Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 30초 대기
sleep 30

# 상태 확인
./quick_status.sh
```

**예상 결과:**
```
✅ uvis-backend: healthy
✅ ORD- pattern: CLEAN (0 references)
✅ max_weight_kg: CLEAN (0 references)
🎉 ALL CLEAN! Code is ready.
```

---

### ✅ STEP 2: 브라우저 캐시 삭제 (1분)

#### 🔥 중요: 시크릿 모드 사용 (가장 빠름)

1. **시크릿 모드 열기**
   - Chrome/Edge: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`

2. **개발자 도구 설정**
   - `F12` 눌러서 개발자 도구 열기
   - **Network** 탭 클릭
   - ☑️ **"Disable cache"** 체크

3. **URL 접속**
   ```
   http://139.150.11.99/orders
   ```

4. **강제 새로고침**
   - `Ctrl + Shift + R` 또는 `Ctrl + F5`

#### 💡 대안: 캐시 완전 삭제 (더 확실함)
```
1. Ctrl + Shift + Delete
2. 시간 범위: "전체 기간"
3. ☑️ 쿠키 및 기타 사이트 데이터
4. ☑️ 캐시된 이미지 및 파일
5. "데이터 삭제" 클릭
6. 브라우저 완전히 종료 후 재시작
```

---

### ✅ STEP 3: UI 테스트 (1분)

#### 주문 페이지 테스트 (필수)

1. **URL 접속**: `http://139.150.11.99/orders`
2. **"주문 등록"** 버튼 클릭
3. **확인 사항**:

| 항목 | 기대 결과 |
|------|-----------|
| `ORD-20260130-001` 텍스트 | ❌ 없어야 함 |
| "주문 코드" 필드 | ❌ 없어야 함 |
| "주문번호" 필드 | ❌ 없어야 함 |
| 첫 번째 필드 | ✅ "주문일자" |
| 온도대 필드 | ✅ 존재 |
| 거래처 필드 | ✅ 존재 |

#### 차량 페이지 테스트 (선택)

1. **URL**: `http://139.150.11.99/vehicles`
2. **확인**: "최대 적재중량(kg)" 필드가 **없어야 함**

#### 거래처 페이지 테스트 (선택)

1. **URL**: `http://139.150.11.99/clients`
2. **확인**: "거래처 코드" 필드가 **없어야 함**

---

## 🛠️ 문제가 발생한 경우

### ❌ Backend가 여전히 unhealthy

```bash
# 1. 상세 로그 확인
docker logs uvis-backend --tail 100

# 2. 에러 패턴 확인
docker logs uvis-backend 2>&1 | grep -i "error\|exception"

# 3. 강제 재빌드 (최후 수단)
cd /root/uvis
./complete_cleanup_and_redeploy.sh
```

### ❌ UI에서 여전히 ORD- 또는 필드 표시

```bash
# Nginx 캐시 삭제 및 재시작
docker exec uvis-nginx sh -c "rm -rf /var/cache/nginx/*"
docker-compose -f /root/uvis/docker-compose.prod.yml restart nginx

# Frontend 재시작
docker-compose -f /root/uvis/docker-compose.prod.yml restart frontend
```

**브라우저에서:**
1. `F12` → Console 탭에서 에러 확인
2. `F12` → Network 탭에서 "OrderModal" 검색
3. 해당 파일의 Response에서 `ORD-` 검색 (없어야 함)

---

## 📊 테스트 결과 보고 양식

테스트 완료 후 아래 양식으로 보고해주세요:

```
========================================
🎯 UVIS 필드 제거 테스트 결과
========================================

📅 일시: 2026-02-02 [시간]
🌐 서버: 139.150.11.99

1. Backend 상태
   - quick_status.sh: [healthy/unhealthy]
   - diagnose_backend_health.sh: [실행함/안 함]
   - 재시작: [했음/안 함]

2. 브라우저 환경
   - 브라우저: [Chrome/Edge/Firefox]
   - 버전: [예: Chrome 130]
   - 모드: [일반/시크릿]
   - 캐시 삭제: [했음/안 함]

3. 주문 페이지 검증 (/orders)
   ✅ 성공 / ❌ 실패
   - ORD- 텍스트: [있음/없음]
   - 주문 코드 필드: [있음/없음]
   - 주문번호 필드: [있음/없음]
   - 첫 필드: [필드명]

4. 차량 페이지 검증 (/vehicles) - 선택
   - 최대 적재중량(kg): [있음/없음]

5. 거래처 페이지 검증 (/clients) - 선택
   - 거래처 코드: [있음/없음]

6. 스크린샷
   [주문 등록 모달 캡처 첨부]

========================================
```

---

## 🎉 성공 기준

모든 항목이 아래와 같으면 **완료**:

```
✅ Backend container: healthy
✅ ORD- 패턴: 0건
✅ max_weight_kg: 0건
✅ 주문 모달: ORD- 텍스트 없음
✅ 주문 모달: 주문 코드/번호 필드 없음
✅ 주문 모달: 주문일자가 첫 필드
✅ 차량 모달: 최대 적재중량(kg) 필드 없음
✅ 거래처 모달: 거래처 코드 필드 없음
```

---

## 🚀 Quick Copy-Paste Commands

### 서버 측 (한 번에 실행)
```bash
ssh root@139.150.11.99 << 'REMOTE'
cd /root/uvis
./diagnose_backend_health.sh
docker-compose -f docker-compose.prod.yml restart backend
sleep 30
./quick_status.sh
REMOTE
```

### 또는 단계별로:
```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 진단
cd /root/uvis && ./diagnose_backend_health.sh

# 3. 재시작 및 확인
docker-compose -f docker-compose.prod.yml restart backend && sleep 30 && ./quick_status.sh
```

---

## 📞 추가 지원이 필요한 경우

다음 정보를 제공해주세요:

1. `./diagnose_backend_health.sh` 전체 출력
2. `./quick_status.sh` 출력
3. 브라우저 Console 탭의 에러 메시지
4. 주문 등록 모달 스크린샷
5. Network 탭에서 OrderModal 관련 파일의 Response

---

## 📂 관련 파일 위치

- **서버**: `/root/uvis/*.sh`
- **로컬**: `/home/user/webapp/*.{sh,md,txt}`
- **URL**: `http://139.150.11.99/orders`

---

## ⏱️ 전체 소요 시간

| 단계 | 시간 |
|------|------|
| 서버 진단 | 30초 |
| Backend 재시작 | 30초 |
| 브라우저 캐시 삭제 | 1분 |
| UI 테스트 | 1분 |
| **총계** | **약 3-4분** |

---

## 🎯 지금 바로 시작!

**가장 먼저 할 일 3가지:**

1. **서버 접속**
   ```bash
   ssh root@139.150.11.99
   ```

2. **Backend 진단**
   ```bash
   cd /root/uvis && ./diagnose_backend_health.sh
   ```

3. **결과 공유**
   - 위 출력을 복사해서 보고

---

**✅ 모든 준비 완료! 이제 시작하세요! 🚀**
