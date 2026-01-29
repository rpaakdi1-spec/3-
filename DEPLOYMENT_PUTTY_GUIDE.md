# 🖥️ PuTTY로 UVIS 프로덕션 배포하기

## 📋 목차
1. [PuTTY 접속](#1-putty-접속)
2. [배포 실행](#2-배포-실행)
3. [배포 모니터링](#3-배포-모니터링)
4. [테스트 실행](#4-테스트-실행)
5. [문제 해결](#5-문제-해결)

---

## 1. PuTTY 접속

### Step 1-1: PuTTY 실행

1. **PuTTY 프로그램 실행**
   - Windows 시작 메뉴에서 "PuTTY" 검색
   - 또는 바탕화면의 PuTTY 아이콘 더블클릭

### Step 1-2: 서버 정보 입력

PuTTY Configuration 창에서:

```
Host Name (or IP address): 139.150.11.99
Port: 22
Connection type: SSH
```

**화면 예시:**
```
┌─ PuTTY Configuration ─────────────────────┐
│                                            │
│ Category:                                  │
│  └─ Session                                │
│                                            │
│ Basic options for your PuTTY session      │
│                                            │
│ Host Name (or IP address)                 │
│ ┌────────────────────────────────────┐    │
│ │ 139.150.11.99                      │    │
│ └────────────────────────────────────┘    │
│                                            │
│ Port: 22      Connection type: SSH        │
│                                            │
│ [Open]  [Cancel]                          │
└────────────────────────────────────────────┘
```

### Step 1-3: 접속

1. **"Open" 버튼 클릭**

2. **보안 경고 창이 뜨면**:
   ```
   The server's host key is not cached in the registry.
   You have no guarantee that the server is the computer you think it is.
   ...
   Do you trust this host and want to continue?
   ```
   - "Accept" 또는 "Yes" 클릭

3. **로그인 정보 입력**:
   ```
   login as: root
   root@139.150.11.99's password: [비밀번호 입력]
   ```
   
   ⚠️ **주의**: 비밀번호 입력 시 화면에 아무것도 표시되지 않습니다 (정상)

4. **접속 성공 확인**:
   ```
   Welcome to Ubuntu 22.04.3 LTS
   
   Last login: Wed Jan 29 14:30:00 2026 from xxx.xxx.xxx.xxx
   root@server:~#
   ```

---

## 2. 배포 실행

### Step 2-1: 프로젝트 디렉토리로 이동

PuTTY 터미널에서 다음 명령어 입력:

```bash
cd /root/uvis
```

**입력 방법**:
- 타이핑 또는 복사/붙여넣기
- **붙여넣기**: 마우스 오른쪽 클릭 또는 Shift+Insert

**결과 확인**:
```bash
root@server:~# cd /root/uvis
root@server:/root/uvis#
```

### Step 2-2: 현재 상태 확인 (선택사항)

```bash
# 현재 커밋 확인
git log --oneline -1

# 현재 실행 중인 서비스 확인
docker-compose -f docker-compose.prod.yml ps
```

### Step 2-3: 최신 코드 가져오기

```bash
# main 브랜치로 전환
git checkout main

# 최신 코드 다운로드
git pull origin main
```

**실행 화면**:
```
root@server:/root/uvis# git pull origin main
remote: Enumerating objects: 15, done.
remote: Counting objects: 100% (15/15), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 9 (delta 6), reused 5 (delta 1), pack-reused 0
Unpacking objects: 100% (9/9), 15.23 KiB | 869.00 KiB/s, done.
From https://github.com/rpaakdi1-spec/3-
 * branch            main       -> FETCH_HEAD
   43164c3..1bb492c  main       -> origin/main
Updating 43164c3..1bb492c
Fast-forward
 DEPLOYMENT_EXECUTE.md | 341 +++++++++++++++++++++++++++++++++
 remote_deploy.sh      | 299 ++++++++++++++++++++++++++++
 2 files changed, 640 insertions(+)
 create mode 100644 DEPLOYMENT_EXECUTE.md
 create mode 100755 remote_deploy.sh
```

### Step 2-4: 배포 스크립트 확인

```bash
# 배포 스크립트가 있는지 확인
ls -lh deploy_production.sh
```

**결과**:
```
-rwxr-xr-x 1 root root 10K Jan 29 14:30 deploy_production.sh
```

### Step 2-5: 배포 스크립트 실행 ⭐

```bash
bash deploy_production.sh
```

**또는** (실행 권한이 있으면):
```bash
./deploy_production.sh
```

---

## 3. 배포 모니터링

### 배포 진행 상황

배포 스크립트가 실행되면 다음과 같은 화면이 표시됩니다:

```
==========================================
  🚀 UVIS 프로덕션 배포 시작
==========================================
배포 시작 시간: 2026-01-29 14:30:00
대상 서버: 139.150.11.99
프로젝트 경로: /root/uvis

[INFO] 사전 확인 단계...
[SUCCESS] ✓ Docker 확인 완료: Docker version 24.0.7
[SUCCESS] ✓ Docker Compose 확인 완료: Docker Compose version v2.23.0
[SUCCESS] ✓ Git 확인 완료: git version 2.34.1
[SUCCESS] 프로젝트 디렉토리 확인 완료

[INFO] 현재 상태 백업 중...
[SUCCESS] 현재 커밋 정보 백업: /root/uvis_backups/backup_20260129_143000.commit
[SUCCESS] .env 파일 백업 완료

[INFO] Git 저장소 업데이트 중...
[INFO] 현재 브랜치: main
[SUCCESS] 현재 커밋: 1bb492c

[INFO] 서비스 중지 중...
Stopping uvis-nginx    ... done
Stopping uvis-frontend ... done
Stopping uvis-backend  ... done
Stopping uvis-redis    ... done
Stopping uvis-db       ... done
[SUCCESS] 서비스 중지 완료

[INFO] 프론트엔드 이미지 빌드 중 (캐시 없이)...
Building frontend
[+] Building 456.2s (15/15) FINISHED
 => [internal] load build definition from Dockerfile.prod
 => => transferring dockerfile: 1.23kB
 => [internal] load .dockerignore
 => => transferring context: 150B
 ...
 => => exporting layers
 => => writing image sha256:abc123...
[SUCCESS] 프론트엔드 이미지 빌드 완료

[INFO] 백엔드 이미지 빌드 중...
Building backend
[+] Building 123.4s (12/12) FINISHED
...
[SUCCESS] 백엔드 이미지 빌드 완료

[INFO] 서비스 시작 중...
Creating network "uvis_default" with the default driver
Creating uvis-db       ... done
Creating uvis-redis    ... done
Creating uvis-backend  ... done
Creating uvis-frontend ... done
Creating uvis-nginx    ... done
[SUCCESS] 서비스 시작 완료

[INFO] 서비스 안정화 대기 중...
[INFO] 서비스 상태 확인 중...

NAME            COMMAND                  SERVICE    STATUS       PORTS
uvis-backend    "uvicorn main:app ..."   backend    Up 15s (healthy)   0.0.0.0:8000->8000/tcp
uvis-db         "docker-entrypoint..."   db         Up 15s (healthy)   0.0.0.0:5432->5432/tcp
uvis-frontend   "docker-entrypoint..."   frontend   Up 15s       0.0.0.0:3000->3000/tcp
uvis-nginx      "/docker-entrypoin..."   nginx      Up 15s       0.0.0.0:80->80/tcp
uvis-redis      "docker-entrypoint..."   redis      Up 15s (healthy)   0.0.0.0:6379->6379/tcp

[SUCCESS] ✓ frontend: Running
[SUCCESS] ✓ backend: Running
[SUCCESS] ✓ db: Running
[SUCCESS] ✓ redis: Running
[SUCCESS] ✓ nginx: Running

[INFO] Health check 수행 중...
[SUCCESS] ✓ Backend health check passed
[SUCCESS] ✓ Frontend health check passed

==========================================
  🎉 배포 완료
==========================================
배포 완료 시간: 2026-01-29 14:47:30
배포된 커밋: 1bb492c
백업 위치: /root/uvis_backups/backup_20260129_143000

[SUCCESS] ✅ 모든 서비스가 정상 작동 중입니다

==========================================
  📊 접속 정보
==========================================
Frontend:  http://139.150.11.99
Backend:   http://139.150.11.99:8000
API Docs:  http://139.150.11.99:8000/docs

==========================================
  📝 다음 단계
==========================================
1. 브라우저에서 http://139.150.11.99/orders 접속
2. 신규 주문 등록 테스트
3. 온도대 선택 시 자동 입력 확인:
   - 냉동: -30°C ~ -18°C
   - 냉장: 0°C ~ 6°C
   - 상온: -30°C ~ 60°C
4. 주문 등록 완료 테스트
5. 팀에 배포 완료 알림
```

### 예상 소요 시간

- **총 소요 시간**: 15-20분
- **가장 오래 걸리는 부분**: 프론트엔드 빌드 (10-15분)

### 진행 중 주의사항

⚠️ **배포 중에는**:
- PuTTY 창을 닫지 마세요
- Ctrl+C를 누르지 마세요 (중단됨)
- 네트워크 연결을 유지하세요
- 화면이 멈춘 것처럼 보여도 기다리세요 (정상)

💡 **팁**:
- 빌드 중에는 많은 로그가 출력됩니다 (정상)
- 스크롤하여 이전 메시지를 확인할 수 있습니다
- 마우스 휠로 스크롤 가능

---

## 4. 테스트 실행

### Step 4-1: 서비스 상태 확인

배포가 완료된 후 PuTTY에서:

```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

**예상 출력**:
```
NAME            STATUS              PORTS
uvis-backend    Up (healthy)        0.0.0.0:8000->8000/tcp
uvis-db         Up (healthy)        0.0.0.0:5432->5432/tcp
uvis-frontend   Up                  0.0.0.0:3000->3000/tcp
uvis-nginx      Up                  0.0.0.0:80->80/tcp
uvis-redis      Up (healthy)        0.0.0.0:6379->6379/tcp
```

✅ **모든 컨테이너가 "Up" 상태여야 합니다**

### Step 4-2: Health Check

```bash
# Backend API 확인
curl http://localhost:8000/health

# 예상 출력: {"status":"ok"}

# Frontend 확인
curl -I http://localhost:3000

# 예상 출력: HTTP/1.1 200 OK
```

### Step 4-3: 브라우저에서 테스트

1. **웹 브라우저 열기** (Chrome, Edge, Firefox 등)

2. **주문 관리 페이지 접속**:
   ```
   http://139.150.11.99/orders
   ```

3. **로그인**:
   - 사용자: `admin`
   - 비밀번호: [기존 비밀번호]

4. **온도 자동입력 테스트**:
   
   a. "+ 신규 등록" 버튼 클릭
   
   b. 온도대 드롭다운 클릭
   
   c. "냉동" 선택
      - ✅ 최저 온도: **-30** 자동 입력
      - ✅ 최고 온도: **-18** 자동 입력
   
   d. "냉장" 선택
      - ✅ 최저 온도: **0** 자동 입력
      - ✅ 최고 온도: **6** 자동 입력
   
   e. "상온" 선택
      - ✅ 최저 온도: **-30** 자동 입력
      - ✅ 최고 온도: **60** 자동 입력

5. **주문 등록 완료**:
   - 거래처, 출발지, 도착지, 팔레트 수량 입력
   - "등록" 버튼 클릭
   - ✅ "주문이 등록되었습니다" 메시지 확인

### Step 4-4: 로그 확인 (PuTTY에서)

```bash
# 최근 로그 확인 (20줄)
docker-compose -f docker-compose.prod.yml logs --tail=20

# 프론트엔드 로그만
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend

# 백엔드 로그만
docker-compose -f docker-compose.prod.yml logs --tail=20 backend

# 에러 확인
docker-compose -f docker-compose.prod.yml logs | grep -i error
```

---

## 5. 문제 해결

### 문제 1: PuTTY 연결이 끊김

**증상**: "Network error: Connection timed out"

**해결**:
1. PuTTY 재실행
2. 다시 접속 (Step 1 반복)
3. 배포 진행 상황 확인:
   ```bash
   cd /root/uvis
   docker-compose -f docker-compose.prod.yml ps
   ```

### 문제 2: 배포 스크립트 실행 중 멈춤

**증상**: 화면이 멈춘 것처럼 보임

**확인**:
1. 빌드 중일 수 있습니다 (정상) - 10-15분 대기
2. 네트워크 연결 확인
3. 새 PuTTY 창에서 접속하여 확인:
   ```bash
   cd /root/uvis
   docker ps
   ```

### 문제 3: 배포 스크립트 에러

**증상**: "[ERROR]" 메시지 표시

**해결**:
1. 에러 메시지 확인
2. 로그 확인:
   ```bash
   docker-compose -f docker-compose.prod.yml logs
   ```
3. 서비스 재시작:
   ```bash
   docker-compose -f docker-compose.prod.yml restart
   ```

### 문제 4: 온도 자동입력이 작동하지 않음

**증상**: 브라우저에서 온도가 자동 입력되지 않음

**해결**:
1. **브라우저 캐시 삭제**:
   - Chrome: Ctrl+Shift+Delete
   - 또는 Ctrl+Shift+R (하드 리프레시)

2. **시크릿 모드에서 테스트**:
   - Chrome: Ctrl+Shift+N
   - URL 다시 접속

3. **프론트엔드 재시작** (PuTTY에서):
   ```bash
   cd /root/uvis
   docker-compose -f docker-compose.prod.yml restart frontend
   
   # 로그 확인
   docker-compose -f docker-compose.prod.yml logs -f frontend
   ```

### 문제 5: 422 에러 발생

**증상**: 주문 등록 시 422 에러

**해결**:
1. **백엔드 재시작** (PuTTY에서):
   ```bash
   docker-compose -f docker-compose.prod.yml restart backend
   ```

2. **브라우저 캐시 삭제**

3. **로그 확인**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend | tail -50
   ```

### 문제 6: 서비스가 시작되지 않음

**증상**: 컨테이너가 "Exited" 상태

**해결**:
```bash
# 1. 모든 서비스 중지
docker-compose -f docker-compose.prod.yml down

# 2. 로그 확인
docker-compose -f docker-compose.prod.yml logs

# 3. 재시작
docker-compose -f docker-compose.prod.yml up -d

# 4. 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

### 긴급 롤백

**심각한 문제 발생 시**:

```bash
cd /root/uvis

# 이전 커밋 목록 확인
git log --oneline -5

# 이전 커밋으로 롤백 (예: 7780df5)
git checkout 7780df5

# 재배포
bash deploy_production.sh
```

---

## 📋 PuTTY 사용 팁

### 복사/붙여넣기
- **복사**: 텍스트 드래그 선택 (자동 복사)
- **붙여넣기**: 
  - 마우스 오른쪽 클릭
  - 또는 Shift+Insert
  - 또는 중간 버튼 클릭

### 스크롤
- **마우스 휠**: 위/아래 스크롤
- **Shift + Page Up/Down**: 페이지 단위 스크롤

### 화면 정리
```bash
clear    # 화면 지우기
```

### 명령어 히스토리
- **↑ (위 화살표)**: 이전 명령어
- **↓ (아래 화살표)**: 다음 명령어

### 자동 완성
- **Tab 키**: 명령어/파일명 자동 완성

### 명령어 중단
- **Ctrl+C**: 현재 실행 중인 명령어 중단

---

## ✅ 배포 완료 체크리스트

배포 후 다음을 확인하세요:

- [ ] PuTTY에서 배포 스크립트 실행 완료
- [ ] "배포 완료" 메시지 확인
- [ ] 모든 컨테이너 "Up" 상태
- [ ] Health check 통과
- [ ] 브라우저에서 페이지 로딩
- [ ] 로그인 성공
- [ ] 온도 자동입력 작동 (냉동/냉장/상온)
- [ ] 주문 등록 성공
- [ ] 팀에 배포 완료 알림

---

## 📞 추가 도움

### 문서 링크
- [배포 가이드](https://github.com/rpaakdi1-spec/3-/blob/main/DEPLOYMENT_INSTRUCTIONS.md)
- [테스트 체크리스트](https://github.com/rpaakdi1-spec/3-/blob/main/DEPLOYMENT_TEST_CHECKLIST.md)

### 유용한 명령어 모음

```bash
# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 실시간 로그 보기 (Ctrl+C로 종료)
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 재시작
docker-compose -f docker-compose.prod.yml restart frontend
docker-compose -f docker-compose.prod.yml restart backend

# 모든 서비스 재시작
docker-compose -f docker-compose.prod.yml restart

# 디스크 사용량 확인
df -h

# 메모리 사용량 확인
free -h

# 현재 커밋 확인
git log --oneline -1

# 현재 디렉토리 확인
pwd
```

---

**PuTTY로 배포를 시작하세요!** 🚀

배포 중 문제가 발생하면 이 가이드의 "문제 해결" 섹션을 참고하세요.

**문서 버전**: 1.0  
**작성일**: 2026-01-29  
**작성자**: GenSpark AI Developer
