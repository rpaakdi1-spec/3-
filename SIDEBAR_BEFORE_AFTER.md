# 사이드바 통합 - 전후 비교

## 📊 아키텍처 변경

### 이전 구조 (Before)
```
┌─────────────────────────────────────────┐
│  Sidebar.tsx (295 lines)                │
│                                         │
│  ┌────────────────────────────────┐    │
│  │ Menu Items (Line 51-89)        │    │
│  │  - 38 menu items hardcoded     │    │
│  │  - Icon imports                │    │
│  │  - Roles configuration         │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │ Filter Logic (Line 108-143)    │    │
│  │  - 35 lines of filtering code  │    │
│  │  - Duplicate logic             │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  BottomNavigation.tsx (54 lines)        │
│                                         │
│  ┌────────────────────────────────┐    │
│  │ Mobile Menu (Line 11-17)       │    │
│  │  - 5 menu items hardcoded      │    │
│  │  - Separate configuration      │    │
│  │  - Different icons             │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘

❌ 문제점:
- 메뉴가 2곳에 분산
- 권한 로직 중복
- 유지보수 어려움
- 불일치 가능성
```

### 현재 구조 (After)
```
┌──────────────────────────────────────────────┐
│  config/navigation.ts (187 lines)            │
│  ⭐ Single Source of Truth                   │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │ navigationConfig                   │     │
│  │  - All menu items (38+)            │     │
│  │  - Icon definitions                │     │
│  │  - Roles configuration             │     │
│  │  - Mobile visibility flags         │     │
│  └────────────────────────────────────┘     │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │ filterMenuByRole()                 │     │
│  │  - Centralized filtering logic     │     │
│  └────────────────────────────────────┘     │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │ getMobileNavigation()              │     │
│  │  - Mobile menu extraction          │     │
│  └────────────────────────────────────┘     │
└──────────────────────────────────────────────┘
              │
              │ import
              ├──────────────────┬────────────────────┐
              │                  │                    │
              ▼                  ▼                    ▼
  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐
  │  Sidebar.tsx     │  │ BottomNav.tsx    │  │  Others... │
  │  (210 lines)     │  │  (51 lines)      │  │            │
  │                  │  │                  │  │            │
  │  Uses central    │  │  Uses central    │  │  Can use   │
  │  configuration   │  │  configuration   │  │  same      │
  └──────────────────┘  └──────────────────┘  └────────────┘

✅ 개선:
- 메뉴 설정 단일화
- 로직 중복 제거
- 유지보수 쉬움
- 일관성 보장
```

## 📝 코드 비교

### 메뉴 추가 시나리오

#### Before (이전)
```typescript
// ❌ 2개 파일을 수정해야 함

// 1. Sidebar.tsx 수정
const menuItems: MenuItem[] = [
  { path: '/dashboard', label: '대시보드', icon: Home, roles: ['ADMIN'] },
  { path: '/orders', label: '주문', icon: Package, roles: ['ADMIN'] },
  // + 새 메뉴 추가
  { path: '/reports', label: '리포트', icon: FileText, roles: ['ADMIN'] },
  // ...
];

// 2. BottomNavigation.tsx 수정
const navItems: BottomNavItem[] = [
  { path: '/dashboard', label: '대시보드', icon: LayoutDashboard },
  { path: '/orders', label: '주문', icon: Package },
  // + 새 메뉴 추가
  { path: '/reports', label: '리포트', icon: FileText },
  // ...
];
```

#### After (현재)
```typescript
// ✅ 1개 파일만 수정

// config/navigation.ts
export const navigationConfig: MenuItem[] = [
  { path: '/dashboard', label: '대시보드', icon: Home, roles: ['ADMIN'], mobileVisible: true },
  { path: '/orders', label: '주문', icon: Package, roles: ['ADMIN'], mobileVisible: true },
  // + 새 메뉴 추가 (한 곳에서만)
  { path: '/reports', label: '리포트', icon: FileText, roles: ['ADMIN'], mobileVisible: true },
  // ...
];
```

### 권한 필터링

#### Before (이전)
```typescript
// ❌ Sidebar.tsx에 35줄의 필터링 로직
const filteredMenuItems = menuItems.filter((item) => {
  const userRole = (user?.role || '').toUpperCase();
  const hasAccess = item.roles.includes(userRole);
  
  if (isDevelopment) {
    console.log(`메뉴 체크: "${item.label}" - role: "${userRole}"...`);
  }
  
  return hasAccess;
}).map(item => {
  if (item.children) {
    const userRole = (user?.role || '').toUpperCase();
    return {
      ...item,
      children: item.children.filter(child => {
        const hasAccess = child.roles.includes(userRole);
        
        if (isDevelopment) {
          console.log(`서브메뉴: "${child.label}"...`);
        }
        
        return hasAccess;
      })
    };
  }
  return item;
});
```

#### After (현재)
```typescript
// ✅ 단 3줄로 처리
const userRole = (user?.role || '').toUpperCase();
const menuItems = React.useMemo(
  () => filterMenuByRole(navigationConfig, userRole),
  [userRole]
);
```

## 📈 메트릭스

### 코드 라인 수
| 파일 | Before | After | 변화 |
|------|--------|-------|------|
| Sidebar.tsx | 295 | ~210 | -85 (-29%) |
| BottomNavigation.tsx | 54 | ~51 | -3 (-6%) |
| navigation.ts | 0 | 187 | +187 (new) |
| **합계** | **349** | **448** | **+99** |

> ℹ️ 전체 라인은 증가했지만, 실제로는 **중복 코드 88 라인이 제거**되고 **새로운 설정 파일이 추가**된 것입니다.

### 유지보수 포인트
| 작업 | Before | After | 개선율 |
|------|--------|-------|--------|
| 메뉴 추가 | 2개 파일 | 1개 파일 | **50%** |
| 권한 변경 | 2개 파일 | 1개 파일 | **50%** |
| 순서 변경 | 2개 파일 | 1개 파일 | **50%** |
| 아이콘 변경 | 2개 파일 | 1개 파일 | **50%** |

### 에러 가능성
| 시나리오 | Before | After |
|----------|--------|-------|
| 메뉴 불일치 | ⚠️ 가능 | ✅ 불가능 |
| 권한 불일치 | ⚠️ 가능 | ✅ 불가능 |
| 타입 에러 | ⚠️ 가능 | ✅ TypeScript 체크 |

## 🎯 실제 사용 예제

### Example 1: 메뉴 순서 변경
```typescript
// config/navigation.ts
export const navigationConfig: MenuItem[] = [
  // 순서만 바꾸면 사이드바와 모바일 네비게이션 모두 적용됨
  { path: '/orders', label: '주문 관리', ... },      // 1순위로
  { path: '/dashboard', label: '대시보드', ... },    // 2순위로
  { path: '/dispatches', label: '배차 관리', ... },  // 3순위로
];
```

### Example 2: 새 권한 추가
```typescript
// 모든 곳에 한 번에 적용
{ 
  path: '/orders', 
  label: '주문 관리', 
  icon: Package, 
  roles: ['ADMIN', 'DISPATCHER', 'VIEWER'],  // VIEWER 추가
  mobileVisible: true
}
```

### Example 3: 서브메뉴 추가
```typescript
{ 
  path: '/analytics', 
  label: '분석', 
  icon: BarChart3, 
  roles: ['ADMIN'],
  children: [
    { path: '/analytics/dashboard', label: '대시보드', icon: Home, roles: ['ADMIN'] },
    { path: '/analytics/reports', label: '리포트', icon: FileText, roles: ['ADMIN'], isNew: true },
  ]
}
```

## 🔍 마이그레이션 검증

### 체크리스트
- [x] `config/navigation.ts` 생성
- [x] `Sidebar.tsx` 리팩토링
- [x] `BottomNavigation.tsx` 리팩토링
- [x] TypeScript 타입 정의
- [x] 유틸리티 함수 구현
- [x] Import 경로 확인
- [ ] 빌드 테스트 (서버에서 실행 필요)
- [ ] 런타임 테스트 (서버에서 실행 필요)
- [ ] 권한별 메뉴 테스트 (서버에서 실행 필요)

### 예상 작동
1. **ADMIN 사용자**: 모든 메뉴 표시
2. **DISPATCHER 사용자**: DISPATCHER 권한 메뉴만 표시
3. **모바일 뷰**: mobileVisible: true 메뉴만 하단에 표시

## 💡 추가 개선 가능성

### Phase 2: 메뉴 그룹화
```typescript
export const navigationConfig = [
  {
    group: '운영',
    items: [
      { path: '/dashboard', ... },
      { path: '/orders', ... },
    ]
  },
  {
    group: '분석',
    items: [
      { path: '/analytics', ... },
      { path: '/reports', ... },
    ]
  }
];
```

### Phase 3: 동적 메뉴
```typescript
// API에서 메뉴 로드
const { data: menuConfig } = useQuery('menu-config', fetchMenuConfig);
const menuItems = filterMenuByRole(menuConfig, userRole);
```

### Phase 4: 메뉴 커스터마이징
```typescript
// 사용자별 즐겨찾기
const favoriteMenus = useFavoriteMenus();
const pinnedMenus = menuItems.filter(m => favoriteMenus.includes(m.path));
```

---

**작성일**: 2026-02-25  
**작성자**: Claude AI Developer  
**목적**: 사이드바 설정 통합 및 중복 코드 제거
