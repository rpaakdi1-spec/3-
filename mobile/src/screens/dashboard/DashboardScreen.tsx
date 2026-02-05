import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface DispatchSummary {
  total: number;
  pending: number;
  in_progress: number;
  completed: number;
}

interface Dispatch {
  id: number;
  order_id: number;
  vehicle_id: number;
  driver_name: string;
  status: string;
  pickup_address: string;
  delivery_address: string;
  scheduled_time: string;
}

export default function DashboardScreen({ navigation }: any) {
  const [summary, setSummary] = useState<DispatchSummary>({
    total: 0,
    pending: 0,
    in_progress: 0,
    completed: 0,
  });
  const [dispatches, setDispatches] = useState<Dispatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [userName, setUserName] = useState('기사님');

  useEffect(() => {
    loadData();
    loadUserName();
  }, []);

  const loadUserName = async () => {
    try {
      const name = await AsyncStorage.getItem('user_name');
      if (name) setUserName(name);
    } catch (error) {
      console.error('Load user name error:', error);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('auth_token');
      
      // 배차 요약 조회
      const summaryRes = await axios.get(`${API_URL}/mobile/summary`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSummary(summaryRes.data);

      // 오늘의 배차 조회
      const dispatchRes = await axios.get(`${API_URL}/mobile/dispatches`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { limit: 5 },
      });
      setDispatches(dispatchRes.data);
    } catch (error: any) {
      console.error('Load data error:', error);
      if (error.response?.status === 401) {
        Alert.alert('세션 만료', '다시 로그인해주세요.');
        navigation.replace('Auth');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING':
        return '#F59E0B';
      case 'IN_PROGRESS':
        return '#3B82F6';
      case 'COMPLETED':
        return '#10B981';
      default:
        return '#9CA3AF';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'PENDING':
        return '대기중';
      case 'IN_PROGRESS':
        return '진행중';
      case 'COMPLETED':
        return '완료';
      default:
        return status;
    }
  };

  return (
    <View style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>안녕하세요, {userName}!</Text>
          <Text style={styles.subGreeting}>오늘도 안전운전 하세요</Text>
        </View>
        <TouchableOpacity style={styles.notificationButton}>
          <Ionicons name="notifications-outline" size={24} color="#111827" />
          <View style={styles.badge}>
            <Text style={styles.badgeText}>3</Text>
          </View>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={loadData} />
        }
      >
        {/* 요약 카드 */}
        <View style={styles.summaryContainer}>
          <View style={[styles.summaryCard, { backgroundColor: '#EFF6FF' }]}>
            <Ionicons name="list-outline" size={24} color="#3B82F6" />
            <Text style={styles.summaryValue}>{summary.total}</Text>
            <Text style={styles.summaryLabel}>전체 배차</Text>
          </View>

          <View style={[styles.summaryCard, { backgroundColor: '#FEF3C7' }]}>
            <Ionicons name="time-outline" size={24} color="#F59E0B" />
            <Text style={styles.summaryValue}>{summary.pending}</Text>
            <Text style={styles.summaryLabel}>대기중</Text>
          </View>

          <View style={[styles.summaryCard, { backgroundColor: '#DBEAFE' }]}>
            <Ionicons name="rocket-outline" size={24} color="#3B82F6" />
            <Text style={styles.summaryValue}>{summary.in_progress}</Text>
            <Text style={styles.summaryLabel}>진행중</Text>
          </View>

          <View style={[styles.summaryCard, { backgroundColor: '#D1FAE5' }]}>
            <Ionicons name="checkmark-circle-outline" size={24} color="#10B981" />
            <Text style={styles.summaryValue}>{summary.completed}</Text>
            <Text style={styles.summaryLabel}>완료</Text>
          </View>
        </View>

        {/* 긴급 알림 */}
        <View style={styles.alertCard}>
          <Ionicons name="warning-outline" size={24} color="#EF4444" />
          <View style={styles.alertContent}>
            <Text style={styles.alertTitle}>긴급 배차 1건</Text>
            <Text style={styles.alertText}>30분 내 픽업 필요</Text>
          </View>
        </View>

        {/* 오늘의 배차 */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>오늘의 배차</Text>
            <TouchableOpacity
              onPress={() => navigation.navigate('Dispatch')}
            >
              <Text style={styles.seeAll}>전체보기</Text>
            </TouchableOpacity>
          </View>

          {dispatches.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="calendar-outline" size={48} color="#9CA3AF" />
              <Text style={styles.emptyText}>배차가 없습니다</Text>
            </View>
          ) : (
            dispatches.map((dispatch) => (
              <TouchableOpacity
                key={dispatch.id}
                style={styles.dispatchCard}
                onPress={() =>
                  navigation.navigate('Dispatch', {
                    screen: 'DispatchDetail',
                    params: { id: dispatch.id },
                  })
                }
              >
                <View style={styles.dispatchHeader}>
                  <Text style={styles.dispatchId}>#{dispatch.id}</Text>
                  <View
                    style={[
                      styles.statusBadge,
                      { backgroundColor: `${getStatusColor(dispatch.status)}15` },
                    ]}
                  >
                    <Text
                      style={[
                        styles.statusText,
                        { color: getStatusColor(dispatch.status) },
                      ]}
                    >
                      {getStatusText(dispatch.status)}
                    </Text>
                  </View>
                </View>

                <View style={styles.dispatchRoute}>
                  <View style={styles.routeItem}>
                    <Ionicons name="location-outline" size={16} color="#3B82F6" />
                    <Text style={styles.routeText} numberOfLines={1}>
                      {dispatch.pickup_address}
                    </Text>
                  </View>
                  <Ionicons name="arrow-down" size={16} color="#9CA3AF" />
                  <View style={styles.routeItem}>
                    <Ionicons name="flag-outline" size={16} color="#10B981" />
                    <Text style={styles.routeText} numberOfLines={1}>
                      {dispatch.delivery_address}
                    </Text>
                  </View>
                </View>

                <View style={styles.dispatchFooter}>
                  <View style={styles.timeInfo}>
                    <Ionicons name="time-outline" size={14} color="#6B7280" />
                    <Text style={styles.timeText}>
                      {new Date(dispatch.scheduled_time).toLocaleTimeString('ko-KR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Text>
                  </View>
                  {dispatch.status === 'PENDING' && (
                    <TouchableOpacity style={styles.startButton}>
                      <Text style={styles.startButtonText}>시작하기</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  subGreeting: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  notificationButton: {
    position: 'relative',
    padding: 8,
  },
  badge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#EF4444',
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  summaryContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  summaryCard: {
    flex: 1,
    minWidth: '46%',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 8,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  alertCard: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: 16,
    marginTop: 0,
    padding: 16,
    backgroundColor: '#FEF2F2',
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#EF4444',
  },
  alertContent: {
    flex: 1,
    marginLeft: 12,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#EF4444',
  },
  alertText: {
    fontSize: 14,
    color: '#991B1B',
    marginTop: 2,
  },
  section: {
    padding: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
  },
  seeAll: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '500',
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 48,
  },
  emptyText: {
    fontSize: 16,
    color: '#9CA3AF',
    marginTop: 16,
  },
  dispatchCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  dispatchHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  dispatchId: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  dispatchRoute: {
    marginBottom: 12,
  },
  routeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  routeText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    marginLeft: 8,
  },
  dispatchFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  timeInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timeText: {
    fontSize: 12,
    color: '#6B7280',
    marginLeft: 4,
  },
  startButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  startButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});
