import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { format } from 'date-fns';
import ApiService from '../../services/api';
import { Dispatch } from '../../types';

const HomeScreen: React.FC = () => {
  const [dispatches, setDispatches] = useState<Dispatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const navigation = useNavigation();

  useEffect(() => {
    loadDispatches();
  }, []);

  const loadDispatches = async () => {
    try {
      const today = format(new Date(), 'yyyy-MM-dd');
      const data = await ApiService.getMyDispatches(today);
      setDispatches(data);
    } catch (error: any) {
      Alert.alert('오류', '배차 정보를 불러오는데 실패했습니다.');
      console.error('Load dispatches error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadDispatches();
  }, []);

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      DRAFT: '초안',
      CONFIRMED: '확정',
      IN_PROGRESS: '진행중',
      COMPLETED: '완료',
      CANCELLED: '취소',
    };
    return statusMap[status] || status;
  };

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      DRAFT: '#999',
      CONFIRMED: '#007AFF',
      IN_PROGRESS: '#FF9500',
      COMPLETED: '#34C759',
      CANCELLED: '#FF3B30',
    };
    return colorMap[status] || '#999';
  };

  const renderDispatchItem = ({ item }: { item: Dispatch }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() =>
        navigation.navigate('DispatchDetail' as never, { dispatchId: item.id } as never)
      }>
      <View style={styles.cardHeader}>
        <Text style={styles.dispatchNumber}>{item.dispatch_number}</Text>
        <View
          style={[
            styles.statusBadge,
            { backgroundColor: getStatusColor(item.status) },
          ]}>
          <Text style={styles.statusText}>{getStatusText(item.status)}</Text>
        </View>
      </View>

      <View style={styles.cardContent}>
        <View style={styles.infoRow}>
          <Text style={styles.label}>차량:</Text>
          <Text style={styles.value}>{item.vehicle_code}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>기사:</Text>
          <Text style={styles.value}>{item.driver_name || '-'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>주문:</Text>
          <Text style={styles.value}>{item.total_orders}건</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>팔레트:</Text>
          <Text style={styles.value}>{item.total_pallets}개</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>중량:</Text>
          <Text style={styles.value}>{item.total_weight_kg}kg</Text>
        </View>
      </View>

      <View style={styles.cardFooter}>
        <Text style={styles.routeCount}>
          경로: {item.routes?.length || 0}개
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>오늘의 배차</Text>
        <Text style={styles.date}>{format(new Date(), 'yyyy년 MM월 dd일')}</Text>
      </View>

      {dispatches.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>오늘 배차가 없습니다</Text>
        </View>
      ) : (
        <FlatList
          data={dispatches}
          renderItem={renderDispatchItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  date: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  list: {
    padding: 15,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  dispatchNumber: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  cardContent: {
    marginBottom: 10,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  label: {
    fontSize: 14,
    color: '#666',
  },
  value: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  cardFooter: {
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 10,
  },
  routeCount: {
    fontSize: 14,
    color: '#007AFF',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});

export default HomeScreen;
