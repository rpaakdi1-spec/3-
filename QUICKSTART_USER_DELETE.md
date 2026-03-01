# 🗑️ 사용자 삭제 기능 수정 - 빠른 가이드

## 문제점
회원 삭제 버튼을 눌러도 목록에서 사라지지 않음 (에러 메시지는 없음)

## 원인
- 백엔드: 삭제 시 `is_active=false`로만 설정 (실제 DB 삭제 안 함)
- 프론트엔드: 비활성 사용자도 목록에 표시

## 해결
✅ **완전 삭제 옵션 추가** - `permanent=true` 파라미터로 DB에서 실제 삭제  
✅ **활성 사용자만 표시** - 목록 조회 시 `show_inactive=false` 기본값  
✅ **관련 데이터 정리** - PendingEmployee 등 함께 삭제

---

## 🚀 배포 (1분)

서버 `/root/uvis`에서:

```bash
cd /root/uvis
bash deploy_user_delete_fix.sh
```

또는 수동:
```bash
cd /root/uvis
git pull origin main
docker compose build backend frontend
docker compose up -d backend frontend
```

---

## 🧪 테스트 (2분)

1. **회원가입**: testdelete01 / test123456
2. **관리자 승인**: admin 로그인 → 승인
3. **삭제 테스트**: 설정 → 사용자 관리 → testdelete01 삭제
4. **확인**: 목록에서 즉시 사라짐 ✅

---

## 📊 변경사항

| API | 변경 전 | 변경 후 |
|-----|---------|---------|
| DELETE /auth/users/{id} | is_active=false만 | permanent=true로 실제 삭제 |
| GET /auth/users | 모든 사용자 | 활성 사용자만 (기본값) |

---

## 📚 문서
- **상세 가이드**: [`USER_DELETE_FIX.md`](USER_DELETE_FIX.md)
- **커밋**: `c13c420`, `94ee1d4`
- **저장소**: https://github.com/rpaakdi1-spec/3-

---

**상태**: ✅ 수정 완료, 배포 대기 중  
**배포 시간**: ~5분
