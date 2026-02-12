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
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f3f4f6' }}>
      {!isMobile && <Sidebar />}
      <main style={{ flex: 1, overflowY: 'auto' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'flex-end', 
          alignItems: 'center', 
          padding: '1rem', 
          backgroundColor: 'white', 
          borderBottom: '1px solid #e5e7eb' 
        }}>
          <NotificationCenter />
        </div>
        <div style={{ 
          padding: isMobile ? '1rem 1rem 5rem 1rem' : '2rem' 
        }}>
          {children}
        </div>
      </main>
      {isMobile && <BottomNavigation />}
    </div>
  );
};

export default Layout;
