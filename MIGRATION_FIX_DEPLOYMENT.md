# 마이그레이션 헤드 충돌 해결 완료

## 문제
`down_revision = None`으로 설정되어 있어서 두 개의 독립적인 마이그레이션 헤드가 생성되었습니다.

## 해결
`pending_employees` 마이그레이션의 `down_revision`을 `e001_employee_model`로 업데이트했습니다.

## 서버 배포 명령어

```bash
cd /root/uvis

# 최신 코드 가져오기
git pull origin main

# 마이그레이션 실행
docker-compose run --rm backend alembic upgrade head

# 백엔드/프론트엔드 재빌드 및 시작
docker-compose up -d --build backend frontend

# 상태 확인
docker-compose ps
docker-compose logs -f backend frontend
```

## 예상 결과
- ✅ 마이그레이션이 성공적으로 실행됩니다
- ✅ `pending_employees` 테이블이 생성됩니다 (work_start_time, work_end_time, max_work_hours 없음)
- ✅ 모든 컨테이너가 정상적으로 시작됩니다

## 테이블 확인

배포 후 다음 명령어로 테이블 생성을 확인하세요:

```bash
docker-compose exec db psql -U uvis_user -d uvis_db -c "\d pending_employees"
```

예상 출력:
```
                                          Table "public.pending_employees"
          Column          |            Type             | Collation | Nullable |                    Default
--------------------------+-----------------------------+-----------+----------+-----------------------------------------------
 id                       | integer                     |           | not null | nextval('pending_employees_id_seq'::regclass)
 user_id                  | integer                     |           | not null |
 employee_code            | character varying(50)       |           | not null |
 name                     | character varying(100)      |           | not null |
 name_en                  | character varying(100)      |           |          |
 phone                    | character varying(20)       |           | not null |
 email                    | character varying(100)      |           |          |
 address                  | text                        |           |          |
 emergency_contact        | character varying(20)       |           |          |
 role                     | character varying(20)       |           | not null |
 employment_type          | character varying(20)       |           | not null |
 department               | character varying(100)      |           |          |
 position                 | character varying(100)      |           |          |
 hire_date                | date                        |           | not null |
 license_type             | character varying(20)       |           |          |
 license_number           | character varying(50)       |           |          |
 license_issue_date       | date                        |           |          |
 has_cargo_license        | boolean                     |           |          | false
 cargo_license_number     | character varying(50)       |           |          |
 cargo_license_issue_date | date                        |           |          |
 cargo_license_expiry_date| date                        |           |          |
 can_drive_forklift       | boolean                     |           |          | false
 has_forklift_certificate | boolean                     |           |          | false
 forklift_certificate_number | character varying(50)    |           |          |
 forklift_certificate_issue_date | date                 |           |          |
 forklift_certificate_expiry_date | date                |           |          |
 created_at               | timestamp with time zone    |           |          | now()
```

**주의**: work_start_time, work_end_time, max_work_hours 컬럼이 없어야 합니다!

## 커밋 정보
- Commit: a1071a7
- Message: "fix: set correct down_revision for pending_employees migration"
- Date: 2026-02-28
