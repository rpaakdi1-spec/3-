# 422 Validation Error 해결 완료

## 🎯 문제 원인
프론트엔드에서 **email 필드를 제거**했지만, 백엔드 `UserBase` 스키마에서는 여전히 **필수(required)**로 설정되어 있어 422 Unprocessable Entity 에러 발생.

## ✅ 해결 방법
`backend/app/schemas/auth.py` 수정:
```python
# Before (line 16)
email: EmailStr

# After
email: Optional[EmailStr] = None
```

## 📦 커밋 정보
- **Commit 1**: `8ee6887` - "fix: make email optional in UserBase schema to fix 422 validation error"
- **Commit 2**: `56134a0` - "docs: add 422 validation error fix deployment guide"
- **GitHub**: https://github.com/rpaakdi1-spec/3-.git

## 🚀 서버 배포 명령어

```bash
cd /root/uvis

# 1. 최신 코드 가져오기
git pull origin main

# 2. 백엔드 재빌드 (캐시 없이)
docker-compose down backend
docker-compose build --no-cache backend
docker-compose up -d backend

# 3. 10초 대기 후 상태 확인
sleep 10
docker-compose ps

# 4. 헬스체크
curl http://139.150.11.99:8000/health

# 5. 백엔드 로그 확인
docker-compose logs backend | tail -50
```

**기대 출력:**
```json
{"status":"healthy","app_name":"Cold Chain Dispatch System","environment":"production"}
```

## 🧪 테스트 절차

### 1. 회원가입 (http://139.150.11.99/)
- **Step 1**: 사용자명 `testuser123`, 비밀번호 `test123456` ✅ Email 필드 없음
- **Step 2**: 이름 `홍길동`, 전화번호 `01012345678` → 자동 `010-1234-5678` ✅ 사원번호 필드 없음 (자동 생성)
- **Step 3**: 입사일 선택 ✅ 근무시간 필드 없음
- **Step 4**: 자격증 정보 (선택)
- **완료**: "회원가입이 완료되었습니다" 메시지 → 로그인 페이지 리다이렉트

### 2. 관리자 승인
- 로그인: `admin` / `admin123`
- **설정 → 사용자 관리 → Pending Users** 탭
- 대기 사용자 확인: `testuser123`, 사원번호 `PENDING_20260228_001`, 전화 `010-1234-5678`
- **Approve** 버튼 클릭
- 최종 사원번호 부여 (예: `D001`)
- "User approved successfully" 메시지

## 📊 변경 사항 요약

| 항목 | Before | After |
|------|--------|-------|
| **Email 필드** | 필수 (required) | 선택 (optional) |
| **사원번호** | 수동 입력 | 자동 생성 `PENDING_YYYYMMDD_XXX` |
| **전화번호 포맷** | 수동 입력 | 자동 하이픈 `###-####-####` |
| **근무시간** | 입력 필요 | 제거됨 ❌ |

## 📝 상세 가이드
전체 배포 가이드: [FIX_422_VALIDATION_ERROR.md](./FIX_422_VALIDATION_ERROR.md)

## ⚠️ 주의사항
1. **캐시 제거 필수**: `--no-cache` 옵션으로 빌드해야 변경사항 적용
2. **전화번호 형식**: 숫자만 입력하면 자동 포맷팅 (하이픈 자동 삽입)
3. **Email 생성**: email 미입력 시 `{username}@pending.local` 자동 생성
4. **사원번호 생성**: 승인 시 관리자가 최종 코드 부여 (예: `D001`, `E001`)

## 🔍 트러블슈팅

### 422 에러 계속 발생
```bash
# Docker 캐시 완전 제거
docker-compose down
docker system prune -f
docker-compose build --no-cache backend
docker-compose up -d
```

### 전화번호 형식 에러
- ✅ 프론트엔드에서 자동 포맷팅 (숫자만 입력하면 됨)
- ✅ 백엔드 검증: 12-13자 (하이픈 포함)

### 프론트엔드 email 필드 여전히 표시
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## ✅ 완료 체크리스트
- [x] 백엔드 스키마 수정 (`UserBase.email` → Optional)
- [x] 코드 커밋 및 푸시 (커밋 `8ee6887`, `56134a0`)
- [x] 배포 가이드 작성 (`FIX_422_VALIDATION_ERROR.md`)
- [ ] 서버 배포 (git pull + docker rebuild)
- [ ] 회원가입 테스트
- [ ] 관리자 승인 테스트
- [ ] 엔드투엔드 검증

## 다음 단계
1. **서버 관리자**: 위 배포 명령어 실행
2. **테스트 담당자**: 회원가입 → 승인 워크플로우 검증
3. **개발자**: 테스트 결과 피드백 반영
