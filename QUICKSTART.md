# 🚀 UVIS 빠른 시작 가이드

**최종 업데이트**: 2026-03-01 14:52  
**상태**: ✅ 운영 중

---

## 📍 주요 정보

### 접속 정보
- **프론트엔드**: http://139.150.11.99/
- **API**: http://139.150.11.99/api/v1/
- **API 문서**: http://139.150.11.99/api/docs
- **GitHub**: https://github.com/rpaakdi1-spec/3-

### 관리자 계정
```
Username: admin
Password: admin123
```

---

## ⚡ 긴급 명령어

### 서버 상태 확인
```bash
cd /root/uvis
docker compose ps
curl http://139.150.11.99/api/v1/health
```

### 로그 확인
```bash
# Backend 에러 확인
docker compose logs backend --tail=100 | grep -i "error\|exception"

# 최근 API 호출 확인
docker compose logs backend --tail=50

# 실시간 로그
docker compose logs backend -f
```

### 재시작
```bash
cd /root/uvis

# Backend만 재시작
docker compose restart backend

# Frontend만 재시작
docker compose restart frontend

# 전체 재시작
docker compose restart

# 완전 재시작 (이미지 재빌드)
docker compose down
docker compose build
docker compose up -d
```

---

## 🔄 배포 프로세스

### 1. 코드 업데이트
```bash
cd /root/uvis
git pull origin main
```

### 2. Backend 배포
```bash
docker compose build backend
docker compose up -d backend
sleep 20
curl http://139.150.11.99/api/v1/health
```

### 3. Frontend 배포
```bash
docker compose build --no-cache frontend
docker compose up -d frontend
sleep 20
curl -I http://139.150.11.99/
```

### 4. DB 마이그레이션 (필요시)
```bash
docker compose run --rm backend alembic upgrade head
```

---

## 🗄️ 데이터베이스 관리

### DB 접속
```bash
docker compose exec db psql -U uvis_user -d uvis_db
```

### 자주 쓰는 쿼리

#### 사용자 목록
```sql
SELECT u.id, u.username, u.full_name, u.approval_status, u.is_active, 
       pe.employee_code, pe.name
FROM users u
LEFT JOIN pending_employees pe ON pe.user_id = u.id
ORDER BY u.id;
```

#### 승인된 사용자
```sql
SELECT u.id, u.username, u.approval_status, u.employee_id
FROM users u
WHERE u.approval_status = 'approved'
ORDER BY u.id;
```

#### 직원 목록
```sql
SELECT id, employee_code, name, phone, role, is_active
FROM employees
ORDER BY id;
```

#### 차량 목록
```sql
SELECT id, code, plate_number, vehicle_type, tonnage, 
       driver_name, driver_phone
FROM vehicles
ORDER BY id;
```

---

## 🔧 일반적인 문제 해결

### 1. 500 에러
```bash
# 로그 확인
docker compose logs backend --tail=200 | grep -A 30 "500\|ERROR\|Traceback"

# Backend 재시작
docker compose restart backend
```

### 2. 데이터가 안 보일 때
```bash
# DB 데이터 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "SELECT COUNT(*) FROM users;"

# Backend 로그 확인
docker compose logs backend --tail=100
```

### 3. 로그인 안 될 때
```bash
# 사용자 상태 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT username, is_active, approval_status FROM users WHERE username='admin';
"
```

### 4. 차량 배정 안 될 때
```bash
# Employee 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, employee_code, name, phone FROM employees WHERE is_active=true;
"

# 차량 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, code, driver_name, driver_phone FROM vehicles;
"
```

---

## 📋 핵심 기능 사용법

### 1. 신규 회원 승인
1. Settings → User Management → **Pending Approval** 탭
2. **승인** 버튼 클릭
3. 확인 대화상자에서 확인
4. 자동으로 Employee 생성됨

### 2. 인사카드 등록
1. **인사관리** 페이지
2. **"승인된 사용자 불러오기"** 버튼 클릭
3. 모달에서 **"인사카드 등록"** 버튼 클릭
4. Employee 목록에 추가됨

### 3. 차량-운전자 배정
1. **차량-운전자 배정 관리** 페이지
2. 좌측 운전자 풀에서 운전자 선택
3. 우측 차량 카드로 드래그 앤 드롭
4. 자동으로 배정 및 업데이트

### 4. 사용자 정보 수정
1. Settings → User Management → **Active Users** 탭
2. 수정할 사용자의 **수정** 버튼 클릭
3. 4단계 폼 작성:
   - Step 1: 계정 정보
   - Step 2: 개인 정보
   - Step 3: 조직/근무 정보
   - Step 4: 자격증 정보
4. **저장** 버튼 클릭

---

## 📊 현재 데이터 상태

### Users: 8명
- admin (승인됨)
- testuser01~03 (대기 중)
- testuser10 (대기 중)
- testuser20 (승인됨) ⭐
- rpaakdi, rpaakdi1 (대기 중)

### Employees: 0명
- 승인된 사용자를 인사카드로 등록 필요

### Vehicles: 46대
- 모두 11톤 DUAL 타입으로 설정됨
- 드라이버 미배정 상태

---

## 📞 지원

문제가 발생하면:
1. 로그 확인 (`docker compose logs backend --tail=100`)
2. 상세 백업 문서 참조 (`BACKUP_COMPLETE_20260301_145219.md`)
3. GitHub Issues에 문의

---

**✨ 완료된 주요 기능**:
- ✅ 회원가입 및 승인 시스템
- ✅ 4단계 사용자 정보 수정
- ✅ 인사관리 ↔ 회원관리 통합
- ✅ 차량-운전자 배정 (전화번호 우선 매칭)
- ✅ 승인된 사용자 자동 Employee 변환
- ✅ 디버그 로깅 강화
