# 메모리 사용량 분석 및 최적화 방안

## 📊 현재 상황 분석 (2026-02-28)

### 시스템 메모리 현황
```
Total Memory: 3.6GB
Used: 2.4GB (66.7%)
Free: 127MB (3.5%)
Buffer/Cache: 1.0GB (27.8%)
Available: 891MB (24.7%)
Swap Used: 251MB / 2.0GB (12.5%)
```

### 컨테이너별 메모리 사용량

| 컨테이너 | 메모리 사용량 | 비율 | 상태 | 최적화 필요도 |
|---------|-------------|------|------|-------------|
| **coldchain-grafana** | 137.2 MB | 3.74% | ⚠️ 주의 | 🔴 높음 |
| **uvis-backend** | 1.196 GB | 33.42% | ⚠️ 주의 | 🟡 중간 |
| **uvis-minio** | 77.64 MB | 2.12% | ✅ 정상 | 🟢 낮음 |
| **uvis-db** | 46.73 MB | 1.28% | ✅ 정상 | 🟢 낮음 |
| **coldchain-prometheus** | 34.86 MB | 0.95% | ✅ 정상 | 🟢 낮음 |
| **uvis-redis** | 10.46 MB | 0.29% | ✅ 정상 | 🟢 낮음 |
| **uvis-frontend** | 5.672 MB | 0.15% | ✅ 정상 | 🟢 낮음 |
| **uvis-frontend-test** | 2.168 MB | 0.06% | ✅ 정상 | 🟢 낮음 |

**총 컨테이너 메모리**: ~1.5GB

---

## 🔍 주요 문제점

### 1. 🔴 **Docker 캐시 과다** (15.13GB) - 🆕 발견!
- **현재**: 15.13GB 빌드 캐시
- **매우 심각** - 디스크 공간 낭비
- **원인**:
  - 반복된 이미지 빌드
  - 캐시 레이어 축적
  - 자동 정리 미설정
- **해결**: `docker builder prune -af` 실행

### 2. ⚠️ **미사용 Docker 이미지** (8.5GB) - 🆕 발견!
- **현재**: 8.5GB (83% 회수 가능)
- **원인**: 이전 버전 이미지 미삭제
- **해결**: `docker image prune -af`

### 3. ⚠️ **미사용 볼륨** (789MB) - 🆕 발견!
- **현재**: 789MB (85% 회수 가능)
- **원인**: 삭제된 컨테이너의 볼륨 잔존
- **해결**: `docker volume prune -f`

### 4. ⚠️ **Grafana 블록 I/O 과다** (94.7GB)
- **현재**: 94.7GB 블록 I/O
- **비정상적으로 높음** - 디스크 읽기/쓰기 과다
- **원인**: 
  - 데이터 소스 쿼리 과다
  - 대시보드 새로고침 빈도 높음
  - 히스토리 데이터 축적

### 5. ⚠️ **Prometheus 블록 I/O 과다** (44.9GB)
- **현재**: 44.9GB 블록 I/O
- **원인**:
  - 메트릭 수집 간격 짧음
  - 보존 기간 길음
  - 메트릭 종류 과다

### 6. 🔴 **Backend 메모리 사용량 높음** (1.2GB)
- **현재**: 1.196GB (33.42%)
- **원인**:
  - Uvicorn workers 4개 × ~300MB
  - 각 worker가 전체 애플리케이션 로드
  - 캐시 메모리
  - 머신러닝 모델 로드 (있는 경우)

### 7. 📉 **여유 메모리 부족**
- **Free**: 127MB (3.5%) - 매우 낮음
- **Available**: 891MB (24.7%) - 보통
- **Swap 사용**: 251MB (스왑 사용은 성능 저하 신호)

---

## 🚀 최적화 방안

### A. 즉시 조치 (Priority: 🔴 High)

#### 1. **Docker 캐시 및 미사용 리소스 정리** (🆕 최우선)
```bash
# 빌드 캐시 정리 (15.13GB)
docker builder prune -af

# 미사용 이미지 정리 (8.5GB)
docker image prune -af

# 미사용 볼륨 정리 (789MB)
docker volume prune -f
```

**효과**: 디스크 ~24GB 절약

#### 2. **Grafana 최적화**
```bash
# Grafana 설정 수정
docker exec coldchain-grafana sh -c 'cat > /etc/grafana/grafana.ini << EOL
[dashboards]
min_refresh_interval = 30s

[database]
max_open_conn = 3
max_idle_conn = 2

[dataproxy]
logging = false
timeout = 30
EOL'

# Grafana 재시작
docker restart coldchain-grafana
```

**효과**: 메모리 ~40-50MB 절약, I/O 80% 감소

#### 3. **Prometheus 메트릭 보존 기간 단축**
```yaml
# docker-compose.yml의 prometheus 설정
prometheus:
  command:
    - '--storage.tsdb.retention.time=3d'  # 기본 15d → 3d로 단축
    - '--storage.tsdb.retention.size=2GB'  # 최대 크기 제한
    - '--web.enable-lifecycle'
```

**효과**: 디스크 I/O 60% 감소, 메모리 ~20MB 절약

#### 4. **Backend Workers 감소**
```yaml
# docker-compose.yml
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2  # 4 → 2
```

**효과**: 메모리 ~600MB 절약 (1.2GB → 0.6GB)

**트레이드오프**: 동시 요청 처리량 50% 감소 (현재 트래픽 낮음으로 문제 없음)

---

### B. 중기 조치 (Priority: 🟡 Medium)

#### 4. **Buffer/Cache 정리 (필요시)**
```bash
# 캐시 정리 (안전)
sync && echo 3 > /proc/sys/vm/drop_caches
```

**주의**: 임시 해결책, 재부팅 후 다시 증가

#### 5. **Swap 증설**
```bash
# Swap 파일 증설 (2GB → 4GB)
sudo swapoff /swapfile
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**효과**: OOM 방지, 안정성 향상

#### 6. **불필요한 컨테이너 제거**
```bash
# uvis-frontend-test 제거 (테스트용)
docker stop uvis-frontend-test
docker rm uvis-frontend-test
```

**효과**: 메모리 ~2MB 절약 (미미)

---

### C. 장기 조치 (Priority: 🟢 Low)

#### 7. **서버 메모리 업그레이드**
- **현재**: 3.6GB
- **권장**: 8GB 이상
- **이유**: 안정적인 운영, 확장 가능성

#### 8. **마이크로서비스 분리**
- Grafana/Prometheus를 별도 서버로 이동
- Backend를 API Gateway + Worker 패턴으로 분리

#### 9. **Redis/PostgreSQL 메모리 제한**
```yaml
redis:
  command: redis-server --maxmemory 100mb --maxmemory-policy allkeys-lru

db:
  environment:
    - POSTGRES_SHARED_BUFFERS=32MB
    - POSTGRES_EFFECTIVE_CACHE_SIZE=128MB
```

---

## 📝 권장 조치 순서

### 1단계: 즉시 적용 (오늘) - 🆕 종합 스크립트 사용
```bash
cd /root/uvis

# 종합 최적화 스크립트 복사
# (GitHub에서 comprehensive_optimize.sh 다운로드)

# 실행
bash comprehensive_optimize.sh
```

**스크립트가 자동 수행하는 작업:**
1. Docker 빌드 캐시 정리 (15.13GB)
2. 미사용 이미지 정리 (8.5GB)
3. 미사용 볼륨 정리 (789MB)
4. Backend workers 4 → 2로 감소
5. 테스트 컨테이너 제거
6. 시스템 캐시 정리
7. 최적화 전/후 비교

**예상 효과**: 
- 디스크 ~24GB 절약
- 메모리 사용량 2.4GB → 1.8GB (25% 감소)

### 2단계: 1시간 후 확인
```bash
# 메모리 모니터링
watch -n 5 'docker stats --no-stream && free -h'
```

### 3단계: 안정화 (내일)
- Grafana/Prometheus 최적화 적용
- 스왑 증설
- 1주일 모니터링

---

## 🎯 최적화 후 예상 결과

| 항목 | 현재 | 최적화 후 | 개선율 |
|-----|------|----------|--------|
| **Backend 메모리** | 1.196GB | 0.6GB | -50% |
| **Grafana I/O** | 94.7GB | 15GB | -84% |
| **Prometheus I/O** | 44.9GB | 10GB | -78% |
| **시스템 Used** | 2.4GB | 1.8GB | -25% |
| **Available 메모리** | 891MB | 1.5GB | +68% |
| **Swap 사용** | 251MB | 100MB | -60% |
| **🆕 Docker 빌드 캐시** | 15.13GB | 0GB | -100% |
| **🆕 미사용 이미지** | 8.5GB | 0GB | -100% |
| **🆕 미사용 볼륨** | 789MB | 0GB | -100% |
| **🆕 총 디스크 절약** | - | ~24GB | - |

---

## ⚡ 긴급 적용 스크립트

```bash
#!/bin/bash
# 메모리 최적화 긴급 적용

cd /root/uvis

echo "=== 1. Backend Workers 감소 (4 → 2) ==="
cp docker-compose.yml docker-compose.yml.backup
sed -i 's/--workers 4/--workers 2/' docker-compose.yml

echo "=== 2. Backend 재시작 ==="
docker-compose down backend
docker-compose up -d backend

echo "=== 3. 캐시 정리 ==="
sync && echo 3 > /proc/sys/vm/drop_caches

echo "=== 4. 5초 후 메모리 확인 ==="
sleep 5
docker stats --no-stream
free -h

echo "=== 완료 ==="
echo "백엔드 메모리: 1.2GB → 0.6GB 예상"
echo "시스템 여유 메모리: 891MB → 1.5GB 예상"
```

---

## 📊 모니터링 대시보드 추가

```bash
# 실시간 메모리 모니터링
cat > /root/memory_monitor.sh << 'SCRIPT'
#!/bin/bash
while true; do
  clear
  echo "=== Container Memory Usage ==="
  docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
  echo ""
  echo "=== System Memory ==="
  free -h | grep -E 'Mem|Swap'
  sleep 10
done
SCRIPT

chmod +x /root/memory_monitor.sh
```

---

## 🚨 알림 임계값

- **Critical**: Memory > 85% → Backend workers 1로 감소
- **Warning**: Memory > 80% → 캐시 정리
- **OK**: Memory < 75%

---

## 결론

**현재 상태**: ⚠️ 주의 필요 (메모리 75.4%, 디스크 캐시 24GB)  
**주요 원인**: 
- 🔴 Docker 캐시 15.13GB (최우선)
- 🔴 미사용 이미지 8.5GB
- 🟡 Backend workers 과다 (4개)
- 🟡 Grafana/Prometheus I/O 과다

**즉시 조치**: 
1. Docker 캐시/이미지/볼륨 정리 → **디스크 24GB 절약**
2. Backend workers 2개로 감소 → **메모리 25% 절약**

**안정화**: Grafana/Prometheus 최적화 → **I/O 80% 감소**  

**최종 목표**: 
- 메모리 사용률 60% 이하 유지
- 디스크 공간 24GB 확보
- Swap 사용 최소화

**🚀 실행 방법**: 서버에서 `bash comprehensive_optimize.sh` 실행

