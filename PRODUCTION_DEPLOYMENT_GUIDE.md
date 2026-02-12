# Cold Chain Production Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2026-01-27  
**Environment**: Production

---

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04 LTS or later (recommended)
- **CPU**: 4+ cores
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 100GB+ SSD
- **Network**: Static IP, domain name, SSL certificate

### Software Requirements
- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+
- Nginx 1.24+
- PostgreSQL 15+ (or Docker)
- Redis 7+ (or Docker)

---

## 🚀 Quick Start Deployment

### Step 1: Clone Repository
```bash
git clone https://github.com/rpaakdi1-spec/3-.git
cd 3-
git checkout main
```

### Step 2: Configure Environment
```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit environment variables
nano .env.production
```

**Critical Variables to Change**:
```bash
# Database
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql://coldchain_user:<password>@postgres:5432/coldchain_prod

# Redis
REDIS_PASSWORD=<strong-redis-password>

# Security
SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_SECRET=<generate-with-openssl-rand-hex-32>

# Domain
DOMAIN=yourdomain.com
VITE_API_URL=https://api.yourdomain.com/api/v1

# Email
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=<app-specific-password>
```

### Step 3: SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/certs/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/private/
```

#### Option B: Self-Signed (Development Only)
```bash
mkdir -p ssl/certs ssl/private
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/private/privkey.pem \
  -out ssl/certs/fullchain.pem
```

### Step 4: Deploy
```bash
# Make scripts executable
chmod +x deploy-production.sh scripts/backup.sh docker/start-production.sh

# Run deployment
./deploy-production.sh
```

---

## 📦 Manual Deployment Steps

### 1. Create Data Directories
```bash
sudo mkdir -p /var/lib/coldchain/{postgres,redis}
sudo chown -R $USER:$USER /var/lib/coldchain
```

### 2. Build Docker Images
```bash
docker-compose -f docker-compose.production.yml build
```

### 3. Start Infrastructure Services
```bash
docker-compose -f docker-compose.production.yml up -d postgres redis
```

### 4: Wait for Services
```bash
# Wait for PostgreSQL
until docker exec coldchain-postgres-prod pg_isready; do sleep 1; done

# Wait for Redis
until docker exec coldchain-redis-prod redis-cli ping; do sleep 1; done
```

### 5. Deploy Backend
```bash
docker-compose -f docker-compose.production.yml up -d backend
```

### 6. Deploy Nginx
```bash
docker-compose -f docker-compose.production.yml up -d nginx
```

### 7. Start Monitoring
```bash
docker-compose -f docker-compose.production.yml up -d prometheus grafana
```

---

## 🔍 Verification

### Health Checks
```bash
# API health
curl https://yourdomain.com/health

# Backend health
curl https://yourdomain.com/api/v1/health

# Database connection
docker exec coldchain-backend-prod python -c "from app.core.database import engine; engine.connect()"
```

### Service Status
```bash
docker-compose -f docker-compose.production.yml ps
```

### Logs
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.production.yml logs --tail=100 backend
```

---

## 🔄 Updates & Rollback

### Update to New Version
```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose -f docker-compose.production.yml build

# Rolling update
./deploy-production.sh deploy
```

### Rollback
```bash
# Stop current version
docker-compose -f docker-compose.production.yml down

# Restore from backup
./scripts/restore.sh <backup-timestamp>

# Start services
docker-compose -f docker-compose.production.yml up -d
```

---

## 💾 Backup & Restore

### Manual Backup
```bash
./scripts/backup.sh
```

### Automated Backup (Cron)
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/webapp/scripts/backup.sh >> /var/log/coldchain-backup.log 2>&1
```

### Restore from Backup
```bash
# List backups
ls -lh /backups/database/

# Restore database
BACKUP_FILE="/backups/database/postgres_20260127_020000.dump.gz"
gunzip -c $BACKUP_FILE | docker exec -i coldchain-postgres-prod \
  pg_restore -U coldchain_user -d coldchain_prod --clean

# Restore Redis
gunzip -c /backups/redis/redis_20260127_020000.rdb.gz | \
  docker cp - coldchain-redis-prod:/data/dump.rdb
docker restart coldchain-redis-prod
```

---

## 📊 Monitoring

### Grafana Dashboard
- URL: `http://yourdomain.com:3001`
- Username: `admin`
- Password: (from .env.production)

### Prometheus Metrics
- URL: `http://yourdomain.com:9090`

### Key Metrics to Monitor
- API response time (p50, p95, p99)
- Error rate
- Request rate
- Database connections
- Redis memory usage
- CPU & Memory usage
- Disk I/O

---

## 🔒 Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY and JWT_SECRET
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall (allow only 80, 443)
- [ ] Set up rate limiting
- [ ] Enable Sentry error tracking
- [ ] Configure CORS properly
- [ ] Disable DEBUG mode
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Enable security headers
- [ ] Set up intrusion detection
- [ ] Configure fail2ban

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker logs coldchain-backend-prod

# Check database connection
docker exec coldchain-backend-prod env | grep DATABASE

# Restart service
docker-compose -f docker-compose.production.yml restart backend
```

### Database Connection Errors
```bash
# Check PostgreSQL logs
docker logs coldchain-postgres-prod

# Check if PostgreSQL is accepting connections
docker exec coldchain-postgres-prod pg_isready

# Reset password
docker exec -it coldchain-postgres-prod psql -U postgres
ALTER USER coldchain_user PASSWORD 'new-password';
```

### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart services with memory limits
docker-compose -f docker-compose.production.yml up -d --force-recreate
```

### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in ssl/certs/fullchain.pem -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew
```

---

## 📞 Support

### Getting Help
1. Check logs: `docker-compose logs`
2. Review documentation
3. Contact: admin@yourdomain.com

### Emergency Contacts
- DevOps Team: devops@yourdomain.com
- System Admin: admin@yourdomain.com
- On-call: +82-10-XXXX-XXXX

---

## 📚 Additional Resources

- [Architecture Documentation](./docs/ARCHITECTURE.md)
- [API Documentation](https://yourdomain.com/api/docs)
- [User Manual](./docs/USER_MANUAL.md)
- [Security Guide](./docs/SECURITY.md)

---

*Last Updated: 2026-01-27*  
*Maintainer: Cold Chain DevOps Team*
