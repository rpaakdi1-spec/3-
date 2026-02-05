/**
 * Mobile Navigation
 * 모바일용 햄버거 메뉴 및 바텀 네비게이션
 */
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Package, 
  Truck, 
  Users, 
  Calendar,
  BarChart3,
  Menu,
  X,
  Mic,
  Zap
} from 'lucide-react';

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { path: '/dashboard', icon: Home, label: '대시보드' },
  { path: '/orders', icon: Package, label: '주문' },
  { path: '/dispatches', icon: Truck, label: '배차' },
  { path: '/calendar', icon: Calendar, label: '캘린더' },
  { path: '/vehicles', icon: Users, label: '차량' },
  { path: '/clients', icon: Users, label: '거래처' },
  { path: '/analytics', icon: BarChart3, label: '분석' },
];

export const MobileNav: React.FC<MobileNavProps> = ({ isOpen, onClose }) => {
  const location = useLocation();

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
        onClick={onClose}
      />

      {/* Sidebar */}
      <div className="fixed top-0 left-0 h-full w-64 bg-white shadow-xl z-50 md:hidden transform transition-transform duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-bold text-gray-800">UVIS</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100"
          >
            <X size={24} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                  ${isActive 
                    ? 'bg-indigo-100 text-indigo-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-gray-50">
          <div className="text-xs text-gray-500 text-center">
            UVIS v1.0.0
          </div>
        </div>
      </div>
    </>
  );
};

export const BottomNav: React.FC = () => {
  const location = useLocation();

  const bottomNavItems = [
    { path: '/dashboard', icon: Home, label: '홈' },
    { path: '/orders', icon: Package, label: '주문' },
    { path: '/dispatches', icon: Truck, label: '배차' },
    { path: '/analytics', icon: BarChart3, label: '분석' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg md:hidden z-30">
      <div className="flex items-center justify-around">
        {bottomNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex flex-col items-center gap-1 px-4 py-3 flex-1
                ${isActive ? 'text-indigo-600' : 'text-gray-500'}
              `}
            >
              <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
              <span className={`text-xs ${isActive ? 'font-semibold' : 'font-normal'}`}>
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export const MobileHeader: React.FC<{ onMenuClick: () => void }> = ({ onMenuClick }) => {
  const location = useLocation();

  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard') return '대시보드';
    if (path === '/orders') return '주문 관리';
    if (path === '/dispatches') return '배차 관리';
    if (path === '/calendar') return '캘린더';
    if (path === '/vehicles') return '차량 관리';
    if (path === '/clients') return '거래처 관리';
    if (path === '/analytics') return '분석';
    return 'UVIS';
  };

  return (
    <div className="sticky top-0 left-0 right-0 bg-white border-b shadow-sm z-20 md:hidden">
      <div className="flex items-center justify-between px-4 py-3">
        <button
          onClick={onMenuClick}
          className="p-2 rounded-lg hover:bg-gray-100"
        >
          <Menu size={24} />
        </button>

        <h1 className="text-lg font-bold text-gray-800">{getPageTitle()}</h1>

        <div className="w-10" /> {/* Spacer for centering */}
      </div>
    </div>
  );
};

export default MobileNav;
