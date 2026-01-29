import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import dashboardService from '@services/dashboardService';
import { DashboardMetrics, Alert } from '@types/index';
import { Colors, FontSizes, Spacing, BorderRadius, Shadows, REFRESH_INTERVALS } from '@utils/constants';

export default function DashboardScreen() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [metricsData, alertsData] = await Promise.all([
        dashboardService.getMetrics(),
        dashboardService.getAlerts({ page: 1, size: 5, is_resolved: false }),
      ]);
      setMetrics(metricsData);
      setAlerts(alertsData.items);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, REFRESH_INTERVALS.DASHBOARD);
    return () => clearInterval(interval);
  }, [loadData]);

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>대시보드</Text>
          <Text style={styles.headerSubtitle}>실시간 운영 현황</Text>
        </View>

        {/* Metrics Cards */}
        <View style={styles.metricsGrid}>
          <MetricCard
            title="활성 배차"
            value={metrics?.active_dispatches || 0}
            color={Colors.primary}
            icon="🚚"
          />
          <MetricCard
            title="금일 완료"
            value={metrics?.completed_today || 0}
            color={Colors.success}
            icon="✓"
          />
          <MetricCard
            title="대기 주문"
            value={metrics?.pending_orders || 0}
            color={Colors.warning}
            icon="📦"
          />
          <MetricCard
            title="운행중 차량"
            value={metrics?.vehicles_in_transit || 0}
            color={Colors.info}
            icon="🚛"
          />
        </View>

        {/* Temperature Alerts */}
        {(metrics?.temperature_alerts || 0) > 0 && (
          <View style={styles.alertBanner}>
            <Text style={styles.alertText}>
              ⚠️ {metrics?.temperature_alerts}건의 온도 경고가 있습니다
            </Text>
          </View>
        )}

        {/* Recent Alerts */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>최근 알림</Text>
          {alerts.length > 0 ? (
            alerts.map((alert) => <AlertCard key={alert.id} alert={alert} />)
          ) : (
            <Text style={styles.emptyText}>알림이 없습니다</Text>
          )}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>빠른 작업</Text>
          <View style={styles.actionsGrid}>
            <ActionButton title="새 배차" icon="+" />
            <ActionButton title="차량 추적" icon="📍" />
            <ActionButton title="온도 모니터링" icon="🌡️" />
            <ActionButton title="리포트" icon="📊" />
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

interface MetricCardProps {
  title: string;
  value: number;
  color: string;
  icon: string;
}

function MetricCard({ title, value, color, icon }: MetricCardProps) {
  return (
    <View style={[styles.metricCard, { borderLeftColor: color }]}>
      <Text style={styles.metricIcon}>{icon}</Text>
      <Text style={styles.metricValue}>{value}</Text>
      <Text style={styles.metricTitle}>{title}</Text>
    </View>
  );
}

interface AlertCardProps {
  alert: Alert;
}

function AlertCard({ alert }: AlertCardProps) {
  const getSeverityColor = (severity: Alert['severity']) => {
    const colors = {
      low: Colors.info,
      medium: Colors.warning,
      high: Colors.danger,
      critical: Colors.dangerDark,
    };
    return colors[severity];
  };

  return (
    <View style={[styles.alertCard, { borderLeftColor: getSeverityColor(alert.severity) }]}>
      <View style={styles.alertHeader}>
        <Text style={styles.alertType}>{alert.alert_type}</Text>
        <Text style={[styles.alertSeverity, { color: getSeverityColor(alert.severity) }]}>
          {alert.severity.toUpperCase()}
        </Text>
      </View>
      <Text style={styles.alertMessage}>{alert.message}</Text>
      <Text style={styles.alertTime}>{new Date(alert.created_at).toLocaleString('ko-KR')}</Text>
    </View>
  );
}

interface ActionButtonProps {
  title: string;
  icon: string;
  onPress?: () => void;
}

function ActionButton({ title, icon, onPress }: ActionButtonProps) {
  return (
    <TouchableOpacity style={styles.actionButton} onPress={onPress}>
      <Text style={styles.actionIcon}>{icon}</Text>
      <Text style={styles.actionTitle}>{title}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: Spacing.lg,
    backgroundColor: Colors.white,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  headerTitle: {
    fontSize: FontSizes['2xl'],
    fontWeight: 'bold',
    color: Colors.text.primary,
  },
  headerSubtitle: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
    marginTop: Spacing.xs,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: Spacing.md,
    gap: Spacing.md,
  },
  metricCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: Colors.white,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    borderLeftWidth: 4,
    ...Shadows.sm,
  },
  metricIcon: {
    fontSize: 30,
    marginBottom: Spacing.sm,
  },
  metricValue: {
    fontSize: FontSizes['3xl'],
    fontWeight: 'bold',
    color: Colors.text.primary,
  },
  metricTitle: {
    fontSize: FontSizes.sm,
    color: Colors.text.secondary,
    marginTop: Spacing.xs,
  },
  alertBanner: {
    backgroundColor: Colors.warningLight,
    padding: Spacing.md,
    marginHorizontal: Spacing.md,
    marginBottom: Spacing.md,
    borderRadius: BorderRadius.md,
  },
  alertText: {
    fontSize: FontSizes.md,
    color: Colors.text.primary,
    fontWeight: '600',
  },
  section: {
    padding: Spacing.md,
  },
  sectionTitle: {
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
    color: Colors.text.primary,
    marginBottom: Spacing.md,
  },
  alertCard: {
    backgroundColor: Colors.white,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    marginBottom: Spacing.sm,
    borderLeftWidth: 4,
    ...Shadows.sm,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  alertType: {
    fontSize: FontSizes.sm,
    color: Colors.text.secondary,
    textTransform: 'uppercase',
  },
  alertSeverity: {
    fontSize: FontSizes.xs,
    fontWeight: 'bold',
  },
  alertMessage: {
    fontSize: FontSizes.md,
    color: Colors.text.primary,
    marginBottom: Spacing.sm,
  },
  alertTime: {
    fontSize: FontSizes.xs,
    color: Colors.text.secondary,
  },
  emptyText: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
    textAlign: 'center',
    padding: Spacing.lg,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
  },
  actionButton: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: Colors.white,
    borderRadius: BorderRadius.md,
    padding: Spacing.lg,
    alignItems: 'center',
    ...Shadows.sm,
  },
  actionIcon: {
    fontSize: 36,
    marginBottom: Spacing.sm,
  },
  actionTitle: {
    fontSize: FontSizes.md,
    color: Colors.text.primary,
    fontWeight: '600',
  },
});
