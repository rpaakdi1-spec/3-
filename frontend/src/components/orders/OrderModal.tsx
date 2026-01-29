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
  const [formData, setFormData] = useState({
    client_id: '',
    origin: '',
    destination: '',
    cargo_type: '',
    pallet_count: '',
    temperature_min: '',
    temperature_max: '',
    pickup_time: '',
    delivery_deadline: '',
    special_requirements: '',
    priority: 'normal'
  });

  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchClients();
      if (order) {
        setFormData({
          client_id: order.client_id?.toString() || '',
          origin: order.origin || '',
          destination: order.destination || '',
          cargo_type: order.cargo_type || '',
          pallet_count: order.pallet_count?.toString() || '',
          temperature_min: order.temperature_min?.toString() || '',
          temperature_max: order.temperature_max?.toString() || '',
          pickup_time: order.pickup_time ? new Date(order.pickup_time).toISOString().slice(0, 16) : '',
          delivery_deadline: order.delivery_deadline ? new Date(order.delivery_deadline).toISOString().slice(0, 16) : '',
          special_requirements: order.special_requirements || '',
          priority: order.priority || 'normal'
        });
      } else {
        resetForm();
      }
    }
  }, [isOpen, order]);

  const fetchClients = async () => {
    try {
      const response = await clientsAPI.list();
      // Backend returns { total, items } structure
      setClients(response.data.items || []);
    } catch (err) {
      console.error('Failed to fetch clients:', err);
      setClients([]);
    }
  };

  const resetForm = () => {
    setFormData({
      client_id: '',
      origin: '',
      destination: '',
      cargo_type: '',
      pallet_count: '',
      temperature_min: '',
      temperature_max: '',
      pickup_time: '',
      delivery_deadline: '',
      special_requirements: '',
      priority: 'normal'
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = {
        ...formData,
        client_id: parseInt(formData.client_id),
        pallet_count: parseInt(formData.pallet_count),
        temperature_min: parseFloat(formData.temperature_min),
        temperature_max: parseFloat(formData.temperature_max),
        pickup_time: new Date(formData.pickup_time).toISOString(),
        delivery_deadline: new Date(formData.delivery_deadline).toISOString()
      };

      if (order) {
        await ordersAPI.update(order.id, payload);
      } else {
        await ordersAPI.create(payload);
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || '주문 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">
            {order ? '주문 수정' : '새 주문 등록'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                거래처 *
              </label>
              <select
                value={formData.client_id}
                onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
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
                우선순위
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="low">낮음</option>
                <option value="normal">보통</option>
                <option value="high">높음</option>
                <option value="urgent">긴급</option>
              </select>
            </div>

            <Input
              label="출발지 *"
              value={formData.origin}
              onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
              required
            />

            <Input
              label="도착지 *"
              value={formData.destination}
              onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                온도대 *
              </label>
              <select
                value={formData.cargo_type}
                onChange={(e) => {
                  const tempZone = e.target.value;
                  // 온도대별 기본 온도 범위 자동 입력
                  let minTemp = '';
                  let maxTemp = '';
                  
                  if (tempZone === 'FROZEN') {
                    minTemp = '-30';
                    maxTemp = '-18';
                  } else if (tempZone === 'REFRIGERATED') {
                    minTemp = '0';
                    maxTemp = '6';
                  } else if (tempZone === 'AMBIENT') {
                    minTemp = '-30';
                    maxTemp = '60';
                  }
                  
                  setFormData({ 
                    ...formData, 
                    cargo_type: tempZone,
                    temperature_min: minTemp,
                    temperature_max: maxTemp
                  });
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">온도대 선택</option>
                <option value="FROZEN">냉동 (-30°C ~ -18°C)</option>
                <option value="REFRIGERATED">냉장 (0°C ~ 6°C)</option>
                <option value="AMBIENT">상온 (-30°C ~ 60°C)</option>
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

            <div>
              <Input
                label="최저 온도(°C) *"
                type="number"
                value={formData.temperature_min}
                onChange={(e) => setFormData({ ...formData, temperature_min: e.target.value })}
                step="0.1"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                온도대 선택 시 자동 입력됩니다. 수정 가능합니다.
              </p>
            </div>

            <div>
              <Input
                label="최고 온도(°C) *"
                type="number"
                value={formData.temperature_max}
                onChange={(e) => setFormData({ ...formData, temperature_max: e.target.value })}
                step="0.1"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                온도대 선택 시 자동 입력됩니다. 수정 가능합니다.
              </p>
            </div>

            <Input
              label="픽업 시간 *"
              type="datetime-local"
              value={formData.pickup_time}
              onChange={(e) => setFormData({ ...formData, pickup_time: e.target.value })}
              required
            />

            <Input
              label="배송 마감 시간 *"
              type="datetime-local"
              value={formData.delivery_deadline}
              onChange={(e) => setFormData({ ...formData, delivery_deadline: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              특이사항
            </label>
            <textarea
              value={formData.special_requirements}
              onChange={(e) => setFormData({ ...formData, special_requirements: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="화물 취급 시 주의사항을 입력하세요"
            />
          </div>

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
