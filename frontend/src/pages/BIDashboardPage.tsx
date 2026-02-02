/**
 * Advanced BI Dashboard Page - Phase 10
 * 고급 분석 및 BI 대시보드
 */
import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  TrendingUp, TrendingDown, DollarSign, Activity, Truck, Users, AlertCircle, Award,
  Target, Package, Clock, Star, ThumbsUp, MapPin, Fuel, Tool
} from 'lucide-react';
import Layout from '../components/common/Layout';
import * as analyticsApi from '../api/analytics';

const BIDashboardPage: React.FC = () => {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });
  
  const [activeTab, setActiveTab] = useState<'overview' | 'vehicles' | 'drivers' | 'customers' | 'routes' | 'costs'>('overview');
  const [loading, setLoading] = useState(true);
  
  // State for different analytics data
  const [fleetPerformance, setFleetPerformance] = useState<any>(null);
  const [driverRankings, setDriverRankings] = useState<any[]>([]);
  const [topCustomers, setTopCustomers] = useState<any[]>([]);
  const [routeEfficiency, setRouteEfficiency] = useState<any>(null);
  const [costReport, setCostReport] = useState<any>(null);
  const [maintenanceAlerts, setMaintenanceAlerts] = useState<any[]>([]);

  useEffect(() => {
    fetchAnalyticsData();
  }, [dateRange, activeTab]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const { start, end } = dateRange;
      
      // Fetch data based on active tab
      switch (activeTab) {
        case 'overview':
          await fetchOverviewData(start, end);
          break;
        case 'vehicles':
          await fetchVehicleData(start, end);
          break;
        case 'drivers':
          await fetchDriverData(start, end);
          break;
        case 'customers':
          await fetchCustomerData(start, end);
          break;
        case 'routes':
          await fetchRouteData(start, end);
          break;
        case 'costs':
          await fetchCostData(start, end);
          break;
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOverviewData = async (start: string, end: string) => {
    const [fleet, drivers, customers, routes, costs, alerts] = await Promise.all([
      analyticsApi.getFleetPerformanceSummary(start, end),
      analyticsApi.getDriverRankings(start, end),
      analyticsApi.getTopCustomers(start, end, 5),
      analyticsApi.getFleetRouteEfficiency(start, end),
      analyticsApi.getCostReport(start, end),
      analyticsApi.getMaintenanceAlerts()
    ]);
    
    setFleetPerformance(fleet);
    setDriverRankings(drivers.slice(0, 5));
    setTopCustomers(customers);
    setRouteEfficiency(routes);
    setCostReport(costs);
    setMaintenanceAlerts(alerts);
  };

  const fetchVehicleData = async (start: string, end: string) => {
    const [fleet, alerts] = await Promise.all([
      analyticsApi.getFleetPerformanceSummary(start, end),
      analyticsApi.getMaintenanceAlerts()
    ]);
    
    setFleetPerformance(fleet);
    setMaintenanceAlerts(alerts);
  };

  const fetchDriverData = async (start: string, end: string) => {
    const rankings = await analyticsApi.getDriverRankings(start, end);
    setDriverRankings(rankings);
  };

  const fetchCustomerData = async (start: string, end: string) => {
    const [top, churn] = await Promise.all([
      analyticsApi.getTopCustomers(start, end, 10),
      analyticsApi.getChurnRiskCustomers(start, end)
    ]);
    
    setTopCustomers(top);
  };

  const fetchRouteData = async (start: string, end: string) => {
    const [efficiency, inefficient] = await Promise.all([
      analyticsApi.getFleetRouteEfficiency(start, end),
      analyticsApi.getInefficientRoutes(start, end, 70)
    ]);
    
    setRouteEfficiency(efficiency);
  };

  const fetchCostData = async (start: string, end: string) => {
    const report = await analyticsApi.getCostReport(start, end);
    setCostReport(report);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0
    }).format(value);
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">고급 분석 대시보드</h1>
          <p className="text-gray-600 mt-1">비즈니스 인텔리전스 및 성과 분석</p>
        </div>
        
        <div className="flex gap-4">
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <span className="flex items-center text-gray-500">~</span>
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-gray-200">
        {[
          { id: 'overview', label: '종합', icon: Activity },
          { id: 'vehicles', label: '차량 성능', icon: Truck },
          { id: 'drivers', label: '운전자 평가', icon: Users },
          { id: 'customers', label: '고객 만족도', icon: ThumbsUp },
          { id: 'routes', label: '경로 효율성', icon: MapPin },
          { id: 'costs', label: '비용 최적화', icon: DollarSign }
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as any)}
            className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2 ${
              activeTab === id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Icon size={20} />
            {label}
          </button>
        ))}
      </div>

      {/* Content based on active tab */}
      {activeTab === 'overview' && (
        <OverviewTab
          fleetPerformance={fleetPerformance}
          driverRankings={driverRankings}
          topCustomers={topCustomers}
          routeEfficiency={routeEfficiency}
          costReport={costReport}
          maintenanceAlerts={maintenanceAlerts}
          formatCurrency={formatCurrency}
          colors={COLORS}
        />
      )}

      {activeTab === 'vehicles' && (
        <VehiclesTab
          fleetPerformance={fleetPerformance}
          maintenanceAlerts={maintenanceAlerts}
          colors={COLORS}
        />
      )}

      {activeTab === 'drivers' && (
        <DriversTab
          driverRankings={driverRankings}
          colors={COLORS}
        />
      )}

      {activeTab === 'customers' && (
        <CustomersTab
          topCustomers={topCustomers}
          formatCurrency={formatCurrency}
          colors={COLORS}
        />
      )}

      {activeTab === 'routes' && (
        <RoutesTab
          routeEfficiency={routeEfficiency}
          colors={COLORS}
        />
      )}

      {activeTab === 'costs' && (
        <CostsTab
          costReport={costReport}
          formatCurrency={formatCurrency}
          colors={COLORS}
        />
      )}
      </div>
    </Layout>
  );
};

// Overview Tab Component
const OverviewTab: React.FC<any> = ({
  fleetPerformance,
  driverRankings,
  topCustomers,
  routeEfficiency,
  costReport,
  maintenanceAlerts,
  formatCurrency,
  colors
}) => {
  return (
    <div className="space-y-6">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="차량 평균 효율성"
          value={`${fleetPerformance?.average_efficiency_score || 0}점`}
          icon={Truck}
          trend={fleetPerformance?.average_efficiency_score >= 80 ? 'up' : 'down'}
          color="blue"
        />
        
        <MetricCard
          title="운전자 평균 점수"
          value={driverRankings.length > 0 ? `${(driverRankings.reduce((sum: number, d: any) => sum + d.overall_score, 0) / driverRankings.length).toFixed(1)}점` : 'N/A'}
          icon={Users}
          trend="up"
          color="green"
        />
        
        <MetricCard
          title="경로 효율성"
          value={`${routeEfficiency?.summary?.average_efficiency_score || 0}점`}
          icon={MapPin}
          trend={routeEfficiency?.summary?.average_efficiency_score >= 80 ? 'up' : 'down'}
          color="purple"
        />
        
        <MetricCard
          title="수익률"
          value={`${costReport?.revenue?.profit_margin_percent || 0}%`}
          icon={DollarSign}
          trend={costReport?.revenue?.profit_margin_percent >= 15 ? 'up' : 'down'}
          color="orange"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fleet Performance Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Truck className="text-blue-600" size={20} />
            차량 성능 분포
          </h3>
          {fleetPerformance?.all_vehicles && (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={fleetPerformance.all_vehicles.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="vehicle_number" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="efficiency_score" fill="#3b82f6" name="효율성 점수" />
                <Bar dataKey="utilization_rate" fill="#10b981" name="가동률" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Driver Rankings */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Award className="text-green-600" size={20} />
            우수 운전자 TOP 5
          </h3>
          <div className="space-y-3">
            {driverRankings.slice(0, 5).map((driver: any, index: number) => (
              <div key={driver.driver_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-600' : 'bg-blue-500'
                  } text-white font-bold`}>
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium">{driver.driver_name}</p>
                    <p className="text-sm text-gray-500">{driver.grade}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">{driver.overall_score.toFixed(1)}</p>
                  <p className="text-xs text-gray-500">점</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cost Breakdown */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <DollarSign className="text-orange-600" size={20} />
            비용 구성
          </h3>
          {costReport?.cost_breakdown_percent && (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={[
                    { name: '연료비', value: costReport.cost_breakdown_percent.fuel },
                    { name: '인건비', value: costReport.cost_breakdown_percent.labor },
                    { name: '유지보수', value: costReport.cost_breakdown_percent.maintenance },
                    { name: '고정비', value: costReport.cost_breakdown_percent.fixed }
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {colors.map((color: string, index: number) => (
                    <Cell key={`cell-${index}`} fill={color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Top Customers */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Star className="text-yellow-500" size={20} />
            주요 고객사
          </h3>
          <div className="space-y-2">
            {topCustomers.slice(0, 5).map((customer: any) => (
              <div key={customer.partner_id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                <div>
                  <p className="font-medium text-sm">{customer.partner_name}</p>
                  <p className="text-xs text-gray-500">주문 {customer.total_orders}건</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-sm">{customer.satisfaction_grade}</p>
                  <p className="text-xs text-gray-500">{customer.satisfaction_score.toFixed(1)}점</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Maintenance Alerts */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertCircle className="text-red-600" size={20} />
            유지보수 알림
          </h3>
          <div className="space-y-2">
            {maintenanceAlerts.slice(0, 5).map((alert: any) => (
              <div
                key={alert.vehicle_id}
                className={`p-3 rounded-lg border-l-4 ${
                  alert.alert_level === 'critical'
                    ? 'border-red-500 bg-red-50'
                    : 'border-yellow-500 bg-yellow-50'
                }`}
              >
                <p className="font-medium text-sm">{alert.vehicle_number}</p>
                <p className="text-xs text-gray-600 mt-1">
                  {alert.reasons[0]}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Metric Card Component
const MetricCard: React.FC<{
  title: string;
  value: string;
  icon: any;
  trend: 'up' | 'down';
  color: string;
}> = ({ title, value, icon: Icon, trend, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
    red: 'bg-red-100 text-red-600'
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
          <Icon size={24} />
        </div>
        {trend === 'up' ? (
          <TrendingUp className="text-green-500" size={20} />
        ) : (
          <TrendingDown className="text-red-500" size={20} />
        )}
      </div>
      <p className="text-gray-600 text-sm mt-4">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
};

// Placeholder components for other tabs (to be implemented)
const VehiclesTab: React.FC<any> = ({ fleetPerformance, maintenanceAlerts, colors }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h2 className="text-xl font-bold mb-4">차량 성능 분석</h2>
    <p className="text-gray-600">차량별 상세 성능 데이터가 여기에 표시됩니다.</p>
  </div>
);

const DriversTab: React.FC<any> = ({ driverRankings, colors }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h2 className="text-xl font-bold mb-4">운전자 평가</h2>
    <p className="text-gray-600">운전자별 상세 평가 데이터가 여기에 표시됩니다.</p>
  </div>
);

const CustomersTab: React.FC<any> = ({ topCustomers, formatCurrency, colors }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h2 className="text-xl font-bold mb-4">고객 만족도 분석</h2>
    <p className="text-gray-600">고객별 상세 만족도 데이터가 여기에 표시됩니다.</p>
  </div>
);

const RoutesTab: React.FC<any> = ({ routeEfficiency, colors }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h2 className="text-xl font-bold mb-4">경로 효율성 분석</h2>
    <p className="text-gray-600">경로별 상세 효율성 데이터가 여기에 표시됩니다.</p>
  </div>
);

const CostsTab: React.FC<any> = ({ costReport, formatCurrency, colors }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h2 className="text-xl font-bold mb-4">비용 최적화 분석</h2>
    <p className="text-gray-600">비용별 상세 분석 데이터가 여기에 표시됩니다.</p>
  </div>
);

export default BIDashboardPage;
