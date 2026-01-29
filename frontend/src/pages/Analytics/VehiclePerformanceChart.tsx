/**
 * Vehicle Performance Chart Component
 * 차량별 운행 성과 차트 (Horizontal Bar Chart + Table)
 */
import React, { useState } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface VehiclePerformanceChartProps {
  data: {
    vehicles: Array<{
      vehicle_id: number;
      vehicle_code: string;
      vehicle_type: string;
      total_dispatches: number;
      total_distance_km: number;
      total_pallets: number;
      avg_pallets_per_dispatch: number;
      avg_distance_per_dispatch: number;
      capacity_utilization: number;
    }>;
  };
}

const VehiclePerformanceChart: React.FC<VehiclePerformanceChartProps> = ({ data }) => {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [sortBy, setSortBy] = useState<'dispatches' | 'distance' | 'utilization'>('dispatches');

  // Top 10 vehicles
  const topVehicles = [...data.vehicles]
    .sort((a, b) => {
      switch (sortBy) {
        case 'distance':
          return b.total_distance_km - a.total_distance_km;
        case 'utilization':
          return b.capacity_utilization - a.capacity_utilization;
        default:
          return b.total_dispatches - a.total_dispatches;
      }
    })
    .slice(0, 10);

  const chartData = {
    labels: topVehicles.map((v) => v.vehicle_code),
    datasets: [
      {
        label: '배차 횟수',
        data: topVehicles.map((v) => v.total_dispatches),
        backgroundColor: 'rgba(54, 162, 235, 0.8)',
        borderColor: 'rgb(54, 162, 235)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            const vehicle = topVehicles[context.dataIndex];
            return [
              `배차: ${vehicle.total_dispatches}회`,
              `거리: ${vehicle.total_distance_km.toFixed(1)}km`,
              `적재율: ${vehicle.capacity_utilization.toFixed(1)}%`,
            ];
          },
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        title: {
          display: true,
          text: '배차 횟수',
        },
      },
    },
  };

  return (
    <div className="vehicle-performance">
      {/* View Mode Toggle */}
      <div className="view-controls">
        <div className="view-toggle">
          <button
            className={viewMode === 'chart' ? 'active' : ''}
            onClick={() => setViewMode('chart')}
          >
            📊 차트
          </button>
          <button
            className={viewMode === 'table' ? 'active' : ''}
            onClick={() => setViewMode('table')}
          >
            📋 표
          </button>
        </div>
        
        <div className="sort-controls">
          <label>정렬:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)}>
            <option value="dispatches">배차 횟수</option>
            <option value="distance">주행 거리</option>
            <option value="utilization">적재율</option>
          </select>
        </div>
      </div>

      {/* Chart View */}
      {viewMode === 'chart' && (
        <div style={{ height: '400px' }}>
          <Bar data={chartData} options={options} />
        </div>
      )}

      {/* Table View */}
      {viewMode === 'table' && (
        <div className="table-container">
          <table className="vehicle-table">
            <thead>
              <tr>
                <th>순위</th>
                <th>차량 번호</th>
                <th>차량 종류</th>
                <th>배차 횟수</th>
                <th>총 거리</th>
                <th>총 팔레트</th>
                <th>평균 적재율</th>
                <th>배차당 평균 거리</th>
              </tr>
            </thead>
            <tbody>
              {topVehicles.map((vehicle, index) => (
                <tr key={vehicle.vehicle_id}>
                  <td>{index + 1}</td>
                  <td className="vehicle-code">{vehicle.vehicle_code}</td>
                  <td>{vehicle.vehicle_type}</td>
                  <td>{vehicle.total_dispatches}회</td>
                  <td>{vehicle.total_distance_km.toFixed(1)}km</td>
                  <td>{vehicle.total_pallets} PLT</td>
                  <td>
                    <span className={`utilization ${vehicle.capacity_utilization >= 80 ? 'high' : vehicle.capacity_utilization >= 60 ? 'medium' : 'low'}`}>
                      {vehicle.capacity_utilization.toFixed(1)}%
                    </span>
                  </td>
                  <td>{vehicle.avg_distance_per_dispatch.toFixed(1)}km</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default VehiclePerformanceChart;
