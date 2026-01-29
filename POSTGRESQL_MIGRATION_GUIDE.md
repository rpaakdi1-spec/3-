# 📊 PostgreSQL 마이그레이션 가이드

**Cold Chain Dispatch System - PostgreSQL Migration Guide**

---

## 📋 목차

1. [개요](#개요)
2. [마이그레이션 이유](#마이그레이션-이유)
3. [PostgreSQL vs SQLite](#postgresql-vs-sqlite)
4. [사전 준비](#사전-준비)
5. [Docker로 PostgreSQL 설치](#docker로-postgresql-설치)
6. [로컬 PostgreSQL 설치](#로컬-postgresql-설치)
7. [데이터베이스 마이그레이션 실행](#데이터베이스-마이그레이션-실행)
8. [데이터 이전 (SQLite → PostgreSQL)](#데이터-이전-sqlite--postgresql)
9. [검증 및 테스트](#검증-및-테스트)
10. [문제 해결](#문제-해결)

---

## 개요

Cold Chain Dispatch System을 SQLite에서 **PostgreSQL**로 마이그레이션하는 가이드입니다.

| 항목 | 내용 |
|------|------|
| **목적** | 프로덕션 환경을 위한 엔터프라이즈급 데이터베이스로 전환 |
| **마이그레이션 도구** | Alembic (SQLAlchemy) |
| **소요 시간** | 30분 ~ 1시간 |
| **다운타임** | 필요 (데이터 이전 시) |

---

## 마이그레이션 이유

### 1. 동시성 지원
- SQLite: 단일 Write 작업만 지원
- PostgreSQL: 다중 사용자 동시 Write 지원

### 2. 성능
- PostgreSQL: 인덱스, 쿼리 최적화, 캐싱 지원
- 대용량 데이터 처리에 최적화

### 3. 트랜잭션 및 무결성
- ACID 트랜잭션 완벽 지원
- Foreign Key 제약조건 강화

### 4. 확장성
- 복제 (Replication) 지원
- 수평 확장 가능

### 5. 고급 기능
- JSON/JSONB 타입
- Full-text Search
- GIS (PostGIS) 확장

---

## PostgreSQL vs SQLite

| 특성 | SQLite | PostgreSQL |
|------|--------|------------|
| **사용 사례** | 개발, 테스트, 소규모 앱 | 프로덕션, 엔터프라이즈 |
| **동시성** | 제한적 | 우수 |
| **성능** | 소규모 데이터: 빠름 | 대규모 데이터: 빠름 |
| **확장성** | 제한적 | 우수 |
| **관리** | 간단 (파일 기반) | 복잡 (서버 관리) |
| **백업** | 파일 복사 | pg_dump, WAL |
| **비용** | 무료 | 무료 (오픈소스) |

---

## 사전 준비

### 1. 백업

**SQLite 데이터베이스 백업**:
```bash
cp backend/dispatch.db backend/dispatch_backup_$(date +%Y%m%d).db
```

### 2. 의존성 설치

**psycopg2 (PostgreSQL 드라이버)**:
```bash
cd backend
pip install psycopg2-binary==2.9.9
```

또는 `requirements.txt`에 추가:
```txt
psycopg2-binary==2.9.9
```

### 3. 환경 변수 설정

`.env` 파일 수정:
```env
# PostgreSQL (Production)
DB_USER=coldchain
DB_PASSWORD=coldchain_password
DB_NAME=coldchain_db
DATABASE_URL=postgresql://coldchain:coldchain_password@localhost:5432/coldchain_db

# SQLite (Development - 선택 사항)
# DATABASE_URL=sqlite:///./backend/dispatch.db
```

---

## Docker로 PostgreSQL 설치

### 1. Docker Compose 사용

프로젝트 루트의 `docker-compose.yml`에 PostgreSQL이 이미 설정되어 있습니다:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: cold-chain-db
    environment:
      POSTGRES_USER: coldchain
      POSTGRES_PASSWORD: coldchain_password
      POSTGRES_DB: coldchain_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### 2. PostgreSQL 컨테이너 시작

```bash
# PostgreSQL만 시작
docker-compose up -d postgres

# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f postgres
```

### 3. PostgreSQL 접속 확인

```bash
# Docker 컨테이너 내부로 접속
docker exec -it cold-chain-db psql -U coldchain -d coldchain_db

# SQL 명령어 실행
\dt  # 테이블 목록
\q   # 종료
```

---

## 로컬 PostgreSQL 설치

### macOS (Homebrew)

```bash
# PostgreSQL 설치
brew install postgresql@15

# 서비스 시작
brew services start postgresql@15

# 데이터베이스 생성
createdb coldchain_db

# 사용자 생성
psql postgres
CREATE USER coldchain WITH PASSWORD 'coldchain_password';
GRANT ALL PRIVILEGES ON DATABASE coldchain_db TO coldchain;
\q
```

### Ubuntu/Debian

```bash
# PostgreSQL 설치
sudo apt update
sudo apt install postgresql postgresql-contrib

# 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 사용자 및 데이터베이스 생성
sudo -u postgres psql
CREATE USER coldchain WITH PASSWORD 'coldchain_password';
CREATE DATABASE coldchain_db OWNER coldchain;
GRANT ALL PRIVILEGES ON DATABASE coldchain_db TO coldchain;
\q
```

### Windows

1. [PostgreSQL 공식 사이트](https://www.postgresql.org/download/windows/)에서 설치 파일 다운로드
2. 설치 마법사 실행
3. pgAdmin 4를 통해 데이터베이스 생성:
   - Database: `coldchain_db`
   - Owner: `coldchain`

---

## 데이터베이스 마이그레이션 실행

### 1. Alembic 초기화 (이미 완료됨)

```bash
cd backend
alembic init alembic
```

### 2. 초기 마이그레이션 생성 (이미 완료됨)

```bash
alembic revision --autogenerate -m "Initial migration - create all tables"
```

### 3. 마이그레이션 실행

```bash
# 환경 변수 확인
echo $DATABASE_URL

# PostgreSQL로 마이그레이션 실행
alembic upgrade head
```

### 4. 마이그레이션 버전 확인

```bash
# 현재 버전 확인
alembic current

# 마이그레이션 히스토리 확인
alembic history
```

---

## 데이터 이전 (SQLite → PostgreSQL)

### 방법 1: Python 스크립트 사용

`backend/migrate_data.py` 생성:

```python
#!/usr/bin/env python3
"""
SQLite에서 PostgreSQL로 데이터 마이그레이션
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Client, Vehicle, Order, Dispatch, User, Driver
from app.core.config import settings

# SQLite 연결
sqlite_url = "sqlite:///./dispatch_backup.db"
sqlite_engine = create_engine(sqlite_url)
SQLiteSession = sessionmaker(bind=sqlite_engine)

# PostgreSQL 연결
pg_engine = create_engine(settings.DATABASE_URL)
PostgresSession = sessionmaker(bind=pg_engine)

def migrate_table(model, batch_size=100):
    """테이블 데이터 마이그레이션"""
    sqlite_session = SQLiteSession()
    pg_session = PostgresSession()
    
    try:
        # SQLite에서 데이터 가져오기
        records = sqlite_session.query(model).all()
        total = len(records)
        
        print(f"Migrating {total} {model.__tablename__} records...")
        
        # 배치 처리
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]
            
            # PostgreSQL에 삽입
            for record in batch:
                # ID 제거 (auto-increment)
                record_dict = {c.name: getattr(record, c.name) 
                             for c in record.__table__.columns
                             if c.name != 'id'}
                
                new_record = model(**record_dict)
                pg_session.add(new_record)
            
            pg_session.commit()
            print(f"  Migrated {min(i + batch_size, total)}/{total}")
        
        print(f"✅ {model.__tablename__} migration completed!")
        
    except Exception as e:
        print(f"❌ Error migrating {model.__tablename__}: {e}")
        pg_session.rollback()
    finally:
        sqlite_session.close()
        pg_session.close()

def main():
    """메인 마이그레이션 함수"""
    print("🚀 Starting data migration from SQLite to PostgreSQL...")
    
    # 순서 중요 (Foreign Key 제약조건)
    models = [
        User,
        Client,
        Driver,
        Vehicle,
        Order,
        Dispatch,
        # 필요에 따라 추가
    ]
    
    for model in models:
        migrate_table(model)
    
    print("\n✅ Data migration completed successfully!")

if __name__ == "__main__":
    main()
```

실행:
```bash
cd backend
python migrate_data.py
```

### 방법 2: pgloader 사용 (추천)

```bash
# pgloader 설치
sudo apt install pgloader  # Ubuntu/Debian
brew install pgloader      # macOS

# 마이그레이션 설정 파일 생성
cat > migrate.load << 'EOF'
LOAD DATABASE
    FROM sqlite://./backend/dispatch.db
    INTO postgresql://coldchain:coldchain_password@localhost/coldchain_db

WITH include drop, create tables, create indexes, reset sequences

SET work_mem to '16MB', maintenance_work_mem to '512 MB';
EOF

# 실행
pgloader migrate.load
```

### 방법 3: 수동 Export/Import

```bash
# SQLite에서 데이터 Export (CSV)
sqlite3 backend/dispatch.db <<EOF
.headers on
.mode csv
.output clients.csv
SELECT * FROM clients;
.quit
EOF

# PostgreSQL로 Import
psql -U coldchain -d coldchain_db -c "\COPY clients FROM 'clients.csv' CSV HEADER"
```

---

## 검증 및 테스트

### 1. 데이터베이스 연결 확인

```bash
psql -U coldchain -d coldchain_db -c "SELECT version();"
```

### 2. 테이블 확인

```sql
\dt  -- 모든 테이블 목록
\d clients  -- clients 테이블 구조 확인
```

### 3. 데이터 개수 확인

```sql
SELECT COUNT(*) FROM clients;
SELECT COUNT(*) FROM vehicles;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM dispatches;
```

### 4. API 테스트

```bash
# 백엔드 서버 시작
cd backend
uvicorn main:app --reload

# API 테스트
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/clients
```

### 5. Python 스크립트로 검증

```python
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM clients"))
    print(f"Total clients: {result.scalar()}")
```

---

## 문제 해결

### 1. 연결 실패

**에러**: `psycopg2.OperationalError: could not connect to server`

**해결**:
```bash
# PostgreSQL 상태 확인
docker-compose ps postgres  # Docker
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# 포트 확인
lsof -i :5432
```

### 2. 인증 실패

**에러**: `psycopg2.OperationalError: FATAL: password authentication failed`

**해결**:
```bash
# .env 파일 확인
cat .env | grep DATABASE_URL

# PostgreSQL 사용자 비밀번호 재설정
psql -U postgres -c "ALTER USER coldchain WITH PASSWORD 'coldchain_password';"
```

### 3. 권한 문제

**에러**: `permission denied for schema public`

**해결**:
```sql
GRANT ALL PRIVILEGES ON DATABASE coldchain_db TO coldchain;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO coldchain;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO coldchain;
```

### 4. Foreign Key 제약조건 위반

**에러**: `violates foreign key constraint`

**해결**:
```python
# 마이그레이션 순서 변경 (부모 테이블 먼저)
models = [
    User,      # 먼저
    Client,    # 먼저
    Vehicle,   # 먼저
    Order,     # 나중
    Dispatch,  # 나중
]
```

### 5. 데이터 타입 불일치

**에러**: `invalid input syntax for type timestamp`

**해결**:
```python
# 날짜 형식 변환
from datetime import datetime
if isinstance(value, str):
    value = datetime.fromisoformat(value)
```

---

## 성능 최적화

### 1. 인덱스 생성

```sql
CREATE INDEX idx_clients_code ON clients(code);
CREATE INDEX idx_vehicles_code ON vehicles(code);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_dispatches_dispatch_number ON dispatches(dispatch_number);
```

### 2. Connection Pool 설정

`backend/app/core/database.py`:
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,           # 연결 풀 크기
    max_overflow=10,        # 최대 오버플로우
    pool_pre_ping=True,     # 연결 상태 확인
    pool_recycle=3600,      # 1시간마다 연결 재활용
)
```

### 3. 쿼리 최적화

```python
# Eager Loading (N+1 문제 해결)
from sqlalchemy.orm import joinedload

dispatches = db.query(Dispatch).options(
    joinedload(Dispatch.vehicle),
    joinedload(Dispatch.routes)
).all()
```

---

## 백업 및 복구

### 백업

```bash
# 전체 데이터베이스 백업
pg_dump -U coldchain -d coldchain_db > backup_$(date +%Y%m%d).sql

# 스키마만 백업
pg_dump -U coldchain -d coldchain_db --schema-only > schema.sql

# 데이터만 백업
pg_dump -U coldchain -d coldchain_db --data-only > data.sql
```

### 복구

```bash
# 복구
psql -U coldchain -d coldchain_db < backup_20260127.sql
```

---

## 모니터링

### 1. 연결 상태 확인

```sql
SELECT * FROM pg_stat_activity WHERE datname = 'coldchain_db';
```

### 2. 테이블 크기 확인

```sql
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;
```

### 3. 느린 쿼리 확인

```sql
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 참고 자료

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [Alembic 문서](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [pgloader 문서](https://pgloader.readthedocs.io/)

---

**작성일**: 2026-01-27  
**버전**: 1.0.0  
**작성자**: GenSpark AI Developer
