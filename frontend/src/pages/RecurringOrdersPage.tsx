import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { toast } from 'react-hot-toast';
import Layout from '../components/common/Layout';
import axios from 'axios';
import type { RecurringOrder, RecurringOrderCreate, Client } from '../types';
import { recurringOrdersAPI } from '../api/recurringOrders';
import { RecurringOrderForm } from '../components/recurring-orders/RecurringOrderForm';
import { RecurringOrderTable } from '../components/recurring-orders/RecurringOrderTable';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const RecurringOrdersPage: React.FC = () => {
  const [recurringOrders, setRecurringOrders] = useState<RecurringOrder[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingOrder, setEditingOrder] = useState<RecurringOrder | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'inactive'>('all');

  // Load data
  useEffect(() => {
    loadRecurringOrders();
    loadClients();
  }, [filter]);

  const loadRecurringOrders = async () => {
    try {
      setIsLoading(true);
      const params: any = {};
      if (filter === 'active') params.is_active = true;
      if (filter === 'inactive') params.is_active = false;

      const response = await recurringOrdersAPI.getAll(params);
      setRecurringOrders(response.items);
    } catch (error) {
      console.error('정기 주문 로드 실패:', error);
      toast.error('정기 주문 목록을 불러올 수 없습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const loadClients = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/clients/`, {
        params: { is_active: true },
      });
      setClients(response.data.items || []);
    } catch (error) {
      console.error('거래처 로드 실패:', error);
    }
  };

  const handleCreate = async (data: RecurringOrderCreate) => {
    try {
      setIsLoading(true);
      await recurringOrdersAPI.create(data);
      toast.success('정기 주문이 생성되었습니다');
      setShowForm(false);
      loadRecurringOrders();
    } catch (error: any) {
      console.error('정기 주문 생성 실패:', error);
      toast.error(error.response?.data?.detail || '정기 주문 생성에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async (data: RecurringOrderCreate) => {
    if (!editingOrder) return;

    try {
      setIsLoading(true);
      await recurringOrdersAPI.update(editingOrder.id, data);
      toast.success('정기 주문이 수정되었습니다');
      setEditingOrder(null);
      setShowForm(false);
      loadRecurringOrders();
    } catch (error: any) {
      console.error('정기 주문 수정 실패:', error);
      toast.error(error.response?.data?.detail || '정기 주문 수정에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setIsLoading(true);
      await recurringOrdersAPI.delete(id);
      toast.success('정기 주문이 삭제되었습니다');
      loadRecurringOrders();
    } catch (error: any) {
      console.error('정기 주문 삭제 실패:', error);
      toast.error(error.response?.data?.detail || '정기 주문 삭제에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (id: number) => {
    try {
      setIsLoading(true);
      await recurringOrdersAPI.toggle(id);
      toast.success('정기 주문 상태가 변경되었습니다');
      loadRecurringOrders();
    } catch (error: any) {
      console.error('정기 주문 토글 실패:', error);
      toast.error(error.response?.data?.detail || '상태 변경에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (order: RecurringOrder) => {
    setEditingOrder(order);
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingOrder(null);
  };

  const handleGenerateNow = async () => {
    if (!window.confirm('오늘 생성될 정기 주문들을 즉시 생성하시겠습니까?')) {
      return;
    }

    try {
      setIsLoading(true);
      const result = await recurringOrdersAPI.generate();
      toast.success(`${result.generated}개의 주문이 생성되었습니다`);
      if (result.failed > 0) {
        toast.error(`${result.failed}개의 주문 생성에 실패했습니다`);
      }
    } catch (error: any) {
      console.error('주문 생성 실패:', error);
      toast.error(error.response?.data?.detail || '주문 생성에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">정기 주문 관리</h1>
        <p className="text-gray-600">
          자동으로 반복 생성될 주문을 관리합니다. 매일 오전 6시에 자동 실행됩니다.
        </p>
      </div>

      {/* Actions Bar */}
      {!showForm && (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          {/* Filter */}
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              전체 ({recurringOrders.length})
            </button>
            <button
              onClick={() => setFilter('active')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'active'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              활성
            </button>
            <button
              onClick={() => setFilter('inactive')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'inactive'
                  ? 'bg-gray-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              비활성
            </button>
          </div>

          {/* Buttons */}
          <div className="flex gap-2">
            <button
              onClick={handleGenerateNow}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              즉시 생성
            </button>
            <button
              onClick={() => {
                setEditingOrder(null);
                setShowForm(true);
              }}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              정기 주문 생성
            </button>
          </div>
        </div>
      )}

      {/* Form */}
      {showForm && (
        <div className="mb-8">
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">
              {editingOrder ? '정기 주문 수정' : '새 정기 주문 생성'}
            </h2>
            <RecurringOrderForm
              initialData={editingOrder || undefined}
              clients={clients}
              onSubmit={editingOrder ? handleUpdate : handleCreate}
              onCancel={handleCancel}
              isLoading={isLoading}
            />
          </div>
        </div>
      )}

      {/* Table */}
      {!showForm && (
        <>
          {isLoading && recurringOrders.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              <p className="mt-4 text-gray-600">로딩 중...</p>
            </div>
          ) : (
            <RecurringOrderTable
              orders={recurringOrders}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onToggle={handleToggle}
              isLoading={isLoading}
            />
          )}
        </>
      )}

      {/* Info Box */}
      {!showForm && recurringOrders.length > 0 && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-blue-900">자동 생성 안내</h4>
              <p className="text-sm text-blue-700 mt-1">
                정기 주문은 <strong>매일 오전 6시</strong>에 자동으로 실행됩니다.
                "즉시 생성" 버튼으로 수동 실행도 가능합니다.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
    </Layout>
  );
};

export default RecurringOrdersPage;
