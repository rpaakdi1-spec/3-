# 템플릿 관리 페이지 배포 가이드

## 📋 변경 사항 요약

### 1. **템플릿 관리 페이지 생성** ✅
- 파일: `frontend/src/pages/TemplateManagementPage.tsx`
- 기능:
  - 템플릿 목록 조회 (카드 뷰)
  - 검색 및 필터링 (고객명, 검색어)
  - 정렬 (최신순, 사용 횟수순, 이름순)
  - 템플릿 활성화/비활성화
  - 즐겨찾기 추가/제거
  - 템플릿 복제
  - 템플릿 삭제
  - 통계 대시보드 (전체/활성/즐겨찾기/사용 횟수)

### 2. **네비게이션 메뉴 추가** ✅
- 파일: `frontend/src/config/navigation.ts`
- 추가된 메뉴:
  - 경로: `/template-management`
  - 이름: `템플릿 관리`
  - 위치: `운영 관리` > `배차 관리` 아래
  - 아이콘: FileText
  - 권한: ADMIN, DISPATCHER
  - NEW 배지 표시

### 3. **라우팅 설정 추가** ✅
- 파일: `frontend/src/App.tsx`
- Lazy import 추가
- Route 경로 추가: `/template-management`

---

## 🚀 배포 단계

### Step 1: 서버 접속
```bash
ssh root@139.150.11.99
cd /root/uvis
```

### Step 2: Git 상태 확인
```bash
git status
```

### Step 3: 변경 사항 확인
```bash
# 수정된 파일 확인
git diff frontend/src/config/navigation.ts
git diff frontend/src/App.tsx

# 새로 생성된 파일 확인
cat frontend/src/pages/TemplateManagementPage.tsx | head -50
```

### Step 4: 프론트엔드 빌드 및 재시작
```bash
# 프론트엔드 이미지 빌드 (캐시 없이)
docker compose build --no-cache frontend

# 빌드 성공 확인 (에러가 없는지 확인)
echo $?  # 0이면 성공

# 컨테이너 재시작
docker compose up -d frontend

# 재시작 확인
docker compose ps frontend
docker compose logs frontend --tail=30
```

### Step 5: 브라우저에서 테스트
1. 브라우저 캐시 삭제: `Ctrl + Shift + R` (강력 새로고침)
2. 또는 시크릿 모드로 접속
3. URL: `http://139.150.11.99/template-management`
4. 사이드바 메뉴에서 `운영 관리` > `템플릿 관리` 확인

---

## 🎯 기능 테스트 체크리스트

### 템플릿 목록 페이지
- [ ] 템플릿 목록이 카드 형태로 표시됨
- [ ] 검색 기능 동작 (템플릿 이름, 고객명)
- [ ] 고객 필터 동작
- [ ] 정렬 기능 동작 (최신순/사용 횟수순/이름순)
- [ ] 통계 카드 표시 (전체/활성/즐겨찾기/총 사용 횟수)

### 템플릿 관리 기능
- [ ] 즐겨찾기 추가/제거 (별 아이콘 클릭)
- [ ] 활성화/비활성화 토글 (전원 아이콘)
- [ ] 템플릿 복제 기능
- [ ] 템플릿 삭제 (확인 다이얼로그 표시)

### 사이드바 메뉴
- [ ] "운영 관리" 섹션에 "템플릿 관리" 메뉴 표시
- [ ] NEW 배지 표시
- [ ] 메뉴 클릭 시 템플릿 관리 페이지로 이동

---

## 📊 현재 템플릿 데이터

서버의 현재 템플릿:
```sql
SELECT 
  id, 
  name, 
  client_name, 
  jsonb_array_length(template_data->'dispatches') as dispatch_count,
  usage_count,
  is_active,
  is_favorite,
  created_at
FROM dispatch_form_templates
ORDER BY created_at DESC;
```

예상 결과:
- ID 41: "이천배차 (월~토)" - 동원 (12건)
- ID 40: "도미노 백암 → 밀양"
- 기타 템플릿들...

---

## 🔍 문제 해결 가이드

### 1. 빌드 에러 발생 시
```bash
# 빌드 로그 확인
docker compose build frontend 2>&1 | tee build.log

# 에러 내용 확인
grep -i error build.log

# 문제가 있으면 해당 파일 수정 후 다시 빌드
```

### 2. 페이지가 표시되지 않을 때
```bash
# 프론트엔드 로그 확인
docker compose logs frontend --tail=100

# 브라우저 콘솔 확인 (F12)
# - JavaScript 에러 확인
# - Network 탭에서 API 호출 확인
```

### 3. 메뉴가 표시되지 않을 때
```bash
# 사용자 권한 확인 (DB에서)
psql -U uvis_user -d uvis_db -c "SELECT username, role FROM users WHERE username='your_username';"

# role이 'ADMIN' 또는 'DISPATCHER'인지 확인
```

### 4. API 에러 발생 시
```bash
# 백엔드 API 확인
curl http://localhost:8000/api/v1/dispatch-form/templates

# 백엔드 로그 확인
docker compose logs backend --tail=50
```

---

## 🎨 UI 스크린샷 예상 모습

### 템플릿 관리 페이지 구조:
```
┌─────────────────────────────────────────────────────┐
│ 📄 템플릿 관리        [+ 새 템플릿 만들기]         │
├─────────────────────────────────────────────────────┤
│ [검색] [고객 필터] [정렬]                           │
├─────────────────────────────────────────────────────┤
│ [전체: 9] [활성: 8] [즐겨찾기: 3] [총 사용: 109]   │
├─────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│ │ 이천배차 │ │ 도미노  │ │ 목우촌  │               │
│ │ 동원    │ │ 백암    │ │ 오후배차 │               │
│ │ 12건    │ │ 8건     │ │ 6건     │               │
│ │ 사용13회 │ │ 사용83회│ │ 사용13회│               │
│ │ [⚡][✏️][📋][🗑️] │                              │
│ └─────────┘ └─────────┘ └─────────┘               │
└─────────────────────────────────────────────────────┘
```

---

## 💡 다음 단계 (추가 개발 가능 항목)

### 1. 템플릿 생성/편집 모달
- 기본 정보 입력 (이름, 고객, 카테고리, 설명)
- 상차지 정보 (주소, 좌표, 시간)
- 하차지 정보 (주소, 좌표, 시간)
- 요일별 스케줄 설정
- 차량 타입, 톤수, 온도, 제품 타입, 파렛 수 입력

### 2. 템플릿 미리보기
- 템플릿 적용 시 어떻게 표시될지 미리보기
- 주간 스케줄 캘린더 뷰

### 3. Excel 업로드/다운로드
- 템플릿을 Excel로 내보내기
- Excel 파일로 템플릿 대량 등록

### 4. 템플릿 버전 관리
- 템플릿 수정 이력 추적
- 이전 버전으로 되돌리기

---

## 📝 Git 커밋 & 푸시

변경 사항을 저장하고 원격 저장소에 푸시하세요:

```bash
cd /root/uvis

# 변경 사항 확인
git status

# 변경 사항 스테이징
git add frontend/src/pages/TemplateManagementPage.tsx
git add frontend/src/config/navigation.ts
git add frontend/src/App.tsx

# 커밋
git commit -m "feat(template-management): add template management page

- Add TemplateManagementPage with full CRUD operations
- Add navigation menu item in Operations section
- Add route configuration in App.tsx
- Features:
  * Template list view with cards
  * Search and filter by client
  * Sort by name, usage count, date
  * Toggle active/inactive status
  * Add/remove favorites
  * Duplicate templates
  * Delete templates with confirmation
  * Statistics dashboard (total/active/favorite/usage)
"

# 원격 저장소에 푸시
git push origin genspark_ai_developer

# 푸시 성공 확인
echo "✅ Git 푸시 완료!"
```

---

## ✅ 배포 완료 확인

모든 단계가 완료되면:

1. ✅ 템플릿 관리 페이지 생성
2. ✅ 사이드바 메뉴 추가
3. ✅ 라우팅 설정 완료
4. ✅ 프론트엔드 빌드 성공
5. ✅ 컨테이너 재시작 완료
6. ✅ 브라우저에서 페이지 접근 가능
7. ✅ 모든 기능 정상 동작
8. ✅ Git 커밋 & 푸시 완료

**배포 완료!** 🎉

---

## 📞 지원

문제가 발생하면:
1. 위의 문제 해결 가이드 참조
2. 로그 파일 확인
3. 브라우저 개발자 도구 확인
4. Git 이력 확인

현재 작업 브랜치: `genspark_ai_developer`
배포 서버: `139.150.11.99`
웹 인터페이스: `http://139.150.11.99/template-management`
