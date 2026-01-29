# 🇰🇷 Cafe24 호스팅 완벽 가이드

## 📋 목차

- [개요](#개요)
- [Step 1: Cafe24 가입 및 서버 구매](#step-1-cafe24-가입-및-서버-구매)
- [Step 2: 서버 정보 확인 및 SSH 접속](#step-2-서버-정보-확인-및-ssh-접속)
- [Step 3: 자동 배포 스크립트 실행](#step-3-자동-배포-스크립트-실행)
- [Step 4: 접속 확인 및 테스트](#step-4-접속-확인-및-테스트)
- [Step 5: 시스템 관리](#step-5-시스템-관리)
- [도메인 연결 (선택사항)](#도메인-연결-선택사항)
- [문제 해결](#문제-해결)
- [Cafe24 고객 지원](#cafe24-고객-지원)

---

## 개요

### ⏱️ 소요 시간
- **총 소요 시간**: 약 30분
- Step 1: 10분 (가입 및 서버 구매)
- Step 2: 2분 (SSH 접속)
- Step 3: 20분 (자동 배포)
- Step 4: 3분 (접속 확인)

### 💰 비용
- **월 요금**: 4,400원 (VAT 별도)
- **연 요금**: 52,800원
- **5년 총 비용**: 264,000원

### 🎯 난이도
⭐⭐ (쉬움 - 초보자도 가능)

### ✅ 필요한 것
- Cafe24 계정
- 신용카드 또는 계좌이체
- SSH 접속 가능한 환경 (Windows/Mac/Linux)

---

## Step 1: Cafe24 가입 및 서버 구매

### 1-1. Cafe24 회원가입

1. **Cafe24 사이트 접속**
   - URL: https://www.cafe24.com/
   - 우측 상단 "회원가입" 클릭

2. **회원가입 진행**
   - URL: https://www.cafe24.com/member/join.php
   - 이메일, 비밀번호, 휴대폰 인증 완료

3. **본인 인증**
   - 휴대폰 인증 또는 아이핀 인증

### 1-2. 클라우드 호스팅 선택

1. **클라우드 호스팅 페이지 접속**
   - 로그인 후 상단 메뉴 "호스팅" → "클라우드 호스팅"
   - 직접 접속: https://www.cafe24.com/solutions/cloud-hosting

2. **플랜 선택**
   - **추천 플랜**: **스타트업 플랜**
     - CPU: 2 Core
     - RAM: 2GB
     - SSD: 50GB
     - 트래픽: 무제한
     - 월 요금: **4,400원** (VAT 별도)

3. **"신청하기" 클릭**

### 1-3. 서버 설정

1. **서버 위치 선택**
   - **추천**: 서울 IDC (낮은 지연시간)
   - 대안: 대전 IDC

2. **운영체제 선택**
   - **Ubuntu 22.04 LTS** (추천)
   - 다른 버전 사용 시 배포 스크립트 수정 필요

3. **관리자 비밀번호 설정**
   - 최소 8자 이상
   - 영문, 숫자, 특수문자 포함
   - 안전하게 보관

4. **서버 이름 설정** (선택사항)
   - 예: `uvis-production-001`

### 1-4. 결제

1. **결제 방법 선택**
   - 신용카드 (추천 - 자동 결제)
   - 계좌이체
   - 무통장 입금

2. **결제 완료**

### 1-5. 서버 정보 확인

1. **마이페이지 접속**
   - URL: https://www.cafe24.com/mypage
   - "호스팅 관리" → "클라우드 호스팅"

2. **서버 정보 확인**
   ```
   서버명: uvis-production-001
   IP 주소: 123.456.789.012  (예시 - 실제 IP로 대체)
   OS: Ubuntu 22.04 LTS
   상태: 실행 중 ✅
   ```

3. **IP 주소 메모**
   - 이후 단계에서 필요

---

## Step 2: 서버 정보 확인 및 SSH 접속

### 2-1. SSH 접속 방법

#### Windows 사용자

**방법 1: 내장 SSH 사용 (Windows 10 이상)**
```bash
# 명령 프롬프트 또는 PowerShell 실행
ssh root@123.456.789.012
```

**방법 2: PuTTY 사용**
1. PuTTY 다운로드: https://www.putty.org/
2. Host Name: `123.456.789.012`
3. Port: `22`
4. Connection Type: `SSH`
5. "Open" 클릭

#### Mac/Linux 사용자

```bash
# 터미널 실행
ssh root@123.456.789.012
```

### 2-2. SSH 접속

1. **최초 접속 시 확인 메시지**
   ```
   The authenticity of host '123.456.789.012' can't be established.
   Are you sure you want to continue connecting (yes/no)?
   ```
   - `yes` 입력

2. **비밀번호 입력**
   - Cafe24에서 설정한 관리자 비밀번호 입력

3. **접속 성공**
   ```
   Welcome to Ubuntu 22.04 LTS
   root@uvis-production-001:~#
   ```

---

## Step 3: 자동 배포 스크립트 실행

### 3-1. 배포 스크립트 다운로드

```bash
# GitHub에서 자동 배포 스크립트 다운로드
wget https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-cafe24.sh
```

### 3-2. 실행 권한 부여

```bash
chmod +x deploy-cafe24.sh
```

### 3-3. 스크립트 실행

```bash
sudo ./deploy-cafe24.sh
```

### 3-4. 스크립트 실행 과정

스크립트가 자동으로 다음 작업을 수행합니다:

1. ✅ **시스템 환경 확인** (1분)
   - Ubuntu 버전 확인
   - 필요한 리소스 확인

2. ✅ **시스템 업데이트** (2분)
   - 패키지 목록 업데이트
   - 보안 패치 적용

3. ✅ **Docker 설치** (3분)
   - Docker Engine 설치
   - Docker Compose 설치
   - Docker 서비스 시작

4. ✅ **보안 설정** (2분)
   - UFW 방화벽 설정
   - Fail2Ban 설치 및 설정

5. ✅ **프로젝트 클론** (1분)
   - GitHub에서 프로젝트 다운로드

6. ✅ **환경 변수 설정** (1분)
   - `.env` 파일 생성
   - 데이터베이스 비밀번호 자동 생성

7. ✅ **데이터베이스 구성** (2분)
   - PostgreSQL 컨테이너 시작
   - Redis 컨테이너 시작

8. ✅ **백엔드 구성** (3분)
   - FastAPI 애플리케이션 빌드
   - 데이터베이스 마이그레이션

9. ✅ **프론트엔드 구성** (3분)
   - React 애플리케이션 빌드
   - Nginx 설정

10. ✅ **모니터링 설치** (2분)
    - Netdata 설치 여부 질문
    - 선택 시 Netdata 자동 설치

### 3-5. 스크립트 완료

```
========================================
✅ Cafe24 배포 완료!
========================================

📍 접속 정보:
- 프론트엔드: http://123.456.789.012
- 백엔드 API: http://123.456.789.012:8000
- API 문서: http://123.456.789.012:8000/docs
- Monitoring: http://123.456.789.012:19999

🔐 기본 관리자 계정:
- 아이디: admin
- 비밀번호: admin123
⚠️ 로그인 후 반드시 비밀번호를 변경하세요!

========================================
```

---

## Step 4: 접속 확인 및 테스트

### 4-1. 프론트엔드 접속

1. **브라우저에서 접속**
   ```
   http://123.456.789.012
   ```

2. **로그인 화면 확인**
   - 로그인 페이지가 표시되어야 합니다

3. **관리자 계정으로 로그인**
   - 아이디: `admin`
   - 비밀번호: `admin123`

4. **대시보드 확인**
   - 메인 대시보드가 정상적으로 표시되어야 합니다

### 4-2. 백엔드 API 테스트

1. **API 문서 접속**
   ```
   http://123.456.789.012:8000/docs
   ```

2. **Health Check**
   ```
   http://123.456.789.012:8000/health
   ```
   - 응답 예시:
   ```json
   {
     "status": "healthy",
     "timestamp": "2026-01-28T09:45:00Z"
   }
   ```

### 4-3. 모니터링 확인 (선택)

Netdata를 설치한 경우:
```
http://123.456.789.012:19999
```

- CPU, 메모리, 디스크, 네트워크 상태 확인

---

## Step 5: 시스템 관리

### 5-1. Docker 컨테이너 상태 확인

```bash
# SSH 접속 후
docker ps

# 실행 중인 컨테이너 목록
CONTAINER ID   IMAGE              STATUS         PORTS
a1b2c3d4e5f6   uvis-frontend     Up 10 minutes   80:80
b2c3d4e5f6g7   uvis-backend      Up 10 minutes   8000:8000
c3d4e5f6g7h8   postgres:15       Up 10 minutes   5432:5432
d4e5f6g7h8i9   redis:7-alpine    Up 10 minutes   6379:6379
```

### 5-2. 로그 확인

```bash
# 프론트엔드 로그
docker logs -f uvis-frontend

# 백엔드 로그
docker logs -f uvis-backend

# 데이터베이스 로그
docker logs -f uvis-postgres
```

### 5-3. 서비스 재시작

```bash
# 전체 서비스 재시작
cd /opt/uvis-gps-fleet
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart backend
docker-compose restart frontend
```

### 5-4. 서비스 중지/시작

```bash
# 전체 서비스 중지
docker-compose down

# 전체 서비스 시작
docker-compose up -d
```

### 5-5. 데이터베이스 백업

```bash
# 백업 디렉토리 생성
mkdir -p /opt/backups

# PostgreSQL 백업
docker exec uvis-postgres pg_dump -U uvis_user uvis_gps_fleet > /opt/backups/backup_$(date +%Y%m%d).sql

# 백업 파일 확인
ls -lh /opt/backups/
```

---

## 도메인 연결 (선택사항)

### 6-1. 도메인 구매

1. **Cafe24 도메인 섹션**
   - 로그인 → "도메인" → "도메인 등록"
   - 원하는 도메인 검색 및 구매
   - 예: `mydomain.com`

### 6-2. DNS 설정

1. **DNS 관리 페이지 접속**
   - "도메인 관리" → "DNS 관리"

2. **A 레코드 추가**
   ```
   호스트명: @
   타입: A
   값: 123.456.789.012 (서버 IP)
   TTL: 3600
   ```

3. **www 레코드 추가** (선택)
   ```
   호스트명: www
   타입: A
   값: 123.456.789.012
   TTL: 3600
   ```

### 6-3. Nginx 설정 변경

1. **SSH 접속**

2. **Nginx 설정 파일 편집**
   ```bash
   nano /opt/uvis-gps-fleet/nginx/nginx.conf
   ```

3. **server_name 수정**
   ```nginx
   server {
       listen 80;
       server_name mydomain.com www.mydomain.com;
       # ... 나머지 설정
   }
   ```

4. **Nginx 재시작**
   ```bash
   docker-compose restart nginx
   ```

### 6-4. SSL 인증서 설치 (HTTPS)

```bash
# Certbot 설치
apt-get install -y certbot python3-certbot-nginx

# SSL 인증서 발급
certbot --nginx -d mydomain.com -d www.mydomain.com

# 이메일 입력 및 약관 동의
# 자동으로 Nginx 설정 업데이트

# 인증서 자동 갱신 테스트
certbot renew --dry-run
```

---

## 문제 해결

### 🔧 문제 1: 웹사이트 접속 불가

**증상**: 브라우저에서 `http://123.456.789.012` 접속 시 연결 거부

**해결 방법**:

1. **방화벽 확인**
   ```bash
   sudo ufw status
   
   # 포트 80, 443, 8000 열려있는지 확인
   # 필요시 포트 열기
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 8000/tcp
   ```

2. **Nginx 상태 확인**
   ```bash
   docker ps | grep nginx
   
   # Nginx 로그 확인
   docker logs uvis-frontend
   ```

3. **서비스 재시작**
   ```bash
   docker-compose restart
   ```

### 🔧 문제 2: 프론트엔드 로드 실패

**증상**: 페이지가 로드되지 않거나 빈 화면

**해결 방법**:

1. **Nginx 로그 확인**
   ```bash
   docker logs -f uvis-frontend
   ```

2. **프론트엔드 빌드 확인**
   ```bash
   docker exec -it uvis-frontend ls -la /usr/share/nginx/html/
   ```

3. **Nginx 설정 테스트**
   ```bash
   docker exec -it uvis-frontend nginx -t
   ```

4. **재빌드**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### 🔧 문제 3: 백엔드 API 응답 없음

**증상**: API 요청 시 응답 없음

**해결 방법**:

1. **백엔드 로그 확인**
   ```bash
   docker logs -f uvis-backend
   ```

2. **데이터베이스 연결 확인**
   ```bash
   docker exec -it uvis-postgres psql -U uvis_user -d uvis_gps_fleet -c "SELECT 1;"
   ```

3. **환경 변수 확인**
   ```bash
   docker exec -it uvis-backend env | grep DATABASE
   ```

### 🔧 문제 4: 데이터베이스 연결 실패

**증상**: 백엔드 로그에 데이터베이스 연결 오류

**해결 방법**:

1. **PostgreSQL 상태 확인**
   ```bash
   docker ps | grep postgres
   ```

2. **PostgreSQL 로그 확인**
   ```bash
   docker logs uvis-postgres
   ```

3. **데이터베이스 재시작**
   ```bash
   docker-compose restart postgres
   ```

4. **데이터베이스 연결 테스트**
   ```bash
   docker exec -it uvis-postgres psql -U uvis_user -d uvis_gps_fleet
   ```

---

## Cafe24 고객 지원

### 📞 고객센터

- **전화**: 1544-4754
- **운영 시간**: 24시간 연중무휴
- **이메일**: hosting@cafe24.com

### 💬 온라인 지원

1. **1:1 문의**
   - 로그인 → "고객지원" → "1:1 문의"

2. **원격 지원**
   - 전화 요청 시 원격 지원 가능

3. **FAQ**
   - https://www.cafe24.com/support/faq

---

## 최종 체크리스트

배포 완료 후 아래 항목을 확인하세요:

- [ ] Cafe24 계정 생성 완료
- [ ] 서버 구매 및 결제 완료
- [ ] SSH 접속 성공
- [ ] 자동 배포 스크립트 실행 완료
- [ ] 프론트엔드 접속 확인 (`http://서버IP`)
- [ ] 백엔드 API 접속 확인 (`http://서버IP:8000`)
- [ ] 관리자 계정 로그인 성공
- [ ] 대시보드 정상 작동 확인
- [ ] Netdata 모니터링 확인 (선택)
- [ ] 도메인 연결 완료 (선택)
- [ ] SSL 인증서 설치 완료 (선택)

---

## 💰 비용 요약

| 항목 | 월 비용 | 연 비용 | 5년 비용 |
|------|---------|---------|----------|
| **Cafe24 스타트업 플랜** | ₩4,400 | ₩52,800 | ₩264,000 |
| AWS (비교) | ₩30,000+ | ₩360,000+ | ₩1,800,000+ |
| Hetzner CX22 (비교) | ₩6,500 | ₩78,000 | ₩390,000 |

**절감 효과**:
- AWS 대비: **5년간 최대 1,536,000원 절감** 🎉
- Hetzner 대비: **5년간 126,000원 절감** 🎉

---

## 다음 단계

배포 완료 후:

1. **관리자 비밀번호 변경**
   - 보안을 위해 즉시 변경

2. **사용자 및 차량 관리**
   - 실제 운영 데이터 입력

3. **모바일 앱 연결** (선택)
   - React Native 앱 설정
   - 서버 IP 주소 업데이트

4. **정기 백업 설정**
   - 데이터베이스 자동 백업
   - cron 작업 설정

5. **모니터링 알림 설정**
   - Netdata 알림 설정
   - 이메일 또는 Slack 연동

---

## 📚 참고 링크

- **Cafe24 메인**: https://www.cafe24.com/
- **회원가입**: https://www.cafe24.com/member/join.php
- **클라우드 호스팅**: https://www.cafe24.com/solutions/cloud-hosting
- **마이페이지**: https://www.cafe24.com/mypage
- **고객지원**: https://www.cafe24.com/support
- **배포 스크립트**: https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-cafe24.sh

---

## 🎉 축하합니다!

Cafe24에 UVIS GPS 차량 관리 시스템을 성공적으로 배포했습니다!

이제 다음과 같은 기능을 모두 사용할 수 있습니다:
- ✅ 실시간 GPS 차량 추적
- ✅ 배차 관리
- ✅ 운전자 관리
- ✅ 발주 관리
- ✅ ML 기반 수요 예측
- ✅ 비용 최적화
- ✅ 실시간 모니터링

**문의사항이 있으시면 Cafe24 고객센터(1544-4754)로 연락주세요!** 📞
