# Dispatch Rules 수정/삭제 테스트 가이드

## 🔍 문제 확인

규칙 관리에서 수정/삭제가 안 되는 경우 다음을 확인해야 합니다:

1. **Backend API 동작 확인**
2. **Frontend 요청 형식 확인**
3. **Backend 로그 확인**

---

## 🚀 서버에서 실행할 테스트 명령어

```bash
ssh root@139.150.11.99

# 1. 규칙 목록 조회
echo "=== 1. 규칙 목록 조회 ==="
curl -s http://localhost:8000/api/v1/dispatch-rules | jq '.'

# 2. 첫 번째 규칙 ID 가져오기
RULE_ID=$(curl -s http://localhost:8000/api/v1/dispatch-rules | jq -r '.[0].id')
echo "규칙 ID: $RULE_ID"

# 3. 단일 규칙 조회
echo -e "\n=== 2. 규칙 상세 조회 ==="
curl -s http://localhost:8000/api/v1/dispatch-rules/$RULE_ID | jq '.'

# 4. 규칙 수정 테스트
echo -e "\n=== 3. 규칙 수정 테스트 ==="
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "rule_update": {
      "name": "테스트_수정_규칙",
      "description": "수정 테스트",
      "priority": 999
    }
  }' \
  http://localhost:8000/api/v1/dispatch-rules/$RULE_ID | jq '.'

# 5. 수정 결과 확인
echo -e "\n=== 4. 수정 후 확인 ==="
curl -s http://localhost:8000/api/v1/dispatch-rules/$RULE_ID | jq '.name, .priority, .version'

# 6. Backend 로그 확인
echo -e "\n=== 5. Backend 로그 (최근 50줄) ==="
docker logs uvis-backend --tail 50 | grep -i "dispatch-rules\|PUT\|DELETE\|error"
```

---

## 🌐 브라우저에서 확인

### 1. 개발자 도구 열기
```
F12 → Network 탭
```

### 2. 규칙 수정 시도
1. http://139.150.11.99/dispatch-rules 접속
2. 규칙 카드에서 **Edit** 버튼 클릭
3. 이름 또는 우선순위 변경
4. **Save** 클릭

### 3. Network 탭에서 확인
- **Request URL**: `PUT http://139.150.11.99/api/v1/dispatch-rules/{id}`
- **Request Headers**: `Content-Type: application/json`
- **Request Payload**:
  ```json
  {
    "rule_update": {
      "name": "새이름",
      "priority": 100
    }
  }
  ```
- **Response Status**: `200 OK` (예상)

### 4. 실패 시 확인할 것
- ❌ Status `404 Not Found` → Backend 라우트 문제
- ❌ Status `422 Unprocessable Entity` → Request 형식 문제
- ❌ Status `500 Internal Server Error` → Backend 로직 오류

---

## 🔧 예상 문제 및 해결

### 문제 1: Request Payload 형식 오류
**증상**: 422 Unprocessable Entity

**원인**: Frontend가 잘못된 형식으로 요청
```json
// ❌ 잘못된 형식
{
  "name": "새이름",
  "priority": 100
}

// ✅ 올바른 형식
{
  "rule_update": {
    "name": "새이름",
    "priority": 100
  }
}
```

**해결**: Frontend 코드 확인
```bash
cd /root/uvis/frontend
grep -r "dispatch-rules" src/ | grep -i "put\|delete"
```

---

### 문제 2: Backend API 라우트 누락
**증상**: 404 Not Found

**원인**: Backend에 PUT/DELETE 엔드포인트가 없음

**해결**: Backend 라우트 확인
```bash
ssh root@139.150.11.99
docker exec uvis-backend grep -r "dispatch-rules" /app/backend/routers/ | grep -i "put\|delete"
```

---

### 문제 3: CORS 문제
**증상**: Console에 CORS 오류

**원인**: Backend가 PUT/DELETE 메서드를 허용하지 않음

**해결**: Backend CORS 설정 확인
```bash
docker exec uvis-backend grep -A10 "CORS" /app/backend/main.py
```

---

## 📋 체크리스트

브라우저 테스트:
- [ ] F12 → Network 탭 열기
- [ ] 규칙 수정 시도
- [ ] Network 탭에서 PUT 요청 확인
- [ ] Request Payload에 `rule_update` 키 있는지 확인
- [ ] Response Status 확인 (200 OK 예상)
- [ ] Console 탭에서 오류 메시지 확인

서버 테스트:
- [ ] curl로 PUT 요청 테스트
- [ ] Backend 로그 확인
- [ ] 수정된 규칙 확인

---

## 💬 결과 공유

다음 정보를 공유해 주세요:

1. **Network 탭 스크린샷**:
   - Request URL
   - Request Headers
   - Request Payload
   - Response Status
   - Response Body

2. **Console 오류 메시지** (있다면)

3. **서버 테스트 결과**:
   - curl PUT 요청 결과
   - Backend 로그

