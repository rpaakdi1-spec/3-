import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface Dispatch {
  id: number;
  order_id: number;
  vehicle_id: number;
  status: string;
  pickup_address: string;
  delivery_address: string;
  scheduled_time: string;
}

export default function DispatchListScreen({ navigation }: any) {
  const [dispatches, setDispatches] = useState<Dispatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<string>('ALL');

  useEffect(() => {
    loadDispatches();
  }, [filter]);

  const loadDispatches = async () => {
    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(`${API_URL}/mobile/dispatches`, {
        headers: { Authorization: `Bearer ${token}` },
        params: filter !== 'ALL' ? { status: filter } : {},
      });
      setDispatches(response.data);
    } catch (error) {
      console.error('Load dispatches error:', error);
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

  const renderDispatch = ({ item }: { item: Dispatch }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => navigation.navigate('DispatchDetail', { id: item.id })}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.cardId}>#{item.id}</Text>
        <View
          style={[
            styles.statusBadge,
            { backgroundColor: `${getStatusColor(item.status)}15` },
          ]}
        >
          <Text
            style={[styles.statusText, { color: getStatusColor(item.status) }]}
          >
            {getStatusText(item.status)}
          </Text>
        </View>
      </View>

      <View style={styles.route}>
        <View style={styles.routeItem}>
          <Ionicons name="location" size={16} color="#3B82F6" />
          <Text style={styles.routeText} numberOfLines={1}>
            {item.pickup_address}
          </Text>
        </View>
        <Ionicons name="arrow-down" size={16} color="#9CA3AF" />
        <View style={styles.routeItem}>
          <Ionicons name="flag" size={16} color="#10B981" />
          <Text style={styles.routeText} numberOfLines={1}>
            {item.delivery_address}
          </Text>
        </View>
      </View>

      <View style={styles.cardFooter}>
        <View style={styles.timeInfo}>
          <Ionicons name="time-outline" size={14} color="#6B7280" />
          <Text style={styles.timeText}>
            {new Date(item.scheduled_time).toLocaleDateString('ko-KR', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        </View>
        <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* 필터 */}
      <View style={styles.filterContainer}>
        {['ALL', 'PENDING', 'IN_PROGRESS', 'COMPLETED'].map((status) => (
          <TouchableOpacity
            key={status}
            style={[
              styles.filterButton,
              filter === status && styles.filterButtonActive,
            ]}
            onPress={() => setFilter(status)}
          >
            <Text
              style={[
                styles.filterText,
                filter === status && styles.filterTextActive,
              ]}
            >
              {status === 'ALL'
                ? '전체'
                : status === 'PENDING'
                ? '대기'
                : status === 'IN_PROGRESS'
                ? '진행중'
                : '완료'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 목록 */}
      <FlatList
        data={dispatches}
        renderItem={renderDispatch}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={loadDispatches} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="clipboard-outline" size={48} color="#9CA3AF" />
            <Text style={styles.emptyText}>배차가 없습니다</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  filterContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    gap: 8,
  },
  filterButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    alignItems: 'center',
  },
  filterButtonActive: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  filterText: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  filterTextActive: {
    color: '#FFFFFF',
  },
  list: {
    padding: 16,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardId: {
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
  route: {
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
  cardFooter: {
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
  empty: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 48,
  },
  emptyText: {
    fontSize: 16,
    color: '#9CA3AF',
    marginTop: 16,
  },
});
