import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import apiClient from '../api/client';
import { DashboardStats } from '../types';
import { Package, Truck, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useResponsive } from '../hooks/useResponsive';
import { MobileDashboardCard } from '../components/mobile/MobileDashboardCard';
import UvisAlerts from '../components/vehicles/UvisAlerts';
import UvisFleetStats from '../components/vehicles/UvisFleetStats';
import UvisAlertToast from '../components/vehicles/UvisAlertToast';
import { NotificationSettings } from '../components/notifications/NotificationSettings';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const { isMobile } = useResponsive();
  const navigate = useNavigate();

  useEffect(() => {
    // Initial fetch
    fetchDashboardData();
    
    // WebSocket connection with proper cleanup
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/dispatches/ws/dashboard`;
    
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5; // Limit reconnection attempts
    let isCleanedUp = false; // Track cleanup state
    
    const connectWebSocket = () => {
      // Don't reconnect if cleaned up or max attempts reached
      if (isCleanedUp || reconnectAttempts >= maxReconnectAttempts) {
        if (reconnectAttempts >= maxReconnectAttempts) {
          console.warn('⚠️ Max WebSocket reconnection attempts reached. Using polling fallback.');
          // Fallback to polling every 30 seconds
          const pollingInterval = setInterval(fetchDashboardData, 30000);
          return () => clearInterval(pollingInterval);
        }
        return;
      }
      
      try {
        // Close existing connection if any
        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
          console.log('⚠️ WebSocket already connecting/connected, skipping...');
          return;
        }
        
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('✅ WebSocket connected: dashboard');
          setIsConnected(true);
          reconnectAttempts = 0; // Reset on successful connection
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            // Only log in development
            if (process.env.NODE_ENV === 'development') {
              console.log('📊 Dashboard stats updated:', data);
            }
            setStats(data);
            setLoading(false);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        ws.onerror = (error) => {
          // Suppress error logging in production
          if (process.env.NODE_ENV === 'development') {
            console.error('❌ WebSocket error:', error);
          }
          setIsConnected(false);
        };
        
        ws.onclose = () => {
          if (process.env.NODE_ENV === 'development') {
            console.log('🔌 WebSocket disconnected');
          }
          setIsConnected(false);
          
          // Only reconnect if not cleaned up and within attempt limit
          if (!isCleanedUp && reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            // Exponential backoff: 5s, 10s, 20s, 40s, 80s
            const delay = Math.min(5000 * Math.pow(2, reconnectAttempts - 1), 80000);
            
            if (process.env.NODE_ENV === 'development') {
              console.log(`🔄 Reconnecting WebSocket in ${delay/1000}s (attempt ${reconnectAttempts}/${maxReconnectAttempts})...`);
            }
            
            reconnectTimeout = setTimeout(() => {
              connectWebSocket();
            }, delay);
          } else if (reconnectAttempts >= maxReconnectAttempts) {
            console.warn('⚠️ Max reconnection attempts reached. Please refresh the page.');
          }
        };
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        reconnectAttempts++;
      }
    };
    
    connectWebSocket();
    
    // Cleanup function
    return () => {
      isCleanedUp = true; // Mark as cleaned up
      
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }
      
      if (ws) {
        ws.onclose = null; // Prevent onclose from firing
        ws.onerror = null;
        ws.onmessage = null;
        ws.onopen = null;
        
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
          ws.close(1000, 'Component unmounting');
        }
        ws = null;
      }
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await apiClient.getDashboard();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return (<Loading />
  );
  }

  const statCards = [
    {
      title: '전체 주문',
      value: stats.total_orders,
      icon: Package,
      color: 'bg-blue-500',
      trend: '+12%',
    },
    {
      title: '대기 중인 주문',
      value: stats.pending_orders,
      icon: Clock,
      color: 'bg-yellow-500',
    },
    {
      title: '진행 중인 배차',
      value: stats.active_dispatches,
      icon: Truck,
      color: 'bg-green-500',
    },
    {
      title: '오늘 완료',
      value: stats.completed_today,
      icon: CheckCircle,
      color: 'bg-purple-500',
      trend: '+8%',
    },
  ];

  // Mock chart data
  const chartData = {
    labels: ['월', '화', '수', '목', '금', '토', '일'],
    datasets: [
      {
        label: '배송 완료',
        data: [12, 19, 15, 25, 22, 18, stats.completed_today],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '주간 배송 현황',
      },
    },
  };

  return (<div className="space-y-4 md:space-y-6">
        {/* UVIS 알림 토스트 (백그라운드 실행) */}
        <UvisAlertToast enabled={true} />

        {/* Header */}
        <div className="px-4 md:px-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900">대시보드</h1>
              <p className="text-sm md:text-base text-gray-600 mt-1 md:mt-2">실시간 배송 현황을 확인하세요</p>
            </div>
            {/* WebSocket 연결 상태 */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
              <span className="text-xs text-gray-500">
                {isConnected ? '실시간 연결' : '연결 끊김'}
              </span>
            </div>
          </div>
        </div>

        {/* Stat Cards - Mobile optimized */}
        {isMobile ? (
          <div className="grid grid-cols-2 gap-3 px-4">
            <MobileDashboardCard
              title="전체 주문"
              value={stats.total_orders}
              icon={Package}
              color="blue"
              trend={{ value: 12, isPositive: true }}
            />
            <MobileDashboardCard
              title="대기 중"
              value={stats.pending_orders}
              icon={Clock}
              color="yellow"
            />
            <MobileDashboardCard
              title="진행 중"
              value={stats.active_dispatches}
              icon={Truck}
              color="green"
            />
            <MobileDashboardCard
              title="오늘 완료"
              value={stats.completed_today}
              icon={CheckCircle}
              color="purple"
              trend={{ value: 8, isPositive: true }}
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {statCards.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">{stat.title}</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {stat.value}
                      </p>
                      {stat.trend && (
                        <p className="text-sm text-green-600 mt-2 flex items-center">
                          <TrendingUp size={16} className="mr-1" />
                          {stat.trend}
                        </p>
                      )}
                    </div>
                    <div className={`${stat.color} p-4 rounded-full`}>
                      <Icon className="text-white" size={24} />
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        )}

        {/* Chart */}
        <div className={`grid grid-cols-1 ${isMobile ? 'gap-4 px-4' : 'lg:grid-cols-2 gap-6'}`}>
          <Card title="주간 배송 추이">
            <div className={isMobile ? 'overflow-x-auto' : ''}>
              <Line data={chartData} options={chartOptions} />
            </div>
          </Card>

          <Card title="차량 현황">
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 md:p-4 bg-green-50 rounded-lg">
                <span className="text-sm md:text-base text-gray-700">가용 차량</span>
                <span className="text-xl md:text-2xl font-bold text-green-600">
                  {stats.available_vehicles}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 md:p-4 bg-blue-50 rounded-lg">
                <span className="text-sm md:text-base text-gray-700">운행 중</span>
                <span className="text-xl md:text-2xl font-bold text-blue-600">
                  {stats.active_vehicles}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 md:p-4 bg-gray-50 rounded-lg">
                <span className="text-sm md:text-base text-gray-700">전체 차량</span>
                <span className="text-xl md:text-2xl font-bold text-gray-600">
                  {stats.available_vehicles + stats.active_vehicles}
                </span>
              </div>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className={isMobile ? 'px-4' : ''}>
          <Card title="빠른 작업">
            <div className={`grid ${isMobile ? 'grid-cols-1 gap-3' : 'grid-cols-1 md:grid-cols-3 gap-4'}`}>
              <button 
                onClick={() => navigate('/orders')}
                className="p-3 md:p-4 bg-blue-50 hover:bg-blue-100 rounded-lg text-left transition-colors active:scale-95 cursor-pointer"
              >
                <Package className="text-blue-600 mb-2" size={isMobile ? 20 : 24} />
                <h3 className="font-semibold text-gray-900 text-sm md:text-base">새 주문 등록</h3>
                <p className="text-xs md:text-sm text-gray-600 mt-1">신규 배송 주문을 등록합니다</p>
              </button>
              <button 
                onClick={() => navigate('/optimization')}
                className="p-3 md:p-4 bg-green-50 hover:bg-green-100 rounded-lg text-left transition-colors active:scale-95 cursor-pointer"
              >
                <Truck className="text-green-600 mb-2" size={isMobile ? 20 : 24} />
                <h3 className="font-semibold text-gray-900 text-sm md:text-base">자동 배차</h3>
                <p className="text-xs md:text-sm text-gray-600 mt-1">대기 중인 주문을 자동 배차합니다</p>
              </button>
              <button 
                onClick={() => navigate('/dispatch/monitoring')}
                className="p-3 md:p-4 bg-purple-50 hover:bg-purple-100 rounded-lg text-left transition-colors active:scale-95 cursor-pointer"
              >
                <CheckCircle className="text-purple-600 mb-2" size={isMobile ? 20 : 24} />
                <h3 className="font-semibold text-gray-900 text-sm md:text-base">배송 현황</h3>
                <p className="text-xs md:text-sm text-gray-600 mt-1">진행 중인 배송을 모니터링합니다</p>
              </button>
            </div>
          </Card>
        </div>

        {/* Push Notification Settings */}
        <div className={isMobile ? 'px-4' : ''}>
          <NotificationSettings />
        </div>

        {/* UVIS Real-time Stats */}
        <div className={isMobile ? 'px-4' : ''}>
          <UvisFleetStats autoRefresh={true} refreshInterval={30000} />
        </div>

        {/* UVIS Alerts */}
        <div className={isMobile ? 'px-4' : ''}>
          <UvisAlerts limit={10} autoRefresh={true} refreshInterval={30000} />
        </div>
      </div>
  );
};

export default DashboardPage;
