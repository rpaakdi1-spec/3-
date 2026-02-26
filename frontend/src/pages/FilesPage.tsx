/**
 * 파일 관리 페이지
 */

import React, { useState } from 'react';
import { FileUpload } from '../components/files/FileUpload';
import { FileManager } from '../components/files/FileManager';
import { Upload, FolderOpen } from 'lucide-react';

const FilesPage: React.FC = () => {
  const [selectedFolder, setSelectedFolder] = useState<string>('uploads');
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const folders = [
    { value: 'uploads', label: '일반 파일' },
    { value: 'images', label: '이미지' },
    { value: 'documents', label: '문서' },
    { value: 'orders', label: '주문 관련' },
    { value: 'vehicles', label: '차량 관련' }
  ];

  const handleUploadComplete = (files: any[]) => {
    console.log('업로드 완료:', files);
    // 파일 관리자 새로고침
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="space-y-6 pb-6">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">파일 관리</h1>
          <p className="text-gray-600 mt-1">파일을 업로드하고 관리합니다</p>
        </div>
      </div>

      {/* 폴더 선택 */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-2 mb-3">
          <FolderOpen className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">폴더 선택</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          {folders.map((folder) => (
            <button
              key={folder.value}
              onClick={() => setSelectedFolder(folder.value)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedFolder === folder.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {folder.label}
            </button>
          ))}
        </div>
      </div>

      {/* 파일 업로드 */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Upload className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">파일 업로드</h2>
        </div>
        <FileUpload
          folder={selectedFolder}
          maxFiles={10}
          maxSizeBytes={50 * 1024 * 1024}
          uploadType={selectedFolder === 'images' ? 'image' : 'file'}
          onUploadComplete={handleUploadComplete}
        />
      </div>

      {/* 파일 관리 */}
      <FileManager 
        key={refreshKey} 
        folder={selectedFolder} 
      />
    </div>
  );
};

export default FilesPage;
