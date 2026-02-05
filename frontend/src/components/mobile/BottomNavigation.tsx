import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Package, Truck, BarChart3, MoreHorizontal } from 'lucide-react';

interface BottomNavItem {
  path: string;
  label: string;
  icon: React.ElementType;
}

const navItems: BottomNavItem[] = [
  { path: '/dashboard', label: '대시보드', icon: LayoutDashboard },
  { path: '/orders', label: '주문', icon: Package },
  { path: '/dispatches', label: '배차', icon: Truck },
  { path: '/analytics', label: '분석', icon: BarChart3 },
  { path: '/more', label: '더보기', icon: MoreHorizontal },
];

export const BottomNavigation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  const handleNavigation = (path: string) => {
    if (path === '/more') {
      // Show more menu modal
      // TODO: Implement more menu
      return;
    }
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
