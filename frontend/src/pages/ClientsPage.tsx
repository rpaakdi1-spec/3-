import React, { useEffect, useState, useCallback } from 'react';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import Loading from '../components/common/Loading';
import apiClient from '../api/client';
import { Client } from '../types';
import { Building2, Plus, Edit, Upload, Download, Trash2, FileSpreadsheet } from 'lucide-react';
import toast from 'react-hot-toast';
import { useResponsive } from '../hooks/useResponsive';
import { MobileClientCard } from '../components/mobile/MobileClientCard';

const ClientsPage: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    client_type: '상차',
    address: '',
    address_detail: '',
    pickup_start_time: '09:00',
    pickup_end_time: '17:00',
    delivery_start_time: '09:00',
    delivery_end_time: '17:00',
    forklift_operator_available: false,
    loading_time_minutes: 30,
    contact_person: '',
    phone: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [uploading, setUploading] = useState(false);
  const { isMobile } = useResponsive();

  const fetchClients = useCallback(async () => {
    try {
      const response = await apiClient.getClients();
      setClients(response.items || response);
      setSelectedIds([]);
    } catch (error) {
      toast.error('거래처 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSelectAll = () => {
    if (selectedIds.length === clients.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(clients.map(c => c.id));
    }
  };

  const handleSelectOne = (id: number) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('이 거래처를 삭제하시겠습니까?')) return;
    
    try {
      await apiClient.deleteClient(id);
      toast.success('거래처가 삭제되었습니다');
      fetchClients();
    } catch (error) {
      toast.error('거래처 삭제에 실패했습니다');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) {
      toast.error('삭제할 거래처를 선택해주세요');
      return;
    }
    
    if (!window.confirm(`선택한 ${selectedIds.length}개의 거래처를 삭제하시겠습니까?`)) return;
    
    try {
      await Promise.all(selectedIds.map(id => apiClient.deleteClient(id)));
      toast.success(`${selectedIds.length}개의 거래처가 삭제되었습니다`);
      fetchClients();
    } catch (error) {
      toast.error('일괄 삭제에 실패했습니다');
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/v1/clients/template/download');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'clients_template.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('양식 파일이 다운로드되었습니다');
    } catch (error) {
      toast.error('양식 다운로드에 실패했습니다');
    }
  };

  const handleDownloadAll = async () => {
    try {
      const response = await fetch('/api/v1/clients/export/excel');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `clients_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('거래처 목록이 다운로드되었습니다');
    } catch (error) {
      toast.error('다운로드에 실패했습니다');
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      const response = await fetch('/api/v1/clients/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const result = await response.json();
      toast.success(`${result.created || 0}개의 거래처가 등록되었습니다`);
      fetchClients();
    } catch (error) {
      toast.error('파일 업로드에 실패했습니다');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

  const openCreateModal = useCallback(() => {
    setEditingClient(null);
    setFormData({
      code: '',
      name: '',
      client_type: '상차',
      address: '',
      address_detail: '',
      pickup_start_time: '09:00',
      pickup_end_time: '17:00',
      delivery_start_time: '09:00',
      delivery_end_time: '17:00',
      forklift_operator_available: false,
      loading_time_minutes: 30,
      contact_person: '',
      phone: '',
      notes: '',
    });
    setModalOpen(true);
  }, []);

  const openEditModal = useCallback((client: Client) => {
    setEditingClient(client);
    setFormData({
      code: client.code || '',
      name: client.name || '',
      client_type: client.client_type || '상차',
      address: client.address || '',
      address_detail: client.address_detail || '',
      pickup_start_time: client.pickup_start_time || '09:00',
      pickup_end_time: client.pickup_end_time || '17:00',
      delivery_start_time: client.delivery_start_time || '09:00',
      delivery_end_time: client.delivery_end_time || '17:00',
      forklift_operator_available: client.forklift_operator_available || false,
      loading_time_minutes: client.loading_time_minutes || 30,
      contact_person: client.contact_person || '',
      phone: client.phone || '',
      notes: client.notes || '',
    });
    setModalOpen(true);
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      if (editingClient) {
        await apiClient.updateClient(editingClient.id, formData);
        toast.success('거래처가 수정되었습니다');
      } else {
        await apiClient.createClient(formData);
        toast.success('거래처가 등록되었습니다');
      }
      setModalOpen(false);
      fetchClients();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '거래처 처리에 실패했습니다');
    } finally {
      setSubmitting(false);
    }
  }, [formData, editingClient, fetchClients]);

  if (loading) {
    return (
      <Layout>
        <Loading />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">거래처 관리</h1>
            <p className="text-gray-600 mt-2">거래처 정보를 관리하세요</p>
          </div>
          <div className="flex flex-wrap gap-2 mt-4 md:mt-0">
            <Button 
              variant="secondary"
              onClick={handleDownloadTemplate}
            >
              <FileSpreadsheet size={20} className="mr-2" />
              양식 다운로드
            </Button>
            <label>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
              <Button 
                variant="secondary"
                as="span"
                disabled={uploading}
              >
                <Upload size={20} className="mr-2" />
                {uploading ? '업로드 중...' : '엑셀 업로드'}
              </Button>
            </label>
            <Button 
              variant="secondary"
              onClick={handleDownloadAll}
            >
              <Download size={20} className="mr-2" />
              전체 다운로드
            </Button>
            <Button variant="primary" onClick={openCreateModal}>
              <Plus size={20} className="mr-2" />
              신규 등록
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">전체 거래처</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{clients.length}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">활성 거래처</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {clients.filter((c) => c.is_active).length}
              </p>
            </div>
          </Card>
        </div>

        {/* Bulk Actions */}
        {selectedIds.length > 0 && (
          <Card>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">
                {selectedIds.length}개 항목 선택됨
              </span>
              <Button 
                variant="danger"
                size="sm"
                onClick={handleBulkDelete}
              >
                <Trash2 size={16} className="mr-2" />
                선택 항목 삭제
              </Button>
            </div>
          </Card>
        )}

        {/* Clients Table/Cards */}
        {isMobile ? (
          /* Mobile View */
          <div className="px-4 space-y-3">
            {clients.length === 0 ? (
              <div className="text-center py-12">
                <Building2 size={48} className="mx-auto mb-4 text-gray-300" />
                <p className="text-gray-600">등록된 거래처가 없습니다</p>
              </div>
            ) : (
              clients.map((client) => (
                <MobileClientCard
                  key={client.id}
                  client={{
                    id: client.id,
                    name: client.name,
                    business_number: client.business_number,
                    contact_person: client.contact_person,
                    phone: client.phone,
                    email: client.email,
                    address: client.address,
                    is_active: client.is_active,
                  }}
                  onEdit={() => openEditModal(client)}
                  onCall={() => window.location.href = `tel:${client.phone}`}
                  onEmail={() => {
                    if (client.email) {
                      window.location.href = `mailto:${client.email}`;
                    }
                  }}
                  onViewMap={() => {
                    const query = encodeURIComponent(client.address);
                    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, '_blank');
                  }}
                />
              ))
            )}
          </div>
        ) : (
          /* Desktop Table View */
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="w-12 py-3 px-4">
                      <input
                        type="checkbox"
                        checked={clients.length > 0 && selectedIds.length === clients.length}
                        onChange={handleSelectAll}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">거래처명</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">사업자번호</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">담당자</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">연락처</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">이메일</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">상태</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">작업</th>
                  </tr>
                </thead>
                <tbody>
                  {clients.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="text-center py-8 text-gray-500">
                        <Building2 size={48} className="mx-auto mb-4 text-gray-300" />
                        <p>등록된 거래처가 없습니다</p>
                      </td>
                    </tr>
                  ) : (
                    clients.map((client) => (
                    <tr key={client.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <input
                          type="checkbox"
                          checked={selectedIds.includes(client.id)}
                          onChange={() => handleSelectOne(client.id)}
                          className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                        />
                      </td>
                      <td className="py-3 px-4 font-medium">{client.name}</td>
                      <td className="py-3 px-4">{client.business_number}</td>
                      <td className="py-3 px-4">{client.contact_person}</td>
                      <td className="py-3 px-4">{client.phone}</td>
                      <td className="py-3 px-4">{client.email || '-'}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded text-sm ${client.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                          {client.is_active ? '활성' : '비활성'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            variant="secondary"
                            onClick={() => openEditModal(client)}
                          >
                            <Edit size={14} className="mr-1" />
                            수정
                          </Button>
                          <Button 
                            size="sm" 
                            variant="danger"
                            onClick={() => handleDelete(client.id)}
                          >
                            <Trash2 size={14} className="mr-1" />
                            삭제
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
        )}

        {/* Client Modal */}
        <Modal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          title={editingClient ? '거래처 수정' : '거래처 등록'}
          size="lg"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* 거래처 코드 */}
            <Input
              label="거래처코드"
              name="code"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              placeholder="CUST-0001"
              required
            />

            {/* 거래처명 */}
            <Input
              label="거래처명"
              name="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="(주)서울냉동"
              required
            />

            {/* 구분 (상차/하차/양쪽) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                구분 <span className="text-red-500">*</span>
              </label>
              <select
                name="client_type"
                value={formData.client_type}
                onChange={(e) => setFormData({ ...formData, client_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="상차">상차</option>
                <option value="하차">하차</option>
                <option value="양쪽">양쪽 (상차/하차 모두 가능)</option>
              </select>
            </div>

            {/* 주소 */}
            <Input
              label="주소"
              name="address"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              placeholder="서울특별시 송파구 문정동 123"
              required
            />

            {/* 상세주소 */}
            <Input
              label="상세주소"
              name="address_detail"
              value={formData.address_detail}
              onChange={(e) => setFormData({ ...formData, address_detail: e.target.value })}
              placeholder="1층"
            />

            {/* 상차 가능 시간 */}
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="상차 가능 시작"
                name="pickup_start_time"
                type="time"
                value={formData.pickup_start_time}
                onChange={(e) => setFormData({ ...formData, pickup_start_time: e.target.value })}
              />
              <Input
                label="상차 가능 종료"
                name="pickup_end_time"
                type="time"
                value={formData.pickup_end_time}
                onChange={(e) => setFormData({ ...formData, pickup_end_time: e.target.value })}
              />
            </div>

            {/* 하차 가능 시간 */}
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="하차 가능 시작"
                name="delivery_start_time"
                type="time"
                value={formData.delivery_start_time}
                onChange={(e) => setFormData({ ...formData, delivery_start_time: e.target.value })}
              />
              <Input
                label="하차 가능 종료"
                name="delivery_end_time"
                type="time"
                value={formData.delivery_end_time}
                onChange={(e) => setFormData({ ...formData, delivery_end_time: e.target.value })}
              />
            </div>

            {/* 지게차 운전능력 */}
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <input
                type="checkbox"
                id="forklift_operator_available"
                checked={formData.forklift_operator_available}
                onChange={(e) => setFormData({ ...formData, forklift_operator_available: e.target.checked })}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="forklift_operator_available" className="text-sm font-medium text-gray-700 cursor-pointer">
                지게차 운전능력 (가능/불가능)
              </label>
            </div>

            {/* 상하차 소요시간 */}
            <Input
              label="상하차 소요시간 (분)"
              name="loading_time_minutes"
              type="number"
              value={formData.loading_time_minutes}
              onChange={(e) => setFormData({ ...formData, loading_time_minutes: parseInt(e.target.value) || 30 })}
              placeholder="30"
              min="1"
              required
            />

            {/* 담당자명 */}
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="담당자명"
                name="contact_person"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                placeholder="홍길동"
              />
              <Input
                label="전화번호"
                name="phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="02-1234-5678"
              />
            </div>

            {/* 특이사항 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                특이사항
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="주차공간 협소"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
              <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">
                취소
              </Button>
              <Button variant="primary" type="submit" isLoading={submitting}>
                {editingClient ? '수정' : '등록'}
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </Layout>
  );
};

export default ClientsPage;
