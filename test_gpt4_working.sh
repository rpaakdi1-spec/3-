#!/bin/bash
echo "=== Testing GPT-4 Functionality ==="
echo ""

# Test 1: Check backend logs for OpenAI activity
echo "[Test 1] Checking recent backend logs for AI activity..."
docker logs uvis-backend --tail 100 2>&1 | grep -i -E "openai|gpt|ai.*chat|chat.*message" | tail -10
echo ""

# Test 2: Check if API endpoints are accessible
echo "[Test 2] Testing health endpoint..."
curl -s http://localhost:8000/health | head -5
echo ""

# Test 3: Check backend environment
echo "[Test 3] Verifying OPENAI_API_KEY in backend..."
docker exec uvis-backend printenv | grep -c OPENAI_API_KEY
if [ $? -eq 0 ]; then
    echo "✅ API Key is present in backend"
else
    echo "❌ API Key is missing"
fi
echo ""

# Test 4: Test OpenAI connection from backend
echo "[Test 4] Testing OpenAI API connection from backend container..."
docker exec uvis-backend python3 -c "
import os
import sys
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[{'role': 'user', 'content': 'Say hello in Korean'}],
        max_tokens=50
    )
    print('✅ GPT-4 API 호출 성공!')
    print(f'응답: {response.choices[0].message.content}')
except Exception as e:
    print(f'❌ 오류 발생: {str(e)}')
    sys.exit(1)
" 2>&1

echo ""
echo "=== Test Complete ==="
