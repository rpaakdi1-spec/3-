# 네비게이션 설정 통합 가이드

## 📋 개요

사이드바 메뉴 설정을 **한 곳에서 중앙 관리**하도록 통합했습니다.

## 🎯 변경 사항

### 이전 (Before)
- ❌ `Sidebar.tsx`: 메뉴 항목 51-89줄에 하드코딩
- ❌ `BottomNavigation.tsx`: 모바일 메뉴 11-17줄에 별도 관리
- ❌ 권한 필터링 로직이 각 컴포넌트에 중복

### 현재 (After)
- ✅ `config/navigation.ts`: **모든 메뉴 설정을 한 파일에서 관리**
- ✅ `Sidebar.tsx`: 중앙 설정 사용
- ✅ `BottomNavigation.tsx`: 중앙 설정 사용
- ✅ 권한 필터링 로직 통합

## 📁 파일 구조

```
frontend/src/
├── config/
│   └── navigation.ts          # 🎯 메뉴 설정 중앙 관리
├── components/
│   ├── common/
│   │   ├── Sidebar.tsx        # ✅ 중앙 설정 사용
│   │   └── Layout.tsx
│   └── mobile/
│       └── BottomNavigation.tsx  # ✅ 중앙 설정 사용
```

## 🔧 메뉴 추가/수정 방법

### 1. 새 메뉴 추가

**`config/navigation.ts`만 수정하면 됩니다:**

```typescript
export const navigationConfig: MenuItem[] = [
  // ... 기존 메뉴들 ...
  
  // 새 메뉴 추가
  { 
    path: '/new-feature', 
    label: '새 기능', 
    icon: Star,  // lucide-react 아이콘
    roles: ['ADMIN', 'DISPATCHER'],  // 접근 권한
    isNew: true,  // NEW 배지 표시
    mobileVisible: true  // 모바일 하단 네비게이션에 표시
  },
];
```

### 2. 서브메뉴가 있는 메뉴 추가

```typescript
{ 
  path: '/reports', 
  label: '리포트', 
  icon: FileText, 
  roles: ['ADMIN', 'DISPATCHER'],
  children: [
    { 
      path: '/reports/daily', 
      label: '일일 리포트', 
      icon: Calendar, 
      roles: ['ADMIN', 'DISPATCHER'] 
    },
    { 
      path: '/reports/monthly', 
      label: '월간 리포트', 
      icon: BarChart3, 
      roles: ['ADMIN'] 
    },
  ]
},
```

### 3. 권한 설정

```typescript
roles: ['ADMIN']              // ADMIN만 접근 가능
roles: ['DISPATCHER']         // DISPATCHER만 접근 가능
roles: ['ADMIN', 'DISPATCHER']  // 둘 다 접근 가능
```

### 4. 모바일 네비게이션 설정

```typescript
mobileVisible: true   // 모바일 하단 네비게이션에 표시
mobileVisible: false  // 표시 안 함 (기본값)
```

**권장:** 모바일 하단에는 **최대 5개 메뉴**만 표시하세요.

## 🎨 아이콘 사용

`lucide-react` 라이브러리 사용:

```typescript
import { 
  Home,        // 홈
  Package,     // 주문
  Truck,       // 배차
  Users,       // 사용자
  Settings,    // 설정
  BarChart3,   // 분석
  Calendar,    // 캘린더
  // ... 더 많은 아이콘들
} from 'lucide-react';
```

[아이콘 목록 보기](https://lucide.dev/icons/)

## 🔍 유틸리티 함수

### filterMenuByRole

사용자 권한에 따라 메뉴 필터링:

```typescript
import { filterMenuByRole, navigationConfig } from '@/config/navigation';

const userRole = 'ADMIN';
const filteredMenu = filterMenuByRole(navigationConfig, userRole);
```

### getMobileNavigation

모바일 네비게이션용 메뉴만 추출:

```typescript
import { getMobileNavigation, navigationConfig } from '@/config/navigation';

const mobileMenu = getMobileNavigation(navigationConfig);
```

## 📊 인터페이스

```typescript
interface MenuItem {
  path: string;           // 라우트 경로
  label: string;          // 메뉴 이름
  icon: LucideIcon;       // 아이콘
  roles: string[];        // 접근 권한 배열
  isNew?: boolean;        // NEW 배지 표시 여부
  children?: MenuItem[];  // 서브메뉴
  mobileVisible?: boolean; // 모바일 네비게이션 표시 여부
}
```

## ✅ 장점

1. **단일 진실 공급원 (Single Source of Truth)**
   - 메뉴 설정이 한 곳에만 있음
   
2. **유지보수 용이**
   - 메뉴 추가/수정 시 한 파일만 수정
   
3. **일관성 보장**
   - 사이드바와 모바일 네비게이션이 동일한 설정 사용
   
4. **타입 안정성**
   - TypeScript 인터페이스로 타입 체크
   
5. **권한 관리 간소화**
   - 권한 필터링 로직 중복 제거

## 🚀 마이그레이션 완료

- ✅ `config/navigation.ts` 생성
- ✅ `Sidebar.tsx` 업데이트
- ✅ `BottomNavigation.tsx` 업데이트
- ✅ 기존 기능 모두 유지
- ✅ 코드 중복 제거

## 💡 예제: 메뉴 순서 변경

`config/navigation.ts`에서 배열 순서만 바꾸면 됩니다:

```typescript
export const navigationConfig: MenuItem[] = [
  { path: '/orders', label: '주문 관리', ... },      // 첫 번째로 이동
  { path: '/dashboard', label: '대시보드', ... },    // 두 번째로 이동
  // ...
];
```

## 🎯 다음 단계

더 고급 기능이 필요하면:

1. **동적 메뉴 로딩**: API에서 메뉴 설정 가져오기
2. **메뉴 즐겨찾기**: 사용자별 메뉴 커스터마이징
3. **메뉴 검색**: 메뉴 이름으로 빠른 검색
4. **메뉴 카테고리**: 메뉴를 카테고리별로 그룹화

## ❓ 문제 해결

### Q: 새 메뉴가 안 보여요
A: 다음을 확인하세요:
- `roles` 배열에 사용자 권한이 포함되어 있는지
- 라우트가 `App.tsx`에 등록되어 있는지
- 브라우저 캐시를 지웠는지

### Q: 모바일에서 메뉴가 안 보여요
A: `mobileVisible: true` 설정을 추가하세요.

### Q: 서브메뉴가 작동 안 해요
A: `children` 배열을 올바르게 설정했는지 확인하세요.

---

**작성일**: 2026-02-25  
**작성자**: Claude AI Developer
