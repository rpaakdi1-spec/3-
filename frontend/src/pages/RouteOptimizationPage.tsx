import React, { useState } from 'react';
import { Navigation, MapPin, Clock, DollarSign, TrendingUp, Route } from 'lucide-react';

interface RouteData {
  id: number;
  route_name: string;
  distance: number;
  duration: number;
  duration_in_traffic: number | null;
  traffic_level: string | null;
  toll_fee: number;
  fuel_cost: number | null;
  total_cost: number;
  optimization_score: number | null;
  is_optimal: boolean;
}

const RouteOptimizationPage: React.FC = () => {
  const [originLat, setOriginLat] = useState('37.5665');
  const [originLng, setOriginLng] = useState('126.9780');
  const [destLat, setDestLat] = useState('37.4979');
  const [destLng, setDestLng] = useState('127.0276');
  const [routes, setRoutes] = useState<RouteData[]>([]);
  const [loading, setLoading] = useState(false);

  const optimizeRoute = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch('/api/v1/routes/alternatives', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          origin_lat: parseFloat(originLat),
          origin_lng: parseFloat(originLng),
          destination_lat: parseFloat(destLat),
          destination_lng: parseFloat(destLng)
        })
      });
      
      const data = await response.json();
      setRoutes(data.routes || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to optimize route:', error);
      setLoading(false);
    }
  };

  const getTrafficLevelColor = (level: string | null) => {
    if (!level) return 'bg-gray-100 text-gray-800';
    switch (level) {
      case 'SMOOTH': return 'bg-green-100 text-green-800';
      case 'NORMAL': return 'bg-blue-100 text-blue-800';
      case 'SLOW': return 'bg-yellow-100 text-yellow-800';
      case 'CONGESTED': return 'bg-orange-100 text-orange-800';
      case 'BLOCKED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTrafficLevelText = (level: string | null) => {
    if (!level) return '-';
    switch (level) {
      case 'SMOOTH': return '원활';
      case 'NORMAL': return '보통';
      case 'SLOW': return '서행';
      case 'CONGESTED': return '혼잡';
      case 'BLOCKED': return '정체';
      default: return level;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Navigation className="h-8 w-8 mr-3 text-blue-600" />
          경로 최적화
        </h1>
        <p className="text-gray-600 mt-2">실시간 교통 정보 기반 경로 계산</p>
      </div>

      {/* Input Form */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <MapPin className="h-6 w-6 mr-2 text-blue-600" />
          출발지 & 목적지 설정
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Origin */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">출발지</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">위도</label>
                <input
                  type="number"
                  step="0.0001"
                  value={originLat}
                  onChange={(e) => setOriginLat(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="37.5665"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">경도</label>
                <input
                  type="number"
                  step="0.0001"
                  value={originLng}
                  onChange={(e) => setOriginLng(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="126.9780"
                />
              </div>
            </div>
          </div>

          {/* Destination */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">목적지</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">위도</label>
                <input
                  type="number"
                  step="0.0001"
                  value={destLat}
                  onChange={(e) => setDestLat(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="37.4979"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">경도</label>
                <input
                  type="number"
                  step="0.0001"
                  value={destLng}
                  onChange={(e) => setDestLng(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="127.0276"
                />
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={optimizeRoute}
          disabled={loading}
          className="mt-6 w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition flex items-center justify-center disabled:bg-gray-400"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              경로 계산 중...
            </>
          ) : (
            <>
              <Route className="h-5 w-5 mr-2" />
              경로 최적화 실행
            </>
          )}
        </button>
      </div>

      {/* Route Results */}
      {routes.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <TrendingUp className="h-6 w-6 mr-2 text-blue-600" />
            추천 경로 ({routes.length}개)
          </h2>
          
          {routes.map((route, index) => (
            <div
              key={route.id}
              className={`bg-white rounded-lg shadow-sm p-6 border-2 ${
                route.is_optimal ? 'border-blue-500' : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-bold text-gray-900">
                      {route.route_name || `경로 ${index + 1}`}
                    </h3>
                    {route.is_optimal && (
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium">
                        ⭐ 최적 경로
                      </span>
                    )}
                    {route.traffic_level && (
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTrafficLevelColor(route.traffic_level)}`}>
                        {getTrafficLevelText(route.traffic_level)}
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-4">
                    {/* Distance */}
                    <div className="bg-purple-50 rounded-lg p-3">
                      <MapPin className="h-5 w-5 text-purple-600 mb-1" />
                      <p className="text-xs text-gray-600">거리</p>
                      <p className="text-lg font-bold text-gray-900">{route.distance.toFixed(1)} km</p>
                    </div>

                    {/* Duration */}
                    <div className="bg-blue-50 rounded-lg p-3">
                      <Clock className="h-5 w-5 text-blue-600 mb-1" />
                      <p className="text-xs text-gray-600">소요시간</p>
                      <p className="text-lg font-bold text-gray-900">{route.duration} 분</p>
                      {route.duration_in_traffic && route.duration_in_traffic !== route.duration && (
                        <p className="text-xs text-orange-600">교통: {route.duration_in_traffic}분</p>
                      )}
                    </div>

                    {/* Toll Fee */}
                    <div className="bg-yellow-50 rounded-lg p-3">
                      <DollarSign className="h-5 w-5 text-yellow-600 mb-1" />
                      <p className="text-xs text-gray-600">통행료</p>
                      <p className="text-lg font-bold text-gray-900">₩{route.toll_fee.toLocaleString()}</p>
                    </div>

                    {/* Fuel Cost */}
                    <div className="bg-green-50 rounded-lg p-3">
                      <DollarSign className="h-5 w-5 text-green-600 mb-1" />
                      <p className="text-xs text-gray-600">연료비</p>
                      <p className="text-lg font-bold text-gray-900">
                        ₩{route.fuel_cost?.toLocaleString() || 0}
                      </p>
                    </div>

                    {/* Total Cost */}
                    <div className="bg-orange-50 rounded-lg p-3">
                      <DollarSign className="h-5 w-5 text-orange-600 mb-1" />
                      <p className="text-xs text-gray-600">총 비용</p>
                      <p className="text-lg font-bold text-gray-900">₩{route.total_cost.toLocaleString()}</p>
                    </div>
                  </div>

                  {route.optimization_score !== null && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">최적화 점수</span>
                        <span className="text-sm font-bold text-gray-900">{route.optimization_score.toFixed(1)} / 100</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${route.optimization_score}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {routes.length === 0 && !loading && (
        <div className="bg-white rounded-lg shadow-sm p-12 border border-gray-200 text-center">
          <Route className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">출발지와 목적지를 입력하고 경로 최적화를 실행하세요</p>
        </div>
      )}
    </div>
  );
};

export default RouteOptimizationPage;
