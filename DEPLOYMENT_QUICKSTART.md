# 🚀 배포 퀵스타트 가이드

UVIS GPS Fleet Management System을 프로덕션 환경에 배포하기 위한 빠른 시작 가이드입니다.

---

## ⚡ 빠른 배포 (10분)

### 전제 조건
```bash
# 필수 도구
- AWS CLI configured
- Docker installed
- Terraform installed
- Git installed
```

### 1단계: 저장소 클론
```bash
git clone https://github.com/rpaakdi1-spec/3-.git
cd 3-
```

### 2단계: AWS 자격 증명 설정
```bash
# AWS CLI 설정
aws configure

# 확인
aws sts get-caller-identity
```

### 3단계: 환경 변수 설정
```bash
# Terraform 변수 파일 생성
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars

# 편집 (도메인, 리전 등)
vi terraform.tfvars
```

### 4단계: 원클릭 배포
```bash
# 배포 스크립트 실행
cd ../../
chmod +x infrastructure/scripts/production-deploy.sh
./infrastructure/scripts/production-deploy.sh
```

**완료!** 약 30-45분 후 시스템이 실행됩니다.

---

## 📋 상세 배포 단계

### Phase 1: 인프라 구축 (Terraform)

```bash
cd infrastructure/terraform

# 초기화
terraform init

# 계획 확인
terraform plan

# 배포 실행
terraform apply
```

**생성되는 리소스:**
- VPC (2 AZs)
- ECS Fargate Cluster
- RDS PostgreSQL
- ElastiCache Redis
- Application Load Balancer
- S3 Buckets
- ECR Repositories
- CloudWatch Alarms

**소요 시간:** ~20분

---

### Phase 2: Docker 이미지 빌드

```bash
# Backend 이미지
cd backend
docker build -t coldchain-backend:latest .
docker tag coldchain-backend:latest <ECR_URL>/backend:latest
docker push <ECR_URL>/backend:latest

# Frontend 이미지
cd ../frontend
docker build -t coldchain-frontend:latest .
docker tag coldchain-frontend:latest <ECR_URL>/frontend:latest
docker push <ECR_URL>/frontend:latest
```

**소요 시간:** ~10분

---

### Phase 3: 데이터베이스 초기화

```bash
# 마이그레이션 실행
cd backend
alembic upgrade head

# 초기 데이터 로드 (선택사항)
python scripts/seed_data.py
```

**소요 시간:** ~5분

---

### Phase 4: ECS 서비스 배포

```bash
# Task Definition 등록
aws ecs register-task-definition \
  --cli-input-json file://task-definition-backend.json

# 서비스 생성
aws ecs create-service \
  --cluster coldchain-cluster \
  --service-name backend \
  --task-definition backend:1 \
  --desired-count 2 \
  --launch-type FARGATE
```

**소요 시간:** ~10분

---

### Phase 5: 모니터링 설정

```bash
# Prometheus & Grafana
cd monitoring
docker-compose up -d

# 대시보드 Import
# Grafana UI: http://localhost:3000
# Username: admin, Password: admin
```

**소요 시간:** ~5분

---

### Phase 6: 헬스 체크 & 검증

```bash
# ALB DNS 확인
ALB_DNS=$(terraform output alb_dns_name)

# Health check
curl http://$ALB_DNS/health

# API 테스트
curl http://$ALB_DNS/api/v1/health
```

**소요 시간:** ~5분

---

## 🔧 환경별 배포

### 개발 환경 (Local)

```bash
# Docker Compose
docker-compose up -d

# 접속
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Docs: http://localhost:8000/docs
```

### 스테이징 환경

```bash
# 환경 변수 설정
export ENVIRONMENT=staging

# Terraform workspace
terraform workspace new staging
terraform workspace select staging

# 배포
terraform apply -var-file=staging.tfvars
```

### 프로덕션 환경

```bash
# 환경 변수 설정
export ENVIRONMENT=production

# Terraform workspace
terraform workspace new production
terraform workspace select production

# 배포 (승인 필요)
terraform apply -var-file=production.tfvars
```

---

## 📊 배포 후 체크리스트

### 필수 확인 사항

- [ ] **Health Check** ✅
  ```bash
  curl https://your-domain.com/health
  # Expected: {"status": "healthy"}
  ```

- [ ] **Database Connection** ✅
  ```bash
  curl https://your-domain.com/api/v1/health
  # Expected: {"database": "connected"}
  ```

- [ ] **Cache Connection** ✅
  ```bash
  # Redis ping
  redis-cli -h <redis-host> ping
  # Expected: PONG
  ```

- [ ] **SSL Certificate** ✅
  ```bash
  curl -I https://your-domain.com
  # Check for "HTTP/2 200"
  ```

- [ ] **Monitoring** ✅
  - Prometheus: http://prometheus.your-domain.com
  - Grafana: http://grafana.your-domain.com
  - Kibana: http://kibana.your-domain.com

- [ ] **Backup** ✅
  ```bash
  # RDS 스냅샷 확인
  aws rds describe-db-snapshots \
    --db-instance-identifier coldchain-prod
  ```

- [ ] **Logs** ✅
  ```bash
  # CloudWatch Logs
  aws logs tail /ecs/backend --follow
  ```

---

## 🔒 보안 설정

### SSL/TLS 인증서

```bash
# AWS Certificate Manager
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS \
  --subject-alternative-names *.your-domain.com
```

### Secrets 설정

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name coldchain/production/database \
  --secret-string '{"username":"admin","password":"..."}'
```

### IAM 역할

```bash
# ECS Task Execution Role 확인
aws iam get-role --role-name ecsTaskExecutionRole
```

---

## 📈 스케일링

### Auto Scaling 설정

```bash
# Target Tracking Policy
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/coldchain-cluster/backend \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --policy-name cpu75-target-tracking-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/coldchain-cluster/backend \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    "TargetValue=75.0,PredefinedMetricSpecification={PredefinedMetricType=ECSServiceAverageCPUUtilization}"
```

### 수동 스케일링

```bash
# 즉시 스케일 업
aws ecs update-service \
  --cluster coldchain-cluster \
  --service backend \
  --desired-count 5
```

---

## 🚨 롤백 절차

### 빠른 롤백

```bash
# 이전 Task Definition으로 복구
aws ecs update-service \
  --cluster coldchain-cluster \
  --service backend \
  --task-definition backend:PREVIOUS_VERSION

# 확인
aws ecs describe-services \
  --cluster coldchain-cluster \
  --services backend
```

### Terraform 롤백

```bash
# 이전 상태로 복원
terraform show -json > current-state.json
terraform state pull > previous-state.tfstate
terraform apply -state=previous-state.tfstate
```

---

## 📞 트러블슈팅

### 일반적인 문제

#### 1. Task가 시작되지 않음

```bash
# 로그 확인
aws ecs describe-tasks \
  --cluster coldchain-cluster \
  --tasks <task-id>

# CloudWatch Logs
aws logs tail /ecs/backend --follow
```

**해결책:**
- Task Definition 확인
- IAM 역할 권한 확인
- 이미지 Pull 가능 여부 확인

#### 2. Database 연결 실패

```bash
# Security Group 확인
aws ec2 describe-security-groups \
  --group-ids <sg-id>

# RDS 상태 확인
aws rds describe-db-instances \
  --db-instance-identifier coldchain-prod
```

**해결책:**
- Security Group Ingress 규칙 추가
- Database 엔드포인트 확인
- 비밀번호 검증

#### 3. 느린 응답 시간

```bash
# CloudWatch 메트릭 확인
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=backend \
  --start-time 2026-01-28T00:00:00Z \
  --end-time 2026-01-28T23:59:59Z \
  --period 3600 \
  --statistics Average
```

**해결책:**
- Task 수 증가
- Task 크기 증가 (CPU/Memory)
- Redis 캐싱 확인

---

## 📚 추가 자료

### 상세 문서
- [프로덕션 배포 가이드](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [운영 매뉴얼](docs/OPERATIONS_GUIDE.md)
- [트러블슈팅 가이드](docs/TROUBLESHOOTING.md)
- [보안 가이드](docs/SECURITY_GUIDE.md)

### 도구 & 대시보드
- **Grafana**: http://grafana.your-domain.com
- **Prometheus**: http://prometheus.your-domain.com
- **Kibana**: http://kibana.your-domain.com
- **API Docs**: https://your-domain.com/docs

### 지원
- **Email**: devops@example.com
- **Slack**: #coldchain-ops
- **On-call**: +82-10-XXXX-XXXX

---

## ✅ 배포 완료 확인

배포가 성공적으로 완료되었다면:

- ✅ Health check 통과
- ✅ API 응답 정상
- ✅ Frontend 로딩 정상
- ✅ Database 연결 정상
- ✅ Redis 연결 정상
- ✅ 모니터링 대시보드 작동
- ✅ 로그 수집 정상
- ✅ SSL 인증서 유효
- ✅ 백업 스케줄 작동
- ✅ 알림 규칙 작동

**축하합니다! 🎉 시스템이 프로덕션에서 실행 중입니다.**

---

**업데이트**: 2026-01-28  
**버전**: 1.0.0  
**상태**: 프로덕션 준비 완료 ✅
