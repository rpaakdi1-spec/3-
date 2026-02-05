import React, { useState, useEffect } from 'react';
import { Bell, BellOff, Check, X } from 'lucide-react';
import { fcmService } from '../services/fcmService';
import toast from 'react-hot-toast';

interface NotificationSettingsProps {
  userId: number;
  onTokenObtained?: (token: string) => void;
}

export const NotificationSettings: React.FC<NotificationSettingsProps> = ({
  userId,
  onTokenObtained
}) => {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSupported, setIsSupported] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fcmToken, setFcmToken] = useState<string | null>(null);

  useEffect(() => {
    // 알림 지원 여부 확인
    setIsSupported(fcmService.isSupported());
    
    // 초기 권한 상태 확인
    setPermission(fcmService.getNotificationPermission());
    
    // Firebase 초기화
    fcmService.initialize();
    
    // 포그라운드 메시지 리스너 등록
    fcmService.onMessageListener((payload) => {
      console.log('Received foreground message:', payload);
      // 필요한 경우 추가 처리
    });
  }, []);

  const handleEnableNotifications = async () => {
    setLoading(true);
    
    try {
      // FCM 토큰 요청
      const token = await fcmService.requestPermissionAndGetToken();
      
      if (token) {
        setFcmToken(token);
        setPermission('granted');
        
        // 서버에 토큰 저장
        const saved = await fcmService.saveTokenToServer(token, userId);
        
        if (saved) {
          toast.success('알림이 활성화되었습니다!');
          onTokenObtained?.(token);
        } else {
          toast.error('토큰 저장에 실패했습니다');
        }
      } else {
        setPermission(fcmService.getNotificationPermission());
      }
    } catch (error) {
      console.error('Error enabling notifications:', error);
      toast.error('알림 활성화에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleTestNotification = () => {
    if (permission === 'granted') {
      new Notification('테스트 알림', {
        body: '알림이 정상적으로 작동합니다! 🎉',
        icon: '/logo192.png',
        badge: '/badge.png',
        vibrate: [200, 100, 200]
      });
    }
  };

  if (!isSupported) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center gap-2 text-yellow-800">
          <BellOff className="w-5 h-5" />
          <span className="font-medium">이 브라우저는 알림을 지원하지 않습니다</span>
        </div>
        <p className="text-sm text-yellow-700 mt-2">
          Chrome, Firefox, Edge 등 최신 브라우저를 사용해주세요.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 권한 상태 */}
      <div className={`p-4 rounded-lg border ${
        permission === 'granted' 
          ? 'bg-green-50 border-green-200' 
          : permission === 'denied'
          ? 'bg-red-50 border-red-200'
          : 'bg-gray-50 border-gray-200'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {permission === 'granted' ? (
              <div className="p-2 bg-green-100 rounded-full">
                <Check className="w-5 h-5 text-green-600" />
              </div>
            ) : permission === 'denied' ? (
              <div className="p-2 bg-red-100 rounded-full">
                <X className="w-5 h-5 text-red-600" />
              </div>
            ) : (
              <div className="p-2 bg-gray-100 rounded-full">
                <Bell className="w-5 h-5 text-gray-600" />
              </div>
            )}
            
            <div>
              <h3 className="font-semibold text-gray-900">
                {permission === 'granted' 
                  ? '알림 활성화됨' 
                  : permission === 'denied'
                  ? '알림 차단됨'
                  : '알림 비활성화'}
              </h3>
              <p className="text-sm text-gray-600">
                {permission === 'granted' 
                  ? '새로운 주문과 배차 알림을 받을 수 있습니다' 
                  : permission === 'denied'
                  ? '브라우저 설정에서 알림을 허용해주세요'
                  : '알림을 활성화하여 실시간 업데이트를 받으세요'}
              </p>
            </div>
          </div>

          {permission !== 'granted' && permission !== 'denied' && (
            <button
              onClick={handleEnableNotifications}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? '활성화 중...' : '알림 활성화'}
            </button>
          )}

          {permission === 'granted' && (
            <button
              onClick={handleTestNotification}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              테스트 알림
            </button>
          )}
        </div>
      </div>

      {/* FCM 토큰 정보 (개발 모드) */}
      {fcmToken && import.meta.env.DEV && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-blue-900 mb-2">FCM Token (개발 모드)</h4>
          <code className="text-xs text-blue-700 break-all block p-2 bg-white rounded">
            {fcmToken}
          </code>
        </div>
      )}

      {/* 알림 설정 안내 */}
      {permission === 'denied' && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="font-semibold text-red-900 mb-2">알림 권한이 차단되었습니다</h4>
          <ol className="text-sm text-red-700 space-y-1 list-decimal list-inside">
            <li>브라우저 주소창 왼쪽의 자물쇠 아이콘을 클릭하세요</li>
            <li>"알림" 설정을 "허용"으로 변경하세요</li>
            <li>페이지를 새로고침하세요</li>
          </ol>
        </div>
      )}
    </div>
  );
};
