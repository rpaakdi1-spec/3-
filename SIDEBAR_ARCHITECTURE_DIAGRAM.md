# 사이드바 통합 구조도

## 🏗️ 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    UVIS Frontend Application                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │
                    ┌─────────────▼─────────────┐
                    │   src/config/navigation.ts │
                    │   🌟 Single Source of Truth│
                    └─────────────┬─────────────┘
                                  │
                  ┌───────────────┼───────────────┐
                  │               │               │
                  ▼               ▼               ▼
          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
          │  Sidebar     │ │ BottomNav    │ │  Future      │
          │  Desktop     │ │ Mobile       │ │  Components  │
          └──────────────┘ └──────────────┘ └──────────────┘
```

## 📁 파일 구조

```
frontend/
├── src/
│   ├── config/
│   │   └── navigation.ts                    ⭐ 메뉴 중앙 관리
│   │       ├── navigationConfig[]           ← 모든 메뉴 항목
│   │       ├── filterMenuByRole()           ← 권한 필터링
│   │       ├── getMobileNavigation()        ← 모바일 필터링
│   │       └── MenuItem interface           ← 타입 정의
│   │
│   └── components/
│       ├── common/
│       │   ├── Layout.tsx                   ✅ 레이아웃 컨테이너
│       │   └── Sidebar.tsx                  ✅ 데스크톱 사이드바
│       │       └── import { navigationConfig, filterMenuByRole }
│       │
│       └── mobile/
│           └── BottomNavigation.tsx         ✅ 모바일 하단 네비
│               └── import { navigationConfig, getMobileNavigation }
│
└── NAVIGATION_CENTRALIZATION.md             📖 사용 가이드
```

## 🔄 데이터 흐름

```
┌────────────────────────────────────────────────────────────────┐
│ 1. 메뉴 정의 (config/navigation.ts)                            │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ export
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ export const navigationConfig: MenuItem[] = [                  │
│   {                                                            │
│     path: '/dashboard',                                        │
│     label: '대시보드',                                          │
│     icon: Home,                                                │
│     roles: ['ADMIN', 'DISPATCHER'],                            │
│     mobileVisible: true                                        │
│   },                                                           │
│   // ... more items                                           │
│ ]                                                              │
└────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│ 2a. Sidebar Component    │  │ 2b. BottomNav Component  │
└──────────────────────────┘  └──────────────────────────┘
                │                           │
                │ filterMenuByRole()        │ getMobileNavigation()
                ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│ 3a. Filtered by Role     │  │ 3b. Mobile Items Only    │
│                          │  │                          │
│ ADMIN → 모든 메뉴        │  │ mobileVisible: true만    │
│ DISPATCHER → 제한된 메뉴 │  │ 최대 5개 항목            │
└──────────────────────────┘  └──────────────────────────┘
                │                           │
                ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│ 4a. Render Desktop Menu  │  │ 4b. Render Mobile Menu   │
│                          │  │                          │
│ - 사이드바 왼쪽 표시     │  │ - 하단 네비게이션        │
│ - 서브메뉴 지원          │  │ - 아이콘 + 라벨          │
│ - 확장/축소              │  │ - 5개 이하 권장          │
└──────────────────────────┘  └──────────────────────────┘
```

## 🎨 컴포넌트 관계도

```
┌──────────────────────────────────────────────────────────┐
│                       App.tsx                            │
│                      (루트 컴포넌트)                      │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ├── /login → LoginPage (Layout 없음)
                   │
                   └── /* → Layout Component ─────────────┐
                                                          │
        ┌─────────────────────────────────────────────────┤
        │                                                 │
        ▼                                                 ▼
┌───────────────────┐                          ┌──────────────────┐
│  Desktop View     │                          │  Mobile View     │
│  (lg: min 1024px) │                          │  (< 1024px)      │
├───────────────────┤                          ├──────────────────┤
│                   │                          │                  │
│  ┌─────────────┐  │                          │  ┌────────────┐  │
│  │  Sidebar    │  │                          │  │   Header   │  │
│  │  (왼쪽)     │  │                          │  │            │  │
│  │             │  │                          │  └────────────┘  │
│  │  • 대시보드 │  │                          │                  │
│  │  • 주문관리 │  │                          │  ┌────────────┐  │
│  │  • 배차관리 │  │                          │  │  Content   │  │
│  │  • ...      │  │                          │  │            │  │
│  │             │  │                          │  └────────────┘  │
│  └─────────────┘  │                          │                  │
│                   │                          │  ┌────────────┐  │
│  ┌─────────────┐  │                          │  │  Bottom    │  │
│  │  Content    │  │                          │  │  Nav       │  │
│  │             │  │                          │  │            │  │
│  │             │  │                          │  │  🏠 📦 🚚  │  │
│  │             │  │                          │  │  📊 ⋯     │  │
│  └─────────────┘  │                          │  └────────────┘  │
│                   │                          │                  │
└───────────────────┘                          └──────────────────┘
```

## 🔐 권한 필터링 로직

```
┌──────────────────────────────────────────────────────────────┐
│                     navigationConfig                         │
│  [38+ menu items with roles]                                │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
              filterMenuByRole(items, userRole)
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
  User Role: ADMIN            User Role: DISPATCHER
        │                             │
        ├── ✅ Dashboard              ├── ✅ Dashboard
        ├── ✅ Orders                 ├── ✅ Orders
        ├── ✅ Dispatches             ├── ✅ Dispatches
        ├── ✅ AI Cost                ├── ❌ AI Cost (ADMIN only)
        ├── ✅ Analytics              ├── ❌ Analytics (ADMIN only)
        ├── ✅ Settings               ├── ❌ Settings (ADMIN only)
        └── ✅ All menus              └── ✅ Allowed menus only
```

## 📱 모바일 네비게이션 필터링

```
┌──────────────────────────────────────────────────────────────┐
│               Filtered Menu Items (by role)                  │
│  [All accessible items for current user]                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
              getMobileNavigation(items)
                       │
                       ▼
              Filter: mobileVisible === true
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
  Dashboard (✅)                Orders (✅)
  mobileVisible: true          mobileVisible: true
        │                             │
        ▼                             ▼
  Dispatches (✅)              Analytics (✅)
  mobileVisible: true          mobileVisible: true
        │                             │
        ▼                             ▼
  More (✅)                    AI Cost (❌)
  mobileVisible: true          mobileVisible: false
        │
        └─────────────────────────────────────┐
                                              │
                                              ▼
                        ┌────────────────────────────────┐
                        │  Mobile Bottom Navigation      │
                        │  [Max 5 items recommended]     │
                        │                                │
                        │  🏠 Dashboard                  │
                        │  📦 Orders                     │
                        │  🚚 Dispatches                 │
                        │  📊 Analytics                  │
                        │  ⋯  More                       │
                        └────────────────────────────────┘
```

## 🎯 메뉴 항목 구조

```
MenuItem {
  path: string                 ← "/dashboard"
  label: string                ← "대시보드"
  icon: LucideIcon             ← Home (from lucide-react)
  roles: string[]              ← ["ADMIN", "DISPATCHER"]
  isNew?: boolean              ← true (NEW 배지 표시)
  mobileVisible?: boolean      ← true (모바일 네비게이션에 표시)
  children?: MenuItem[]        ← 서브메뉴 배열
}

예제:
{
  path: '/billing',
  label: '청구/정산',
  icon: DollarSign,
  roles: ['ADMIN', 'DISPATCHER'],
  children: [
    {
      path: '/billing/financial-dashboard',
      label: '재무 대시보드',
      icon: BarChart3,
      roles: ['ADMIN', 'DISPATCHER'],
      isNew: true
    },
    // ... more children
  ]
}
```

## 🔄 업데이트 사이클

```
1. 개발자가 config/navigation.ts 수정
                │
                ▼
2. npm run build (빌드)
                │
                ▼
3. React가 navigationConfig를 로드
                │
                ▼
4. 컴포넌트들이 중앙 설정 사용
                │
        ┌───────┴───────┐
        ▼               ▼
   Sidebar        BottomNav
        │               │
        └───────┬───────┘
                ▼
5. 사용자에게 일관된 메뉴 표시
```

## 📊 변경 전후 비교

### Before (분산 관리)
```
Sidebar.tsx                 BottomNavigation.tsx
├── Menu Items (38개)       ├── Menu Items (5개)
├── Filter Logic            ├── (권한 체크 없음)
└── Render Logic            └── Render Logic

❌ 문제:
• 메뉴 불일치 가능
• 중복 코드
• 유지보수 어려움
```

### After (중앙 관리)
```
            navigation.ts
            ├── Menu Items (38+개)
            ├── filterMenuByRole()
            └── getMobileNavigation()
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
   Sidebar.tsx            BottomNavigation.tsx
   └── Render Logic       └── Render Logic

✅ 개선:
• 단일 진실 공급원
• 중복 제거
• 쉬운 유지보수
```

---

**작성일**: 2026-02-25  
**작성자**: Claude AI Developer  
**목적**: 사이드바 통합 아키텍처 시각화
