# 근무시간 필드 제거 완료

## 개요
회원가입 양식과 인사카드에서 근무시간 관련 필드를 제거했습니다.

## 제거된 필드
1. **work_start_time** - 근무 시작 시간
2. **work_end_time** - 근무 종료 시간
3. **max_work_hours** - 최대 근무 시간

## 변경된 파일

### Backend
1. **backend/app/schemas/auth.py**
   - `SignupRequest` 스키마에서 work_start_time, work_end_time, max_work_hours 제거

2. **backend/app/models/pending_employee.py**
   - `PendingEmployee` 모델에서 work_start_time, work_end_time, max_work_hours 컬럼 제거

3. **backend/alembic/versions/20260228_133550_add_pending_employees.py**
   - pending_employees 테이블 생성 마이그레이션에서 work_start_time, work_end_time, max_work_hours 컬럼 제거

4. **backend/app/api/auth.py**
   - `/auth/signup` 엔드포인트에서 근무시간 필드 제거
   - `/users/{user_id}/approve` 엔드포인트에서 Employee 생성 시 근무시간 필드 제거

### Frontend
1. **frontend/src/pages/SignupPage.tsx**
   - SignupFormData 인터페이스에서 work_start_time, work_end_time, max_work_hours 제거
   - 초기값 설정에서 근무시간 필드 제거
   - Step 3 (조직/근무 정보)에서 근무시간 입력 필드 제거

## 영향 범위
- 새로운 회원가입 시 근무시간 정보를 입력할 필요 없음
- 승인 시 생성되는 Employee 레코드에도 근무시간 정보가 저장되지 않음
- 기존 Employee 테이블의 work_start_time, work_end_time, max_work_hours 컬럼은 그대로 유지됨 (기존 데이터 보존)

## 배포 방법

서버에서 다음 명령어를 실행하세요:

```bash
cd /root/uvis

# 최신 코드 가져오기
git pull origin main

# 컨테이너 중지
docker-compose down

# 데이터베이스 마이그레이션 실행
docker-compose run --rm backend alembic upgrade head

# 백엔드/프론트엔드 재빌드 및 시작
docker-compose up -d --build backend frontend

# 상태 확인
docker-compose ps
docker-compose logs -f backend frontend
```

## 검증 방법

1. **회원가입 테스트**
   - http://139.150.11.99/ 접속
   - 회원가입 클릭
   - Step 3 (조직/근무)에서 근무시간 입력 필드가 없는지 확인
   - 입사일만 입력하고 다음 단계로 진행
   - 회원가입 완료

2. **승인 테스트**
   - 관리자 로그인
   - 설정 → 회원관리
   - 대기 사용자 승인
   - 인사카드가 정상 생성되는지 확인

3. **데이터베이스 확인**
   ```sql
   -- pending_employees 테이블 구조 확인 (work_start_time, work_end_time, max_work_hours 컬럼이 없어야 함)
   \d pending_employees
   
   -- employees 테이블은 그대로 유지 (기존 필드 보존)
   \d employees
   ```

## 커밋 정보
- Commit: b4a1648
- Message: "refactor: remove work hours fields from signup and employee card"
- Date: 2026-02-28

## 참고사항
- Employee 테이블의 기존 work_start_time, work_end_time, max_work_hours 컬럼은 유지됩니다
- 기존 직원 데이터는 영향을 받지 않습니다
- 새로 가입하는 사용자의 인사카드에는 근무시간 정보가 기본값(NULL 또는 default)으로 설정됩니다
