/**
 * 채팅 페이지 (메인)
 */

import React, { useState, useEffect } from 'react';
import { MessageSquare, Users, Settings, X } from 'lucide-react';
import { ChatRoomList } from '../components/chat/ChatRoomList';
import { MessageList } from '../components/chat/MessageList';
import { MessageInput } from '../components/chat/MessageInput';
import { useChatWebSocket } from '../hooks/useChatWebSocket';
import toast from 'react-hot-toast';

interface ChatPageProps {}

export const ChatPage: React.FC<ChatPageProps> = () => {
  const [selectedRoomId, setSelectedRoomId] = useState<number | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number>(0);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [roomName, setRoomName] = useState('');
  const [roomDescription, setRoomDescription] = useState('');
  const [selectedRoomInfo, setSelectedRoomInfo] = useState<any>(null);

  // WebSocket 훅
  const {
    isConnected,
    messages,
    typingUsers,
    sendMessage,
    sendTyping
  } = useChatWebSocket({
    roomId: selectedRoomId,
    onMessageReceived: (message) => {
      console.log('새 메시지 수신:', message);
    }
  });

  // 현재 사용자 ID 가져오기
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const user = await response.json();
          setCurrentUserId(user.id);
        }
      } catch (error) {
        console.error('사용자 정보 조회 오류:', error);
      }
    };

    fetchCurrentUser();
  }, []);

  // 선택된 채팅방 정보 조회
  useEffect(() => {
    if (!selectedRoomId) {
      setSelectedRoomInfo(null);
      return;
    }

    const fetchRoomInfo = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/v1/chat/rooms/${selectedRoomId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setSelectedRoomInfo(data);
        }
      } catch (error) {
        console.error('채팅방 정보 조회 오류:', error);
      }
    };

    fetchRoomInfo();
  }, [selectedRoomId]);

  // 채팅방 선택
  const handleRoomSelect = (roomId: number) => {
    setSelectedRoomId(roomId);
  };

  // 채팅방 생성
  const handleCreateRoom = async () => {
    if (!roomName.trim()) {
      toast.error('채팅방 이름을 입력해주세요');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/chat/rooms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: roomName,
          description: roomDescription
        })
      });

      if (response.ok) {
        const data = await response.json();
        toast.success('채팅방이 생성되었습니다');
        setShowCreateModal(false);
        setRoomName('');
        setRoomDescription('');
        setSelectedRoomId(data.id);
      } else {
        throw new Error('채팅방 생성 실패');
      }
    } catch (error) {
      console.error('채팅방 생성 오류:', error);
      toast.error('채팅방 생성에 실패했습니다');
    }
  };

  // 메시지 전송
  const handleSendMessage = (content: string, messageType: 'text' | 'image' | 'file', fileUrl?: string) => {
    const success = sendMessage(content, messageType, fileUrl);
    if (!success) {
      toast.error('메시지 전송에 실패했습니다');
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* 헤더 */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <MessageSquare className="w-7 h-7 text-blue-600" />
            실시간 채팅
          </h1>
          
          {selectedRoomInfo && (
            <div className="flex items-center gap-4">
              <div className="text-right">
                <h2 className="font-semibold text-gray-800">{selectedRoomInfo.name}</h2>
                <p className="text-sm text-gray-600 flex items-center gap-1">
                  <Users className="w-3 h-3" />
                  {selectedRoomInfo.participant_count}명
                  {isConnected && (
                    <span className="ml-2 flex items-center gap-1">
                      <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                      <span className="text-green-600">연결됨</span>
                    </span>
                  )}
                </p>
              </div>
              <button
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="채팅방 설정"
              >
                <Settings className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 채팅방 목록 (왼쪽) */}
        <ChatRoomList
          selectedRoomId={selectedRoomId}
          onRoomSelect={handleRoomSelect}
          onCreateRoom={() => setShowCreateModal(true)}
          className="w-80 hidden md:flex"
        />

        {/* 채팅 영역 (오른쪽) */}
        <div className="flex-1 flex flex-col">
          {selectedRoomId ? (
            <>
              {/* 메시지 목록 */}
              <MessageList
                messages={messages}
                currentUserId={currentUserId}
                typingUsers={typingUsers}
                className="flex-1"
              />

              {/* 메시지 입력 */}
              <MessageInput
                onSendMessage={handleSendMessage}
                onTyping={sendTyping}
                disabled={!isConnected}
              />
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-xl font-semibold mb-2">채팅방을 선택해주세요</h3>
                <p className="text-sm">
                  왼쪽에서 채팅방을 선택하거나 새로운 채팅방을 만들어보세요
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 채팅방 생성 모달 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">새 채팅방 만들기</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  채팅방 이름 *
                </label>
                <input
                  type="text"
                  value={roomName}
                  onChange={(e) => setRoomName(e.target.value)}
                  placeholder="예: 배송팀 채팅"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  maxLength={100}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  설명
                </label>
                <textarea
                  value={roomDescription}
                  onChange={(e) => setRoomDescription(e.target.value)}
                  placeholder="채팅방에 대한 간단한 설명을 입력하세요"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={3}
                  maxLength={500}
                />
              </div>

              <div className="flex gap-2 pt-4">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  취소
                </button>
                <button
                  onClick={handleCreateRoom}
                  disabled={!roomName.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  만들기
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPage;
