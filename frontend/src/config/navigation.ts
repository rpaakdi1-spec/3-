import {
  Home, Package, Truck, Users, Building2, BarChart3, Settings, Radio, Calendar,
  Brain, Zap, MessageSquare, DollarSign, Activity, Thermometer, Wrench, Calculator,
  Clock, CheckSquare, Bell, Download, ListChecks, MoreHorizontal, FileText, Folder,
  TrendingUp, ClipboardList, Target, UserCheck, UsersRound
} from 'lucide-react';
import { LucideIcon } from 'lucide-react';

export interface MenuItem {
  path: string;
  label: string;
  icon: LucideIcon;
  roles: string[];
  isNew?: boolean;
  children?: MenuItem[];
  mobileVisible?: boolean;
}

export const navigationConfig: MenuItem[] = [
  // 📊 대시보드
  { 
    path: '/dashboard', 
    label: '대시보드', 
    icon: Home, 
    roles: ['ADMIN', 'DISPATCHER'], 
    mobileVisible: true 
  },
  
  // 📦 운영 관리
  {
    path: '/operations',
    label: '운영 관리',
    icon: Folder,
    roles: ['ADMIN', 'DISPATCHER'],
    children: [
      { path: '/orders', label: '주문 관리', icon: Package, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/calendar', label: '오더 캘린더', icon: Calendar, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/dispatches', label: '배차 관리', icon: Truck, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/dispatch-rules', label: '배차 규칙 관리', icon: ListChecks, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/vehicles', label: '차량 관리', icon: Truck, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/vehicle-driver-management', label: '차량-운전자 배정', icon: UserCheck, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      { path: '/employees', label: '인사 관리', icon: UsersRound, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      { path: '/clients', label: '거래처 관리', icon: Building2, roles: ['ADMIN', 'DISPATCHER'] }
    ]
  },
  
  // 🤖 AI & 최적화
  {
    path: '/ai',
    label: 'AI & 최적화',
    icon: Brain,
    roles: ['ADMIN', 'DISPATCHER'],
    children: [
      // { path: '/optimization', label: 'AI 배차 최적화', icon: Zap, roles: ['ADMIN', 'DISPATCHER'] },
      // { path: '/dispatch-optimization', label: '자동 배차 최적화', icon: Target, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/ai-cost', label: 'AI 비용 모니터링', icon: DollarSign, roles: ['ADMIN'] },
      { path: '/ab-test', label: 'AB Test 모니터링', icon: Activity, roles: ['ADMIN'] },
      { path: '/ml-training', label: 'AI 학습', icon: Brain, roles: ['ADMIN', 'DISPATCHER'] }
    ]
  },
  
  // 💰 청구/정산
  {
    path: '/billing',
    label: '청구/정산',
    icon: DollarSign,
    roles: ['ADMIN', 'DISPATCHER'],
    children: [
      { path: '/billing/financial-dashboard', label: '재무 대시보드', icon: BarChart3, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      { path: '/billing/charge-preview', label: '요금 미리보기', icon: Calculator, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      { path: '/billing/auto-schedule', label: '자동 청구 스케줄', icon: Clock, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      { path: '/billing/settlement-approval', label: '정산 승인', icon: CheckSquare, roles: ['ADMIN'], isNew: true },
      { path: '/billing/payment-reminder', label: '결제 알림', icon: Bell, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      { path: '/billing/export-task', label: '데이터 내보내기', icon: Download, roles: ['ADMIN', 'DISPATCHER'], isNew: true }
    ]
  },
  
  // 🔧 유지보수
  {
    path: '/maintenance',
    label: '유지보수',
    icon: Wrench,
    roles: ['ADMIN', 'DISPATCHER'],
    children: [
      { path: '/maintenance', label: '차량 유지보수', icon: Wrench, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/vehicle-mileage', label: '주행거리 관리', icon: TrendingUp, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      { path: '/ml-predictions', label: 'AI 예측 정비', icon: Brain, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/telemetry', label: '실시간 텔레메트리', icon: Activity, roles: ['ADMIN', 'DISPATCHER'] }
    ]
  },
  
  // 📊 모니터링 & 분석
  {
    path: '/monitoring',
    label: '모니터링 & 분석',
    icon: BarChart3,
    roles: ['ADMIN', 'DISPATCHER'],
    children: [
      { path: '/dispatch/monitoring', label: '실시간 배차 모니터링', icon: Radio, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      { path: '/realtime', label: '실시간 모니터링', icon: Radio, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/temperature-monitoring', label: '온도 모니터링', icon: Thermometer, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/temperature-analytics', label: '온도 분석', icon: TrendingUp, roles: ['ADMIN', 'DISPATCHER'] },
      { path: '/analytics-dashboard', label: '고급 분석 & BI', icon: BarChart3, roles: ['ADMIN'] },
      { path: '/analytics', label: '통계/분석', icon: BarChart3, roles: ['ADMIN'] }
    ]
  },
  
  // 💬 커뮤니케이션
  {
    path: '/communication',
    label: '커뮤니케이션',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    children: [
      { path: '/chat', label: '실시간 채팅', icon: MessageSquare, roles: ['ADMIN', 'DISPATCHER'], isNew: true, mobileVisible: true },
      { path: '/files', label: '파일 관리', icon: FileText, roles: ['ADMIN', 'DISPATCHER'], isNew: true, mobileVisible: true }
    ]
  },
  
  // ⚙️ 설정
  { 
    path: '/settings', 
    label: '설정', 
    icon: Settings, 
    roles: ['ADMIN'] 
  },
  
  // 📱 모바일 더보기
  { 
    path: '/more', 
    label: '더보기', 
    icon: MoreHorizontal, 
    roles: ['ADMIN', 'DISPATCHER'], 
    mobileVisible: true 
  }
];

export const filterMenuByRole = (menuItems: MenuItem[], userRole: string): MenuItem[] => {
  const roleUpper = userRole.toUpperCase();
  return menuItems
    .filter(item => item.roles.includes(roleUpper))
    .map(item => {
      if (item.children) {
        return {
          ...item,
          children: item.children.filter(child => child.roles.includes(roleUpper))
        };
      }
      return item;
    });
};

export const getMobileNavigation = (menuItems: MenuItem[]): MenuItem[] => {
  return menuItems.filter(item => item.mobileVisible);
};
