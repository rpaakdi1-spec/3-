import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { ordersAPI } from '../../services/api';

interface VoiceOrderInputProps {
  onOrderCreated?: () => void;
}

export const VoiceOrderInput: React.FC<VoiceOrderInputProps> = ({ onOrderCreated }) => {
  const {
    isListening,
    transcript,
    interimTranscript,
    startListening,
    stopListening,
    resetTranscript,
    isSupported,
    error: speechError,
  } = useSpeechRecognition();

  const [isProcessing, setIsProcessing] = useState(false);

  const handleStartListening = () => {
    resetTranscript();
    startListening();
    toast.success('음성 인식을 시작합니다. 주문 정보를 말씀해주세요.');
  };

  const handleStopListening = () => {
    stopListening();
    toast.success('음성 인식이 중지되었습니다.');
  };

  const handleParseAndCreate = async () => {
    if (!transcript.trim()) {
      toast.error('음성으로 입력된 내용이 없습니다.');
      return;
    }

    setIsProcessing(true);
    try {
      // 1. NLP 파싱
      const parseResponse = await ordersAPI.parseNLP(transcript);
      
      if (!parseResponse.orders || parseResponse.orders.length === 0) {
        toast.error('주문 정보를 인식할 수 없습니다. 다시 시도해주세요.');
        return;
      }

      const parsedOrder = parseResponse.orders[0];

      // 2. 주문 생성
      const timestamp = Date.now();
      const orderNumber = `VOICE-${timestamp}`;
      
      const orderData = {
        order_number: orderNumber,
        order_date: new Date().toISOString().split('T')[0],
        temperature_zone: parsedOrder.temperature_zone || 'AMBIENT',
        pickup_address: parsedOrder.pickup_address || '',
        delivery_address: parsedOrder.delivery_address || '',
        pallet_count: parsedOrder.pallet_count || 1,
        weight_kg: parsedOrder.weight_kg || 0,
        volume_cbm: 0,
      };

      const createdOrder = await ordersAPI.create(orderData);

      toast.success(`음성 주문이 생성되었습니다! (${orderNumber})`);
      
      // 초기화
      resetTranscript();
      
      if (onOrderCreated) {
        onOrderCreated();
      }

    } catch (error: any) {
      console.error('Voice order creation failed:', error);
      toast.error(error.response?.data?.detail || '주문 생성에 실패했습니다.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <svg
          className="mx-auto h-12 w-12 text-yellow-400 mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h3 className="text-lg font-medium text-yellow-900 mb-2">
          음성 인식을 사용할 수 없습니다
        </h3>
        <p className="text-sm text-yellow-700">
          Chrome 브라우저를 사용하시거나, HTTPS 환경에서 접속해주세요.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-100 rounded-lg">
            <svg
              className="w-6 h-6 text-indigo-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">음성 주문 입력</h2>
            <p className="text-sm text-gray-500">말로 주문 정보를 입력하세요</p>
          </div>
        </div>

        {/* Status Badge */}
        {isListening && (
          <span className="flex items-center gap-2 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium animate-pulse">
            <span className="w-2 h-2 bg-red-500 rounded-full"></span>
            녹음 중...
          </span>
        )}
      </div>

      {/* Transcript Display */}
      <div className="mb-6">
        <div className="min-h-[120px] p-4 bg-gray-50 border border-gray-200 rounded-lg">
          {transcript || interimTranscript ? (
            <div className="text-gray-900">
              <p className="whitespace-pre-wrap">{transcript}</p>
              {interimTranscript && (
                <p className="text-gray-400 italic">{interimTranscript}</p>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">
              {isListening
                ? '음성을 인식하고 있습니다...'
                : '마이크 버튼을 눌러 주문 정보를 말씀해주세요'}
            </p>
          )}
        </div>

        {speechError && (
          <div className="mt-2 text-sm text-red-600">
            ⚠️ {speechError}
          </div>
        )}
      </div>

      {/* Example */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 mb-2">💡 예시</h4>
        <p className="text-sm text-blue-700">
          "2월 10일 배차요청, 동이천에서 호남으로, 16판 1대, 상온"
        </p>
        <p className="text-sm text-blue-700 mt-1">
          "내일 냉장 20팔레트, 서울시 강남구에서 부산시 해운대구로"
        </p>
      </div>

      {/* Controls */}
      <div className="flex gap-3">
        {!isListening ? (
          <button
            onClick={handleStartListening}
            disabled={isProcessing}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
            음성 입력 시작
          </button>
        ) : (
          <button
            onClick={handleStopListening}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
              />
            </svg>
            중지
          </button>
        )}

        <button
          onClick={handleParseAndCreate}
          disabled={!transcript.trim() || isProcessing || isListening}
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isProcessing ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              처리 중...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              주문 생성
            </>
          )}
        </button>

        <button
          onClick={resetTranscript}
          disabled={isProcessing || isListening}
          className="px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="초기화"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>
      </div>

      {/* Info */}
      <div className="mt-4 text-xs text-gray-500 text-center">
        🎤 마이크 권한이 필요합니다. 브라우저에서 마이크 사용을 허용해주세요.
      </div>
    </div>
  );
};

export default VoiceOrderInput;
