/**
 * 채팅 WebSocket Hook
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import toast from 'react-hot-toast';

export interface ChatMessage {
  id: number;
  room_id: number;
  user_id: number;
  content: string;
  message_type: 'text' | 'image' | 'file';
  file_url?: string;
  is_read: boolean;
  created_at: string;
  user_name?: string;
}

export interface TypingIndicator {
  user_id: number;
  user_name: string;
}

interface UseChatWebSocketProps {
  roomId: number | null;
  onMessageReceived?: (message: ChatMessage) => void;
  onTypingUpdate?: (users: TypingIndicator[]) => void;
}

export const useChatWebSocket = ({
  roomId,
  onMessageReceived,
  onTypingUpdate
}: UseChatWebSocketProps) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [typingUsers, setTypingUsers] = useState<TypingIndicator[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  // WebSocket 연결
  const connect = useCallback(() => {
    if (!roomId || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('인증 토큰이 없습니다');
        return;
      }

      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = import.meta.env.VITE_WS_URL?.replace('ws://', '').replace('wss://', '') || 
                     window.location.host;
      const wsUrl = `${wsProtocol}//${wsHost}/api/v1/chat/ws/${roomId}?token=${token}`;

      console.log('🔌 채팅 WebSocket 연결 시도:', wsUrl);

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✅ 채팅 WebSocket 연결됨');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 메시지 수신:', data);

          switch (data.type) {
            case 'message':
              const newMessage: ChatMessage = data.data;
              setMessages((prev) => [...prev, newMessage]);
              if (onMessageReceived) {
                onMessageReceived(newMessage);
              }
              break;

            case 'typing':
              const typingData: TypingIndicator[] = data.data;
              setTypingUsers(typingData);
              if (onTypingUpdate) {
                onTypingUpdate(typingData);
              }
              break;

            case 'user_joined':
              toast.info(`${data.data.user_name}님이 입장했습니다`);
              break;

            case 'user_left':
              toast.info(`${data.data.user_name}님이 퇴장했습니다`);
              break;

            case 'error':
              console.error('WebSocket 오류:', data.message);
              toast.error(data.message || '채팅 오류가 발생했습니다');
              break;

            default:
              console.warn('알 수 없는 메시지 타입:', data.type);
          }
        } catch (error) {
          console.error('메시지 파싱 오류:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket 오류:', error);
        setIsConnected(false);
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket 연결 종료:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;

        // 자동 재연결
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
          console.log(`🔄 ${delay}ms 후 재연결 시도 (${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        } else {
          toast.error('채팅 서버에 연결할 수 없습니다. 페이지를 새로고침해주세요.');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('WebSocket 연결 오류:', error);
      setIsConnected(false);
    }
  }, [roomId, onMessageReceived, onTypingUpdate]);

  // 메시지 전송
  const sendMessage = useCallback((content: string, messageType: 'text' | 'image' | 'file' = 'text', fileUrl?: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      toast.error('채팅 서버와 연결되어 있지 않습니다');
      return false;
    }

    try {
      const message = {
        type: 'message',
        data: {
          content,
          message_type: messageType,
          file_url: fileUrl
        }
      };

      wsRef.current.send(JSON.stringify(message));
      console.log('📤 메시지 전송:', message);
      return true;
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      toast.error('메시지 전송에 실패했습니다');
      return false;
    }
  }, []);

  // 타이핑 상태 전송
  const sendTyping = useCallback((isTyping: boolean) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    try {
      const message = {
        type: 'typing',
        data: { is_typing: isTyping }
      };

      wsRef.current.send(JSON.stringify(message));
    } catch (error) {
      console.error('타이핑 상태 전송 오류:', error);
    }
  }, []);

  // 연결 해제
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setMessages([]);
    setTypingUsers([]);
  }, []);

  // roomId 변경 시 재연결
  useEffect(() => {
    if (roomId) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [roomId, connect, disconnect]);

  return {
    isConnected,
    messages,
    typingUsers,
    sendMessage,
    sendTyping,
    connect,
    disconnect
  };
};
