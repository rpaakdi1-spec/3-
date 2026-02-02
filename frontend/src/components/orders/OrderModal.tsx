import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import Button from '../common/Button';
import Input from '../common/Input';
import { Order } from '../../types';
import { clientsAPI, ordersAPI } from '../../services/api';

interface OrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  order?: Order | null;
}

const OrderModal: React.FC<OrderModalProps> = ({ isOpen, onClose, onSuccess, order }) => {
  // Get today's date in YYYY-MM-DD format
  const getTodayDate = () => new Date().toISOString().split('T')[0];
  
  const [formData, setFormData] = useState({
    order_number: `ORD-${Date.now()}`,
    order_date: getTodayDate(),
    temperature_zone: '',
    pickup_client_id: '',
    delivery_client_id: '',
    pickup_address: '',
    pickup_address_detail: '',
    delivery_address: '',
    delivery_address_detail: '',
    pallet_count: '',
    weight_kg: '',
    pickup_start_time: '09:00',
    pickup_end_time: '18:00',
    delivery_start_time: '09:00',
    delivery_end_time: '18:00',
    requested_delivery_date: getTodayDate(),
    priority: 5,
    notes: ''
  });

  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [useClientSelection, setUseClientSelection] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchClients();
      if (order) {
        setFormData({
          order_number: order.order_number || '',
          order_date: order.order_date ? new Date(order.order_date).toISOString().split('T')[0] : '',
          temperature_zone: order.temperature_zone || '',
          pickup_client_id: order.pickup_client_id?.toString() || '',
          delivery_client_id: order.delivery_client_id?.toString() || '',
          pickup_address: order.pickup_address || '',
          pickup_address_detail: order.pickup_address_detail || '',
          delivery_address: order.delivery_address || '',
          delivery_address_detail: order.delivery_address_detail || '',
          pallet_count: order.pallet_count?.toString() || '',
          weight_kg: order.weight_kg?.toString() || '',
          pickup_start_time: order.pickup_start_time || '',
          pickup_end_time: order.pickup_end_time || '',
          delivery_start_time: order.delivery_start_time || '',
          delivery_end_time: order.delivery_end_time || '',
          requested_delivery_date: order.requested_delivery_date ? new Date(order.requested_delivery_date).toISOString().split('T')[0] : '',
          priority: order.priority || 5,
          notes: order.notes || ''
        });
        // 거래처 ID가 있으면 거래처 선택 모드, 없으면 주소 직접 입력 모드
        setUseClientSelection(!!(order.pickup_client_id || order.delivery_client_id));
      } else {
        resetForm();
      }
    }
  }, [isOpen, order]);

  const fetchClients = async () => {
    try {
      const response = await clientsAPI.list();
      setClients(response.data.items || []);
    } catch (err) {
      console.error('Failed to fetch clients:', err);
      setClients([]);
    }
  };

  const resetForm = () => {
    const today = new Date().toISOString().split('T')[0];
    setFormData({
      order_number: `ORD-${Date.now()}`,
      order_date: today,
      temperature_zone: '',
      pickup_client_id: '',
      delivery_client_id: '',
      pickup_address: '',
      pickup_address_detail: '',
      delivery_address: '',
      delivery_address_detail: '',
      pallet_count: '',
      weight_kg: '',
      pickup_start_time: '09:00',
      pickup_end_time: '18:00',
      delivery_start_time: '09:00',
      delivery_end_time: '18:00',
      requested_delivery_date: today,
      priority: 5,
      notes: ''
    });
    setError('');
    setUseClientSelection(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate required fields
      if (!formData.order_number) {
        setError('주문번호를 입력해주세요');
        setLoading(false);
        return;
      }
      if (!formData.order_date) {
        setError('주문일자를 선택해주세요');
        setLoading(false);
        return;
      }
      if (!formData.temperature_zone) {
        setError('온도대를 선택해주세요');
        setLoading(false);
        return;
      }
      if (!formData.pallet_count || parseInt(formData.pallet_count) <= 0) {
        setError('팔레트 수량을 입력해주세요 (1개 이상)');
        setLoading(false);
        return;
      }

      // Validate: either client_id or address must be provided
      if (useClientSelection) {
        if (!formData.pickup_client_id) {
          setError('상차 거래처를 선택해주세요');
          setLoading(false);
          return;
        }
        if (!formData.delivery_client_id) {
          setError('하차 거래처를 선택해주세요');
          setLoading(false);
          return;
        }
      } else {
        if (!formData.pickup_address) {
          setError('상차 주소를 입력해주세요');
          setLoading(false);
          return;
        }
        if (!formData.delivery_address) {
          setError('하차 주소를 입력해주세요');
          setLoading(false);
          return;
        }
      }

      const payload: any = {
        order_number: formData.order_number,
        order_date: formData.order_date,
        temperature_zone: formData.temperature_zone,
        pallet_count: parseInt(formData.pallet_count),
        priority: formData.priority,
      };

      // Add optional fields
      if (formData.weight_kg) payload.weight_kg = parseFloat(formData.weight_kg);
      if (formData.pickup_start_time) payload.pickup_start_time = formData.pickup_start_time;
      if (formData.pickup_end_time) payload.pickup_end_time = formData.pickup_end_time;
      if (formData.delivery_start_time) payload.delivery_start_time = formData.delivery_start_time;
      if (formData.delivery_end_time) payload.delivery_end_time = formData.delivery_end_time;
      if (formData.requested_delivery_date) payload.requested_delivery_date = formData.requested_delivery_date;
      if (formData.notes) payload.notes = formData.notes;

      // Add client IDs or addresses
      if (useClientSelection) {
        payload.pickup_client_id = parseInt(formData.pickup_client_id);
        payload.delivery_client_id = parseInt(formData.delivery_client_id);
      } else {
        payload.pickup_address = formData.pickup_address;
        payload.pickup_address_detail = formData.pickup_address_detail;
        payload.delivery_address = formData.delivery_address;
        payload.delivery_address_detail = formData.delivery_address_detail;
      }

      // Debug log
      console.log('🚀 Submitting order:', payload);

      if (order) {
        await ordersAPI.update(order.id, payload);
      } else {
        await ordersAPI.create(payload);
      }

      // Call onSuccess callback (parent will handle modal close and refresh)
      onSuccess();
    } catch (err: any) {
      console.error('❌ Order submission error:', err);
      console.error('❌ Error response:', err.response);
      
      // Extract error message from various error formats
      let errorMessage = '주문 저장에 실패했습니다.';
      
      if (err.response?.data?.detail) {
        // FastAPI error format
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          // Pydantic validation error format
          const errors = err.response.data.detail.map((e: any) => {
            const field = Array.isArray(e.loc) ? e.loc.join('.') : e.loc;
            return `${field}: ${e.msg} (${e.type})`;
          }).join('\n');
          errorMessage = `입력 오류:\n${errors}`;
          console.error('📋 Validation errors:', err.response.data.detail);
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">
            {order ? '주문 수정' : '새 주문 등록'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* 기본 정보 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">기본 정보</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input
                label="주문번호 *"
                value={formData.order_number}
                onChange={(e) => setFormData({ ...formData, order_number: e.target.value })}
                placeholder="ORD-20260130-001"
                required
              />

              <Input
                label="주문일자 *"
                type="date"
                value={formData.order_date}
                onChange={(e) => setFormData({ ...formData, order_date: e.target.value })}
                required
              />

              <Input
                label="희망 배송일"
                type="date"
                value={formData.requested_delivery_date}
                onChange={(e) => setFormData({ ...formData, requested_delivery_date: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  온도대 *
                </label>
                <select
                  value={formData.temperature_zone}
                  onChange={(e) => setFormData({ ...formData, temperature_zone: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">선택</option>
                  <option value="냉동">냉동 (-30°C ~ -18°C)</option>
                  <option value="냉장">냉장 (0°C ~ 6°C)</option>
                  <option value="상온">상온</option>
                </select>
              </div>

              <Input
                label="팔레트 수량 *"
                type="number"
                value={formData.pallet_count}
                onChange={(e) => setFormData({ ...formData, pallet_count: e.target.value })}
                min="1"
                placeholder="20"
                required
              />

              <Input
                label="중량(kg)"
                type="number"
                value={formData.weight_kg}
                onChange={(e) => setFormData({ ...formData, weight_kg: e.target.value })}
                min="0"
                step="0.1"
                placeholder="1000"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  우선순위
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="1">최우선 (1)</option>
                  <option value="3">높음 (3)</option>
                  <option value="5">보통 (5)</option>
                  <option value="7">낮음 (7)</option>
                  <option value="10">최하 (10)</option>
                </select>
              </div>
            </div>
          </div>

          {/* 거래처/주소 선택 방식 */}
          <div className="space-y-4">
            <div className="flex items-center gap-4 border-b pb-2">
              <h3 className="text-lg font-semibold text-gray-800">상차/하차 정보</h3>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setUseClientSelection(true)}
                  className={`px-3 py-1 text-sm rounded ${
                    useClientSelection
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  거래처 선택
                </button>
                <button
                  type="button"
                  onClick={() => setUseClientSelection(false)}
                  className={`px-3 py-1 text-sm rounded ${
                    !useClientSelection
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  주소 직접 입력
                </button>
              </div>
            </div>

            {useClientSelection ? (
              /* 거래처 선택 모드 */
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    상차 거래처 *
                  </label>
                  <select
                    value={formData.pickup_client_id}
                    onChange={(e) => setFormData({ ...formData, pickup_client_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required={useClientSelection}
                  >
                    <option value="">거래처 선택</option>
                    {clients.map((client) => (
                      <option key={client.id} value={client.id}>
                        {client.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    하차 거래처 *
                  </label>
                  <select
                    value={formData.delivery_client_id}
                    onChange={(e) => setFormData({ ...formData, delivery_client_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required={useClientSelection}
                  >
                    <option value="">거래처 선택</option>
                    {clients.map((client) => (
                      <option key={client.id} value={client.id}>
                        {client.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ) : (
              /* 주소 직접 입력 모드 */
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Input
                      label="상차 주소 *"
                      value={formData.pickup_address}
                      onChange={(e) => setFormData({ ...formData, pickup_address: e.target.value })}
                      placeholder="서울시 강남구 테헤란로 427"
                      required={!useClientSelection}
                    />
                    <Input
                      label="상차 상세주소"
                      value={formData.pickup_address_detail}
                      onChange={(e) => setFormData({ ...formData, pickup_address_detail: e.target.value })}
                      placeholder="1층"
                    />
                  </div>

                  <div className="space-y-2">
                    <Input
                      label="하차 주소 *"
                      value={formData.delivery_address}
                      onChange={(e) => setFormData({ ...formData, delivery_address: e.target.value })}
                      placeholder="부산시 해운대구 센텀중앙로 48"
                      required={!useClientSelection}
                    />
                    <Input
                      label="하차 상세주소"
                      value={formData.delivery_address_detail}
                      onChange={(e) => setFormData({ ...formData, delivery_address_detail: e.target.value })}
                      placeholder="2층 창고"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 시간 정보 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">상차/하차 시간</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Input
                label="상차 시작"
                type="time"
                value={formData.pickup_start_time}
                onChange={(e) => setFormData({ ...formData, pickup_start_time: e.target.value })}
              />
              <Input
                label="상차 종료"
                type="time"
                value={formData.pickup_end_time}
                onChange={(e) => setFormData({ ...formData, pickup_end_time: e.target.value })}
              />
              <Input
                label="하차 시작"
                type="time"
                value={formData.delivery_start_time}
                onChange={(e) => setFormData({ ...formData, delivery_start_time: e.target.value })}
              />
              <Input
                label="하차 종료"
                type="time"
                value={formData.delivery_end_time}
                onChange={(e) => setFormData({ ...formData, delivery_end_time: e.target.value })}
              />
            </div>
          </div>

          {/* 특이사항 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              특이사항
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="화물 취급 시 주의사항을 입력하세요"
            />
          </div>

          {/* 버튼 */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={loading}
            >
              취소
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={loading}
            >
              {order ? '수정' : '등록'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OrderModal;
