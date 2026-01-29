import React, { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './store/authStore';
import { useNotificationStore } from './store/notificationStore';
import { wsClient } from './utils/websocket';
import { registerServiceWorker, requestNotificationPermission } from './utils/pwa';
import ErrorBoundary from './components/common/ErrorBoundary';
import Loading from './components/common/Loading';

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/LoginPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const OrdersPage = lazy(() => import('./pages/OrdersPage'));
const OrderCalendarPage = lazy(() => import('./pages/OrderCalendarPage'));
const DispatchesPage = lazy(() => import('./pages/DispatchesPage'));
const TrackingPage = lazy(() => import('./pages/TrackingPage'));
const RealtimeDashboardPage = lazy(() => import('./pages/RealtimeDashboardPage'));
const VehiclesPage = lazy(() => import('./pages/VehiclesPage'));
const ClientsPage = lazy(() => import('./pages/ClientsPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const ReportsPage = lazy(() => import('./pages/ReportsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  const { checkAuth, isAuthenticated } = useAuthStore();
  const { addNotification } = useNotificationStore();

  useEffect(() => {
    checkAuth();
    
    // Initialize PWA features
    registerServiceWorker();
    requestNotificationPermission();
  }, [checkAuth]);

  // Setup WebSocket connection for real-time updates
  useEffect(() => {
    if (isAuthenticated) {
      wsClient.connect();

      // Listen for order updates
      wsClient.on('order_update', (data) => {
        addNotification({
          type: 'info',
          title: '주문 업데이트',
          message: `주문 #${data.order_id}의 상태가 변경되었습니다.`
        });
      });

      // Listen for dispatch updates
      wsClient.on('dispatch_update', (data) => {
        addNotification({
          type: 'info',
          title: '배차 업데이트',
          message: `배차 #${data.dispatch_id}의 상태가 변경되었습니다.`
        });
      });

      // Listen for temperature alerts
      wsClient.on('temperature_alert', (data) => {
        addNotification({
          type: 'warning',
          title: '온도 경고',
          message: `차량 ${data.vehicle_number}의 온도가 범위를 벗어났습니다.`
        });
      });

      return () => {
        wsClient.disconnect();
      };
    }
  }, [isAuthenticated, addNotification]);

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
        <Suspense fallback={<Loading />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/tracking/:trackingNumber" element={<TrackingPage />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/orders"
              element={
                <ProtectedRoute>
                  <OrdersPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/calendar"
              element={
                <ProtectedRoute>
                  <OrderCalendarPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dispatches"
              element={
                <ProtectedRoute>
                  <DispatchesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/realtime"
              element={
                <ProtectedRoute>
                  <RealtimeDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/vehicles"
              element={
                <ProtectedRoute>
                  <VehiclesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/clients"
              element={
                <ProtectedRoute>
                  <ClientsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <AnalyticsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <ReportsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />

            {/* Default Route */}
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
