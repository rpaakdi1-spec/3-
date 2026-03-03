import React, { useState, useEffect } from 'react';
import { RefreshCw, TrendingUp, Clock, Gauge, Fuel, Calendar, Car, ChevronDown, ChevronUp, Truck } from 'lucide-react';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';
import toast from 'react-hot-toast';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import { vehicleMileageAPI } from '../services/api';

interface DailyMileage {
  vehicle_id: number;
  vehicle_code: string;
  plate_number: string;
  date: string;
  total_distance_km: number;
  total_driving_minutes: number;
  engine_on_minutes: number;
  idle_minutes: number;
  max_speed_kmh: number;
  avg_speed_kmh: number;
  gps_point_count: number;
  start_time: string | null;
  end_time: string | null;
  calculation_method: string;
}

interface MileageSummary {
  vehicle_id: number;
  vehicle_code: string;
  plate_number: string;
  total_distance_km: number;
  total_driving_minutes?: number;
  total_driving_hours?: number;
  total_idle_minutes?: number;
  avg_speed_kmh: number;
  max_speed_kmh: number;
  driving_days: number;
  avg_distance_per_day: number;
}

interface Statistics {
  vehicle_count: number;
  total_distance_km: number;
  total_driving_hours: number;
  avg_speed_kmh: number;
  record_count: number;
}

const VehicleMileagePage: React.FC = () => {
  const [tabValue, setTabValue] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [selectedDate, setSelectedDate] = useState<string>(format(subDays(new Date(), 1), 'yyyy-MM-dd'));
  const [selectedMonth, setSelectedMonth] = useState<string>(format(new Date(), 'yyyy-MM'));
  
  const [dailyMileages, setDailyMileages] = useState<DailyMileage[]>([]);
  const [weeklySummary, setWeeklySummary] = useState<MileageSummary[]>([]);
  const [monthlySummary, setMonthlySummary] = useState<MileageSummary[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  
  const [loading, setLoading] = useState(false);

  // 일별 주행거리 조회
  const fetchDailyMileages = async (date: string) => {
    setLoading(true);
    try {
      const response = await vehicleMileageAPI.getDaily(date);
      setDailyMileages(response.data.mileages || []);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || '일별 주행거리 조회 실패');
      console.error('Failed to fetch daily mileages:', err);
    } finally {
      setLoading(false);
    }
  };

  // 주간 주행거리 조회
  const fetchWeeklySummary = async () => {
    setLoading(true);
    try {
      const response = await vehicleMileageAPI.getWeekly();
      setWeeklySummary(response.data.summary || []);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || '주간 주행거리 조회 실패');
      console.error('Failed to fetch weekly summary:', err);
    } finally {
      setLoading(false);
    }
  };

  // 월별 주행거리 조회
  const fetchMonthlySummary = async (yearMonth: string) => {
    setLoading(true);
    try {
      const [year, month] = yearMonth.split('-').map(Number);
      const response = await vehicleMileageAPI.getMonthly(year, month);
      setMonthlySummary(response.data.summary || []);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || '월별 주행거리 조회 실패');
      console.error('Failed to fetch monthly summary:', err);
    } finally {
      setLoading(false);
    }
  };

  // 통계 조회
  const fetchStatistics = async (startDate: string, endDate: string) => {
    try {
      const response = await vehicleMileageAPI.getStatistics(startDate, endDate);
      setStatistics(response.data || null);
    } catch (err: any) {
      console.error('Failed to fetch statistics:', err);
    }
  };

  // 주행거리 재계산 (어제 날짜)
  const handleRecalculate = async () => {
    const yesterday = format(subDays(new Date(), 1), 'yyyy-MM-dd');
    setLoading(true);
    try {
      await vehicleMileageAPI.calculate(yesterday);
      toast.success('주행거리 재계산 완료');
      fetchDailyMileages(selectedDate);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || '재계산 실패');
      console.error('Failed to recalculate:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleRow = (vehicleId: number) => {
    setExpandedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(vehicleId)) {
        newSet.delete(vehicleId);
      } else {
        newSet.add(vehicleId);
      }
      return newSet;
    });
  };

  // 탭 변경 시
  useEffect(() => {
    if (tabValue === 'daily') {
      fetchDailyMileages(selectedDate);
      fetchStatistics(selectedDate, selectedDate);
    } else if (tabValue === 'weekly') {
      fetchWeeklySummary();
      const weekStart = format(subDays(new Date(), 7), 'yyyy-MM-dd');
      const today = format(new Date(), 'yyyy-MM-dd');
      fetchStatistics(weekStart, today);
    } else if (tabValue === 'monthly') {
      fetchMonthlySummary(selectedMonth);
      const [year, month] = selectedMonth.split('-').map(Number);
      const monthStart = format(startOfMonth(new Date(year, month - 1)), 'yyyy-MM-dd');
      const monthEnd = format(endOfMonth(new Date(year, month - 1)), 'yyyy-MM-dd');
      fetchStatistics(monthStart, monthEnd);
    }
  }, [tabValue, selectedDate, selectedMonth]);

  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto">
      {/* 헤더 */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <div className="flex items-center gap-3 mb-4 md:mb-0">
          <Car className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl md:text-3xl font-bold text-gray-800">주행거리 관리</h1>
        </div>
        <Button
          onClick={handleRecalculate}
          variant="primary"
          icon={<RefreshCw className="h-4 w-4" />}
          disabled={loading}
        >
          어제 주행거리 재계산
        </Button>
      </div>

      {/* 통계 카드 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 font-medium mb-1">운행 차량</p>
                <p className="text-2xl font-bold text-blue-700">{statistics?.vehicle_count || 0}대</p>
              </div>
              <Truck className="h-10 w-10 text-blue-500 opacity-70" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600 font-medium mb-1">총 주행거리</p>
                <p className="text-2xl font-bold text-green-700">{statistics?.total_distance_km?.toFixed(1) || '0.0'} km</p>
              </div>
              <TrendingUp className="h-10 w-10 text-green-500 opacity-70" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-orange-600 font-medium mb-1">총 운행시간</p>
                <p className="text-2xl font-bold text-orange-700">{statistics?.total_driving_hours?.toFixed(1) || '0.0'}시간</p>
              </div>
              <Clock className="h-10 w-10 text-orange-500 opacity-70" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 font-medium mb-1">평균 속도</p>
                <p className="text-2xl font-bold text-purple-700">{statistics?.avg_speed_kmh?.toFixed(1) || '0.0'} km/h</p>
              </div>
              <Gauge className="h-10 w-10 text-purple-500 opacity-70" />
            </div>
          </Card>
        </div>
      )}

      {/* 탭 네비게이션 */}
      <Card className="mb-6">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setTabValue('daily')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              tabValue === 'daily'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            일별 조회
          </button>
          <button
            onClick={() => setTabValue('weekly')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              tabValue === 'weekly'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            주간 통계 (최근 7일)
          </button>
          <button
            onClick={() => setTabValue('monthly')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              tabValue === 'monthly'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
            }`}
          >
            월별 통계
          </button>
        </div>

        <div className="p-4">
          {/* 일별 조회 탭 */}
          {tabValue === 'daily' && (
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">날짜 선택</label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {loading ? (
                <Loading />
              ) : dailyMileages.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>해당 날짜에 주행 기록이 없습니다.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          차량번호
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          주행거리
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          운행시간
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          평균속도
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          최고속도
                        </th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          상세
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {dailyMileages.map((mileage) => (
                        <React.Fragment key={mileage.vehicle_id}>
                          <tr className="hover:bg-gray-50 transition-colors">
                            <td className="px-4 py-3 whitespace-nowrap">
                              <div className="flex items-center">
                                <Truck className="h-4 w-4 text-gray-400 mr-2" />
                                <span className="font-medium text-gray-900">{mileage.plate_number}</span>
                              </div>
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-right">
                              <span className="text-sm font-semibold text-blue-600">
                                {mileage.total_distance_km.toFixed(1)} km
                              </span>
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-right">
                              <span className="text-sm text-gray-900">
                                {(mileage.total_driving_minutes / 60).toFixed(1)}시간
                              </span>
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-right">
                              <span className="text-sm text-gray-900">{mileage.avg_speed_kmh.toFixed(1)} km/h</span>
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-right">
                              <span className="text-sm text-gray-900">{mileage.max_speed_kmh.toFixed(1)} km/h</span>
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-center">
                              <button
                                onClick={() => toggleRow(mileage.vehicle_id)}
                                className="text-blue-600 hover:text-blue-800 transition-colors"
                              >
                                {expandedRows.has(mileage.vehicle_id) ? (
                                  <ChevronUp className="h-5 w-5" />
                                ) : (
                                  <ChevronDown className="h-5 w-5" />
                                )}
                              </button>
                            </td>
                          </tr>
                          {expandedRows.has(mileage.vehicle_id) && (
                            <tr className="bg-gray-50">
                              <td colSpan={6} className="px-4 py-4">
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                  <div>
                                    <p className="text-xs text-gray-500 mb-1">엔진 가동시간</p>
                                    <p className="text-sm font-medium text-gray-900">
                                      {(mileage.engine_on_minutes / 60).toFixed(1)}시간
                                    </p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500 mb-1">공회전 시간</p>
                                    <p className="text-sm font-medium text-gray-900">
                                      {(mileage.idle_minutes / 60).toFixed(1)}시간
                                    </p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500 mb-1">GPS 수집 수</p>
                                    <p className="text-sm font-medium text-gray-900">{mileage.gps_point_count}개</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500 mb-1">계산 방법</p>
                                    <p className="text-sm font-medium text-gray-900">{mileage.calculation_method}</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500 mb-1">운행 시작</p>
                                    <p className="text-sm font-medium text-gray-900">
                                      {mileage.start_time ? format(new Date(mileage.start_time), 'HH:mm') : '-'}
                                    </p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-500 mb-1">운행 종료</p>
                                    <p className="text-sm font-medium text-gray-900">
                                      {mileage.end_time ? format(new Date(mileage.end_time), 'HH:mm') : '-'}
                                    </p>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* 주간 통계 탭 */}
          {tabValue === 'weekly' && (
            <div>
              {loading ? (
                <Loading />
              ) : weeklySummary.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>최근 7일간 주행 기록이 없습니다.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          차량번호
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          총 주행거리
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          운행일수
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          일평균
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          평균속도
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          최고속도
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {weeklySummary.map((summary) => (
                        <tr key={summary.vehicle_id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="flex items-center">
                              <Truck className="h-4 w-4 text-gray-400 mr-2" />
                              <span className="font-medium text-gray-900">{summary.plate_number}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm font-semibold text-blue-600">
                              {summary.total_distance_km.toFixed(1)} km
                            </span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm text-gray-900">{summary.driving_days}일</span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm text-gray-900">{summary.avg_distance_per_day.toFixed(1)} km/일</span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm text-gray-900">{summary.avg_speed_kmh.toFixed(1)} km/h</span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm text-gray-900">{summary.max_speed_kmh.toFixed(1)} km/h</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* 월별 통계 탭 */}
          {tabValue === 'monthly' && (
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">월 선택</label>
                <input
                  type="month"
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {loading ? (
                <Loading />
              ) : monthlySummary.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>해당 월에 주행 기록이 없습니다.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          차량번호
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          총 주행거리
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          운행일수
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          일평균
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          총 운행시간
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          평균속도
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {monthlySummary.map((summary) => (
                        <tr key={summary.vehicle_id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="flex items-center">
                              <Truck className="h-4 w-4 text-gray-400 mr-2" />
                              <span className="font-medium text-gray-900">{summary.plate_number}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm font-semibold text-blue-600">
                              {summary.total_distance_km.toFixed(1)} km
                            </span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm text-gray-900">{summary.driving_days}일</span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm text-gray-900">{summary.avg_distance_per_day.toFixed(1)} km/일</span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm text-gray-900">
                              {summary.total_driving_hours?.toFixed(1) || '-'}시간
                            </span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right">
                            <span className="text-sm text-gray-900">{summary.avg_speed_kmh.toFixed(1)} km/h</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default VehicleMileagePage;
