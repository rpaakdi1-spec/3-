import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { isDevelopment } from '../../config/api';
import {
  LogOut,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { navigationConfig, filterMenuByRole, MenuItem } from '../../config/navigation';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [isOpen, setIsOpen] = React.useState(false);

  // 중앙 설정에서 메뉴 가져오기
  const userRole = (user?.role || '').toUpperCase();
  const menuItems = React.useMemo(
    () => filterMenuByRole(navigationConfig, userRole),
    [userRole]
  );

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
              {menuItems.map((item, index) => renderMenuItem(item, index))}
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
