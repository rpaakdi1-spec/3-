#!/bin/bash

echo "=== Testing Dispatch Form Template API ==="
echo ""

echo "1️⃣ Check backend health:"
curl -s http://localhost/api/v1/health | head -20
echo ""
echo ""

echo "2️⃣ List all API routes with dispatch:"
curl -s http://localhost/openapi.json 2>&1 | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    paths = [p for p in data.get('paths', {}).keys() if 'dispatch' in p.lower()]
    if paths:
        print('Found dispatch routes:')
        for p in sorted(paths):
            print(f'  - {p}')
    else:
        print('No dispatch routes found')
except Exception as e:
    print(f'Error: {e}')
"
echo ""
echo ""

echo "3️⃣ Test dispatch-form API (raw response):"
curl -v http://localhost/api/v1/dispatch-form/templates 2>&1 | head -30
echo ""
echo ""

echo "4️⃣ Check backend logs for errors:"
echo "(Run on server: docker compose logs backend --tail=100 | grep -i error)"
