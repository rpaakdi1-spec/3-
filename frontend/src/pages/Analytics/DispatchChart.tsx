/**
 * Dispatch Chart Component
 * 배차 통계 차트 (Line Chart)
 */
import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface DispatchChartProps {
  data: {
    statistics: Array<{
      date: string;
      total_dispatches: number;
      total_orders: number;
      total_pallets: number;
      total_distance_km: number;
    }>;
  };
  period: 'daily' | 'weekly' | 'monthly';
}

const DispatchChart: React.FC<DispatchChartProps> = ({ data, period }) => {
  const labels = data.statistics.map((stat) => {
    const date = new Date(stat.date);
    switch (period) {
      case 'daily':
        return format(date, 'MM/dd');
      case 'weekly':
        return format(date, 'MM/dd');
      case 'monthly':
        return format(date, 'yyyy-MM');
      default:
        return format(date, 'MM/dd');
    }
  });

  const chartData = {
    labels,
    datasets: [
      {
        label: '배차 건수',
        data: data.statistics.map((stat) => stat.total_dispatches),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: '주문 건수',
        data: data.statistics.map((stat) => stat.total_orders),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: '팔레트 수',
        data: data.statistics.map((stat) => stat.total_pallets),
        borderColor: 'rgb(255, 159, 64)',
        backgroundColor: 'rgba(255, 159, 64, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y.toLocaleString();
              if (context.dataset.label === '배차 건수' || context.dataset.label === '주문 건수') {
                label += ' 건';
              } else {
                label += ' PLT';
              }
            }
            return label;
          },
        },
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: '배차/주문 건수',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: '팔레트 수 (PLT)',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  return (
    <div style={{ height: '400px' }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default DispatchChart;
