import React, { useState } from 'react';
import { FiUpload, FiX, FiCheck, FiAlertCircle, FiCopy, FiTrash2 } from 'react-icons/fi';
import { ordersAPI } from '../services/api';

interface ParsedOrder {
  order_date: string;
  pickup_client?: string;
  pickup_address?: string;
  delivery_client?: string;
  delivery_address?: string;
  temperature_zone?: string;
  pallet_count?: number;
  weight_kg?: number;
  product_name?: string;
  pickup_start_time?: string;
  pickup_end_time?: string;
  delivery_start_time?: string;
  delivery_end_time?: string;
  notes?: string;
  confidence_score?: number;
  matched_pickup_client_id?: number;
  matched_delivery_client_id?: number;
}

interface ParseResult {
  success: boolean;
  orders?: ParsedOrder[];
  error?: string;
}

const OrderNLPParser: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [selectedOrders, setSelectedOrders] = useState<Set<number>>(new Set());

  const handleParse = async () => {
    if (!inputText.trim()) {
      alert('주문 텍스트를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await ordersAPI.parseNLP(inputText);
      setParseResult(response.data);
    } catch (error: any) {
      console.error('NLP 파싱 실패:', error);
      setParseResult({
        success: false,
        error: error.response?.data?.detail || '파싱 중 오류가 발생했습니다.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setInputText('');
    setParseResult(null);
    setSelectedOrders(new Set());
  };

  const handleToggleSelect = (index: number) => {
    const newSelected = new Set(selectedOrders);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedOrders(newSelected);
  };

  const handleSelectAll = () => {
    if (parseResult?.orders) {
      if (selectedOrders.size === parseResult.orders.length) {
        setSelectedOrders(new Set());
      } else {
        setSelectedOrders(new Set(parseResult.orders.map((_, idx) => idx)));
      }
    }
  };

  const handleCreateOrders = async () => {
    if (!parseResult?.orders || selectedOrders.size === 0) {
      alert('생성할 주문을 선택해주세요.');
      return;
    }

    const ordersToCreate = parseResult.orders.filter((_, idx) => selectedOrders.has(idx));
    
    try {
      setIsLoading(true);
      const results = await Promise.all(
        ordersToCreate.map(order => ordersAPI.create(order))
      );
      
      alert(`${results.length}개의 주문이 생성되었습니다.`);
      handleReset();
      // Optionally refresh parent component or navigate
      window.location.href = '/orders';
    } catch (error: any) {
      console.error('주문 생성 실패:', error);
      alert('주문 생성 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const getConfidenceColor = (score?: number) => {
    if (!score) return 'text-gray-500';
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceBadge = (score?: number) => {
    if (!score) return { label: '미확인', color: 'bg-gray-100 text-gray-600' };
    if (score >= 0.9) return { label: '높음', color: 'bg-green-100 text-green-700' };
    if (score >= 0.7) return { label: '보통', color: 'bg-yellow-100 text-yellow-700' };
    return { label: '낮음', color: 'bg-red-100 text-red-700' };
  };

  const formatTemperatureZone = (zone?: string) => {
    const zoneMap: Record<string, string> = {
      'FROZEN': '냉동',
      'REFRIGERATED': '냉장',
      'AMBIENT': '상온'
    };
    return zone ? zoneMap[zone] || zone : '-';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-2">📝 자연어 주문 입력</h2>
        <p className="text-gray-600">
          거래처에서 받은 주문을 그대로 입력하면 자동으로 파싱합니다.
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <label className="block mb-2 font-semibold">주문 텍스트 입력</label>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={`예시 1:
[02/03] 추가 배차요청
백암 _ 저온 → 경산 16판 1대

예시 2:
**2/3(화)목우촌 오후배차**
15:30 / 육가공5톤
16:30 / 육가공11톤

예시 3:
동이천센터 → 양산 16판 1대`}
          className="w-full h-48 p-3 border rounded-md focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        
        <div className="flex gap-3 mt-4">
          <button
            onClick={handleParse}
            disabled={isLoading || !inputText.trim()}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                파싱 중...
              </>
            ) : (
              <>
                <FiUpload />
                파싱 시작
              </>
            )}
          </button>
          
          <button
            onClick={handleReset}
            disabled={isLoading}
            className="flex items-center gap-2 px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:cursor-not-allowed"
          >
            <FiX />
            초기화
          </button>
        </div>
      </div>

      {/* Parse Results */}
      {parseResult && (
        <div className="bg-white p-6 rounded-lg shadow">
          {parseResult.success && parseResult.orders ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <FiCheck className="text-green-600" />
                  파싱 결과: {parseResult.orders.length}개 주문
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={handleSelectAll}
                    className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                  >
                    {selectedOrders.size === parseResult.orders.length ? '전체 해제' : '전체 선택'}
                  </button>
                  <button
                    onClick={handleCreateOrders}
                    disabled={selectedOrders.size === 0 || isLoading}
                    className="px-4 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <FiCheck />
                    선택한 주문 생성 ({selectedOrders.size})
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {parseResult.orders.map((order, idx) => {
                  const confidenceBadge = getConfidenceBadge(order.confidence_score);
                  const isSelected = selectedOrders.has(idx);

                  return (
                    <div
                      key={idx}
                      className={`border rounded-lg p-4 ${
                        isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => handleToggleSelect(idx)}
                            className="w-5 h-5 cursor-pointer"
                          />
                          <h4 className="font-bold text-lg">주문 #{idx + 1}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${confidenceBadge.color}`}>
                            신뢰도: {confidenceBadge.label} {order.confidence_score ? `(${(order.confidence_score * 100).toFixed(0)}%)` : ''}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-semibold text-gray-600">주문일자:</span>
                          <span className="ml-2">{order.order_date || '-'}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-600">온도대:</span>
                          <span className="ml-2">{formatTemperatureZone(order.temperature_zone)}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-600">상차지:</span>
                          <span className="ml-2">{order.pickup_client || order.pickup_address || '-'}</span>
                          {order.matched_pickup_client_id && (
                            <span className="ml-1 text-xs text-green-600">(매칭됨)</span>
                          )}
                        </div>
                        <div>
                          <span className="font-semibold text-gray-600">하차지:</span>
                          <span className="ml-2">{order.delivery_client || order.delivery_address || '-'}</span>
                          {order.matched_delivery_client_id && (
                            <span className="ml-1 text-xs text-green-600">(매칭됨)</span>
                          )}
                        </div>
                        <div>
                          <span className="font-semibold text-gray-600">팔레트:</span>
                          <span className="ml-2">{order.pallet_count || '-'}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-600">중량:</span>
                          <span className="ml-2">{order.weight_kg ? `${order.weight_kg}kg` : '-'}</span>
                        </div>
                        {order.pickup_start_time && (
                          <div>
                            <span className="font-semibold text-gray-600">상차시간:</span>
                            <span className="ml-2">{order.pickup_start_time} ~ {order.pickup_end_time || '-'}</span>
                          </div>
                        )}
                        {order.delivery_start_time && (
                          <div>
                            <span className="font-semibold text-gray-600">하차시간:</span>
                            <span className="ml-2">{order.delivery_start_time} ~ {order.delivery_end_time || '-'}</span>
                          </div>
                        )}
                        {order.product_name && (
                          <div className="col-span-2">
                            <span className="font-semibold text-gray-600">상품명:</span>
                            <span className="ml-2">{order.product_name}</span>
                          </div>
                        )}
                        {order.notes && (
                          <div className="col-span-2">
                            <span className="font-semibold text-gray-600">메모:</span>
                            <span className="ml-2 text-gray-600">{order.notes}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-md">
              <FiAlertCircle className="text-red-600 text-xl" />
              <div>
                <p className="font-semibold text-red-800">파싱 실패</p>
                <p className="text-sm text-red-600">{parseResult.error || '알 수 없는 오류가 발생했습니다.'}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Usage Guide */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <h4 className="font-semibold mb-2 text-blue-900">💡 사용 가이드</h4>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>거래처에서 받은 주문 텍스트를 그대로 복사해서 붙여넣으세요</li>
          <li>날짜, 거래처명, 온도대, 팔레트 수 등이 자동으로 인식됩니다</li>
          <li>여러 주문을 한 번에 입력할 수 있습니다</li>
          <li>파싱 결과를 확인하고 수정이 필요한 경우 주문 생성 후 수정하세요</li>
          <li>신뢰도가 낮은 경우(70% 이하) 반드시 확인 후 생성하세요</li>
        </ul>
      </div>
    </div>
  );
};

export default OrderNLPParser;
