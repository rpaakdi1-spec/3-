import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import dispatchService from '@services/dispatchService';
import { Dispatch } from '@types/index';
import { Colors, FontSizes, Spacing, BorderRadius, Shadows, StatusColors, StatusLabels } from '@utils/constants';

export default function DispatchListScreen() {
  const navigation = useNavigation();
  const [dispatches, setDispatches] = useState<Dispatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [page, setPage] = useState(1);

  const loadDispatches = useCallback(async (pageNum: number = 1) => {
    try {
      const response = await dispatchService.getDispatches({ page: pageNum, size: 20 });
      if (pageNum === 1) {
        setDispatches(response.items);
      } else {
        setDispatches(prev => [...prev, ...response.items]);
      }
    } catch (error) {
      console.error('Failed to load dispatches:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadDispatches();
  }, [loadDispatches]);

  const onRefresh = () => {
    setRefreshing(true);
    setPage(1);
    loadDispatches(1);
  };

  const renderItem = ({ item }: { item: Dispatch }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => navigation.navigate('DispatchDetail', { dispatchId: item.id })}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.dispatchNumber}>{item.dispatch_number}</Text>
        <View style={[styles.statusBadge, { backgroundColor: StatusColors.dispatch[item.status] }]}>
          <Text style={styles.statusText}>{StatusLabels.dispatch[item.status]}</Text>
        </View>
      </View>
      
      <View style={styles.cardBody}>
        <InfoRow label="차량" value={item.vehicle?.vehicle_plate_number || '미배정'} />
        <InfoRow label="운전자" value={item.driver?.driver_name || '미배정'} />
        <InfoRow label="픽업 시간" value={formatDateTime(item.scheduled_pickup_time)} />
        <InfoRow label="배송 시간" value={formatDateTime(item.scheduled_delivery_time)} />
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>배차 관리</Text>
      </View>
      
      <FlatList
        data={dispatches}
        renderItem={renderItem}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>배차가 없습니다</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

interface InfoRowProps {
  label: string;
  value: string;
}

function InfoRow({ label, value }: InfoRowProps) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}:</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  });
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
  },
  header: {
    padding: Spacing.lg,
    backgroundColor: Colors.white,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  title: {
    fontSize: FontSizes['2xl'],
    fontWeight: 'bold',
    color: Colors.text.primary,
  },
  list: {
    padding: Spacing.md,
  },
  card: {
    backgroundColor: Colors.white,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    marginBottom: Spacing.md,
    ...Shadows.md,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  dispatchNumber: {
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
    color: Colors.text.primary,
  },
  statusBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.sm,
  },
  statusText: {
    color: Colors.white,
    fontSize: FontSizes.sm,
    fontWeight: '600',
  },
  cardBody: {
    gap: Spacing.sm,
  },
  infoRow: {
    flexDirection: 'row',
  },
  infoLabel: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
    width: 80,
  },
  infoValue: {
    fontSize: FontSizes.md,
    color: Colors.text.primary,
    flex: 1,
  },
  emptyContainer: {
    padding: Spacing['2xl'],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
  },
});
