# 🎯 Dispatch Rules API 수정사항 테스트 가이드

## ✅ 변경 내용

### 1. 규칙 수정 시 `rule_type` 변경 가능
- **Before**: `DispatchRuleUpdate`에 `rule_type` 필드 없음
- **After**: `rule_type` 필드 추가 (assignment, constraint, optimization 중 선택)

### 2. 규칙 삭제 기능 수정
- **Before**: Soft delete (is_active = False)
- **After**: Hard delete (DB에서 완전히 삭제)

---

## 🚀 서버 반영 방법

### 방법 1: Git을 통한 반영 (권장)

```bash
# 로컬에서 커밋 및 푸시
cd /home/user/webapp
git add backend/app/api/v1/endpoints/dispatch_rules.py
git commit -m "feat: Allow rule_type update and implement hard delete for dispatch rules"
git push origin main

# 서버에서 pull
ssh root@139.150.11.99
cd /root/uvis
git pull origin main
docker-compose restart backend
sleep 10
docker logs uvis-backend --tail 20
```

### 방법 2: 직접 파일 복사

```bash
# 서버에서 직접 수정
ssh root@139.150.11.99
cd /root/uvis

# 백업
cp backend/app/api/v1/endpoints/dispatch_rules.py backend/app/api/v1/endpoints/dispatch_rules.py.backup

# 수정사항 적용 (nano 또는 vim 사용)
nano backend/app/api/v1/endpoints/dispatch_rules.py

# 또는 cat을 사용한 직접 수정
# (아래 전체 파일 내용 사용)
```

---

## 🧪 테스트 시나리오

### 테스트 1: 규칙 타입 변경

```bash
ssh root@139.150.11.99

# 1. 현재 규칙 확인
curl -s http://localhost:8000/api/v1/dispatch-rules/1 | jq '{id, name, rule_type, priority, version}'

# 2. rule_type 변경 (assignment → constraint)
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "rule_update": {
      "rule_type": "constraint",
      "name": "제약조건_테스트"
    }
  }' \
  http://localhost:8000/api/v1/dispatch-rules/1 | jq '{id, name, rule_type, version}'

# 3. 변경 확인
curl -s http://localhost:8000/api/v1/dispatch-rules/1 | jq '{id, name, rule_type, priority, version}'

# 예상 결과:
# - rule_type: "constraint"
# - version: 11 (이전 10에서 증가)
```

### 테스트 2: 규칙 생성 후 삭제

```bash
# 1. 새 규칙 생성
RULE_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "삭제_테스트_규칙",
    "description": "Hard delete 테스트용",
    "rule_type": "assignment",
    "priority": 50,
    "conditions": {"test": true},
    "actions": {"test_action": 1}
  }' \
  http://localhost:8000/api/v1/dispatch-rules/)

echo "생성된 규칙:"
echo $RULE_RESPONSE | jq '{id, name, rule_type}'

# 2. 생성된 규칙 ID 가져오기
NEW_RULE_ID=$(echo $RULE_RESPONSE | jq -r '.id')
echo -e "\n생성된 규칙 ID: $NEW_RULE_ID"

# 3. 규칙 목록에서 확인
echo -e "\n규칙 목록:"
curl -s http://localhost:8000/api/v1/dispatch-rules/ | jq '.[] | {id, name}'

# 4. 규칙 삭제
echo -e "\n규칙 삭제 중..."
curl -s -X DELETE http://localhost:8000/api/v1/dispatch-rules/$NEW_RULE_ID -w "\nHTTP Status: %{http_code}\n"

# 5. 삭제 후 확인 (404 에러 발생 예상)
echo -e "\n삭제 후 조회 (404 예상):"
curl -s http://localhost:8000/api/v1/dispatch-rules/$NEW_RULE_ID -w "\nHTTP Status: %{http_code}\n" | jq '.'

# 6. 목록에서도 사라졌는지 확인
echo -e "\n최종 규칙 목록:"
curl -s http://localhost:8000/api/v1/dispatch-rules/ | jq '.[] | {id, name}'

# 예상 결과:
# - 삭제 요청: HTTP 204 No Content
# - 삭제 후 조회: HTTP 404 Not Found
# - 목록에서 제거됨
```

### 테스트 3: 통합 테스트

```bash
# 1. 규칙 생성
echo "=== 1. 규칙 생성 ==="
CREATE_RESULT=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "통합_테스트_규칙",
    "description": "assignment로 시작",
    "rule_type": "assignment",
    "priority": 100,
    "conditions": {"order.priority": "high"},
    "actions": {"assign_to": "best_driver"}
  }' \
  http://localhost:8000/api/v1/dispatch-rules/)

TEST_RULE_ID=$(echo $CREATE_RESULT | jq -r '.id')
echo "생성됨: ID=$TEST_RULE_ID, rule_type=assignment"
echo $CREATE_RESULT | jq '{id, name, rule_type, priority, version}'

# 2. 이름과 우선순위 변경
echo -e "\n=== 2. 이름/우선순위 변경 ==="
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "rule_update": {
      "name": "통합_테스트_규칙_수정",
      "priority": 200
    }
  }' \
  http://localhost:8000/api/v1/dispatch-rules/$TEST_RULE_ID | jq '{id, name, rule_type, priority, version}'

# 3. rule_type 변경 (assignment → constraint)
echo -e "\n=== 3. rule_type 변경 ==="
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "rule_update": {
      "rule_type": "constraint"
    }
  }' \
  http://localhost:8000/api/v1/dispatch-rules/$TEST_RULE_ID | jq '{id, name, rule_type, priority, version}'

# 4. rule_type 다시 변경 (constraint → optimization)
echo -e "\n=== 4. rule_type 다시 변경 ==="
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "rule_update": {
      "rule_type": "optimization"
    }
  }' \
  http://localhost:8000/api/v1/dispatch-rules/$TEST_RULE_ID | jq '{id, name, rule_type, priority, version}'

# 5. 최종 상태 확인
echo -e "\n=== 5. 최종 상태 ==="
curl -s http://localhost:8000/api/v1/dispatch-rules/$TEST_RULE_ID | jq '{id, name, rule_type, priority, version, is_active}'

# 6. 삭제
echo -e "\n=== 6. 규칙 삭제 ==="
curl -s -X DELETE http://localhost:8000/api/v1/dispatch-rules/$TEST_RULE_ID -w "HTTP Status: %{http_code}\n"

# 7. 삭제 확인
echo -e "\n=== 7. 삭제 확인 (404 예상) ==="
curl -s http://localhost:8000/api/v1/dispatch-rules/$TEST_RULE_ID -w "\nHTTP Status: %{http_code}\n"

# 예상 결과:
# - version이 생성(1) → 수정(2) → rule_type 변경(3) → rule_type 재변경(4) 순으로 증가
# - 최종 rule_type: "optimization"
# - 삭제 후 404 에러
```

---

## 📊 예상 결과

### ✅ 성공 시:

**테스트 1 (rule_type 변경):**
```json
{
  "id": 1,
  "name": "제약조건_테스트",
  "rule_type": "constraint",  ← "assignment"에서 변경됨
  "version": 11                ← 버전 증가
}
```

**테스트 2 (Hard delete):**
```
HTTP Status: 204             ← 삭제 성공
HTTP Status: 404             ← 삭제 후 조회 실패 (정상)
```

**Backend 로그:**
```
Successfully deleted rule 2
```

### ❌ 실패 시:

**테스트 1 실패:**
```json
{
  "detail": "Invalid rule_type"
}
```
→ 백엔드 재시작 필요

**테스트 2 실패:**
```json
{
  "id": 2,
  "is_active": false  ← soft delete (이전 방식)
}
```
→ 코드 수정 미반영

---

## 🔧 문제 해결

### 문제 1: rule_type 변경이 안됨
```bash
# Backend 로그 확인
docker logs uvis-backend --tail 50 | grep -i "rule_type\|error"

# Backend 재시작
docker-compose restart backend
sleep 10
```

### 문제 2: 삭제 후에도 규칙이 남아있음
```bash
# DB 직접 확인
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT id, name, is_active FROM dispatch_rules WHERE id=2;"

# 이전 방식(soft delete)이면 코드 미반영
# → 파일 재확인 및 재배포
```

### 문제 3: 삭제 시 에러 발생
```bash
# 외래 키 제약 조건 에러 가능성
# RuleExecutionLog도 함께 삭제하는 코드가 포함됨
docker logs uvis-backend --tail 20 | grep -i "foreign\|constraint"
```

---

## 📝 체크리스트

배포 후 확인:

- [ ] Backend 재시작 완료
- [ ] Backend 로그에 에러 없음
- [ ] 테스트 1: rule_type 변경 성공
- [ ] 테스트 2: Hard delete 성공 (404 확인)
- [ ] 테스트 3: 통합 테스트 모두 통과
- [ ] 기존 규칙(ID=1) 정상 작동

---

## 💡 추가 참고

### 변경 파일:
- `backend/app/api/v1/endpoints/dispatch_rules.py`
  - Line 42-52: `DispatchRuleUpdate` 스키마에 `rule_type` 추가
  - Line 283-299: DELETE 엔드포인트 hard delete로 변경

### Git 커밋 메시지 예시:
```
feat: Allow rule_type update and implement hard delete for dispatch rules

- Add rule_type field to DispatchRuleUpdate schema
- Change DELETE endpoint from soft delete to hard delete
- Delete related RuleExecutionLog entries on rule deletion

Closes #123
```

