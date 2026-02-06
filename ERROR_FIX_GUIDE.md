# UVIS 전체 오류 수정 가이드

## 📋 개요

대시보드가 작동하지 않거나 시스템에 문제가 있을 때 사용하는 **3가지 핵심 스크립트**입니다.

---

## 🔧 3가지 핵심 스크립트

### 1. 진단 스크립트 (빠른 확인)
```bash
cd /root/uvis
./diagnose_system.sh
```

**목적**: 현재 시스템 상태를 빠르게 진단
- Docker 컨테이너 상태
- 백엔드/프론트엔드 헬스 체크
- 데이터베이스 연결 상태
- API 엔드포인트 테스트
- 환경 설정 파일 확인
- 문제 원인 파악 및 해결 방법 제시

**실행 시간**: 약 10초

---

### 2. 빠른 수정 스크립트 (대화형 메뉴)
```bash
cd /root/uvis
./quick_fix.sh
```

**목적**: 일반적인 문제를 빠르게 수정

**메뉴 옵션**:
1. 백엔드 재시작 (가장 빠름)
2. 프론트엔드 재빌드 및 재시작
3. 데이터베이스 재시작
4. 모든 컨테이너 재시작
5. Git 저장소 최신 코드로 업데이트
6. 환경 설정 파일 수정
7. 전체 시스템 완전 재설치
8. 시스템 진단만 실행

**실행 시간**: 선택에 따라 3초 ~ 5분

---

### 3. 전체 오류 수정 스크립트 (완전 자동화)
```bash
cd /root/uvis
./fix_all_errors.sh
```

**목적**: 모든 문제를 포괄적으로 해결

**수행 작업**:
1. ✅ 시스템 상태 진단
2. ✅ Git 저장소 정리 및 최신 코드 업데이트
3. ✅ 환경 설정 파일 확인/수정
4. ✅ 데이터베이스 마이그레이션
5. ✅ 프론트엔드 완전 재빌드
6. ✅ Docker 컨테이너 캐시 없이 재빌드
7. ✅ 모든 서비스 재시작
8. ✅ 헬스 체크 및 API 테스트
9. ✅ 로그 확인 및 문제 보고
10. ✅ 다음 단계 안내

**실행 시간**: 약 5-10분

**주의**: 로컬 변경사항은 자동으로 백업됩니다.

---

## 🚨 문제 상황별 사용 가이드

### 상황 1: 대시보드가 로드되지 않음
```bash
# 1단계: 진단
./diagnose_system.sh

# 2단계: 빠른 수정 시도
./quick_fix.sh
# → 메뉴에서 1번 (백엔드 재시작) 선택

# 3단계: 여전히 문제가 있으면
./fix_all_errors.sh
```

### 상황 2: API 호출이 404 오류
```bash
# 환경 설정 문제일 가능성
./quick_fix.sh
# → 메뉴에서 6번 (환경 설정 파일 수정) 선택

# 그래도 안되면
./fix_all_errors.sh
```

### 상황 3: 프론트엔드 페이지가 비어있음
```bash
# 빌드 문제일 가능성
./quick_fix.sh
# → 메뉴에서 2번 (프론트엔드 재빌드) 선택
```

### 상황 4: 데이터베이스 연결 오류
```bash
./quick_fix.sh
# → 메뉴에서 3번 (데이터베이스 재시작) 선택
```

### 상황 5: 모든 것이 작동하지 않음
```bash
# 가장 강력한 해결책
./fix_all_errors.sh
```

---

## 📊 권장 워크플로우

### 일반적인 문제 해결 순서:

1. **진단 먼저**
   ```bash
   ./diagnose_system.sh
   ```
   - 무엇이 문제인지 파악

2. **빠른 수정 시도**
   ```bash
   ./quick_fix.sh
   ```
   - 필요한 부분만 수정 (시간 절약)

3. **전체 수정 (최종 수단)**
   ```bash
   ./fix_all_errors.sh
   ```
   - 모든 것을 처음부터 다시 설정

---

## 🎯 각 스크립트의 장단점

### diagnose_system.sh (진단)
**장점**:
- ✅ 빠름 (10초)
- ✅ 시스템 상태만 확인
- ✅ 아무것도 변경하지 않음

**단점**:
- ❌ 문제를 자동으로 수정하지 않음

**사용 시기**: 먼저 무엇이 문제인지 파악할 때

---

### quick_fix.sh (빠른 수정)
**장점**:
- ✅ 대화형 메뉴로 쉬움
- ✅ 필요한 부분만 수정
- ✅ 시간 절약

**단점**:
- ❌ 복잡한 문제는 해결 못할 수도 있음

**사용 시기**: 간단한 문제 (재시작, 재빌드 등)

---

### fix_all_errors.sh (전체 수정)
**장점**:
- ✅ 모든 문제를 포괄적으로 해결
- ✅ 완전 자동화
- ✅ 백업 자동 생성
- ✅ 헬스 체크 포함

**단점**:
- ❌ 시간이 오래 걸림 (5-10분)
- ❌ 로컬 변경사항 삭제 (백업은 생성됨)

**사용 시기**: 
- 다른 방법으로 해결되지 않을 때
- 시스템을 완전히 깨끗한 상태로 만들고 싶을 때
- 최신 코드로 완전히 업데이트하고 싶을 때

---

## 💡 실전 팁

### 팁 1: 항상 진단부터
```bash
./diagnose_system.sh
```
문제가 무엇인지 먼저 파악하면 시간을 절약할 수 있습니다.

### 팁 2: 간단한 것부터
백엔드 문제라면:
```bash
./quick_fix.sh → 1번 (백엔드 재시작)
```
많은 경우 재시작만으로 해결됩니다.

### 팁 3: 로그 확인
```bash
# 실시간 백엔드 로그
docker logs uvis-backend -f

# 실시간 프론트엔드 로그
docker logs uvis-frontend -f

# Ctrl + C로 종료
```

### 팁 4: 브라우저 캐시
프론트엔드 문제는 브라우저 캐시일 수 있습니다:
- **Ctrl + Shift + R** (강력 새로고침)
- 또는 **F12 → Network 탭 → Disable cache 체크**

---

## 🔍 헬스 체크 URL

수정 후 이 URL들로 확인:

```bash
# 프론트엔드
curl -I http://139.150.11.99/
# 응답: 200 OK

# 백엔드 헬스
curl http://139.150.11.99:8000/health
# 응답: {"status":"healthy",...}

# API 문서
curl -I http://139.150.11.99:8000/docs
# 응답: 200 OK
```

**브라우저에서**:
- http://139.150.11.99/ (메인 페이지)
- http://139.150.11.99:8000/docs (API 문서)
- http://139.150.11.99/billing/financial-dashboard (Phase 8)

---

## 📝 로그 위치 및 확인 방법

### Docker 컨테이너 로그
```bash
# 백엔드 (최근 100줄)
docker logs uvis-backend --tail 100

# 프론트엔드 (최근 100줄)
docker logs uvis-frontend --tail 100

# 데이터베이스 (최근 50줄)
docker logs uvis-db --tail 50

# 실시간 추적
docker logs uvis-backend -f

# 에러만 필터링
docker logs uvis-backend --tail 1000 | grep -i error
```

### 백업 위치
`fix_all_errors.sh` 실행 시 자동 백업:
```bash
/root/uvis_backup_YYYYMMDD_HHMMSS/
```

---

## ⚠️ 주의사항

### fix_all_errors.sh 실행 시:
1. **로컬 변경사항 삭제됨** (백업은 자동 생성)
2. **Git이 최신 코드로 완전히 리셋됨**
3. **모든 Docker 컨테이너가 재빌드됨**
4. **시간이 오래 걸림** (5-10분)

### 백업 확인:
```bash
ls -la /root/uvis_backup_*
```

### 백업 복원 (필요시):
```bash
cp -r /root/uvis_backup_YYYYMMDD_HHMMSS/* /root/uvis/
```

---

## 🆘 긴급 상황

### 모든 스크립트가 작동하지 않으면:

1. **수동으로 컨테이너 재시작**
   ```bash
   cd /root/uvis
   docker-compose down
   docker-compose up -d
   ```

2. **Docker 완전 정리**
   ```bash
   cd /root/uvis
   docker-compose down -v
   docker system prune -a -f
   docker-compose up -d
   ```
   ⚠️ 주의: 모든 데이터가 삭제됩니다!

3. **GitHub에서 다시 클론**
   ```bash
   cd /root
   mv uvis uvis_old_$(date +%Y%m%d)
   git clone https://github.com/rpaakdi1-spec/3-.git uvis
   cd uvis
   git checkout genspark_ai_developer
   # 그 다음 fix_all_errors.sh 실행
   ```

---

## 📞 지원

### 스크립트 파일들:
- `diagnose_system.sh` - 시스템 진단
- `quick_fix.sh` - 빠른 수정 (대화형)
- `fix_all_errors.sh` - 전체 오류 수정

### 문서:
- `PHASE_8_COMPLETE_PROJECT_SUMMARY.md` - 전체 프로젝트 요약
- `PHASE_8_API_PATH_FIX.md` - API 경로 수정 문서
- `PHASE_8_PRODUCTION_DEPLOYMENT.md` - 배포 가이드

### 도움이 필요하면:
1. `diagnose_system.sh` 실행 결과 공유
2. `docker logs uvis-backend --tail 100` 로그 공유
3. 브라우저 F12 Console 오류 메시지 공유

---

## ✅ 체크리스트

수정 후 다음 항목을 확인하세요:

- [ ] 진단 스크립트 실행: `./diagnose_system.sh`
- [ ] 백엔드 헬스 체크: 200 OK
- [ ] 프론트엔드 헬스 체크: 200 OK
- [ ] 브라우저에서 메인 페이지 로드: http://139.150.11.99/
- [ ] 로그인 가능: admin / admin123
- [ ] 대시보드 페이지 표시
- [ ] Phase 8 페이지 접근 가능
- [ ] 브라우저 Console에 오류 없음
- [ ] API 호출이 200 OK 반환

모두 체크되면 시스템이 정상입니다! ✅

---

**작성일**: 2026-02-06  
**버전**: 1.0  
**업데이트**: Phase 8 완료 후
