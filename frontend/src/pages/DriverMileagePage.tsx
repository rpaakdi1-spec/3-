import React, { useState, useEffect } from 'react';
import { format, subDays, startOfWeek, endOfWeek, startOfMonth, endOfMonth } from 'date-fns';
import { ko } from 'date-fns/locale';
import toast from 'react-hot-toast';
import { api } from '../services/api';

interface DriverMileage {
  driver_name: string;
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
  vehicle_count: number;
  vehicle_ids: string;
  calculation_method: string;
}

interface DailySummary {
  date: string;
  count: number;
  mileages: DriverMileage[];
}

interface WeeklySummary {
  driver_name: string;
  total_distance_km: number;
  total_driving_hours: number;
  avg_speed_kmh: number;
  max_speed_kmh: number;
  driving_days: number;
  avg_distance_per_day: number;
}

interface MonthlySummary {
  driver_name: string;
  total_distance_km: number;
  total_driving_hours: number;
  total_idle_hours: number;
  avg_speed_kmh: number;
  max_speed_kmh: number;
  driving_days: number;
  avg_distance_per_day: number;
}

const DriverMileagePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [selectedDate, setSelectedDate] = useState(format(subDays(new Date(), 1), 'yyyy-MM-dd'));
  const [selectedMonth, setSelectedMonth] = useState(format(new Date(), 'yyyy-MM'));
  const [searchQuery, setSearchQuery] = useState('');
  
  const [dailyData, setDailyData] = useState<DailySummary | null>(null);
  const [weeklyData, setWeeklyData] = useState<WeeklySummary[]>([]);
  const [monthlyData, setMonthlyData] = useState<MonthlySummary[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);

  // API 기본 URL
  const API_BASE_URL = '';

  // 일별 데이터 조회
  const fetchDailyData = async (date: string, driverName?: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ target_date: date });
      if (driverName) {
        params.append('driver_name', driverName);
      }
      
      const response = await api.get(`${API_BASE_URL}/driver-mileage/daily?${params}`);
      setDailyData(response.data);
    } catch (error: any) {
      console.error('일별 데이터 조회 실패:', error);
      toast.error(`일별 데이터 조회 실패: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 주간 데이터 조회
  const fetchWeeklyData = async () => {
    setLoading(true);
    try {
      const response = await api.get(`${API_BASE_URL}/driver-mileage/weekly`);
      setWeeklyData(response.data.summary || []);
    } catch (error: any) {
      console.error('주간 데이터 조회 실패:', error);
      toast.error(`주간 데이터 조회 실패: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 월간 데이터 조회
  const fetchMonthlyData = async (yearMonth: string) => {
    setLoading(true);
    try {
      const [year, month] = yearMonth.split('-');
      const response = await api.get(`${API_BASE_URL}/driver-mileage/monthly?year=${year}&month=${month}`);
      setMonthlyData(response.data.summary || []);
    } catch (error: any) {
      console.error('월간 데이터 조회 실패:', error);
      toast.error(`월간 데이터 조회 실패: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 주행거리 재계산
  const handleRecalculate = async () => {
    if (!confirm(`${selectedDate} 날짜의 운전자별 주행거리를 재계산하시겠습니까?`)) {
      return;
    }

    setCalculating(true);
    try {
      const response = await api.post(`${API_BASE_URL}/driver-mileage/calculate?target_date=${selectedDate}`);
      toast.success(response.data.message || '주행거리 재계산 완료');
      fetchDailyData(selectedDate, searchQuery);
    } catch (error: any) {
      console.error('재계산 실패:', error);
      toast.error(`재계산 실패: ${error.response?.data?.detail || error.message}`);
    } finally {
      setCalculating(false);
    }
  };

  // 탭 변경 시 데이터 로드
  useEffect(() => {
    if (activeTab === 'daily') {
      fetchDailyData(selectedDate, searchQuery);
    } else if (activeTab === 'weekly') {
      fetchWeeklyData();
    } else if (activeTab === 'monthly') {
      fetchMonthlyData(selectedMonth);
    }
  }, [activeTab, selectedDate, selectedMonth]);

  // 검색 처리
  const handleSearch = () => {
    if (activeTab === 'daily') {
      fetchDailyData(selectedDate, searchQuery);
    }
  };

  // 시간 포맷팅
  const formatTime = (timeStr: string | null) => {
    if (!timeStr) return '-';
    return format(new Date(timeStr), 'HH:mm', { locale: ko });
  };

  // 분을 시간으로 변환
  const minutesToHours = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}시간 ${mins}분`;
  };

  // Excel 다운로드
  const downloadExcel = async (type: 'daily' | 'weekly' | 'monthly') => {
    try {
      let url = '';
      let filename = '';
      
      if (type === 'daily') {
        url = `${API_BASE_URL}/driver-mileage/export/daily?target_date=${selectedDate}`;
        if (searchQuery) url += `&driver_name=${encodeURIComponent(searchQuery)}`;
        filename = `driver_mileage_daily_${selectedDate.replace(/-/g, '')}.xlsx`;
      } else if (type === 'weekly') {
        url = `${API_BASE_URL}/driver-mileage/export/weekly?end_date=${selectedDate}`;
        if (searchQuery) url += `&driver_name=${encodeURIComponent(searchQuery)}`;
        filename = `driver_mileage_weekly_${selectedDate.replace(/-/g, '')}.xlsx`;
      } else if (type === 'monthly') {
        const [year, month] = selectedMonth.split('-');
        url = `${API_BASE_URL}/driver-mileage/export/monthly?year=${year}&month=${month}`;
        if (searchQuery) url += `&driver_name=${encodeURIComponent(searchQuery)}`;
        filename = `driver_mileage_monthly_${selectedMonth.replace(/-/g, '')}.xlsx`;
      }

      const response = await api.get(url, { responseType: 'blob' });
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(link.href);
      
      toast.success('Excel 파일 다운로드 완료');
    } catch (error: any) {
      console.error('Excel 다운로드 실패:', error);
      toast.error(`Excel 다운로드 실패: ${error.response?.data?.detail || error.message}`);
    }
  };

  // PDF 다운로드
  const downloadPDF = async (type: 'monthly' | 'annual') => {
    try {
      let url = '';
      let filename = '';
      
      if (type === 'monthly') {
        const [year, month] = selectedMonth.split('-');
        url = `${API_BASE_URL}/driver-mileage/export/pdf/monthly?year=${year}&month=${month}`;
        if (searchQuery) url += `&driver_name=${encodeURIComponent(searchQuery)}`;
        filename = `driver_mileage_monthly_${selectedMonth.replace(/-/g, '')}.pdf`;
      } else if (type === 'annual') {
        const year = selectedMonth.split('-')[0];
        url = `${API_BASE_URL}/driver-mileage/export/pdf/annual?year=${year}`;
        if (searchQuery) url += `&driver_name=${encodeURIComponent(searchQuery)}`;
        filename = `driver_mileage_annual_${year}.pdf`;
      }

      const response = await api.get(url, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(link.href);
      
      toast.success('PDF 파일 다운로드 완료');
    } catch (error: any) {
      console.error('PDF 다운로드 실패:', error);
      toast.error(`PDF 다운로드 실패: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">운전자별 주행거리 관리</h1>
        <p className="mt-2 text-gray-600">차량 기반 운전자별 주행거리 통계 및 이력</p>
      </div>

      {/* 탭 메뉴 */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('daily')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'daily'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            일별 조회
          </button>
          <button
            onClick={() => setActiveTab('weekly')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'weekly'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            주간 통계
          </button>
          <button
            onClick={() => setActiveTab('monthly')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'monthly'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            월간 통계
          </button>
        </nav>
      </div>

      {/* 일별 조회 */}
      {activeTab === 'daily' && (
        <div className="space-y-6">
          {/* 필터 및 액션 */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  조회 날짜
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  운전자 검색
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="운전자명 입력"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {loading ? '조회 중...' : '조회'}
                </button>
                
                <button
                  onClick={handleRecalculate}
                  disabled={calculating}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {calculating ? '계산 중...' : '재계산'}
                </button>
                
                <button
                  onClick={() => downloadExcel('daily')}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700"
                >
                  📊 Excel 다운로드
                </button>
              </div>
            </div>
          </div>

          {/* 통계 카드 */}
          {dailyData && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600">총 운전자 수</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {dailyData.count}명
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600">총 주행거리</div>
                <div className="text-2xl font-bold text-blue-600 mt-1">
                  {dailyData.mileages.reduce((sum, m) => sum + m.total_distance_km, 0).toFixed(2)} km
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600">평균 주행거리</div>
                <div className="text-2xl font-bold text-green-600 mt-1">
                  {(dailyData.mileages.reduce((sum, m) => sum + m.total_distance_km, 0) / (dailyData.count || 1)).toFixed(2)} km
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600">총 차량 수</div>
                <div className="text-2xl font-bold text-purple-600 mt-1">
                  {dailyData.mileages.reduce((sum, m) => sum + m.vehicle_count, 0)}대
                </div>
              </div>
            </div>
          )}

          {/* 데이터 테이블 */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      순위
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      운전자명
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      주행거리
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      주행시간
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      차량수
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      평균속도
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      최고속도
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      운행시간
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                        로딩 중...
                      </td>
                    </tr>
                  ) : dailyData && dailyData.mileages.length > 0 ? (
                    dailyData.mileages.map((mileage, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {index === 0 && '🥇'}
                          {index === 1 && '🥈'}
                          {index === 2 && '🥉'}
                          {index > 2 && `${index + 1}위`}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {mileage.driver_name}
                          </div>
                          <div className="text-xs text-gray-500">
                            차량 ID: {mileage.vehicle_ids}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                          <span className="font-semibold text-blue-600">
                            {mileage.total_distance_km.toFixed(2)} km
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {minutesToHours(mileage.total_driving_minutes)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            mileage.vehicle_count > 1 
                              ? 'bg-purple-100 text-purple-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {mileage.vehicle_count}대
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {mileage.avg_speed_kmh.toFixed(1)} km/h
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {mileage.max_speed_kmh.toFixed(1)} km/h
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatTime(mileage.start_time)} ~ {formatTime(mileage.end_time)}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                        데이터가 없습니다
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 주간 통계 */}
      {activeTab === 'weekly' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                최근 7일 주행 통계
              </h3>
              <button
                onClick={() => downloadExcel('weekly')}
                className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700"
              >
                📊 Excel 다운로드
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">운전자명</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">총 주행거리</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">총 주행시간</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">운행일수</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">일평균 거리</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">평균속도</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                        로딩 중...
                      </td>
                    </tr>
                  ) : weeklyData.length > 0 ? (
                    weeklyData.map((data, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {data.driver_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-blue-600 font-semibold">
                          {data.total_distance_km.toFixed(2)} km
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {data.total_driving_hours.toFixed(1)} 시간
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {data.driving_days}일
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-green-600">
                          {data.avg_distance_per_day.toFixed(2)} km
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {data.avg_speed_kmh.toFixed(1)} km/h
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                        데이터가 없습니다
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 월간 통계 */}
      {activeTab === 'monthly' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
              <h3 className="text-lg font-semibold text-gray-900">월간 주행 통계</h3>
              <div className="flex gap-2 items-center">
                <input
                  type="month"
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={() => downloadExcel('monthly')}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 whitespace-nowrap"
                >
                  📊 Excel
                </button>
                <button
                  onClick={() => downloadPDF('monthly')}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 whitespace-nowrap"
                >
                  📄 PDF
                </button>
                <button
                  onClick={() => downloadPDF('annual')}
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 whitespace-nowrap"
                >
                  📑 연간 PDF
                </button>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">운전자명</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">총 주행거리</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">주행시간</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">유휴시간</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">운행일수</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">일평균</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">평균속도</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                        로딩 중...
                      </td>
                    </tr>
                  ) : monthlyData.length > 0 ? (
                    monthlyData.map((data, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {data.driver_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-blue-600 font-semibold">
                          {data.total_distance_km.toFixed(2)} km
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {data.total_driving_hours.toFixed(1)} 시간
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-orange-600">
                          {data.total_idle_hours.toFixed(1)} 시간
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {data.driving_days}일
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-green-600">
                          {data.avg_distance_per_day.toFixed(2)} km
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {data.avg_speed_kmh.toFixed(1)} km/h
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                        데이터가 없습니다
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DriverMileagePage;
