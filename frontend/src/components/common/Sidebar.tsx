import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
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
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [isOpen, setIsOpen] = React.useState(false);

  const menuItems = [
    { path: '/dashboard', label: '대시보드', icon: Home, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/orders', label: '주문 관리', icon: Package, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/calendar', label: '오더 캘린더', icon: Calendar, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/ai-chat', label: 'AI 주문 어시스턴트', icon: MessageSquare, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/optimization', label: 'AI 배차 최적화', icon: Zap, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/ai-cost', label: 'AI 비용 모니터링', icon: DollarSign, roles: ['ADMIN'] },
    { path: '/dispatches', label: '배차 관리', icon: Truck, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/realtime', label: '실시간 모니터링', icon: Radio, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/vehicles', label: '차량 관리', icon: Truck, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/clients', label: '거래처 관리', icon: Building2, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/analytics', label: '통계/분석', icon: BarChart3, roles: ['ADMIN'] },
    { path: '/ml-training', label: 'AI 학습', icon: Brain, roles: ['ADMIN', 'DISPATCHER'] },
    { path: '/settings', label: '설정', icon: Settings, roles: ['ADMIN'] },
  ];

  const filteredMenuItems = menuItems.filter((item) =>
    item.roles.includes((user?.role || '').toUpperCase())
  );

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
          <nav className="flex-1 overflow-y-auto p-4">
            <ul className="space-y-2">
              {filteredMenuItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <li key={item.path}>
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
                    </Link>
                  </li>
                );
              })}
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
