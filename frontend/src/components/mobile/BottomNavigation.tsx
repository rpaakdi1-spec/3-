import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { navigationConfig, filterMenuByRole, getMobileNavigation } from '../../config/navigation';

export const BottomNavigation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuthStore();

  // 중앙 설정에서 모바일 네비게이션 메뉴 가져오기
  const userRole = (user?.role || '').toUpperCase();
  const filteredMenuItems = React.useMemo(
    () => filterMenuByRole(navigationConfig, userRole),
    [userRole]
  );
  const navItems = React.useMemo(
    () => getMobileNavigation(filteredMenuItems),
    [filteredMenuItems]
  );

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 md:hidden">
      <div className="flex justify-around items-center h-16">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <button
              key={item.path}
              onClick={() => handleNavigation(item.path)}
              className={`flex flex-col items-center justify-center flex-1 h-full space-y-1 transition-colors active:bg-gray-50 ${
                active ? 'text-blue-600' : 'text-gray-600'
              }`}
            >
              <Icon className="w-6 h-6" />
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
