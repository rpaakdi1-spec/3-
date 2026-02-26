# ✅ Dispatch Rules API 업데이트 완료

## 📦 변경 내용

### 1. ✅ 규칙 타입 변경 가능
- **파일**: `backend/app/api/v1/endpoints/dispatch_rules.py`
- **Line 45**: `DispatchRuleUpdate` 스키마에 `rule_type` 필드 추가
- **기능**: assignment ↔ constraint ↔ optimization 간 자유롭게 변경 가능

### 2. ✅ Hard Delete 구현
- **파일**: `backend/app/api/v1/endpoints/dispatch_rules.py`
- **Line 283-299**: DELETE 엔드포인트 수정
- **변경**:
  - **Before**: Soft delete (`is_active = False`)
  - **After**: Hard delete (DB에서 완전히 삭제)
  - 관련 `RuleExecutionLog`도 함께 삭제
  - 삭제 성공 시 로그 기록

---

## 🚀 배포 방법 (자동)

### ✅ Git push 완료!
- **Commit**: `9cd8c3d`
- **Branch**: `main`
- **Repository**: https://github.com/rpaakdi1-spec/3-

### 서버에서 실행 (복사해서 붙여넣기)

```bash
ssh root@139.150.11.99
cd /root/uvis
git pull origin main
docker-compose restart backend
sleep 10
docker logs uvis-backend --tail 20
```

---

## 🧪 테스트 방법

### 테스트 1: rule_type 변경

```bash
# 현재 규칙 확인
curl -s http://localhost:8000/api/v1/dispatch-rules/1 | jq '{id, name, rule_type, version}'

# rule_type 변경 (assignment → constraint)
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{"rule_update": {"rule_type": "constraint", "name": "타입변경테스트"}}' \
  http://localhost:8000/api/v1/dispatch-rules/1 | jq '{id, name, rule_type, version}'

# 예상 결과:
# {
#   "id": 1,
#   "name": "타입변경테스트",
#   "rule_type": "constraint",  ← 변경됨!
#   "version": 11                ← 버전 증가
# }
```

### 테스트 2: Hard Delete

```bash
# 1. 새 규칙 생성
NEW_ID=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"삭제테스트","rule_type":"assignment","priority":1,"conditions":{},"actions":{}}' \
  http://localhost:8000/api/v1/dispatch-rules/ | jq -r '.id')

echo "생성된 ID: $NEW_ID"

# 2. 삭제
curl -X DELETE http://localhost:8000/api/v1/dispatch-rules/$NEW_ID -w "\nHTTP Status: %{http_code}\n"
# 예상: HTTP 204

# 3. 삭제 확인 (404 예상)
curl -s http://localhost:8000/api/v1/dispatch-rules/$NEW_ID -w "\nHTTP Status: %{http_code}\n"
# 예상: HTTP 404 (완전히 삭제됨)
```

---

## 📊 예상 결과

### ✅ 성공 시

**rule_type 변경:**
```json
{
  "id": 1,
  "name": "타입변경테스트",
  "rule_type": "constraint",
  "version": 11
}
```

**Hard Delete:**
```
HTTP Status: 204  ← 삭제 성공
HTTP Status: 404  ← 조회 실패 (정상)
```

**Backend 로그:**
```
Successfully deleted rule 2
```

---

## 📝 API 변경 사항

### PUT /api/v1/dispatch-rules/{rule_id}

**Before:**
```json
{
  "rule_update": {
    "name": "...",
    "priority": 100
  }
}
```

**After (rule_type 추가):**
```json
{
  "rule_update": {
    "name": "...",
    "rule_type": "constraint",  ← 새로 추가!
    "priority": 100
  }
}
```

### DELETE /api/v1/dispatch-rules/{rule_id}

**Before:**
- Soft delete (`is_active = False`)
- 규칙이 DB에 남아있음
- 재활성화 가능

**After:**
- Hard delete (완전 삭제)
- DB에서 제거됨
- 관련 로그도 함께 삭제
- 재활성화 불가능

---

## 🔧 문제 해결

### 문제 1: rule_type 변경이 안됨
```bash
# Backend 로그 확인
docker logs uvis-backend --tail 50 | grep -i "rule_type\|error"

# Backend 재시작
docker-compose restart backend
```

### 문제 2: 삭제 후에도 규칙이 남아있음
```bash
# DB 직접 확인
docker exec uvis-db psql -U uvis_user -d uvis_db \
  -c "SELECT id, name, is_active FROM dispatch_rules WHERE id=2;"

# is_active=false면 이전 방식(soft delete)
# → git pull 재확인 필요
```

### 문제 3: Foreign Key 에러
```bash
# RuleExecutionLog와의 관계 때문에 에러 발생 가능
# 하지만 코드에서 이미 처리함:
# db.query(RuleExecutionLog).filter(...).delete()

docker logs uvis-backend --tail 20 | grep -i "foreign\|constraint"
```

---

## 📋 체크리스트

배포 후 확인:

- [ ] `git pull origin main` 성공
- [ ] Backend 재시작 완료
- [ ] Backend 로그에 에러 없음
- [ ] 테스트 1: rule_type 변경 성공
- [ ] 테스트 2: Hard delete 성공 (HTTP 204)
- [ ] 테스트 3: 삭제 후 조회 실패 (HTTP 404)
- [ ] Backend 로그에 "Successfully deleted rule X" 메시지

---

## 💡 추가 정보

### Git Commit
```
feat: Allow rule_type update and implement hard delete for dispatch rules

- Add rule_type field to DispatchRuleUpdate schema for dynamic rule type changes
- Change DELETE endpoint from soft delete to hard delete
- Delete related RuleExecutionLog entries on rule deletion
- Log successful deletions for audit trail

Commit: 9cd8c3d
```

### 관련 파일
- `backend/app/api/v1/endpoints/dispatch_rules.py`
- `test_dispatch_rules_update.md` (상세 테스트 가이드)

### API 문서
- http://139.150.11.99:8000/docs

---

## 🎯 다음 단계

1. ✅ **Backend API 수정 완료**
2. ⏳ **서버 배포** ← 지금 여기!
3. ⏳ **Frontend Tailwind CSS 수정**
4. ⏳ **브라우저 UI 테스트**
5. ⏳ **최종 문서 작성**

