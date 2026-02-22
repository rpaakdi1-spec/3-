#!/bin/bash
# 모든 페이지에 Sidebar 추가 (LoginPage 제외)

cd /home/user/webapp

# Sidebar가 없는 페이지 목록 (LoginPage 제외)
PAGES=(
  "AIChatPage.tsx"
  "AnalyticsPage.tsx"
  "BIDashboardPage.tsx"
  "ClientsPage.tsx"
  "DashboardPage.tsx"
  "DispatchesPage.tsx"
  "MLTrainingPage.tsx"
  "OptimizationPage.tsx"
  "OrderCalendarPage.tsx"
  "OrdersPage.tsx"
  "RealtimeDashboardPage.tsx"
  "ReportsPage.tsx"
  "TrackingPage.tsx"
  "VehiclesPage.tsx"
)

echo "🚀 Sidebar 일괄 추가 시작..."
echo ""

for page in "${PAGES[@]}"; do
  filepath="frontend/src/pages/$page"
  
  if [ ! -f "$filepath" ]; then
    echo "⚠️  파일 없음: $page"
    continue
  fi
  
  echo "📝 처리 중: $page"
  
  # 1. Sidebar import 추가 (이미 있으면 스킵)
  if ! grep -q "import.*Sidebar.*from.*components/common/Sidebar" "$filepath"; then
    # 마지막 import 문 다음에 Sidebar import 추가
    sed -i "/^import.*from.*;$/a import Sidebar from '../components/common/Sidebar';" "$filepath"
    echo "  ✅ Sidebar import 추가"
  else
    echo "  ℹ️  Sidebar import 이미 존재"
  fi
  
  # 2. return 문 찾아서 레이아웃 래핑
  # 간단한 패턴 매칭으로 처리
  # 주의: 복잡한 구조는 수동 확인 필요
  
  echo "  ⚠️  레이아웃 래핑은 수동 확인 필요"
  echo ""
done

echo "✅ Import 추가 완료!"
echo ""
echo "⚠️  주의: 각 페이지의 return 문을 수동으로 확인하고 레이아웃 래핑이 필요합니다."
echo "패턴:"
echo "  Before: return (<div>...</div>);"
echo "  After:  return (<div className=\"flex h-screen bg-gray-100\"><Sidebar /><div className=\"flex-1 overflow-auto\">...</div></div>);"
