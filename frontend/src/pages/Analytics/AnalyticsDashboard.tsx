/**
 * Analytics Dashboard Page
 * 배차 이력 분석 대시보드
 */
import React, { useState, useEffect } from 'react';
import { format, subDays, startOfWeek, endOfWeek, startOfMonth, endOfMonth } from 'date-fns';
import {
  getDispatchStatistics,
  getVehicleAnalytics,
  getClientAnalytics,
  getDashboardSummary,
  getQuickStats,
} from '../../services/analyticsService';
import StatisticsCards from './StatisticsCards';
import DispatchChart from './DispatchChart';
import VehiclePerformanceChart from './VehiclePerformanceChart';
import ClientDistributionChart from './ClientDistributionChart';
import DateRangeFilter from './DateRangeFilter';
import './AnalyticsDashboard.css';

const AnalyticsDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    startDate: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd'),
  });
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  
  // Data states
  const [summary, setSummary] = useState<any>(null);
  const [dispatchStats, setDispatchStats] = useState<any>(null);
  const [vehicleAnalytics, setVehicleAnalytics] = useState<any>(null);
  const [clientAnalytics, setClientAnalytics] = useState<any>(null);

  // Load all data
  const loadData = async () => {
    try {
      setLoading(true);
      
      const [summaryData, dispatchData, vehicleData, clientData] = await Promise.all([
        getDashboardSummary(),
        getDispatchStatistics(dateRange.startDate, dateRange.endDate, period),
        getVehicleAnalytics(dateRange.startDate, dateRange.endDate),
        getClientAnalytics(dateRange.startDate, dateRange.endDate),
      ]);
      
      setSummary(summaryData);
      setDispatchStats(dispatchData);
      setVehicleAnalytics(vehicleData);
      setClientAnalytics(clientData);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadData();
  }, []);

  // Reload on date range or period change
  useEffect(() => {
    loadData();
  }, [dateRange, period]);

  // Quick date range shortcuts
  const setQuickRange = (type: 'today' | 'week' | 'month' | 'last30') => {
    const today = new Date();
    let start: Date;
    let end: Date = today;

    switch (type) {
      case 'today':
        start = today;
        break;
      case 'week':
        start = startOfWeek(today, { weekStartsOn: 1 });
        end = endOfWeek(today, { weekStartsOn: 1 });
        break;
      case 'month':
        start = startOfMonth(today);
        end = endOfMonth(today);
        break;
      case 'last30':
        start = subDays(today, 30);
        break;
      default:
        start = subDays(today, 7);
    }

    setDateRange({
      startDate: format(start, 'yyyy-MM-dd'),
      endDate: format(end, 'yyyy-MM-dd'),
    });
  };

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="loading">
          <div className="spinner"></div>
          <p>데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>📊 배차 이력 분석 대시보드</h1>
        <p>데이터 기반 배차 운영 최적화</p>
      </div>

      {/* Date Range Filter */}
      <DateRangeFilter
        dateRange={dateRange}
        setDateRange={setDateRange}
        period={period}
        setPeriod={setPeriod}
        setQuickRange={setQuickRange}
      />

      {/* Statistics Cards */}
      {summary && <StatisticsCards summary={summary} />}

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Dispatch Statistics Chart */}
        {dispatchStats && (
          <div className="chart-container">
            <h2>📈 배차 통계</h2>
            <DispatchChart data={dispatchStats} period={period} />
          </div>
        )}

        {/* Vehicle Performance Chart */}
        {vehicleAnalytics && (
          <div className="chart-container">
            <h2>🚛 차량별 운행 성과</h2>
            <VehiclePerformanceChart data={vehicleAnalytics} />
          </div>
        )}

        {/* Client Distribution Chart */}
        {clientAnalytics && (
          <div className="chart-container">
            <h2>📦 거래처별 배송 분포</h2>
            <ClientDistributionChart data={clientAnalytics} />
          </div>
        )}
      </div>

      {/* Summary Stats */}
      {dispatchStats && (
        <div className="summary-section">
          <h2>📊 기간 요약</h2>
          <div className="summary-grid">
            <div className="summary-card">
              <span className="label">총 배차</span>
              <span className="value">{dispatchStats.summary.total_dispatches} 건</span>
            </div>
            <div className="summary-card">
              <span className="label">총 주문</span>
              <span className="value">{dispatchStats.summary.total_orders} 건</span>
            </div>
            <div className="summary-card">
              <span className="label">총 팔레트</span>
              <span className="value">{dispatchStats.summary.total_pallets} PLT</span>
            </div>
            <div className="summary-card">
              <span className="label">총 주행 거리</span>
              <span className="value">
                {dispatchStats.summary.total_distance_km?.toFixed(1)} km
              </span>
            </div>
            <div className="summary-card">
              <span className="label">일평균 배차</span>
              <span className="value">
                {dispatchStats.summary.avg_dispatches_per_day?.toFixed(1)} 건
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
