/**
 * 채팅방 목록 컴포넌트
 */

import React, { useEffect, useState } from 'react';
import { MessageSquare, Users, Plus, Search } from 'lucide-react';
import toast from 'react-hot-toast';

export interface ChatRoom {
  id: number;
  name: string;
  description?: string;
  participant_count: number;
  last_message?: string;
  last_message_at?: string;
  unread_count: number;
  created_at: string;
}

interface ChatRoomListProps {
  selectedRoomId: number | null;
  onRoomSelect: (roomId: number) => void;
  onCreateRoom: () => void;
  className?: string;
}

export const ChatRoomList: React.FC<ChatRoomListProps> = ({
  selectedRoomId,
  onRoomSelect,
  onCreateRoom,
  className = ''
}) => {
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // 채팅방 목록 조회
  const fetchRooms = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/chat/rooms', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRooms(data);
      } else {
        throw new Error('채팅방 목록을 불러올 수 없습니다');
      }
    } catch (error) {
      console.error('채팅방 목록 조회 오류:', error);
      toast.error('채팅방 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRooms();
    
    // 30초마다 목록 갱신
    const interval = setInterval(fetchRooms, 30000);
    return () => clearInterval(interval);
  }, []);

  // 검색 필터링
  const filteredRooms = rooms.filter(room =>
    room.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    room.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 시간 포맷팅
  const formatTime = (dateString?: string) => {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return '방금 전';
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;
    
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-full bg-white border-r ${className}`}>
        <div className="text-gray-500">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full bg-white border-r ${className}`}>
      {/* 헤더 */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            채팅
          </h2>
          <button
            onClick={onCreateRoom}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="새 채팅방 만들기"
          >
            <Plus className="w-5 h-5 text-blue-600" />
          </button>
        </div>

        {/* 검색 */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="채팅방 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* 채팅방 목록 */}
      <div className="flex-1 overflow-y-auto">
        {filteredRooms.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 p-4">
            <MessageSquare className="w-12 h-12 mb-3 text-gray-300" />
            <p className="text-sm text-center">
              {searchQuery ? '검색 결과가 없습니다' : '채팅방이 없습니다'}
            </p>
            {!searchQuery && (
              <button
                onClick={onCreateRoom}
                className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
              >
                채팅방 만들기
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y">
            {filteredRooms.map((room) => (
              <button
                key={room.id}
                onClick={() => onRoomSelect(room.id)}
                className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                  selectedRoomId === room.id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <h3 className="font-semibold text-gray-800 truncate flex-1">
                    {room.name}
                  </h3>
                  {room.last_message_at && (
                    <span className="text-xs text-gray-500 ml-2 whitespace-nowrap">
                      {formatTime(room.last_message_at)}
                    </span>
                  )}
                </div>

                {room.description && (
                  <p className="text-xs text-gray-600 mb-2 truncate">
                    {room.description}
                  </p>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Users className="w-3 h-3" />
                    <span>{room.participant_count}</span>
                  </div>

                  {room.unread_count > 0 && (
                    <span className="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold">
                      {room.unread_count > 99 ? '99+' : room.unread_count}
                    </span>
                  )}
                </div>

                {room.last_message && (
                  <p className="text-sm text-gray-600 mt-2 truncate">
                    {room.last_message}
                  </p>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
