import React from 'react';
import type { RecurringOrder, RecurringFrequency } from '../../types';

interface RecurringOrderTableProps {
  orders: RecurringOrder[];
  onEdit: (order: RecurringOrder) => void;
  onDelete: (id: number) => void;
  onToggle: (id: number) => void;
  isLoading?: boolean;
}

const FREQUENCY_LABELS: Record<RecurringFrequency, string> = {
  DAILY: '매일',
  WEEKLY: '매주',
  MONTHLY: '매월',
  CUSTOM: '사용자 지정',
};

const WEEKDAY_LABELS = ['월', '화', '수', '목', '금', '토', '일'];

const getWeekdayLabels = (weekdays: number): string => {
  const days: string[] = [];
  WEEKDAY_LABELS.forEach((label, index) => {
    if ((weekdays & (1 << index)) !== 0) {
      days.push(label);
    }
  });
  return days.join(', ');
};

export const RecurringOrderTable: React.FC<RecurringOrderTableProps> = ({
  orders,
  onEdit,
  onDelete,
  onToggle,
  isLoading = false,
}) => {
  if (orders.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">정기 주문 없음</h3>
        <p className="mt-1 text-sm text-gray-500">새로운 정기 주문을 생성해보세요</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                상태
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                정기 주문 이름
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                주기
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                경로
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                시작일/종료일
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                마지막 생성
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                작업
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {orders.map((order) => (
              <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                {/* 상태 */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => onToggle(order.id)}
                    disabled={isLoading}
                    className="flex items-center gap-2 disabled:opacity-50"
                  >
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        order.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {order.is_active ? '활성' : '비활성'}
                    </span>
                  </button>
                </td>

                {/* 이름 */}
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{order.name}</div>
                  <div className="text-sm text-gray-500">
                    {order.temperature_zone} · {order.pallet_count}팔레트
                  </div>
                </td>

                {/* 주기 */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {FREQUENCY_LABELS[order.frequency]}
                  </div>
                  {order.frequency === 'WEEKLY' && (
                    <div className="text-xs text-gray-500">
                      {getWeekdayLabels(order.weekdays)}
                    </div>
                  )}
                  {(order.frequency === 'MONTHLY' || order.frequency === 'CUSTOM') &&
                    order.custom_days && (
                      <div className="text-xs text-gray-500 font-mono">
                        {order.custom_days}
                      </div>
                    )}
                </td>

                {/* 경로 */}
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">
                    {order.pickup_client_name || order.pickup_address || '미정'}
                  </div>
                  <div className="text-xs text-gray-400">→</div>
                  <div className="text-sm text-gray-900">
                    {order.delivery_client_name || order.delivery_address || '미정'}
                  </div>
                </td>

                {/* 기간 */}
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div>{order.start_date}</div>
                  {order.end_date && <div>~ {order.end_date}</div>}
                </td>

                {/* 마지막 생성 */}
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {order.last_generated_date || '없음'}
                </td>

                {/* 작업 */}
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => onEdit(order)}
                      disabled={isLoading}
                      className="text-indigo-600 hover:text-indigo-900 disabled:opacity-50"
                      title="수정"
                    >
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        />
                      </svg>
                    </button>
                    <button
                      onClick={() => {
                        if (
                          window.confirm(
                            `"${order.name}" 정기 주문을 삭제하시겠습니까?`
                          )
                        ) {
                          onDelete(order.id);
                        }
                      }}
                      disabled={isLoading}
                      className="text-red-600 hover:text-red-900 disabled:opacity-50"
                      title="삭제"
                    >
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RecurringOrderTable;
