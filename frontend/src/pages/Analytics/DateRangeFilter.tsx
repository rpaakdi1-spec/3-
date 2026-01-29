/**
 * Date Range Filter Component
 * 날짜 범위 필터
 */
import React from 'react';
import './DateRangeFilter.css';

interface DateRangeFilterProps {
  dateRange: {
    startDate: string;
    endDate: string;
  };
  setDateRange: (range: { startDate: string; endDate: string }) => void;
  period: 'daily' | 'weekly' | 'monthly';
  setPeriod: (period: 'daily' | 'weekly' | 'monthly') => void;
  setQuickRange: (type: 'today' | 'week' | 'month' | 'last30') => void;
}

const DateRangeFilter: React.FC<DateRangeFilterProps> = ({
  dateRange,
  setDateRange,
  period,
  setPeriod,
  setQuickRange,
}) => {
  return (
    <div className="date-range-filter">
      {/* Quick Range Buttons */}
      <div className="quick-range">
        <button onClick={() => setQuickRange('today')}>오늘</button>
        <button onClick={() => setQuickRange('week')}>이번 주</button>
        <button onClick={() => setQuickRange('month')}>이번 달</button>
        <button onClick={() => setQuickRange('last30')}>최근 30일</button>
      </div>

      {/* Date Inputs */}
      <div className="date-inputs">
        <div className="input-group">
          <label>시작 날짜</label>
          <input
            type="date"
            value={dateRange.startDate}
            onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
          />
        </div>
        <span className="separator">~</span>
        <div className="input-group">
          <label>종료 날짜</label>
          <input
            type="date"
            value={dateRange.endDate}
            onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
          />
        </div>
      </div>

      {/* Period Selector */}
      <div className="period-selector">
        <label>집계 단위</label>
        <div className="period-buttons">
          <button
            className={period === 'daily' ? 'active' : ''}
            onClick={() => setPeriod('daily')}
          >
            일별
          </button>
          <button
            className={period === 'weekly' ? 'active' : ''}
            onClick={() => setPeriod('weekly')}
          >
            주별
          </button>
          <button
            className={period === 'monthly' ? 'active' : ''}
            onClick={() => setPeriod('monthly')}
          >
            월별
          </button>
        </div>
      </div>
    </div>
  );
};

export default DateRangeFilter;
