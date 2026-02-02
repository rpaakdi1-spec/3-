# 🚀 지금 바로 실행하세요!

## 📊 현재 상황
```
✅ 코드: ORD- 패턴 0건, max_weight_kg 0건 (CLEAN)
✅ Frontend: healthy (16시간)
⚠️ Backend: unhealthy (16시간)
⚠️ 브라우저: 캐시 문제 가능성
```

---

## ⚡ 즉시 실행 단계 (2분 소요)

### 1️⃣ 서버에 업로드할 파일 (4개)
아래 파일들을 서버 `/root/uvis/`에 업로드하세요:

1. ✅ **quick_status.sh** (1.6KB) - 이미 서버에 있음
2. ✅ **verify_current_state.sh** (2.1KB) - 이미 서버에 있음
3. ✅ **complete_cleanup_and_redeploy.sh** (4.0KB) - 이미 서버에 있음
4. ⭐ **diagnose_backend_health.sh** (4.4KB) - **새로 추가됨**

#### 서버 업로드 명령어 (로컬에서 실행)
```bash
# 방법 1: SCP로 한 번에 업로드
scp /path/to/diagnose_backend_health.sh root@139.150.11.99:/root/uvis/

# 방법 2: 또는 서버에서 직접 생성 (아래 전체 스크립트 복사)
```

---

### 2️⃣ 서버에서 실행 (순서대로)

#### ✅ Step 2-1: 서버 접속
```bash
ssh root@139.150.11.99
cd /root/uvis
```

#### 🔍 Step 2-2: Backend 문제 진단 (30초)
```bash
# 실행권한 부여 (필요시)
chmod +x diagnose_backend_health.sh

# 상세 진단 실행
./diagnose_backend_health.sh

# 또는 로그로 저장
./diagnose_backend_health.sh > backend_diagnosis.log
cat backend_diagnosis.log
```

**예상 결과:** 
- ✅ DB 연결 성공 → Backend 재시작만 필요
- ❌ DB 연결 실패 → 로그에서 구체적 에러 확인

#### 🔧 Step 2-3: Backend 재시작 (30초)
```bash
# Backend 컨테이너 재시작
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

### 3️⃣ 브라우저 테스트 (2분)

#### 🔥 중요: 캐시 완전 삭제

**방법 A: 시크릿 모드 (가장 빠름)**
1. Chrome/Edge: `Ctrl + Shift + N`
2. Firefox: `Ctrl + Shift + P`
3. URL 입력: `http://139.150.11.99/orders`
4. `F12` (개발자 도구) → Network 탭 → "Disable cache" 체크
5. `Ctrl + Shift + R` (강제 새로고침)

**방법 B: 캐시 완전 삭제 (권장)**
1. `Ctrl + Shift + Delete`
2. 시간 범위: **전체 기간**
3. 체크: 쿠키, 캐시된 이미지/파일
4. 브라우저 **완전히 종료** 후 재시작

#### ✅ 검증 체크리스트

**주문 페이지 테스트**
1. URL: `http://139.150.11.99/orders`
2. "주문 등록" 버튼 클릭
3. 확인 사항:
   - ❌ `ORD-20260130-001` 텍스트 없어야 함
   - ❌ "주문 코드" 필드 없어야 함
   - ❌ "주문번호" 필드 없어야 함
   - ✅ "주문일자"가 첫 번째 필드
   - ✅ "온도대", "거래처" 필드는 존재

**차량 페이지 테스트** (선택)
1. URL: `http://139.150.11.99/vehicles`
2. "차량 등록" 버튼 클릭
3. 확인: "최대 적재중량(kg)" 필드 없어야 함

**거래처 페이지 테스트** (선택)
1. URL: `http://139.150.11.99/clients`
2. "거래처 등록" 버튼 클릭
3. 확인: "거래처 코드" 필드 없어야 함

---

## 🛠️ 문제 해결

### ❌ Backend가 여전히 unhealthy인 경우

#### Option 1: 로그 상세 확인
```bash
# 전체 로그 확인
docker logs uvis-backend --tail 200 > backend_full.log
cat backend_full.log

# 에러만 필터링
docker logs uvis-backend 2>&1 | grep -i "error\|exception\|failed"
```

#### Option 2: 강제 재빌드 (5분)
```bash
cd /root/uvis
./complete_cleanup_and_redeploy.sh
```

### ❌ UI에서 여전히 ORD- 또는 필드가 보이는 경우

#### Step 1: Nginx 캐시 삭제
```bash
# 서버에서 실행
docker exec uvis-nginx sh -c "rm -rf /var/cache/nginx/*"
docker-compose -f docker-compose.prod.yml restart nginx
```

#### Step 2: Frontend 재빌드 확인
```bash
# Frontend 컨테이너 로그 확인
docker logs uvis-frontend --tail 20

# 빌드 시간 확인 (최근 16시간 이내여야 함)
docker inspect uvis-frontend --format='{{.State.StartedAt}}'
```

#### Step 3: 브라우저 Developer Tools로 확인
1. `F12` (개발자 도구)
2. Network 탭
3. `Ctrl + Shift + R` (강제 새로고침)
4. `OrderModal` 검색
5. Response 탭에서 `ORD-` 검색 (없어야 함)

---

## 📋 보고 형식

테스트 완료 후 아래 형식으로 결과를 공유해주세요:

```
========================================
🎯 UVIS 필드 제거 테스트 결과
========================================

📅 테스트 일시: 2026-02-02
🌐 서버: 139.150.11.99

1. Backend 상태
   - quick_status.sh 결과: [healthy/unhealthy]
   - 재시작 여부: [했음/안 함]
   - diagnose_backend_health.sh 실행: [했음/안 함]

2. 브라우저 테스트
   - 브라우저: [Chrome/Edge/Firefox]
   - 모드: [일반/시크릿]
   - 캐시 삭제: [했음/안 함]

3. 주문 페이지 (/orders)
   - ORD- 텍스트: [있음/없음]
   - 주문 코드 필드: [있음/없음]
   - 주문번호 필드: [있음/없음]
   - 첫 번째 필드: [필드명]

4. 차량 페이지 (/vehicles) - 선택
   - 최대 적재중량(kg) 필드: [있음/없음]

5. 거래처 페이지 (/clients) - 선택
   - 거래처 코드 필드: [있음/없음]

6. 스크린샷
   [가능하면 주문 등록 모달 스크린샷 첨부]

========================================
```

---

## 🎉 성공 시나리오

모든 것이 정상이라면 다음과 같이 표시됩니다:

```
✅ Backend: healthy
✅ ORD- 패턴: 0건 (CLEAN)
✅ max_weight_kg: 0건 (CLEAN)
✅ 주문 모달: ORD- 텍스트 없음
✅ 주문 모달: 주문 코드/번호 필드 없음
✅ 첫 필드: 주문일자
✅ 차량 모달: 최대 적재중량(kg) 필드 없음
✅ 거래처 모달: 거래처 코드 필드 없음
```

---

## 📞 추가 지원

문제가 지속되면 다음 정보를 공유해주세요:

1. `./diagnose_backend_health.sh` 전체 출력
2. `./verify_current_state.sh` 전체 출력
3. 브라우저 Developer Tools의 Console 탭 에러
4. 브라우저 Developer Tools의 Network 탭 스크린샷
5. 주문 등록 모달 스크린샷

---

## ⏱️ 예상 소요 시간

| 단계 | 소요 시간 |
|------|----------|
| 서버 진단 실행 | 30초 |
| Backend 재시작 | 30초 |
| 브라우저 캐시 삭제 | 1분 |
| UI 테스트 | 2분 |
| **총계** | **약 4분** |

---

## 🚀 Quick Commands (복사해서 사용)

### 서버 측 (순서대로 실행)
```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 디렉터리 이동
cd /root/uvis

# 3. Backend 진단
./diagnose_backend_health.sh

# 4. Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend && sleep 30

# 5. 상태 확인
./quick_status.sh
```

### 클라이언트 측
1. 브라우저 완전히 종료
2. 시크릿 모드로 시작: `Ctrl + Shift + N`
3. URL: `http://139.150.11.99/orders`
4. `F12` → Network → "Disable cache" 체크
5. `Ctrl + Shift + R` 강제 새로고침
6. "주문 등록" 클릭 → ORD- 텍스트/필드 확인

---

## ✅ 최종 체크리스트

- [ ] 서버에 4개 스크립트 모두 업로드됨
- [ ] `diagnose_backend_health.sh` 실행 완료
- [ ] Backend 재시작 완료
- [ ] `quick_status.sh`에서 Backend healthy 확인
- [ ] 브라우저 캐시 완전 삭제
- [ ] 시크릿 모드로 테스트 완료
- [ ] 주문 모달에서 ORD- 텍스트 없음 확인
- [ ] 주문 모달에서 주문 코드/번호 필드 없음 확인
- [ ] 테스트 결과 보고 작성

---

**🎯 지금 바로 시작하세요!**

가장 먼저 할 일:
1. 서버 접속: `ssh root@139.150.11.99`
2. 진단 실행: `cd /root/uvis && ./diagnose_backend_health.sh`
3. 결과 공유
