import React, { useEffect, useState, useMemo } from 'react';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import apiClient from '../api/client';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { TrendingUp, Package, Truck, DollarSign } from 'lucide-react';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const AnalyticsPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiClient.getDashboard();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const deliveryTrendData = useMemo(() => ({
    labels: ['1주', '2주', '3주', '4주'],
    datasets: [
      {
        label: '완료 배송',
        data: [45, 52, 48, 58],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: '취소 배송',
        data: [3, 2, 4, 2],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
    ],
  }), []);

  const vehicleUsageData = useMemo(() => ({
    labels: ['냉동', '냉장', '혼합'],
    datasets: [
      {
        label: '차량 사용률',
        data: [65, 25, 10],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(249, 115, 22, 0.8)',
        ],
      },
    ],
  }), []);

  const monthlyRevenueData = useMemo(() => ({
    labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
    datasets: [
      {
        label: '월별 매출',
        data: [4500000, 5200000, 4800000, 5800000, 6200000, 6500000],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
      },
    ],
  }), []);

  const statusDistributionData = useMemo(() => ({
    labels: ['완료', '진행중', '대기', '취소'],
    datasets: [
      {
        data: [120, 35, 15, 5],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
      },
    ],
  }), []);

  if (loading || !stats) {
    return (
      <Layout>
        <Loading />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">통계 및 분석</h1>
          <p className="text-gray-600 mt-2">배송 데이터 분석 및 인사이트</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">이번 달 배송</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">203</p>
                <p className="text-sm text-green-600 mt-2 flex items-center">
                  <TrendingUp size={16} className="mr-1" />
                  +15%
                </p>
              </div>
              <div className="bg-blue-500 p-4 rounded-full">
                <Package className="text-white" size={24} />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">평균 배송시간</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">4.2h</p>
                <p className="text-sm text-green-600 mt-2 flex items-center">
                  <TrendingUp size={16} className="mr-1" />
                  -8%
                </p>
              </div>
              <div className="bg-green-500 p-4 rounded-full">
                <Truck className="text-white" size={24} />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">이번 달 매출</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">650만</p>
                <p className="text-sm text-green-600 mt-2 flex items-center">
                  <TrendingUp size={16} className="mr-1" />
                  +12%
                </p>
              </div>
              <div className="bg-purple-500 p-4 rounded-full">
                <DollarSign className="text-white" size={24} />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">고객 만족도</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">4.8</p>
                <p className="text-sm text-gray-500 mt-2">/ 5.0</p>
              </div>
              <div className="bg-yellow-500 p-4 rounded-full">
                <TrendingUp className="text-white" size={24} />
              </div>
            </div>
          </Card>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="배송 추이">
            <Line
              data={deliveryTrendData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
              }}
            />
          </Card>

          <Card title="월별 매출">
            <Bar
              data={monthlyRevenueData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    ticks: {
                      callback: (value) => `${(Number(value) / 1000000).toFixed(1)}M`,
                    },
                  },
                },
              }}
            />
          </Card>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="차량 유형별 사용률">
            <div className="max-w-md mx-auto">
              <Doughnut
                data={vehicleUsageData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'bottom' as const,
                    },
                  },
                }}
              />
            </div>
          </Card>

          <Card title="주문 상태 분포">
            <div className="max-w-md mx-auto">
              <Doughnut
                data={statusDistributionData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'bottom' as const,
                    },
                  },
                }}
              />
            </div>
          </Card>
        </div>

        {/* Performance Table */}
        <Card title="주요 성과 지표">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">지표</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">이번 달</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">지난 달</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">변화율</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4">총 배송 건수</td>
                  <td className="py-3 px-4 font-semibold">203</td>
                  <td className="py-3 px-4">176</td>
                  <td className="py-3 px-4 text-green-600">+15.3%</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4">정시 배송률</td>
                  <td className="py-3 px-4 font-semibold">94.5%</td>
                  <td className="py-3 px-4">92.3%</td>
                  <td className="py-3 px-4 text-green-600">+2.2%</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4">평균 배송시간</td>
                  <td className="py-3 px-4 font-semibold">4.2시간</td>
                  <td className="py-3 px-4">4.6시간</td>
                  <td className="py-3 px-4 text-green-600">-8.7%</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4">차량 가동률</td>
                  <td className="py-3 px-4 font-semibold">87.2%</td>
                  <td className="py-3 px-4">84.5%</td>
                  <td className="py-3 px-4 text-green-600">+3.2%</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-3 px-4">고객 만족도</td>
                  <td className="py-3 px-4 font-semibold">4.8/5.0</td>
                  <td className="py-3 px-4">4.7/5.0</td>
                  <td className="py-3 px-4 text-green-600">+2.1%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default AnalyticsPage;
