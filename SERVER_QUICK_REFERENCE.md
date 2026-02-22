# 🎯 UVIS 서버 관리자 빠른 참조 가이드

## 📥 서버에서 최신 코드 배포하기

### 방법 1: 자동 배포 스크립트 (권장)
```bash
cd /root/uvis
git pull origin main
chmod +x deploy.sh
./deploy.sh
```

### 방법 2: 수동 배포 (단계별)
```bash
# 1. 코드 업데이트
cd /root/uvis
git pull origin main

# 2. 백엔드 파일 복사
docker cp /root/uvis/backend/app/api/v1/endpoints/dispatch_rules.py \
    uvis-backend:/app/app/api/v1/endpoints/

# 3. 백엔드 재시작
docker-compose restart backend
sleep 30

# 4. 시스템 진단
/root/uvis/system_diagnosis.sh
```

---

## 🔍 시스템 상태 확인

### 컨테이너 상태
```bash
docker ps | grep uvis
# 기대 결과: 4개 컨테이너 모두 "Up" 상태
```

### 백엔드 로그
```bash
docker logs uvis-backend --tail 50
# 에러 메시지 확인
```

### API 헬스 체크
```bash
curl -s http://localhost:8000/api/v1/health | jq
```

### 시스템 진단 (전체 테스트)
```bash
/root/uvis/system_diagnosis.sh
# 기대 결과: 7/7 테스트 통과 (100%)
```

---

## 💾 데이터베이스 백업

### 수동 백업 실행
```bash
/root/uvis/backup_database.sh
```

### 백업 파일 확인
```bash
ls -lht /root/uvis/backups/ | head -5
```

### 백업 로그 확인
```bash
tail -f /var/log/db_backup.log
```

### Cron 작업 확인
```bash
crontab -l | grep backup
# 기대 결과: 0 2 * * * /root/uvis/backup_database.sh ...
```

---

## 🚨 충돌 감지 API

### JWT 토큰 획득 + 충돌 감지
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" | jq -r '.access_token')

curl -s -X GET "http://localhost:8000/api/v1/dispatch-rules/conflicts" \
    -H "Authorization: Bearer $TOKEN" | jq
```

### 예상 출력
```json
{
  "total_conflicts": 3,
  "by_severity": {
    "high": 0,
    "medium": 3,
    "low": 0
  },
  "conflicts": [
    {
      "rule1_id": 6,
      "rule2_id": 4,
      "severity": "medium",
      "recommendation": "우선순위를 다르게 설정하거나 조건을 명확히 구분하세요."
    }
  ]
}
```

---

## 📊 성능 모니터링

### 규칙 성능 대시보드
```bash
/root/uvis/monitor_rule_performance.sh
```

### 출력 예시
```
🔍 UVIS 배차 규칙 성능 모니터링
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 전체 규칙: 17개
✅ 활성 규칙: 8개

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 규칙별 성능 지표
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID | 규칙명 | 우선순위 | 실행횟수 | 평균시간 | 성공률
───┼────────┼──────────┼──────────┼──────────┼────────
1  | 냉장 운송 전용 차량 배정 | 90 | 245 | 0.12s | 98.4%
```

---

## 🤖 ML 자동 최적화

### 수동 실행
```bash
/root/uvis/ml_auto_optimize.sh
```

### Cron 작업 확인
```bash
crontab -l | grep ml_auto
# 기대 결과: 0 9 * * 1 /root/uvis/ml_auto_optimize.sh ...
```

### 로그 확인
```bash
tail -f /var/log/ml_auto_optimize.log
```

---

## 🐛 문제 해결

### 문제 #1: 백엔드가 시작되지 않음
```bash
# 로그 확인
docker logs uvis-backend --tail 100

# 환경 변수 확인
docker exec uvis-backend env | grep -E "(DATABASE|SECRET|API)"

# 재시작
docker-compose restart backend
```

### 문제 #2: 데이터베이스 연결 실패
```bash
# DB 컨테이너 상태 확인
docker ps | grep db

# DB 로그 확인
docker logs uvis-db --tail 50

# DB 접속 테스트
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT version();"
```

### 문제 #3: 백업 실패
```bash
# DB 사용자 확인
docker exec uvis-db env | grep POSTGRES

# 백업 스크립트 디버깅
bash -x /root/uvis/backup_database.sh
```

### 문제 #4: API 404 에러
```bash
# 엔드포인트 순서 확인
docker exec uvis-backend grep -n "@router.get" \
    /app/app/api/v1/endpoints/dispatch_rules.py | head -10

# 기대 결과:
# 124: @router.get("/", ...)
# 150: @router.get("/conflicts")  ← /conflicts가 /{rule_id} 앞에 있어야 함
# 227: @router.get("/{rule_id}", ...)
```

---

## 🌐 웹 인터페이스 접속

| 페이지 | URL | 기능 |
|--------|-----|------|
| 규칙 관리 | http://139.150.11.99/dispatch-rules | 규칙 CRUD, AI 생성 |
| 대시보드 | http://139.150.11.99/dashboard | 실시간 통계 |
| API 문서 | http://139.150.11.99:8000/docs | Swagger UI |
| Redoc | http://139.150.11.99:8000/redoc | ReDoc UI |

---

## 📝 주요 파일 위치

### 서버 스크립트
- `/root/uvis/deploy.sh` - 자동 배포 스크립트
- `/root/uvis/backup_database.sh` - DB 백업 스크립트
- `/root/uvis/system_diagnosis.sh` - 시스템 진단 스크립트
- `/root/uvis/monitor_rule_performance.sh` - 성능 모니터링 스크립트
- `/root/uvis/ml_auto_optimize.sh` - ML 최적화 스크립트

### 로그 파일
- `/var/log/db_backup.log` - 백업 로그
- `/var/log/ml_auto_optimize.log` - ML 최적화 로그
- `docker logs uvis-backend` - 백엔드 애플리케이션 로그
- `docker logs uvis-db` - 데이터베이스 로그

### 백업 디렉토리
- `/root/uvis/backups/` - 데이터베이스 백업 파일 (.sql.gz)

### 설정 파일
- `/root/uvis/.env` - 환경 변수
- `/root/uvis/docker-compose.yml` - Docker 구성

---

## ⚡ 빠른 명령어 모음

### 전체 재시작
```bash
cd /root/uvis
docker-compose restart
```

### 특정 컨테이너 재시작
```bash
docker-compose restart backend   # 백엔드만
docker-compose restart frontend  # 프론트엔드만
docker-compose restart db        # DB만
```

### 로그 실시간 모니터링
```bash
docker logs -f uvis-backend      # 백엔드
docker logs -f uvis-frontend     # 프론트엔드
docker logs -f uvis-db           # DB
```

### 컨테이너 내부 접속
```bash
docker exec -it uvis-backend bash    # 백엔드
docker exec -it uvis-frontend sh     # 프론트엔드
docker exec -it uvis-db psql -U uvis_user -d uvis_db  # DB
```

### 디스크 사용량 확인
```bash
du -sh /root/uvis/backups/       # 백업 디렉토리
du -sh /root/uvis/               # 전체 프로젝트
docker system df                 # Docker 디스크 사용량
```

---

## 🎯 일일 체크리스트

### 매일 확인 항목
- [ ] 컨테이너 상태: `docker ps | grep uvis` (4개 모두 Up)
- [ ] 백업 로그: `tail /var/log/db_backup.log` (성공 메시지 확인)
- [ ] 백엔드 로그: `docker logs uvis-backend --tail 20 | grep -i error` (에러 없음)
- [ ] 디스크 공간: `df -h /root` (여유 공간 확인)

### 매주 확인 항목 (월요일)
- [ ] ML 최적화 로그: `tail /var/log/ml_auto_optimize.log` (성공 확인)
- [ ] 성능 모니터링: `/root/uvis/monitor_rule_performance.sh` (8개 규칙 정상)
- [ ] 백업 파일 수: `ls /root/uvis/backups/*.gz | wc -l` (7-8개 정도)
- [ ] 충돌 감지: (위 명령 실행) 새로운 충돌 확인

### 매월 확인 항목 (1일)
- [ ] 시스템 진단: `/root/uvis/system_diagnosis.sh` (100% 통과)
- [ ] 백업 복구 테스트: 최근 백업으로 테스트 DB 복구 테스트
- [ ] Git 커밋 로그: `cd /root/uvis && git log --oneline --since="1 month ago"`
- [ ] 디스크 정리: 30일 이상 백업 파일 자동 삭제 확인

---

## 📞 긴급 연락처

### GitHub Repository
- **URL**: https://github.com/rpaakdi1-spec/3-
- **Branch**: main
- **Latest Commit**: a2e2a9d

### 문서
- **DEPLOYMENT_SUMMARY.md** - 배포 가이드 (영문)
- **FINAL_STATUS_REPORT_KO.md** - 프로젝트 보고서 (한글)
- **README.md** - 프로젝트 개요

---

## 🔐 중요 인증 정보

### 데이터베이스
- **Host**: localhost (컨테이너: uvis-db)
- **Port**: 5432
- **Database**: uvis_db
- **User**: uvis_user
- **Password**: uvis_secure_password_2024

### 기본 관리자 계정
- **Username**: admin
- **Password**: admin123

### API 키
- **OpenAI**: .env 파일에서 확인
- **GEMINI**: .env 파일에서 확인 (선택 사항)
- **Naver Map**: CLIENT_ID=oimsa0yj4k

⚠️ **보안 주의**: 이 정보는 절대 공개 저장소에 커밋하지 마세요!

---

**버전**: 1.0  
**최종 업데이트**: 2026-02-22  
**작성자**: GenSpark AI Developer
