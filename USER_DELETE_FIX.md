# 🗑️ 사용자 삭제 기능 수정 가이드

## 🔍 문제점

사용자 삭제 버튼을 클릭해도 사용자가 목록에서 사라지지 않았습니다.

### 원인 분석

**백엔드 (이전):**
```python
# backend/app/api/auth.py (문제)
@router.delete("/users/{user_id}")
async def delete_user(...):
    user.is_active = False  # ❌ 단순 비활성화만
    db.commit()
```

**프론트엔드 목록 조회 (이전):**
```python
# 모든 사용자 조회 (비활성 사용자 포함)
const response = await api.get('/auth/users');  # ❌ 비활성 사용자도 표시됨
```

**결과:** 삭제해도 `is_active=false`로만 변경되고, 목록에는 계속 표시되어 삭제가 안 된 것처럼 보임

---

## ✅ 해결 방법

### 1. 백엔드: 실제 삭제 + 필터링 옵션 추가

**삭제 API 개선:**
```python
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    permanent: bool = False,  # 완전 삭제 옵션
    ...
):
    if permanent:
        # 완전 삭제: PendingEmployee 등 관련 데이터도 삭제
        db.query(PendingEmployee).filter(PendingEmployee.user_id == user_id).delete()
        db.delete(user)
        db.commit()
        return {"message": "사용자가 완전히 삭제되었습니다"}
    else:
        # 소프트 삭제: 비활성화만
        user.is_active = False
        db.commit()
        return {"message": "사용자가 비활성화되었습니다"}
```

**목록 조회 API 개선:**
```python
@router.get("/users")
async def get_users(
    show_inactive: bool = False,  # 비활성 사용자 표시 여부
    ...
):
    query = db.query(User)
    
    # 기본적으로 활성 사용자만
    if not show_inactive:
        query = query.filter(User.is_active == True)
    
    users = query.offset(skip).limit(limit).all()
    return UserListResponse(total=total, items=users)
```

### 2. 프론트엔드: 완전 삭제 + 활성 사용자만 표시

**삭제 함수 수정:**
```typescript
const handleDeleteUser = async (userId: number) => {
  if (!window.confirm('정말 이 사용자를 삭제하시겠습니까?\n\n⚠️ 이 작업은 되돌릴 수 없습니다.')) {
    return;
  }

  try {
    // permanent=true로 완전 삭제
    await api.delete(`/auth/users/${userId}?permanent=true`);
    toast.success('사용자가 삭제되었습니다');
    loadUsers();
  } catch (error) {
    toast.error('사용자 삭제에 실패했습니다');
  }
};
```

**목록 조회 수정:**
```typescript
const loadUsers = async () => {
  try {
    setLoading(true);
    // show_inactive=false로 활성 사용자만 조회
    const response = await api.get('/auth/users?show_inactive=false');
    setUsers(response.data.items || response.data);
  } catch (error) {
    toast.error('사용자 목록 조회에 실패했습니다');
  } finally {
    setLoading(false);
  }
};
```

---

## 📋 배포 방법

### 서버에서 실행 (/root/uvis)

```bash
cd /root/uvis

# 1. 최신 코드 가져오기
git pull origin main

# 2. 백엔드 재빌드
docker compose build backend

# 3. 재시작
docker compose up -d backend
sleep 10

# 4. 프론트엔드 재빌드
docker compose build frontend
docker compose up -d frontend
sleep 10

# 5. 확인
curl http://139.150.11.99/api/v1/health
curl -I http://139.150.11.99/
```

---

## 🧪 테스트 방법

### 1. 테스트 사용자 생성

**회원가입:**
- http://139.150.11.99/ 접속
- 회원가입 클릭
- `testdelete01` / `test123456` 로 가입

**관리자 승인:**
- admin / admin123 로그인
- 설정 → 사용자 관리 → Pending Users
- testdelete01 승인 (사원번호: T001)

### 2. 삭제 테스트

**방법 1: 완전 삭제 (현재 기본값)**
1. 설정 → 사용자 관리
2. testdelete01 찾기
3. 🗑️ 삭제 버튼 클릭
4. 확인 대화상자에서 "확인"
5. ✅ 사용자가 목록에서 즉시 사라짐
6. ✅ DB에서 완전히 제거됨

**방법 2: 소프트 삭제 (비활성화만)**

프론트엔드에서 `permanent=false`로 변경하면:
```typescript
await api.delete(`/auth/users/${userId}?permanent=false`);
```
- 사용자가 비활성화만 되고 DB에는 남음
- 목록에서는 사라짐 (활성 사용자만 표시)
- `show_inactive=true`로 조회하면 다시 보임

### 3. 데이터베이스 확인

```bash
# 삭제 전 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, username, email, is_active 
FROM users 
WHERE username = 'testdelete01';
"

# 완전 삭제 후 확인 (행이 없어야 함)
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, username, email, is_active 
FROM users 
WHERE username = 'testdelete01';
"
# 출력: (0 rows)
```

---

## 🔧 삭제 방식 비교

| 항목 | 소프트 삭제 (is_active=false) | 완전 삭제 (DB 제거) |
|------|---------------------------|------------------|
| **장점** | • 데이터 복구 가능<br>• 히스토리 보존<br>• 외래키 문제 없음 | • 깔끔한 DB 관리<br>• 즉시 목록에서 제거<br>• 개인정보 완전 삭제 |
| **단점** | • DB 용량 증가<br>• 목록 필터링 필요 | • 복구 불가능<br>• 관련 데이터 정리 필요 |
| **사용 사례** | • 임시 정지<br>• 재활성화 가능성 | • GDPR 준수<br>• 테스트 데이터 정리 |
| **현재 설정** | `permanent=false` | `permanent=true` ✅ |

---

## 📊 API 명세

### DELETE /api/v1/auth/users/{user_id}

**쿼리 파라미터:**
- `permanent` (boolean, optional, default: false)
  - `true`: 완전 삭제 (DB에서 제거)
  - `false`: 소프트 삭제 (비활성화)

**응답:**
```json
{
  "message": "사용자가 완전히 삭제되었습니다"
}
```

**에러 응답:**
```json
{
  "detail": "자기 자신을 삭제할 수 없습니다"
}
```

### GET /api/v1/auth/users

**쿼리 파라미터:**
- `show_inactive` (boolean, optional, default: false)
  - `true`: 모든 사용자 (활성 + 비활성)
  - `false`: 활성 사용자만

**응답:**
```json
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "username": "admin",
      "is_active": true,
      ...
    }
  ]
}
```

---

## ⚠️ 주의사항

### 1. 관련 데이터 정리
완전 삭제 시 다음 데이터도 함께 삭제됩니다:
- ✅ PendingEmployee (대기 중인 인사카드)
- ⚠️ TODO: Dispatch, Orders 등 (외래키 제약조건 확인 필요)

### 2. 자기 자신 삭제 불가
현재 로그인한 사용자는 자신을 삭제할 수 없습니다.

### 3. 관리자 권한 필요
사용자 삭제는 ADMIN 권한이 필요합니다.

---

## 🐛 문제 해결

### "삭제했는데 여전히 보임"
**원인:** 브라우저 캐시  
**해결:** Ctrl+Shift+R로 새로고침

### "외래키 제약조건 위반 에러"
**원인:** 다른 테이블에서 해당 사용자 참조 중  
**해결:** 
1. 소프트 삭제 사용 (`permanent=false`)
2. 또는 관련 데이터 먼저 삭제

```bash
# 관련 데이터 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT 
    tc.table_name, 
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
  ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND kcu.column_name LIKE '%user_id%';
"
```

---

## 📚 관련 파일

**백엔드:**
- `backend/app/api/auth.py` - 삭제 API 엔드포인트

**프론트엔드:**
- `frontend/src/components/settings/UserManagementTab.tsx` - 사용자 관리 UI

**커밋:**
- `c13c420` - fix: implement proper user deletion with permanent delete option and active user filtering

**저장소:**
https://github.com/rpaakdi1-spec/3-

---

## ✅ 체크리스트

배포 후 확인:
- [ ] 백엔드 재빌드 완료
- [ ] 프론트엔드 재빌드 완료
- [ ] 테스트 사용자 생성
- [ ] 삭제 버튼 클릭 시 목록에서 즉시 사라짐
- [ ] DB에서 실제로 제거됨 확인
- [ ] 자기 자신 삭제 시 에러 메시지 표시
- [ ] 관리자 권한 확인

---

**마지막 업데이트:** 2026-02-28  
**상태:** ✅ 수정 완료, 배포 대기 중
