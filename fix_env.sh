#!/bin/bash
# Quick fix for missing DB_PASSWORD in .env
# This script should be run on the server at /root/uvis

echo "🔧 Fixing .env file for backend deployment..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Creating from .env.example..."
    cp .env.example .env
fi

# Check if DB_PASSWORD exists
if grep -q "^DB_PASSWORD=" .env; then
    echo "✅ DB_PASSWORD already exists in .env"
else
    echo "⚠️  DB_PASSWORD not found in .env"
    echo "Adding default DB_PASSWORD..."
    echo "" >> .env
    echo "# Database Password (added by fix_env.sh)" >> .env
    echo "DB_PASSWORD=uvis_secure_password_2024" >> .env
    echo "✅ DB_PASSWORD added to .env"
fi

# Check if other required variables exist
echo ""
echo "🔍 Checking other required variables..."

# Function to add variable if missing
add_if_missing() {
    local var_name=$1
    local var_value=$2
    
    if grep -q "^${var_name}=" .env; then
        echo "✅ ${var_name} exists"
    else
        echo "⚠️  ${var_name} not found, adding..."
        echo "${var_name}=${var_value}" >> .env
        echo "✅ ${var_name} added"
    fi
}

# Add DATABASE_URL if missing
DB_USER=$(grep "^DB_USER=" .env | cut -d'=' -f2)
DB_PASSWORD=$(grep "^DB_PASSWORD=" .env | cut -d'=' -f2)
DB_NAME=$(grep "^DB_NAME=" .env | cut -d'=' -f2)

if [ -z "$DB_USER" ]; then DB_USER="uvis_user"; fi
if [ -z "$DB_PASSWORD" ]; then DB_PASSWORD="uvis_secure_password_2024"; fi
if [ -z "$DB_NAME" ]; then DB_NAME="uvis_db"; fi

add_if_missing "DATABASE_URL" "postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}"
add_if_missing "SECRET_KEY" "$(openssl rand -hex 32)"
add_if_missing "NAVER_MAP_CLIENT_ID" "your_naver_client_id"
add_if_missing "NAVER_MAP_CLIENT_SECRET" "your_naver_client_secret"

echo ""
echo "✅ .env file is ready!"
echo ""
echo "📝 Current DB configuration:"
grep -E "^DB_|^DATABASE_URL=" .env | grep -v PASSWORD
echo "DB_PASSWORD=****** (hidden)"
echo ""
echo "🚀 You can now run: docker-compose build backend && docker-compose up -d backend"
