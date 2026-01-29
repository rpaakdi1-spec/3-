import React, { useState, useCallback } from 'react';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { Order, Vehicle } from '../../types';
import apiClient from '../../api/client';
import toast from 'react-hot-toast';
import { Truck, Zap } from 'lucide-react';

interface DispatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  order: Order;
  vehicles: Vehicle[];
}

const DispatchModal: React.FC<DispatchModalProps> = React.memo(({
  isOpen,
  onClose,
  onSuccess,
  order,
  vehicles,
}) => {
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'auto' | 'manual'>('auto');
  const [selectedVehicle, setSelectedVehicle] = useState<number | null>(null);
  const [selectedDriver, setSelectedDriver] = useState<number | null>(null);

  const handleAutoDispatch = useCallback(async () => {
    setLoading(true);
    try {
      await apiClient.autoDispatch(order.id);
      toast.success('자동 배차가 완료되었습니다');
      onSuccess();
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '자동 배차에 실패했습니다');
    } finally {
      setLoading(false);
    }
  }, [order.id, onSuccess, onClose]);

  const handleManualDispatch = useCallback(async () => {
    if (!selectedVehicle || !selectedDriver) {
      toast.error('차량과 기사를 선택해주세요');
      return;
    }

    setLoading(true);
    try {
      await apiClient.manualDispatch({
        order_id: order.id,
        vehicle_id: selectedVehicle,
        driver_id: selectedDriver,
      });
      toast.success('수동 배차가 완료되었습니다');
      onSuccess();
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '수동 배차에 실패했습니다');
    } finally {
      setLoading(false);
    }
  }, [order.id, selectedVehicle, selectedDriver, onSuccess, onClose]);

  const availableVehicles = vehicles.filter(
    v => v.status === 'AVAILABLE' && v.is_active
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="배차 등록"
      size="lg"
    >
      <div className="space-y-6">
        {/* Order Info */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">주문 정보</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-600">주문번호:</span>
              <span className="ml-2 font-medium">{order.order_number}</span>
            </div>
            <div>
              <span className="text-gray-600">거래처:</span>
              <span className="ml-2 font-medium">{order.client_name}</span>
            </div>
            <div className="col-span-2">
              <span className="text-gray-600">상차지:</span>
              <span className="ml-2">{order.pickup_address}</span>
            </div>
            <div className="col-span-2">
              <span className="text-gray-600">하차지:</span>
              <span className="ml-2">{order.delivery_address}</span>
            </div>
            <div>
              <span className="text-gray-600">화물:</span>
              <span className="ml-2">{order.cargo_type === 'FROZEN' ? '냉동' : '냉장'}</span>
            </div>
            <div>
              <span className="text-gray-600">무게:</span>
              <span className="ml-2">{order.weight_kg}kg</span>
            </div>
          </div>
        </div>

        {/* Mode Selection */}
        <div className="flex space-x-4">
          <button
            onClick={() => setMode('auto')}
            className={`flex-1 p-4 rounded-lg border-2 transition-all ${
              mode === 'auto'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Zap className={`mx-auto mb-2 ${mode === 'auto' ? 'text-blue-600' : 'text-gray-400'}`} size={32} />
            <h5 className="font-semibold text-gray-900">자동 배차</h5>
            <p className="text-sm text-gray-600 mt-1">AI가 최적의 차량을 자동으로 선택합니다</p>
          </button>
          <button
            onClick={() => setMode('manual')}
            className={`flex-1 p-4 rounded-lg border-2 transition-all ${
              mode === 'manual'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Truck className={`mx-auto mb-2 ${mode === 'manual' ? 'text-blue-600' : 'text-gray-400'}`} size={32} />
            <h5 className="font-semibold text-gray-900">수동 배차</h5>
            <p className="text-sm text-gray-600 mt-1">직접 차량과 기사를 선택합니다</p>
          </button>
        </div>

        {/* Manual Dispatch Options */}
        {mode === 'manual' && (
          <div className="space-y-4">
            {/* Vehicle Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                차량 선택 <span className="text-red-500">*</span>
              </label>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {availableVehicles.length === 0 ? (
                  <p className="text-center text-gray-500 py-4">가용한 차량이 없습니다</p>
                ) : (
                  availableVehicles.map((vehicle) => (
                    <button
                      key={vehicle.id}
                      onClick={() => setSelectedVehicle(vehicle.id)}
                      className={`w-full p-3 text-left rounded-lg border-2 transition-all ${
                        selectedVehicle === vehicle.id
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-semibold">{vehicle.license_plate}</p>
                          <p className="text-sm text-gray-600">
                            {vehicle.vehicle_type} • {vehicle.capacity_ton}톤
                          </p>
                        </div>
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                          가용
                        </span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Driver Selection (Mock) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                기사 선택 <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedDriver || ''}
                onChange={(e) => setSelectedDriver(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">기사 선택</option>
                <option value="1">김철수 (010-1234-5678)</option>
                <option value="2">이영희 (010-2345-6789)</option>
                <option value="3">박민수 (010-3456-7890)</option>
              </select>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" onClick={onClose} type="button">
            취소
          </Button>
          <Button
            variant="primary"
            onClick={mode === 'auto' ? handleAutoDispatch : handleManualDispatch}
            isLoading={loading}
            disabled={mode === 'manual' && (!selectedVehicle || !selectedDriver)}
          >
            {mode === 'auto' ? '자동 배차' : '수동 배차'}
          </Button>
        </div>
      </div>
    </Modal>
  );
});

DispatchModal.displayName = 'DispatchModal';

export default DispatchModal;
