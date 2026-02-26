#!/bin/bash
# Diagnose Backend Async Errors
# This script helps locate the ChunkedIteratorResult error

set -e

echo "🔍 Diagnosing Backend Async Errors"
echo "==================================="
echo ""

echo "1️⃣  Searching for 'broadcast' functions..."
echo "----------------------------------------"
docker exec uvis-backend grep -rn "async def.*broadcast" /app/app --include="*.py" || echo "No broadcast functions found"

echo ""
echo "2️⃣  Searching for 'ChunkedIteratorResult' or await issues..."
echo "----------------------------------------------------------"
docker exec uvis-backend grep -rn "broadcast.*vehicle\|broadcast.*dashboard" /app/app --include="*.py" -A 10 || echo "No matches found"

echo ""
echo "3️⃣  Checking WebSocket background tasks..."
echo "---------------------------------------"
docker exec uvis-backend find /app/app -name "*.py" -exec grep -l "background.*task\|create_task" {} \; || echo "No background tasks found"

echo ""
echo "4️⃣  Recent error logs (last 100 lines)..."
echo "--------------------------------------"
docker logs uvis-backend --tail 100 | grep -E "Error|Traceback|ChunkedIteratorResult" -A 5 || echo "No errors in recent logs"

echo ""
echo "5️⃣  WebSocket implementation check..."
echo "----------------------------------"
docker exec uvis-backend cat /app/app/api/v1/websocket.py | head -150

echo ""
echo "6️⃣  Looking for SQLAlchemy execute + await pattern (common issue)..."
echo "------------------------------------------------------------------"
docker exec uvis-backend grep -rn "result = await.*execute\|await result" /app/app --include="*.py" -B 2 -A 2 | head -50 || echo "No suspicious patterns found"

echo ""
echo "✅ Diagnosis complete!"
echo ""
echo "📝 Common fix patterns:"
echo "----------------------"
echo "WRONG:"
echo "  result = await session.execute(select(...))"
echo "  await result  # ❌ ChunkedIteratorResult is not awaitable"
echo ""
echo "CORRECT:"
echo "  result = await session.execute(select(...))"
echo "  items = result.scalars().all()  # ✅ Use .scalars() or .all()"
echo ""
echo "Or:"
echo "  result = await session.execute(select(...))"
echo "  item = result.scalar_one_or_none()  # ✅ For single result"
