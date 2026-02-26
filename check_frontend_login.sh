#!/bin/bash
echo "=== src/api/client.ts의 로그인 부분 확인 ==="
echo ""
echo "파일 내용 (50-70줄):"
ssh root@139.150.11.99 "cat /root/uvis/frontend/src/api/client.ts" | sed -n '50,70p'
echo ""
echo "=== src/config/api.ts 확인 ==="
ssh root@139.150.11.99 "cat /root/uvis/frontend/src/config/api.ts" | head -40
