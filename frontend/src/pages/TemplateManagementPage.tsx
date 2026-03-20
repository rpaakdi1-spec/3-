import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus, Search, Star, Edit, Copy, Trash2, Power, PowerOff,
  X, Save, Loader2, AlertCircle, ChevronDown, ChevronUp, Truck
} from 'lucide-react';
import apiClient from '../api/client';
import toast from 'react-hot-toast';

// ===================== Types =====================

interface DispatchItem {
  time: string;
  vehicle_type: string;
  tonnage: number | string;
  product_type: string;
  temperature: string;
  pallet_count: number | string;
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
  is_active: boolean;
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
  last_used_at?: string;
}

// ===================== Constants =====================

const EMPTY_DISPATCH_ITEM: DispatchItem = {
  time: '',
  vehicle_type: '',
  tonnage: '',
  product_type: '',
  temperature: '냉장',
  pallet_count: '',
  notes: '',
};

const VEHICLE_TYPES = [
  '1톤', '1.5톤', '2.5톤', '3.5톤', '5톤', '11톤', '18톤', '25톤', '기타'
];

const PRODUCT_TYPES = ['식육', '육가공', '냉동식품', '신선식품', '기타'];
const TEMPERATURE_TYPES = ['냉동/냉장', '냉동', '냉장', '상온'];

// ===================== Template Form Modal =====================

interface TemplateFormModalProps {
  template: Template | null;
  onClose: () => void;
  onSaved: () => void;
}

const TemplateFormModal: React.FC<TemplateFormModalProps> = ({ template, onClose, onSaved }) => {
  const isEdit = !!template;

  const [name, setName] = useState(template?.name || '');
  const [clientName, setClientName] = useState(template?.client_name || '');
  const [category, setCategory] = useState(template?.category || '');
  const [description, setDescription] = useState(template?.description || '');
  const [defaultPickup, setDefaultPickup] = useState(template?.template_data?.default_pickup || '');
  const [defaultDelivery, setDefaultDelivery] = useState(template?.template_data?.default_delivery || '');
  const [defaultNotes, setDefaultNotes] = useState(template?.template_data?.default_notes || '');
  const [isFavorite, setIsFavorite] = useState(template?.is_favorite || false);
  const [dispatches, setDispatches] = useState<DispatchItem[]>(
    template?.template_data?.dispatches?.length
      ? template.template_data.dispatches
      : [{ ...EMPTY_DISPATCH_ITEM }]
  );
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!name.trim()) errs.name = '템플릿 이름을 입력하세요';
    if (!clientName.trim()) errs.clientName = '거래처명을 입력하세요';
    if (dispatches.length === 0) errs.dispatches = '배차 항목을 최소 1개 추가하세요';
    dispatches.forEach((d, i) => {
      if (!d.vehicle_type) errs[`d_vtype_${i}`] = '차량 타입 필수';
      if (!d.temperature) errs[`d_temp_${i}`] = '온도 필수';
      if (d.pallet_count === '' || isNaN(Number(d.pallet_count))) errs[`d_pal_${i}`] = '팔레트 수 필수';
    });
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleAddDispatch = () => {
    setDispatches(prev => [...prev, { ...EMPTY_DISPATCH_ITEM }]);
  };

  const handleRemoveDispatch = (index: number) => {
    setDispatches(prev => prev.filter((_, i) => i !== index));
  };

  const handleDispatchChange = (index: number, field: keyof DispatchItem, value: string) => {
    setDispatches(prev => prev.map((d, i) => i === index ? { ...d, [field]: value } : d));
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      const payload = {
        name: name.trim(),
        client_name: clientName.trim(),
        category: category.trim() || undefined,
        description: description.trim() || undefined,
        is_favorite: isFavorite,
        template_data: {
          dispatches: dispatches.map(d => ({
            ...d,
            tonnage: Number(d.tonnage),
            pallet_count: Number(d.pallet_count),
          })),
          default_pickup: defaultPickup.trim(),
          default_delivery: defaultDelivery.trim(),
          default_notes: defaultNotes.trim(),
        },
      };

      if (isEdit) {
        await apiClient.put(`/dispatch-form/templates/${template!.id}`, payload);
        toast.success('템플릿이 수정되었습니다');
      } else {
        await apiClient.post('/dispatch-form/templates', payload);
        toast.success('템플릿이 생성되었습니다');
      }
      onSaved();
      onClose();
    } catch (error: any) {
      const msg = error?.response?.data?.detail || '저장에 실패했습니다';
      toast.error(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[92vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b sticky top-0 bg-white z-10">
          <h2 className="text-xl font-bold text-gray-900">
            {isEdit ? '템플릿 수정' : '새 템플릿 생성'}
          </h2>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* 기본 정보 */}
          <section>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">기본 정보</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  템플릿 이름 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="예: 서울물류센터 화요일 정기배차"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.name ? 'border-red-400' : 'border-gray-300'}`}
                />
                {errors.name && <p className="mt-1 text-xs text-red-500">{errors.name}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  거래처명 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={clientName}
                  onChange={e => setClientName(e.target.value)}
                  placeholder="예: (주)한국물류"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.clientName ? 'border-red-400' : 'border-gray-300'}`}
                />
                {errors.clientName && <p className="mt-1 text-xs text-red-500">{errors.clientName}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">카테고리</label>
                <input
                  type="text"
                  value={category}
                  onChange={e => setCategory(e.target.value)}
                  placeholder="예: 정기배차, 특별배차"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex items-center gap-3 pt-6">
                <button
                  type="button"
                  onClick={() => setIsFavorite(p => !p)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
                    isFavorite ? 'border-yellow-400 bg-yellow-50 text-yellow-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Star size={16} className={isFavorite ? 'fill-current' : ''} />
                  {isFavorite ? '즐겨찾기 등록됨' : '즐겨찾기 추가'}
                </button>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">설명</label>
                <textarea
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  placeholder="템플릿에 대한 설명을 입력하세요"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>
            </div>
          </section>

          {/* 기본 주소 */}
          <section>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">기본 주소</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">기본 상차지</label>
                <input
                  type="text"
                  value={defaultPickup}
                  onChange={e => setDefaultPickup(e.target.value)}
                  placeholder="예: 서울특별시 강남구..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">기본 하차지</label>
                <input
                  type="text"
                  value={defaultDelivery}
                  onChange={e => setDefaultDelivery(e.target.value)}
                  placeholder="예: 경기도 성남시..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">기본 비고</label>
                <input
                  type="text"
                  value={defaultNotes}
                  onChange={e => setDefaultNotes(e.target.value)}
                  placeholder="공통 비고 사항"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </section>

          {/* 배차 항목 */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                배차 항목 <span className="text-red-500">*</span>
                <span className="ml-2 text-xs font-normal text-gray-500 normal-case">({dispatches.length}개)</span>
              </h3>
              <button
                type="button"
                onClick={handleAddDispatch}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Plus size={14} />
                항목 추가
              </button>
            </div>
            {errors.dispatches && (
              <div className="mb-3 flex items-center gap-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
                <AlertCircle size={14} />
                {errors.dispatches}
              </div>
            )}
            <div className="space-y-3">
              {dispatches.map((d, i) => (
                <div key={i} className="border border-gray-200 rounded-lg p-4 bg-gray-50 relative">
                  <div className="flex items-center gap-2 mb-3">
                    <Truck size={14} className="text-gray-400" />
                    <span className="text-sm font-medium text-gray-600">항목 {i + 1}</span>
                    {dispatches.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveDispatch(i)}
                        className="ml-auto p-1 text-red-400 hover:text-red-600 hover:bg-red-50 rounded"
                        title="항목 삭제"
                      >
                        <X size={14} />
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">배차 시간</label>
                      <input
                        type="text"
                        value={d.time}
                        onChange={e => handleDispatchChange(i, 'time', e.target.value)}
                        placeholder="예: 13:00"
                        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 bg-white"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">
                        차량 <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={d.vehicle_type}
                        onChange={e => handleDispatchChange(i, 'vehicle_type', e.target.value)}
                        className={`w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-blue-500 bg-white ${errors[`d_vtype_${i}`] ? 'border-red-400' : 'border-gray-300'}`}
                      >
                        <option value="">선택</option>
                        {VEHICLE_TYPES.map(v => <option key={v} value={v}>{v}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">
                        온도 <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={d.temperature}
                        onChange={e => handleDispatchChange(i, 'temperature', e.target.value)}
                        className={`w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-blue-500 bg-white ${errors[`d_temp_${i}`] ? 'border-red-400' : 'border-gray-300'}`}
                      >
                        {TEMPERATURE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">
                        팔레트 수 <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={d.pallet_count}
                        onChange={e => handleDispatchChange(i, 'pallet_count', e.target.value)}
                        placeholder="예: 16"
                        className={`w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-blue-500 bg-white ${errors[`d_pal_${i}`] ? 'border-red-400' : 'border-gray-300'}`}
                      />
                    </div>
                    <div className="md:col-span-4">
                      <label className="block text-xs text-gray-500 mb-1">비고</label>
                      <input
                        type="text"
                        value={d.notes}
                        onChange={e => handleDispatchChange(i, 'notes', e.target.value)}
                        placeholder="특이사항 입력"
                        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 bg-white"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t sticky bottom-0 bg-white">
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
          >
            취소
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={saving}
            className="flex items-center gap-2 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60 text-sm font-medium"
          >
            {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
            {saving ? '저장 중...' : (isEdit ? '수정 저장' : '템플릿 생성')}
          </button>
        </div>
      </div>
    </div>
  );
};

// ===================== Main Page =====================

const TemplateManagementPage: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');
  const [clientList, setClientList] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);

  // ─── Fetch ───────────────────────────────────────────
  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch ALL templates (active + inactive) for management page
      const response = await apiClient.get('/dispatch-form/templates/all');
      setTemplates(response.data || []);
    } catch (error: any) {
      // Fallback: active-only endpoint if /all doesn't exist yet
      try {
        const response = await apiClient.get('/dispatch-form/templates');
        setTemplates(response.data || []);
      } catch {
        console.error('템플릿 조회 실패:', error);
        toast.error('템플릿을 불러오는데 실패했습니다');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchClientList = useCallback(async () => {
    try {
      const response = await apiClient.get('/dispatch-form/templates/clients/list');
      const clients = response.data.map((item: any) => item.client_name);
      setClientList(clients);
    } catch (error) {
      console.error('거래처 목록 조회 실패:', error);
    }
  }, []);

  useEffect(() => {
    fetchTemplates();
    fetchClientList();
  }, [fetchTemplates, fetchClientList]);

  // ─── Filter ──────────────────────────────────────────
  useEffect(() => {
    let filtered = templates;

    if (filterStatus === 'active') filtered = filtered.filter(t => t.is_active);
    else if (filterStatus === 'inactive') filtered = filtered.filter(t => !t.is_active);

    if (selectedClient) filtered = filtered.filter(t => t.client_name === selectedClient);

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(q) ||
        t.client_name.toLowerCase().includes(q) ||
        (t.description && t.description.toLowerCase().includes(q)) ||
        (t.category && t.category.toLowerCase().includes(q))
      );
    }

    setFilteredTemplates(filtered);
  }, [searchQuery, selectedClient, filterStatus, templates]);

  // ─── Actions ─────────────────────────────────────────
  const toggleActive = async (template: Template) => {
    try {
      await apiClient.put(`/dispatch-form/templates/${template.id}`, {
        is_active: !template.is_active,
      });
      toast.success(`템플릿이 ${!template.is_active ? '활성화' : '비활성화'}되었습니다`);
      fetchTemplates();
    } catch (error) {
      toast.error('템플릿 상태 변경에 실패했습니다');
    }
  };

  const toggleFavorite = async (template: Template) => {
    try {
      await apiClient.put(`/dispatch-form/templates/${template.id}`, {
        is_favorite: !template.is_favorite,
      });
      toast.success(template.is_favorite ? '즐겨찾기에서 제거되었습니다' : '즐겨찾기에 추가되었습니다');
      fetchTemplates();
    } catch (error) {
      toast.error('즐겨찾기 변경에 실패했습니다');
    }
  };

  const duplicateTemplate = async (template: Template) => {
    try {
      await apiClient.post('/dispatch-form/templates', {
        name: `${template.name} (복사)`,
        client_name: template.client_name,
        category: template.category,
        description: template.description,
        template_data: template.template_data,
        is_favorite: false,
      });
      toast.success('템플릿이 복사되었습니다');
      fetchTemplates();
    } catch (error: any) {
      const msg = error?.response?.data?.detail || '템플릿 복사에 실패했습니다';
      toast.error(msg);
    }
  };

  const deleteTemplate = async (template: Template) => {
    if (!window.confirm(`"${template.name}" 템플릿을 영구 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.`)) return;
    try {
      await apiClient.delete(`/dispatch-form/templates/${template.id}?permanent=true`);
      toast.success('템플릿이 삭제되었습니다');
      fetchTemplates();
      fetchClientList();
    } catch (error) {
      toast.error('템플릿 삭제에 실패했습니다');
    }
  };

  const openCreate = () => {
    setEditingTemplate(null);
    setShowModal(true);
  };

  const openEdit = (template: Template) => {
    setEditingTemplate(template);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingTemplate(null);
  };

  // ─── Status badge ─────────────────────────────────────
  const StatusBadge: React.FC<{ active: boolean }> = ({ active }) => (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
      active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
    }`}>
      <span className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-green-500' : 'bg-gray-400'}`} />
      {active ? '활성' : '비활성'}
    </span>
  );

  // ─── Render ──────────────────────────────────────────
  const activeCount = templates.filter(t => t.is_active).length;
  const inactiveCount = templates.filter(t => !t.is_active).length;
  const favoriteCount = templates.filter(t => t.is_favorite).length;

  return (
    <div className="p-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">템플릿 관리</h1>
          <p className="mt-1 text-sm text-gray-500">
            배차 템플릿을 생성하고 관리합니다
          </p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm shadow-sm"
        >
          <Plus size={18} />
          새 템플릿
        </button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 text-center">
          <div className="text-2xl font-bold text-blue-600">{templates.length}</div>
          <div className="text-xs text-gray-500 mt-0.5">전체 템플릿</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 text-center">
          <div className="text-2xl font-bold text-green-600">{activeCount}</div>
          <div className="text-xs text-gray-500 mt-0.5">활성 템플릿</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 text-center">
          <div className="text-2xl font-bold text-yellow-500">{favoriteCount}</div>
          <div className="text-xs text-gray-500 mt-0.5">즐겨찾기</div>
        </div>
      </div>

      {/* 필터 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <div className="flex flex-wrap gap-3">
          {/* 검색 */}
          <div className="flex-1 min-w-48 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="이름, 거래처, 설명 검색..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* 거래처 필터 */}
          <select
            value={selectedClient}
            onChange={e => setSelectedClient(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">모든 거래처</option>
            {clientList.map(c => <option key={c} value={c}>{c}</option>)}
          </select>

          {/* 상태 필터 */}
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            {([
              { key: 'all', label: `전체 (${templates.length})` },
              { key: 'active', label: `활성 (${activeCount})` },
              { key: 'inactive', label: `비활성 (${inactiveCount})` },
            ] as const).map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setFilterStatus(key)}
                className={`px-3 py-2 text-sm font-medium transition-colors ${
                  filterStatus === key
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 템플릿 목록 */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="animate-spin text-blue-500 mr-3" size={24} />
          <span className="text-gray-500">로딩 중...</span>
        </div>
      ) : filteredTemplates.length === 0 ? (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
          <p className="text-gray-500 mb-3">
            {templates.length === 0 ? '등록된 템플릿이 없습니다' : '검색 결과가 없습니다'}
          </p>
          {templates.length === 0 && (
            <button onClick={openCreate} className="text-blue-600 hover:underline text-sm">
              + 첫 번째 템플릿 생성하기
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTemplates.map(template => (
            <div
              key={template.id}
              className={`bg-white border rounded-xl p-4 hover:shadow-md transition-all ${
                template.is_active ? 'border-gray-200' : 'border-gray-100 opacity-70'
              }`}
            >
              {/* 카드 헤더 */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0 mr-2">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <h3 className="font-semibold text-gray-900 truncate">{template.name}</h3>
                    {template.is_favorite && (
                      <Star className="text-yellow-500 fill-current shrink-0" size={14} />
                    )}
                  </div>
                  <p className="text-sm text-gray-500 truncate">{template.client_name}</p>
                  <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                    <StatusBadge active={template.is_active} />
                    {template.category && (
                      <span className="px-2 py-0.5 text-xs bg-blue-50 text-blue-700 rounded-full border border-blue-100">
                        {template.category}
                      </span>
                    )}
                  </div>
                </div>

                {/* 상태 변경 버튼 */}
                <button
                  onClick={() => toggleActive(template)}
                  className={`p-1.5 rounded-lg shrink-0 transition-colors ${
                    template.is_active
                      ? 'text-green-600 hover:bg-green-50'
                      : 'text-gray-400 hover:bg-gray-100'
                  }`}
                  title={template.is_active ? '클릭하여 비활성화' : '클릭하여 활성화'}
                >
                  {template.is_active ? <Power size={18} /> : <PowerOff size={18} />}
                </button>
              </div>

              {/* 설명 */}
              {template.description && (
                <p className="text-sm text-gray-500 mb-3 line-clamp-2">{template.description}</p>
              )}

              {/* 배차 항목 요약 */}
              {template.template_data?.dispatches?.length > 0 && (
                <div className="mb-3 px-3 py-2 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">배차 항목 {template.template_data.dispatches.length}개</p>
                  <div className="text-xs text-gray-700 truncate">
                    {template.template_data.dispatches.slice(0, 2).map((d, i) => (
                      <span key={i} className="mr-2">{d.vehicle_type || d.product_type}</span>
                    ))}
                    {template.template_data.dispatches.length > 2 && (
                      <span className="text-gray-400">+{template.template_data.dispatches.length - 2}개</span>
                    )}
                  </div>
                </div>
              )}

              {/* 통계 */}
              <div className="flex gap-3 mb-3 text-xs text-gray-400">
                <span>사용 {template.usage_count}회</span>
                {template.last_used_at && (
                  <span>최근 {new Date(template.last_used_at).toLocaleDateString('ko-KR')}</span>
                )}
              </div>

              {/* 액션 버튼 */}
              <div className="grid grid-cols-4 gap-1.5">
                <button
                  onClick={() => toggleFavorite(template)}
                  className={`flex items-center justify-center py-2 rounded-lg border text-sm transition-colors ${
                    template.is_favorite
                      ? 'border-yellow-300 bg-yellow-50 text-yellow-600 hover:bg-yellow-100'
                      : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                  }`}
                  title={template.is_favorite ? '즐겨찾기 해제' : '즐겨찾기 추가'}
                >
                  <Star size={15} className={template.is_favorite ? 'fill-current' : ''} />
                </button>
                <button
                  onClick={() => openEdit(template)}
                  className="flex items-center justify-center py-2 border border-gray-200 rounded-lg text-gray-600 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600 transition-colors"
                  title="수정"
                >
                  <Edit size={15} />
                </button>
                <button
                  onClick={() => duplicateTemplate(template)}
                  className="flex items-center justify-center py-2 border border-gray-200 rounded-lg text-gray-600 hover:bg-green-50 hover:border-green-200 hover:text-green-600 transition-colors"
                  title="복사"
                >
                  <Copy size={15} />
                </button>
                <button
                  onClick={() => deleteTemplate(template)}
                  className="flex items-center justify-center py-2 border border-red-200 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
                  title="삭제"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 생성/수정 모달 */}
      {showModal && (
        <TemplateFormModal
          template={editingTemplate}
          onClose={closeModal}
          onSaved={() => {
            fetchTemplates();
            fetchClientList();
          }}
        />
      )}
    </div>
  );
};

export default TemplateManagementPage;
