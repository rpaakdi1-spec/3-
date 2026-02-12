/**
 * IoT 알림 센터 페이지
 * 전체 알림 목록 및 관리
 */

import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Bell,
  ArrowLeft,
  RefreshCw,
  Filter,
  Check,
} from 'lucide-react';
import {
  getAlerts,
  acknowledgeAlert,
  type Alert,
} from '../services/iotSensorService';

const IoTAlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'INFO' | 'WARNING' | 'CRITICAL' | 'unacknowledged'>('all');

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const data = await getAlerts();
      setAlerts(data);
    } catch (error) {
      console.error('알림 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    
    // 30초마다 자동 새로고침
    const interval = setInterval(fetchAlerts, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await acknowledgeAlert(alertId);
      // 로컬 상태 업데이트
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? { ...alert, acknowledged: true } : alert
      ));
    } catch (error) {
      console.error('알림 확인 처리 실패:', error);
      alert('알림 확인 처리에 실패했습니다');
    }
  };

  // 필터링된 알림
  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'all') return true;
    if (filter === 'unacknowledged') return !alert.acknowledged;
    return alert.alert_level === filter;
  });

  // 통계
  const stats = {
    total: alerts.length,
    critical: alerts.filter(a => a.alert_level === 'CRITICAL').length,
    warning: alerts.filter(a => a.alert_level === 'WARNING').length,
    info: alerts.filter(a => a.alert_level === 'INFO').length,
    unacknowledged: alerts.filter(a => !a.acknowledged).length,
  };

  const getAlertIcon = (level: string) => {
    switch (level) {
      case 'CRITICAL': return <XCircle className="w-5 h-5 text-red-600" />;
      case 'WARNING': return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'INFO': return <CheckCircle className="w-5 h-5 text-blue-600" />;
      default: return <Bell className="w-5 h-5 text-gray-600" />;
    }
  };

  const getAlertBgColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'bg-red-50 border-red-200';
      case 'WARNING': return 'bg-yellow-50 border-yellow-200';
      case 'INFO': return 'bg-blue-50 border-blue-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const getAlertBadgeColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'bg-red-100 text-red-800';
      case 'WARNING': return 'bg-yellow-100 text-yellow-800';
      case 'INFO': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link
            to="/iot/sensors"
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Bell className="w-8 h-8 text-blue-600" />
              알림 센터
            </h1>
            <p className="text-gray-600 mt-1">
              실시간 알림 모니터링 및 관리
            </p>
          </div>
        </div>
        <button
          onClick={fetchAlerts}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          새로고침
        </button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-gray-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전체 알림</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <Bell className="w-10 h-10 text-gray-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">위험</p>
              <p className="text-3xl font-bold text-red-600">{stats.critical}</p>
            </div>
            <XCircle className="w-10 h-10 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">경고</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.warning}</p>
            </div>
            <AlertTriangle className="w-10 h-10 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">정보</p>
              <p className="text-3xl font-bold text-blue-600">{stats.info}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">미확인</p>
              <p className="text-3xl font-bold text-purple-600">{stats.unacknowledged}</p>
            </div>
            <Bell className="w-10 h-10 text-purple-500" />
          </div>
        </div>
      </div>

      {/* 필터 */}
      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-5 h-5 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">필터:</span>
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 text-sm rounded ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            전체 ({stats.total})
          </button>
          <button
            onClick={() => setFilter('CRITICAL')}
            className={`px-3 py-1 text-sm rounded ${
              filter === 'CRITICAL'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            위험 ({stats.critical})
          </button>
          <button
            onClick={() => setFilter('WARNING')}
            className={`px-3 py-1 text-sm rounded ${
              filter === 'WARNING'
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            경고 ({stats.warning})
          </button>
          <button
            onClick={() => setFilter('INFO')}
            className={`px-3 py-1 text-sm rounded ${
              filter === 'INFO'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            정보 ({stats.info})
          </button>
          <button
            onClick={() => setFilter('unacknowledged')}
            className={`px-3 py-1 text-sm rounded ${
              filter === 'unacknowledged'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            미확인 ({stats.unacknowledged})
          </button>
        </div>
      </div>

      {/* 알림 목록 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            알림 목록 ({filteredAlerts.length}건)
          </h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-gray-600">알림 로딩 중...</span>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-xl text-gray-600">알림이 없습니다</p>
            <p className="text-sm text-gray-500 mt-2">
              {filter === 'all' ? '모든 알림이 처리되었습니다' : '해당 필터에 맞는 알림이 없습니다'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-6 hover:bg-gray-50 transition-colors ${
                  alert.acknowledged ? 'opacity-60' : ''
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 mt-1">
                    {getAlertIcon(alert.alert_level)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getAlertBadgeColor(alert.alert_level)}`}>
                            {alert.alert_level}
                          </span>
                          <span className="text-sm text-gray-500">
                            {alert.vehicle_id} / {alert.sensor_id}
                          </span>
                        </div>
                        <p className="text-base font-medium text-gray-900">
                          {alert.message}
                        </p>
                      </div>
                      
                      {!alert.acknowledged && (
                        <button
                          onClick={() => handleAcknowledge(alert.id)}
                          className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors flex-shrink-0"
                        >
                          <Check className="w-4 h-4" />
                          확인
                        </button>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>
                        {new Date(alert.timestamp).toLocaleString('ko-KR')}
                      </span>
                      {alert.acknowledged && (
                        <span className="inline-flex items-center gap-1 text-green-600">
                          <Check className="w-4 h-4" />
                          확인됨
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
    </Layout>
  );
};

export default IoTAlertsPage;
