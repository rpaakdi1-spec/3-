import React, { useEffect, useState } from 'react';
import { Bell, Check, CheckCheck, ExternalLink, Trash2, Filter } from 'lucide-react';

interface Notification {
  id: number;
  notification_type: string;
  title: string;
  message: string;
  dispatch_id: number | null;
  is_read: boolean;
  read_at: string | null;
  action_required: boolean;
  action_url: string | null;
  action_taken: boolean;
  created_at: string;
}

const DriverNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const fetchNotifications = async () => {
    try {
      const token = localStorage.getItem('token');
      const unreadOnly = filter === 'unread';
      
      const response = await fetch(`/api/v1/driver/notifications?unread_only=${unreadOnly}&limit=100`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      setNotifications(data.notifications || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      const token = localStorage.getItem('token');
      
      await fetch(`/api/v1/driver/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // 목록 갱신
      fetchNotifications();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const markActionTaken = async (notificationId: number) => {
    try {
      const token = localStorage.getItem('token');
      
      await fetch(`/api/v1/driver/notifications/${notificationId}/action`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // 목록 갱신
      fetchNotifications();
    } catch (error) {
      console.error('Failed to mark action:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'DISPATCH_ASSIGNED':
        return '🚚';
      case 'DISPATCH_UPDATED':
        return '🔄';
      case 'DISPATCH_CANCELLED':
        return '❌';
      case 'ROUTE_OPTIMIZED':
        return '🗺️';
      case 'CHAT_MESSAGE':
        return '💬';
      case 'SYSTEM_ALERT':
        return '⚠️';
      case 'PERFORMANCE_UPDATE':
        return '📊';
      default:
        return '🔔';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'DISPATCH_ASSIGNED':
        return 'bg-blue-50 border-blue-200';
      case 'DISPATCH_UPDATED':
        return 'bg-yellow-50 border-yellow-200';
      case 'DISPATCH_CANCELLED':
        return 'bg-red-50 border-red-200';
      case 'ROUTE_OPTIMIZED':
        return 'bg-green-50 border-green-200';
      case 'CHAT_MESSAGE':
        return 'bg-purple-50 border-purple-200';
      case 'SYSTEM_ALERT':
        return 'bg-orange-50 border-orange-200';
      default:
        return 'bg-gray-50 border-gray-200';
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

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Bell className="h-8 w-8 mr-3 text-blue-600" />
          알림
        </h1>
        <p className="text-gray-600 mt-2">배차 및 시스템 알림</p>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200 mb-6">
        <div className="flex items-center space-x-4">
          <Filter className="h-5 w-5 text-gray-600" />
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            전체
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === 'unread'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            읽지 않음
          </button>
        </div>
      </div>

      {/* Notifications List */}
      <div className="space-y-4">
        {notifications.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-8 border border-gray-200 text-center">
            <Bell className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">알림이 없습니다</p>
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              className={`bg-white rounded-lg shadow-sm p-6 border-2 transition hover:shadow-md ${
                getNotificationColor(notification.notification_type)
              } ${notification.is_read ? 'opacity-60' : ''}`}
            >
              <div className="flex items-start">
                {/* Icon */}
                <div className="text-3xl mr-4">
                  {getNotificationIcon(notification.notification_type)}
                </div>

                {/* Content */}
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{notification.title}</h3>
                      <p className="text-gray-700 mt-1">{notification.message}</p>
                      
                      {/* Metadata */}
                      <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                        <span>{new Date(notification.created_at).toLocaleString('ko-KR')}</span>
                        {notification.dispatch_id && (
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            배차 #{notification.dispatch_id}
                          </span>
                        )}
                        {notification.action_required && (
                          <span className="bg-red-100 text-red-800 px-2 py-1 rounded">
                            액션 필요
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Status Badge */}
                    <div>
                      {notification.is_read ? (
                        <CheckCheck className="h-6 w-6 text-green-600" />
                      ) : (
                        <div className="h-3 w-3 bg-blue-600 rounded-full"></div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-3 mt-4">
                    {!notification.is_read && (
                      <button
                        onClick={() => markAsRead(notification.id)}
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
                      >
                        <Check className="h-4 w-4" />
                        <span>읽음 표시</span>
                      </button>
                    )}
                    
                    {notification.action_required && !notification.action_taken && (
                      <button
                        onClick={() => markActionTaken(notification.id)}
                        className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm"
                      >
                        <ExternalLink className="h-4 w-4" />
                        <span>액션 완료</span>
                      </button>
                    )}

                    {notification.action_url && (
                      <a
                        href={notification.action_url}
                        className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition text-sm"
                      >
                        <ExternalLink className="h-4 w-4" />
                        <span>상세 보기</span>
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DriverNotifications;
