import React, { useState } from 'react';
import Layout from '../components/common/Layout';
import {
import Layout from '../components/common/Layout';
  Calculator,
  DollarSign,
  TrendingUp,
  MapPin,
  Package,
  Weight,
  Clock,
  Thermometer,
  AlertCircle,
  CheckCircle,
  Calendar,
  Truck
} from 'lucide-react';
import * as BillingEnhancedAPI from '../api/billing-enhanced';

interface ChargePreviewRequest {
  client_id: number;
  distance_km: number;
  total_pallets: number;
  total_weight_kg: number;
  is_weekend: boolean;
  is_urgent: boolean;
  requires_temperature_control: boolean;
  dispatch_date: string;
}

interface ChargeBreakdown {
  base_amount: number;
  surcharge_amount: number;
  discount_amount: number;
  total_amount: number;
  details: {
    distance_charge: number;
    pallet_charge: number;
    weight_charge: number;
    weekend_surcharge: number;
    urgent_surcharge: number;
    temperature_surcharge: number;
    volume_discount: number;
  };
}

const ChargePreviewPage: React.FC = () => {
  const [formData, setFormData] = useState<ChargePreviewRequest>({
    client_id: 0,
    distance_km: 0,
    total_pallets: 0,
    total_weight_kg: 0,
    is_weekend: false,
    is_urgent: false,
    requires_temperature_control: false,
    dispatch_date: new Date().toISOString().split('T')[0]
  });

  const [preview, setPreview] = useState<ChargeBreakdown | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof ChargePreviewRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Reset preview when inputs change
    setPreview(null);
  };

  const handlePreview = async () => {
    // Validation
    if (formData.client_id <= 0) {
      setError('거래처를 선택해주세요.');
      return;
    }
    if (formData.distance_km <= 0) {
      setError('거리를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await BillingEnhancedAPI.previewCharge(formData);
      setPreview(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || '요금 계산에 실패했습니다.');
      setPreview(null);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">실시간 요금 계산기</h1>
          <p className="text-gray-600">배차 정보를 입력하면 예상 요금을 즉시 확인할 수 있습니다</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Form */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Calculator className="w-5 h-5 text-blue-500" />
              배차 정보 입력
            </h2>

            <div className="space-y-4">
              {/* Client ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  거래처 ID *
                </label>
                <input
                  type="number"
                  value={formData.client_id || ''}
                  onChange={(e) => handleInputChange('client_id', parseInt(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="거래처 ID를 입력하세요"
                />
              </div>

              {/* Distance */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  운행 거리 (km) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.distance_km || ''}
                  onChange={(e) => handleInputChange('distance_km', parseFloat(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="예: 45.5"
                />
              </div>

              {/* Pallets */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <Package className="w-4 h-4" />
                  팔레트 수
                </label>
                <input
                  type="number"
                  value={formData.total_pallets || ''}
                  onChange={(e) => handleInputChange('total_pallets', parseInt(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="예: 10"
                />
              </div>

              {/* Weight */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <Weight className="w-4 h-4" />
                  총 중량 (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.total_weight_kg || ''}
                  onChange={(e) => handleInputChange('total_weight_kg', parseFloat(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="예: 1500"
                />
              </div>

              {/* Dispatch Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  배차 날짜
                </label>
                <input
                  type="date"
                  value={formData.dispatch_date}
                  onChange={(e) => handleInputChange('dispatch_date', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Checkboxes */}
              <div className="space-y-3 pt-2">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_weekend}
                    onChange={(e) => handleInputChange('is_weekend', e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-orange-500" />
                    주말 배차 (할증 적용)
                  </span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_urgent}
                    onChange={(e) => handleInputChange('is_urgent', e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-500" />
                    긴급 배송 (할증 적용)
                  </span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.requires_temperature_control}
                    onChange={(e) => handleInputChange('requires_temperature_control', e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 flex items-center gap-2">
                    <Thermometer className="w-4 h-4 text-blue-500" />
                    온도 관리 필요 (냉장/냉동)
                  </span>
                </label>
              </div>

              {/* Calculate Button */}
              <button
                onClick={handlePreview}
                disabled={loading}
                className="w-full mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2 font-medium"
              >
                <Calculator className={`w-5 h-5 ${loading ? 'animate-pulse' : ''}`} />
                {loading ? '계산 중...' : '요금 계산하기'}
              </button>
            </div>
          </div>

          {/* Preview Result */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-500" />
              예상 요금
            </h2>

            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-800">오류</p>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            )}

            {!preview && !error && (
              <div className="text-center py-12">
                <Calculator className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">배차 정보를 입력하고</p>
                <p className="text-gray-500">'요금 계산하기'를 클릭하세요</p>
              </div>
            )}

            {preview && (
              <div className="space-y-4">
                {/* Total Amount - Big Display */}
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white text-center">
                  <p className="text-sm font-medium mb-2">총 예상 요금</p>
                  <p className="text-4xl font-bold">{formatCurrency(preview.total_amount)}</p>
                </div>

                {/* Base Charges */}
                <div className="border-t border-gray-200 pt-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">기본 요금</h3>
                  <div className="space-y-2">
                    {preview.details.distance_charge > 0 && (
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600 flex items-center gap-2">
                          <MapPin className="w-4 h-4" />
                          거리 요금 ({formData.distance_km}km)
                        </span>
                        <span className="font-medium text-gray-900">
                          {formatCurrency(preview.details.distance_charge)}
                        </span>
                      </div>
                    )}

                    {preview.details.pallet_charge > 0 && (
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600 flex items-center gap-2">
                          <Package className="w-4 h-4" />
                          팔레트 요금 ({formData.total_pallets}개)
                        </span>
                        <span className="font-medium text-gray-900">
                          {formatCurrency(preview.details.pallet_charge)}
                        </span>
                      </div>
                    )}

                    {preview.details.weight_charge > 0 && (
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600 flex items-center gap-2">
                          <Weight className="w-4 h-4" />
                          중량 요금 ({formData.total_weight_kg}kg)
                        </span>
                        <span className="font-medium text-gray-900">
                          {formatCurrency(preview.details.weight_charge)}
                        </span>
                      </div>
                    )}

                    <div className="flex justify-between items-center text-sm pt-2 border-t border-gray-100">
                      <span className="font-medium text-gray-700">기본 요금 합계</span>
                      <span className="font-semibold text-gray-900">
                        {formatCurrency(preview.base_amount)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Surcharges */}
                {preview.surcharge_amount > 0 && (
                  <div className="border-t border-gray-200 pt-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">할증 요금</h3>
                    <div className="space-y-2">
                      {preview.details.weekend_surcharge > 0 && (
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-600 flex items-center gap-2">
                            <Clock className="w-4 h-4 text-orange-500" />
                            주말 할증
                          </span>
                          <span className="font-medium text-orange-600">
                            +{formatCurrency(preview.details.weekend_surcharge)}
                          </span>
                        </div>
                      )}

                      {preview.details.urgent_surcharge > 0 && (
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-600 flex items-center gap-2">
                            <AlertCircle className="w-4 h-4 text-red-500" />
                            긴급 할증
                          </span>
                          <span className="font-medium text-red-600">
                            +{formatCurrency(preview.details.urgent_surcharge)}
                          </span>
                        </div>
                      )}

                      {preview.details.temperature_surcharge > 0 && (
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-600 flex items-center gap-2">
                            <Thermometer className="w-4 h-4 text-blue-500" />
                            온도 관리 할증
                          </span>
                          <span className="font-medium text-blue-600">
                            +{formatCurrency(preview.details.temperature_surcharge)}
                          </span>
                        </div>
                      )}

                      <div className="flex justify-between items-center text-sm pt-2 border-t border-gray-100">
                        <span className="font-medium text-gray-700">할증 합계</span>
                        <span className="font-semibold text-orange-600">
                          +{formatCurrency(preview.surcharge_amount)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Discounts */}
                {preview.discount_amount > 0 && (
                  <div className="border-t border-gray-200 pt-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">할인</h3>
                    <div className="space-y-2">
                      {preview.details.volume_discount > 0 && (
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-600 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-green-500" />
                            물량 할인
                          </span>
                          <span className="font-medium text-green-600">
                            -{formatCurrency(preview.details.volume_discount)}
                          </span>
                        </div>
                      )}

                      <div className="flex justify-between items-center text-sm pt-2 border-t border-gray-100">
                        <span className="font-medium text-gray-700">할인 합계</span>
                        <span className="font-semibold text-green-600">
                          -{formatCurrency(preview.discount_amount)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Success Message */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-green-800">계산 완료</p>
                    <p className="text-sm text-green-700 mt-1">
                      위 금액은 예상 요금이며, 실제 청구 시 정책에 따라 변동될 수 있습니다.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <MapPin className="w-5 h-5 text-blue-500" />
              <h3 className="font-medium text-blue-900">거리 기반 요금</h3>
            </div>
            <p className="text-sm text-blue-700">
              운행 거리에 따라 km당 요금이 적용됩니다. 거래처별로 다른 요율이 설정될 수 있습니다.
            </p>
          </div>

          <div className="bg-orange-50 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-orange-500" />
              <h3 className="font-medium text-orange-900">할증 요금</h3>
            </div>
            <p className="text-sm text-orange-700">
              주말, 긴급 배송, 온도 관리 등 특수 조건에 따라 추가 할증이 적용됩니다.
            </p>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              <h3 className="font-medium text-green-900">물량 할인</h3>
            </div>
            <p className="text-sm text-green-700">
              월간 배차 건수가 일정 기준을 초과하면 자동으로 물량 할인이 적용됩니다.
            </p>
          </div>
        </div>
      </div>
    </div>
    </Layout>
  );
};

export default ChargePreviewPage;
