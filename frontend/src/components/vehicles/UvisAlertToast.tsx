import React, { useEffect, useState } from 'react';
import { AlertTriangle, Bell, AlertCircle, XCircle, X } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface Alert {
  id?: number;
  vehicle_id: number;
  vehicle_plate: string;
  alert_type: string;
  severity: 'info' | 'warning' | 'danger' | 'critical';
  title: string;
  message: string;
  data?: any;
  created_at: string;
}

interface UvisAlertToastProps {
  enabled?: boolean;
}

const UvisAlertToast: React.FC<UvisAlertToastProps> = ({ enabled = true }) => {
  const [lastAlertId, setLastAlertId] = useState<number | null>(null);

  // 심각도별 아이콘 및 색상
  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'critical':
        return {
          icon: <XCircle size={20} />,
          bgColor: 'bg-red-50',
          borderColor: 'border-red-500',
          textColor: 'text-red-900',
          iconColor: 'text-red-600',
        };
      case 'danger':
        return {
          icon: <AlertTriangle size={20} />,
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-500',
          textColor: 'text-orange-900',
          iconColor: 'text-orange-600',
        };
      case 'warning':
        return {
          icon: <AlertCircle size={20} />,
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-500',
          textColor: 'text-yellow-900',
          iconColor: 'text-yellow-600',
        };
      default:
        return {
          icon: <Bell size={20} />,
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-500',
          textColor: 'text-blue-900',
          iconColor: 'text-blue-600',
        };
    }
  };

  // 알림 타입 한글명
  const getAlertTypeName = (type: string) => {
    const types: Record<string, string> = {
      speed_warning: '속도 경고',
      speed_danger: '속도 위험',
      speed_sensor_error: '센서 오류',
      engine_on: '엔진 켜짐',
      engine_off: '엔진 꺼짐',
      engine_off_prolonged: '장시간 정차',
      temp_frozen: '온도 낮음',
      temp_high_warning: '온도 높음',
      temp_critical: '온도 치명적',
      gps_signal_lost: 'GPS 신호 손실',
    };
    return types[type] || type;
  };

  // 커스텀 토스트 컴포넌트
  const CustomToast = ({ alert, onDismiss }: { alert: Alert; onDismiss: () => void }) => {
    const config = getSeverityConfig(alert.severity);

    return (
      <div
        className={`${config.bgColor} ${config.borderColor} border-l-4 p-4 rounded-r-lg shadow-lg max-w-md`}
        onClick={() => {
          // 차량 페이지로 이동
          window.location.href = `/vehicles?vehicle_id=${alert.vehicle_id}`;
        }}
      >
        <div className="flex items-start gap-3 cursor-pointer">
          <div className={config.iconColor}>{config.icon}</div>
          <div className="flex-1">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className={`font-semibold ${config.textColor}`}>
                  {getAlertTypeName(alert.alert_type)}
                </p>
                <p className={`text-sm ${config.textColor} mt-1`}>
                  {alert.vehicle_plate} - {alert.title}
                </p>
                <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDismiss();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // 새 알림 체크 및 토스트 표시
  const checkNewAlerts = async () => {
    if (!enabled) return;

    try {
      const response = await fetch('/api/v1/vehicles/alerts/recent?limit=1');
      const data = await response.json();

      if (data.alerts && data.alerts.length > 0) {
        const latestAlert = data.alerts[0];

        // 새 알림인지 확인 (ID 또는 timestamp 기준)
        if (lastAlertId === null || latestAlert.id > lastAlertId) {
          setLastAlertId(latestAlert.id);

          // 토스트 표시
          toast.custom(
            (t) => <CustomToast alert={latestAlert} onDismiss={() => toast.dismiss(t.id)} />,
            {
              duration: 8000, // 8초 동안 표시
              position: 'top-right',
            }
          );

          // 브라우저 알림 (권한이 있는 경우)
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(`${getAlertTypeName(latestAlert.alert_type)} - ${latestAlert.vehicle_plate}`, {
              body: latestAlert.message,
              icon: '/logo.png',
              tag: `uvis-alert-${latestAlert.id}`,
            });
          }
        }
      }
    } catch (error) {
      console.error('Failed to check alerts:', error);
    }
  };

  // 브라우저 알림 권한 요청
  const requestNotificationPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  };

  useEffect(() => {
    if (!enabled) return;

    // 브라우저 알림 권한 요청
    requestNotificationPermission();

    // 초기 알림 ID 가져오기
    checkNewAlerts();

    // 30초마다 새 알림 체크
    const interval = setInterval(checkNewAlerts, 30000);

    return () => clearInterval(interval);
  }, [enabled, lastAlertId]);

  return null; // UI 없음 (토스트만 표시)
};

export default UvisAlertToast;
