# 🚨 가비아 서버 접속 불가 - 긴급 복구 가이드

**현재 상황**: PuTTY로 서버 접속 불가 (과부하 추정)  
**서버 제공사**: 가비아 (Gabia)  
**서버 IP**: 139.150.11.99

---

## ⚡ 가비아 콘솔을 통한 긴급 복구 (5분)

### 1단계: 가비아 콘솔 접속 ⏱️ 1분

```
1. 브라우저에서 열기: https://my.gabia.com/
2. 로그인 (가비아 계정)
3. 상단 메뉴 → "서비스 관리" → "서버" 클릭
```

### 2단계: 서버 찾기 ⏱️ 30초

```
1. "Server" 또는 "Cloud Server" 메뉴
2. 서버 목록에서 IP "139.150.11.99" 또는 서버명으로 찾기
3. 해당 서버 클릭하여 상세 페이지 진입
```

### 3단계: 서버 상태 확인 및 재시작 ⏱️ 3분

#### 옵션 A: 웹 콘솔 사용 (권장)

```
1. 서버 상세 페이지에서
2. "콘솔" 또는 "원격 콘솔" 버튼 클릭
3. 브라우저에서 터미널이 열림
4. 다음 명령어 실행:
```

```bash
# 루트 로그인 (비밀번호 입력)
root

# 시스템 상태 확인
free -h
df -h
top -bn1 | head -20

# 서버 재시작
reboot
```

#### 옵션 B: 가비아 콘솔에서 직접 재시작

```
1. 서버 상세 페이지
2. "서버 관리" 또는 "전원 관리" 메뉴
3. "재시작" 또는 "Reboot" 버튼 클릭
4. 확인
```

### 4단계: 재시작 대기 ⏱️ 2-3분

```
서버가 재시작되는 동안 대기...
가비아 콘솔에서 서버 상태가 "실행 중"으로 변경될 때까지 기다림
```

### 5단계: SSH 재접속 ⏱️ 30초

```bash
# PuTTY 또는 터미널에서
ssh root@139.150.11.99

# 비밀번호 입력
```

---

## 🔍 가비아 서버 정보 확인

### 가비아 콘솔에서 확인할 정보

```
1. 서버 상세 페이지에서:
   - CPU 사용률
   - 메모리 사용률
   - 디스크 사용률
   - 네트워크 트래픽

2. 모니터링 탭 (있는 경우):
   - 실시간 리소스 그래프
   - 트래픽 통계
```

---

## 📊 복구 후 확인 명령어

### SSH 접속 후 즉시 실행

```bash
# 1. 시스템 상태 빠른 확인
echo "===== 시스템 상태 =====" && \
free -h && \
df -h && \
uptime

# 2. Docker 상태 확인
docker ps

# 3. UVIS 서비스 확인
cd /root/uvis && docker-compose ps

# 4. 헬스체크
curl http://localhost:8000/health
```

### 자동 점검 스크립트 실행

```bash
cd /root/uvis

# GitHub에서 스크립트 다운로드
curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/server_recovery_check.sh

# 실행 권한 부여
chmod +x server_recovery_check.sh

# 실행
./server_recovery_check.sh
```

---

## 🆘 가비아 특화 문제 해결

### 문제 1: 웹 콘솔이 없는 경우

**해결책 1: SSH 키 재설정**
```
1. 가비아 콘솔 → 서버 상세
2. "SSH 키 관리" 또는 "비밀번호 재설정"
3. 새 비밀번호 설정
4. 재접속 시도
```

**해결책 2: 방화벽 확인**
```
1. 가비아 콘솔 → 서버 상세
2. "방화벽 설정" 또는 "보안 그룹"
3. SSH 포트 22번이 열려있는지 확인
4. 필요시 "내 IP 추가" 클릭
```

### 문제 2: 서버가 완전히 응답 없음

**긴급 조치: 강제 재시작**
```
1. 가비아 콘솔 → 서버 상세
2. "전원 관리"
3. "강제 종료" 클릭
4. 10초 대기
5. "시작" 클릭
```

⚠️ **주의**: 강제 종료는 데이터 손실 가능성이 있으므로 최후의 수단으로만 사용

---

## 🛡️ 가비아 서버 리소스 모니터링

### 가비아 콘솔에서 모니터링

```
1. 서비스 관리 → 서버
2. 해당 서버 선택
3. "모니터링" 탭 클릭
4. 실시간 그래프 확인:
   - CPU 사용률
   - 메모리 사용률
   - 디스크 I/O
   - 네트워크
```

### SSH에서 모니터링

```bash
# 실시간 리소스 모니터링
watch -n 5 'free -h && df -h && top -bn1 | head -10'

# Docker 리소스 확인
docker stats --no-stream
```

---

## 🔧 가비아 서버 최적화 (복구 후)

### 1. 스왑 메모리 설정 확인

```bash
# 현재 스왑 확인
swapon --show

# 스왑이 없다면 생성 (2GB 예시)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 2. 불필요한 로그 정리

```bash
# Docker 로그 정리
docker system prune -af --volumes

# 시스템 로그 정리
journalctl --vacuum-time=3d

# 임시 파일 정리
rm -rf /tmp/*
```

### 3. 자동 재시작 설정

```bash
# Cron으로 매일 새벽 4시 메모리 정리
crontab -e

# 아래 라인 추가
0 4 * * * sync && echo 3 > /proc/sys/vm/drop_caches
```

---

## 📞 가비아 고객 지원

### 가비아 연락처

- **고객센터**: 1544-4755 (24시간)
- **웹사이트**: https://www.gabia.com/
- **고객센터**: https://customer.gabia.com/
- **1:1 문의**: 가비아 콘솔 → 고객센터 → 1:1 문의

### 긴급 문의 사항

```
서버 IP: 139.150.11.99
문제: SSH 접속 불가 (과부하 추정)
요청 사항: 서버 상태 확인 및 재시작 지원
```

---

## 🎯 가비아 서버 스펙 확인

### 콘솔에서 확인

```
1. 가비아 콘솔 → 서비스 관리 → 서버
2. 서버 상세 페이지
3. "서버 정보" 또는 "상세 정보" 확인:
   - CPU 코어 수
   - RAM 용량
   - 스토리지 용량
   - 네트워크 대역폭
```

### SSH에서 확인

```bash
# CPU 정보
lscpu | grep -E "^CPU\(s\)|Model name"

# 메모리 정보
free -h

# 디스크 정보
df -h

# OS 정보
cat /etc/os-release
```

---

## ✅ 복구 확인 체크리스트

### 가비아 콘솔 확인
- [ ] 가비아 콘솔 로그인 성공
- [ ] 서버 상태 "실행 중" 확인
- [ ] CPU/메모리 사용률 정상 범위 (<80%)
- [ ] 네트워크 트래픽 정상

### SSH 접속 확인
- [ ] SSH 접속 성공
- [ ] Docker 컨테이너 7개 실행 중
- [ ] 백엔드 API 응답 정상
- [ ] 프론트엔드 웹사이트 접속 가능
- [ ] 데이터베이스 연결 정상

---

## 🚀 서비스 재시작 (필요 시)

### 안전한 재시작 절차

```bash
# 1. 작업 디렉토리 이동
cd /root/uvis

# 2. 현재 상태 백업
docker-compose logs --tail=500 > /tmp/logs_backup_$(date +%Y%m%d_%H%M%S).txt

# 3. 모든 컨테이너 중지
docker-compose down

# 4. 5초 대기
sleep 5

# 5. 다시 시작
docker-compose up -d

# 6. 상태 확인
docker-compose ps

# 7. 헬스체크
sleep 10
curl http://localhost:8000/health
curl -I http://localhost/
```

---

## 💡 가비아 서버 업그레이드 고려사항

### 현재 리소스가 부족하다면

**옵션 1: 서버 스펙 업그레이드**
```
1. 가비아 콘솔 → 서버 관리
2. "서버 스펙 변경" 또는 "업그레이드"
3. CPU/RAM 증설 옵션 선택
4. 권장: RAM 4GB → 8GB
```

**옵션 2: 로드 밸런싱**
```
1. 가비아의 로드 밸런서 서비스 검토
2. 멀티 서버 구성 고려
```

---

## 📊 예방 모니터링 설정

### Grafana 대시보드 활용

```bash
# Grafana 접속
http://139.150.11.99:3001

# 기본 로그인
ID: admin
PW: (설정된 비밀번호)

# 알림 설정
1. Alerting → Notification channels
2. Email/Slack 알림 추가
3. CPU/메모리 임계값 설정 (80%)
```

---

## 🎊 복구 성공 확인

### 정상 작동 지표

```bash
# 모든 서비스가 정상이면 아래 출력 확인
curl http://localhost:8000/health
# 출력: {"status":"healthy",...}

curl -I http://localhost/
# 출력: HTTP/1.1 200 OK

docker-compose ps | grep "Up"
# 7개 컨테이너 모두 "Up" 상태
```

---

## 📝 복구 로그 기록

```bash
# 복구 작업 기록
cat > /root/uvis/recovery_log_$(date +%Y%m%d_%H%M%S).txt << EOF
===== 가비아 서버 복구 로그 =====
날짜: $(date)
서버 IP: 139.150.11.99

== 문제 상황 ==
- PuTTY SSH 접속 불가
- 서버 과부하 추정

== 수행한 조치 ==
- 가비아 콘솔을 통한 서버 재시작
- 시스템 리소스 확인
- Docker 컨테이너 상태 점검
- 서비스 헬스체크 수행

== 결과 ==
- SSH 접속: 복구
- 모든 서비스: 정상
- 리소스 사용량: 정상 범위

== 향후 계획 ==
- 리소스 모니터링 강화
- 자동 알림 설정
- 정기 점검 실시
EOF

cat /root/uvis/recovery_log_*.txt
```

---

## 🔗 관련 문서

- `SERVER_OVERLOAD_RECOVERY_GUIDE.md` - 상세 복구 가이드
- `server_recovery_check.sh` - 자동 점검 스크립트
- GitHub: https://github.com/rpaakdi1-spec/3-

---

**작성**: 2026-02-08  
**서버 제공사**: 가비아 (Gabia)  
**최종 업데이트**: AI Assistant

**중요**: 가비아 서버 특성에 맞춘 복구 절차입니다. 웹 콘솔 기능이 다를 수 있으므로 가비아 고객센터(1544-4755)에 문의하시기 바랍니다.
