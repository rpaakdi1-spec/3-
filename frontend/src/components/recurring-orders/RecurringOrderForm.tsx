import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import type { RecurringOrderCreate, RecurringFrequency, Client } from '../../types';
import { FrequencySelector } from './FrequencySelector';
import { WeekdayPicker } from './WeekdayPicker';

interface RecurringOrderFormProps {
  initialData?: Partial<RecurringOrderCreate>;
  clients: Client[];
  onSubmit: (data: RecurringOrderCreate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export const RecurringOrderForm: React.FC<RecurringOrderFormProps> = ({
  initialData,
  clients,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  // Form state
  const [formData, setFormData] = useState<RecurringOrderCreate>({
    name: initialData?.name || '',
    frequency: initialData?.frequency || 'WEEKLY',
    start_date: initialData?.start_date || new Date().toISOString().split('T')[0],
    end_date: initialData?.end_date || '',
    weekdays: initialData?.weekdays || 31, // Default: Mon-Fri
    custom_days: initialData?.custom_days || '',
    
    order_date: initialData?.order_date || new Date().toISOString().split('T')[0],
    temperature_zone: initialData?.temperature_zone || '상온',
    
    pickup_client_id: initialData?.pickup_client_id,
    pickup_address: initialData?.pickup_address || '',
    pickup_address_detail: initialData?.pickup_address_detail || '',
    
    delivery_client_id: initialData?.delivery_client_id,
    delivery_address: initialData?.delivery_address || '',
    delivery_address_detail: initialData?.delivery_address_detail || '',
    
    pallet_count: initialData?.pallet_count || 1,
    weight_kg: initialData?.weight_kg || 0,
    volume_cbm: initialData?.volume_cbm || 0,
    product_name: initialData?.product_name || '',
    product_code: initialData?.product_code || '',
    
    pickup_start_time: initialData?.pickup_start_time || '',
    pickup_end_time: initialData?.pickup_end_time || '',
    delivery_start_time: initialData?.delivery_start_time || '',
    delivery_end_time: initialData?.delivery_end_time || '',
    
    is_active: initialData?.is_active !== undefined ? initialData.is_active : true,
  });

  const [pickupMode, setPickupMode] = useState<'client' | 'address'>(
    initialData?.pickup_client_id ? 'client' : 'address'
  );
  const [deliveryMode, setDeliveryMode] = useState<'client' | 'address'>(
    initialData?.delivery_client_id ? 'client' : 'address'
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      toast.error('정기 주문 이름을 입력해주세요');
      return;
    }

    if (formData.frequency === 'WEEKLY' && formData.weekdays === 0) {
      toast.error('최소 1개 이상의 요일을 선택해주세요');
      return;
    }

    if (formData.frequency === 'MONTHLY' || formData.frequency === 'CUSTOM') {
      if (!formData.custom_days || formData.custom_days.trim() === '') {
        toast.error('날짜를 입력해주세요 (예: [1,15,30])');
        return;
      }
    }

    if (pickupMode === 'client' && !formData.pickup_client_id) {
      toast.error('상차 거래처를 선택해주세요');
      return;
    }

    if (pickupMode === 'address' && !formData.pickup_address?.trim()) {
      toast.error('상차 주소를 입력해주세요');
      return;
    }

    if (deliveryMode === 'client' && !formData.delivery_client_id) {
      toast.error('하차 거래처를 선택해주세요');
      return;
    }

    if (deliveryMode === 'address' && !formData.delivery_address?.trim()) {
      toast.error('하차 주소를 입력해주세요');
      return;
    }

    if (formData.pallet_count < 1) {
      toast.error('팔레트 수는 최소 1개 이상이어야 합니다');
      return;
    }

    // Remove unused fields based on mode
    const submitData = { ...formData };
    if (pickupMode === 'client') {
      delete submitData.pickup_address;
      delete submitData.pickup_address_detail;
    } else {
      delete submitData.pickup_client_id;
    }

    if (deliveryMode === 'client') {
      delete submitData.delivery_address;
      delete submitData.delivery_address_detail;
    } else {
      delete submitData.delivery_client_id;
    }

    await onSubmit(submitData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 기본 정보 */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">기본 정보</h3>
        
        {/* 이름 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            정기 주문 이름 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="예: 서울-부산 매주 월수금 배송"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            required
          />
        </div>

        {/* 주기 선택 */}
        <FrequencySelector
          value={formData.frequency}
          onChange={(frequency) => setFormData({ ...formData, frequency })}
        />

        {/* 요일 선택 (WEEKLY) */}
        {formData.frequency === 'WEEKLY' && (
          <WeekdayPicker
            value={formData.weekdays}
            onChange={(weekdays) => setFormData({ ...formData, weekdays })}
          />
        )}

        {/* 날짜 배열 (MONTHLY, CUSTOM) */}
        {(formData.frequency === 'MONTHLY' || formData.frequency === 'CUSTOM') && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              날짜 배열 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.custom_days}
              onChange={(e) => setFormData({ ...formData, custom_days: e.target.value })}
              placeholder='[1,15,30] (매월 1일, 15일, 30일)'
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono"
            />
            <p className="text-xs text-gray-500 mt-1">
              JSON 배열 형식으로 입력 (예: [1,15,30])
            </p>
          </div>
        )}

        {/* 시작일/종료일 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              시작일 <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              종료일 (선택)
            </label>
            <input
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              min={formData.start_date}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* 상차 정보 */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">상차 정보</h3>
        
        <div className="flex gap-4 mb-4">
          <button
            type="button"
            onClick={() => setPickupMode('client')}
            className={`px-4 py-2 rounded-lg font-medium ${
              pickupMode === 'client'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            거래처 선택
          </button>
          <button
            type="button"
            onClick={() => setPickupMode('address')}
            className={`px-4 py-2 rounded-lg font-medium ${
              pickupMode === 'address'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            주소 직접 입력
          </button>
        </div>

        {pickupMode === 'client' ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              상차 거래처 <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.pickup_client_id || ''}
              onChange={(e) =>
                setFormData({ ...formData, pickup_client_id: Number(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            >
              <option value="">거래처 선택</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name} - {client.address}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                상차 주소 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.pickup_address}
                onChange={(e) =>
                  setFormData({ ...formData, pickup_address: e.target.value })
                }
                placeholder="서울시 강남구 테헤란로 123"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                상세 주소 (선택)
              </label>
              <input
                type="text"
                value={formData.pickup_address_detail}
                onChange={(e) =>
                  setFormData({ ...formData, pickup_address_detail: e.target.value })
                }
                placeholder="101동 203호"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </>
        )}
      </div>

      {/* 하차 정보 */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">하차 정보</h3>
        
        <div className="flex gap-4 mb-4">
          <button
            type="button"
            onClick={() => setDeliveryMode('client')}
            className={`px-4 py-2 rounded-lg font-medium ${
              deliveryMode === 'client'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            거래처 선택
          </button>
          <button
            type="button"
            onClick={() => setDeliveryMode('address')}
            className={`px-4 py-2 rounded-lg font-medium ${
              deliveryMode === 'address'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            주소 직접 입력
          </button>
        </div>

        {deliveryMode === 'client' ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              하차 거래처 <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.delivery_client_id || ''}
              onChange={(e) =>
                setFormData({ ...formData, delivery_client_id: Number(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            >
              <option value="">거래처 선택</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name} - {client.address}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                하차 주소 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.delivery_address}
                onChange={(e) =>
                  setFormData({ ...formData, delivery_address: e.target.value })
                }
                placeholder="부산시 해운대구 해운대로 456"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                상세 주소 (선택)
              </label>
              <input
                type="text"
                value={formData.delivery_address_detail}
                onChange={(e) =>
                  setFormData({ ...formData, delivery_address_detail: e.target.value })
                }
                placeholder="B동 5층"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </>
        )}
      </div>

      {/* 화물 정보 */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">화물 정보</h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              온도대 <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.temperature_zone}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  temperature_zone: e.target.value as '냉동' | '냉장' | '상온',
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="냉동">냉동</option>
              <option value="냉장">냉장</option>
              <option value="상온">상온</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              팔레트 수 <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="1"
              value={formData.pallet_count}
              onChange={(e) =>
                setFormData({ ...formData, pallet_count: Number(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              중량 (kg)
            </label>
            <input
              type="number"
              min="0"
              step="0.1"
              value={formData.weight_kg}
              onChange={(e) =>
                setFormData({ ...formData, weight_kg: Number(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              품목명
            </label>
            <input
              type="text"
              value={formData.product_name}
              onChange={(e) =>
                setFormData({ ...formData, product_name: e.target.value })
              }
              placeholder="냉동식품"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              품목코드
            </label>
            <input
              type="text"
              value={formData.product_code}
              onChange={(e) =>
                setFormData({ ...formData, product_code: e.target.value })
              }
              placeholder="PROD-001"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* 버튼 */}
      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          취소
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? '저장 중...' : initialData ? '수정' : '생성'}
        </button>
      </div>
    </form>
  );
};

export default RecurringOrderForm;
