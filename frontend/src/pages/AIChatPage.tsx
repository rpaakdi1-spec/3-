import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, CheckCircle, XCircle, Package, History, MessageSquare, Mic, MicOff } from 'lucide-react';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { toast } from 'react-hot-toast';
import apiClient from '../api/client';
import useSpeechRecognition from '../hooks/useSpeechRecognition';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  data?: any; // 추출된 주문 정보
  multipleData?: any[]; // 여러 주문 정보
  action?: 'confirm_order' | 'confirm_multiple_orders' | 'create_order' | 'update_order'; // 액션 타입
}

interface ParsedOrder {
  order_number?: string;
  order_date?: string;
  temperature_zone?: string;
  pickup_client_name?: string;
  pickup_address?: string;
  delivery_client_name?: string;
  delivery_address?: string;
  pallet_count?: number;
  weight_kg?: number;
  volume_cbm?: number;
  pickup_start_time?: string;
  pickup_end_time?: string;
  delivery_start_time?: string;
  delivery_end_time?: string;
  product_name?: string;
  notes?: string;
}

interface ChatHistory {
  id: number;
  user_message: string;
  assistant_message: string;
  intent: string;
  action?: string;
  created_at: string;
  parsed_order?: any;
  parsed_orders?: any[];
}

const AIChatPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'history'>('chat');
  const [selectedModel, setSelectedModel] = useState<'auto' | 'gpt-4' | 'gpt-3.5-turbo' | 'gemini-pro'>('gpt-4');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '안녕하세요! 😊 주문 등록/수정을 도와드리겠습니다.\n\n**단일 배송:**\n"서울에서 부산으로 냉동 10팔레트 500kg"\n\n**1:N 배송 (여러 곳으로):**\n"서울 창고에서 출발\n- 부산: 냉동 10팔레트\n- 대전: 냉동 15팔레트\n- 광주: 냉장 5팔레트"',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pendingOrder, setPendingOrder] = useState<ParsedOrder | null>(null);
  const [pendingOrders, setPendingOrders] = useState<ParsedOrder[] | null>(null); // 여러 주문
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 음성 인식
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript,
    isSupported: isSpeechSupported,
  } = useSpeechRecognition();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 히스토리 로드
  useEffect(() => {
    if (activeTab === 'history') {
      loadChatHistory();
    }
  }, [activeTab]);

  // 음성 인식 결과를 입력창에 반영
  useEffect(() => {
    if (transcript) {
      setInput(prev => prev + transcript);
      resetTranscript();
    }
  }, [transcript, resetTranscript]);

  const loadChatHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await apiClient.getChatHistory({ limit: 100 });
      setChatHistory(response.items || []);
    } catch (error) {
      console.error('히스토리 로드 실패:', error);
      toast.error('히스토리를 불러오는데 실패했습니다.');
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleVoiceInput = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try:
      // AI 채팅 API 호출 (선택된 모델 사용)
      const response = await apiClient.processChatMessage(userMessage.content, {
        pending_order: pendingOrder,
        pending_orders: pendingOrders,
        recent_messages: messages.slice(-5).map(m => ({
          role: m.role,
          content: m.content
        }))
      }, selectedModel);

      const { intent, message, parsed_order, parsed_orders, action, order_created, orders_created } = response;

      // AI 응답 메시지 추가
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: message,
        timestamp: new Date(),
        data: parsed_order,
        multipleData: parsed_orders,
        action: action,
      };

      setMessages(prev => [...prev, assistantMessage]);

      // 여러 주문 확인 대기
      if (intent === 'confirm_multiple_orders' && parsed_orders) {
        setPendingOrders(parsed_orders);
        setPendingOrder(null);
      }
      // 단일 주문 확인 대기
      else if (intent === 'confirm_order' && parsed_order) {
        setPendingOrder(parsed_order);
        setPendingOrders(null);
      }

      // 여러 주문 생성 완료
      if (intent === 'orders_created' && orders_created) {
        setPendingOrders(null);
        setPendingOrder(null);
        toast.success(`${orders_created.length}개 주문이 등록되었습니다!`);
      }

      // 단일 주문 생성 완료
      if (intent === 'order_created' && order_created) {
        setPendingOrder(null);
        setPendingOrders(null);
        toast.success(`주문 ${order_created.order_number}이(가) 등록되었습니다!`);
      }

    } catch (error: any) {
      console.error('AI 채팅 오류:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ 오류가 발생했습니다: ${error.response?.data?.detail || error.message || '알 수 없는 오류'}`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
      toast.error('메시지 전송에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleConfirmOrder = async () => {
    if (!pendingOrder && !pendingOrders) return;

    setIsLoading(true);
    const confirmMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: '네, 등록해주세요',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, confirmMessage]);

    try {
      const response = await apiClient.processChatMessage('확인', {
        pending_order: pendingOrder,
        pending_orders: pendingOrders,
        confirm: true
      }, selectedModel);

      const { message, order_created, orders_created } = response;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: message,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (orders_created) {
        setPendingOrders(null);
        setPendingOrder(null);
        toast.success(`✅ ${orders_created.length}개 주문이 등록되었습니다!`);
      } else if (order_created) {
        setPendingOrder(null);
        setPendingOrders(null);
        toast.success(`✅ 주문 ${order_created.order_number}이(가) 등록되었습니다!`);
      }

    } catch (error: any) {
      console.error('주문 확인 오류:', error);
      toast.error('주문 등록에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelOrder = () => {
    setPendingOrder(null);
    setPendingOrders(null);
    const cancelMessage: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: '주문 등록이 취소되었습니다. 다시 입력해주세요.',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, cancelMessage]);
  };

  return (
    <Layout>
      <div className="h-[calc(100vh-4rem)] flex flex-col">
        {/* 헤더 */}
        <div className="bg-white border-b px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-1.5 sm:p-2 rounded-lg">
                <Bot className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg sm:text-2xl font-bold text-gray-900">AI 주문 어시스턴트</h1>
                <p className="text-xs sm:text-sm text-gray-600 hidden sm:block">자연어로 주문을 등록하고 수정하세요</p>
              </div>
            </div>

            {/* AI 모델 선택 & 탭 */}
            <div className="flex items-center gap-2 sm:gap-3">
              {/* AI 모델 선택 */}
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value as any)}
                className="px-2 sm:px-3 py-1.5 sm:py-2 text-xs sm:text-sm border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="auto">🤖 자동</option>
                <option value="gpt-4">💎 GPT-4</option>
                <option value="gpt-3.5-turbo">⚡ GPT-3.5</option>
                <option value="gemini-pro">🌟 Gemini</option>
              </select>

              {/* 탭 */}
              <div className="flex gap-1 sm:gap-2">
              <button
                onClick={() => setActiveTab('chat')}
                className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                  activeTab === 'chat'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <MessageSquare className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden sm:inline">채팅</span>
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                  activeTab === 'history'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <History className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden sm:inline">히스토리</span>
              </button>
            </div>
            </div>
          </div>
        </div>

        {/* 콘텐츠 영역 */}
        {activeTab === 'chat' ? (
          <>{/* 채팅 메시지 영역 */}
        <div className="flex-1 overflow-y-auto bg-gray-50 p-3 sm:p-6">
          <div className="max-w-4xl mx-auto space-y-3 sm:space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-2 sm:gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                    </div>
                  </div>
                )}

                <div
                  className={`max-w-[85%] sm:max-w-2xl rounded-lg px-3 py-2 sm:px-4 sm:py-3 text-sm sm:text-base ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-900 shadow-sm border border-gray-200'
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">{message.content}</p>
                  
                  {/* 파싱된 주문 정보 표시 */}
                  {message.data && (
                    <div className="mt-2 sm:mt-3 p-2 sm:p-3 bg-gray-50 rounded border border-gray-200 text-xs sm:text-sm">
                      <div className="flex items-center gap-2 mb-2 text-gray-700 font-semibold">
                        <Package className="w-3 h-3 sm:w-4 sm:h-4" />
                        <span>추출된 주문 정보</span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 sm:gap-2 text-gray-600">
                        {message.data.temperature_zone && (
                          <div className="break-words"><span className="font-medium">온도대:</span> {message.data.temperature_zone}</div>
                        )}
                        {message.data.pickup_address && (
                          <div className="break-words"><span className="font-medium">상차지:</span> {message.data.pickup_address}</div>
                        )}
                        {message.data.delivery_address && (
                          <div className="break-words"><span className="font-medium">하차지:</span> {message.data.delivery_address}</div>
                        )}
                        {message.data.pallet_count && (
                          <div><span className="font-medium">팔레트:</span> {message.data.pallet_count}개</div>
                        )}
                        {message.data.weight_kg && (
                          <div><span className="font-medium">중량:</span> {message.data.weight_kg}kg</div>
                        )}
                        {message.data.pickup_start_time && (
                          <div className="break-words"><span className="font-medium">상차시간:</span> {message.data.pickup_start_time}</div>
                        )}
                        {message.data.delivery_start_time && (
                          <div className="break-words"><span className="font-medium">하차시간:</span> {message.data.delivery_start_time}</div>
                        )}
                      </div>
                    </div>
                  )}

                  <p className="text-[10px] sm:text-xs mt-1.5 sm:mt-2 opacity-70">
                    {message.timestamp.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-300 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-700" />
                    </div>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-2 sm:gap-3 justify-start">
                <div className="flex-shrink-0">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                  </div>
                </div>
                <div className="bg-white rounded-lg px-3 py-2 sm:px-4 sm:py-3 shadow-sm border border-gray-200">
                  <div className="flex items-center gap-2 text-gray-600 text-sm">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>AI가 생각하고 있습니다...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* 확인 대기 중인 주문 */}
        {(pendingOrder || pendingOrders) && (
          <div className="bg-yellow-50 border-t border-yellow-200 px-3 sm:px-6 py-2 sm:py-3">
            <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
              <div className="flex items-center gap-2 text-yellow-800 text-sm sm:text-base">
                <Package className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />
                <span className="font-medium">주문 확인 대기 중</span>
              </div>
              <div className="flex gap-2 w-full sm:w-auto">
                <Button
                  onClick={handleConfirmOrder}
                  disabled={isLoading}
                  className="bg-green-600 hover:bg-green-700 flex-1 sm:flex-initial text-sm sm:text-base py-2"
                  size="sm"
                >
                  <CheckCircle className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                  등록하기
                </Button>
                <Button
                  onClick={handleCancelOrder}
                  variant="secondary"
                  disabled={isLoading}
                  className="flex-1 sm:flex-initial text-sm sm:text-base py-2"
                  size="sm"
                >
                  <XCircle className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                  취소
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* 입력 영역 */}
        <div className="bg-white border-t px-3 sm:px-6 py-3 sm:py-4">
          <div className="max-w-4xl mx-auto flex gap-2 sm:gap-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="주문 정보를 입력하세요..."
                className="w-full px-3 sm:px-4 py-2 sm:py-3 pr-10 sm:pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm sm:text-base"
                rows={2}
                disabled={isLoading}
              />
              {/* 음성 입력 버튼 */}
              {isSpeechSupported && (
                <button
                  onClick={handleVoiceInput}
                  disabled={isLoading}
                  className={`absolute right-2 sm:right-3 bottom-2 sm:bottom-3 p-1.5 sm:p-2 rounded-full transition-all touch-manipulation ${
                    isListening
                      ? 'bg-red-500 text-white animate-pulse'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200 active:bg-gray-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                  title={isListening ? '음성 인식 중지' : '음성 입력'}
                >
                  {isListening ? (
                    <MicOff className="w-4 h-4 sm:w-5 sm:h-5" />
                  ) : (
                    <Mic className="w-4 h-4 sm:w-5 sm:h-5" />
                  )}
                </button>
              )}
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              className="self-end px-3 sm:px-6 py-2 sm:py-3 text-sm sm:text-base touch-manipulation"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
              ) : (
                <>
                  <Send className="w-4 h-4 sm:w-5 sm:h-5 sm:mr-2" />
                  <span className="hidden sm:inline">전송</span>
                </>
              )}
            </Button>
          </div>
        </div>
        </>
        ) : (
          /* 히스토리 뷰 */
          <div className="flex-1 overflow-y-auto bg-gray-50 p-6">
            <div className="max-w-6xl mx-auto">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">대화 히스토리</h2>
                <Button
                  onClick={loadChatHistory}
                  disabled={historyLoading}
                  variant="secondary"
                  size="sm"
                >
                  {historyLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <History className="w-4 h-4 mr-2" />
                  )}
                  새로고침
                </Button>
              </div>

              {historyLoading ? (
                <div className="flex justify-center items-center py-20">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
              ) : chatHistory.length === 0 ? (
                <div className="text-center py-20 text-gray-500">
                  <History className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>아직 대화 기록이 없습니다.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {chatHistory.map((history) => (
                    <Card key={history.id} className="p-4">
                      <div className="space-y-3">
                        {/* 사용자 메시지 */}
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                            <User className="w-5 h-5 text-gray-700" />
                          </div>
                          <div className="flex-1">
                            <p className="text-gray-900">{history.user_message}</p>
                          </div>
                        </div>

                        {/* AI 응답 */}
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                            <Bot className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex-1">
                            <p className="text-gray-900 whitespace-pre-wrap">{history.assistant_message}</p>
                            
                            {/* 파싱된 주문 정보 */}
                            {history.parsed_order && (
                              <div className="mt-2 p-3 bg-gray-50 rounded border border-gray-200 text-sm">
                                <div className="flex items-center gap-2 mb-2 text-gray-700 font-semibold">
                                  <Package className="w-4 h-4" />
                                  <span>추출된 주문 정보</span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-gray-600">
                                  {history.parsed_order.temperature_zone && (
                                    <div><span className="font-medium">온도대:</span> {history.parsed_order.temperature_zone}</div>
                                  )}
                                  {history.parsed_order.pickup_address && (
                                    <div><span className="font-medium">상차지:</span> {history.parsed_order.pickup_address}</div>
                                  )}
                                  {history.parsed_order.delivery_address && (
                                    <div><span className="font-medium">하차지:</span> {history.parsed_order.delivery_address}</div>
                                  )}
                                  {history.parsed_order.pallet_count && (
                                    <div><span className="font-medium">팔레트:</span> {history.parsed_order.pallet_count}개</div>
                                  )}
                                </div>
                              </div>
                            )}

                            {/* 다중 주문 정보 */}
                            {history.parsed_orders && history.parsed_orders.length > 0 && (
                              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200 text-sm">
                                <div className="flex items-center gap-2 mb-2 text-blue-700 font-semibold">
                                  <Package className="w-4 h-4" />
                                  <span>{history.parsed_orders.length}개의 주문</span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* 메타 정보 */}
                        <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t">
                          <div className="flex items-center gap-3">
                            {history.intent && (
                              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                                {history.intent}
                              </span>
                            )}
                            {history.action && (
                              <span className="px-2 py-1 bg-green-100 text-green-700 rounded">
                                {history.action}
                              </span>
                            )}
                          </div>
                          <span>
                            {new Date(history.created_at).toLocaleString('ko-KR')}
                          </span>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AIChatPage;
