import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { isDevelopment } from '../../config/api';
import {
  Home,
  Package,
  Truck,
  Users,
  Building2,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  Radio,
  Calendar,
  Brain,
  Zap,
  MessageSquare,
  DollarSign,
  Activity,
  Thermometer,
  Wrench,
  FileText,
  Calculator,
  Clock,
  CheckSquare,
  Bell,
  Download,
  ChevronDown,
  ChevronRight,
  ListChecks,
} from 'lucide-react';

interface MenuItem {
  path: string;
  label: string;
  icon: any;
  roles: string[];
  isNew?: boolean;
  children?: MenuItem[];
}

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [isOpen, setIsOpen] = React.useState(false);

  const menuItems: MenuItem[] = [
    { path: '/dashboard', label: '대시보드', icon: Home, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/orders', label: '주문 관리', icon: Package, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/calendar', label: '오더 캘린더', icon: Calendar, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/ai-chat', label: 'AI 주문 어시스턴트', icon: MessageSquare, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/optimization', label: 'AI 배차 최적화', icon: Zap, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/ai-cost', label: 'AI 비용 모니터링', icon: DollarSign, roles: ['ADMIN'] },
    { path: '/ab-test', label: 'AB Test 모니터링', icon: Activity, roles: ['ADMIN'] },
    { path: '/dispatches', label: '배차 관리', icon: Truck, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/dispatch-rules', label: '규칙 관리', icon: ListChecks, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
    { path: '/dispatch/monitoring', label: '실시간 배차 모니터링', icon: Radio, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
    { path: '/realtime', label: '실시간 모니터링', icon: Radio, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/temperature-monitoring', label: '온도 모니터링', icon: Thermometer, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/temperature-analytics', label: '온도 분석', icon: BarChart3, roles: ['ADMIN', 'DISPATCHER'] },
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
        { path: '/billing/export-task', label: '데이터 내보내기', icon: Download, roles: ['ADMIN', 'DISPATCHER'], isNew: true },
      ]
    },
    { path: '/maintenance', label: '차량 유지보수', icon: Wrench, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/ml-predictions', label: 'AI 예측 정비', icon: Brain, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/telemetry', label: '실시간 텔레메트리', icon: Activity, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/dispatch-optimization', label: '자동 배차 최적화', icon: Zap, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/analytics-dashboard', label: '고급 분석 & BI', icon: BarChart3, roles: ['ADMIN'] },
    { path: '/vehicles', label: '차량 관리', icon: Truck, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/clients', label: '거래처 관리', icon: Building2, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/analytics', label: '통계/분석', icon: BarChart3, roles: ['ADMIN'] },
    { path: '/ml-training', label: 'AI 학습', icon: Brain, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/settings', label: '설정', icon: Settings, roles: ['ADMIN'] },
  ];

  // 모든 서브메뉴를 기본적으로 확장 상태로 초기화
  const initialExpandedState = React.useMemo(() => {
    const expanded: Record<string, boolean> = {};
    menuItems.forEach(item => {
      if (item.children && item.children.length > 0) {
        expanded[item.path] = true; // 모든 서브메뉴 자동 확장
      }
    });
    return expanded;
  }, []);

  const [expandedMenus, setExpandedMenus] = React.useState<Record<string, boolean>>(initialExpandedState);

  const toggleMenu = (key: string) => {
    setExpandedMenus(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const filteredMenuItems = menuItems.filter((item) => {
    const userRole = (user?.role || '').toUpperCase();
    const hasAccess = item.roles.includes(userRole);
    
    // Debug log (development only)
    if (isDevelopment) {
      console.log(`메뉴 체크: "${item.label}" - 사용자 role: "${userRole}", 필요 role: [${item.roles.join(', ')}], 접근: ${hasAccess ? '✅' : '❌'}`);
    }
    
    return hasAccess;
  }).map(item => {
    if (item.children) {
      const userRole = (user?.role || '').toUpperCase();
      return {
        ...item,
        children: item.children.filter(child => {
          const hasAccess = child.roles.includes(userRole);
          
          // Debug log (development only)
          if (isDevelopment) {
            console.log(`  └─ 서브메뉴: "${child.label}" - 접근: ${hasAccess ? '✅' : '❌'}`);
          }
          
          return hasAccess;
        })
      };
    }
    return item;
  });

  // Debug log filtered menu count (development only)
  if (isDevelopment) {
    console.log(`\n📋 총 메뉴 수: ${filteredMenuItems.length}개`);
    console.log(`👤 사용자: ${user?.username}, 권한: ${user?.role?.toUpperCase()}\n`);
  }

  const renderMenuItem = (item: MenuItem, index: number) => {
    const Icon = item.icon;
    const isActive = location.pathname === item.path;
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedMenus[item.path] || false;
    const ChevronIcon = isExpanded ? ChevronDown : ChevronRight;

    return (
      <li key={item.path + index}>
        {hasChildren ? (
          <>
            <button
              onClick={() => toggleMenu(item.path)}
              className={`flex items-center justify-between w-full space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon size={20} />
                <span>{item.label}</span>
              </div>
              <ChevronIcon size={16} />
            </button>
            {isExpanded && (
              <ul className="ml-4 mt-1 space-y-1 border-l-2 border-gray-700 pl-2">
                {item.children!.map((child, childIndex) => {
                  const ChildIcon = child.icon;
                  const isChildActive = location.pathname === child.path;
                  return (
                    <li key={child.path + childIndex}>
                      <Link
                        to={child.path}
                        className={`flex items-center justify-between space-x-2 px-3 py-2 rounded-lg transition-colors text-sm ${
                          isChildActive
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                        }`}
                        onClick={() => setIsOpen(false)}
                      >
                        <div className="flex items-center space-x-2">
                          <ChildIcon size={16} />
                          <span>{child.label}</span>
                        </div>
                        {child.isNew && (
                          <span className="px-2 py-0.5 text-xs font-bold bg-green-500 text-white rounded-full">
                            NEW
                          </span>
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </>
        ) : (
          <Link
            to={item.path}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              isActive
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
            onClick={() => setIsOpen(false)}
          >
            <Icon size={20} />
            <span>{item.label}</span>
            {item.isNew && (
              <span className="ml-auto px-2 py-0.5 text-xs font-bold bg-green-500 text-white rounded-full">
                NEW
              </span>
            )}
          </Link>
        )}
      </li>
    );
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-blue-600 text-white rounded-lg"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-40 w-64 bg-gray-900 text-white transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 border-b border-gray-800">
            <h1 className="text-xl font-bold">Cold Chain</h1>
          </div>

          {/* User info */}
          <div className="p-4 border-b border-gray-800">
            <p className="text-sm font-medium">{user?.username}</p>
            <p className="text-xs text-gray-400">{user?.role}</p>
          </div>

          {/* Navigation */}
          <nav 
            className="flex-1 overflow-y-auto p-4" 
            style={{ 
              maxHeight: 'calc(100vh - 200px)',
              scrollbarWidth: 'thin',
              scrollbarColor: '#4B5563 #1F2937'
            }}
          >
            <ul className="space-y-2">
              {filteredMenuItems.map((item, index) => renderMenuItem(item, index))}
            </ul>
          </nav>

          {/* Logout button */}
          <div className="p-4 border-t border-gray-800">
            <button
              onClick={handleLogout}
              className="flex items-center space-x-3 w-full px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <LogOut size={20} />
              <span>로그아웃</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default Sidebar;
