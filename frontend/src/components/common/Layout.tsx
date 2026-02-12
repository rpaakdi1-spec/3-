import React from 'react';
import Sidebar from './Sidebar';
import NotificationCenter from './NotificationCenter';
import { BottomNavigation } from '../mobile/BottomNavigation';
import { useResponsive } from '../../hooks/useResponsive';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isMobile } = useResponsive();

  return (
    <div className="flex h-screen bg-gray-100">
      {!isMobile && <Sidebar />}
      <main className="flex-1 overflow-y-auto">
        <div className="flex justify-end items-center p-4 bg-white border-b">
          <NotificationCenter />
        </div>
        <div className={`p-4 md:p-6 lg:p-8 ${isMobile ? 'pb-20' : ''}`}>
          {children}
        </div>
      </main>
      {isMobile && <BottomNavigation />}
    </div>
  );
};

export default Layout;
