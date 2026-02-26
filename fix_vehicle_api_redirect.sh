#!/bin/bash
# Fix Vehicle API 307 Redirect
# This script adds a rewrite rule in Nginx to handle the trailing slash

set -e

echo "🔧 Fix Vehicle API 307 Redirect"
echo "================================"

cd /root/uvis/frontend

# Backup
BACKUP_FILE="nginx.conf.backup.vehicle_$(date +%Y%m%d_%H%M%S)"
cp nginx.conf "$BACKUP_FILE"
echo "✅ Backup created: $BACKUP_FILE"

# Check if rewrite rule already exists
if grep -q "rewrite.*vehicles.*vehicles/" nginx.conf; then
    echo "⚠️  Rewrite rule already exists"
else
    echo "📝 Adding rewrite rule for /api/v1/vehicles..."
    
    # Insert rewrite rule before first location block
    sed -i '/location \/api\/v1\/ws\// i\        # Fix vehicle API redirect - add trailing slash automatically\n        rewrite ^/api/v1/vehicles$ /api/v1/vehicles/ permanent;\n' nginx.conf
    
    echo "✅ Rewrite rule added"
fi

# Show the relevant section
echo ""
echo "📄 Updated nginx.conf section:"
grep -B 2 -A 2 "rewrite.*vehicles" nginx.conf || echo "Rule not found in expected location"

echo ""
echo "🚀 Deploying to container..."
docker cp nginx.conf uvis-frontend:/etc/nginx/nginx.conf

echo ""
echo "🧪 Testing configuration..."
docker exec uvis-frontend nginx -t

echo ""
echo "♻️  Reloading nginx..."
docker exec uvis-frontend nginx -s reload

echo ""
echo "✅ Vehicle API redirect fix complete!"
echo ""
echo "🧪 Test with:"
echo "TOKEN=\$(curl -s -X POST http://139.150.11.99/api/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin&password=admin123' | python3 -c \"import sys,json;print(json.load(sys.stdin)['access_token'])\")"
echo "curl -X GET 'http://139.150.11.99/api/v1/vehicles' -H \"Authorization: Bearer \$TOKEN\" -v"
echo ""
echo "Expected: 200 OK (not 307)"
