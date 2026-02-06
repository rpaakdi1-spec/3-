# 🚨 긴급 수정: 백엔드 파일명 오타 수정

## 문제 확인
프로덕션 서버에 `billing_enchanced.py` (오타) 파일이 존재하여 405 에러가 발생합니다.
올바른 이름은 `billing_enhanced.py` 입니다.

## 즉시 실행할 명령어 (프로덕션 서버에서)

```bash
cd /root/uvis

# 1. 현재 상태 확인
ls -la backend/app/api/v1/billing_en*.py

# 2. 파일명이 잘못되었다면 수정
# 만약 billing_enchanced.py가 있다면:
if [ -f "backend/app/api/v1/billing_enchanced.py" ]; then
    echo "오타 파일 발견! 수정 중..."
    mv backend/app/api/v1/billing_enchanced.py backend/app/api/v1/billing_enhanced.py
    echo "파일명 수정 완료"
fi

# 3. main.py에서 import 확인 및 수정
grep -n "billing_enchanced" backend/main.py
# 만약 billing_enchanced가 있다면 수정:
sed -i 's/billing_enchanced/billing_enhanced/g' backend/main.py

# 4. 모든 파일에서 오타 검색 및 수정
echo "전체 파일 검색 중..."
grep -r "billing_enchanced" backend/ 2>/dev/null

# 5. 오타가 있는 모든 파일 자동 수정
find backend -type f -name "*.py" -exec sed -i 's/billing_enchanced/billing_enhanced/g' {} +

# 6. 변경사항 확인
git status

# 7. 변경사항 커밋
git add -A
git commit -m "fix(backend): Correct typo billing_enchanced -> billing_enhanced"

# 8. 백엔드 재시작
docker-compose restart backend

# 9. 30초 대기
echo "백엔드 재시작 중... 30초 대기"
sleep 30

# 10. 헬스 체크
curl http://localhost:8000/health

# 11. API 문서 확인 (billing/enhanced 엔드포인트 존재 확인)
curl http://localhost:8000/openapi.json | grep -o "/api/v1/billing/enhanced/[^\"]*" | sort | uniq

echo ""
echo "✅ 수정 완료! 이제 Phase 8 API 테스트를 다시 실행하세요."
```

## 빠른 원스텝 스크립트

```bash
cd /root/uvis
chmod +x fix_filename_typo.sh
./fix_filename_typo.sh
```

## 수정 후 확인

```bash
# 토큰 획득
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"

# Phase 8 API 테스트
echo ""
echo "=== Phase 8 API 테스트 ==="

echo "1. Settlement Approval:"
curl -X GET "http://localhost:8000/api/v1/billing/enhanced/settlement-approval" \
  -H "Authorization: Bearer $TOKEN"

echo ""
echo "2. Payment Reminder:"
curl -X GET "http://localhost:8000/api/v1/billing/enhanced/payment-reminder" \
  -H "Authorization: Bearer $TOKEN"

echo ""
echo "3. Export:"
curl -X GET "http://localhost:8000/api/v1/billing/enhanced/export" \
  -H "Authorization: Bearer $TOKEN"
```

## 기대 결과

### ✅ 성공 시:
- 각 엔드포인트에서 `[]` (빈 배열) 또는 데이터 반환
- HTTP 200 OK

### ❌ 실패 시:
- 405 Method Not Allowed → 파일명 여전히 오타
- 500 Internal Server Error → 로그 확인 필요: `docker logs uvis-backend --tail 100`

## 추가 확인사항

```bash
# 백엔드 로그 실시간 모니터링
docker logs uvis-backend -f

# 특정 오류 검색
docker logs uvis-backend --tail 200 | grep -i "error\|405\|500"
```

## 문제가 계속되면

1. **완전 재빌드:**
   ```bash
   cd /root/uvis
   docker-compose down
   docker-compose build --no-cache backend
   docker-compose up -d
   sleep 30
   curl http://localhost:8000/health
   ```

2. **Python 캐시 삭제:**
   ```bash
   find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
   find backend -name "*.pyc" -delete
   docker-compose restart backend
   ```

## 도움말

궁금한 점이나 추가 오류가 발생하면 다음 정보를 공유해주세요:
1. `ls -la backend/app/api/v1/billing_en*.py` 결과
2. `grep -n "billing_en" backend/main.py` 결과
3. `docker logs uvis-backend --tail 50` 결과
