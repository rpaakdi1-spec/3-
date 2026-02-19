# 모바일 웹 최적화 가이드

## 📱 개요

UVIS Cold Chain 시스템의 모바일 웹 경험을 최적화하기 위한 컴포넌트 및 가이드입니다.

## ✨ 새로 추가된 모바일 컴포넌트

### 1. **MorePage** (`/more`)
- 모바일 하단 네비게이션의 "더보기" 메뉴
- 모든 기능에 쉽게 접근할 수 있는 메뉴 페이지
- 사용자 프로필, 시스템 설정, 로그아웃 등

```tsx
// 자동으로 /more 경로에서 표시됨
// BottomNavigation에서 "더보기" 탭 클릭 시 이동
```

### 2. **MobileFilterSheet**
- 하단에서 슬라이드업되는 필터 시트
- iOS 스타일의 바텀 시트
- 드래그하여 닫기 가능

```tsx
import { MobileFilterSheet, MobileFilterChip, MobileFilterGroup } from '../components/mobile/MobileFilterSheet';

<MobileFilterSheet
  isOpen={filterOpen}
  onClose={() => setFilterOpen(false)}
  onApply={handleApplyFilters}
  onReset={handleResetFilters}
  title="필터"
>
  <MobileFilterGroup title="상태">
    <MobileFilterChip
      label="전체"
      selected={status === 'all'}
      onClick={() => setStatus('all')}
    />
    <MobileFilterChip
      label="진행중"
      selected={status === 'in_progress'}
      onClick={() => setStatus('in_progress')}
      color="green"
    />
  </MobileFilterGroup>
</MobileFilterSheet>
```

### 3. **MobileSearchBar**
- 터치에 최적화된 검색 바
- 필터 버튼 통합
- 활성 필터 카운트 표시

```tsx
import { MobileSearchBar } from '../components/mobile/MobileFilterSheet';

<MobileSearchBar
  value={searchTerm}
  onChange={setSearchTerm}
  placeholder="주문 검색..."
  onFilterClick={() => setFilterOpen(true)}
  filterCount={activeFilterCount}
/>
```

### 4. **MobileListItem**
- 테이블 대신 사용하는 모바일 리스트 아이템
- 선택, 스와이프, 메뉴 등 모바일 인터랙션 지원
- 아바타, 뱃지, 부가 정보 표시

```tsx
import { MobileListItem, MobileListSection, MobileEmptyState } from '../components/mobile/MobileListItem';

<MobileListSection title="주문 목록" count={orders.length}>
  {orders.map(order => (
    <MobileListItem
      key={order.id}
      title={order.order_number}
      subtitle={`${order.client_name} • ${order.pallets}파레트`}
      badge={{ text: order.status, color: 'green' }}
      onClick={() => handleOrderClick(order)}
      selected={selectedIds.includes(order.id)}
      onSelectChange={(selected) => handleSelect(order.id, selected)}
    />
  ))}
</MobileListSection>
```

### 5. **MobileActionSheet**
- iOS 스타일 액션 시트
- 여러 액션을 선택할 수 있는 메뉴
- 위험한 액션은 빨간색으로 표시

```tsx
import { MobileActionSheet } from '../components/mobile/MobileActionSheet';

<MobileActionSheet
  isOpen={actionSheetOpen}
  onClose={() => setActionSheetOpen(false)}
  title="주문 작업"
  actions={[
    {
      label: '수정',
      icon: <Edit2 size={20} />,
      onClick: handleEdit,
    },
    {
      label: '삭제',
      icon: <Trash2 size={20} />,
      onClick: handleDelete,
      variant: 'danger',
    },
  ]}
/>
```

### 6. **MobileFAB** (Floating Action Button)
- 화면 하단에 떠있는 액션 버튼
- 주요 액션에 빠르게 접근

```tsx
import { MobileFAB } from '../components/mobile/MobileActionSheet';

<MobileFAB
  icon={<Plus size={24} />}
  label="주문 추가"
  onClick={() => setModalOpen(true)}
  position="bottom-right"
/>
```

### 7. **MobilePullToRefresh**
- 아래로 당겨서 새로고침
- 네이티브 앱과 유사한 UX

```tsx
import { MobilePullToRefresh } from '../components/mobile/MobileListItem';

<MobilePullToRefresh onRefresh={fetchOrders}>
  <MobileListSection>
    {/* 리스트 아이템들 */}
  </MobileListSection>
</MobilePullToRefresh>
```

### 8. **MobileSwipeableItem**
- 스와이프 액션이 있는 리스트 아이템
- 좌우 스와이프로 빠른 액션 실행

```tsx
import { MobileSwipeableItem } from '../components/mobile/MobileActionSheet';

<MobileSwipeableItem
  leftAction={{
    label: '완료',
    icon: <Check size={20} />,
    color: 'bg-green-500',
  }}
  rightAction={{
    label: '삭제',
    icon: <Trash2 size={20} />,
    color: 'bg-red-500',
  }}
  onSwipeLeft={handleComplete}
  onSwipeRight={handleDelete}
>
  <MobileListItem {...item} />
</MobileSwipeableItem>
```

---

## 🎨 모바일 최적화 CSS

`index.css`에 다음이 추가되었습니다:

### iOS 최적화
```css
/* 부드러운 스크롤 */
-webkit-overflow-scrolling: touch;

/* 텍스트 크기 자동 조정 방지 */
-webkit-text-size-adjust: 100%;

/* 탭 하이라이트 제거 */
-webkit-tap-highlight-color: transparent;
```

### 터치 최적화
```css
/* 더 나은 터치 타겟 */
button, a, input {
  touch-action: manipulation;
  -webkit-touch-callout: none;
}
```

### 노치 디바이스 대응
```css
/* Safe Area 지원 */
.pb-safe {
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}
```

### 애니메이션
```css
.animate-fadeIn    /* 페이드 인 */
.animate-slideUp   /* 아래에서 위로 */
.animate-slideDown /* 위에서 아래로 */
.animate-scaleIn   /* 스케일 인 */
```

---

## 📐 반응형 브레이크포인트

기존 `useResponsive` 훅:

```typescript
const { isMobile, isTablet, isDesktop, windowSize } = useResponsive();

// isMobile: < 768px
// isTablet: 768px ~ 1024px
// isDesktop: >= 1024px
```

---

## 🚀 페이지별 적용 가이드

### OrdersPage 모바일 최적화 예시

```tsx
import { useResponsive } from '../hooks/useResponsive';
import { 
  MobileSearchBar, 
  MobileFilterSheet, 
  MobileFilterChip 
} from '../components/mobile/MobileFilterSheet';
import { 
  MobileListItem, 
  MobileListSection,
  MobilePullToRefresh 
} from '../components/mobile/MobileListItem';
import { MobileFAB } from '../components/mobile/MobileActionSheet';

const OrdersPage = () => {
  const { isMobile } = useResponsive();
  const [filterOpen, setFilterOpen] = useState(false);

  return (
    <Layout>
      {isMobile ? (
        <>
          {/* 모바일 검색 + 필터 */}
          <MobileSearchBar
            value={searchTerm}
            onChange={setSearchTerm}
            onFilterClick={() => setFilterOpen(true)}
            filterCount={activeFilters}
          />

          {/* Pull to Refresh */}
          <MobilePullToRefresh onRefresh={fetchOrders}>
            <MobileListSection title="주문 목록" count={filteredOrders.length}>
              {filteredOrders.map(order => (
                <MobileListItem
                  key={order.id}
                  title={order.order_number}
                  subtitle={`${order.client_name} • ${order.pallets}파레트`}
                  badge={{ text: order.status, color: getStatusColor(order.status) }}
                  onClick={() => navigate(`/orders/${order.id}`)}
                />
              ))}
            </MobileListSection>
          </MobilePullToRefresh>

          {/* FAB */}
          <MobileFAB
            icon={<Plus />}
            label="주문 추가"
            onClick={() => setModalOpen(true)}
          />

          {/* 필터 시트 */}
          <MobileFilterSheet
            isOpen={filterOpen}
            onClose={() => setFilterOpen(false)}
            onApply={handleApplyFilters}
            onReset={handleResetFilters}
          >
            {/* 필터 내용 */}
          </MobileFilterSheet>
        </>
      ) : (
        /* 데스크톱 테이블 뷰 */
        <table>...</table>
      )}
    </Layout>
  );
};
```

---

## ✅ 모바일 최적화 체크리스트

### 레이아웃
- [x] 하단 네비게이션 (BottomNavigation)
- [x] 더보기 페이지 (MorePage)
- [x] Safe Area 대응 (노치 디바이스)
- [x] 스크롤 영역 최적화

### 인터랙션
- [x] 터치 타겟 크기 (최소 44x44px)
- [x] 스와이프 제스처
- [x] Pull to Refresh
- [x] 바텀 시트
- [x] 액션 시트
- [x] FAB (Floating Action Button)

### 폼 & 입력
- [x] 큰 입력 필드
- [x] 검색 바 최적화
- [x] 필터 시트
- [ ] 음성 입력 (기존 VoiceOrderInput 활용)

### 성능
- [x] 부드러운 애니메이션
- [x] 터치 최적화 CSS
- [x] Lazy Loading (기존 구현)
- [ ] 이미지 최적화

### UX
- [x] 로딩 상태 표시
- [x] Empty State
- [x] 에러 처리
- [x] 터치 피드백

---

## 🎯 다음 단계

### 1. 기존 페이지에 모바일 컴포넌트 적용
- [ ] OrdersPage 모바일 뷰 개선
- [ ] DispatchesPage 모바일 뷰 개선
- [ ] VehiclesPage 모바일 뷰 개선
- [ ] ClientsPage 모바일 뷰 개선

### 2. 모바일 성능 최적화
- [ ] 이미지 lazy loading
- [ ] 번들 사이즈 최적화
- [ ] PWA 개선 (오프라인 지원)

### 3. 모바일 테스트
- [ ] iOS Safari 테스트
- [ ] Android Chrome 테스트
- [ ] 다양한 화면 크기 테스트
- [ ] 터치 제스처 테스트

---

## 📱 테스트 방법

### Chrome DevTools
1. F12 → 디바이스 툴바 켜기 (Ctrl+Shift+M)
2. 디바이스 선택 (iPhone 12, Galaxy S20 등)
3. 터치 시뮬레이션 활성화

### 실제 디바이스
```bash
# 로컬 네트워크에서 접속
npm run dev -- --host

# 표시된 네트워크 IP로 모바일에서 접속
# 예: http://192.168.0.100:5173
```

### 모바일 브라우저 디버깅
- **iOS**: Safari → 개발자 메뉴 → 디바이스 선택
- **Android**: Chrome → chrome://inspect → 디바이스 선택

---

## 🐛 문제 해결

### 하단 네비게이션이 보이지 않음
```tsx
// Layout.tsx에서 isMobile 확인
const { isMobile } = useResponsive();
{isMobile && <BottomNavigation />}
```

### 바텀 시트가 닫히지 않음
```tsx
// z-index 확인 (z-50 이상)
// backdrop onClick 이벤트 확인
```

### 터치 영역이 작음
```css
/* 최소 44x44px 확보 */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  touch-action: manipulation;
}
```

---

## 📚 참고 자료

- [Apple Human Interface Guidelines - Mobile](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design - Mobile](https://material.io/design/platform-guidance/android-bars.html)
- [Web.dev - Mobile Performance](https://web.dev/mobile/)

---

**작성일**: 2026-02-19  
**버전**: 1.0.0  
**작성자**: AI Assistant
