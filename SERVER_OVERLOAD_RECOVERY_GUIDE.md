# 🚨 서버 과부하 복구 가이드

**날짜**: 2026-02-08  
**상황**: PuTTY 연결 불가 (서버 과부하 추정)

---

## 🔍 증상 진단

### 현재 상황
- ❌ PuTTY SSH 연결 실패
- ⚠️ 서버 응답 없음
- 💡 원인: 서버 리소스 과부하 (CPU/메모리)

### 가능한 원인
1. **메모리 부족** (Out of Memory)
2. **CPU 100% 사용**
3. **디스크 I/O 과부하**
4. **좀비 프로세스**
5. **로그 파일 과다**

---

## 🆘 긴급 복구 방법

### 옵션 1: Hetzner 웹 콘솔 사용 (권장)

#### 단계 1: Hetzner Cloud Console 접속
```
1. https://console.hetzner.cloud/ 접속
2. 로그인
3. 해당 서버 선택
4. 우측 상단 "Console" 버튼 클릭
```

#### 단계 2: 리소스 상태 확인
```bash
# 메모리 사용량 확인
free -h

# CPU 사용량 확인
top -bn1 | head -20

# 디스크 사용량 확인
df -h

# 실행 중인 프로세스 확인
ps aux --sort=-%mem | head -20
```

#### 단계 3: 문제 프로세스 종료
```bash
# Docker 컨테이너 상태 확인
docker ps

# 과부하 컨테이너 재시작
docker restart <container_name>

# 또는 전체 재시작
docker-compose -f /root/uvis/docker-compose.yml restart

# 최악의 경우 Docker 전체 중지 후 시작
docker-compose -f /root/uvis/docker-compose.yml down
docker-compose -f /root/uvis/docker-compose.yml up -d
```

---

### 옵션 2: Hetzner 서버 재시작 (긴급)

#### 웹 콘솔에서 재시작
```
1. Hetzner Cloud Console 접속
2. 서버 선택
3. "Power" > "Reboot" 클릭
4. 확인
5. 2-3분 대기 후 재접속 시도
```

#### ⚠️ 주의사항
- 재시작 시 모든 컨테이너가 자동 시작되도록 설정되어 있음
- 데이터 손실 없음 (영구 볼륨 사용)
- 약 3-5분 소요

---

## 🔧 복구 후 실행할 명령어

### 1단계: 서버 접속 확인
```bash
ssh root@139.150.11.99
```

### 2단계: 시스템 상태 확인
```bash
# 메모리 상태
free -h

# 디스크 상태
df -h

# CPU 로드
uptime

# Docker 상태
docker ps
```

### 3단계: 로그 확인
```bash
cd /root/uvis

# 전체 로그 확인
docker-compose logs --tail=100

# 백엔드 로그
docker-compose logs backend --tail=50

# 프론트엔드 로그
docker-compose logs frontend --tail=50

# Nginx 로그
docker-compose logs nginx --tail=50
```

### 4단계: 서비스 헬스체크
```bash
# 백엔드 헬스체크
curl http://localhost:8000/health

# 프론트엔드 확인
curl -I http://localhost/

# 데이터베이스 확인
docker-compose exec db pg_isready -U postgres
```

---

## 🛡️ 예방 조치

### 즉시 실행할 명령어

#### 1. 로그 파일 정리
```bash
# Docker 로그 정리
docker system prune -af

# 시스템 로그 정리
journalctl --vacuum-time=7d

# 임시 파일 정리
rm -rf /tmp/*
rm -rf /var/tmp/*
```

#### 2. 메모리 최적화
```bash
# 캐시 정리
sync && echo 3 > /proc/sys/vm/drop_caches

# Swap 활성화 확인
swapon --show
```

#### 3. Docker 리소스 제한 설정
```yaml
# /root/uvis/docker-compose.yml 수정 필요
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          memory: 1G
  
  frontend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
```

#### 4. 모니터링 설정
```bash
# Prometheus/Grafana 확인
docker-compose ps prometheus grafana

# 메트릭 확인
curl http://localhost:9090/metrics | head -50
```

---

## 📊 리소스 모니터링 스크립트

### 자동 모니터링 스크립트 생성
```bash
cat > /root/uvis/monitor.sh << 'EOF'
#!/bin/bash

echo "===== 시스템 리소스 모니터링 ====="
echo "시간: $(date)"
echo ""

echo "=== 메모리 사용량 ==="
free -h
echo ""

echo "=== CPU 사용량 ==="
top -bn1 | head -20
echo ""

echo "=== 디스크 사용량 ==="
df -h
echo ""

echo "=== Docker 컨테이너 상태 ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== 상위 메모리 사용 프로세스 ==="
ps aux --sort=-%mem | head -10
echo ""

echo "=== 상위 CPU 사용 프로세스 ==="
ps aux --sort=-%cpu | head -10
EOF

chmod +x /root/uvis/monitor.sh
```

### 모니터링 실행
```bash
# 1회 실행
/root/uvis/monitor.sh

# 1분마다 실행 (Ctrl+C로 중지)
watch -n 60 /root/uvis/monitor.sh
```

---

## 🚀 서비스 재시작 스크립트

### 안전한 재시작 스크립트
```bash
cat > /root/uvis/safe_restart.sh << 'EOF'
#!/bin/bash

echo "===== 안전한 서비스 재시작 ====="
cd /root/uvis

echo "1. 현재 상태 저장..."
docker-compose ps > /tmp/docker_status_before.txt

echo "2. 로그 백업..."
docker-compose logs --tail=500 > /tmp/docker_logs_backup.txt

echo "3. 서비스 중지..."
docker-compose down

echo "4. 시스템 리소스 정리..."
sync && echo 3 > /proc/sys/vm/drop_caches

echo "5. 5초 대기..."
sleep 5

echo "6. 서비스 시작..."
docker-compose up -d

echo "7. 10초 대기..."
sleep 10

echo "8. 서비스 상태 확인..."
docker-compose ps

echo "9. 헬스체크..."
echo "Backend:"
curl -s http://localhost:8000/health | jq .

echo ""
echo "Frontend:"
curl -I http://localhost/

echo ""
echo "✅ 재시작 완료!"
EOF

chmod +x /root/uvis/safe_restart.sh
```

### 실행
```bash
/root/uvis/safe_restart.sh
```

---

## 📞 Hetzner 서버 정보

### 서버 스펙
- **Provider**: Hetzner Cloud
- **IP**: 139.150.11.99
- **Location**: 독일 (Falkenstein)
- **RAM**: 4GB
- **CPU**: 2 vCPU
- **Storage**: 40GB SSD

### 접속 정보
- **SSH**: `ssh root@139.150.11.99`
- **웹 콘솔**: https://console.hetzner.cloud/

---

## 🔍 문제 원인 분석 (복구 후)

### 로그 분석 명령어
```bash
cd /root/uvis

# 에러 로그만 추출
docker-compose logs | grep -i "error\|exception\|fatal" | tail -100

# 메모리 관련 로그
docker-compose logs | grep -i "memory\|oom" | tail -50

# 최근 재시작 로그
docker-compose logs | grep -i "restart\|stopped\|killed" | tail -50
```

---

## 💡 권장 조치

### 즉시 조치
1. ✅ Hetzner 웹 콘솔로 서버 재시작
2. ✅ SSH 재접속 확인
3. ✅ Docker 서비스 상태 확인
4. ✅ 로그 분석

### 단기 조치 (오늘)
1. ⏳ 리소스 사용량 모니터링
2. ⏳ 불필요한 로그 정리
3. ⏳ Docker 리소스 제한 설정
4. ⏳ 메모리 스왑 설정 확인

### 중기 조치 (이번 주)
1. ⏳ 서버 스펙 업그레이드 검토 (RAM 8GB로)
2. ⏳ 자동 알림 시스템 구축
3. ⏳ 로그 로테이션 설정
4. ⏳ 부하 테스트 수행

---

## 🆘 긴급 연락처

### Hetzner 지원
- **웹사이트**: https://www.hetzner.com/support
- **지원 티켓**: https://console.hetzner.cloud/support

### 시스템 관리자
- 프로젝트 담당자에게 연락

---

## 📋 체크리스트

### 즉시 확인 사항
- [ ] Hetzner 웹 콘솔 접속 가능?
- [ ] 서버 재시작 시도?
- [ ] SSH 재접속 성공?
- [ ] Docker 컨테이너 정상 작동?
- [ ] 웹사이트 접속 가능?

### 복구 후 확인 사항
- [ ] 백엔드 API 응답?
- [ ] 프론트엔드 로딩?
- [ ] 데이터베이스 연결?
- [ ] 로그에 에러 없음?
- [ ] 리소스 사용량 정상?

---

## 📝 복구 로그 기록

### 복구 작업 기록
```bash
# 복구 로그 파일 생성
cat > /root/uvis/recovery_log_$(date +%Y%m%d_%H%M%S).txt << 'EOF'
===== 서버 복구 로그 =====
날짜: $(date)
작업자: 

== 문제 상황 ==
- 

== 수행한 조치 ==
- 

== 결과 ==
- 

== 재발 방지 ==
- 

EOF
```

---

## ✅ 결론

**복구 절차 요약:**

1. **Hetzner 웹 콘솔** 접속
2. **서버 재시작** (Power > Reboot)
3. **3-5분 대기** 후 SSH 재접속
4. **Docker 상태 확인** (`docker ps`)
5. **서비스 헬스체크** (curl 명령어)
6. **로그 분석** (에러 확인)
7. **모니터링 설정** (재발 방지)

**긴급 연락처:**
- Hetzner: https://console.hetzner.cloud/

---

**작성자**: AI Assistant  
**최종 업데이트**: 2026-02-08 05:40 UTC
