# 🚀 배포 실행 - 즉시 실행 가이드

## ⚡ 빠른 시작 (3가지 방법)

---

## 방법 1️⃣: 서버에서 직접 실행 ⭐ 권장

가장 안정적인 방법입니다.

### 단계

```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 프로젝트 디렉토리로 이동
cd /root/uvis

# 3. 최신 코드 가져오기
git pull origin main

# 4. 배포 스크립트 실행
bash deploy_production.sh
```

**소요 시간**: 15-20분

---

## 방법 2️⃣: 원격 배포 스크립트 사용

로컬에서 원격 서버에 배포합니다.

### 단계

```bash
# 로컬 터미널에서 실행
cd /home/user/webapp
bash remote_deploy.sh
```

**필요 사항**: 
- SSH 접근 권한 (비밀번호 또는 SSH 키)
- 서버 비밀번호 입력 필요할 수 있음

**소요 시간**: 15-20분

---

## 방법 3️⃣: 한 줄 명령어 (고급 사용자)

SSH로 원격 실행:

```bash
ssh root@139.150.11.99 'cd /root/uvis && git pull origin main && bash deploy_production.sh'
```

**주의**: 
- 비밀번호를 여러 번 입력해야 할 수 있음
- 실행 과정을 실시간으로 보려면 방법 1 권장

---

## 🔍 배포 중 확인사항

배포 스크립트가 실행되면 다음을 자동으로 수행합니다:

### 1. 사전 확인 (1분)
- ✅ Docker 설치 확인
- ✅ Docker Compose 확인
- ✅ Git 확인
- ✅ 프로젝트 디렉토리 확인

### 2. 백업 (1분)
- ✅ 현재 커밋 정보 저장
- ✅ .env 파일 백업
- ✅ 백업 위치: `/root/uvis_backups/`

### 3. 코드 업데이트 (1분)
- ✅ Git fetch
- ✅ Git pull
- ✅ 커밋 확인

### 4. 서비스 중지 (30초)
- ✅ 기존 컨테이너 중지
- ✅ 리소스 정리

### 5. 이미지 빌드 (10-15분) ⏱️ 가장 오래 걸림
- 🔨 프론트엔드 빌드 (캐시 없이)
- 🔨 백엔드 빌드

### 6. 서비스 시작 (1분)
- ✅ 모든 컨테이너 시작
- ✅ 네트워크 설정

### 7. Health Check (30초)
- ✅ Backend API 확인
- ✅ Frontend 확인
- ✅ Database 연결 확인

### 8. 결과 요약 (즉시)
- 📊 서비스 상태 출력
- 📋 접속 URL 안내
- 📝 다음 단계 안내

---

## 📺 실행 화면 예시

배포 스크립트를 실행하면 다음과 같이 표시됩니다:

```
🚀 UVIS 프로덕션 배포 시작
==============================================
배포 시작 시간: 2026-01-29 14:30:00
대상 서버: 139.150.11.99
프로젝트 경로: /root/uvis

[INFO] 사전 확인 단계...
[SUCCESS] ✓ Docker 확인 완료: Docker version 24.0.7
[SUCCESS] ✓ Docker Compose 확인 완료: Docker Compose version v2.23.0
[SUCCESS] ✓ Git 확인 완료: git version 2.34.1

[INFO] 현재 상태 백업 중...
[SUCCESS] 현재 커밋 정보 백업: /root/uvis_backups/backup_20260129_143000.commit

[INFO] Git 저장소 업데이트 중...
[INFO] 현재 브랜치: main
[INFO] 원격 저장소에서 최신 코드 가져오는 중...
[SUCCESS] 현재 커밋: 43164c3

[INFO] 서비스 중지 중...
[SUCCESS] 서비스 중지 완료

[INFO] 프론트엔드 이미지 빌드 중 (캐시 없이)...
Building frontend
[+] Building 456.2s (15/15) FINISHED
[SUCCESS] 프론트엔드 이미지 빌드 완료

[INFO] 백엔드 이미지 빌드 중...
Building backend
[+] Building 123.4s (12/12) FINISHED
[SUCCESS] 백엔드 이미지 빌드 완료

[INFO] 서비스 시작 중...
Creating network "uvis_default" (if not exists)
Creating uvis-db ... done
Creating uvis-redis ... done
Creating uvis-backend ... done
Creating uvis-frontend ... done
Creating uvis-nginx ... done
[SUCCESS] 서비스 시작 완료

[INFO] 서비스 안정화 대기 중...

[INFO] 서비스 상태 확인 중...

NAME            STATUS          PORTS
uvis-frontend   Up 15 seconds   0.0.0.0:3000->3000/tcp
uvis-backend    Up (healthy)    0.0.0.0:8000->8000/tcp
uvis-db         Up (healthy)    0.0.0.0:5432->5432/tcp
uvis-redis      Up (healthy)    0.0.0.0:6379->6379/tcp
uvis-nginx      Up 15 seconds   0.0.0.0:80->80/tcp

[SUCCESS] ✓ frontend: Running
[SUCCESS] ✓ backend: Running
[SUCCESS] ✓ db: Running
[SUCCESS] ✓ redis: Running
[SUCCESS] ✓ nginx: Running

[INFO] Health check 수행 중...
[SUCCESS] ✓ Backend health check passed
[SUCCESS] ✓ Frontend health check passed

🎉 배포 완료
==============================================
배포 완료 시간: 2026-01-29 14:47:30
배포된 커밋: 43164c3
백업 위치: /root/uvis_backups/backup_20260129_143000

[SUCCESS] ✅ 모든 서비스가 정상 작동 중입니다

📊 접속 정보
==============================================
Frontend:  http://139.150.11.99
Backend:   http://139.150.11.99:8000
API Docs:  http://139.150.11.99:8000/docs

📝 다음 단계
==============================================
1. 브라우저에서 http://139.150.11.99/orders 접속
2. 신규 주문 등록 테스트
3. 온도대 선택 시 자동 입력 확인:
   - 냉동: -30°C ~ -18°C
   - 냉장: 0°C ~ 6°C
   - 상온: -30°C ~ 60°C
4. 주문 등록 완료 테스트
5. 팀에 배포 완료 알림
```

---

## ✅ 배포 성공 확인

배포가 완료되면 다음을 확인하세요:

### 1. 서비스 접근성
```bash
# 브라우저에서 확인
http://139.150.11.99                 ✓ Frontend 로딩
http://139.150.11.99:8000            ✓ Backend API
http://139.150.11.99:8000/docs       ✓ API 문서

# 또는 명령어로 확인
curl http://139.150.11.99
curl http://139.150.11.99:8000/health
```

### 2. 컨테이너 상태
```bash
# 서버에서 확인
ssh root@139.150.11.99
cd /root/uvis
docker-compose -f docker-compose.prod.yml ps

# 모든 컨테이너가 "Up" 또는 "Up (healthy)" 상태여야 함
```

### 3. 로그 확인
```bash
# 에러가 없는지 확인
docker-compose -f docker-compose.prod.yml logs | grep -i error

# 최근 로그 확인
docker-compose -f docker-compose.prod.yml logs --tail=50
```

---

## 🧪 기능 테스트

배포 후 즉시 온도 자동입력 기능을 테스트하세요!

### 테스트 순서

1. **브라우저 접속**
   ```
   http://139.150.11.99/orders
   ```

2. **로그인**
   - 사용자: admin
   - 비밀번호: (기존 비밀번호)

3. **신규 주문 등록**
   - "+ 신규 등록" 버튼 클릭

4. **온도대 테스트**
   - 드롭다운에서 "냉동" 선택
   - 최저 온도: -30 자동 입력 확인 ✅
   - 최고 온도: -18 자동 입력 확인 ✅
   
   - "냉장" 선택
   - 최저 온도: 0 자동 입력 확인 ✅
   - 최고 온도: 6 자동 입력 확인 ✅
   
   - "상온" 선택
   - 최저 온도: -30 자동 입력 확인 ✅
   - 최고 온도: 60 자동 입력 확인 ✅

5. **수동 수정 테스트**
   - 자동 입력된 값을 수동으로 변경 가능한지 확인

6. **주문 등록**
   - 필수 필드 입력 후 등록
   - 성공 메시지 확인

---

## 🚨 문제 발생 시

### 증상 1: 배포 스크립트가 실패함

**해결**:
```bash
# 로그 확인
cd /root/uvis
docker-compose -f docker-compose.prod.yml logs

# 수동으로 재시작
docker-compose -f docker-compose.prod.yml restart
```

### 증상 2: Frontend가 로딩되지 않음

**해결**:
```bash
# Frontend 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 증상 3: 온도 자동입력이 작동하지 않음

**해결**:
```
1. 브라우저 캐시 삭제 (Ctrl+Shift+R 또는 Cmd+Shift+R)
2. 시크릿/프라이빗 모드에서 테스트
3. 브라우저 콘솔(F12) 확인
```

### 증상 4: 422 에러 발생

**해결**:
```bash
# Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 브라우저 캐시 삭제
```

### 긴급 롤백

심각한 문제 발생 시:
```bash
ssh root@139.150.11.99
cd /root/uvis

# 이전 커밋으로 롤백
git log --oneline -5
git checkout <이전_커밋_해시>

# 재배포
bash deploy_production.sh
```

---

## 📞 지원

### 문의
- **이슈 보고**: https://github.com/rpaakdi1-spec/3-/issues
- **배포 문서**: https://github.com/rpaakdi1-spec/3-/blob/main/READY_FOR_DEPLOYMENT.md

### 유용한 링크
- [배포 가이드](https://github.com/rpaakdi1-spec/3-/blob/main/DEPLOYMENT_INSTRUCTIONS.md)
- [테스트 체크리스트](https://github.com/rpaakdi1-spec/3-/blob/main/DEPLOYMENT_TEST_CHECKLIST.md)
- [액션 아이템](https://github.com/rpaakdi1-spec/3-/blob/main/ACTION_ITEMS.md)

---

## 🎊 준비 완료!

**이제 위의 방법 중 하나를 선택하여 배포를 시작하세요!**

방법 1 (서버 직접 실행) 권장:
```bash
ssh root@139.150.11.99
cd /root/uvis
git pull origin main
bash deploy_production.sh
```

**배포 성공을 기원합니다!** 🚀

---

**문서 버전**: 1.0  
**작성일**: 2026-01-29  
**작성자**: GenSpark AI Developer
