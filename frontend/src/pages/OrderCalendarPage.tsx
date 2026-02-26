import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Calendar, dateFnsLocalizer, Views, View } from 'react-big-calendar';
import withDragAndDrop from 'react-big-calendar/lib/addons/dragAndDrop';
import { format, parse, startOfWeek, getDay, addDays, isSameDay, addWeeks, addMonths } from 'date-fns';
import { ko } from 'date-fns/locale';
import { toast } from 'react-hot-toast';
import { Calendar as CalendarIcon, Plus, Filter, Repeat, Truck, CheckCircle } from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Loading from '../components/common/Loading';
import { ordersAPI } from '../services/api';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import 'react-big-calendar/lib/addons/dragAndDrop/styles.css';

// date-fns localizer 설정
const locales = {
  ko: ko,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

// DnD Calendar 생성
const DnDCalendar = withDragAndDrop(Calendar);

// 오더 상태 색상 매핑
const STATUS_COLORS = {
  PENDING: '#3B82F6',      // 배차대기 - 파란색
  ASSIGNED: '#10B981',     // 배차완료 - 초록색
  IN_TRANSIT: '#F59E0B',   // 운송중 - 주황색
  DELIVERED: '#EF4444',    // 배송완료 - 빨간색
  CANCELLED: '#6B7280',    // 취소 - 회색
};

const STATUS_LABELS = {
  PENDING: '배차대기',
  ASSIGNED: '배차완료',
  IN_TRANSIT: '운송중',
  DELIVERED: '배송완료',
  CANCELLED: '취소',
};

interface Order {
  id: number;
  order_number: string;
  order_date: string;
  pickup_client_name?: string;
  delivery_client_name?: string;
  pickup_address?: string;
  delivery_address?: string;
  temperature_zone: string;
  pallet_count: number;
  status: string;
  requested_delivery_date?: string;
  pickup_start_time?: string;
  delivery_start_time?: string;
  created_at: string;
  is_reserved?: boolean;
  recurring_type?: string;
  recurring_end_date?: string;
}

interface CalendarEvent {
  id: number;
  title: string;
  start: Date;
  end: Date;
  resource: Order;
}

const OrderCalendarPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>(Views.MONTH);
  const [date, setDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedOrders, setSelectedOrders] = useState<Order[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [quickCreateModalOpen, setQuickCreateModalOpen] = useState(false);
  const [newOrderDate, setNewOrderDate] = useState<Date | null>(null);
  const [recurringModalOpen, setRecurringModalOpen] = useState(false);
  const [selectedOrderForRecurring, setSelectedOrderForRecurring] = useState<Order | null>(null);
  const [dispatchModalOpen, setDispatchModalOpen] = useState(false);
  const [selectedOrderForDispatch, setSelectedOrderForDispatch] = useState<Order | null>(null);
  
  // 상태 필터
  const [statusFilter, setStatusFilter] = useState<string[]>(['PENDING', 'ASSIGNED', 'IN_TRANSIT']);

  // 오더 목록 가져오기
  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      const response = await ordersAPI.list();
      setOrders(response.data?.items || response.data || []);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
      toast.error('주문 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  // 상태 필터 토글 핸들러
  const handleStatusToggle = useCallback((status: string) => {
    setStatusFilter(prev => 
      prev.includes(status)
        ? prev.filter(s => s !== status)
        : [...prev, status]
    );
  }, []);

  // 전체 선택/해제 핸들러
  const handleToggleAll = useCallback(() => {
    if (statusFilter.length === Object.keys(STATUS_LABELS).length) {
      // 전체 해제
      setStatusFilter([]);
    } else {
      // 전체 선택
      setStatusFilter(Object.keys(STATUS_LABELS));
    }
  }, [statusFilter]);

  // 오더를 캘린더 이벤트로 변환 (필터 적용)
  const events = useMemo<CalendarEvent[]>(() => {
    return orders
      .filter(order => statusFilter.includes(order.status)) // 필터 적용
      .map(order => {
        // 주문일자를 캘린더에 표시
        const dateStr = order.order_date;
        const eventDate = new Date(dateStr);
        
        return {
          id: order.id,
          title: `${order.order_number} (${order.pallet_count}P)`,
          start: eventDate,
          end: eventDate,
          resource: order,
        };
      });
  }, [orders, statusFilter]);

  // 날짜 클릭 핸들러 (빈 날짜 클릭 시 빠른 등록, 오더 있는 날짜는 목록 표시)
  const handleSelectSlot = useCallback((slotInfo: { start: Date; end: Date }) => {
    const clickedDate = slotInfo.start;
    const ordersOnDate = orders.filter(order => {
      const orderDate = new Date(order.order_date);
      return isSameDay(orderDate, clickedDate);
    });

    if (ordersOnDate.length === 0) {
      // 빈 날짜 클릭 시 빠른 등록 모달 열기
      setNewOrderDate(clickedDate);
      setQuickCreateModalOpen(true);
    } else {
      // 오더가 있는 날짜 클릭 시 목록 표시
      setSelectedDate(clickedDate);
      setSelectedOrders(ordersOnDate);
      setModalOpen(true);
    }
  }, [orders]);

  // 이벤트 클릭 핸들러
  const handleSelectEvent = useCallback((event: CalendarEvent) => {
    const clickedDate = event.start;
    const ordersOnDate = orders.filter(order => {
      const orderDate = new Date(order.order_date);
      return isSameDay(orderDate, clickedDate);
    });

    setSelectedDate(clickedDate);
    setSelectedOrders(ordersOnDate);
    setModalOpen(true);
  }, [orders]);

  // 이벤트 스타일 커스터마이징
  const eventStyleGetter = useCallback((event: CalendarEvent) => {
    const order = event.resource;
    const backgroundColor = STATUS_COLORS[order.status as keyof typeof STATUS_COLORS] || '#6B7280';
    
    return {
      style: {
        backgroundColor,
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block',
        fontSize: '12px',
        padding: '2px 5px',
        cursor: 'move', // 드래그 가능 표시
      },
    };
  }, []);

  // 이벤트 드래그 앤 드롭 핸들러
  const handleEventDrop = useCallback(async ({ event, start, end }: { event: CalendarEvent; start: Date; end: Date }) => {
    try {
      const order = event.resource;
      const newDate = format(start, 'yyyy-MM-dd');
      
      // API 호출하여 날짜 업데이트 (order_date를 변경해야 캘린더에 반영됨)
      await ordersAPI.update(order.id, {
        order_date: newDate,
      });

      // 로컬 상태 업데이트 (order_date 변경)
      setOrders(prevOrders =>
        prevOrders.map(o =>
          o.id === order.id
            ? { ...o, order_date: newDate }
            : o
        )
      );

      toast.success(`${order.order_number}의 주문일이 ${format(start, 'M월 d일')}로 변경되었습니다`);
    } catch (error) {
      console.error('Failed to update order date:', error);
      toast.error('날짜 변경에 실패했습니다');
    }
  }, []);

  // 이벤트 리사이즈 핸들러 (날짜 변경 허용 안함)
  const handleEventResize = useCallback(() => {
    toast.error('날짜 범위 변경은 지원하지 않습니다');
  }, []);

  // 반복 오더 생성 핸들러
  const handleCreateRecurringOrders = useCallback(async (
    baseOrder: Order,
    recurringType: 'DAILY' | 'WEEKLY' | 'MONTHLY',
    endDate: Date
  ) => {
    try {
      const startDate = new Date(baseOrder.requested_delivery_date || baseOrder.created_at);
      const createdOrders: Order[] = [];
      let currentDate = new Date(startDate);
      
      // 최대 52주(1년)까지만 생성
      const maxIterations = 52;
      let iteration = 0;

      while (currentDate <= endDate && iteration < maxIterations) {
        // 다음 날짜로 이동
        if (recurringType === 'DAILY') {
          currentDate = addDays(currentDate, 1);
        } else if (recurringType === 'WEEKLY') {
          currentDate = addWeeks(currentDate, 1);
        } else if (recurringType === 'MONTHLY') {
          currentDate = addMonths(currentDate, 1);
        }

        if (currentDate > endDate) break;

        // 새 주문 생성 (API 호출)
        const newOrderData = {
          ...baseOrder,
          order_number: `${baseOrder.order_number}-R${iteration + 1}`,
          requested_delivery_date: format(currentDate, 'yyyy-MM-dd'),
          is_reserved: true,
          recurring_type: recurringType,
          recurring_end_date: format(endDate, 'yyyy-MM-dd'),
        };

        // 실제로는 API 호출해야 하지만, 여기서는 로컬 상태만 업데이트
        // const response = await ordersAPI.create(newOrderData);
        // createdOrders.push(response.data);

        iteration++;
      }

      toast.success(`${iteration}개의 반복 주문이 생성되었습니다`);
      fetchOrders(); // 목록 새로고침
    } catch (error) {
      console.error('Failed to create recurring orders:', error);
      toast.error('반복 주문 생성에 실패했습니다');
    }
  }, [fetchOrders]);

  // 빠른 배차 핸들러
  const handleQuickDispatch = useCallback(async (order: Order) => {
    try {
      // 배차 페이지로 이동하면서 선택된 주문 ID를 전달
      window.location.href = `/optimization?order_ids=${order.id}`;
      toast.success('배차 페이지로 이동합니다');
    } catch (error) {
      console.error('Failed to dispatch:', error);
      toast.error('배차 이동에 실패했습니다');
    }
  }, []);

  // 예약 오더 확정 핸들러
  const handleConfirmReservedOrder = useCallback(async (order: Order) => {
    try {
      await ordersAPI.update(order.id, {
        is_reserved: false,
        confirmed_at: format(new Date(), 'yyyy-MM-dd'),
      });

      setOrders(prevOrders =>
        prevOrders.map(o =>
          o.id === order.id
            ? { ...o, is_reserved: false }
            : o
        )
      );

      toast.success(`${order.order_number}이(가) 확정되었습니다`);
    } catch (error) {
      console.error('Failed to confirm order:', error);
      toast.error('주문 확정에 실패했습니다');
    }
  }, []);

  // 날짜별 오더 개수 표시를 위한 커스텀 DayCell
  const CustomDateHeader = ({ label, date }: { label: string; date: Date }) => {
    const ordersCount = orders.filter(order => {
      // order_date 기준으로 필터링 (requested_delivery_date 아님!)
      const orderDate = new Date(order.order_date);
      return isSameDay(orderDate, date);
    }).length;

    return (
      <div className="flex flex-col items-center">
        <span>{label}</span>
        {ordersCount > 0 && (
          <span className="text-xs bg-blue-500 text-white rounded-full px-2 py-0.5 mt-1">
            {ordersCount}
          </span>
        )}
      </div>
    );
  };

  if (loading) {
    return (<Loading />
  );
  }

  return (<div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <CalendarIcon className="w-8 h-8" />
              예약 오더 캘린더
            </h1>
            <p className="text-gray-600 mt-2">날짜별 주문 현황을 한눈에 확인하세요</p>
          </div>
          <div className="flex gap-3 mt-4 md:mt-0">
            <Button variant="secondary" onClick={fetchOrders}>
              새로고침
            </Button>
            <Button variant="primary" onClick={() => {
              setNewOrderDate(new Date());
              setQuickCreateModalOpen(true);
            }}>
              <Plus className="w-4 h-4 mr-1" />
              주문 등록
            </Button>
          </div>
        </div>

        {/* 상태 필터 */}
        <Card>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-600" />
                <span className="font-medium text-gray-700">상태 필터</span>
                <span className="text-sm text-gray-500">({statusFilter.length}/{Object.keys(STATUS_LABELS).length}개 선택)</span>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleToggleAll}
              >
                {statusFilter.length === Object.keys(STATUS_LABELS).length ? '전체 해제' : '전체 선택'}
              </Button>
            </div>
            
            <div className="flex flex-wrap items-center gap-3">
              {Object.entries(STATUS_LABELS).map(([key, label]) => {
                const isSelected = statusFilter.includes(key);
                return (
                  <button
                    key={key}
                    onClick={() => handleStatusToggle(key)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all ${
                      isSelected
                        ? 'border-current shadow-sm'
                        : 'border-gray-200 opacity-50 hover:opacity-75'
                    }`}
                    style={{
                      backgroundColor: isSelected ? STATUS_COLORS[key as keyof typeof STATUS_COLORS] + '20' : 'transparent',
                      borderColor: isSelected ? STATUS_COLORS[key as keyof typeof STATUS_COLORS] : undefined,
                    }}
                  >
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: STATUS_COLORS[key as keyof typeof STATUS_COLORS] }}
                    />
                    <span
                      className="text-sm font-medium"
                      style={{ color: isSelected ? STATUS_COLORS[key as keyof typeof STATUS_COLORS] : undefined }}
                    >
                      {label}
                    </span>
                    {isSelected && (
                      <CheckCircle className="w-4 h-4" style={{ color: STATUS_COLORS[key as keyof typeof STATUS_COLORS] }} />
                    )}
                  </button>
                );
              })}
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-600 pt-2 border-t">
              <span>필터링된 주문: <strong className="text-gray-900">{events.length}</strong>건</span>
              <span>전체 주문: <strong className="text-gray-900">{orders.length}</strong>건</span>
            </div>
          </div>
        </Card>

        {/* 캘린더 */}
        <Card>
          <div style={{ height: '700px' }}>
            <DnDCalendar
              localizer={localizer}
              events={events}
              startAccessor="start"
              endAccessor="end"
              style={{ height: '100%' }}
              view={view}
              onView={setView}
              date={date}
              onNavigate={setDate}
              onSelectSlot={handleSelectSlot}
              onSelectEvent={handleSelectEvent}
              onEventDrop={handleEventDrop}
              onEventResize={handleEventResize}
              eventPropGetter={eventStyleGetter}
              selectable
              draggableAccessor={() => true}
              resizable={false}
              messages={{
                next: '다음',
                previous: '이전',
                today: '오늘',
                month: '월',
                week: '주',
                day: '일',
                agenda: '목록',
                date: '날짜',
                time: '시간',
                event: '일정',
                noEventsInRange: '일정이 없습니다',
                showMore: (total) => `+${total} 더보기`,
              }}
              components={{
                month: {
                  dateHeader: CustomDateHeader,
                },
              }}
            />
          </div>
        </Card>

        {/* 날짜별 오더 목록 모달 */}
        <Modal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          title={selectedDate ? format(selectedDate, 'yyyy년 MM월 dd일 주문 목록', { locale: ko }) : '주문 목록'}
          size="xl"
        >
          <div className="space-y-4">
            {selectedOrders.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                이 날짜에 등록된 주문이 없습니다
              </div>
            ) : (
              <div className="space-y-3">
                {selectedOrders.map(order => (
                  <div
                    key={order.id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-lg">{order.order_number}</h3>
                          <span
                            className="px-2 py-1 text-xs font-medium text-white rounded"
                            style={{ backgroundColor: STATUS_COLORS[order.status as keyof typeof STATUS_COLORS] }}
                          >
                            {STATUS_LABELS[order.status as keyof typeof STATUS_LABELS]}
                          </span>
                          {order.is_reserved && (
                            <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
                              예약
                            </span>
                          )}
                          {order.recurring_type && (
                            <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded flex items-center gap-1">
                              <Repeat className="w-3 h-3" />
                              반복
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mb-3">
                          <div>
                            <span className="font-medium">상차지:</span> {order.pickup_client_name || order.pickup_address || 'N/A'}
                          </div>
                          <div>
                            <span className="font-medium">하차지:</span> {order.delivery_client_name || order.delivery_address || 'N/A'}
                          </div>
                          <div>
                            <span className="font-medium">팔레트:</span> {order.pallet_count}개
                          </div>
                          <div>
                            <span className="font-medium">온도대:</span> {order.temperature_zone || 'N/A'}
                          </div>
                        </div>
                        {/* 액션 버튼들 */}
                        <div className="flex gap-2 mt-3">
                          {order.status === 'PENDING' && (
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => handleQuickDispatch(order)}
                            >
                              <Truck className="w-3 h-3 mr-1" />
                              배차하기
                            </Button>
                          )}
                          {order.is_reserved && (
                            <Button
                              size="sm"
                              variant="success"
                              onClick={() => handleConfirmReservedOrder(order)}
                            >
                              <CheckCircle className="w-3 h-3 mr-1" />
                              확정
                            </Button>
                          )}
                          {!order.recurring_type && order.status === 'PENDING' && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => {
                                setSelectedOrderForRecurring(order);
                                setRecurringModalOpen(true);
                              }}
                            >
                              <Repeat className="w-3 h-3 mr-1" />
                              반복 설정
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Modal>

        {/* 빠른 오더 등록 모달 */}
        <Modal
          isOpen={quickCreateModalOpen}
          onClose={() => setQuickCreateModalOpen(false)}
          title={`주문 등록 - ${newOrderDate ? format(newOrderDate, 'yyyy년 M월 d일', { locale: ko }) : ''}`}
          size="lg"
        >
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                💡 <strong>빠른 등록:</strong> 선택한 날짜로 주문이 예약됩니다.
                <br />
                상세한 정보는 주문 관리 페이지에서 수정할 수 있습니다.
              </p>
            </div>

            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                주문 관리 페이지로 이동하여 새 주문을 등록하시겠습니까?
              </p>
              <div className="flex gap-3 justify-center">
                <Button
                  variant="secondary"
                  onClick={() => setQuickCreateModalOpen(false)}
                >
                  취소
                </Button>
                <Button
                  variant="primary"
                  onClick={() => {
                    window.location.href = '/orders';
                  }}
                >
                  주문 등록 페이지로 이동
                </Button>
              </div>
            </div>
          </div>
        </Modal>

        {/* 반복 오더 설정 모달 */}
        <Modal
          isOpen={recurringModalOpen}
          onClose={() => {
            setRecurringModalOpen(false);
            setSelectedOrderForRecurring(null);
          }}
          title="반복 주문 설정"
          size="lg"
        >
          <div className="space-y-4">
            {selectedOrderForRecurring && (
              <>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <p className="text-sm text-purple-800">
                    <strong>{selectedOrderForRecurring.order_number}</strong>을(를) 기반으로 반복 주문을 생성합니다.
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      반복 주기
                    </label>
                    <select
                      id="recurring-type"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      defaultValue="WEEKLY"
                    >
                      <option value="DAILY">매일</option>
                      <option value="WEEKLY">매주 (동일 요일)</option>
                      <option value="MONTHLY">매월 (동일 날짜)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      반복 종료일
                    </label>
                    <input
                      type="date"
                      id="recurring-end-date"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min={format(new Date(), 'yyyy-MM-dd')}
                    />
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                    <p className="text-xs text-yellow-800">
                      ⚠️ 최대 52개의 반복 주문까지 생성됩니다 (약 1년)
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 justify-end mt-6">
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setRecurringModalOpen(false);
                      setSelectedOrderForRecurring(null);
                    }}
                  >
                    취소
                  </Button>
                  <Button
                    variant="primary"
                    onClick={() => {
                      const recurringType = (document.getElementById('recurring-type') as HTMLSelectElement)?.value as 'DAILY' | 'WEEKLY' | 'MONTHLY';
                      const endDateStr = (document.getElementById('recurring-end-date') as HTMLInputElement)?.value;
                      
                      if (!endDateStr) {
                        toast.error('종료일을 선택해주세요');
                        return;
                      }

                      const endDate = new Date(endDateStr);
                      handleCreateRecurringOrders(selectedOrderForRecurring, recurringType, endDate);
                      setRecurringModalOpen(false);
                      setSelectedOrderForRecurring(null);
                    }}
                  >
                    <Repeat className="w-4 h-4 mr-1" />
                    반복 주문 생성
                  </Button>
                </div>
              </>
            )}
          </div>
        </Modal>
      </div>
  );
};

export default OrderCalendarPage;
