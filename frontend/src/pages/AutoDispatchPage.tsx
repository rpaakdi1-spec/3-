/**
 * Phase 12: 자동 배차 페이지
 * AI 기반 최적 차량 자동 선택
 */
import React, { useState } from 'react';
import { Zap, Truck, MapPin, Clock, TrendingUp, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';

interface DispatchResult {
  success: boolean;
  dispatch_id?: number;
  vehicle?: {
    id: number;
    license_plate: string;
    vehicle_type: string;
    temperature_type?: string;
  };
  driver?: {
    id: number;
    name: string;
    phone: string;
    rating?: number;
  };
  location?: {
    latitude: number;
    longitude: number;
  };
  distance_km: number;
  estimated_time_min: number;
  alternatives?: Array<{
    vehicle_id: number;
    distance_km: number;
    estimated_time_min: number;
  }>;
  reasoning: string;
}

const AutoDispatchPage: React.FC = () => {
  const [orderId, setOrderId] = useState('');
  const [applyRules, setApplyRules] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DispatchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAutoDispatch = async () => {
    if (!orderId) {
      setError('주문 ID를 입력해주세요');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.post('/dispatch/auto', {
        order_id: parseInt(orderId),
        apply_rules: applyRules,
        simulate: false,
      });

      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '자동 배차에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async () => {
    if (!orderId) {
      setError('주문 ID를 입력해주세요');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.post('/dispatch/auto', {
        order_id: parseInt(orderId),
        apply_rules: applyRules,
        simulate: true,
      });

      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '시뮬레이션에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Zap className="w-7 h-7 text-yellow-500" />
          AI 자동 배차
        </h1>
        <p className="text-gray-600 mt-1">
          인공지능이 최적의 차량과 기사를 자동으로 선택합니다
        </p>
      </div>

      {/* 입력 폼 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-bold mb-4">배차 설정</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              주문 ID
            </label>
            <input
              type="number"
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
              placeholder="주문 ID를 입력하세요"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="applyRules"
              checked={applyRules}
              onChange={(e) => setApplyRules(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <label htmlFor="applyRules" className="text-sm font-medium">
              배차 규칙 적용 (Phase 10)
            </label>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleSimulate}
              disabled={loading || !orderId}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50"
            >
              <TrendingUp className="w-5 h-5" />
              시뮬레이션
            </button>
            <button
              onClick={handleAutoDispatch}
              disabled={loading || !orderId}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              <Zap className="w-5 h-5" />
              {loading ? '처리중...' : '자동 배차 실행'}
            </button>
          </div>
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-red-800">오류 발생</h3>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* 결과 */}
      {result && result.success && (
        <div className="space-y-4">
          {/* 성공 메시지 */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-green-800">
                {result.simulated ? '시뮬레이션 완료' : '자동 배차 완료'}
              </h3>
              <p className="text-sm text-green-600 mt-1">
                최적의 차량과 기사가 선택되었습니다
                {result.dispatch_id && ` (배차 ID: ${result.dispatch_id})`}
              </p>
            </div>
          </div>

          {/* 배차 결과 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-bold mb-4">배차 결과</h2>
            
            {/* 차량 & 기사 정보 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* 차량 */}
              {result.vehicle && (
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Truck className="w-5 h-5 text-blue-500" />
                    <h3 className="font-bold">선택된 차량</h3>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">차량번호:</span>
                      <span className="font-medium">{result.vehicle.license_plate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">차량타입:</span>
                      <span className="font-medium">{result.vehicle.vehicle_type}</span>
                    </div>
                    {result.vehicle.temperature_type && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">온도타입:</span>
                        <span className="font-medium">{result.vehicle.temperature_type}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 기사 */}
              {result.driver && (
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <MapPin className="w-5 h-5 text-green-500" />
                    <h3 className="font-bold">배정 기사</h3>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">이름:</span>
                      <span className="font-medium">{result.driver.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">연락처:</span>
                      <span className="font-medium">{result.driver.phone}</span>
                    </div>
                    {result.driver.rating && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">평점:</span>
                        <span className="font-medium text-yellow-600">
                          ⭐ {result.driver.rating.toFixed(1)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* 거리 & 시간 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <span className="text-sm font-medium text-blue-900">예상 거리</span>
                </div>
                <p className="text-2xl font-bold text-blue-600">
                  {result.distance_km.toFixed(1)} km
                </p>
              </div>

              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-5 h-5 text-green-600" />
                  <span className="text-sm font-medium text-green-900">예상 시간</span>
                </div>
                <p className="text-2xl font-bold text-green-600">
                  {result.estimated_time_min}분
                </p>
              </div>
            </div>

            {/* AI 선택 이유 */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h3 className="font-bold text-purple-900 mb-2">🤖 AI 선택 이유</h3>
              <p className="text-sm text-purple-700">{result.reasoning}</p>
            </div>

            {/* 대안 차량 */}
            {result.alternatives && result.alternatives.length > 0 && (
              <div className="mt-6">
                <h3 className="font-bold mb-3">대안 차량</h3>
                <div className="space-y-2">
                  {result.alternatives.map((alt, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm"
                    >
                      <span className="font-medium">차량 #{alt.vehicle_id}</span>
                      <div className="flex items-center gap-4 text-gray-600">
                        <span>{alt.distance_km.toFixed(1)} km</span>
                        <span>{alt.estimated_time_min}분</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 기능 설명 */}
      {!result && !error && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-bold text-blue-900 mb-3">🚀 자동 배차 기능</h3>
          <ul className="space-y-2 text-sm text-blue-700">
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>가용 차량 자동 조회 (UVIS GPS)</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>거리 및 소요 시간 자동 계산 (네이버 맵 API)</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>배차 규칙 자동 적용 (Phase 10)</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>AI 기반 최적 차량 선택</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>경로 자동 생성 및 표시</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>설명 가능한 AI (배차 이유 제공)</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default AutoDispatchPage;
