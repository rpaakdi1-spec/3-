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
  Zap,
  MessageSquare,
  DollarSign,
  Activity,
  Thermometer,
  Wrench,
  Calculator,
  Clock,
  CheckSquare,
  Bell,
  Download,
  ListChecks,
  MoreHorizontal,
  FileText,
} from 'lucide-react';
import { LucideIcon } from 'lucide-react';

export interface MenuItem {
  path: string;
  label: string;
  icon: LucideIcon;
  roles: string[];
  isNew?: boolean;
  children?: MenuItem[];
  mobileVisible?: boolean; // 모바일 하단 네비게이션에 표시 여부
}

/**
 * 통합 네비게이션 설정
 * - 사이드바 메뉴
 * - 모바일 하단 네비게이션
 * - 권한 관리
 * 모두 이 파일에서 중앙 관리
 */
export const navigationConfig: MenuItem[] = [
  { 
    path: '/dashboard', 
    label: '대시보드', 
    icon: Home, 
    roles: ['ADMIN', 'DISPATCHER'],
    mobileVisible: true // 모바일 하단 네비게이션에 표시
  },
  { 
    path: '/orders', 
    label: '주문 관리', 
    icon: Package, 
    roles: ['ADMIN', 'DISPATCHER'],
    mobileVisible: true // 모바일 하단 네비게이션에 표시
  },
  { 
    path: '/calendar', 
    label: '오더 캘린더', 
    icon: Calendar, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/dispatches', 
    label: '배차 관리', 
    icon: Truck, 
    roles: ['ADMIN', 'DISPATCHER'],
    mobileVisible: true // 모바일 하단 네비게이션에 표시
  },
  { 
    path: '/dispatch-rules', 
    label: '배차 규칙 관리', 
    icon: ListChecks, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/dispatch/monitoring', 
    label: '실시간 배차 모니터링', 
    icon: Radio, 
    roles: ['ADMIN', 'DISPATCHER'], 
    isNew: true 
  },
  { 
    path: '/optimization', 
    label: 'AI 배차 최적화', 
    icon: Zap, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/ai-cost', 
    label: 'AI 비용 모니터링', 
    icon: DollarSign, 
    roles: ['ADMIN'] 
  },
  { 
    path: '/ab-test', 
    label: 'AB Test 모니터링', 
    icon: Activity, 
    roles: ['ADMIN'] 
  },
  { 
    path: '/realtime', 
    label: '실시간 모니터링', 
    icon: Radio, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/temperature-monitoring', 
    label: '온도 모니터링', 
    icon: Thermometer, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/temperature-analytics', 
    label: '온도 분석', 
    icon: BarChart3, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
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
      { 
        path: '/billing/charge-preview', 
        label: '요금 미리보기', 
        icon: Calculator, 
        roles: ['ADMIN', 'DISPATCHER'], 
        isNew: true 
      },
      { 
        path: '/billing/auto-schedule', 
        label: '자동 청구 스케줄', 
        icon: Clock, 
        roles: ['ADMIN', 'DISPATCHER'], 
        isNew: true 
      },
      { 
        path: '/billing/settlement-approval', 
        label: '정산 승인', 
        icon: CheckSquare, 
        roles: ['ADMIN'], 
        isNew: true 
      },
      { 
        path: '/billing/payment-reminder', 
        label: '결제 알림', 
        icon: Bell, 
        roles: ['ADMIN', 'DISPATCHER'], 
        isNew: true 
      },
      { 
        path: '/billing/export-task', 
        label: '데이터 내보내기', 
        icon: Download, 
        roles: ['ADMIN', 'DISPATCHER'], 
        isNew: true 
      },
    ]
  },
  { 
    path: '/maintenance', 
    label: '차량 유지보수', 
    icon: Wrench, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/ml-predictions', 
    label: 'AI 예측 정비', 
    icon: Brain, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/telemetry', 
    label: '실시간 텔레메트리', 
    icon: Activity, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/dispatch-optimization', 
    label: '자동 배차 최적화', 
    icon: Zap, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/analytics-dashboard', 
    label: '고급 분석 & BI', 
    icon: BarChart3, 
    roles: ['ADMIN'] 
  },
  { 
    path: '/vehicles', 
    label: '차량 관리', 
    icon: Truck, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/clients', 
    label: '거래처 관리', 
    icon: Building2, 
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  { 
    path: '/analytics', 
    label: '통계/분석', 
    icon: BarChart3, 
    roles: ['ADMIN'],
    mobileVisible: true // 모바일 하단 네비게이션에 표시
  },
  { 
    path: '/ml-training', 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    label: 'AI 학습', 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    icon: Brain, 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    roles: ['ADMIN', 'DISPATCHER'] 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  { 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    path: '/settings', 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    label: '설정', 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    icon: Settings, 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    roles: ['ADMIN'] 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  { 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    path: '/more', 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    label: '더보기', 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    icon: MoreHorizontal, 
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    roles: ['ADMIN', 'DISPATCHER'],
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    mobileVisible: true // 모바일 하단 네비게이션에 표시
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
];
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true

  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
/**
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
 * 사용자 권한에 따라 메뉴 필터링
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
 */
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
export const filterMenuByRole = (menuItems: MenuItem[], userRole: string): MenuItem[] => {
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  const roleUpper = userRole.toUpperCase();
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  return menuItems
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    .filter(item => item.roles.includes(roleUpper))
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    .map(item => {
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
      if (item.children) {
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
        return {
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
          ...item,
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
          children: item.children.filter(child => child.roles.includes(roleUpper))
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
        };
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
      }
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
      return item;
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
    });
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
};
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true

  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
/**
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
 * 모바일 하단 네비게이션용 메뉴 추출
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
 */
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
export const getMobileNavigation = (menuItems: MenuItem[]): MenuItem[] => {
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  return menuItems.filter(item => item.mobileVisible);
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
};
  },
  {
    path: '/chat',
    label: '실시간 채팅',
    icon: MessageSquare,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
  },
  {
    path: '/files',
    label: '파일 관리',
    icon: FileText,
    roles: ['ADMIN', 'DISPATCHER'],
    isNew: true,
    mobileVisible: true
