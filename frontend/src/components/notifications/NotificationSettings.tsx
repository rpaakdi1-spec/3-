/**
 * 푸시 알림 설정 컴포넌트
 */

import React from 'react';
import { Bell, BellOff, Check, X } from 'lucide-react';
import { useFCM } from '../../hooks/useFCM';
import toast from 'react-hot-toast';

interface NotificationSettingsProps {
  className?: string;
}

export const NotificationSettings: React.FC<NotificationSettingsProps> = ({ className = '' }) => {
  const { permission, isSupported, requestPermission, unregisterToken } = useFCM();

  const handleEnableNotifications = async () => {
    const success = await requestPermission();
    if (!success) {
      toast.error('알림을 활성화할 수 없습니다. 브라우저 설정을 확인해주세요.');
    }
  };

  const handleDisableNotifications = async () => {
    const success = await unregisterToken();
    if (!success) {
      toast.error('알림을 비활성화할 수 없습니다.');
    }
  };

  if (!isSupported) {
    return (
      <div className={`bg-gray-100 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-gray-600">
          <BellOff className="w-5 h-5" />
          <span className="text-sm">이 브라우저는 푸시 알림을 지원하지 않습니다.</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow p-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-full ${
            permission === 'granted' ? 'bg-green-100' : 'bg-gray-100'
          }`}>
            {permission === 'granted' ? (
              <Bell className="w-5 h-5 text-green-600" />
            ) : (
              <BellOff className="w-5 h-5 text-gray-600" />
            )}
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900">푸시 알림</h3>
            <p className="text-sm text-gray-600">
              {permission === 'granted' && '알림이 활성화되었습니다'}
              {permission === 'denied' && '알림이 차단되었습니다'}
              {permission === 'default' && '주문, 배차 등 중요한 알림을 받으세요'}
            </p>
          </div>
        </div>

        <div>
          {permission === 'granted' ? (
            <button
              onClick={handleDisableNotifications}
              className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              <span className="text-sm font-medium">비활성화</span>
            </button>
          ) : permission === 'denied' ? (
            <div className="text-sm text-gray-500">
              브라우저 설정에서 알림을 허용해주세요
            </div>
          ) : (
            <button
              onClick={handleEnableNotifications}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Check className="w-4 h-4" />
              <span className="text-sm font-medium">활성화</span>
            </button>
          )}
        </div>
      </div>

      {permission === 'denied' && (
        <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
          <p className="text-sm text-yellow-800">
            💡 <strong>알림 허용 방법:</strong>
          </p>
          <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside space-y-1">
            <li>Chrome: 주소창 왼쪽 자물쇠 아이콘 → 사이트 설정 → 알림 허용</li>
            <li>Firefox: 주소창 왼쪽 아이콘 → 권한 → 알림 허용</li>
            <li>Safari: 설정 → Safari → 웹사이트 → 알림 → 허용</li>
          </ul>
        </div>
      )}
    </div>
  );
};
