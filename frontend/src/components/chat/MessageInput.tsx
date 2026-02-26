/**
 * 메시지 입력 컴포넌트
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Image as ImageIcon, X } from 'lucide-react';
import toast from 'react-hot-toast';

interface MessageInputProps {
  onSendMessage: (content: string, messageType: 'text' | 'image' | 'file', fileUrl?: string) => void;
  onTyping: (isTyping: boolean) => void;
  disabled?: boolean;
  className?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  onTyping,
  disabled = false,
  className = ''
}) => {
  const [message, setMessage] = useState('');
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // 타이핑 이벤트 처리
  useEffect(() => {
    if (message.trim()) {
      onTyping(true);
      
      // 3초 후 타이핑 상태 해제
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      typingTimeoutRef.current = setTimeout(() => {
        onTyping(false);
      }, 3000);
    } else {
      onTyping(false);
    }

    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [message, onTyping]);

  // 텍스트 입력 처리
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // 자동 높이 조절
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  // 파일 선택 처리
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 파일 크기 확인 (50MB)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('파일 크기는 50MB를 초과할 수 없습니다');
      return;
    }

    setSelectedFile(file);

    // 이미지 미리보기
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // 파일 제거
  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 파일 업로드
  const uploadFile = async (file: File): Promise<string | null> => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token');
      const endpoint = file.type.startsWith('image/') 
        ? '/api/files/upload-image'
        : '/api/files/upload';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        return data.file_url || data.url;
      } else {
        throw new Error('파일 업로드 실패');
      }
    } catch (error) {
      console.error('파일 업로드 오류:', error);
      toast.error('파일 업로드에 실패했습니다');
      return null;
    }
  };

  // 메시지 전송
  const handleSend = async () => {
    const trimmedMessage = message.trim();
    
    if (!trimmedMessage && !selectedFile) {
      return;
    }

    if (disabled) {
      toast.error('채팅 서버와 연결되어 있지 않습니다');
      return;
    }

    try {
      let messageType: 'text' | 'image' | 'file' = 'text';
      let fileUrl: string | undefined;

      // 파일이 있으면 업로드
      if (selectedFile) {
        setUploading(true);
        fileUrl = await uploadFile(selectedFile) || undefined;
        
        if (!fileUrl) {
          setUploading(false);
          return;
        }

        messageType = selectedFile.type.startsWith('image/') ? 'image' : 'file';
      }

      // 메시지 전송
      onSendMessage(
        trimmedMessage || selectedFile?.name || '',
        messageType,
        fileUrl
      );

      // 입력 초기화
      setMessage('');
      setSelectedFile(null);
      setPreviewUrl(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
      
      onTyping(false);
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      toast.error('메시지 전송에 실패했습니다');
    } finally {
      setUploading(false);
    }
  };

  // Enter 키 처리
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`border-t bg-white p-4 ${className}`}>
      {/* 파일 미리보기 */}
      {selectedFile && (
        <div className="mb-3 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="미리보기"
                  className="w-12 h-12 object-cover rounded"
                />
              ) : (
                <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
                  <Paperclip className="w-6 h-6 text-gray-500" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
            <button
              onClick={handleRemoveFile}
              className="p-1 hover:bg-gray-200 rounded transition-colors"
              disabled={uploading}
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>
      )}

      {/* 입력 영역 */}
      <div className="flex items-end gap-2">
        {/* 파일 첨부 버튼 */}
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          className="hidden"
          disabled={disabled || uploading}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={disabled || uploading}
          title="파일 첨부"
        >
          <Paperclip className="w-5 h-5" />
        </button>

        {/* 텍스트 입력 */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? '연결 중...' : '메시지를 입력하세요 (Shift+Enter: 줄바꿈)'}
          disabled={disabled || uploading}
          className="flex-1 px-4 py-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          rows={1}
          style={{ minHeight: '40px', maxHeight: '120px' }}
        />

        {/* 전송 버튼 */}
        <button
          onClick={handleSend}
          disabled={disabled || uploading || (!message.trim() && !selectedFile)}
          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="전송 (Enter)"
        >
          {uploading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* 힌트 */}
      <p className="text-xs text-gray-500 mt-2">
        Enter: 전송 | Shift+Enter: 줄바꿈 | 파일 크기 제한: 50MB
      </p>
    </div>
  );
};
