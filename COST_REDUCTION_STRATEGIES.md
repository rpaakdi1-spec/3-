# 💰 AWS 비용 절감 전략

**작성일**: 2026-01-28  
**현재 예상 비용**: $300-460/월  
**목표**: **$50-150/월로 절감 (최대 90% 절감)**

---

## 📊 현재 비용 구조

### 권장 구성 ($320/월)
```yaml
ECS Fargate: $108 (3 Tasks, 1vCPU, 2GB)
RDS PostgreSQL: $90 (db.t3.medium)
ElastiCache Redis: $66 (cache.t3.medium)
ALB: $16
NAT Gateway: $24
S3 + ECR + CloudWatch: $16
──────────────────────
Total: $320/월
```

---

## 🎯 비용 절감 전략 (3가지 시나리오)

## ✅ 시나리오 1: 극단적 절감 (~$0-20/월, 90%+ 절감)

### 📍 VPS/저렴한 클라우드 활용

#### 옵션 A: Oracle Cloud Free Tier (완전 무료!)
```yaml
비용: $0/월 (영구 무료)

무료 제공 리소스:
  - VM.Standard.E2.1.Micro (2 vCPU, 1GB RAM) x2
  - Block Storage: 200GB
  - Object Storage: 20GB
  - Outbound Traffic: 10TB/월

배포 방법:
  1. 2개 VM:
     - VM1: Backend + PostgreSQL + Redis
     - VM2: Frontend (Nginx)
  2. Docker Compose 사용
  3. Let's Encrypt SSL

장점:
  ✅ 완전 무료 (영구)
  ✅ 충분한 성능 (중소 규모)
  ✅ 기존 Docker 설정 그대로 사용

단점:
  ⚠️ 수동 관리 필요
  ⚠️ 자동 스케일링 없음
  ⚠️ 지역 제한 (Seoul 없음)
```

#### 옵션 B: Contabo VPS ($6.99/월)
```yaml
비용: $6.99/월 (약 $7/월)

제공 스펙:
  - 4 vCPU
  - 8GB RAM
  - 200GB NVMe SSD
  - Unlimited Traffic
  - 서울 데이터센터 가능

배포 방법:
  - Docker Compose로 전체 스택
  - PostgreSQL + Redis 포함
  - Nginx reverse proxy

장점:
  ✅ 매우 저렴 ($7/월)
  ✅ 높은 성능 (8GB RAM)
  ✅ 무제한 트래픽
  ✅ 서울 가능

단점:
  ⚠️ 수동 백업 필요
  ⚠️ 자동 스케일링 없음
```

#### 옵션 C: Hetzner Cloud ($4.90/월)
```yaml
비용: €4.49/월 (약 $4.90/월)

제공 스펙:
  - 2 vCPU (Intel/AMD)
  - 4GB RAM
  - 40GB SSD
  - 20TB Traffic

배포 방법:
  - Docker Compose
  - 단일 서버 배포

장점:
  ✅ 극도로 저렴
  ✅ 우수한 성능/가격비
  ✅ 유럽 데이터센터 (빠름)

단점:
  ⚠️ 한국 데이터센터 없음
  ⚠️ 영어 지원
```

### 📊 시나리오 1 비교
| 옵션 | 월 비용 | 성능 | 지역 | 관리 |
|------|---------|------|------|------|
| Oracle Free | $0 | ⭐⭐⭐ | 🌍 | 수동 |
| Contabo | $7 | ⭐⭐⭐⭐ | 🇰🇷 | 수동 |
| Hetzner | $5 | ⭐⭐⭐⭐ | 🇪🇺 | 수동 |

**권장**: Oracle Cloud (완전 무료) 또는 Contabo (서울)

---

## ✅ 시나리오 2: AWS 최적화 (~$50-80/월, 75% 절감)

### 🎯 Lightsail + RDS 조합

```yaml
비용: $55-80/월

구성:
  Lightsail Instance: $20/월
    - 2 vCPU
    - 4GB RAM
    - 80GB SSD
    - 4TB Transfer
    - 배포: Backend + Frontend + Redis
  
  RDS PostgreSQL: $25/월
    - db.t3.micro (2 vCPU, 1GB)
    - Single-AZ
    - 20GB Storage
  
  Backup + Monitoring: $10/월

Total: $55/월
```

#### 배포 방법
```bash
# 1. Lightsail 인스턴스 생성
aws lightsail create-instances \
  --instance-names coldchain-app \
  --blueprint-id ubuntu_22_04 \
  --bundle-id medium_2_0

# 2. Docker 설치 및 배포
ssh ubuntu@<lightsail-ip>
curl -fsSL https://get.docker.com | sh
docker-compose -f docker-compose.prod.yml up -d

# 3. RDS 생성 (최소 스펙)
aws rds create-db-instance \
  --db-instance-identifier coldchain-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --allocated-storage 20
```

### 📊 비용 상세
```yaml
Lightsail: $20 (4GB, 2 vCPU)
RDS: $25 (db.t3.micro)
Backup: $5
Monitoring: $5
──────────────────
Total: $55/월

절감액: $265/월 (83% 절감)
```

---

## ✅ 시나리오 3: AWS 스마트 최적화 (~$100-150/월, 50% 절감)

### 🔧 최적화 포인트

#### 1. Spot Instances 활용 (70% 절감)
```yaml
현재 ECS Fargate: $108/월
→ EC2 Spot Instances: $32/월

설정:
  - ECS on EC2 (Spot)
  - t3a.medium Spot (2 vCPU, 4GB)
  - Auto Scaling Group
  - Spot Fleet 설정

절감: $76/월
```

#### 2. Aurora Serverless v2 (50% 절감)
```yaml
현재 RDS: $90/월
→ Aurora Serverless v2: $45/월

설정:
  - Min: 0.5 ACU (1GB RAM)
  - Max: 2 ACU (4GB RAM)
  - 자동 스케일링
  - 사용량 기반 과금

절감: $45/월
```

#### 3. ElastiCache → Redis on EC2 (100% 절감)
```yaml
현재 ElastiCache: $66/월
→ Redis on ECS: $0 (ECS 리소스 공유)

설정:
  - ECS Task에 Redis 컨테이너 추가
  - Persistent Volume (EFS)
  - 메모리 제한 512MB

절감: $66/월
```

#### 4. NAT Gateway → NAT Instance (75% 절감)
```yaml
현재 NAT Gateway: $24/월
→ NAT Instance (t4g.nano): $6/월

설정:
  - t4g.nano (ARM, 512MB)
  - NAT 전용 인스턴스
  - Elastic IP

절감: $18/월
```

#### 5. CloudWatch Logs 최적화 (50% 절감)
```yaml
현재 CloudWatch: $15/월
→ 최적화된 CloudWatch: $7/월

최적화:
  - 로그 보관 기간: 30일 → 7일
  - 필터링으로 중요 로그만
  - S3로 아카이브

절감: $8/월
```

### 📊 시나리오 3 총계
```yaml
비용 항목별:
  ECS (Spot): $32 (was $108)
  Aurora Serverless: $45 (was $90)
  Redis on ECS: $0 (was $66)
  ALB: $16 (유지)
  NAT Instance: $6 (was $24)
  S3 + ECR: $10 (유지)
  CloudWatch: $7 (was $15)
─────────────────────────
Total: $116/월 (was $320)

절감액: $204/월 (64% 절감)
```

---

## 🚀 구현 가이드

### 시나리오 1: Oracle Cloud Free (추천!)

#### 1. Oracle Cloud 가입
```bash
# 1. Oracle Cloud 계정 생성
https://www.oracle.com/cloud/free/

# 2. 무료 티어 VM 2개 생성
- VM1: Ubuntu 22.04 (Backend + DB)
- VM2: Ubuntu 22.04 (Frontend)

# 3. 방화벽 설정
- 80, 443 (HTTP/HTTPS)
- 22 (SSH)
```

#### 2. 배포 스크립트
```bash
# VM1: Backend + PostgreSQL + Redis
#!/bin/bash
# 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 프로젝트 클론
git clone https://github.com/rpaakdi1-spec/3-.git
cd 3-

# 환경 변수 설정
cp .env.example .env
vi .env

# 배포
docker-compose -f docker-compose.prod.yml up -d

# SSL 인증서 (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

#### 3. 모니터링 설정
```bash
# 무료 모니터링 도구
docker run -d \
  --name=netdata \
  -p 19999:19999 \
  netdata/netdata

# Uptime 모니터링 (무료)
https://uptimerobot.com
```

### 시나리오 2: AWS Lightsail

#### Terraform 설정
```hcl
# lightsail.tf
resource "aws_lightsail_instance" "app" {
  name              = "coldchain-app"
  availability_zone = "ap-northeast-2a"
  blueprint_id      = "ubuntu_22_04"
  bundle_id         = "medium_2_0"  # $20/month

  user_data = <<-EOF
    #!/bin/bash
    curl -fsSL https://get.docker.com | sh
    git clone https://github.com/rpaakdi1-spec/3-.git /opt/app
    cd /opt/app
    docker-compose -f docker-compose.prod.yml up -d
  EOF
}

resource "aws_lightsail_static_ip" "app" {
  name = "coldchain-static-ip"
}

resource "aws_lightsail_static_ip_attachment" "app" {
  static_ip_name = aws_lightsail_static_ip.app.name
  instance_name  = aws_lightsail_instance.app.name
}

resource "aws_db_instance" "main" {
  identifier             = "coldchain-db"
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = "db.t3.micro"  # $25/month
  allocated_storage      = 20
  storage_type           = "gp2"
  db_name                = "coldchain"
  username               = "admin"
  password               = var.db_password
  skip_final_snapshot    = true
  backup_retention_period = 7
}
```

### 시나리오 3: AWS 스마트 최적화

#### ECS Spot Instances 설정
```hcl
# ecs_spot.tf
resource "aws_launch_template" "ecs_spot" {
  name_prefix   = "ecs-spot-"
  image_id      = data.aws_ami.ecs_optimized.id
  instance_type = "t3a.medium"

  instance_market_options {
    market_type = "spot"
    spot_options {
      max_price = "0.04"  # 70% 할인
    }
  }

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs.name
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    echo ECS_CLUSTER=${aws_ecs_cluster.main.name} >> /etc/ecs/ecs.config
    echo ECS_ENABLE_SPOT_INSTANCE_DRAINING=true >> /etc/ecs/ecs.config
  EOF
  )
}

resource "aws_autoscaling_group" "ecs_spot" {
  name                = "ecs-spot-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  min_size            = 1
  max_size            = 3
  desired_capacity    = 1

  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.ecs_spot.id
      }
    }

    instances_distribution {
      on_demand_percentage_above_base_capacity = 0
      spot_allocation_strategy                 = "lowest-price"
    }
  }
}
```

#### Aurora Serverless v2 설정
```hcl
# aurora_serverless.tf
resource "aws_rds_cluster" "main" {
  cluster_identifier      = "coldchain-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.3"
  database_name           = "coldchain"
  master_username         = "admin"
  master_password         = var.db_password
  
  serverlessv2_scaling_configuration {
    min_capacity = 0.5  # 1GB RAM
    max_capacity = 2    # 4GB RAM
  }

  skip_final_snapshot = true
}

resource "aws_rds_cluster_instance" "main" {
  identifier         = "coldchain-instance"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.main.engine
}
```

---

## 📊 비용 비교표

| 시나리오 | 월 비용 | 절감율 | 성능 | 관리 난이도 | 추천도 |
|----------|---------|--------|------|-------------|--------|
| **현재 (AWS 표준)** | $320 | - | ⭐⭐⭐⭐⭐ | 낮음 | - |
| **1. Oracle Free** | **$0** | **100%** | ⭐⭐⭐ | 중간 | ⭐⭐⭐⭐⭐ |
| **1. Contabo** | **$7** | **98%** | ⭐⭐⭐⭐ | 중간 | ⭐⭐⭐⭐⭐ |
| **1. Hetzner** | **$5** | **98%** | ⭐⭐⭐⭐ | 중간 | ⭐⭐⭐⭐ |
| **2. Lightsail** | **$55** | **83%** | ⭐⭐⭐⭐ | 낮음 | ⭐⭐⭐⭐ |
| **3. AWS 최적화** | **$116** | **64%** | ⭐⭐⭐⭐⭐ | 낮음 | ⭐⭐⭐ |

---

## 🎯 권장 사항

### 🥇 1순위: Oracle Cloud Free (완전 무료!)
```yaml
비용: $0/월
절감: 100% ($320 절감)
용도: 중소 규모 운영 (초기)

장점:
  ✅ 완전 무료 (영구)
  ✅ 충분한 성능
  ✅ 기존 Docker 활용

시작:
  1. Oracle Cloud 가입
  2. VM 2개 생성
  3. Docker Compose 배포
  4. Let's Encrypt SSL
```

### 🥈 2순위: Contabo VPS ($7/월)
```yaml
비용: $7/월
절감: 98% ($313 절감)
용도: 중규모 운영 (한국)

장점:
  ✅ 매우 저렴
  ✅ 높은 성능 (8GB RAM)
  ✅ 서울 데이터센터
  ✅ 무제한 트래픽

시작:
  1. Contabo 가입
  2. Seoul VPS 구매
  3. Docker Compose 배포
```

### 🥉 3순위: AWS Lightsail ($55/월)
```yaml
비용: $55/월
절감: 83% ($265 절감)
용도: AWS 생태계 활용

장점:
  ✅ AWS 통합
  ✅ 고정 가격
  ✅ 간단한 관리
  ✅ RDS 연동

시작:
  1. Lightsail 인스턴스 생성
  2. RDS micro 추가
  3. Terraform 배포
```

---

## 💡 추가 절감 팁

### 1. CDN 무료 활용
```yaml
Cloudflare Free:
  - Unlimited Bandwidth
  - DDoS Protection
  - SSL Certificate
  - CDN (전세계)

절감: $20-50/월 (트래픽 비용)
```

### 2. 모니터링 무료 도구
```yaml
무료 도구:
  - Uptime Robot (모니터링)
  - Netdata (시스템 메트릭)
  - Grafana Cloud Free (대시보드)
  - Sentry Free (에러 추적)

절감: $20-30/월
```

### 3. 백업 최적화
```yaml
백업 전략:
  - 데이터베이스: Daily → Weekly
  - S3 Lifecycle: 30일 후 Glacier
  - 로그: 7일 보관

절감: $10-15/월
```

### 4. 예약 인스턴스 (장기)
```yaml
AWS Reserved Instances (1년):
  - 40% 할인
  - 3년: 60% 할인

적용 시 비용:
  $320 → $192/월 (40% 할인)
```

---

## 🎉 최종 권장 시나리오

### 초기 단계 (0-6개월)
```yaml
Platform: Oracle Cloud Free
비용: $0/월
이유: 완전 무료로 시작, 검증
```

### 성장 단계 (6개월-1년)
```yaml
Platform: Contabo VPS
비용: $7-14/월 (서버 1-2대)
이유: 저렴 + 높은 성능
```

### 확장 단계 (1년+)
```yaml
Platform: AWS Lightsail + RDS
비용: $55-100/월
이유: 안정성 + 자동 백업
```

### 대규모 단계 (2년+)
```yaml
Platform: AWS 최적화 (Spot + Serverless)
비용: $100-150/월
이유: 자동 스케일링 + 고가용성
```

---

## 📞 구현 지원

### 즉시 시작 가능
```bash
# Oracle Cloud Free 배포
1. https://www.oracle.com/cloud/free/ 가입
2. VM 생성 (Ubuntu 22.04)
3. 기존 docker-compose.prod.yml 사용
4. 완료!

예상 시간: 30분
비용: $0/월
절감: $320/월 (100%)
```

---

**작성일**: 2026-01-28  
**최종 권장**: Oracle Cloud Free ($0/월) 또는 Contabo ($7/월)  
**최대 절감**: **$320/월 → $0-7/월 (98-100% 절감!)**
