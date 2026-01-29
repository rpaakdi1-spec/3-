/**
 * Client Distribution Chart Component
 * 거래처별 배송 분포 차트 (Pie/Doughnut Chart)
 */
import React, { useState } from 'react';
import { Doughnut, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface ClientDistributionChartProps {
  data: {
    clients: Array<{
      client_id: number;
      client_code: string;
      client_name: string;
      client_type: string;
      total_orders: number;
      total_pallets: number;
      delivery_frequency: number;
      region?: string;
    }>;
  };
}

const ClientDistributionChart: React.FC<ClientDistributionChartProps> = ({ data }) => {
  const [chartType, setChartType] = useState<'doughnut' | 'pie'>('doughnut');
  const [metric, setMetric] = useState<'orders' | 'pallets'>('orders');

  // Top 10 clients
  const topClients = [...data.clients]
    .sort((a, b) => (metric === 'orders' ? b.total_orders - a.total_orders : b.total_pallets - a.total_pallets))
    .slice(0, 10);

  // Colors
  const colors = [
    'rgba(54, 162, 235, 0.8)',
    'rgba(255, 99, 132, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(255, 159, 64, 0.8)',
    'rgba(153, 102, 255, 0.8)',
    'rgba(255, 205, 86, 0.8)',
    'rgba(201, 203, 207, 0.8)',
    'rgba(255, 99, 255, 0.8)',
    'rgba(100, 200, 100, 0.8)',
    'rgba(200, 100, 200, 0.8)',
  ];

  const chartData = {
    labels: topClients.map((c) => c.client_name),
    datasets: [
      {
        label: metric === 'orders' ? '주문 건수' : '팔레트 수',
        data: topClients.map((c) => (metric === 'orders' ? c.total_orders : c.total_pallets)),
        backgroundColor: colors,
        borderColor: colors.map((c) => c.replace('0.8', '1')),
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          boxWidth: 12,
          padding: 10,
          font: {
            size: 11,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            const client = topClients[context.dataIndex];
            const total = topClients.reduce((sum, c) => sum + (metric === 'orders' ? c.total_orders : c.total_pallets), 0);
            const value = metric === 'orders' ? client.total_orders : client.total_pallets;
            const percentage = ((value / total) * 100).toFixed(1);
            return [
              `${context.label}`,
              `${metric === 'orders' ? '주문' : '팔레트'}: ${value.toLocaleString()}${metric === 'orders' ? '건' : 'PLT'}`,
              `비율: ${percentage}%`,
              `배송 빈도: ${client.delivery_frequency.toFixed(1)}회/월`,
            ];
          },
        },
      },
    },
  };

  // Region distribution
  const regionData: Record<string, number> = {};
  data.clients.forEach((client) => {
    const region = client.region || '기타';
    if (!regionData[region]) {
      regionData[region] = 0;
    }
    regionData[region] += metric === 'orders' ? client.total_orders : client.total_pallets;
  });

  const regionChartData = {
    labels: Object.keys(regionData),
    datasets: [
      {
        label: metric === 'orders' ? '주문 건수' : '팔레트 수',
        data: Object.values(regionData),
        backgroundColor: colors,
        borderColor: colors.map((c) => c.replace('0.8', '1')),
        borderWidth: 1,
      },
    ],
  };

  const ChartComponent = chartType === 'doughnut' ? Doughnut : Pie;

  return (
    <div className="client-distribution">
      {/* Controls */}
      <div className="chart-controls">
        <div className="control-group">
          <label>차트 유형:</label>
          <select value={chartType} onChange={(e) => setChartType(e.target.value as any)}>
            <option value="doughnut">도넛</option>
            <option value="pie">파이</option>
          </select>
        </div>
        
        <div className="control-group">
          <label>측정 항목:</label>
          <select value={metric} onChange={(e) => setMetric(e.target.value as any)}>
            <option value="orders">주문 건수</option>
            <option value="pallets">팔레트 수</option>
          </select>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-row">
        {/* Top Clients Chart */}
        <div className="chart-column">
          <h4>상위 거래처 TOP 10</h4>
          <div style={{ height: '350px' }}>
            <ChartComponent data={chartData} options={options} />
          </div>
        </div>

        {/* Region Distribution Chart */}
        <div className="chart-column">
          <h4>지역별 배송 분포</h4>
          <div style={{ height: '350px' }}>
            <ChartComponent data={regionChartData} options={options} />
          </div>
        </div>
      </div>

      {/* Client List */}
      <div className="client-list">
        <h4>거래처 목록</h4>
        <div className="client-grid">
          {topClients.map((client, index) => (
            <div key={client.client_id} className="client-item">
              <span className="rank">#{index + 1}</span>
              <div className="client-info">
                <span className="name">{client.client_name}</span>
                <span className="stats">
                  {client.total_orders}건 · {client.total_pallets}PLT · {client.delivery_frequency.toFixed(1)}회/월
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ClientDistributionChart;
