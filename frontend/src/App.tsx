import React, { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './store/authStore';
import { useNotificationStore } from './store/notificationStore';
import { wsClient } from './utils/websocket';
import { registerServiceWorker, requestNotificationPermission } from './utils/pwa';
import ErrorBoundary from './components/common/ErrorBoundary';
import Loading from './components/common/Loading';
import Layout from './components/common/Layout';

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SignupPage = lazy(() => import('./pages/SignupPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const OrdersPage = lazy(() => import('./pages/OrdersPage'));
const OrderCalendarPage = lazy(() => import('./pages/OrderCalendarPage'));
const DispatchesPage = lazy(() => import('./pages/DispatchesPage'));
const OptimizationPage = lazy(() => import('./pages/OptimizationPage'));
const AICostDashboardPage = lazy(() => import('./pages/AICostDashboardPage'));
const TrackingPage = lazy(() => import('./pages/TrackingPage'));
const RealtimeDashboardPage = lazy(() => import('./pages/RealtimeDashboardPage'));
const VehiclesPage = lazy(() => import('./pages/VehiclesPage'));
const VehicleMileagePage = lazy(() => import('./pages/VehicleMileagePage'));
const DriverMileagePage = lazy(() => import('./pages/DriverMileagePage'));
const ClientsPage = lazy(() => import('./pages/ClientsPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const ReportsPage = lazy(() => import('./pages/ReportsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const MorePage = lazy(() => import('./pages/MorePage'));
const MLTrainingPage = lazy(() => import('./pages/MLTrainingPage'));
const ABTestMonitorPage = lazy(() => import('./pages/ABTestMonitorPage'));
const RecurringOrdersPage = lazy(() => import('./pages/RecurringOrdersPage'));
const TemperatureMonitoringPage = lazy(() => import('./pages/TemperatureMonitoringPage'));
const TemperatureAnalyticsPage = lazy(() => import('./pages/TemperatureAnalyticsPage'));
const BillingPage = lazy(() => import('./pages/BillingPage'));
const VehicleMaintenancePage = lazy(() => import('./pages/VehicleMaintenancePage'));
const MLPredictionsPage = lazy(() => import('./pages/MLPredictionsPage'));
const RealtimeTelemetryPage = lazy(() => import('./pages/RealtimeTelemetryPage'));
const DispatchOptimizationPage = lazy(() => import('./pages/DispatchOptimizationPage'));
const AnalyticsDashboardPage = lazy(() => import('./pages/AnalyticsDashboardPage'));

// Phase 8: Billing Enhanced Pages
const FinancialDashboardPage = lazy(() => import('./pages/FinancialDashboardPage'));
const ChargePreviewPage = lazy(() => import('./pages/ChargePreviewPage'));
const AutoInvoiceSchedulePage = lazy(() => import('./pages/AutoInvoiceSchedulePage'));
const SettlementApprovalPage = lazy(() => import('./pages/SettlementApprovalPage'));
const PaymentReminderPage = lazy(() => import('./pages/PaymentReminderPage'));
const ExportTaskPage = lazy(() => import('./pages/ExportTaskPage'));

// AI Dispatch Monitoring Dashboard
const DispatchMonitoringDashboard = lazy(() => import('./pages/DispatchMonitoringDashboard'));

// Dispatch Rules Management Page
const DispatchRulesPage = lazy(() => import('./pages/DispatchRulesPage'));

// Vehicle-Driver Management Page
const VehicleDriverManagementPage = lazy(() => import('./pages/VehicleDriverManagementPage'));

// Employee Management Page
const EmployeeManagementPage = lazy(() => import('./pages/EmployeeManagementPage'));

// IoT Sensor Pages
const IoTSensorsPage = lazy(() => import('./pages/IoTSensorsPage'));
const IoTSensorDetailPage = lazy(() => import('./pages/IoTSensorDetailPage'));
const IoTAlertsPage = lazy(() => import('./pages/IoTAlertsPage'));

// File Management Page (Phase 16.2)
const FilesPage = lazy(() => import('./pages/FilesPage'));
const TemplateManagementPage = lazy(() => import('./pages/TemplateManagementPage'));

// Chat Page (Phase 16.3)
const ChatPage = lazy(() => import('./pages/ChatPage'));

// Public Tracking Page (no auth required)
const PublicTrackingPage = lazy(() => import('./pages/PublicTrackingPage'));

// Driver Pages
const DriverDispatchesPage = lazy(() => import('./pages/DriverDispatchesPage'));

// Guest Delivery Page (no auth required)
const GuestDeliveryPage = lazy(() => import('./pages/GuestDeliveryPage'));

// Location Room Pages
const LocationRoomsPage = lazy(() => import('./pages/LocationRoomsPage'));
const DriverRoomPage = lazy(() => import('./pages/DriverRoomPage'));
const ClientRoomPage = lazy(() => import('./pages/ClientRoomPage'));

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

// Layout Wrapper for Protected Routes
const LayoutWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ProtectedRoute>
      <Layout>
        {children}
      </Layout>
    </ProtectedRoute>
  );
};


const App: React.FC = () => {
  const { checkAuth, isAuthenticated } = useAuthStore();
  const { addNotification } = useNotificationStore();

  useEffect(() => {
    checkAuth();
    
    // PWA 기능은 페이지 로드 완료 후 등록 (초기 로딩 차단 방지)
    const initPWA = () => {
      registerServiceWorker();
      // 알림 권한은 사용자 인터랙션 후 요청 (auto-request 제거)
      // requestNotificationPermission();
    };

    if (document.readyState === 'complete') {
      // 이미 로드 완료된 경우 다음 틱에 실행
      setTimeout(initPWA, 2000);
    } else {
      window.addEventListener('load', () => setTimeout(initPWA, 2000), { once: true });
    }
  }, [checkAuth]);

  // Setup WebSocket connection for real-time updates (OPTIONAL - only if needed)
  useEffect(() => {
    if (isAuthenticated) {
      // WebSocket is now optional - only connect for real-time pages
      // Uncomment if you need global WebSocket connection:
      // wsClient.connect('dashboard');
      
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
        // Only disconnect if connected
        if (wsClient.isConnected()) {
          wsClient.disconnect();
        }
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
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/tracking/:trackingNumber" element={<TrackingPage />} />
            <Route path="/track/:trackingNumber" element={<PublicTrackingPage />} />
            <Route path="/guest/delivery/:token" element={<GuestDeliveryPage />} />

            {/* Location Room Public Routes (no auth) */}
            <Route path="/room/driver/:driverToken" element={<DriverRoomPage />} />
            <Route path="/room/client/:clientToken" element={<ClientRoomPage />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <LayoutWrapper>
                  <DashboardPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/orders"
              element={
                <LayoutWrapper>
                  <OrdersPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/calendar"
              element={
                <LayoutWrapper>
                  <OrderCalendarPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/recurring-orders"
              element={
                <LayoutWrapper>
                  <RecurringOrdersPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/dispatches"
              element={
                <LayoutWrapper>
                  <DispatchesPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/driver/dispatches"
              element={
                <LayoutWrapper>
                  <DriverDispatchesPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/location-rooms"
              element={
                <LayoutWrapper>
                  <LocationRoomsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/template-management"
              element={
                <LayoutWrapper>
                  <TemplateManagementPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/optimization"
              element={
                <LayoutWrapper>
                  <OptimizationPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/dispatch/monitoring"
              element={
                <LayoutWrapper>
                  <DispatchMonitoringDashboard />
                </LayoutWrapper>
              }
            />
            <Route
              path="/ai-cost"
              element={
                <LayoutWrapper>
                  <AICostDashboardPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/realtime"
              element={
                <LayoutWrapper>
                  <RealtimeDashboardPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/vehicles"
              element={
                <LayoutWrapper>
                  <VehiclesPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/vehicle-driver-management"
              element={
                <LayoutWrapper>
                  <VehicleDriverManagementPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/employees"
              element={
                <LayoutWrapper>
                  <EmployeeManagementPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/clients"
              element={
                <LayoutWrapper>
                  <ClientsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/analytics"
              element={
                <LayoutWrapper>
                  <AnalyticsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/reports"
              element={
                <LayoutWrapper>
                  <ReportsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/settings"
              element={
                <LayoutWrapper>
                  <SettingsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/more"
              element={
                <LayoutWrapper>
                  <MorePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/ml-training"
              element={
                <LayoutWrapper>
                  <MLTrainingPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/dispatch-rules"
              element={
                <LayoutWrapper>
                  <DispatchRulesPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/ab-test"
              element={
                <LayoutWrapper>
                  <ABTestMonitorPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/temperature-monitoring"
              element={
                <LayoutWrapper>
                  <TemperatureMonitoringPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/temperature-analytics"
              element={
                <LayoutWrapper>
                  <TemperatureAnalyticsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/billing"
              element={
                <LayoutWrapper>
                  <BillingPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/billing/financial-dashboard"
              element={
                <LayoutWrapper>
                  <FinancialDashboardPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/billing/charge-preview"
              element={
                <LayoutWrapper>
                  <ChargePreviewPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/billing/auto-schedule"
              element={
                <LayoutWrapper>
                  <AutoInvoiceSchedulePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/billing/settlement-approval"
              element={
                <LayoutWrapper>
                  <SettlementApprovalPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/billing/payment-reminder"
              element={
                <LayoutWrapper>
                  <PaymentReminderPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/billing/export-task"
              element={
                <LayoutWrapper>
                  <ExportTaskPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/maintenance"
              element={
                <LayoutWrapper>
                  <VehicleMaintenancePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/vehicle-mileage"
              element={
                <LayoutWrapper>
                  <VehicleMileagePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/driver-mileage"
              element={
                <LayoutWrapper>
                  <DriverMileagePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/ml-predictions"
              element={
                <LayoutWrapper>
                  <MLPredictionsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/telemetry"
              element={
                <LayoutWrapper>
                  <RealtimeTelemetryPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/dispatch-optimization"
              element={
                <LayoutWrapper>
                  <DispatchOptimizationPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/analytics-dashboard"
              element={
                <LayoutWrapper>
                  <AnalyticsDashboardPage />
                </LayoutWrapper>
              }
            />

            {/* IoT Sensor Routes */}
            <Route
              path="/iot/sensors"
              element={
                <LayoutWrapper>
                  <IoTSensorsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/iot/sensors/:vehicleId"
              element={
                <LayoutWrapper>
                  <IoTSensorDetailPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/iot/alerts"
              element={
                <LayoutWrapper>
                  <IoTAlertsPage />
                </LayoutWrapper>
              }
            />

            {/* File Management (Phase 16.2) */}
            <Route
              path="/files"
              element={
                <LayoutWrapper>
                  <FilesPage />
                </LayoutWrapper>
              }
            />

            {/* Real-time Chat (Phase 16.3) */}
            <Route
              path="/chat"
              element={
                <LayoutWrapper>
                  <ChatPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/template-management"
              element={
                <LayoutWrapper>
                  <TemplateManagementPage />
                </LayoutWrapper>
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
