import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { format } from 'date-fns';
import ApiService from '../../services/api';
import { Dispatch, DispatchRoute, RouteType } from '../../types';

const DispatchDetailScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const { dispatchId } = route.params as { dispatchId: number };

  const [dispatch, setDispatch] = useState<Dispatch | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    loadDispatch();
  }, [dispatchId]);

  const loadDispatch = async () => {
    try {
      const data = await ApiService.getDispatchById(dispatchId);
      setDispatch(data);
    } catch (error) {
      Alert.alert('오류', '배차 정보를 불러오는데 실패했습니다.');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  const handleStartDispatch = async () => {
    Alert.alert(
      '배차 시작',
      '배차를 시작하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '시작',
          onPress: async () => {
            setUpdating(true);
            try {
              await ApiService.updateDispatchStatus(dispatchId, 'IN_PROGRESS');
              await loadDispatch();
              Alert.alert('완료', '배차가 시작되었습니다.');
            } catch (error) {
              Alert.alert('오류', '배차 시작에 실패했습니다.');
            } finally {
              setUpdating(false);
            }
          },
        },
      ]
    );
  };

  const handleCompleteDispatch = async () => {
    Alert.alert(
      '배차 완료',
      '모든 경로를 완료하셨습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '완료',
          onPress: async () => {
            setUpdating(true);
            try {
              await ApiService.updateDispatchStatus(dispatchId, 'COMPLETED');
              await loadDispatch();
              Alert.alert('완료', '배차가 완료되었습니다.');
            } catch (error) {
              Alert.alert('오류', '배차 완료 처리에 실패했습니다.');
            } finally {
              setUpdating(false);
            }
          },
        },
      ]
    );
  };

  const getRouteTypeText = (type: RouteType) => {
    const typeMap: Record<RouteType, string> = {
      GARAGE_START: '출발',
      PICKUP: '상차',
      DELIVERY: '하차',
      GARAGE_END: '복귀',
    };
    return typeMap[type] || type;
  };

  const getRouteTypeColor = (type: RouteType) => {
    const colorMap: Record<RouteType, string> = {
      GARAGE_START: '#666',
      PICKUP: '#007AFF',
      DELIVERY: '#34C759',
      GARAGE_END: '#666',
    };
    return colorMap[type] || '#666';
  };

  const renderRoute = (routeItem: DispatchRoute, index: number) => (
    <TouchableOpacity
      key={routeItem.id}
      style={styles.routeCard}
      onPress={() =>
        navigation.navigate('RouteDetail' as never, {
          dispatchId,
          routeId: routeItem.id,
        } as never)
      }>
      <View style={styles.routeHeader}>
        <View style={styles.sequenceBadge}>
          <Text style={styles.sequenceText}>{routeItem.sequence}</Text>
        </View>
        <View
          style={[
            styles.routeTypeBadge,
            { backgroundColor: getRouteTypeColor(routeItem.route_type) },
          ]}>
          <Text style={styles.routeTypeText}>
            {getRouteTypeText(routeItem.route_type)}
          </Text>
        </View>
        {routeItem.status && (
          <View style={styles.routeStatusBadge}>
            <Text style={styles.routeStatusText}>{routeItem.status}</Text>
          </View>
        )}
      </View>

      <Text style={styles.locationName}>{routeItem.location_name}</Text>
      <Text style={styles.address}>{routeItem.address}</Text>

      <View style={styles.routeInfo}>
        <Text style={styles.routeInfoText}>
          팔레트: {routeItem.current_pallets}개 | 중량: {routeItem.current_weight_kg}kg
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

  if (!dispatch) {
    return (
      <View style={styles.centerContainer}>
        <Text>배차 정보를 찾을 수 없습니다</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <Text style={styles.title}>{dispatch.dispatch_number}</Text>
          <Text style={styles.date}>
            {format(new Date(dispatch.dispatch_date), 'yyyy년 MM월 dd일')}
          </Text>
        </View>

        <View style={styles.summary}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>차량</Text>
            <Text style={styles.summaryValue}>{dispatch.vehicle_code}</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>주문</Text>
            <Text style={styles.summaryValue}>{dispatch.total_orders}건</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>팔레트</Text>
            <Text style={styles.summaryValue}>{dispatch.total_pallets}개</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>중량</Text>
            <Text style={styles.summaryValue}>
              {dispatch.total_weight_kg}kg
            </Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>경로 ({dispatch.routes.length}개)</Text>
          {dispatch.routes.map((routeItem, index) =>
            renderRoute(routeItem, index)
          )}
        </View>
      </ScrollView>

      <View style={styles.footer}>
        {dispatch.status === 'CONFIRMED' && (
          <TouchableOpacity
            style={[styles.actionButton, updating && styles.buttonDisabled]}
            onPress={handleStartDispatch}
            disabled={updating}>
            {updating ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.actionButtonText}>배차 시작</Text>
            )}
          </TouchableOpacity>
        )}

        {dispatch.status === 'IN_PROGRESS' && (
          <TouchableOpacity
            style={[
              styles.actionButton,
              styles.completeButton,
              updating && styles.buttonDisabled,
            ]}
            onPress={handleCompleteDispatch}
            disabled={updating}>
            {updating ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.actionButtonText}>배차 완료</Text>
            )}
          </TouchableOpacity>
        )}
      </View>
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
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  date: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  summary: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    padding: 15,
    marginTop: 10,
  },
  summaryItem: {
    flex: 1,
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  summaryValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  section: {
    marginTop: 10,
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  routeCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  routeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  sequenceBadge: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  sequenceText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  routeTypeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
    marginRight: 10,
  },
  routeTypeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  routeStatusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
    backgroundColor: '#f0f0f0',
  },
  routeStatusText: {
    fontSize: 11,
    color: '#666',
  },
  locationName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  address: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  routeInfo: {
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 10,
  },
  routeInfoText: {
    fontSize: 13,
    color: '#666',
  },
  footer: {
    backgroundColor: '#fff',
    padding: 15,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  actionButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  completeButton: {
    backgroundColor: '#34C759',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default DispatchDetailScreen;
