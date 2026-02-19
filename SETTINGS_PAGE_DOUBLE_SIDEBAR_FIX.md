# 설정 페이지 이중 사이드바 문제 해결

## 📋 문제 설명

설정 페이지(/settings)에서 **사이드바가 2개 표시**되는 문제가 발생했습니다.

### 문제 원인
1. **Layout 컴포넌트**가 이미 왼쪽 메인 사이드바를 포함
2. **SettingsPage 내부**에서 추가로 세로 탭 네비게이션을 구현
3. 결과: 사이드바 2개가 동시에 표시됨

```
┌─────────┬─────────┬─────────────────┐
│  메인   │  설정   │                 │
│사이드바 │  탭     │   컨텐츠        │
│         │사이드바 │                 │
└─────────┴─────────┴─────────────────┘
    ❌        ❌          ✅
  (중복)    (중복)
```

## ✅ 해결 방법

설정 페이지 내부의 **세로 탭을 가로 탭으로 변경**했습니다.

### Before (세로 탭 - 이중 사이드바 발생)
```tsx
<div className="grid grid-cols-12 gap-6">
  {/* Sidebar */}
  <div className="col-span-12 md:col-span-3">
    <Card className="p-2">
      <nav className="space-y-1">
        {tabs.map((tab) => (
          <button className="w-full flex items-center px-4 py-3">
            {tab.label}
          </button>
        ))}
      </nav>
    </Card>
  </div>
  
  {/* Content */}
  <div className="col-span-12 md:col-span-9">
    ...
  </div>
</div>
```

### After (가로 탭 - 단일 사이드바)
```tsx
{/* Horizontal Tabs */}
<div className="mb-6 border-b border-gray-200">
  <nav className="flex space-x-8">
    {tabs.map((tab) => (
      <button
        className={`flex items-center px-1 py-4 border-b-2 ${
          activeTab === tab.id
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500'
        }`}
      >
        <tab.icon size={20} className="mr-2" />
        {tab.label}
      </button>
    ))}
  </nav>
</div>

{/* Content */}
<div>
  ...
</div>
```

## 📊 변경 사항

### 레이아웃 구조 변경

**Before:**
```
┌─────────┬─────────┬─────────────────┐
│  메인   │  설정   │                 │
│사이드바 │  탭     │   컨텐츠        │
│         │사이드바 │                 │
│  HOME   │ 프로필  │  프로필 폼      │
│  주문   │ 알림    │                 │
│  배차   │ 보안    │                 │
│  설정   │ 시스템  │                 │
└─────────┴─────────┴─────────────────┘
```

**After:**
```
┌─────────┬─────────────────────────────┐
│  메인   │                             │
│사이드바 │    프로필 | 알림 | 보안 | 시스템│  ← 가로 탭
│         │    ─────                    │
│  HOME   │                             │
│  주문   │      프로필 폼              │
│  배차   │                             │
│  설정   │                             │
└─────────┴─────────────────────────────┘
```

### UI 개선 사항

1. **공간 효율성 향상**
   - 세로 공간 절약
   - 더 넓은 컨텐츠 영역

2. **사용자 경험 개선**
   - 탭 전환이 더 직관적
   - 현대적인 탭 디자인 (하단 밑줄)

3. **반응형 디자인**
   - 모바일에서도 잘 작동
   - 스크롤 가능한 탭

## 🚀 배포 방법

### 서버에서 실행할 명령어

```bash
# 1. 프론트엔드 디렉토리로 이동
cd /root/uvis/frontend

# 2. 최신 코드 가져오기
git fetch origin main
git reset --hard origin/main

# 3. 최신 커밋 확인 (f74be44 이어야 함)
git log --oneline -1

# 4. 변경사항 확인
grep -n "Horizontal Tabs" src/pages/SettingsPage.tsx

# 5. 프론트엔드 빌드
npm run build

# 6. 빌드 결과물을 컨테이너에 복사
docker cp dist/. uvis-frontend:/usr/share/nginx/html/

# 7. 프론트엔드 컨테이너 재시작
docker restart uvis-frontend

# 8. 10초 대기 후 상태 확인
sleep 10
docker ps | grep uvis-frontend
```

또는 자동 배포 스크립트 사용:
```bash
./DEPLOY_SETTINGS_HORIZONTAL_TABS.sh
```

## 🧪 테스트 방법

### 1. 브라우저 캐시 완전 삭제
- `Ctrl+Shift+Delete` 누르기
- **전체 기간** 선택
- **캐시된 이미지 및 파일** 체크
- **삭제** 버튼 클릭

### 2. InPrivate/시크릿 모드로 접속
```
http://139.150.11.99/settings
```

### 3. 확인 사항

#### ✅ 정상 동작
- [ ] 왼쪽 메인 사이드바 **1개만** 표시
- [ ] 설정 페이지 상단에 **가로 탭** 표시
- [ ] 탭 구성: `프로필 | 알림 설정 | 보안 | 시스템`
- [ ] 각 탭 클릭 시 컨텐츠 변경
- [ ] 활성 탭은 **파란색 밑줄** 표시
- [ ] 아이콘과 텍스트가 함께 표시

#### ❌ 비정상 동작
- 여전히 사이드바 2개 표시
- 탭이 세로로 표시
- 레이아웃이 깨짐

## 🐛 문제 해결

### 문제가 계속되면

1. **브라우저 개발자 도구 열기** (F12)

2. **Console 탭 확인**
   - 에러 메시지 확인
   - 스크린샷 캡처

3. **Network 탭 확인**
   - `SettingsPage-XXXXX.js` 파일 찾기
   - 상태가 `200 OK`인지 확인
   - 파일이 새로 로드되는지 확인

4. **강제 새로고침**
   - `Ctrl+Shift+R` (Windows/Linux)
   - `Cmd+Shift+R` (Mac)

5. **다른 브라우저에서 테스트**
   - Chrome 시크릿 모드
   - Edge InPrivate
   - Firefox 사생활 보호 모드

## 📝 커밋 정보

### Git 커밋
- **Commit Hash**: `f74be44`
- **Message**: `fix: Convert settings page sidebar to horizontal tabs to resolve double sidebar issue`
- **Date**: 2026-02-19

### 변경된 파일
```
frontend/src/pages/SettingsPage.tsx
  - 1 file changed
  - 22 insertions(+)
  - 25 deletions(-)
```

### 주요 변경 사항
1. `grid-cols-12` 레이아웃 제거
2. 세로 탭 네비게이션 제거
3. 가로 탭 네비게이션 추가
4. 활성 탭 스타일 변경 (배경색 → 하단 밑줄)
5. 아이콘 위치 조정 (왼쪽 → 텍스트 앞)

## 📚 관련 문서

- [배포 스크립트](./DEPLOY_SETTINGS_HORIZONTAL_TABS.sh)
- [GitHub Commit](https://github.com/rpaakdi1-spec/3-/commit/f74be44)
- [Layout 컴포넌트](../frontend/src/components/common/Layout.tsx)

## 🎯 개선 효과

### Before vs After 비교

| 항목 | Before | After |
|-----|--------|-------|
| 사이드바 개수 | 2개 ❌ | 1개 ✅ |
| 탭 방향 | 세로 | 가로 |
| 공간 효율성 | 낮음 | 높음 |
| 사용자 경험 | 혼란 | 명확 |
| 모바일 지원 | 불편 | 편리 |

## ✨ 추가 개선 사항 (선택)

향후 개선 가능한 사항:

1. **스크롤 가능한 탭**
   - 많은 탭이 있을 경우 가로 스크롤 추가

2. **탭 애니메이션**
   - 탭 전환 시 부드러운 애니메이션

3. **키보드 네비게이션**
   - 화살표 키로 탭 이동

4. **접근성 개선**
   - ARIA 속성 추가
   - 스크린 리더 지원

## 📞 문의

문제가 계속되거나 추가 도움이 필요하면 알려주세요!

---

**작성일**: 2026-02-19  
**작성자**: AI Assistant  
**버전**: 1.0
