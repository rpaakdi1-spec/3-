#!/bin/bash

# ===================================================================
# UI 문제 완전 수정 스크립트
# ===================================================================
# 이 스크립트는 다음 문제들을 해결합니다:
# 1. OrdersPage.tsx의 Layout 중복 제거
# 2. App.tsx의 /orders 라우트에서 LayoutWrapper 제거
# 3. 중앙 집중식 navigation.ts 설정 확인
# ===================================================================

set -e

echo "🔧 UI 문제 수정 시작..."
echo ""

# 현재 디렉토리 확인
if [ ! -d "src" ]; then
    echo "❌ 오류: frontend 디렉토리에서 실행해주세요"
    exit 1
fi

# 백업 생성
echo "📦 현재 상태 백업 중..."
cp src/pages/OrdersPage.tsx src/pages/OrdersPage.tsx.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
cp src/App.tsx src/App.tsx.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
echo "✅ 백업 완료"
echo ""

# 1. OrdersPage.tsx에서 Layout import 완전 제거
echo "1️⃣ OrdersPage.tsx 수정 중..."

# Git에서 클린 버전 가져오기
git checkout HEAD -- src/pages/OrdersPage.tsx

# Layout import가 있는지 확인
if grep -q "^import Layout from" src/pages/OrdersPage.tsx; then
    echo "⚠️  Layout import 발견됨 - 제거 중..."
    sed -i '/^import Layout from/d' src/pages/OrdersPage.tsx
    echo "✅ Layout import 제거 완료"
else
    echo "✅ Layout import 없음 (정상)"
fi

# Layout 태그가 있는지 확인
if grep -q "<Layout>" src/pages/OrdersPage.tsx; then
    echo "⚠️  Layout 태그 발견됨 - 제거 중..."
    
    # Python으로 정확하게 제거
    python3 << 'PYTHON_EOF'
with open("src/pages/OrdersPage.tsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

# <Layout>과 </Layout> 태그만 제거 (해당 라인 전체)
filtered_lines = []
for line in lines:
    stripped = line.strip()
    if stripped == "<Layout>" or stripped == "</Layout>":
        continue  # 이 라인은 건너뜀
    filtered_lines.append(line)

with open("src/pages/OrdersPage.tsx", "w", encoding="utf-8") as f:
    f.writelines(filtered_lines)

print("✅ Layout 태그 제거 완료")
PYTHON_EOF
else
    echo "✅ Layout 태그 없음 (정상)"
fi

echo ""

# 2. App.tsx에서 /orders 라우트의 LayoutWrapper 제거
echo "2️⃣ App.tsx 수정 중..."

# /orders 라우트에서 LayoutWrapper 제거
python3 << 'PYTHON_EOF'
import re

with open("src/App.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# /orders 라우트 패턴 찾기 및 수정
# 기존: <LayoutWrapper><OrdersPage /></LayoutWrapper>
# 수정: <ProtectedRoute><OrdersPage /></ProtectedRoute>

# 패턴 1: 여러 줄에 걸쳐 있는 경우
pattern1 = r'<Route\s+path="/orders"\s+element={\s*<LayoutWrapper>\s*<OrdersPage\s*/>\s*</LayoutWrapper>\s*}\s*/>'
replacement1 = '''<Route
              path="/orders"
              element={
                <ProtectedRoute>
                  <OrdersPage />
                </ProtectedRoute>
              }
            />'''

# 패턴 2: 한 줄로 되어 있는 경우
pattern2 = r'<Route\s+path="/orders"\s+element={<LayoutWrapper><OrdersPage\s*/></LayoutWrapper>}\s*/>'
replacement2 = '<Route path="/orders" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />'

content_modified = re.sub(pattern1, replacement1, content, flags=re.MULTILINE | re.DOTALL)
content_modified = re.sub(pattern2, replacement2, content_modified)

# 변경사항이 있는지 확인
if content != content_modified:
    with open("src/App.tsx", "w", encoding="utf-8") as f:
        f.write(content_modified)
    print("✅ /orders 라우트에서 LayoutWrapper 제거 완료")
else:
    print("✅ /orders 라우트가 이미 올바르게 설정되어 있습니다")
PYTHON_EOF

echo ""

# 3. navigation.ts 파일 확인
echo "3️⃣ 중앙 navigation 설정 확인 중..."

if [ ! -f "src/config/navigation.ts" ]; then
    echo "⚠️  navigation.ts 파일이 없습니다 - 생성 중..."
    mkdir -p src/config
    
    cat > src/config/navigation.ts << 'NAV_EOF'
import {
  Home,
  Package,
  Truck,
  Users,
  Building2,
  BarChart3,
  Settings,
  Radio,
  Calendar,
  Brain,
  DollarSign,
  Wrench,
  LineChart,
  Activity,
  Target,
  MessageSquare,
  Zap,
  TestTube,
  ThermometerSun,
  MoreHorizontal,
} from 'lucide-react';

export interface MenuItem {
  path: string;
  label: string;
  icon: React.ComponentType<{ className?: string; size?: number }>;
  roles?: string[];
  isNew?: boolean;
  children?: MenuItem[];
  mobileVisible?: boolean;
}

export const navigationConfig: MenuItem[] = [
  {
    path: '/dashboard',
    label: '대시보드',
    icon: Home,
    roles: ['ADMIN', 'DISPATCHER', 'DRIVER'],
    mobileVisible: true,
  },
  {
    path: '/orders',
    label: '주문 관리',
    icon: Package,
    roles: ['ADMIN', 'DISPATCHER'],
    mobileVisible: true,
  },
  {
    path: '/calendar',
    label: '배송 일정',
    icon: Calendar,
    roles: ['ADMIN', 'DISPATCHER'],
  },
  {
    path: '/dispatches',
    label: '배차 관리',
    icon: Truck,
    roles: ['ADMIN', 'DISPATCHER'],
  },
  {
    path: '/dispatch-rules',
    label: '배차 규칙',
    icon: Settings,
    roles: ['ADMIN'],
  },
  {
    path: '/dispatch/monitoring',
    label: 'AI 배차 모니터링',
    icon: Activity,
    roles: ['ADMIN'],
    isNew: true,
  },
  {
    path: '/ai-chat',
    label: 'AI 어시스턴트',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
  },
  {
    path: '/optimization',
    label: '경로 최적화',
    icon: Target,
    roles: ['ADMIN', 'DISPATCHER'],
  },
  {
    path: '/ai-cost',
    label: 'AI 비용 대시보드',
    icon: DollarSign,
    roles: ['ADMIN'],
  },
  {
    path: '/ab-test',
    label: 'A/B 테스트',
    icon: TestTube,
    roles: ['ADMIN'],
  },
  {
    path: '/realtime',
    label: '실시간 모니터링',
    icon: Radio,
    roles: ['ADMIN', 'DISPATCHER'],
    mobileVisible: true,
  },
  {
    path: '/temperature-monitoring',
    label: '온도 모니터링',
    icon: ThermometerSun,
    roles: ['ADMIN', 'DISPATCHER'],
  },
  {
    path: '/temperature-analytics',
    label: '온도 분석',
    icon: LineChart,
    roles: ['ADMIN'],
  },
  {
    path: '/billing',
    label: '정산 관리',
    icon: DollarSign,
    roles: ['ADMIN'],
    children: [
      {
        path: '/billing/financial-dashboard',
        label: '재무 대시보드',
        icon: BarChart3,
        roles: ['ADMIN'],
      },
      {
        path: '/billing/charge-preview',
        label: '요금 미리보기',
        icon: DollarSign,
        roles: ['ADMIN'],
      },
      {
        path: '/billing/auto-schedule',
        label: '자동 청구 일정',
        icon: Calendar,
        roles: ['ADMIN'],
      },
      {
        path: '/billing/settlement-approval',
        label: '정산 승인',
        icon: Target,
        roles: ['ADMIN'],
      },
      {
        path: '/billing/payment-reminder',
        label: '결제 알림',
        icon: MessageSquare,
        roles: ['ADMIN'],
      },
      {
        path: '/billing/export-task',
        label: '내보내기 작업',
        icon: Zap,
        roles: ['ADMIN'],
      },
    ],
  },
  {
    path: '/maintenance',
    label: '차량 정비',
    icon: Wrench,
    roles: ['ADMIN'],
  },
  {
    path: '/ml-predictions',
    label: 'ML 예측',
    icon: Brain,
    roles: ['ADMIN'],
  },
  {
    path: '/telemetry',
    label: '실시간 텔레메트리',
    icon: Activity,
    roles: ['ADMIN'],
  },
  {
    path: '/dispatch-optimization',
    label: '배차 최적화',
    icon: Target,
    roles: ['ADMIN'],
  },
  {
    path: '/analytics-dashboard',
    label: '분석 대시보드',
    icon: BarChart3,
    roles: ['ADMIN'],
  },
  {
    path: '/vehicles',
    label: '차량 관리',
    icon: Truck,
    roles: ['ADMIN', 'DISPATCHER'],
    mobileVisible: true,
  },
  {
    path: '/clients',
    label: '고객 관리',
    icon: Building2,
    roles: ['ADMIN', 'DISPATCHER'],
  },
  {
    path: '/analytics',
    label: '통계 분석',
    icon: BarChart3,
    roles: ['ADMIN'],
  },
  {
    path: '/ml-training',
    label: 'ML 모델 학습',
    icon: Brain,
    roles: ['ADMIN'],
  },
  {
    path: '/settings',
    label: '설정',
    icon: Settings,
    roles: ['ADMIN', 'DISPATCHER', 'DRIVER'],
    mobileVisible: true,
  },
  {
    path: '/more',
    label: '더보기',
    icon: MoreHorizontal,
    roles: ['ADMIN', 'DISPATCHER', 'DRIVER'],
    mobileVisible: true,
  },
];

/**
 * 사용자 권한에 따라 메뉴 필터링
 */
export const filterMenuByRole = (
  menuItems: MenuItem[],
  userRole: string
): MenuItem[] => {
  return menuItems
    .filter((item) => !item.roles || item.roles.includes(userRole))
    .map((item) => {
      if (item.children) {
        return {
          ...item,
          children: filterMenuByRole(item.children, userRole),
        };
      }
      return item;
    });
};

/**
 * 모바일 네비게이션 항목 가져오기
 */
export const getMobileNavigation = (menuItems: MenuItem[]): MenuItem[] => {
  return menuItems.filter((item) => item.mobileVisible);
};
NAV_EOF
    
    echo "✅ navigation.ts 파일 생성 완료"
else
    echo "✅ navigation.ts 파일 존재함"
fi

echo ""

# 4. 검증
echo "4️⃣ 수정 내용 검증 중..."
echo ""

echo "OrdersPage.tsx:"
echo "  - Layout import: $(grep -c '^import Layout from' src/pages/OrdersPage.tsx 2>/dev/null || echo '0')개 (0이어야 함)"
echo "  - <Layout> 태그: $(grep -c '<Layout>' src/pages/OrdersPage.tsx 2>/dev/null || echo '0')개 (0이어야 함)"
echo "  - </Layout> 태그: $(grep -c '</Layout>' src/pages/OrdersPage.tsx 2>/dev/null || echo '0')개 (0이어야 함)"
echo ""

echo "App.tsx /orders 라우트:"
grep -A3 'path="/orders"' src/App.tsx | head -5
echo ""

echo "navigation.ts:"
if [ -f "src/config/navigation.ts" ]; then
    echo "  ✅ 파일 존재 ($(wc -l < src/config/navigation.ts) 줄)"
else
    echo "  ❌ 파일 없음"
fi
echo ""

# 5. 빌드
echo "5️⃣ 프로젝트 빌드 중..."
npm run build 2>&1 | tail -30

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 빌드 성공!"
    echo ""
    echo "📋 다음 단계:"
    echo "1. Docker 재배포:"
    echo "   cd /root/uvis"
    echo "   docker-compose stop frontend"
    echo "   docker-compose rm -f frontend"
    echo "   docker rmi uvis-frontend"
    echo "   docker-compose build --no-cache frontend"
    echo "   docker-compose up -d frontend"
    echo ""
    echo "2. 브라우저에서 http://139.150.11.99 접속 후 Ctrl+F5로 강제 새로고침"
    echo ""
else
    echo ""
    echo "❌ 빌드 실패! 로그를 확인해주세요."
    exit 1
fi
