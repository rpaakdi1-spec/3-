# 인사관리 시스템 구현 로드맵

**최종 업데이트**: 2026-02-27  
**현재 커밋**: 0df5a19  
**프로젝트**: 화물운수업 통합 인사관리 시스템

---

## 🎯 프로젝트 목표

### 핵심 기능
1. **조직 계층 관리**: 마스터(총괄) → 관리자(운영사원) → 운전직
2. **통합 인사카드**: 모든 회원을 화물운수업 맞춤 인사카드로 등록
3. **운전자 풀 연동**: 운전직 사원 정보를 차량-운전자 배정 시스템에 자동 반영
4. **자격증 관리**: 운전면허, 화물운송자격증, 지게차 운전능력 통합 관리

### 주요 특징
- ✅ **지게차 운전능력**: 자격증 유무와 별개로 실제 운전 가능 여부 관리
- ✅ **권한 기반 접근**: 직급별 차등 권한 부여
- ✅ **자동 동기화**: 운전직 사원 → 운전자 풀 자동 반영
- ✅ **필터 및 검색**: 다양한 조건으로 인력 검색

---

## 📋 현재 상태

### ✅ 완료된 작업 (설계 단계)
- [x] HR 시스템 전체 설계 문서 작성 (`HR_SYSTEM_DESIGN.md`)
- [x] 지게차 운전능력 필드 설계 (`FORKLIFT_ABILITY_DESIGN.md`)
- [x] 업데이트 요약 문서 작성 (`FORKLIFT_ABILITY_UPDATE_SUMMARY.md`)
- [x] 데이터베이스 스키마 설계
- [x] API 엔드포인트 설계
- [x] UI/UX 목업 설계
- [x] 권한 체계 설계

### 🚧 진행 예정 (구현 단계)

#### Phase 1: 데이터베이스 & 백엔드 (3일)
- [ ] Employee 모델 구현
- [ ] 데이터베이스 마이그레이션
- [ ] API 엔드포인트 구현
- [ ] 권한 미들웨어 구현
- [ ] 단위 테스트 작성

#### Phase 2: 프론트엔드 UI (4일)
- [ ] 인사 관리 페이지 구현
- [ ] 인사카드 모달 구현
- [ ] 운전자 풀 연동 업데이트
- [ ] 필터 및 검색 기능 구현
- [ ] 반응형 디자인 적용

#### Phase 3: 통합 & 배포 (2일)
- [ ] 통합 테스트
- [ ] 운전자 풀 동기화 테스트
- [ ] 배차 시스템 연동 테스트
- [ ] 프로덕션 배포
- [ ] 사용자 가이드 작성

---

## 🗓️ 상세 일정

### Week 1: 백엔드 구현 (Day 1-3)

#### Day 1: 데이터베이스 모델
**작업 항목**:
1. `backend/app/models/employee.py` 파일 생성
   - Employee 모델 정의
   - 관계(Relationships) 설정
   - 인덱스 및 제약조건 추가

2. Alembic 마이그레이션 스크립트 생성
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add employee model with forklift ability"
   ```

3. 마이그레이션 실행 (개발 환경)
   ```bash
   alembic upgrade head
   ```

**검증**:
- [ ] 테이블이 정상 생성되었는지 확인
- [ ] 인덱스가 올바르게 설정되었는지 확인
- [ ] 외래키 제약조건 확인

---

#### Day 2: API 스키마 & 엔드포인트
**작업 항목**:
1. `backend/app/schemas/employee.py` 파일 생성
   - EmployeeBase, EmployeeCreate, EmployeeUpdate 스키마
   - EmployeeResponse 스키마
   - 검증 규칙 추가

2. `backend/app/api/v1/endpoints/employees.py` 파일 생성
   - CRUD 엔드포인트 구현:
     - `GET /api/v1/employees` - 목록 조회 (필터링, 페이지네이션)
     - `POST /api/v1/employees` - 신규 등록
     - `GET /api/v1/employees/{id}` - 상세 조회
     - `PUT /api/v1/employees/{id}` - 정보 수정
     - `DELETE /api/v1/employees/{id}` - 삭제 (소프트 삭제)
   - 특수 엔드포인트:
     - `GET /api/v1/employees/drivers` - 운전직 조회
     - `GET /api/v1/employees/drivers/available` - 배차 가능 운전자
     - `POST /api/v1/employees/bulk-upload` - Excel 대량 등록
     - `GET /api/v1/employees/export` - Excel 내보내기

3. 권한 체크 데코레이터 추가
   ```python
   @router.get("/", dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MASTER]))])
   ```

**검증**:
- [ ] Swagger UI에서 API 문서 확인
- [ ] Postman으로 각 엔드포인트 테스트
- [ ] 권한 체크 동작 확인

---

#### Day 3: 비즈니스 로직 & 테스트
**작업 항목**:
1. `backend/app/crud/employee.py` 파일 생성
   - CRUD 비즈니스 로직 구현
   - 필터링 로직 (role, is_active, license_type, 등)
   - 검색 로직 (이름, 사번, 전화번호)

2. 운전자 풀 동기화 로직
   ```python
   async def sync_driver_pool():
       """운전직 사원을 운전자 풀에 동기화"""
       employees = await employee_crud.get_drivers()
       # Driver 모델과 동기화
   ```

3. 단위 테스트 작성
   - `tests/api/test_employees.py`
   - CRUD 작업 테스트
   - 필터링 테스트
   - 권한 테스트

**검증**:
- [ ] 모든 테스트 통과
- [ ] 코드 커버리지 80% 이상
- [ ] API 응답 시간 200ms 이하

---

### Week 2: 프론트엔드 구현 (Day 4-7)

#### Day 4: 기본 페이지 구조
**작업 항목**:
1. `frontend/src/pages/EmployeeManagementPage.tsx` 생성
   - 페이지 레이아웃 구성
   - 헤더 (제목, 신규 등록 버튼)
   - 검색바
   - 필터 섹션
   - 직원 목록 그리드

2. API 클라이언트 생성
   - `frontend/src/api/employees.ts`
   - axios 기반 API 호출 함수들

3. 상태 관리 설정
   ```typescript
   const [employees, setEmployees] = useState<Employee[]>([]);
   const [loading, setLoading] = useState(false);
   const [searchTerm, setSearchTerm] = useState('');
   const [filters, setFilters] = useState<EmployeeFilters>({});
   ```

**검증**:
- [ ] 페이지 접근 가능
- [ ] API 호출 성공
- [ ] 로딩 상태 표시

---

#### Day 5: 직원 카드 & 필터
**작업 항목**:
1. `EmployeeCard` 컴포넌트 생성
   - 직원 사진 표시
   - 기본 정보 (사번, 이름, 직급, 전화번호)
   - 배지 (화물자격증, 지게차 가능)
   - 액션 버튼 (상세, 편집, 삭제)

2. 필터 컴포넌트 구현
   - 직급 필터 (MASTER, ADMIN, MANAGER, DRIVER)
   - 고용 형태 필터 (정규직, 계약직, 일용직)
   - 재직 상태 필터 (재직, 퇴사)
   - 면허 종류 필터
   - 화물자격증 필터
   - 지게차 운전 필터:
     - 전체
     - 운전 가능 (자격증 보유)
     - 운전 가능 (자격증 미보유)
     - 운전 불가

3. 검색 기능 구현
   - 실시간 검색 (debounce 300ms)
   - 이름, 사번, 전화번호 검색

**검증**:
- [ ] 필터 작동 확인
- [ ] 검색 정확도 확인
- [ ] 성능 테스트 (1000명 이상 데이터)

---

#### Day 6: 인사카드 모달
**작업 항목**:
1. `EmployeeModal` 컴포넌트 생성
   - 탭 구조 구현 (기본정보, 근무정보, 자격증, 급여정보)
   - 폼 검증 (react-hook-form)
   - 저장/취소 버튼

2. **기본정보 탭**:
   - 사진 업로드 (크롭 기능)
   - 사번 (자동 생성 옵션)
   - 이름, 영문명
   - 전화번호, 이메일
   - 주소 (다음 주소 API)
   - 비상연락처

3. **근무정보 탭**:
   - 직급 (Select)
   - 고용 형태 (Select)
   - 부서, 직책
   - 입사일, 퇴사일
   - 근무시간 (시작, 종료)
   - 최대근무시간

4. **자격증 탭**:
   - 운전면허
     - 면허 종류 (Select)
     - 면허번호
     - 발급일
   - 화물운송자격증
     - 보유 여부 (Checkbox)
     - 자격번호
     - 유효기간
   - 🆕 지게차 운전
     - **운전 가능 여부** (Checkbox) ← 주요 필드
     - 자격증 보유 여부 (Checkbox)
     - 자격번호
     - 발급일, 만료일
     - 💡 안내문구: "자격증 미보유 시에도 운전 가능 여부를 체크하면 실태 파악에 활용됩니다"

5. **급여정보 탭**:
   - 기본급
   - 수당 (식대, 교통비, 위험수당)
   - 계좌정보

**검증**:
- [ ] 폼 검증 정상 작동
- [ ] 데이터 저장 확인
- [ ] 탭 전환 부드러움
- [ ] 모바일 반응형 확인

---

#### Day 7: 운전자 풀 연동 & 통합
**작업 항목**:
1. `VehicleDriverManagementPage` 업데이트
   - 운전자 풀 데이터를 Employee API에서 가져오도록 수정
   - 기존 Driver 인터페이스를 Employee 인터페이스로 매핑
   - 지게차 가능 배지 추가 표시

2. 운전자 카드 UI 업데이트
   ```tsx
   <DriverCard>
     <Name>{employee.name}</Name>
     <Phone>{employee.phone}</Phone>
     <License>{employee.license_type}</License>
     <Badge show={employee.has_cargo_license}>화물자격증</Badge>
     <Badge show={employee.can_drive_forklift}>
       지게차 가능
       {employee.has_forklift_certificate && " (자격증 보유)"}
     </Badge>
   </DriverCard>
   ```

3. 필터 업데이트
   - 지게차 운전 능력 필터 추가
   - 기존 필터와 조합 가능하도록 로직 수정

**검증**:
- [ ] 운전자 풀에 올바른 데이터 표시
- [ ] 지게차 배지 정확히 표시
- [ ] 필터 조합 정상 작동
- [ ] 드래그앤드롭 기능 유지

---

### Week 3: 테스트 & 배포 (Day 8-9)

#### Day 8: 통합 테스트
**작업 항목**:
1. **E2E 테스트 시나리오**:
   - [ ] 직원 등록 → 운전자 풀 자동 반영
   - [ ] 지게차 가능 여부 변경 → 배지 업데이트
   - [ ] 필터 조합 테스트
   - [ ] 차량 배정 테스트

2. **성능 테스트**:
   - [ ] 1000명 직원 데이터 로드 시간
   - [ ] 필터링 응답 시간
   - [ ] 검색 응답 시간

3. **크로스 브라우저 테스트**:
   - [ ] Chrome
   - [ ] Firefox
   - [ ] Safari
   - [ ] 모바일 브라우저

4. **접근성 테스트**:
   - [ ] 키보드 네비게이션
   - [ ] 스크린 리더 호환
   - [ ] 색상 대비 확인

**검증**:
- [ ] 모든 시나리오 통과
- [ ] 성능 기준 충족
- [ ] 접근성 AA 등급 이상

---

#### Day 9: 배포 & 문서화
**작업 항목**:
1. **프로덕션 배포**:
   ```bash
   # 1. 백엔드 마이그레이션
   ssh root@139.150.11.99
   cd /root/uvis
   git pull origin main
   cd backend
   docker-compose exec backend alembic upgrade head
   
   # 2. 프론트엔드 빌드
   docker-compose down frontend
   docker-compose up -d --build frontend
   
   # 3. 서비스 확인
   docker-compose ps
   docker-compose logs -f frontend backend
   ```

2. **사용자 가이드 작성**:
   - 인사 관리 페이지 사용법
   - 운전자 풀 연동 방법
   - 필터 사용법
   - 자주 묻는 질문 (FAQ)

3. **배포 체크리스트**:
   - [ ] 데이터베이스 백업
   - [ ] 마이그레이션 실행
   - [ ] 프론트엔드 빌드
   - [ ] 서비스 재시작
   - [ ] 기능 테스트
   - [ ] 로그 모니터링

**검증**:
- [ ] 프로덕션 정상 작동
- [ ] 사용자 가이드 검토
- [ ] 팀 교육 완료

---

## 🔧 기술 스택

### 백엔드
- **프레임워크**: FastAPI
- **ORM**: SQLAlchemy
- **마이그레이션**: Alembic
- **인증**: JWT
- **데이터베이스**: PostgreSQL

### 프론트엔드
- **프레임워크**: React + TypeScript
- **상태 관리**: React Hooks
- **UI 라이브러리**: shadcn/ui
- **폼 관리**: react-hook-form
- **드래그앤드롭**: react-dnd
- **API 클라이언트**: axios

### 인프라
- **컨테이너**: Docker + Docker Compose
- **웹서버**: Nginx
- **배포 서버**: 139.150.11.99

---

## 📊 주요 메트릭

### 성능 목표
- API 응답 시간: < 200ms
- 페이지 로드 시간: < 2초
- 1000명 직원 필터링: < 300ms

### 코드 품질
- 테스트 커버리지: > 80%
- ESLint 오류: 0
- TypeScript 오류: 0

### 사용자 경험
- 모바일 반응형: 100%
- 접근성: AA 등급 이상
- 브라우저 호환: Chrome, Firefox, Safari

---

## 🚀 Quick Start (개발자용)

### 1. 저장소 클론
```bash
git clone https://github.com/rpaakdi1-spec/3-.git
cd 3-
```

### 2. 백엔드 실행
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

### 4. 접속
- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## 📞 문의 및 지원

### 개발팀
- **프로젝트 관리자**: GenSpark AI Assistant
- **리포지토리**: https://github.com/rpaakdi1-spec/3-
- **이슈 트래킹**: GitHub Issues

### 관련 문서
- `HR_SYSTEM_DESIGN.md` - 전체 시스템 설계
- `FORKLIFT_ABILITY_DESIGN.md` - 지게차 운전능력 상세 설계
- `FORKLIFT_ABILITY_UPDATE_SUMMARY.md` - 업데이트 요약
- `VEHICLE_DRIVER_ASSIGNMENT_FIX.md` - 차량-운전자 배정 시스템

---

**마지막 업데이트**: 2026-02-27  
**커밋**: 0df5a19  
**상태**: 설계 완료, 구현 준비 완료 ✅
