import React, { useEffect, useState } from 'react';
import { Bell, MessageSquare, TrendingUp, Package, DollarSign, Star, Award, Clock } from 'lucide-react';

interface PerformanceStats {
  today: {
    total_dispatches: number;
    completed_dispatches: number;
    total_distance: number;
    total_revenue: number;
    avg_rating: number;
  } | null;
  weekly: {
    total_dispatches: number;
    completed_dispatches: number;
    total_distance: number;
    total_revenue: number;
    avg_rating: number;
  } | null;
  monthly: {
    total_dispatches: number;
    completed_dispatches: number;
    total_distance: number;
    total_revenue: number;
    avg_rating: number;
    rank: number;
  } | null;
}

const DriverDashboard: React.FC = () => {
  const [stats, setStats] = useState<PerformanceStats | null>(null);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // 30초마다 갱신
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // 성과 통계
      const statsRes = await fetch('/api/v1/driver/performance/statistics', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const statsData = await statsRes.json();
      setStats(statsData);

      // 읽지 않은 알림
      const notifRes = await fetch('/api/v1/driver/notifications/unread-count', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const notifData = await notifRes.json();
      setUnreadNotifications(notifData.unread_count || 0);

      // 읽지 않은 메시지
      const chatRes = await fetch('/api/v1/driver/chat/unread-count', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const chatData = await chatRes.json();
      setUnreadMessages(chatData.unread_count || 0);

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch driver dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  const todayStats = stats?.today;
  const weeklyStats = stats?.weekly;
  const monthlyStats = stats?.monthly;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">🚚 드라이버 대시보드</h1>
        <p className="text-gray-600 mt-2">실시간 성과 및 활동 현황</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">알림</p>
              <p className="text-2xl font-bold text-gray-900">{unreadNotifications}</p>
              <p className="text-xs text-gray-500 mt-1">읽지 않은 알림</p>
            </div>
            <div className="relative">
              <Bell className="h-12 w-12 text-blue-600" />
              {unreadNotifications > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {unreadNotifications}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">채팅</p>
              <p className="text-2xl font-bold text-gray-900">{unreadMessages}</p>
              <p className="text-xs text-gray-500 mt-1">읽지 않은 메시지</p>
            </div>
            <div className="relative">
              <MessageSquare className="h-12 w-12 text-green-600" />
              {unreadMessages > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {unreadMessages}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">내 순위</p>
              <p className="text-2xl font-bold text-gray-900">
                {monthlyStats?.rank ? `#${monthlyStats.rank}` : '-'}
              </p>
              <p className="text-xs text-gray-500 mt-1">이번 달 순위</p>
            </div>
            <Award className="h-12 w-12 text-yellow-600" />
          </div>
        </div>
      </div>

      {/* Today's Performance */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <Clock className="h-6 w-6 mr-2 text-blue-600" />
            오늘의 성과
          </h2>
          <span className="text-sm text-gray-500">
            {new Date().toLocaleDateString('ko-KR', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <Package className="h-8 w-8 text-blue-600 mb-2" />
            <p className="text-sm text-gray-600">총 배차</p>
            <p className="text-2xl font-bold text-gray-900">{todayStats?.total_dispatches || 0}</p>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <Package className="h-8 w-8 text-green-600 mb-2" />
            <p className="text-sm text-gray-600">완료</p>
            <p className="text-2xl font-bold text-gray-900">{todayStats?.completed_dispatches || 0}</p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <TrendingUp className="h-8 w-8 text-purple-600 mb-2" />
            <p className="text-sm text-gray-600">이동 거리</p>
            <p className="text-2xl font-bold text-gray-900">
              {todayStats?.total_distance?.toFixed(1) || 0} km
            </p>
          </div>

          <div className="bg-yellow-50 rounded-lg p-4">
            <DollarSign className="h-8 w-8 text-yellow-600 mb-2" />
            <p className="text-sm text-gray-600">수익</p>
            <p className="text-2xl font-bold text-gray-900">
              ₩{todayStats?.total_revenue?.toLocaleString() || 0}
            </p>
          </div>

          <div className="bg-orange-50 rounded-lg p-4">
            <Star className="h-8 w-8 text-orange-600 mb-2" />
            <p className="text-sm text-gray-600">평점</p>
            <p className="text-2xl font-bold text-gray-900">
              {todayStats?.avg_rating?.toFixed(1) || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Weekly & Monthly Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Weekly */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">이번 주 성과</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">총 배차</span>
              <span className="font-bold text-gray-900">{weeklyStats?.total_dispatches || 0} 건</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">완료율</span>
              <span className="font-bold text-green-600">
                {weeklyStats?.total_dispatches ? 
                  ((weeklyStats.completed_dispatches / weeklyStats.total_dispatches) * 100).toFixed(1) 
                  : 0}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">이동 거리</span>
              <span className="font-bold text-gray-900">{weeklyStats?.total_distance?.toFixed(1) || 0} km</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">수익</span>
              <span className="font-bold text-blue-600">₩{weeklyStats?.total_revenue?.toLocaleString() || 0}</span>
            </div>
          </div>
        </div>

        {/* Monthly */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">이번 달 성과</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">총 배차</span>
              <span className="font-bold text-gray-900">{monthlyStats?.total_dispatches || 0} 건</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">완료율</span>
              <span className="font-bold text-green-600">
                {monthlyStats?.total_dispatches ? 
                  ((monthlyStats.completed_dispatches / monthlyStats.total_dispatches) * 100).toFixed(1) 
                  : 0}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">이동 거리</span>
              <span className="font-bold text-gray-900">{monthlyStats?.total_distance?.toFixed(1) || 0} km</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">수익</span>
              <span className="font-bold text-blue-600">₩{monthlyStats?.total_revenue?.toLocaleString() || 0}</span>
            </div>
            {monthlyStats?.rank && (
              <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                <span className="text-gray-600 font-medium">순위</span>
                <span className="font-bold text-yellow-600 text-xl">#{monthlyStats.rank}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DriverDashboard;
