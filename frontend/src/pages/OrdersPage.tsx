import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import OrderModal from '../components/orders/OrderModal';
import BatchDispatchModal from '../components/orders/BatchDispatchModal';
import apiClient from '../api/client';
import { Order } from '../types';
import { Package, Plus, Search, Filter, Upload, Download, Trash2, Edit2, FileSpreadsheet, Zap, Calendar, Clock, MessageSquare, Mic, Send, Bot, User, Loader2, CheckCircle, XCircle, History, MicOff } from 'lucide-react';
import toast from 'react-hot-toast';
import { useResponsive } from '../hooks/useResponsive';
import { MobileOrderCard } from '../components/mobile/MobileOrderCard';
import useSpeechRecognition from '../hooks/useSpeechRecognition';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  data?: any;
  multipleData?: any[];
  action?: 'confirm_order' | 'confirm_multiple_orders' | 'create_order' | 'update_order';
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

// AI Assistant Component
const AIAssistantContent: React.FC<{
  messages: Message[];
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  pendingOrder: ParsedOrder | null;
  pendingOrders: ParsedOrder[] | null;
  selectedModel: string;
  setSelectedModel: (value: any) => void;
  handleSendMessage: () => void;
  handleKeyPress: (e: React.KeyboardEvent) => void;
  handleConfirmOrder: () => void;
  handleCancelOrder: () => void;
  handleVoiceInput: () => void;
  isListening: boolean;
  isSpeechSupported: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}> = ({
  messages,
  input,
  setInput,
  isLoading,
  pendingOrder,
  pendingOrders,
  selectedModel,
  setSelectedModel,
  handleSendMessage,
  handleKeyPress,
  handleConfirmOrder,
  handleCancelOrder,
  handleVoiceInput,
  isListening,
  isSpeechSupported,
  messagesEndRef,
}) => {
  return (
    <div className="h-[calc(100vh-16rem)] flex flex-col">
      {/* AI 모델 선택 */}
      <Card className="mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-purple-600" />
            <span className="font-medium">AI 모델 선택:</span>
          </div>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value as any)}
            className="px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="auto">🤖 자동</option>
            <option value="gpt-4">💎 GPT-4</option>
            <option value="gpt-3.5-turbo">⚡ GPT-3.5</option>
            <option value="gemini-pro">🌟 Gemini</option>
          </select>
        </div>
      </Card>

      {/* 채팅 메시지 영역 */}
      <div className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                </div>
              )}

              <div
                className={`max-w-2xl rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-purple-600 text-white'
                    : 'bg-white text-gray-900 shadow-sm border border-gray-200'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                
                {/* 파싱된 주문 정보 표시 */}
                {message.data && (
                  <div className="mt-3 p-3 bg-gray-50 rounded border border-gray-200 text-sm">
                    <div className="flex items-center gap-2 mb-2 text-gray-700 font-semibold">
                      <Package className="w-4 h-4" />
                      <span>추출된 주문 정보</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-gray-600">
                      {message.data.temperature_zone && (
                        <div><span className="font-medium">온도대:</span> {message.data.temperature_zone}</div>
                      )}
                      {message.data.pickup_address && (
                        <div><span className="font-medium">상차지:</span> {message.data.pickup_address}</div>
                      )}
                      {message.data.delivery_address && (
                        <div><span className="font-medium">하차지:</span> {message.data.delivery_address}</div>
                      )}
                      {message.data.pallet_count && (
                        <div><span className="font-medium">팔레트:</span> {message.data.pallet_count}개</div>
                      )}
                      {message.data.weight_kg && (
                        <div><span className="font-medium">중량:</span> {message.data.weight_kg}kg</div>
                      )}
                      {message.data.pickup_start_time && (
                        <div><span className="font-medium">상차시간:</span> {message.data.pickup_start_time}</div>
                      )}
                      {message.data.delivery_start_time && (
                        <div><span className="font-medium">하차시간:</span> {message.data.delivery_start_time}</div>
                      )}
                    </div>
                  </div>
                )}

                <p className="text-xs mt-2 opacity-70">
                  {message.timestamp.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-gray-700" />
                  </div>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="bg-white rounded-lg px-4 py-3 shadow-sm border border-gray-200">
                <div className="flex items-center gap-2 text-gray-600">
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
        <div className="bg-yellow-50 border-t border-yellow-200 px-6 py-3 mt-4 rounded-lg">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2 text-yellow-800">
              <Package className="w-5 h-5" />
              <span className="font-medium">주문 확인 대기 중</span>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleConfirmOrder}
                disabled={isLoading}
                className="bg-green-600 hover:bg-green-700"
                size="sm"
              >
                <CheckCircle className="w-4 h-4 mr-1" />
                등록하기
              </Button>
              <Button
                onClick={handleCancelOrder}
                variant="secondary"
                disabled={isLoading}
                size="sm"
              >
                <XCircle className="w-4 h-4 mr-1" />
                취소
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* 입력 영역 */}
      <Card className="mt-4">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="주문 정보를 입력하세요 (예: 서울에서 부산으로 냉동 10팔레트 500kg)..."
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows={2}
              disabled={isLoading}
            />
            {/* 음성 입력 버튼 */}
            {isSpeechSupported && (
              <button
                onClick={handleVoiceInput}
                disabled={isLoading}
                className={`absolute right-3 bottom-3 p-2 rounded-full transition-all ${
                  isListening
                    ? 'bg-red-500 text-white animate-pulse'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                title={isListening ? '음성 인식 중지' : '음성 입력'}
              >
                {isListening ? (
                  <MicOff className="w-5 h-5" />
                ) : (
                  <Mic className="w-5 h-5" />
                )}
              </button>
            )}
          </div>
          <Button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            className="self-end"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Send className="w-5 h-5 mr-2" />
                전송
              </>
            )}
          </Button>
        </div>
      </Card>
    </div>
  );
};

// History Component
const HistoryContent: React.FC<{
  chatHistory: ChatHistory[];
  historyLoading: boolean;
  loadChatHistory: () => void;
  onResumeConversation?: (history: ChatHistory) => void;
}> = ({ chatHistory, historyLoading, loadChatHistory, onResumeConversation }) => {
  const [searchKeyword, setSearchKeyword] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [intentFilter, setIntentFilter] = useState('ALL');

  // 필터링된 히스토리
  const filteredHistory = chatHistory.filter(history => {
    const matchesKeyword = !searchKeyword || 
      history.user_message.toLowerCase().includes(searchKeyword.toLowerCase()) ||
      history.assistant_message.toLowerCase().includes(searchKeyword.toLowerCase());
    
    const matchesDate = !dateFilter || 
      new Date(history.created_at).toISOString().split('T')[0] === dateFilter;
    
    const matchesIntent = intentFilter === 'ALL' || history.intent === intentFilter;

    return matchesKeyword && matchesDate && matchesIntent;
  });

  // 개별 삭제
  const handleDelete = async (id: number) => {
    if (!window.confirm('이 대화 기록을 삭제하시겠습니까?')) return;
    
    try {
      await fetch(`/api/v1/ai-chat/history/${id}`, { method: 'DELETE' });
      toast.success('대화 기록이 삭제되었습니다');
      loadChatHistory();
    } catch (error) {
      toast.error('삭제에 실패했습니다');
    }
  };

  // 전체 삭제
  const handleDeleteAll = async () => {
    if (!window.confirm('모든 대화 기록을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) return;
    
    try {
      await fetch('/api/v1/ai-chat/history/all', { method: 'DELETE' });
      toast.success('모든 대화 기록이 삭제되었습니다');
      loadChatHistory();
    } catch (error) {
      toast.error('삭제에 실패했습니다');
    }
  };

  // Excel 내보내기
  const handleExportExcel = async () => {
    try {
      const response = await fetch('/api/v1/ai-chat/history/export/excel');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat_history_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Excel 파일이 다운로드되었습니다');
    } catch (error) {
      toast.error('내보내기에 실패했습니다');
    }
  };

  // CSV 내보내기
  const handleExportCSV = () => {
    try {
      const headers = ['ID', '사용자 메시지', 'AI 응답', '의도', '액션', '생성일시'];
      const rows = filteredHistory.map(h => [
        h.id,
        `"${h.user_message.replace(/"/g, '""')}"`,
        `"${h.assistant_message.replace(/"/g, '""')}"`,
        h.intent || '',
        h.action || '',
        new Date(h.created_at).toLocaleString('ko-KR')
      ]);
      
      const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      const blob = new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat_history_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('CSV 파일이 다운로드되었습니다');
    } catch (error) {
      toast.error('내보내기에 실패했습니다');
    }
  };

  // 고유 intent 목록 추출
  const uniqueIntents = ['ALL', ...Array.from(new Set(chatHistory.map(h => h.intent).filter(Boolean)))];

  return (
    <div className="max-h-[calc(100vh-16rem)] overflow-y-auto">
      {/* 헤더 및 액션 버튼 */}
      <div className="mb-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">대화 히스토리</h2>
          <div className="flex gap-2">
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
            <Button
              onClick={handleExportExcel}
              variant="secondary"
              size="sm"
              disabled={chatHistory.length === 0}
            >
              <Download className="w-4 h-4 mr-2" />
              Excel
            </Button>
            <Button
              onClick={handleExportCSV}
              variant="secondary"
              size="sm"
              disabled={filteredHistory.length === 0}
            >
              <Download className="w-4 h-4 mr-2" />
              CSV
            </Button>
            <Button
              onClick={handleDeleteAll}
              variant="secondary"
              size="sm"
              disabled={chatHistory.length === 0}
              className="text-red-600 hover:text-red-700"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              전체 삭제
            </Button>
          </div>
        </div>

        {/* 검색 및 필터 */}
        <Card className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* 키워드 검색 */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="키워드 검색..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* 날짜 필터 */}
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* 의도 필터 */}
            <select
              value={intentFilter}
              onChange={(e) => setIntentFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {uniqueIntents.map(intent => (
                <option key={intent} value={intent}>
                  {intent === 'ALL' ? '전체 의도' : intent}
                </option>
              ))}
            </select>
          </div>

          {/* 필터 결과 표시 */}
          <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
            <span>
              전체 {chatHistory.length}개 중 {filteredHistory.length}개 표시
            </span>
            {(searchKeyword || dateFilter || intentFilter !== 'ALL') && (
              <button
                onClick={() => {
                  setSearchKeyword('');
                  setDateFilter('');
                  setIntentFilter('ALL');
                }}
                className="text-purple-600 hover:text-purple-700 font-medium"
              >
                필터 초기화
              </button>
            )}
          </div>
        </Card>
      </div>

      {/* 로딩 및 빈 상태 */}
      {historyLoading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="text-center py-20 text-gray-500">
          <History className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="mb-2">
            {chatHistory.length === 0 
              ? '아직 대화 기록이 없습니다.'
              : '검색 결과가 없습니다.'}
          </p>
          <p className="text-sm">
            {chatHistory.length === 0
              ? '위의 "새로고침" 버튼을 눌러 히스토리를 불러오세요.'
              : '다른 검색 조건을 시도해보세요.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredHistory.map((history) => (
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
                  <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
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

                {/* 메타 정보 및 액션 버튼 */}
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
                  <div className="flex items-center gap-3">
                    <span>
                      {new Date(history.created_at).toLocaleString('ko-KR')}
                    </span>
                    <div className="flex gap-1">
                      {onResumeConversation && (
                        <button
                          onClick={() => onResumeConversation(history)}
                          className="p-1 hover:bg-gray-100 rounded transition-colors"
                          title="대화 이어하기"
                        >
                          <MessageSquare className="w-4 h-4 text-blue-600" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(history.id)}
                        className="p-1 hover:bg-red-50 rounded transition-colors"
                        title="삭제"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

const OrdersPage: React.FC = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [modalOpen, setModalOpen] = useState(false);
  const [batchDispatchModalOpen, setBatchDispatchModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [uploading, setUploading] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const { isMobile } = useResponsive();

  // AI 어시스턴트 관련 상태
  const [activeTab, setActiveTab] = useState<'orders' | 'assistant' | 'history'>('orders');
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
  const [pendingOrders, setPendingOrders] = useState<ParsedOrder[] | null>(null);
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

  // 히스토리 로드 - 자동 로드 제거 (수동으로만 로드)
  // useEffect(() => {
  //   if (activeTab === 'history') {
  //     loadChatHistory();
  //   }
  // }, [activeTab]);

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

  // 대화 재개 함수
  const handleResumeConversation = (history: ChatHistory) => {
    // AI 어시스턴트 탭으로 전환
    setActiveTab('assistant');

    // 히스토리의 대화를 메시지로 복원
    const userMsg: Message = {
      id: `history-user-${history.id}`,
      role: 'user',
      content: history.user_message,
      timestamp: new Date(history.created_at),
    };

    const assistantMsg: Message = {
      id: `history-assistant-${history.id}`,
      role: 'assistant',
      content: history.assistant_message,
      timestamp: new Date(history.created_at),
      data: history.parsed_order,
      multipleData: history.parsed_orders,
    };

    // 기존 메시지 초기화 후 히스토리 메시지 추가
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: '이전 대화를 불러왔습니다. 이어서 대화하시겠습니까?',
        timestamp: new Date(),
      },
      userMsg,
      assistantMsg,
    ]);

    toast.success('대화를 불러왔습니다. AI 어시스턴트 탭에서 이어서 대화하세요.');
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

    try {
      const response = await apiClient.processChatMessage(userMessage.content, {
        pending_order: pendingOrder,
        pending_orders: pendingOrders,
        recent_messages: messages.slice(-5).map(m => ({
          role: m.role,
          content: m.content
        }))
      }, selectedModel);

      const { intent, message, parsed_order, parsed_orders, action, order_created, orders_created } = response;

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

      if (intent === 'confirm_multiple_orders' && parsed_orders) {
        setPendingOrders(parsed_orders);
        setPendingOrder(null);
      }
      else if (intent === 'confirm_order' && parsed_order) {
        setPendingOrder(parsed_order);
        setPendingOrders(null);
      }

      if (intent === 'orders_created' && orders_created) {
        setPendingOrders(null);
        setPendingOrder(null);
        toast.success(`${orders_created.length}개 주문이 등록되었습니다!`);
        fetchOrders(); // 주문 목록 새로고침
      }

      if (intent === 'order_created' && order_created) {
        setPendingOrder(null);
        setPendingOrders(null);
        toast.success(`주문 ${order_created.order_number}이(가) 등록되었습니다!`);
        fetchOrders(); // 주문 목록 새로고침
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
        fetchOrders(); // 주문 목록 새로고침
      } else if (order_created) {
        setPendingOrder(null);
        setPendingOrders(null);
        toast.success(`✅ 주문 ${order_created.order_number}이(가) 등록되었습니다!`);
        fetchOrders(); // 주문 목록 새로고침
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

  useEffect(() => {
    fetchOrders();
    // 기본 날짜 필터: 오늘 ~ 오늘
    const today = new Date();
    
    setStartDate(today.toISOString().split('T')[0]);
    setEndDate(today.toISOString().split('T')[0]);
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getOrders();
      // Safely extract items array
      const items = response.items || response.data?.items || response.data || [];
      // Ensure items is an array
      const ordersArray = Array.isArray(items) ? items : [];
      setOrders(ordersArray);
      setSelectedIds([]); // Reset selection
    } catch (error) {
      console.error('Failed to fetch orders:', error);
      toast.error('주문 목록을 불러오는데 실패했습니다');
      setOrders([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === filteredOrders.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredOrders.map(o => o.id));
    }
  };

  const handleSelectOne = (id: number) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('이 주문을 삭제하시겠습니까?')) return;
    
    try {
      await apiClient.deleteOrder(id);
      toast.success('주문이 삭제되었습니다');
      fetchOrders();
    } catch (error) {
      toast.error('주문 삭제에 실패했습니다');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) {
      toast.error('삭제할 주문을 선택해주세요');
      return;
    }
    
    if (!window.confirm(`선택한 ${selectedIds.length}개의 주문을 삭제하시겠습니까?`)) return;
    
    try {
      await Promise.all(selectedIds.map(id => apiClient.deleteOrder(id)));
      toast.success(`${selectedIds.length}개의 주문이 삭제되었습니다`);
      fetchOrders();
    } catch (error) {
      toast.error('일괄 삭제에 실패했습니다');
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/v1/orders/template/download');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'orders_template.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('양식 파일이 다운로드되었습니다');
    } catch (error) {
      toast.error('양식 다운로드에 실패했습니다');
    }
  };

  const handleDownloadAll = async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter !== 'ALL') params.append('status', statusFilter);
      
      const response = await fetch(`/api/v1/orders/export/excel?${params.toString()}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `orders_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('주문 목록이 다운로드되었습니다');
    } catch (error) {
      toast.error('다운로드에 실패했습니다');
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      const response = await fetch('/api/v1/orders/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const result = await response.json();
      toast.success(`${result.created || 0}개의 주문이 등록되었습니다`);
      fetchOrders();
    } catch (error) {
      toast.error('파일 업로드에 실패했습니다');
    } finally {
      setUploading(false);
      event.target.value = ''; // Reset file input
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      ASSIGNED: 'bg-blue-100 text-blue-800',
      IN_TRANSIT: 'bg-green-100 text-green-800',
      DELIVERED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    const labels = {
      PENDING: '배차대기',
      ASSIGNED: '배차완료',
      IN_TRANSIT: '운송중',
      DELIVERED: '배송완료',
      CANCELLED: '취소',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${styles[status as keyof typeof styles]}`}>
        {labels[status as keyof typeof labels] || status}
      </span>
    );
  };

  const isPastOrder = (order: Order): boolean => {
    if (order.status !== 'PENDING') return false;
    
    const now = new Date();
    // order.pickup_start_time은 "HH:MM:SS" 형식의 문자열
    if (order.pickup_start_time) {
      const pickupDateTime = new Date(`${order.order_date}T${order.pickup_start_time}`);
      return pickupDateTime < now;
    }
    
    // 시간 정보가 없으면 날짜만 비교
    const orderDate = new Date(order.order_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return orderDate < today;
  };

  const formatDateTime = (date: string, time?: string): string => {
    const d = new Date(date);
    const dateStr = `${d.getMonth() + 1}/${d.getDate()}`;
    if (time) {
      const timeStr = time.substring(0, 5); // HH:MM
      return `${dateStr} ${timeStr}`;
    }
    return dateStr;
  };

  const filteredOrders = orders.filter((order) => {
    const matchesSearch =
      order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (order.client_name?.toLowerCase() || '').includes(searchTerm.toLowerCase());
    
    // 상태 필터링 - 백엔드가 Enum 키값을 반환
    const matchesStatus = statusFilter === 'ALL' || order.status === statusFilter;
    
    // 날짜 필터링
    let matchesDate = true;
    if (startDate || endDate) {
      const orderDate = new Date(order.order_date);
      if (startDate && endDate) {
        matchesDate = orderDate >= new Date(startDate) && orderDate <= new Date(endDate);
      } else if (startDate) {
        matchesDate = orderDate >= new Date(startDate);
      } else if (endDate) {
        matchesDate = orderDate <= new Date(endDate);
      }
    }
    
    return matchesSearch && matchesStatus && matchesDate;
  });

  // Calculate pending orders count for AI dispatch
  const pendingOrdersList = orders.filter(order => 
    order.status === 'PENDING'
  );
  const pendingOrdersCount = pendingOrdersList.length;

  if (loading) {
    return <Loading />;
  }

  return (
    <>
    <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">주문 관리</h1>
            <p className="text-gray-600 mt-2">배송 주문을 관리하세요</p>
            
            {/* 탭 메뉴 */}
            <div className="flex gap-2 mt-4">
              <button
                onClick={() => setActiveTab('orders')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'orders'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Package className="w-4 h-4" />
                <span>주문 목록</span>
              </button>
              <button
                onClick={() => setActiveTab('assistant')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'assistant'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Bot className="w-4 h-4" />
                <span>AI 어시스턴트</span>
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'history'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <History className="w-4 h-4" />
                <span>히스토리</span>
              </button>
            </div>
          </div>
          {activeTab === 'orders' && (
          <div className="flex flex-wrap gap-2 mt-4 md:mt-0">
            <Button 
              variant={pendingOrdersCount > 0 ? "success" : "secondary"}
              onClick={() => {
                const orderIds = pendingOrdersList.map(o => o.id).join(',');
                navigate(`/optimization?order_ids=${orderIds}`);
              }}
              className={pendingOrdersCount > 0 ? "animate-pulse" : ""}
              disabled={pendingOrdersCount === 0}
              title={pendingOrdersCount === 0 ? "배차대기 주문이 없습니다" : "AI 배차 최적화 페이지로 이동"}
            >
              <Zap size={20} className="mr-2" />
              AI 배차 {pendingOrdersCount > 0 ? `(${pendingOrdersCount}건)` : ''}
            </Button>
            <Button 
              variant="secondary"
              onClick={handleDownloadTemplate}
            >
              <FileSpreadsheet size={20} className="mr-2" />
              양식 다운로드
            </Button>
            <label>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
              <Button 
                variant="secondary"
                as="span"
                disabled={uploading}
              >
                <Upload size={20} className="mr-2" />
                {uploading ? '업로드 중...' : '엑셀 업로드'}
              </Button>
            </label>
            <Button 
              variant="secondary"
              onClick={handleDownloadAll}
            >
              <Download size={20} className="mr-2" />
              전체 다운로드
            </Button>
            <Button 
              variant="secondary"
              onClick={() => setBatchDispatchModalOpen(true)}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              <FileSpreadsheet size={20} className="mr-2" />
              배차 일괄등록
            </Button>
            <Button 
              variant="primary"
              onClick={() => {
                setSelectedOrder(null);
                setModalOpen(true);
              }}
            >
              <Plus size={20} className="mr-2" />
              신규 등록
            </Button>
          </div>
          )}
        </div>

        {/* Tab Content */}
        {activeTab === 'orders' && (
          <>
        {/* Filters */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="col-span-1 md:col-span-2 lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="주문번호 또는 거래처명 검색"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="date"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  placeholder="시작일"
                />
              </div>
            </div>
            <div>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="date"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  placeholder="종료일"
                />
              </div>
            </div>
            <div>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">전체 상태</option>
                <option value="PENDING">배차대기</option>
                <option value="ASSIGNED">배차완료</option>
                <option value="IN_TRANSIT">운송중</option>
                <option value="DELIVERED">배송완료</option>
                <option value="CANCELLED">취소</option>
              </select>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {startDate || endDate ? (
                <>
                  {startDate && <span>시작: {new Date(startDate).toLocaleDateString('ko-KR')}</span>}
                  {startDate && endDate && <span className="mx-2">~</span>}
                  {endDate && <span>종료: {new Date(endDate).toLocaleDateString('ko-KR')}</span>}
                </>
              ) : (
                <span>전체 기간</span>
              )}
            </div>
            <Button 
              variant="secondary" 
              size="sm"
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('ALL');
                setStartDate('');
                setEndDate('');
              }}
            >
              <Filter size={16} className="mr-2" />
              필터 초기화
            </Button>
          </div>
        </Card>

        {/* Bulk Actions */}
        {selectedIds.length > 0 && (
          <Card>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">
                {selectedIds.length}개 항목 선택됨
              </span>
              <Button 
                variant="danger"
                size="sm"
                onClick={handleBulkDelete}
              >
                <Trash2 size={16} className="mr-2" />
                선택 항목 삭제
              </Button>
            </div>
          </Card>
        )}

        {/* Orders Table */}
        {isMobile ? (
          /* Mobile Card View */
          <div className="px-4 space-y-3">
            {filteredOrders.length === 0 ? (
              <div className="text-center py-12">
                <Package size={48} className="mx-auto mb-4 text-gray-300" />
                <p className="text-gray-500">주문이 없습니다</p>
              </div>
            ) : (
              filteredOrders.map((order) => (
                <MobileOrderCard
                  key={order.id}
                  order={order}
                  onEdit={() => {
                    setSelectedOrder(order);
                    setModalOpen(true);
                  }}
                  onDelete={() => handleDelete(order.id)}
                />
              ))
            )}
          </div>
        ) : (
          /* Desktop Table View */
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="w-12 py-3 px-4">
                      <input
                        type="checkbox"
                        checked={filteredOrders.length > 0 && selectedIds.length === filteredOrders.length}
                        onChange={handleSelectAll}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">주문번호</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">상차 날짜/시간</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">거래처</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">상차지</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">하차지</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">화물유형</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">팔레트</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">상태</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">작업</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOrders.length === 0 ? (
                    <tr>
                      <td colSpan={10} className="text-center py-8 text-gray-500">
                        <Package size={48} className="mx-auto mb-4 text-gray-300" />
                        <p>주문이 없습니다</p>
                      </td>
                    </tr>
                  ) : (
                    filteredOrders.map((order) => {
                      const isPast = isPastOrder(order);
                      return (
                        <tr 
                          key={order.id} 
                          className={`border-b border-gray-100 hover:bg-gray-50 ${isPast ? 'bg-red-50' : ''}`}
                        >
                          <td className="py-3 px-4">
                            <input
                              type="checkbox"
                              checked={selectedIds.includes(order.id)}
                              onChange={() => handleSelectOne(order.id)}
                              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                            />
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-blue-600">{order.order_number}</span>
                              {isPast && (
                                <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-medium">
                                  지난 오더
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-1 text-sm">
                              <Clock size={14} className="text-gray-400" />
                              <span>{formatDateTime(order.order_date, order.pickup_start_time)}</span>
                            </div>
                            {order.pickup_start_time && order.pickup_end_time && (
                              <div className="text-xs text-gray-500 mt-1">
                                {order.pickup_start_time.substring(0, 5)} ~ {order.pickup_end_time.substring(0, 5)}
                              </div>
                            )}
                          </td>
                          <td className="py-3 px-4">{order.client_name || order.pickup_client_name || order.delivery_client_name || '-'}</td>
                          <td className="py-3 px-4 max-w-xs truncate">{order.pickup_address || order.pickup_client_name || '-'}</td>
                          <td className="py-3 px-4 max-w-xs truncate">{order.delivery_address || order.delivery_client_name || '-'}</td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                              {order.temperature_zone || order.cargo_type || '-'}
                            </span>
                          </td>
                          <td className="py-3 px-4">{order.pallet_count || 0}개</td>
                          <td className="py-3 px-4">{getStatusBadge(order.status)}</td>
                          <td className="py-3 px-4">
                            <div className="flex space-x-2">
                              <Button 
                                size="sm" 
                                variant="secondary"
                                onClick={() => {
                                  setSelectedOrder(order);
                                  setModalOpen(true);
                                }}
                              >
                                <Edit2 size={14} className="mr-1" />
                                수정
                              </Button>
                              <Button 
                                size="sm" 
                                variant="danger"
                                onClick={() => handleDelete(order.id)}
                              >
                                <Trash2 size={14} className="mr-1" />
                                삭제
                              </Button>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">전체 주문</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{orders.length}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">대기 중</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">
                {orders.filter((o) => o.status === 'PENDING').length}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">진행 중</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {orders.filter((o) => o.status === 'IN_PROGRESS').length}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">완료</p>
              <p className="text-3xl font-bold text-gray-600 mt-2">
                {orders.filter((o) => o.status === 'COMPLETED').length}
              </p>
            </div>
          </Card>
        </div>
        </>
        )}

        {/* AI Assistant Tab */}
        {activeTab === 'assistant' && (
          <AIAssistantContent
            messages={messages}
            input={input}
            setInput={setInput}
            isLoading={isLoading}
            pendingOrder={pendingOrder}
            pendingOrders={pendingOrders}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            handleSendMessage={handleSendMessage}
            handleKeyPress={handleKeyPress}
            handleConfirmOrder={handleConfirmOrder}
            handleCancelOrder={handleCancelOrder}
            handleVoiceInput={handleVoiceInput}
            isListening={isListening}
            isSpeechSupported={isSpeechSupported}
            messagesEndRef={messagesEndRef}
          />
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <HistoryContent
            chatHistory={chatHistory}
            historyLoading={historyLoading}
            loadChatHistory={loadChatHistory}
            onResumeConversation={handleResumeConversation}
          />
        )}
      </div>

      {/* Modal */}
      <OrderModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedOrder(null);
        }}
        onSuccess={() => {
          setModalOpen(false);
          setSelectedOrder(null);
          fetchOrders();
          toast.success(selectedOrder ? '주문이 수정되었습니다' : '주문이 등록되었습니다');
        }}
        order={selectedOrder}
      />
      
      {/* Batch Dispatch Modal */}
      <BatchDispatchModal
        isOpen={batchDispatchModalOpen}
        onClose={() => setBatchDispatchModalOpen(false)}
        onSuccess={() => {
          fetchOrders();
          toast.success('배차가 일괄 등록되었습니다');
        }}
      />
    </>
  );
};

export default OrdersPage;
