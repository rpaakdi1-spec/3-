import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Linking,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface DispatchDetail {
  id: number;
  order_id: number;
  vehicle_id: number;
  status: string;
  pickup_address: string;
  pickup_contact: string;
  delivery_address: string;
  delivery_contact: string;
  scheduled_time: string;
  notes: string;
}

export default function DispatchDetailScreen({ route, navigation }: any) {
  const { id } = route.params;
  const [dispatch, setDispatch] = useState<DispatchDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDispatch();
  }, [id]);

  const loadDispatch = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(`${API_URL}/mobile/dispatches/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDispatch(response.data);
    } catch (error) {
      console.error('Load dispatch error:', error);
      Alert.alert('오류', '배차 정보를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleCall = (phone: string) => {
    Linking.openURL(`tel:${phone}`);
  };

  const handleStatusUpdate = async (newStatus: string) => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      await axios.put(
        `${API_URL}/mobile/dispatches/${id}/status`,
        { status: newStatus },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      Alert.alert('성공', '상태가 업데이트되었습니다.');
      loadDispatch();
    } catch (error) {
      console.error('Update status error:', error);
      Alert.alert('오류', '상태 업데이트에 실패했습니다.');
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

  if (loading) {
    return (
      <View style={styles.loading}>
        <Text>로딩 중...</Text>
      </View>
    );
  }

  if (!dispatch) {
    return (
      <View style={styles.loading}>
        <Text>배차 정보를 찾을 수 없습니다.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.content}>
        {/* 상태 */}
        <View style={styles.statusCard}>
          <Text style={styles.label}>현재 상태</Text>
          <View
            style={[
              styles.statusBadge,
              { backgroundColor: `${getStatusColor(dispatch.status)}15` },
            ]}
          >
            <View
              style={[
                styles.statusDot,
                { backgroundColor: getStatusColor(dispatch.status) },
              ]}
            />
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

        {/* 출발지 */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="location" size={24} color="#3B82F6" />
            <Text style={styles.cardTitle}>출발지</Text>
          </View>
          <Text style={styles.address}>{dispatch.pickup_address}</Text>
          <TouchableOpacity
            style={styles.contactButton}
            onPress={() => handleCall(dispatch.pickup_contact)}
          >
            <Ionicons name="call-outline" size={20} color="#3B82F6" />
            <Text style={styles.contactText}>{dispatch.pickup_contact}</Text>
          </TouchableOpacity>
        </View>

        {/* 경로 표시 */}
        <View style={styles.routeIndicator}>
          <View style={styles.routeLine} />
        </View>

        {/* 도착지 */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="flag" size={24} color="#10B981" />
            <Text style={styles.cardTitle}>도착지</Text>
          </View>
          <Text style={styles.address}>{dispatch.delivery_address}</Text>
          <TouchableOpacity
            style={styles.contactButton}
            onPress={() => handleCall(dispatch.delivery_contact)}
          >
            <Ionicons name="call-outline" size={20} color="#10B981" />
            <Text style={styles.contactText}>{dispatch.delivery_contact}</Text>
          </TouchableOpacity>
        </View>

        {/* 일정 */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="time-outline" size={24} color="#F59E0B" />
            <Text style={styles.cardTitle}>예정 시간</Text>
          </View>
          <Text style={styles.scheduleText}>
            {new Date(dispatch.scheduled_time).toLocaleString('ko-KR')}
          </Text>
        </View>

        {/* 특이사항 */}
        {dispatch.notes && (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Ionicons name="document-text-outline" size={24} color="#6B7280" />
              <Text style={styles.cardTitle}>특이사항</Text>
            </View>
            <Text style={styles.notesText}>{dispatch.notes}</Text>
          </View>
        )}

        {/* 지도 보기 버튼 */}
        <TouchableOpacity
          style={styles.mapButton}
          onPress={() => navigation.navigate('Map', { dispatch })}
        >
          <Ionicons name="map-outline" size={20} color="#FFFFFF" />
          <Text style={styles.mapButtonText}>경로 보기</Text>
        </TouchableOpacity>
      </ScrollView>

      {/* 하단 액션 버튼 */}
      <View style={styles.actions}>
        {dispatch.status === 'PENDING' && (
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: '#3B82F6' }]}
            onPress={() => handleStatusUpdate('IN_PROGRESS')}
          >
            <Text style={styles.actionButtonText}>픽업 완료</Text>
          </TouchableOpacity>
        )}
        {dispatch.status === 'IN_PROGRESS' && (
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: '#10B981' }]}
            onPress={() => handleStatusUpdate('COMPLETED')}
          >
            <Text style={styles.actionButtonText}>배송 완료</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  statusCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    alignItems: 'center',
  },
  label: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginLeft: 8,
  },
  address: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 12,
    lineHeight: 20,
  },
  contactButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
  },
  contactText: {
    fontSize: 14,
    color: '#111827',
    marginLeft: 8,
  },
  routeIndicator: {
    alignItems: 'center',
    marginVertical: -8,
    zIndex: 1,
  },
  routeLine: {
    width: 2,
    height: 32,
    backgroundColor: '#E5E7EB',
  },
  scheduleText: {
    fontSize: 16,
    color: '#111827',
    fontWeight: '500',
  },
  notesText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  mapButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#3B82F6',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  mapButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  actions: {
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  actionButton: {
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
