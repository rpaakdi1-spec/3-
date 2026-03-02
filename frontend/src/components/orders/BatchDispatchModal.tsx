import React, { useState } from 'react';
import { X, FileText, MapPin, Calendar, CheckCircle2, AlertCircle } from 'lucide-react';
import Button from '../common/Button';
import Card from '../common/Card';
import toast from 'react-hot-toast';
import apiClient from '../../api/client';

interface BatchDispatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const BatchDispatchModal: React.FC<BatchDispatchModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const [dispatchText, setDispatchText] = useState('');
  const [pickupAddress, setPickupAddress] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [parsedOrders, setParsedOrders] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState(false);

  if (!isOpen) return null;

  const handleParse = async () => {
    if (!dispatchText.trim()) {
      toast.error('배차 정보를 입력해주세요');
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.post('/orders/parse-batch-dispatch', {
        text: dispatchText,
        pickup_address: pickupAddress,
        delivery_address: deliveryAddress
      });

      if (response.data.success) {
        setParsedOrders(response.data.orders);
        setShowPreview(true);
        toast.success(`${response.data.count}건의 배차 정보를 파싱했습니다`);
      }
    } catch (error: any) {
      console.error('Parse error:', error);
      toast.error(error.response?.data?.detail || '파싱 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async () => {
    if (parsedOrders.length === 0) {
      toast.error('등록할 배차가 없습니다');
      return;
    }

    setIsLoading(true);
    try {
      // 각 주문을 개별적으로 등록
      let successCount = 0;
      let failCount = 0;

      for (const order of parsedOrders) {
        try {
          await apiClient.post('/orders/', order);
          successCount++;
        } catch (error) {
          console.error('Order creation error:', error);
          failCount++;
        }
      }

      if (successCount > 0) {
        toast.success(`${successCount}건의 배차가 등록되었습니다`);
        onSuccess();
        handleClose();
      }

      if (failCount > 0) {
        toast.error(`${failCount}건의 배차 등록에 실패했습니다`);
      }
    } catch (error: any) {
      console.error('Register error:', error);
      toast.error('배차 등록 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setDispatchText('');
    setPickupAddress('');
    setDeliveryAddress('');
    setParsedOrders([]);
    setShowPreview(false);
    onClose();
  };

  const exampleText = `**2/23(월)목우촌 오후배차**
13:00 / 식육11톤(냉동)
13:30 / 식육5톤
14:30 / 육가공11톤
15:00 / 식육5톤
16:30 / 육가공11톤`;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6 pb-4 border-b">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold">배차 일괄 등록</h2>
              <p className="text-sm text-gray-600">텍스트로 여러 건의 배차를 한 번에 등록하세요</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {!showPreview ? (
          <>
            {/* Input Section */}
            <div className="space-y-4">
              {/* 예시 */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  입력 예시
                </h3>
                <pre className="text-sm text-blue-800 whitespace-pre-wrap font-mono">
                  {exampleText}
                </pre>
              </div>

              {/* 배차 정보 입력 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <FileText className="w-4 h-4 inline mr-1" />
                  배차 정보
                </label>
                <textarea
                  value={dispatchText}
                  onChange={(e) => setDispatchText(e.target.value)}
                  placeholder={exampleText}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  rows={10}
                />
              </div>

              {/* 주소 입력 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <MapPin className="w-4 h-4 inline mr-1" />
                    상차지 주소
                  </label>
                  <input
                    type="text"
                    value={pickupAddress}
                    onChange={(e) => setPickupAddress(e.target.value)}
                    placeholder="전북 김제시 금산면 용산리 9-13"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <MapPin className="w-4 h-4 inline mr-1" />
                    하차지 주소
                  </label>
                  <input
                    type="text"
                    value={deliveryAddress}
                    onChange={(e) => setDeliveryAddress(e.target.value)}
                    placeholder="경기도 안성시 양성면 양성로 376-106"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
              <Button variant="outline" onClick={handleClose}>
                취소
              </Button>
              <Button
                onClick={handleParse}
                isLoading={isLoading}
                disabled={!dispatchText.trim()}
              >
                파싱하기
              </Button>
            </div>
          </>
        ) : (
          <>
            {/* Preview Section */}
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-900 mb-2 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5" />
                  {parsedOrders.length}건의 배차 정보가 파싱되었습니다
                </h3>
                <p className="text-sm text-green-700">
                  아래 내용을 확인하고 등록 버튼을 눌러주세요
                </p>
              </div>

              {/* Orders Table */}
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">시간</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">품목</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">팔레트</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">무게</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">온도</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">주소</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {parsedOrders.map((order, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm">
                          {order.pickup_start_time?.substring(0, 5)}
                        </td>
                        <td className="px-4 py-3 text-sm font-medium">
                          {order.product_name}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {order.pallet_count}p
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {(order.weight_kg / 1000).toFixed(1)}톤
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            order.temperature_zone === 'FROZEN'
                              ? 'bg-blue-100 text-blue-700'
                              : order.temperature_zone === 'REFRIGERATED'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {order.temperature_zone === 'FROZEN' ? '냉동' : 
                             order.temperature_zone === 'REFRIGERATED' ? '냉장' : '상온'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          <div className="space-y-1">
                            <div className="flex items-start gap-1">
                              <span className="text-gray-500">↑</span>
                              <span className="line-clamp-1">{order.pickup_address}</span>
                            </div>
                            <div className="flex items-start gap-1">
                              <span className="text-gray-500">↓</span>
                              <span className="line-clamp-1">{order.delivery_address}</span>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between gap-3 mt-6 pt-4 border-t">
              <Button variant="outline" onClick={() => setShowPreview(false)}>
                뒤로
              </Button>
              <div className="flex gap-3">
                <Button variant="outline" onClick={handleClose}>
                  취소
                </Button>
                <Button
                  onClick={handleRegister}
                  isLoading={isLoading}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  {parsedOrders.length}건 등록하기
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  );
};

export default BatchDispatchModal;
