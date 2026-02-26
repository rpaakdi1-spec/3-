/**
 * 파일 업로드 컴포넌트 (드래그 & 드롭 지원)
 */

import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, X, File, Image as ImageIcon, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface FileUploadProps {
  onUploadComplete?: (files: UploadedFile[]) => void;
  accept?: string;
  maxFiles?: number;
  maxSizeBytes?: number;
  folder?: string;
  uploadType?: 'file' | 'image';
  className?: string;
}

interface UploadedFile {
  url: string;
  key: string;
  name: string;
  size: number;
  contentType?: string;
}

interface FileWithPreview {
  file: File;
  preview?: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
  uploadedData?: UploadedFile;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onUploadComplete,
  accept = '*/*',
  maxFiles = 10,
  maxSizeBytes = 50 * 1024 * 1024, // 50MB
  folder = 'uploads',
  uploadType = 'file',
  className = ''
}) => {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 파일 크기 포맷팅
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  // 파일 검증
  const validateFile = (file: File): string | null => {
    if (file.size > maxSizeBytes) {
      return `파일 크기가 너무 큽니다 (최대: ${formatFileSize(maxSizeBytes)})`;
    }

    if (uploadType === 'image' && !file.type.startsWith('image/')) {
      return '이미지 파일만 업로드 가능합니다';
    }

    return null;
  };

  // 파일 미리보기 생성 (이미지만)
  const createPreview = (file: File): Promise<string | undefined> => {
    return new Promise((resolve) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = () => resolve(undefined);
        reader.readAsDataURL(file);
      } else {
        resolve(undefined);
      }
    });
  };

  // 파일 추가 처리
  const handleFiles = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;

    const newFiles: FileWithPreview[] = [];

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];

      // 파일 개수 확인
      if (files.length + newFiles.length >= maxFiles) {
        toast.warning(`최대 ${maxFiles}개 파일만 업로드할 수 있습니다`);
        break;
      }

      // 파일 검증
      const error = validateFile(file);
      if (error) {
        toast.error(`${file.name}: ${error}`);
        continue;
      }

      // 미리보기 생성
      const preview = await createPreview(file);

      newFiles.push({
        file,
        preview,
        progress: 0,
        status: 'pending'
      });
    }

    if (newFiles.length > 0) {
      setFiles((prev) => [...prev, ...newFiles]);
    }
  };

  // 드래그 이벤트
  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = e.dataTransfer.files;
    handleFiles(droppedFiles);
  };

  // 파일 선택
  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  // 파일 제거
  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // 파일 업로드
  const uploadFile = async (fileWithPreview: FileWithPreview, index: number): Promise<void> => {
    const { file } = fileWithPreview;

    // 상태 업데이트: uploading
    setFiles((prev) =>
      prev.map((f, i) => (i === index ? { ...f, status: 'uploading', progress: 0 } : f))
    );

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder', folder);

      if (uploadType === 'image') {
        formData.append('max_width', '1920');
        formData.append('max_height', '1080');
        formData.append('quality', '85');
      }

      const endpoint = uploadType === 'image' 
        ? '/api/files/upload-image' 
        : '/api/files/upload';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();

      // 상태 업데이트: success
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index
            ? {
                ...f,
                status: 'success',
                progress: 100,
                uploadedData: {
                  url: result.url,
                  key: result.key,
                  name: file.name,
                  size: result.size,
                  contentType: result.content_type
                }
              }
            : f
        )
      );

      toast.success(`${file.name} 업로드 완료`);
    } catch (error) {
      console.error('Upload error:', error);

      // 상태 업데이트: error
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index
            ? {
                ...f,
                status: 'error',
                error: error instanceof Error ? error.message : 'Upload failed'
              }
            : f
        )
      );

      toast.error(`${file.name} 업로드 실패`);
    }
  };

  // 모든 파일 업로드
  const uploadAllFiles = async () => {
    const pendingFiles = files
      .map((f, index) => ({ file: f, index }))
      .filter(({ file }) => file.status === 'pending');

    if (pendingFiles.length === 0) {
      toast.warning('업로드할 파일이 없습니다');
      return;
    }

    // 순차 업로드
    for (const { file, index } of pendingFiles) {
      await uploadFile(file, index);
    }

    // 완료 콜백
    const uploadedFiles = files
      .filter((f) => f.status === 'success' && f.uploadedData)
      .map((f) => f.uploadedData!);

    if (uploadedFiles.length > 0 && onUploadComplete) {
      onUploadComplete(uploadedFiles);
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* 드래그 & 드롭 영역 */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          파일을 드래그하거나 클릭하여 선택
        </p>
        <p className="text-sm text-gray-500">
          {uploadType === 'image' ? '이미지 파일' : '모든 파일'} (최대 {maxFiles}개, 개당 {formatFileSize(maxSizeBytes)})
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={maxFiles > 1}
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* 파일 목록 */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">
              선택된 파일 ({files.length})
            </h3>
            <button
              onClick={uploadAllFiles}
              disabled={files.every((f) => f.status !== 'pending')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-sm font-medium"
            >
              모두 업로드
            </button>
          </div>

          <div className="space-y-2">
            {files.map((fileWithPreview, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg"
              >
                {/* 미리보기 또는 아이콘 */}
                <div className="flex-shrink-0">
                  {fileWithPreview.preview ? (
                    <img
                      src={fileWithPreview.preview}
                      alt={fileWithPreview.file.name}
                      className="w-12 h-12 object-cover rounded"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gray-100 rounded flex items-center justify-center">
                      <File className="w-6 h-6 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* 파일 정보 */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {fileWithPreview.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(fileWithPreview.file.size)}
                  </p>

                  {/* 진행률 바 */}
                  {fileWithPreview.status === 'uploading' && (
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-1">
                      <div
                        className="bg-blue-600 h-1 rounded-full transition-all"
                        style={{ width: `${fileWithPreview.progress}%` }}
                      />
                    </div>
                  )}

                  {/* 에러 메시지 */}
                  {fileWithPreview.status === 'error' && (
                    <p className="text-xs text-red-600 mt-1">{fileWithPreview.error}</p>
                  )}
                </div>

                {/* 상태 아이콘 */}
                <div className="flex-shrink-0">
                  {fileWithPreview.status === 'success' && (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  )}
                  {fileWithPreview.status === 'error' && (
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  )}
                  {fileWithPreview.status === 'pending' && (
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 hover:bg-gray-100 rounded transition-colors"
                    >
                      <X className="w-5 h-5 text-gray-400" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
