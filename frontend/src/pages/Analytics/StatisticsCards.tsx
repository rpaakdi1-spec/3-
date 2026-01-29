/**
 * Statistics Cards Component
 * 대시보드 요약 통계 카드
 */
import React from 'react';
import './StatisticsCards.css';

interface StatisticsCardsProps {
  summary: {
    today_dispatches: number;
    today_orders: number;
    today_pallets: number;
    week_dispatches: number;
    week_orders: number;
    week_distance_km: number;
    month_dispatches: number;
    month_orders: number;
    month_pallets: number;
    active_vehicles: number;
    total_vehicles: number;
    active_clients: number;
    total_clients: number;
    dispatch_growth_rate: number;
    order_growth_rate: number;
  };
}

const StatisticsCards: React.FC<StatisticsCardsProps> = ({ summary }) => {
  const formatGrowthRate = (rate: number) => {
    const sign = rate >= 0 ? '+' : '';
    return `${sign}${rate.toFixed(1)}%`;
  };

  const getGrowthClass = (rate: number) => {
    return rate >= 0 ? 'positive' : 'negative';
  };

  return (
    <div className="statistics-cards">
      {/* Today Section */}
      <div className="card-section">
        <h3>오늘</h3>
        <div className="cards-row">
          <div className="stat-card">
            <div className="icon">🚚</div>
            <div className="content">
              <span className="label">배차</span>
              <span className="value">{summary.today_dispatches}</span>
              <span className="unit">건</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="icon">📦</div>
            <div className="content">
              <span className="label">주문</span>
              <span className="value">{summary.today_orders}</span>
              <span className="unit">건</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="icon">📊</div>
            <div className="content">
              <span className="label">팔레트</span>
              <span className="value">{summary.today_pallets}</span>
              <span className="unit">PLT</span>
            </div>
          </div>
        </div>
      </div>

      {/* This Week Section */}
      <div className="card-section">
        <h3>이번 주</h3>
        <div className="cards-row">
          <div className="stat-card">
            <div className="icon">🚛</div>
            <div className="content">
              <span className="label">배차</span>
              <span className="value">{summary.week_dispatches}</span>
              <span className="unit">건</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="icon">📋</div>
            <div className="content">
              <span className="label">주문</span>
              <span className="value">{summary.week_orders}</span>
              <span className="unit">건</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="icon">🛣️</div>
            <div className="content">
              <span className="label">주행 거리</span>
              <span className="value">{summary.week_distance_km.toFixed(1)}</span>
              <span className="unit">km</span>
            </div>
          </div>
        </div>
      </div>

      {/* This Month Section */}
      <div className="card-section">
        <h3>이번 달</h3>
        <div className="cards-row">
          <div className="stat-card">
            <div className="icon">📈</div>
            <div className="content">
              <span className="label">배차</span>
              <span className="value">{summary.month_dispatches}</span>
              <span className="unit">건</span>
              <span className={`growth ${getGrowthClass(summary.dispatch_growth_rate)}`}>
                {formatGrowthRate(summary.dispatch_growth_rate)}
              </span>
            </div>
          </div>
          <div className="stat-card">
            <div className="icon">📦</div>
            <div className="content">
              <span className="label">주문</span>
              <span className="value">{summary.month_orders}</span>
              <span className="unit">건</span>
              <span className={`growth ${getGrowthClass(summary.order_growth_rate)}`}>
                {formatGrowthRate(summary.order_growth_rate)}
              </span>
            </div>
          </div>
          <div className="stat-card">
            <div className="icon">📊</div>
            <div className="content">
              <span className="label">팔레트</span>
              <span className="value">{summary.month_pallets}</span>
              <span className="unit">PLT</span>
            </div>
          </div>
        </div>
      </div>

      {/* Resources Section */}
      <div className="card-section">
        <h3>운영 현황</h3>
        <div className="cards-row">
          <div className="stat-card">
            <div className="icon">🚗</div>
            <div className="content">
              <span className="label">활성 차량</span>
              <span className="value">{summary.active_vehicles}</span>
              <span className="unit">/ {summary.total_vehicles}</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="icon">🏢</div>
            <div className="content">
              <span className="label">활성 거래처</span>
              <span className="value">{summary.active_clients}</span>
              <span className="unit">/ {summary.total_clients}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatisticsCards;
