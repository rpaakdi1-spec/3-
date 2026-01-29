# 모니터링 시스템 설정 가이드

## 📊 개요

이 문서는 Cold Chain Dispatch System의 모니터링 시스템 (Prometheus + Grafana) 설정 방법을 설명합니다.

## 🏗️ 아키텍처

```
┌─────────────┐
│  Services   │
│ (Backend/   │
│  Frontend)  │
└──────┬──────┘
       │ metrics
       ▼
┌─────────────┐     ┌──────────────┐
│ Prometheus  │────▶│ AlertManager │
│  (수집/저장) │     │  (알림 관리)  │
└──────┬──────┘     └──────┬───────┘
       │                   │
       │ query             │ alerts
       ▼                   ▼
┌─────────────┐     ┌──────────────┐
│  Grafana    │     │  Email/Slack │
│ (시각화)     │     │  (알림 전송)  │
└─────────────┘     └──────────────┘
```

## 🚀 빠른 시작

### 1. 환경 변수 설정

```bash
# .env 파일 생성
cat > infrastructure/monitoring/.env << EOF
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-secure-password

DB_USER=coldchain_user
DB_PASSWORD=coldchain_password
DB_NAME=coldchain_db

REDIS_PASSWORD=coldchain_redis_password
EOF
```

### 2. 모니터링 스택 시작

```bash
# 모니터링 디렉토리로 이동
cd infrastructure/monitoring

# Docker Compose로 시작
docker-compose -f docker-compose.monitoring.yml up -d

# 로그 확인
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 3. 서비스 접속

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin / your-secure-password)
- **AlertManager**: http://localhost:9093
- **cAdvisor**: http://localhost:8080

## 📋 구성 요소

### 1. Prometheus (메트릭 수집 및 저장)

**기능**:
- 애플리케이션 메트릭 수집
- 시계열 데이터 저장 (30일 보관)
- 알림 규칙 평가
- PromQL 쿼리 지원

**수집 대상**:
- ✅ Backend API (FastAPI)
- ✅ PostgreSQL 데이터베이스
- ✅ Redis 캐시
- ✅ 시스템 리소스 (CPU, 메모리, 디스크)
- ✅ 컨테이너 메트릭
- ✅ ECS 서비스 (프로덕션)

**주요 설정**:
- 스크랩 간격: 15초
- 데이터 보관: 30일
- 평가 간격: 15초

### 2. Grafana (시각화 대시보드)

**기능**:
- 실시간 메트릭 시각화
- 커스텀 대시보드 생성
- 알림 및 알람 설정
- 다중 데이터소스 지원

**제공 대시보드**:
1. **시스템 개요** - 전체 시스템 상태
2. **애플리케이션 성능** - API 응답 시간, 요청률
3. **데이터베이스** - PostgreSQL 성능 메트릭
4. **캐시** - Redis 성능 및 사용률
5. **컨테이너** - Docker 컨테이너 리소스
6. **알림 현황** - 발생한 알림 이력

### 3. AlertManager (알림 관리)

**기능**:
- 알림 그룹화 및 라우팅
- 알림 억제 및 침묵
- 다중 채널 알림 (Email, Slack)
- 알림 템플릿 관리

**알림 심각도**:
- 🔴 **Critical**: 즉시 조치 필요 (5분마다 반복)
- 🟡 **Warning**: 모니터링 필요 (1시간마다 반복)
- 🔵 **Info**: 정보성 알림

### 4. Exporters

#### Node Exporter
- CPU, 메모리, 디스크, 네트워크 메트릭
- 포트: 9100

#### cAdvisor
- 컨테이너 리소스 사용량
- 포트: 8080

#### PostgreSQL Exporter
- 데이터베이스 연결, 쿼리 성능
- 포트: 9187

#### Redis Exporter
- 캐시 성능, 메모리 사용량
- 포트: 9121

## ⚠️ 알림 규칙

### 시스템 알림

| 알림 | 조건 | 심각도 |
|------|------|--------|
| HighCPUUsage | CPU > 80% (5분) | Warning |
| HighMemoryUsage | 메모리 > 85% (5분) | Warning |
| LowDiskSpace | 디스크 < 15% (5분) | Critical |

### 컨테이너 알림

| 알림 | 조건 | 심각도 |
|------|------|--------|
| ContainerDown | 컨테이너 다운 (2분) | Critical |
| ContainerRestarting | 빈번한 재시작 (5분) | Warning |
| ContainerHighMemory | 메모리 > 90% (5분) | Warning |

### 데이터베이스 알림

| 알림 | 조건 | 심각도 |
|------|------|--------|
| PostgreSQLDown | DB 다운 (1분) | Critical |
| PostgreSQLTooManyConnections | 연결 > 80개 (5분) | Warning |
| PostgreSQLSlowQueries | 쿼리 > 1초 (5분) | Warning |
| RedisDown | Redis 다운 (1분) | Critical |
| RedisHighMemory | 메모리 > 90% (5분) | Warning |

### 애플리케이션 알림

| 알림 | 조건 | 심각도 |
|------|------|--------|
| High5xxErrorRate | 5xx 에러 > 5% (5분) | Critical |
| HighResponseTime | 응답 시간 > 1초 (P95, 5분) | Warning |
| LowRequestThroughput | RPS < 10 (10분) | Warning |

## 🔧 설정 커스터마이징

### Prometheus 설정 수정

```bash
# prometheus.yml 편집
vim infrastructure/monitoring/prometheus/prometheus.yml

# 설정 리로드 (재시작 없이)
curl -X POST http://localhost:9090/-/reload
```

### 알림 규칙 추가

```bash
# alerts.yml 편집
vim infrastructure/monitoring/prometheus/rules/alerts.yml

# 규칙 검증
promtool check rules infrastructure/monitoring/prometheus/rules/alerts.yml

# 설정 리로드
curl -X POST http://localhost:9090/-/reload
```

### AlertManager 설정

```bash
# alertmanager.yml 편집
vim infrastructure/monitoring/alertmanager/alertmanager.yml

# 설정 검증
amtool check-config infrastructure/monitoring/alertmanager/alertmanager.yml

# 설정 리로드
curl -X POST http://localhost:9093/-/reload
```

## 📧 알림 채널 설정

### Email 설정

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@coldchain-system.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'
```

### Slack 설정

1. Slack Incoming Webhook 생성
2. alertmanager.yml에 웹훅 URL 추가:

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

receivers:
  - name: 'slack-critical'
    slack_configs:
      - channel: '#alerts-critical'
        username: 'AlertManager'
        icon_emoji: ':fire:'
```

## 🎨 Grafana 대시보드 생성

### 1. 기본 대시보드 import

```bash
# Grafana UI에서:
# 1. + → Import → Upload JSON
# 2. infrastructure/monitoring/grafana/dashboards/*.json 선택
```

### 2. 커스텀 대시보드 생성

```
1. Grafana 접속 (http://localhost:3001)
2. + → Dashboard
3. Add panel
4. Prometheus 데이터소스 선택
5. PromQL 쿼리 작성
6. 시각화 타입 선택
7. Save dashboard
```

### 유용한 PromQL 쿼리

```promql
# CPU 사용률
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 메모리 사용률
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# HTTP 요청률
rate(http_requests_total[5m])

# HTTP 응답 시간 (P95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 데이터베이스 연결 수
pg_stat_activity_count

# Redis 메모리 사용률
(redis_memory_used_bytes / redis_memory_max_bytes) * 100
```

## 🔍 트러블슈팅

### Prometheus 메트릭이 수집되지 않음

```bash
# 타겟 상태 확인
curl http://localhost:9090/api/v1/targets

# 특정 job 상태 확인
curl 'http://localhost:9090/api/v1/targets?state=down'

# 서비스 접근 가능 여부 확인
curl http://backend:8000/metrics
```

### AlertManager 알림이 전송되지 않음

```bash
# AlertManager 로그 확인
docker logs coldchain-alertmanager

# 알림 상태 확인
curl http://localhost:9093/api/v2/alerts

# 설정 검증
amtool config routes test --config.file=alertmanager.yml
```

### Grafana 대시보드가 표시되지 않음

```bash
# Grafana 로그 확인
docker logs coldchain-grafana

# 데이터소스 연결 테스트
# Grafana UI → Configuration → Data Sources → Test

# 플러그인 설치
docker exec coldchain-grafana grafana-cli plugins install redis-datasource
docker restart coldchain-grafana
```

## 📊 모니터링 베스트 프랙티스

### 1. 알림 피로도 방지
- 중요한 알림만 설정
- 적절한 임계값 설정
- 알림 그룹화 및 억제 활용

### 2. 대시보드 구성
- 계층적 대시보드 구조 (개요 → 상세)
- 핵심 메트릭 우선 표시
- 시간 범위 선택 옵션 제공

### 3. 데이터 보관
- 핫 데이터: Prometheus (30일)
- 콜드 데이터: 장기 저장소로 이동 (선택)

### 4. 성능 최적화
- 불필요한 레이블 제거
- 스크랩 간격 조정
- 쿼리 최적화

## 🔒 보안 고려사항

### 1. 접근 제어
```yaml
# Grafana - 인증 설정
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=강력한비밀번호
GF_AUTH_ANONYMOUS_ENABLED=false
```

### 2. TLS/SSL 설정
```yaml
# Prometheus - TLS 설정
tls_config:
  cert_file: /etc/prometheus/cert.pem
  key_file: /etc/prometheus/key.pem
```

### 3. 민감 정보 보호
- 환경 변수로 비밀번호 관리
- Secret 데이터는 암호화하여 저장

## 📚 추가 리소스

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)

---

**문서 버전**: 1.0.0  
**최종 업데이트**: 2026-01-28
