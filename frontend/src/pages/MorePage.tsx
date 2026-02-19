import React from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import { 
  Users, 
  Truck as TruckIcon, 
  MapPin, 
  Settings, 
  Bell,
  FileText,
  BarChart3,
  Calendar,
  DollarSign,
  Shield,
  HelpCircle,
  LogOut,
  ChevronRight
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

interface MenuItem {
  icon: React.ElementType;
  label: string;
  path?: string;
  onClick?: () => void;
  color: string;
  badge?: string;
}

const MorePage: React.FC = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  const handleLogout = () => {
    if (window.confirm('로그아웃 하시겠습니까?')) {
      logout();
      toast.success('로그아웃되었습니다');
      navigate('/login');
    }
  };

  const menuSections: { title: string; items: MenuItem[] }[] = [
    {
      title: '관리',
      items: [
        { icon: Users, label: '고객 관리', path: '/clients', color: 'text-blue-600' },
        { icon: TruckIcon, label: '차량 관리', path: '/vehicles', color: 'text-green-600' },
        { icon: MapPin, label: '기사 관리', path: '/drivers', color: 'text-purple-600' },
        { icon: Calendar, label: '주문 캘린더', path: '/calendar', color: 'text-orange-600' },
      ],
    },
    {
      title: '분석 및 리포트',
      items: [
        { icon: BarChart3, label: '실시간 모니터링', path: '/monitoring', color: 'text-indigo-600' },
        { icon: FileText, label: '재무 대시보드', path: '/financial', color: 'text-teal-600' },
        { icon: DollarSign, label: '청구 관리', path: '/billing', color: 'text-emerald-600' },
      ],
    },
    {
      title: '설정',
      items: [
        { icon: Settings, label: '시스템 설정', path: '/settings', color: 'text-gray-600' },
        { icon: Bell, label: '알림 설정', path: '/settings', color: 'text-yellow-600' },
        { icon: Shield, label: '보안 설정', path: '/settings', color: 'text-red-600' },
      ],
    },
    {
      title: '기타',
      items: [
        { icon: HelpCircle, label: '도움말', path: '/help', color: 'text-blue-500' },
        { icon: LogOut, label: '로그아웃', onClick: handleLogout, color: 'text-red-500' },
      ],
    },
  ];

  const handleMenuClick = (item: MenuItem) => {
    if (item.onClick) {
      item.onClick();
    } else if (item.path) {
      navigate(item.path);
    }
  };

  return (
    <Layout>
      <div className="p-4 pb-20 md:p-6">
        {/* User Profile Card */}
        <Card className="mb-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-gray-800">{user?.full_name || user?.username}</h2>
              <p className="text-sm text-gray-600">{user?.email}</p>
              <p className="text-xs text-gray-500 mt-1">
                {user?.role === 'ADMIN' ? '관리자' : '사용자'}
              </p>
            </div>
            <ChevronRight className="text-gray-400" size={24} />
          </div>
        </Card>

        {/* Menu Sections */}
        {menuSections.map((section, index) => (
          <div key={index} className="mb-6">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3 px-2">
              {section.title}
            </h3>
            <Card className="divide-y divide-gray-100">
              {section.items.map((item, itemIndex) => {
                const Icon = item.icon;
                return (
                  <button
                    key={itemIndex}
                    onClick={() => handleMenuClick(item)}
                    className="w-full flex items-center justify-between p-4 hover:bg-gray-50 active:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 ${item.color} bg-opacity-10 rounded-lg flex items-center justify-center`}>
                        <Icon className={item.color} size={20} />
                      </div>
                      <span className="text-gray-800 font-medium">{item.label}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {item.badge && (
                        <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">
                          {item.badge}
                        </span>
                      )}
                      <ChevronRight className="text-gray-400" size={20} />
                    </div>
                  </button>
                );
              })}
            </Card>
          </div>
        ))}

        {/* App Version */}
        <div className="text-center text-sm text-gray-500 mt-8 mb-4">
          <p>UVIS Cold Chain v1.0.0</p>
          <p className="text-xs mt-1">© 2026 All rights reserved</p>
        </div>
      </div>
    </Layout>
  );
};

export default MorePage;
