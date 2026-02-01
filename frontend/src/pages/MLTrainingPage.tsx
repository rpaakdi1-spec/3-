import React, { useState, useEffect } from 'react';
import { Brain, Upload, Download, Play, CheckCircle, AlertCircle, FileSpreadsheet, TrendingUp, Database } from 'lucide-react';
import { toast } from 'react-hot-toast';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';

interface TrainingFile {
  filename: string;
  uploaded_at: string;
  file_size_kb: number;
  data_count: number;
}

interface TrainingStatus {
  dispatch_optimizer?: {
    status: string;
    trained_at?: string;
    data_count?: number;
  };
  training_data_files?: string[];
}

const MLTrainingPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [training, setTraining] = useState(false);
  const [trainingHistory, setTrainingHistory] = useState<TrainingFile[]>([]);
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  // 학습 설정
  const [modelType, setModelType] = useState('dispatch');
  const [epochs, setEpochs] = useState(10);
  const [batchSize, setBatchSize] = useState(32);

  useEffect(() => {
    fetchTrainingData();
  }, []);

  const fetchTrainingData = async () => {
    try {
      setLoading(true);
      
      // 학습 상태 조회
      const statusResponse = await fetch('/api/v1/ml/training/status');
      const statusData = await statusResponse.json();
      setTrainingStatus(statusData);

      // 학습 이력 조회
      const historyResponse = await fetch('/api/v1/ml/training/history');
      const historyData = await historyResponse.json();
      setTrainingHistory(historyData.files || []);

    } catch (error) {
      console.error('Failed to fetch training data:', error);
      toast.error('데이터를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/v1/ml/training/template/download');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'AI학습데이터_template.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('템플릿이 다운로드되었습니다');
    } catch (error) {
      console.error('Failed to download template:', error);
      toast.error('템플릿 다운로드에 실패했습니다');
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('파일을 선택해주세요');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setUploading(true);
      const response = await fetch('/api/v1/ml/training/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '업로드 실패');
      }

      const result = await response.json();
      setUploadResult(result);
      
      toast.success(`${result.valid_rows}건의 데이터가 업로드되었습니다`);
      
      // 업로드 성공 후 이력 갱신
      fetchTrainingData();
      
    } catch (error: any) {
      console.error('Upload failed:', error);
      toast.error(error.message || '업로드에 실패했습니다');
    } finally {
      setUploading(false);
    }
  };

  const handleStartTraining = async () => {
    if (!uploadResult && trainingHistory.length === 0) {
      toast.error('먼저 학습 데이터를 업로드해주세요');
      return;
    }

    try {
      setTraining(true);
      
      const response = await fetch('/api/v1/ml/training/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_type: modelType,
          epochs: epochs,
          batch_size: batchSize,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '학습 시작 실패');
      }

      const result = await response.json();
      
      toast.success(`AI 학습이 완료되었습니다!\n학습 데이터: ${result.training_data_count}건`);
      
      // 학습 완료 후 상태 갱신
      fetchTrainingData();
      
    } catch (error: any) {
      console.error('Training failed:', error);
      toast.error(error.message || '학습에 실패했습니다');
    } finally {
      setTraining(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Loading />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 flex items-center">
              <Brain className="mr-3 text-blue-600" size={36} />
              AI 모델 학습
            </h1>
            <p className="text-gray-600 mt-1">배차 데이터를 업로드하고 AI 모델을 학습시킵니다</p>
          </div>
        </div>

        {/* 현재 상태 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">학습된 모델</p>
                <p className="text-2xl font-bold text-gray-800">
                  {trainingStatus?.dispatch_optimizer?.status === 'trained' ? '✅ 완료' : '❌ 미학습'}
                </p>
                {trainingStatus?.dispatch_optimizer?.trained_at && (
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(trainingStatus.dispatch_optimizer.trained_at).toLocaleString('ko-KR')}
                  </p>
                )}
              </div>
              <CheckCircle className="text-green-500" size={48} />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">학습 데이터</p>
                <p className="text-2xl font-bold text-gray-800">
                  {trainingStatus?.dispatch_optimizer?.data_count || 0}건
                </p>
                <p className="text-xs text-gray-500 mt-1">사용된 데이터</p>
              </div>
              <Database className="text-blue-500" size={48} />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">업로드된 파일</p>
                <p className="text-2xl font-bold text-gray-800">
                  {trainingHistory.length}개
                </p>
                <p className="text-xs text-gray-500 mt-1">학습 데이터 파일</p>
              </div>
              <FileSpreadsheet className="text-purple-500" size={48} />
            </div>
          </Card>
        </div>

        {/* Step 1: 템플릿 다운로드 */}
        <Card className="mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">1</span>
            템플릿 다운로드
          </h2>
          <p className="text-gray-600 mb-4">
            AI 학습에 필요한 엑셀 템플릿을 다운로드하세요. 템플릿에는 샘플 데이터와 필드 설명이 포함되어 있습니다.
          </p>
          <Button onClick={handleDownloadTemplate} variant="primary">
            <Download size={18} className="mr-2" />
            AI 학습 템플릿 다운로드
          </Button>
        </Card>

        {/* Step 2: 데이터 업로드 */}
        <Card className="mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="bg-green-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">2</span>
            학습 데이터 업로드
          </h2>
          <p className="text-gray-600 mb-4">
            작성한 엑셀 파일을 업로드하세요. 거리와 소요시간은 네이버 지도 API로 자동 계산됩니다.
          </p>

          <div className="flex items-center gap-4">
            <label className="flex-1">
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileSelect}
                className="hidden"
              />
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500 transition-colors">
                {selectedFile ? (
                  <div>
                    <FileSpreadsheet size={48} className="mx-auto text-green-600 mb-2" />
                    <p className="text-sm font-medium text-gray-800">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">{(selectedFile.size / 1024).toFixed(2)} KB</p>
                  </div>
                ) : (
                  <div>
                    <Upload size={48} className="mx-auto text-gray-400 mb-2" />
                    <p className="text-sm text-gray-600">클릭하여 파일 선택</p>
                    <p className="text-xs text-gray-500">.xlsx, .xls 파일만 가능</p>
                  </div>
                )}
              </div>
            </label>

            <Button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              variant="primary"
            >
              <Upload size={18} className="mr-2" />
              {uploading ? '업로드 중...' : '업로드'}
            </Button>
          </div>

          {/* 업로드 결과 */}
          {uploadResult && (
            <div className={`mt-4 p-4 rounded-lg ${uploadResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className="flex items-start">
                {uploadResult.success ? (
                  <CheckCircle className="text-green-600 mr-3 flex-shrink-0" size={24} />
                ) : (
                  <AlertCircle className="text-red-600 mr-3 flex-shrink-0" size={24} />
                )}
                <div className="flex-1">
                  <p className={`font-semibold ${uploadResult.success ? 'text-green-800' : 'text-red-800'}`}>
                    {uploadResult.message}
                  </p>
                  <div className="mt-2 text-sm space-y-1">
                    <p>총 데이터: {uploadResult.total_rows}건</p>
                    <p className="text-green-700">✓ 유효: {uploadResult.valid_rows}건</p>
                    {uploadResult.error_rows > 0 && (
                      <p className="text-red-700">✗ 오류: {uploadResult.error_rows}건</p>
                    )}
                  </div>
                  {uploadResult.errors && uploadResult.errors.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-600 font-semibold">오류 목록:</p>
                      <ul className="text-xs text-gray-600 list-disc list-inside">
                        {uploadResult.errors.map((error: string, idx: number) => (
                          <li key={idx}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* Step 3: 학습 시작 */}
        <Card className="mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="bg-purple-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">3</span>
            AI 학습 시작
          </h2>
          <p className="text-gray-600 mb-4">
            학습 설정을 확인하고 AI 모델 학습을 시작하세요.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                모델 종류
              </label>
              <select
                value={modelType}
                onChange={(e) => setModelType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="dispatch">배차 최적화</option>
                <option value="demand">수요 예측</option>
                <option value="failure">고장 예측</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Epochs (반복 횟수)
              </label>
              <input
                type="number"
                value={epochs}
                onChange={(e) => setEpochs(parseInt(e.target.value))}
                min="1"
                max="1000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Batch Size
              </label>
              <input
                type="number"
                value={batchSize}
                onChange={(e) => setBatchSize(parseInt(e.target.value))}
                min="1"
                max="256"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <Button
            onClick={handleStartTraining}
            disabled={training || (!uploadResult && trainingHistory.length === 0)}
            variant="primary"
            className="w-full py-3 text-lg"
          >
            <Play size={24} className="mr-2" />
            {training ? '학습 중...' : 'AI 학습 시작'}
          </Button>

          {training && (
            <div className="mt-4 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-sm text-gray-600 mt-2">AI 모델을 학습하고 있습니다...</p>
            </div>
          )}
        </Card>

        {/* 학습 이력 */}
        <Card>
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <TrendingUp className="mr-3 text-blue-600" size={24} />
            학습 이력
          </h2>

          {trainingHistory.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">파일명</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">업로드 시간</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">파일 크기</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">데이터 건수</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trainingHistory.map((file, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-800">{file.filename}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(file.uploaded_at).toLocaleString('ko-KR')}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">{file.file_size_kb.toFixed(2)} KB</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{file.data_count}건</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <FileSpreadsheet size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">학습 이력이 없습니다</p>
              <p className="text-sm text-gray-500">먼저 학습 데이터를 업로드해주세요</p>
            </div>
          )}
        </Card>
      </div>
    </Layout>
  );
};

export default MLTrainingPage;
