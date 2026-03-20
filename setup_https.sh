#!/bin/bash
# ============================================================
# UVIS HTTPS 설정 스크립트
# 도메인: www.rhkdtls.cloud
#
# 사용법:
#   sudo bash setup_https.sh [이메일주소]
#   예) sudo bash setup_https.sh admin@rhkdtls.cloud
# ============================================================

set -e

DOMAIN="www.rhkdtls.cloud"
APEX_DOMAIN="rhkdtls.cloud"
SERVER_DIR="/root/uvis"
SSL_DIR="$SERVER_DIR/nginx/ssl"
EMAIL="${1:-admin@rhkdtls.cloud}"

echo "========================================"
echo " UVIS HTTPS 설정 (Let's Encrypt)"
echo " 도메인 : $DOMAIN"
echo " 이메일 : $EMAIL"
echo " SSL 경로: $SSL_DIR"
echo "========================================"

# ── 루트 확인 ──
if [ "$EUID" -ne 0 ]; then
    echo "❌ root 권한이 필요합니다. sudo 로 실행하세요."
    exit 1
fi

mkdir -p "$SSL_DIR"

# ────────────────────────────────────────
# Step 1. certbot 설치 (OS 자동 감지)
# ────────────────────────────────────────
echo ""
echo "[1/5] certbot 설치 확인..."

install_certbot() {
    # Ubuntu / Debian
    if command -v apt-get &> /dev/null; then
        echo "  → apt-get으로 certbot 설치..."
        apt-get update -qq
        apt-get install -y certbot

    # CentOS / RHEL / Rocky / AlmaLinux (dnf 우선)
    elif command -v dnf &> /dev/null; then
        echo "  → dnf으로 certbot 설치..."
        # EPEL 저장소 활성화 (certbot이 EPEL에 있음)
        dnf install -y epel-release 2>/dev/null || true
        dnf install -y certbot

    # 구형 CentOS 7 (yum)
    elif command -v yum &> /dev/null; then
        echo "  → yum으로 certbot 설치..."
        yum install -y epel-release 2>/dev/null || true
        yum install -y certbot

    else
        echo "  → pip으로 certbot 설치 (패키지 매니저 미발견)..."
        pip3 install certbot 2>/dev/null || pip install certbot
    fi
}

if ! command -v certbot &> /dev/null; then
    install_certbot
fi

echo "✅ certbot $(certbot --version 2>&1 | head -1)"

# ────────────────────────────────────────
# Step 2. 임시 Self-signed 인증서 생성
#         (nginx가 443으로 먼저 떠야 certbot webroot 인증 가능)
# ────────────────────────────────────────
echo ""
echo "[2/5] 임시 Self-signed 인증서 생성..."
openssl req -x509 -nodes -days 1 \
    -newkey rsa:2048 \
    -keyout "$SSL_DIR/privkey.pem" \
    -out   "$SSL_DIR/fullchain.pem" \
    -subj  "/CN=$DOMAIN" 2>/dev/null
chmod 644 "$SSL_DIR/fullchain.pem"
chmod 600 "$SSL_DIR/privkey.pem"
echo "✅ 임시 인증서 생성 완료"

# ────────────────────────────────────────
# Step 3. 포트 80 충돌 해제 + nginx 시작
# ────────────────────────────────────────
echo ""
echo "[3/5] nginx 컨테이너 시작..."
cd "$SERVER_DIR"

# frontend가 80 포트를 점유하고 있으면 재시작 (expose 전환 후)
echo "  → docker-compose.yml 반영 (frontend 포트 내부화)..."
docker compose up -d --no-deps frontend 2>/dev/null || true
sleep 2

# 포트 80이 아직 사용 중이면 강제 해제
if ss -tlnp 2>/dev/null | grep -q ':80 ' || netstat -tlnp 2>/dev/null | grep -q ':80 '; then
    echo "  → 포트 80 사용 중인 프로세스 확인..."
    # 호스트의 80 포트를 점유한 컨테이너 찾아서 중지
    CONTAINER_80=$(docker ps --format '{{.Names}}' | xargs -I{} sh -c \
        'docker port {} 2>/dev/null | grep -q "0.0.0.0:80->" && echo {}' 2>/dev/null | head -1)
    if [ -n "$CONTAINER_80" ]; then
        echo "  → $CONTAINER_80 컨테이너가 포트 80 점유 → 재시작..."
        docker stop "$CONTAINER_80" 2>/dev/null || true
        sleep 1
        docker start "$CONTAINER_80" 2>/dev/null || true
        sleep 2
    fi
fi

docker compose up -d nginx
echo "  → 5초 대기..."
sleep 5
docker compose ps nginx
echo "✅ nginx 실행 확인"

# ────────────────────────────────────────
# Step 4. Let's Encrypt 인증서 발급
#         webroot 방식: nginx가 /.well-known/acme-challenge/ 서빙
# ────────────────────────────────────────
echo ""
echo "[4/5] Let's Encrypt 인증서 발급..."

# certbot_webroot Docker volume 실제 경로 찾기
WEBROOT_PATH=$(docker volume inspect uvis_certbot_webroot \
    --format '{{.Mountpoint}}' 2>/dev/null || echo "")

if [ -z "$WEBROOT_PATH" ]; then
    WEBROOT_PATH="/var/www/certbot"
    mkdir -p "$WEBROOT_PATH"
fi

echo "  → webroot: $WEBROOT_PATH"

certbot certonly \
    --webroot \
    --webroot-path="$WEBROOT_PATH" \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "$APEX_DOMAIN"

echo "✅ 인증서 발급 완료"

# ────────────────────────────────────────
# Step 5. 실제 인증서로 교체 + nginx 재시작
# ────────────────────────────────────────
echo ""
echo "[5/5] 인증서 적용 및 nginx 재시작..."

cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$SSL_DIR/fullchain.pem"
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem   "$SSL_DIR/privkey.pem"
chmod 644 "$SSL_DIR/fullchain.pem"
chmod 600 "$SSL_DIR/privkey.pem"

docker compose restart nginx
sleep 3
echo "✅ nginx 재시작 완료"

# ────────────────────────────────────────
# 자동 갱신 cron 등록 (매일 새벽 3시)
# Let's Encrypt 인증서는 90일 유효 → certbot renew가 만료 30일 전부터 갱신
# ────────────────────────────────────────
RENEW_CMD="certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/fullchain.pem && cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/privkey.pem && chmod 644 $SSL_DIR/fullchain.pem && chmod 600 $SSL_DIR/privkey.pem && docker compose -f $SERVER_DIR/docker-compose.yml restart nginx"
CRON_LINE="0 3 * * * $RENEW_CMD"

# 기존 certbot renew cron 제거 후 새로 등록
(crontab -l 2>/dev/null | grep -v "certbot renew"; echo "$CRON_LINE") | crontab -
echo "✅ 자동 갱신 cron 등록 (매일 03:00)"

echo ""
echo "========================================"
echo "🎉 HTTPS 설정 완료!"
echo ""
echo "  접속 URL  : https://www.rhkdtls.cloud"
echo "  인증서 만료: 90일 (자동 갱신 설정됨)"
echo ""
echo "  확인 명령어:"
echo "    curl -I https://www.rhkdtls.cloud/health"
echo "    docker compose logs nginx --tail=20"
echo "========================================"
