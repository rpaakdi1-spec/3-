# 🚀 빠른 배포 가이드

## 서버에서 실행할 명령어

```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 프로젝트 디렉토리로 이동
cd /root/uvis

# 3. 배포 스크립트 실행 (한 번에 모든 단계 완료)
bash DEPLOY_TEMPLATE_MANAGEMENT.sh
```

## 또는 수동으로 단계별 실행

```bash
cd /root/uvis

# 프론트엔드 빌드
docker compose build --no-cache frontend

# 컨테이너 재시작
docker compose up -d frontend

# 로그 확인
docker compose logs frontend --tail=30
```

## 웹 브라우저에서 확인

1. **캐시 삭제**: `Ctrl + Shift + R` (강력 새로고침)
2. **URL 접속**: `http://139.150.11.99/template-management`
3. **메뉴 확인**: 사이드바 > 운영 관리 > 템플릿 관리 (NEW)

## 주요 기능

### 템플릿 관리 페이지
- ✅ 템플릿 목록 (카드 뷰)
- ✅ 검색 & 필터 (고객명, 검색어)
- ✅ 정렬 (최신순, 사용 횟수, 이름)
- ✅ 즐겨찾기 ⭐
- ✅ 활성화/비활성화 ⚡
- ✅ 템플릿 복제 📋
- ✅ 템플릿 삭제 🗑️
- ✅ 통계 대시보드

### 사이드바 메뉴
```
운영 관리
├── 주문 관리
├── 오더 캘린더
├── 배차 관리
├── 템플릿 관리 ⭐ NEW
├── 배차 규칙 관리
└── ...
```

## Git 커밋 & 푸시

테스트 완료 후:

```bash
cd /root/uvis

# 변경 사항 추가
git add frontend/src/pages/TemplateManagementPage.tsx
git add frontend/src/config/navigation.ts
git add frontend/src/App.tsx

# 커밋
git commit -m "feat(template-management): add template management page

- Add TemplateManagementPage with CRUD operations
- Add navigation menu item
- Features: search, filter, sort, favorite, duplicate, delete
"

# 푸시
git push origin genspark_ai_developer
```

## 문제 해결

### 빌드 에러
```bash
# 빌드 로그 확인
docker compose build frontend 2>&1 | tee build.log
grep -i error build.log
```

### 페이지가 안 보일 때
```bash
# 로그 확인
docker compose logs frontend --tail=100

# 브라우저 콘솔 (F12) 확인
# - JavaScript 에러
# - Network 요청/응답
```

### 메뉴가 안 보일 때
- 로그아웃 후 다시 로그인
- 사용자 권한 확인 (ADMIN 또는 DISPATCHER)
- 브라우저 캐시 완전 삭제

## 생성된 파일

1. `frontend/src/pages/TemplateManagementPage.tsx` - 메인 페이지 컴포넌트
2. `frontend/src/config/navigation.ts` - 메뉴 설정 (수정)
3. `frontend/src/App.tsx` - 라우팅 설정 (수정)
4. `TEMPLATE_MANAGEMENT_DEPLOYMENT.md` - 상세 배포 가이드
5. `DEPLOY_TEMPLATE_MANAGEMENT.sh` - 자동 배포 스크립트
6. `QUICK_DEPLOY.md` - 이 파일

## 배포 체크리스트

- [ ] 서버 접속 완료
- [ ] 빌드 성공 (no error)
- [ ] 컨테이너 재시작 완료
- [ ] 브라우저 캐시 삭제
- [ ] 템플릿 관리 페이지 접근 가능
- [ ] 사이드바 메뉴 표시
- [ ] 템플릿 목록 로드
- [ ] 검색/필터 동작
- [ ] 즐겨찾기 토글
- [ ] 활성화/비활성화 토글
- [ ] 템플릿 복제 기능
- [ ] 템플릿 삭제 기능
- [ ] Git 커밋 & 푸시

---

**배포 완료 시간**: 약 5-10분  
**테스트 소요 시간**: 약 5-10분  
**총 소요 시간**: 약 10-20분

🎉 **모든 단계 완료 후 프로젝트에 새로운 템플릿 관리 기능이 추가됩니다!**
