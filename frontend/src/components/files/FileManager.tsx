/**
 * 파일 관리 컴포넌트 (목록, 삭제, 다운로드)
 */

import React, { useState, useEffect } from 'react';
import { File, Download, Trash2, RefreshCw, Image as ImageIcon, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

interface FileItem {
  key: string;
  size: number;
  last_modified: string;
  url: string;
}

interface FileManagerProps {
  folder?: string;
  onFileDeleted?: (key: string) => void;
  className?: string;
}

export const FileManager: React.FC<FileManagerProps> = ({
  folder = 'uploads',
  onFileDeleted,
  className = ''
}) => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());

  // 파일 목록 조회
  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/files/list?folder=${folder}&limit=100`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      } else {
        toast.error('파일 목록을 불러올 수 없습니다');
      }
    } catch (error) {
      console.error('파일 목록 조회 오류:', error);
      toast.error('파일 목록 조회 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  // 파일 삭제
  const deleteFile = async (key: string) => {
    if (!confirm('이 파일을 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`/api/files/delete/${encodeURIComponent(key)}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        toast.success('파일이 삭제되었습니다');
        setFiles((prev) => prev.filter((f) => f.key !== key));
        if (onFileDeleted) {
          onFileDeleted(key);
        }
      } else {
        const error = await response.json();
        toast.error(error.detail || '파일 삭제에 실패했습니다');
      }
    } catch (error) {
      console.error('파일 삭제 오류:', error);
      toast.error('파일 삭제 중 오류가 발생했습니다');
    }
  };

  // 파일 다운로드
  const downloadFile = async (key: string) => {
    try {
      const fileName = key.split('/').pop() || 'download';
      
      const response = await fetch(`/api/files/download/${encodeURIComponent(key)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('파일 다운로드 시작');
      } else {
        toast.error('파일 다운로드에 실패했습니다');
      }
    } catch (error) {
      console.error('파일 다운로드 오류:', error);
      toast.error('파일 다운로드 중 오류가 발생했습니다');
    }
  };

  // 선택된 파일 일괄 삭제
  const deleteSelectedFiles = async () => {
    if (selectedFiles.size === 0) {
      toast.warning('삭제할 파일을 선택해주세요');
      return;
    }

    if (!confirm(`선택한 ${selectedFiles.size}개 파일을 삭제하시겠습니까?`)) return;

    const deletePromises = Array.from(selectedFiles).map((key) =>
      fetch(`/api/files/delete/${encodeURIComponent(key)}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
    );

    try {
      await Promise.all(deletePromises);
      toast.success(`${selectedFiles.size}개 파일이 삭제되었습니다`);
      setSelectedFiles(new Set());
      fetchFiles();
    } catch (error) {
      console.error('파일 삭제 오류:', error);
      toast.error('일부 파일 삭제에 실패했습니다');
    }
  };

  // 파일 크기 포맷팅
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  // 날짜 포맷팅
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 파일 아이콘 결정
  const getFileIcon = (key: string) => {
    const extension = key.split('.').pop()?.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(extension || '')) {
      return <ImageIcon className="w-5 h-5 text-blue-600" />;
    }
    return <FileText className="w-5 h-5 text-gray-600" />;
  };

  // 체크박스 토글
  const toggleFileSelection = (key: string) => {
    setSelectedFiles((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  // 전체 선택/해제
  const toggleSelectAll = () => {
    if (selectedFiles.size === files.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(files.map((f) => f.key)));
    }
  };

  useEffect(() => {
    fetchFiles();
  }, [folder]);

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* 헤더 */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">파일 관리</h2>
            <p className="text-sm text-gray-600 mt-1">
              폴더: <span className="font-mono text-blue-600">{folder}</span>
            </p>
          </div>
          <div className="flex items-center gap-2">
            {selectedFiles.size > 0 && (
              <button
                onClick={deleteSelectedFiles}
                className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                선택 삭제 ({selectedFiles.size})
              </button>
            )}
            <button
              onClick={fetchFiles}
              disabled={loading}
              className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* 파일 목록 */}
      <div className="p-4">
        {loading && files.length === 0 ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 mx-auto text-gray-400 animate-spin mb-4" />
            <p className="text-gray-600">파일 목록을 불러오는 중...</p>
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-12">
            <File className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">파일이 없습니다</p>
          </div>
        ) : (
          <div className="space-y-2">
            {/* 전체 선택 */}
            <div className="flex items-center gap-2 py-2 px-3 bg-gray-50 rounded">
              <input
                type="checkbox"
                checked={selectedFiles.size === files.length}
                onChange={toggleSelectAll}
                className="w-4 h-4"
              />
              <span className="text-sm text-gray-600">전체 선택</span>
            </div>

            {/* 파일 리스트 */}
            {files.map((file) => (
              <div
                key={file.key}
                className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedFiles.has(file.key)}
                  onChange={() => toggleFileSelection(file.key)}
                  className="w-4 h-4"
                />

                <div className="flex-shrink-0">{getFileIcon(file.key)}</div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.key.split('/').pop()}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(file.size)} • {formatDate(file.last_modified)}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => downloadFile(file.key)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="다운로드"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteFile(file.key)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="삭제"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
