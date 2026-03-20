import React, { useState, useEffect } from 'react';
import { Search, Star, Clock, BookOpen, X } from 'lucide-react';
import apiClient from '../../api/client';
import toast from 'react-hot-toast';

interface DispatchItem {
  time: string;
  vehicle_type: string;
  tonnage: number;
  product_type: string;
  temperature: string;
  pallet_count: number;
  notes: string;
}

interface TemplateData {
  dispatches: DispatchItem[];
  default_pickup: string;
  default_delivery: string;
  default_notes: string;
}

interface Template {
  id: number;
  name: string;
  client_name: string;
  category?: string;
  description?: string;
  template_data: TemplateData;
  usage_count: number;
  is_favorite: boolean;
}

interface DispatchTemplateSelectorProps {
  onSelectTemplate: (template: Template) => void;
  onClose: () => void;
}

const DispatchTemplateSelector: React.FC<DispatchTemplateSelectorProps> = ({
  onSelectTemplate,
  onClose
}) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [clientList, setClientList] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTemplates();
    fetchClientList();
  }, []);

  useEffect(() => {
    filterTemplates();
  }, [searchQuery, selectedClient, templates]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/dispatch-form/templates');
      setTemplates(response.data || []);
    } catch (error) {
      console.error('템플릿 조회 실패:', error);
      toast.error('템플릿을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const fetchClientList = async () => {
    try {
      const response = await apiClient.get('/dispatch-form/templates/clients/list');
      const clients = response.data.map((item: any) => item.client_name);
      setClientList(clients);
    } catch (error) {
      console.error('거래처 목록 조회 실패:', error);
    }
  };

  const filterTemplates = () => {
    let filtered = templates;

    if (selectedClient) {
      filtered = filtered.filter(t => t.client_name === selectedClient);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.client_name.toLowerCase().includes(query) ||
        (t.description && t.description.toLowerCase().includes(query))
      );
    }

    setFilteredTemplates(filtered);
  };

  const handleSelectTemplate = async (template: Template) => {
    // 사용 횟수 증가 (실패해도 템플릿 적용 진행)
    apiClient.post(`/dispatch-form/templates/${template.id}/use`).catch(() => {});
    onSelectTemplate(template);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* 헤더 */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">배차 템플릿 선택</h2>
            <p className="text-sm text-gray-600 mt-1">저장된 템플릿을 선택하여 빠르게 배차를 입력하세요</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        {/* 필터 */}
        <div className="p-6 border-b bg-gray-50">
          <div className="flex flex-col md:flex-row gap-4">
            {/* 검색 */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="템플릿 이름, 거래처명 검색..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* 거래처 필터 */}
            <div className="md:w-64">
              <select
                value={selectedClient}
                onChange={(e) => setSelectedClient(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">전체 거래처</option>
                {clientList.map(client => (
                  <option key={client} value={client}>{client}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 템플릿 목록 */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-240px)]">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-gray-500 mt-4">템플릿 로딩 중...</p>
            </div>
          ) : filteredTemplates.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">검색 결과가 없습니다</p>
              <p className="text-gray-400 text-sm mt-2">다른 검색어로 시도해보세요</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredTemplates.map(template => (
                <div
                  key={template.id}
                  onClick={() => handleSelectTemplate(template)}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer group"
                >
                  {/* 헤더 */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        {template.is_favorite && (
                          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                        )}
                        <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                          {template.name}
                        </h3>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{template.client_name}</p>
                    </div>
                    {template.category && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                        {template.category}
                      </span>
                    )}
                  </div>

                  {/* 설명 */}
                  {template.description && (
                    <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                      {template.description}
                    </p>
                  )}

                  {/* 배차 정보 미리보기 */}
                  <div className="bg-gray-50 rounded p-3 mb-3">
                    <div className="text-xs text-gray-600 mb-2">
                      총 {template.template_data.dispatches.length}건의 배차
                    </div>
                    <div className="space-y-1">
                      {template.template_data.dispatches.slice(0, 3).map((dispatch, idx) => (
                        <div key={idx} className="text-xs text-gray-700 flex items-center gap-2">
                          <Clock className="w-3 h-3 text-gray-400" />
                          <span className="font-medium">{dispatch.time || '-'}</span>
                          <span>·</span>
                          <span className={dispatch.temperature === '냉동' ? 'text-blue-600 font-medium' : 'text-green-600 font-medium'}>
                            {dispatch.temperature}
                          </span>
                          <span>·</span>
                          <span>{dispatch.pallet_count}p</span>
                        </div>
                      ))}
                      {template.template_data.dispatches.length > 3 && (
                        <div className="text-xs text-gray-500">
                          +{template.template_data.dispatches.length - 3}건 더보기
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 메타 정보 */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>사용 {template.usage_count}회</span>
                    </div>
                    <span className="text-blue-600 group-hover:underline">
                      선택하기 →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DispatchTemplateSelector;
