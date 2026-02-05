import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface VehicleInfo {
  id: number;
  license_plate: string;
  type: string;
  status: string;
  fuel_level: number;
  mileage: number;
  next_maintenance: string;
}

export default function VehicleInfoScreen() {
  const [vehicle, setVehicle] = useState<VehicleInfo | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadVehicle();
  }, []);

  const loadVehicle = async () => {
    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(`${API_URL}/mobile/vehicle`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setVehicle(response.data);
    } catch (error) {
      console.error('Load vehicle error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return '#10B981';
      case 'MAINTENANCE':
        return '#F59E0B';
      case 'INACTIVE':
        return '#EF4444';
      default:
        return '#9CA3AF';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return '운행 중';
      case 'MAINTENANCE':
        return '정비 중';
      case 'INACTIVE':
        return '비활성';
      default:
        return status;
    }
  };

  if (!vehicle) {
    return (
      <View style={styles.container}>
        <View style={styles.empty}>
          <Ionicons name="car-outline" size={64} color="#9CA3AF" />
          <Text style={styles.emptyText}>차량 정보가 없습니다</Text>
        </View>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={loading} onRefresh={loadVehicle} />
      }
    >
      <View style={styles.content}>
        {/* 차량 개요 */}
        <View style={styles.header}>
          <View style={styles.vehicleIcon}>
            <Ionicons name="car" size={48} color="#3B82F6" />
          </View>
          <View style={styles.headerInfo}>
            <Text style={styles.licensePlate}>{vehicle.license_plate}</Text>
            <Text style={styles.vehicleType}>{vehicle.type}</Text>
            <View
              style={[
                styles.statusBadge,
                { backgroundColor: `${getStatusColor(vehicle.status)}15` },
              ]}
            >
              <Text
                style={[
                  styles.statusText,
                  { color: getStatusColor(vehicle.status) },
                ]}
              >
                {getStatusText(vehicle.status)}
              </Text>
            </View>
          </View>
        </View>

        {/* 정보 카드 */}
        <View style={styles.infoCards}>
          {/* 연료 */}
          <View style={[styles.infoCard, { backgroundColor: '#DBEAFE' }]}>
            <Ionicons name="water" size={32} color="#3B82F6" />
            <Text style={styles.infoValue}>{vehicle.fuel_level}%</Text>
            <Text style={styles.infoLabel}>연료 잔량</Text>
          </View>

          {/* 주행거리 */}
          <View style={[styles.infoCard, { backgroundColor: '#D1FAE5' }]}>
            <Ionicons name="speedometer" size={32} color="#10B981" />
            <Text style={styles.infoValue}>
              {vehicle.mileage.toLocaleString()}
            </Text>
            <Text style={styles.infoLabel}>주행거리 (km)</Text>
          </View>
        </View>

        {/* 다음 정비 */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="build-outline" size={24} color="#F59E0B" />
            <Text style={styles.cardTitle}>다음 정비 일정</Text>
          </View>
          <Text style={styles.maintenanceDate}>
            {new Date(vehicle.next_maintenance).toLocaleDateString('ko-KR')}
          </Text>
        </View>

        {/* 안내 */}
        <View style={styles.tipCard}>
          <Ionicons name="information-circle-outline" size={24} color="#3B82F6" />
          <View style={styles.tipContent}>
            <Text style={styles.tipTitle}>안전운행 팁</Text>
            <Text style={styles.tipText}>
              • 출발 전 차량 점검을 하세요{' \n'}
              • 제한속도를 준수하세요{' \n'}
              • 충분한 휴식을 취하세요
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 16,
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 48,
  },
  emptyText: {
    fontSize: 16,
    color: '#9CA3AF',
    marginTop: 16,
  },
  header: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
  },
  vehicleIcon: {
    width: 80,
    height: 80,
    backgroundColor: '#EFF6FF',
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerInfo: {
    flex: 1,
    marginLeft: 16,
  },
  licensePlate: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  vehicleType: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 8,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  infoCards: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  infoCard: {
    flex: 1,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
  },
  infoValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 8,
  },
  infoLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
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
  maintenanceDate: {
    fontSize: 18,
    fontWeight: '500',
    color: '#111827',
  },
  tipCard: {
    flexDirection: 'row',
    backgroundColor: '#EFF6FF',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
  },
  tipContent: {
    flex: 1,
    marginLeft: 12,
  },
  tipTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E40AF',
    marginBottom: 4,
  },
  tipText: {
    fontSize: 12,
    color: '#1E40AF',
    lineHeight: 18,
  },
});
