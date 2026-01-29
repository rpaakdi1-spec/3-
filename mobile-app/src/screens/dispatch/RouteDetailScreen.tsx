import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  TextInput,
  Image,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { format } from 'date-fns';
import ApiService from '../../services/api';
import { DispatchRoute, RouteStatus } from '../../types';

const RouteDetailScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const { dispatchId, routeId } = route.params as {
    dispatchId: number;
    routeId: number;
  };

  const [routeData, setRouteData] = useState<DispatchRoute | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [notes, setNotes] = useState('');
  const [photos, setPhotos] = useState<string[]>([]);

  useEffect(() => {
    loadRouteData();
  }, [routeId]);

  const loadRouteData = async () => {
    try {
      // In real app, this should fetch route details
      // For now, we'll fetch dispatch and find the route
      const dispatch = await ApiService.getDispatchById(dispatchId);
      const foundRoute = dispatch.routes.find((r: DispatchRoute) => r.id === routeId);
      
      if (foundRoute) {
        setRouteData(foundRoute);
        setNotes(foundRoute.notes || '');
        setPhotos(foundRoute.photos?.map(p => p.photo_url) || []);
      }
    } catch (error) {
      Alert.alert('오류', '경로 정보를 불러오는데 실패했습니다.');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  const handleArrive = async () => {
    Alert.alert(
      '도착 확인',
      '이 위치에 도착하셨습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '도착',
          onPress: async () => {
            setUpdating(true);
            try {
              const arrivalTime = new Date().toISOString();
              await ApiService.updateRouteStatus(
                dispatchId,
                routeId,
                'ARRIVED',
                arrivalTime
              );
              await loadRouteData();
              Alert.alert('완료', '도착 처리되었습니다.');
            } catch (error) {
              Alert.alert('오류', '도착 처리에 실패했습니다.');
            } finally {
              setUpdating(false);
            }
          },
        },
      ]
    );
  };

  const handleStartWork = async () => {
    setUpdating(true);
    try {
      await ApiService.updateRouteStatus(
        dispatchId,
        routeId,
        'IN_PROGRESS'
      );
      await loadRouteData();
      Alert.alert('완료', '작업을 시작했습니다.');
    } catch (error) {
      Alert.alert('오류', '작업 시작 처리에 실패했습니다.');
    } finally {
      setUpdating(false);
    }
  };

  const handleComplete = async () => {
    if (routeData?.route_type === 'PICKUP' || routeData?.route_type === 'DELIVERY') {
      if (photos.length === 0) {
        Alert.alert('알림', '사진을 촬영해주세요.');
        return;
      }
    }

    Alert.alert(
      '작업 완료',
      '이 작업을 완료하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '완료',
          onPress: async () => {
            setUpdating(true);
            try {
              const departureTime = new Date().toISOString();
              await ApiService.updateRouteStatus(
                dispatchId,
                routeId,
                'COMPLETED',
                undefined,
                departureTime
              );
              await loadRouteData();
              Alert.alert('완료', '작업이 완료되었습니다.', [
                {
                  text: '확인',
                  onPress: () => navigation.goBack(),
                },
              ]);
            } catch (error) {
              Alert.alert('오류', '작업 완료 처리에 실패했습니다.');
            } finally {
              setUpdating(false);
            }
          },
        },
      ]
    );
  };

  const handleTakePhoto = () => {
    const photoType = routeData?.route_type === 'PICKUP' ? 'pickup' : 'delivery';
    navigation.navigate('Camera' as never, {
      dispatchId,
      routeId,
      photoType,
    } as never);
  };

  const getStatusText = (status?: RouteStatus) => {
    const statusMap: Record<string, string> = {
      PENDING: '대기',
      ARRIVED: '도착',
      IN_PROGRESS: '진행중',
      COMPLETED: '완료',
      SKIPPED: '건너뜀',
    };
    return status ? statusMap[status] || status : '대기';
  };

  const getRouteTypeText = (type: string) => {
    const typeMap: Record<string, string> = {
      GARAGE_START: '출발',
      PICKUP: '상차',
      DELIVERY: '하차',
      GARAGE_END: '복귀',
    };
    return typeMap[type] || type;
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (!routeData) {
    return (
      <View style={styles.centerContainer}>
        <Text>경로 정보를 찾을 수 없습니다</Text>
      </View>
    );
  }

  const showArriveButton = !routeData.status || routeData.status === 'PENDING';
  const showStartButton = routeData.status === 'ARRIVED';
  const showCompleteButton = routeData.status === 'IN_PROGRESS';
  const needsPhoto = routeData.route_type === 'PICKUP' || routeData.route_type === 'DELIVERY';

  return (
    <View style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <View style={styles.sequenceBadge}>
            <Text style={styles.sequenceText}>{routeData.sequence}</Text>
          </View>
          <View style={styles.headerText}>
            <Text style={styles.routeType}>
              {getRouteTypeText(routeData.route_type)}
            </Text>
            <Text style={styles.status}>{getStatusText(routeData.status)}</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>위치 정보</Text>
          <Text style={styles.locationName}>{routeData.location_name}</Text>
          <Text style={styles.address}>{routeData.address}</Text>
          {routeData.latitude && routeData.longitude && (
            <Text style={styles.coordinates}>
              좌표: {routeData.latitude.toFixed(4)}, {routeData.longitude.toFixed(4)}
            </Text>
          )}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>화물 정보</Text>
          <View style={styles.infoRow}>
            <Text style={styles.label}>현재 팔레트:</Text>
            <Text style={styles.value}>{routeData.current_pallets}개</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.label}>현재 중량:</Text>
            <Text style={styles.value}>{routeData.current_weight_kg}kg</Text>
          </View>
          {routeData.estimated_work_duration_minutes && (
            <View style={styles.infoRow}>
              <Text style={styles.label}>예상 작업 시간:</Text>
              <Text style={styles.value}>
                {routeData.estimated_work_duration_minutes}분
              </Text>
            </View>
          )}
        </View>

        {routeData.actual_arrival_time && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>시간 기록</Text>
            <View style={styles.infoRow}>
              <Text style={styles.label}>도착 시간:</Text>
              <Text style={styles.value}>
                {format(new Date(routeData.actual_arrival_time), 'HH:mm')}
              </Text>
            </View>
            {routeData.actual_departure_time && (
              <View style={styles.infoRow}>
                <Text style={styles.label}>출발 시간:</Text>
                <Text style={styles.value}>
                  {format(new Date(routeData.actual_departure_time), 'HH:mm')}
                </Text>
              </View>
            )}
          </View>
        )}

        {needsPhoto && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>사진 ({photos.length}장)</Text>
            {photos.length > 0 && (
              <View style={styles.photoGrid}>
                {photos.map((photoUri, index) => (
                  <Image
                    key={index}
                    source={{ uri: photoUri }}
                    style={styles.photo}
                  />
                ))}
              </View>
            )}
            {routeData.status === 'IN_PROGRESS' && (
              <TouchableOpacity
                style={styles.photoButton}
                onPress={handleTakePhoto}>
                <Text style={styles.photoButtonText}>📷 사진 촬영</Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>메모</Text>
          <TextInput
            style={styles.notesInput}
            placeholder="메모를 입력하세요..."
            value={notes}
            onChangeText={setNotes}
            multiline
            numberOfLines={4}
            editable={routeData.status !== 'COMPLETED'}
          />
        </View>
      </ScrollView>

      <View style={styles.footer}>
        {showArriveButton && (
          <TouchableOpacity
            style={[styles.actionButton, updating && styles.buttonDisabled]}
            onPress={handleArrive}
            disabled={updating}>
            {updating ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.actionButtonText}>도착</Text>
            )}
          </TouchableOpacity>
        )}

        {showStartButton && (
          <TouchableOpacity
            style={[
              styles.actionButton,
              styles.startButton,
              updating && styles.buttonDisabled,
            ]}
            onPress={handleStartWork}
            disabled={updating}>
            {updating ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.actionButtonText}>작업 시작</Text>
            )}
          </TouchableOpacity>
        )}

        {showCompleteButton && (
          <TouchableOpacity
            style={[
              styles.actionButton,
              styles.completeButton,
              updating && styles.buttonDisabled,
            ]}
            onPress={handleComplete}
            disabled={updating}>
            {updating ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.actionButtonText}>작업 완료</Text>
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
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  sequenceBadge: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  sequenceText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  headerText: {
    flex: 1,
  },
  routeType: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  status: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  section: {
    backgroundColor: '#fff',
    padding: 20,
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  locationName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  address: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  coordinates: {
    fontSize: 12,
    color: '#999',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
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
  photoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 15,
  },
  photo: {
    width: 100,
    height: 100,
    borderRadius: 8,
    marginRight: 10,
    marginBottom: 10,
  },
  photoButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
  },
  photoButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  notesInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 10,
    fontSize: 14,
    minHeight: 100,
    textAlignVertical: 'top',
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
  startButton: {
    backgroundColor: '#FF9500',
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

export default RouteDetailScreen;
