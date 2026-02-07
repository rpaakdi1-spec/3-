# 사이드바 항상 확장 배포 가이드

## 🎯 변경 사항

**요청**: 전체메뉴 서브메뉴까지 사이드바가 모두 안사라지게 설정

**구현**:
- 모든 메뉴와 서브메뉴가 **항상 펼쳐진 상태**로 표시
- 메뉴 접기/펼치기 기능 비활성화
- 모든 서브메뉴 항목 항상 표시

---

## 📝 수정 내용

### 파일: `frontend/src/components/common/Sidebar.tsx`

#### 1. 항상 확장 상태 설정
```typescript
// ❌ 이전: 동적 확장/축소
const isExpanded = expandedMenus[item.path] || expandedMenus['billing'];
const ChevronIcon = isExpanded ? ChevronDown : ChevronRight;

// ✅ 수정: 항상 확장
const isExpanded = true; // 항상 확장 상태
const ChevronIcon = ChevronDown; // 항상 아래 화살표
```

#### 2. 토글 기능 비활성화
```typescript
// ❌ 이전: 메뉴 토글 가능
const toggleMenu = (key: string) => {
  setExpandedMenus(prev => ({ ...prev, [key]: !prev[key] }));
};

// ✅ 수정: 토글 비활성화
const toggleMenu = (key: string) => {
  // 아무 동작도 하지 않음 - 항상 확장 상태 유지
};
```

#### 3. 버튼 비활성화
```typescript
<button
  onClick={() => toggleMenu(item.path)}
  disabled                        // 클릭 비활성화
  style={{ cursor: 'default' }}   // 커서 변경 방지
  // ...
>
```

#### 4. 조건부 렌더링 제거
```typescript
// ❌ 이전: 조건부 표시
{isExpanded && (
  <ul>
    {/* 서브메뉴 */}
  </ul>
)}

// ✅ 수정: 항상 표시
{/* 항상 서브메뉴 표시 */}
<ul>
  {/* 서브메뉴 */}
</ul>
```

---

## 🚀 프로덕션 배포

### 빠른 배포 (한 줄)
```bash
cd /root/uvis && git fetch origin && git checkout phase8-verification && git pull origin phase8-verification && cd frontend && npm run build && cd .. && docker-compose build --no-cache frontend && docker-compose up -d frontend && echo "✅ 사이드바 항상 확장 배포 완료!"
```

**예상 소요 시간**: 3-4분

### 단계별 배포

#### 1. 최신 코드 가져오기
```bash
cd /root/uvis
git fetch origin
git checkout phase8-verification
git pull origin phase8-verification
```

**확인**:
```bash
git log --oneline -1
# 7b527ca feat(sidebar): Make all menus and submenus always expanded
```

#### 2. 프론트엔드 빌드
```bash
cd /root/uvis/frontend
npm run build
```

**예상 시간**: 10-15초

#### 3. Docker 재빌드 및 재시작
```bash
cd /root/uvis
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

**예상 시간**: 2-3분

#### 4. 배포 확인
```bash
docker ps | grep uvis-frontend
docker logs uvis-frontend --tail 30
```

---

## ✅ 배포 후 테스트

### 1. 브라우저 캐시 삭제 (필수!)
```
Ctrl+Shift+Delete (Windows/Linux)
Cmd+Shift+Delete (Mac)
→ "쿠키 및 캐시" 전체 삭제
```

**또는 강력 새로고침**:
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

### 2. 사이드바 확인

#### A. 기본 접속
1. URL: `http://139.150.11.99/`
2. 로그인: `admin` / `admin123`

#### B. 사이드바 상태 확인

**확인 사항**:

1. **청구/정산 메뉴**:
   - [ ] "청구/정산" 메뉴가 보임
   - [ ] 아래 화살표 (▼) 아이콘 표시
   - [ ] **6개 서브메뉴가 항상 보임** (확장된 상태):
     - [ ] 재무 대시보드 (NEW)
     - [ ] 요금 미리보기 (NEW)
     - [ ] 자동 청구 스케줄 (NEW)
     - [ ] 정산 승인 (NEW)
     - [ ] 결제 알림 (NEW)
     - [ ] 데이터 내보내기 (NEW)

2. **메뉴 클릭 동작**:
   - [ ] "청구/정산" 메뉴 클릭해도 **서브메뉴가 사라지지 않음**
   - [ ] 화살표 아이콘 변경 없음 (항상 ▼)
   - [ ] 커서가 기본 모양 (pointer 아님)

3. **다른 메뉴**:
   - [ ] 다른 메뉴들도 정상 동작
   - [ ] 서브메뉴가 없는 메뉴는 그대로 동작

4. **모바일 반응형**:
   - [ ] 모바일에서도 메뉴 햄버거 버튼 정상 동작
   - [ ] 사이드바 열면 모든 메뉴 보임

---

## 📊 기대 결과

### ✅ 변경 전 (이전)
```
청구/정산 ▶          ← 클릭하면 펼쳐짐
```

클릭 후:
```
청구/정산 ▼
  ├─ 재무 대시보드 (NEW)
  ├─ 요금 미리보기 (NEW)
  ├─ 자동 청구 스케줄 (NEW)
  ├─ 정산 승인 (NEW)
  ├─ 결제 알림 (NEW)
  └─ 데이터 내보내기 (NEW)
```

### ✅ 변경 후 (현재)
```
청구/정산 ▼          ← 항상 펼쳐진 상태
  ├─ 재무 대시보드 (NEW)
  ├─ 요금 미리보기 (NEW)
  ├─ 자동 청구 스케줄 (NEW)
  ├─ 정산 승인 (NEW)
  ├─ 결제 알림 (NEW)
  └─ 데이터 내보내기 (NEW)
```

**항상 이 상태로 유지됨!**

---

## 🎨 UI/UX 개선

### 장점
- ✅ **모든 메뉴 항상 표시** - 사용자가 모든 옵션을 한눈에 볼 수 있음
- ✅ **클릭 횟수 감소** - 서브메뉴를 펼치는 추가 클릭 불필요
- ✅ **더 빠른 네비게이션** - 원하는 페이지로 바로 이동 가능
- ✅ **일관된 UI** - 서브메뉴가 사라졌다 나타나는 혼란 방지

### 고려 사항
- ⚠️ **사이드바 높이 증가** - 서브메뉴가 많으면 스크롤 필요할 수 있음
  - 현재: 청구/정산 6개 서브메뉴 → 문제없음
  - 해결: 사이드바 내부 스크롤 (`overflow-y-auto`) 이미 적용됨

---

## 🐛 문제 해결

### 서브메뉴가 여전히 숨겨지는 경우

#### 1. 브라우저 캐시 문제
```bash
# 시크릿/프라이빗 모드로 테스트
Ctrl+Shift+N (Chrome)
Ctrl+Shift+P (Firefox)
```

#### 2. 빌드 파일 확인
```bash
cd /root/uvis/frontend
ls -lh dist/assets/ | grep Sidebar
# 최신 시간의 Sidebar-*.js 파일 확인
```

#### 3. 컨테이너 재시작
```bash
docker-compose restart frontend
docker logs uvis-frontend --tail 30
```

#### 4. 완전 재빌드
```bash
cd /root/uvis
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 📝 테스트 결과 보고 양식

```markdown
### 사이드바 항상 확장 테스트 결과

**배포 정보**:
- 배포 시간: [시간]
- 커밋: 7b527ca
- 브랜치: phase8-verification

**사전 준비**:
- [ ] 브라우저 캐시 삭제: 완료
- [ ] 강력 새로고침: 완료

**사이드바 테스트**:
- [ ] 청구/정산 메뉴 표시: 성공/실패
- [ ] 6개 서브메뉴 항상 표시: 성공/실패
- [ ] 서브메뉴 목록:
  - [ ] 재무 대시보드 (NEW)
  - [ ] 요금 미리보기 (NEW)
  - [ ] 자동 청구 스케줄 (NEW)
  - [ ] 정산 승인 (NEW)
  - [ ] 결제 알림 (NEW)
  - [ ] 데이터 내보내기 (NEW)

**메뉴 클릭 동작**:
- [ ] 청구/정산 클릭해도 서브메뉴 유지: 예/아니오
- [ ] 화살표 아이콘: 항상 ▼ / 변경됨
- [ ] 커서 모양: 기본 / pointer

**모바일 반응형**:
- [ ] 햄버거 메뉴: 정상 동작
- [ ] 사이드바 열기/닫기: 정상 동작

**최종 평가**:
- [ ] ✅ 완전히 해결됨 - 모든 메뉴 항상 표시
- [ ] ⚠️ 부분적으로 해결됨
- [ ] ❌ 여전히 문제 있음

**추가 코멘트**:
[여기에 스크린샷 또는 상세 설명]
```

---

## 📸 스크린샷 요청

가능하면 다음 스크린샷을 공유해 주세요:

1. **사이드바 전체** - 청구/정산 메뉴와 6개 서브메뉴가 모두 보이는 화면
2. **NEW 배지** - 6개 서브메뉴에 녹색 NEW 배지 표시 확인
3. **모바일 뷰** (선택) - 모바일 반응형 확인

---

## 🔄 변경 커밋 정보

**커밋**: `7b527ca`  
**브랜치**: `phase8-verification`  
**날짜**: 2026-02-07

**변경 파일**:
- `frontend/src/components/common/Sidebar.tsx` (+40/-35 lines)

**주요 변경**:
- `isExpanded` 항상 `true`
- `ChevronIcon` 항상 `ChevronDown`
- `toggleMenu()` 비활성화
- 조건부 렌더링 제거
- 버튼 `disabled` 속성 추가

---

## 🎉 완료 후

모든 테스트가 통과하면:

**✅ 사이드바 항상 확장 성공!**
- 모든 메뉴 항상 표시 ✅
- 모든 서브메뉴 항상 표시 ✅
- 청구/정산 6개 항목 항상 보임 ✅
- NEW 배지 표시 ✅
- 더 나은 UX ✅

---

**지금 바로 배포하고 테스트해보세요!** 🚀

```bash
cd /root/uvis && git fetch origin && git checkout phase8-verification && git pull origin phase8-verification && cd frontend && npm run build && cd .. && docker-compose build --no-cache frontend && docker-compose up -d frontend && echo "✅ 사이드바 항상 확장 배포 완료!"
```

**작성일**: 2026-02-07  
**커밋**: 7b527ca  
**상태**: 즉시 배포 가능 ✅
