#!/bin/bash
# Quick fix deployment script for email nullable issue
# Run this on the server at /root/uvis

set -e  # Exit on error

echo "🚀 Starting deployment to fix 500 error..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📥 Step 1: Pulling latest code..."
git pull origin main
echo -e "${GREEN}✅ Code updated${NC}"
echo ""

echo "🗄️  Step 2: Running database migration..."
if docker compose run --rm backend alembic upgrade head; then
    echo -e "${GREEN}✅ Migration completed${NC}"
else
    echo -e "${YELLOW}⚠️  Migration failed, trying manual SQL...${NC}"
    docker compose exec db psql -U uvis_user -d uvis_db -c "ALTER TABLE users ALTER COLUMN email DROP NOT NULL;"
    echo -e "${GREEN}✅ Manual SQL executed${NC}"
fi
echo ""

echo "🔨 Step 3: Rebuilding backend..."
docker compose build --no-cache backend
echo -e "${GREEN}✅ Backend rebuilt${NC}"
echo ""

echo "🔄 Step 4: Restarting backend..."
docker compose up -d backend
echo "⏳ Waiting 20 seconds for backend to start..."
sleep 20
echo -e "${GREEN}✅ Backend restarted${NC}"
echo ""

echo "🏥 Step 5: Health check..."
HEALTH_RESPONSE=$(curl -s http://139.150.11.99/api/v1/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "$HEALTH_RESPONSE"
    exit 1
fi
echo ""

echo "🧪 Step 6: Testing signup API..."
SIGNUP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://139.150.11.99/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser05",
    "password": "test123456",
    "role": "DRIVER",
    "name": "최영수",
    "phone": "010-3333-2222",
    "employee_role": "DRIVER",
    "employment_type": "FULL_TIME",
    "hire_date": "2026-02-28",
    "has_cargo_license": false,
    "can_drive_forklift": false,
    "has_forklift_certificate": false
  }')

HTTP_CODE=$(echo "$SIGNUP_RESPONSE" | tail -n 1)
BODY=$(echo "$SIGNUP_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✅ Signup API working! Got HTTP 201${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" = "400" ] && echo "$BODY" | grep -q "이미 존재하는"; then
    echo -e "${YELLOW}⚠️  User already exists (that's OK for testing)${NC}"
    echo "Trying with testuser06..."
    
    SIGNUP_RESPONSE2=$(curl -s -w "\n%{http_code}" -X POST http://139.150.11.99/api/v1/auth/signup \
      -H "Content-Type: application/json" \
      -d '{
        "username": "testuser06",
        "password": "test123456",
        "role": "DRIVER",
        "name": "김영희",
        "phone": "010-4444-3333",
        "employee_role": "DRIVER",
        "employment_type": "FULL_TIME",
        "hire_date": "2026-02-28",
        "has_cargo_license": false,
        "can_drive_forklift": false,
        "has_forklift_certificate": false
      }')
    
    HTTP_CODE2=$(echo "$SIGNUP_RESPONSE2" | tail -n 1)
    BODY2=$(echo "$SIGNUP_RESPONSE2" | head -n -1)
    
    if [ "$HTTP_CODE2" = "201" ]; then
        echo -e "${GREEN}✅ Signup API working! Got HTTP 201${NC}"
        echo "$BODY2" | python3 -m json.tool 2>/dev/null || echo "$BODY2"
    else
        echo -e "${RED}❌ Still getting error. HTTP $HTTP_CODE2${NC}"
        echo "$BODY2"
        exit 1
    fi
else
    echo -e "${RED}❌ Signup failed with HTTP $HTTP_CODE${NC}"
    echo "$BODY"
    
    if [ "$HTTP_CODE" = "500" ]; then
        echo ""
        echo "Still getting 500 error. Check backend logs:"
        echo "  docker compose logs backend --tail=50"
    fi
    exit 1
fi
echo ""

echo "📊 Step 7: Verifying database..."
echo "Checking users table:"
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, username, email, full_name, phone, is_active, approval_status
FROM users
ORDER BY id DESC
LIMIT 3;
"
echo ""

echo "Checking pending_employees table:"
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, employee_code, name, phone, email, created_at
FROM pending_employees
ORDER BY id DESC
LIMIT 3;
"
echo ""

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo "📋 Next steps:"
echo "  1. Open browser: http://139.150.11.99/"
echo "  2. Try signup as testuser07 (use any phone number)"
echo "  3. Login as admin (admin/admin123)"
echo "  4. Go to Settings → User Management → Pending Users"
echo "  5. Approve testuser07"
echo "  6. Login as testuser07"
echo ""
echo "📚 Documentation:"
echo "  - CRITICAL_FIX_EMAIL_NULLABLE.md"
echo "  - FINAL_500_ERROR_SOLUTION.md"
echo ""
