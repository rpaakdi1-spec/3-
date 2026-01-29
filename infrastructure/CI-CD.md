# CI/CD 파이프라인 설정 가이드

## 📋 개요

이 문서는 Cold Chain Dispatch System의 CI/CD 파이프라인 설정 방법을 설명합니다.

## 🔧 GitHub Actions 워크플로우

### 1. 자동 배포 (deploy.yml)

**트리거**:
- `main` 브랜치에 push
- 수동 실행 (workflow_dispatch)

**기능**:
- 변경사항 자동 감지 (backend/frontend/infrastructure)
- Docker 이미지 빌드 및 ECR 푸시
- ECS 태스크 정의 업데이트
- ECS 서비스 배포
- 헬스 체크
- Slack 알림

**필요한 Secrets**:
```
AWS_ACCESS_KEY_ID          # AWS 액세스 키
AWS_SECRET_ACCESS_KEY      # AWS 시크릿 키
VITE_API_BASE_URL          # Frontend API URL
SLACK_WEBHOOK_URL          # Slack 웹훅 URL (선택)
```

### 2. 데이터베이스 마이그레이션 (migration.yml)

**트리거**:
- 수동 실행만 (workflow_dispatch)

**기능**:
- 마이그레이션 전 자동 백업
- Alembic 마이그레이션 실행
- 마이그레이션 검증
- Slack 알림

**사용법**:
1. GitHub Actions 탭으로 이동
2. "Database Migration" 워크플로우 선택
3. "Run workflow" 클릭
4. 옵션 선택:
   - Direction: upgrade/downgrade
   - Revision: 대상 리비전 (비워두면 head)

### 3. 롤백 (rollback.yml)

**트리거**:
- 수동 실행만 (workflow_dispatch)

**기능**:
- 이전 태스크 정의로 롤백
- Backend/Frontend 개별 또는 동시 롤백
- 자동 헬스 체크
- Slack 알림

**사용법**:
1. GitHub Actions 탭으로 이동
2. "Rollback Deployment" 워크플로우 선택
3. "Run workflow" 클릭
4. 옵션 선택:
   - Service: backend/frontend/both
   - Task Definition Revision: 특정 리비전 (비워두면 이전 버전)

## 🚀 GitHub Secrets 설정

### 1. AWS Credentials

AWS IAM 사용자 생성 및 권한 부여:

```bash
# IAM 사용자 생성
aws iam create-user --user-name github-actions-coldchain

# 정책 연결
aws iam attach-user-policy \
  --user-name github-actions-coldchain \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

aws iam attach-user-policy \
  --user-name github-actions-coldchain \
  --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess

# 액세스 키 생성
aws iam create-access-key --user-name github-actions-coldchain
```

생성된 액세스 키를 GitHub Secrets에 추가:

1. Repository Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. 다음 Secrets 추가:
   - `AWS_ACCESS_KEY_ID`: IAM 액세스 키 ID
   - `AWS_SECRET_ACCESS_KEY`: IAM 시크릿 액세스 키

### 2. Application Secrets

```
VITE_API_BASE_URL=https://your-domain.com/api
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 📦 수동 배포

GitHub Actions를 사용하지 않고 로컬에서 배포:

### 사전 요구사항

```bash
# AWS CLI 설치 및 구성
aws configure

# Docker 설치
# https://docs.docker.com/get-docker/

# 환경 변수 설정
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=ap-northeast-2
export ECS_CLUSTER=coldchain-production-cluster
```

### 배포 실행

```bash
# 배포 스크립트 실행
./infrastructure/scripts/deploy.sh

# 대화형 프롬프트에 응답:
# 1. 배포할 서비스 선택 (Backend/Frontend/Both)
# 2. 이미지 태그 입력 (기본값: latest)
# 3. 배포 확인
```

## 🔄 배포 프로세스

### 자동 배포 흐름

```
┌─────────────────┐
│  Git Push       │
│  to main        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Detect Changes  │
│ (paths-filter)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│Backend │ │Frontend  │
│Build   │ │Build     │
└───┬────┘ └────┬─────┘
    │           │
    ▼           ▼
┌────────┐ ┌──────────┐
│ECR Push│ │ECR Push  │
└───┬────┘ └────┬─────┘
    │           │
    ▼           ▼
┌────────┐ ┌──────────┐
│ECS     │ │ECS       │
│Deploy  │ │Deploy    │
└───┬────┘ └────┬─────┘
    │           │
    └─────┬─────┘
          ▼
    ┌──────────┐
    │Health    │
    │Check     │
    └─────┬────┘
          │
          ▼
    ┌──────────┐
    │Slack     │
    │Notify    │
    └──────────┘
```

### 배포 시간

| 단계 | 예상 시간 |
|------|----------|
| Docker 이미지 빌드 | 3-5분 |
| ECR 푸시 | 1-2분 |
| ECS 태스크 정의 업데이트 | 10초 |
| ECS 서비스 배포 | 5-10분 |
| **총 배포 시간** | **10-20분** |

## 🔍 모니터링 및 로그

### 배포 상태 확인

```bash
# ECS 서비스 상태
aws ecs describe-services \
  --cluster coldchain-production-cluster \
  --services coldchain-production-backend coldchain-production-frontend

# 최근 배포 이벤트
aws ecs describe-services \
  --cluster coldchain-production-cluster \
  --services coldchain-production-backend \
  --query 'services[0].events[:5]'

# 실행 중인 태스크
aws ecs list-tasks \
  --cluster coldchain-production-cluster \
  --service-name coldchain-production-backend
```

### CloudWatch 로그

```bash
# Backend 로그
aws logs tail /ecs/coldchain-production/backend --follow

# Frontend 로그
aws logs tail /ecs/coldchain-production/frontend --follow
```

## 🚨 트러블슈팅

### 배포 실패

**증상**: ECS 서비스가 안정화되지 않음

**해결 방법**:
1. CloudWatch 로그 확인
2. ECS 태스크 이벤트 확인
3. 보안 그룹 및 IAM 역할 확인
4. 롤백 실행

```bash
# 서비스 이벤트 확인
aws ecs describe-services \
  --cluster coldchain-production-cluster \
  --services coldchain-production-backend \
  --query 'services[0].events[:10]'

# 실패한 태스크 로그 확인
TASK_ARN=$(aws ecs list-tasks \
  --cluster coldchain-production-cluster \
  --service-name coldchain-production-backend \
  --desired-status STOPPED \
  --query 'taskArns[0]' \
  --output text)

aws ecs describe-tasks \
  --cluster coldchain-production-cluster \
  --tasks $TASK_ARN
```

### 헬스 체크 실패

**증상**: 배포는 성공했지만 헬스 체크 실패

**해결 방법**:
1. ALB 대상 그룹 상태 확인
2. 보안 그룹 규칙 확인
3. 애플리케이션 로그 확인

```bash
# ALB 대상 상태
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# 보안 그룹 규칙 확인
aws ec2 describe-security-groups \
  --group-ids sg-xxxxx
```

### 롤백이 필요한 경우

```bash
# GitHub Actions에서 롤백 워크플로우 실행
# 또는 수동으로:

aws ecs update-service \
  --cluster coldchain-production-cluster \
  --service coldchain-production-backend \
  --task-definition coldchain-production-backend:PREVIOUS_REVISION \
  --force-new-deployment
```

## 📊 배포 메트릭

### 추적할 주요 지표

- **배포 빈도**: 주당 배포 횟수
- **배포 성공률**: 성공한 배포 / 전체 배포
- **평균 배포 시간**: 시작부터 안정화까지 시간
- **롤백 빈도**: 배포 후 롤백 횟수
- **MTTR** (Mean Time To Recovery): 평균 복구 시간

### CloudWatch 대시보드

배포 메트릭을 추적하기 위한 CloudWatch 대시보드 생성:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name coldchain-deployment \
  --dashboard-body file://infrastructure/monitoring/deployment-dashboard.json
```

## 🔐 보안 모범 사례

1. **최소 권한 원칙**
   - GitHub Actions 사용자에게 필요한 최소 권한만 부여
   - IAM 정책 정기 검토

2. **Secrets 관리**
   - GitHub Secrets 사용
   - AWS Secrets Manager 통합 고려
   - 정기적인 키 로테이션

3. **이미지 보안**
   - ECR 이미지 스캔 활성화
   - 취약점 발견 시 자동 알림
   - 정기적인 베이스 이미지 업데이트

4. **감사 로깅**
   - 모든 배포 활동 로깅
   - CloudTrail 활성화
   - 정기적인 로그 검토

## 📚 추가 리소스

- [AWS ECS Deployment Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**문서 버전**: 1.0.0  
**최종 업데이트**: 2026-01-28
