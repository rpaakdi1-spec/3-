# 회원가입 테스트 가이드

## ✅ 백엔드 배포 완료
- **상태**: 정상 작동 중 ✅
- **헬스체크**: `{"status":"healthy","app_name":"Cold Chain Dispatch System","environment":"production"}`
- **URL**: http://139.150.11.99:8000

## 🎯 테스트 시나리오

### 1️⃣ 프론트엔드 재빌드 (서버에서 실행)
프론트엔드가 이전 코드를 캐싱하고 있을 수 있으므로 재빌드가 필요합니다:

```bash
cd /root/uvis

# 프론트엔드 중지
docker compose down frontend

# 이미지 재빌드 (캐시 없이)
docker compose build --no-cache frontend

# 프론트엔드 시작
docker compose up -d frontend

# 10초 대기 후 상태 확인
sleep 10
docker compose ps frontend

# 접속 확인
curl -I http://139.150.11.99/
```

**기대 출력**: HTTP/1.1 200 OK

### 2️⃣ 회원가입 테스트

#### Step 1: 회원가입 페이지 접속
1. 브라우저에서 http://139.150.11.99/ 접속
2. "회원가입" 버튼 클릭

#### Step 2: 계정 정보 입력 (Step 1/4)
- **사용자명**: `testuser01`
- **비밀번호**: `test123456`
- **비밀번호 확인**: `test123456`
- **권한**: `DRIVER` (기본값)
- ✅ **확인사항**: Email 필드가 **없어야** 함

**"다음" 버튼 클릭**

#### Step 3: 기본 인적사항 (Step 2/4)
- **이름**: `홍길동`
- **영문명**: `Hong Gildong` (선택사항, 비워둬도 됨)
- **전화번호**: `01012345678` (숫자만 입력)
  - ✅ **자동 포맷팅 확인**: 입력 즉시 `010-1234-5678`로 변환되어야 함
- **비상연락처**: `01098765432` (선택사항)
  - ✅ **자동 포맷팅 확인**: 입력 시 `010-9876-5432`로 변환
- **주소**: (선택사항, 비워둬도 됨)
- ✅ **확인사항**: 사원번호 필드가 **없어야** 함

**"다음" 버튼 클릭**

#### Step 4: 조직/근무 정보 (Step 3/4)
- **직급**: `DRIVER` (기본값)
- **고용 형태**: `FULL_TIME` (기본값)
- **부서**: (선택사항)
- **직책**: (선택사항)
- **입사일**: (기본값: 오늘 날짜, 변경 가능)
- ✅ **확인사항**: 
  - **근무 시작 시간** 필드가 **없어야** 함
  - **근무 종료 시간** 필드가 **없어야** 함
  - **최대 근무 시간** 필드가 **없어야** 함

**"다음" 버튼 클릭**

#### Step 5: 자격증 정보 (Step 4/4)
- **운전면허 종류**: (선택사항)
- **운전면허 번호**: (선택사항)
- **운전면허 발급일**: (선택사항)
- **화물운송자격증 보유**: (체크박스, 선택사항)
- **지게차 운전 가능**: (체크박스, 선택사항)
- **지게차 자격증 보유**: (체크박스, 선택사항)

**"가입 완료" 버튼 클릭**

#### Step 6: 가입 완료 확인
✅ **성공 메시지**: "회원가입이 완료되었습니다. 관리자 승인 후 로그인 가능합니다." (토스트 알림)
✅ **자동 리다이렉트**: 2초 후 로그인 페이지로 이동

---

### 3️⃣ 관리자 승인 테스트

#### Step 1: 관리자 로그인
1. http://139.150.11.99/ 접속
2. 사용자명: `admin`
3. 비밀번호: `admin123`
4. "로그인" 버튼 클릭

#### Step 2: 대기 중인 사용자 확인
1. 좌측 메뉴에서 **"설정"** 클릭
2. **"사용자 관리"** 탭 선택
3. **"Pending Users"** 탭 클릭

#### Step 3: 사용자 정보 확인
테이블에서 다음 정보를 확인:
- **사용자명**: `testuser01`
- **이름**: `홍길동`
- **사원번호**: `PENDING_20260228_XXX` (예: `PENDING_20260228_001`)
  - ✅ **확인사항**: `PENDING_YYYYMMDD_XXX` 형식의 임시 사원번호가 자동 생성되어야 함
- **전화번호**: `010-1234-5678` (하이픈 포함)
- **Email**: `testuser01@pending.local` (자동 생성)
- **승인 상태**: `pending`

#### Step 4: 사용자 승인
1. 해당 사용자 행의 **"Approve"** 버튼 클릭
2. (선택) 최종 사원번호 입력 팝업이 나타나면 예: `D001`, `E001` 등 입력
3. "확인" 버튼 클릭

#### Step 5: 승인 완료 확인
✅ **성공 메시지**: "User approved successfully" (토스트 알림)
✅ **목록 업데이트**: 해당 사용자가 Pending Users 목록에서 사라짐
✅ **사용자 목록 확인**: "Active Users" 탭에서 `testuser01` 확인 가능

---

### 4️⃣ 승인된 사용자 로그인 테스트

#### Step 1: 로그아웃
1. 우측 상단 관리자 아이콘 클릭
2. "로그아웃" 선택

#### Step 2: 승인된 사용자로 로그인
1. 사용자명: `testuser01`
2. 비밀번호: `test123456`
3. "로그인" 버튼 클릭

#### Step 3: 로그인 성공 확인
✅ **대시보드 접속**: 메인 대시보드 화면이 표시되어야 함
✅ **권한 확인**: DRIVER 권한으로 제한된 메뉴만 표시
✅ **사용자 정보**: 우측 상단에 "홍길동" 또는 `testuser01` 표시

---

## 📊 데이터베이스 검증 (선택사항)

### pending_employees 테이블 확인
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT 
  id, 
  employee_code, 
  name, 
  phone, 
  email, 
  created_at 
FROM pending_employees 
WHERE name = '홍길동'
ORDER BY id DESC 
LIMIT 1;
"
```

**기대 출력** (승인 전):
```
 id | employee_code         | name   | phone         | email                    | created_at
----+-----------------------+--------+---------------+--------------------------+-------------------
  1 | PENDING_20260228_001  | 홍길동 | 010-1234-5678 | testuser01@pending.local | 2026-02-28 15:10
```

### employees 테이블 확인 (승인 후)
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT 
  id, 
  employee_code, 
  name, 
  phone, 
  email, 
  hire_date, 
  created_at 
FROM employees 
WHERE name = '홍길동'
ORDER BY id DESC 
LIMIT 1;
"
```

**기대 출력** (승인 후):
```
 id | employee_code | name   | phone         | email                    | hire_date  | created_at
----+---------------+--------+---------------+--------------------------+------------+-------------------
  1 | D001          | 홍길동 | 010-1234-5678 | testuser01@pending.local | 2026-02-28 | 2026-02-28 15:15
```

### users 테이블 확인
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT 
  id, 
  username, 
  email, 
  full_name, 
  phone, 
  role, 
  approval_status, 
  is_active 
FROM users 
WHERE username = 'testuser01';
"
```

**기대 출력** (승인 후):
```
 id | username   | email                    | full_name | phone         | role   | approval_status | is_active
----+------------+--------------------------+-----------+---------------+--------+-----------------+-----------
  X | testuser01 | testuser01@pending.local | 홍길동    | 010-1234-5678 | DRIVER | approved        | t
```

---

## 🔍 트러블슈팅

### 문제 1: 회원가입 시 422 에러 발생
**원인**: 백엔드 이미지가 업데이트되지 않음
**해결**:
```bash
cd /root/uvis
docker compose down backend
docker compose build --no-cache backend
docker compose up -d backend
sleep 10
curl http://139.150.11.99:8000/health
```

### 문제 2: Email 필드가 여전히 표시됨
**원인**: 프론트엔드 이미지가 업데이트되지 않음
**해결**:
```bash
cd /root/uvis
docker compose down frontend
docker compose build --no-cache frontend
docker compose up -d frontend
sleep 10
curl -I http://139.150.11.99/
```

### 문제 3: 전화번호 포맷팅이 안 됨
**확인사항**:
1. 브라우저 캐시 삭제 (Ctrl+Shift+Delete)
2. 프론트엔드 재빌드 (위 문제 2 참고)
3. 개발자 도구(F12) → Console에서 JavaScript 에러 확인

### 문제 4: 승인 후에도 로그인 안 됨
**확인사항**:
```bash
# 사용자 상태 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT username, approval_status, is_active 
FROM users 
WHERE username = 'testuser01';
"
```
**기대값**: `approval_status = 'approved'`, `is_active = t`

**해결** (상태가 잘못된 경우):
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
UPDATE users 
SET approval_status = 'approved', is_active = true 
WHERE username = 'testuser01';
"
```

---

## ✅ 테스트 체크리스트

### 프론트엔드 확인
- [ ] Email 필드 없음 (Step 1)
- [ ] 사원번호 필드 없음 (Step 2)
- [ ] 전화번호 자동 포맷팅 (`010-1234-5678`)
- [ ] 비상연락처 자동 포맷팅
- [ ] 근무시간 필드 없음 (work_start_time, work_end_time, max_work_hours)

### 백엔드 확인
- [ ] 회원가입 성공 (200 OK)
- [ ] 자동 employee_code 생성 (`PENDING_YYYYMMDD_XXX`)
- [ ] 자동 email 생성 (`{username}@pending.local`)
- [ ] pending_employees 테이블에 데이터 삽입
- [ ] 전화번호 하이픈 포함 저장 (`010-1234-5678`)

### 관리자 승인
- [ ] Pending Users 목록에 표시
- [ ] 임시 사원번호 확인 (`PENDING_20260228_XXX`)
- [ ] Approve 버튼 클릭 성공
- [ ] Employee 레코드 생성
- [ ] User 상태 업데이트 (approved, active)
- [ ] pending_employees 레코드 삭제

### 로그인 테스트
- [ ] 승인된 사용자 로그인 성공
- [ ] 대시보드 접근 가능
- [ ] DRIVER 권한 메뉴만 표시

---

## 📝 다음 단계
1. ✅ 백엔드 배포 완료
2. ⏳ 프론트엔드 재빌드 필요 (위 명령어 실행)
3. ⏳ 회원가입 테스트 진행
4. ⏳ 승인 테스트 진행
5. ⏳ 로그인 테스트 진행
6. ⏳ 엔드투엔드 검증 완료

**테스트 결과를 알려주시면 추가 조치를 도와드리겠습니다!** 🚀
