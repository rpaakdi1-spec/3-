import React, { useState, useEffect } from 'react';
import { AlertTriangle, AlertCircle, ThermometerSnowflake, Power, Clock, Signal } from 'lucide-react';
import Card from '../common/Card';
import { toast } from 'react-hot-toast';

interface UvisAlert {
  type: string;
  severity: string;
  message: string;
  value?: number | string;
  threshold?: number | string;
  vehicle_id: number;
  plate_number: string;
  timestamp: string;
}

interface UvisAlertsProps {
  vehicleId?: number;
  limit?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const UvisAlerts: React.FC<UvisAlertsProps> = ({
  vehicleId,
  limit = 20,
  autoRefresh = true,
  refreshInterval = 30000, // 30초
}) => {
  const [alerts, setAlerts] = useState<UvisAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  const fetchAlerts = async () => {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      if (vehicleId) params.append('vehicle_id', vehicleId.toString());
      if (filter !== 'all') params.append('alert_type', filter);

      const response = await fetch(`/api/v1/vehicles/alerts/recent?${params}`);
      const data = await response.json();
      
      setAlerts(data.alerts || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      toast.error('알림 조회에 실패했습니다');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    
    if (autoRefresh) {
      const interval = setInterval(fetchAlerts, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [vehicleId, filter, autoRefresh, refreshInterval]);

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'speed_abnormal_high':
      case 'speed_warning_high':
        return <AlertTriangle size={20} />;
      case 'temperature_high':
      case 'temperature_critical':
      case 'temperature_out_of_range':
        return <ThermometerSnowflake size={20} />;
      case 'engine_on':
      case 'engine_off':
        return <Power size={20} />;
      case 'engine_off_long':
        return <Clock size={20} />;
      case 'gps_signal_lost':
        return <Signal size={20} />;
      default:
        return <AlertCircle size={20} />;
    }
  };

  const getAlertColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getAlertBadgeColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'info':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return '방금 전';
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}시간 전`;
    return date.toLocaleString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const alertTypes = [
    { value: 'all', label: '전체' },
    { value: 'speed_abnormal_high', label: '과속' },
    { value: 'temperature_critical', label: '온도 이상' },
    { value: 'engine_off_long', label: '장시간 정차' },
    { value: 'gps_signal_lost', label: 'GPS 손실' },
  ];

  if (loading) {
    return (
      <Card>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="space-y-4">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-gray-800">
            UVIS 알림 {alerts.length > 0 && `(${alerts.length})`}
          </h3>
          <div className="flex gap-2">
            {alertTypes.map(type => (
              <button
                key={type.value}
                onClick={() => setFilter(type.value)}
                className={`px-3 py-1 text-sm rounded-full transition-colors ${
                  filter === type.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* 알림 목록 */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {alerts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              최근 24시간 이내 알림이 없습니다
            </div>
          ) : (
            alerts.map((alert, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border transition-all hover:shadow-md ${getAlertColor(alert.severity)}`}
              >
                <div className="flex items-start gap-3">
                  {/* 아이콘 */}
                  <div className="flex-shrink-0 mt-0.5">
                    {getAlertIcon(alert.type)}
                  </div>
                  
                  {/* 내용 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold">{alert.plate_number}</span>
                      <span className={`px-2 py-0.5 text-xs rounded-full ${getAlertBadgeColor(alert.severity)}`}>
                        {alert.severity === 'critical' ? '위험' : 
                         alert.severity === 'warning' ? '경고' : '정보'}
                      </span>
                    </div>
                    
                    <p className="text-sm mb-2">{alert.message}</p>
                    
                    {(alert.value !== undefined || alert.threshold !== undefined) && (
                      <div className="flex gap-4 text-xs text-gray-600">
                        {alert.value !== undefined && (
                          <span>현재값: <strong>{alert.value}</strong></span>
                        )}
                        {alert.threshold !== undefined && (
                          <span>기준값: <strong>{alert.threshold}</strong></span>
                        )}
                      </div>
                    )}
                    
                    <div className="mt-2 text-xs text-gray-500">
                      {formatTimestamp(alert.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </Card>
  );
};

export default UvisAlerts;
