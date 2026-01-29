# 🔒 SSL/TLS Configuration and Security Hardening

## Overview

This document covers SSL/TLS certificate setup and comprehensive security hardening for the UVIS GPS Fleet Management System.

## SSL/TLS Certificates

### AWS Certificate Manager (ACM)

#### Request Certificate

```bash
# Request certificate for domain
aws acm request-certificate \
    --domain-name example.com \
    --subject-alternative-names "*.example.com" \
    --validation-method DNS \
    --region ap-northeast-2

# Get certificate ARN
aws acm list-certificates --region ap-northeast-2
```

#### DNS Validation

1. **Get validation records**:
```bash
aws acm describe-certificate \
    --certificate-arn arn:aws:acm:region:account:certificate/xxxxx \
    --region ap-northeast-2
```

2. **Add CNAME records to Route53**:
```bash
aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch file://cert-validation.json
```

cert-validation.json:
```json
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "_validation-token.example.com",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{
        "Value": "validation-value.acm-validations.aws."
      }]
    }
  }]
}
```

### Let's Encrypt (Free Certificates)

#### Using Certbot

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Request certificate
sudo certbot --nginx -d example.com -d www.example.com

# Auto-renewal (add to crontab)
0 0 * * * certbot renew --quiet
```

#### Using Docker Certbot

```bash
# Run Certbot in Docker
docker run -it --rm \
    -v /etc/letsencrypt:/etc/letsencrypt \
    -v /var/lib/letsencrypt:/var/lib/letsencrypt \
    certbot/certbot certonly \
    --standalone \
    -d example.com \
    -d www.example.com \
    --email admin@example.com \
    --agree-tos
```

### Self-Signed Certificates (Development Only)

```bash
# Generate private key
openssl genrsa -out server.key 2048

# Generate certificate signing request
openssl req -new -key server.key -out server.csr

# Generate self-signed certificate
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

# Combine for nginx
cat server.crt server.key > server.pem
```

## Nginx SSL Configuration

### Optimal SSL Configuration

Create `/infrastructure/nginx/ssl.conf`:

```nginx
# SSL/TLS Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';

# SSL Session
ssl_session_cache shared:SSL:50m;
ssl_session_timeout 1d;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# DH Parameters (generate with: openssl dhparam -out dhparam.pem 4096)
ssl_dhparam /etc/nginx/ssl/dhparam.pem;

# Security Headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' wss: https:;" always;
add_header Permissions-Policy "geolocation=(self), microphone=(), camera=()" always;

# Hide Nginx Version
server_tokens off;
```

### Production Nginx Configuration

Update `/home/user/webapp/frontend/nginx.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    
    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com www.example.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    # Include SSL configuration
    include /etc/nginx/ssl.conf;
    
    # Root directory
    root /usr/share/nginx/html;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;
    
    # Client body size limit
    client_max_body_size 100M;
    
    # Timeouts
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Security headers (additional)
    add_header X-Robots-Tag "noindex, nofollow" always;
    
    # API proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket proxy
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }
    
    # Static files with caching
    location /static/ {
        alias /usr/share/nginx/html/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # React Router support
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

## Application Load Balancer (ALB) SSL

### Terraform Configuration

```hcl
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# Additional certificates for multiple domains
resource "aws_lb_listener_certificate" "additional" {
  listener_arn    = aws_lb_listener.https.arn
  certificate_arn = var.additional_certificate_arn
}
```

## Security Hardening

### 1. Operating System Hardening

#### Update System

```bash
# Update packages
sudo apt-get update
sudo apt-get upgrade -y

# Auto-update security patches
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

#### Firewall Configuration

```bash
# Install UFW
sudo apt-get install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow specific IP for admin access
sudo ufw allow from 203.0.113.0/24 to any port 22

# Enable firewall
sudo ufw enable
```

#### Fail2ban

```bash
# Install Fail2ban
sudo apt-get install fail2ban

# Configure
sudo cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22

[nginx-http-auth]
enabled = true
port = http,https

[nginx-noscript]
enabled = true
port = http,https

[nginx-badbots]
enabled = true
port = http,https
EOF

# Restart Fail2ban
sudo systemctl restart fail2ban
```

### 2. Docker Security

#### Docker Daemon Configuration

```json
{
  "log-level": "info",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp-default.json",
  "icc": false,
  "userns-remap": "default"
}
```

#### Docker Compose Security

```yaml
version: '3.8'

services:
  backend:
    image: backend:latest
    # Run as non-root user
    user: "1000:1000"
    # Read-only root filesystem
    read_only: true
    # Drop all capabilities
    cap_drop:
      - ALL
    # No new privileges
    security_opt:
      - no-new-privileges:true
    # Seccomp profile
    security_opt:
      - seccomp:unconfined
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 3. Database Security

#### PostgreSQL Hardening

```sql
-- Change default postgres password
ALTER USER postgres WITH PASSWORD 'very_strong_password_here';

-- Create application user with limited privileges
CREATE USER uvis_app WITH PASSWORD 'app_password_here';
GRANT CONNECT ON DATABASE uvis_gps TO uvis_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO uvis_app;

-- Revoke public schema privileges
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/postgresql/ssl/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/postgresql/ssl/server.key';

-- Configure pg_hba.conf
-- hostssl all all 0.0.0.0/0 md5

-- Restart PostgreSQL
SELECT pg_reload_conf();
```

#### RDS Security

```hcl
resource "aws_db_instance" "main" {
  # ... other configuration ...

  # Encryption
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  # SSL/TLS
  ca_cert_identifier = "rds-ca-2019"

  # Backup encryption
  backup_retention_period = 7
  backup_window          = "03:00-04:00"

  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  # Security group
  vpc_security_group_ids = [aws_security_group.rds.id]

  # Multi-AZ
  multi_az = true

  # Deletion protection
  deletion_protection = true
}
```

### 4. Application Security

#### Environment Variables

```bash
# Never commit secrets to Git
# Use AWS Secrets Manager or Parameter Store

# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name uvis-gps/prod/db-password \
    --secret-string "very_strong_password"

# Retrieve in application
aws secretsmanager get-secret-value \
    --secret-id uvis-gps/prod/db-password \
    --query SecretString \
    --output text
```

#### API Security

Update backend security middleware:

```python
# backend/app/core/security.py

from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt

security = HTTPBearer()

# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",
        "https://www.example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

# Security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

# Request ID middleware
from uuid import uuid4

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### 5. Network Security

#### AWS Security Groups

```hcl
# Backend security group
resource "aws_security_group" "backend" {
  name        = "uvis-gps-backend"
  description = "Security group for backend services"
  vpc_id      = aws_vpc.main.id

  # Allow inbound from ALB only
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow outbound to RDS
  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.rds.id]
  }

  # Allow outbound to Redis
  egress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.redis.id]
  }

  # Allow outbound HTTPS
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "uvis-gps-backend"
  }
}

# RDS security group
resource "aws_security_group" "rds" {
  name        = "uvis-gps-rds"
  description = "Security group for RDS"
  vpc_id      = aws_vpc.main.id

  # Allow inbound from backend only
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  tags = {
    Name = "uvis-gps-rds"
  }
}
```

#### VPC Flow Logs

```hcl
resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id

  tags = {
    Name = "uvis-gps-vpc-flow-logs"
  }
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  name              = "/aws/vpc/uvis-gps"
  retention_in_days = 30
}
```

### 6. Secrets Management

#### AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
    --name uvis-gps/prod/env \
    --secret-string file://secrets.json

# secrets.json
{
  "DB_PASSWORD": "strong_password",
  "JWT_SECRET": "jwt_secret_key",
  "OPENAI_API_KEY": "openai_key",
  "AWS_ACCESS_KEY": "aws_key"
}

# Rotate secret
aws secretsmanager rotate-secret \
    --secret-id uvis-gps/prod/db-password \
    --rotation-lambda-arn arn:aws:lambda:region:account:function:rotate-secret
```

#### ECS Task Definition with Secrets

```hcl
resource "aws_ecs_task_definition" "backend" {
  family = "uvis-gps-backend"
  
  container_definitions = jsonencode([{
    name  = "backend"
    image = "${aws_ecr_repository.backend.repository_url}:latest"
    
    secrets = [
      {
        name      = "DB_PASSWORD"
        valueFrom = "${aws_secretsmanager_secret.db_password.arn}"
      },
      {
        name      = "JWT_SECRET"
        valueFrom = "${aws_secretsmanager_secret.jwt_secret.arn}"
      }
    ]
  }])
}
```

### 7. Monitoring and Alerting

#### Security Monitoring

```hcl
# CloudWatch alarm for unauthorized API access
resource "aws_cloudwatch_metric_alarm" "unauthorized_access" {
  alarm_name          = "uvis-gps-unauthorized-access"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "4xxError"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "100"
  alarm_description   = "Alert on high 4xx errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
}

# CloudWatch alarm for failed logins
resource "aws_cloudwatch_log_metric_filter" "failed_logins" {
  name           = "failed-logins"
  log_group_name = aws_cloudwatch_log_group.backend.name
  pattern        = "[time, request_id, level=ERROR, msg=\"*login failed*\"]"

  metric_transformation {
    name      = "FailedLoginCount"
    namespace = "UVIS/Security"
    value     = "1"
  }
}
```

#### AWS GuardDuty

```hcl
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
  }
}

resource "aws_guardduty_detector_finding_publishing_destination" "main" {
  detector_id     = aws_guardduty_detector.main.id
  destination_arn = aws_s3_bucket.guardduty_findings.arn
  destination_type = "S3"
}
```

## Security Checklist

### Pre-Production

- [ ] SSL/TLS certificates configured
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Security headers configured
- [ ] Firewall rules configured
- [ ] Fail2ban installed and configured
- [ ] Database passwords changed from defaults
- [ ] Application secrets stored in Secrets Manager
- [ ] Security groups configured with least privilege
- [ ] VPC Flow Logs enabled
- [ ] GuardDuty enabled
- [ ] CloudWatch alarms configured
- [ ] Backup encryption enabled
- [ ] Multi-factor authentication enabled

### Post-Production

- [ ] Regular security audits scheduled
- [ ] Penetration testing conducted
- [ ] Vulnerability scanning automated
- [ ] Security patches applied regularly
- [ ] Access logs reviewed regularly
- [ ] Incident response plan documented
- [ ] Security training completed
- [ ] Compliance requirements met

## Vulnerability Scanning

### Trivy (Container Scanning)

```bash
# Scan Docker image
trivy image backend:latest

# Scan with severity filter
trivy image --severity HIGH,CRITICAL backend:latest

# Output to file
trivy image -f json -o results.json backend:latest
```

### OWASP Dependency Check

```bash
# Backend (Python)
pip install safety
safety check --file requirements.txt

# Frontend (JavaScript)
npm audit
npm audit fix
```

## Incident Response

### Security Incident Playbook

1. **Detection**: Automated alerts via CloudWatch
2. **Containment**: Isolate affected resources
3. **Investigation**: Analyze logs and metrics
4. **Eradication**: Remove threat
5. **Recovery**: Restore from backup
6. **Lessons Learned**: Document and improve

### Contact List

- **Security Lead**: security@example.com
- **DevOps On-Call**: +82-10-xxxx-xxxx
- **AWS Support**: AWS Console
- **Incident Response Team**: incident@example.com

---

**Last Updated**: 2026-01-28  
**Version**: 1.0.0  
**Author**: GenSpark AI Developer
