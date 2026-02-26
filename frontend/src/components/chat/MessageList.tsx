/**
 * 메시지 목록 컴포넌트
 */

import React, { useEffect, useRef } from 'react';
import { File, Image as ImageIcon, Download } from 'lucide-react';
import { ChatMessage } from '../../hooks/useChatWebSocket';

interface MessageListProps {
  messages: ChatMessage[];
  currentUserId: number;
  typingUsers: Array<{ user_id: number; user_name: string }>;
  className?: string;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  currentUserId,
  typingUsers,
  className = ''
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageListRef = useRef<HTMLDivElement>(null);

  // 새 메시지가 추가되면 자동 스크롤
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // 시간 포맷팅
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    } else {
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      
      if (date.toDateString() === yesterday.toDateString()) {
        return '어제 ' + date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
      } else {
        return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }) + ' ' +
               date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
      }
    }
  };

  // 파일 다운로드
  const handleDownload = async (fileUrl: string, fileName: string) => {
    try {
      const response = await fetch(fileUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('파일 다운로드 오류:', error);
    }
  };

  // 메시지 렌더링
  const renderMessage = (message: ChatMessage) => {
    const isOwn = message.user_id === currentUserId;

    return (
      <div
        key={message.id}
        className={`flex mb-4 ${isOwn ? 'justify-end' : 'justify-start'}`}
      >
        <div className={`max-w-[70%] ${isOwn ? 'items-end' : 'items-start'} flex flex-col`}>
          {/* 발신자 이름 (본인 메시지가 아닐 때) */}
          {!isOwn && message.user_name && (
            <div className="text-xs text-gray-600 mb-1 px-3">
              {message.user_name}
            </div>
          )}

          {/* 메시지 내용 */}
          <div
            className={`rounded-lg px-4 py-2 ${
              isOwn
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {/* 텍스트 메시지 */}
            {message.message_type === 'text' && (
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
            )}

            {/* 이미지 메시지 */}
            {message.message_type === 'image' && message.file_url && (
              <div>
                {message.content && (
                  <p className="mb-2 whitespace-pre-wrap break-words">{message.content}</p>
                )}
                <img
                  src={message.file_url}
                  alt="첨부 이미지"
                  className="max-w-full rounded cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => window.open(message.file_url, '_blank')}
                />
              </div>
            )}

            {/* 파일 메시지 */}
            {message.message_type === 'file' && message.file_url && (
              <div className="flex items-center gap-3">
                <File className="w-8 h-8 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{message.content}</p>
                  <button
                    onClick={() => handleDownload(message.file_url!, message.content)}
                    className={`flex items-center gap-1 text-sm mt-1 hover:underline ${
                      isOwn ? 'text-blue-100' : 'text-blue-600'
                    }`}
                  >
                    <Download className="w-3 h-3" />
                    다운로드
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* 시간 및 읽음 상태 */}
          <div className={`flex items-center gap-2 mt-1 px-3 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}>
            <span className="text-xs text-gray-500">
              {formatTime(message.created_at)}
            </span>
            {isOwn && (
              <span className="text-xs text-gray-500">
                {message.is_read ? '읽음' : '안읽음'}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div
      ref={messageListRef}
      className={`flex-1 overflow-y-auto p-4 bg-gray-50 ${className}`}
    >
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <ImageIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>메시지가 없습니다</p>
            <p className="text-sm mt-1">첫 메시지를 보내보세요!</p>
          </div>
        </div>
      ) : (
        <>
          {messages.map(renderMessage)}

          {/* 타이핑 인디케이터 */}
          {typingUsers.length > 0 && (
            <div className="flex mb-4">
              <div className="bg-gray-200 rounded-lg px-4 py-2 max-w-[70%]">
                <div className="flex items-center gap-1">
                  <span className="text-sm text-gray-600">
                    {typingUsers.map(u => u.user_name).join(', ')}님이 입력 중
                  </span>
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 스크롤 앵커 */}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
};
