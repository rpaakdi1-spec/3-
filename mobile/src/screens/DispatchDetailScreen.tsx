import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRoute, useNavigation } from '@react-navigation/native';
import dispatchService from '@services/dispatchService';
import gpsService from '@services/gpsService';
import cameraService from '@services/cameraService';
import { Dispatch } from '@types/index';
import { Colors, FontSizes, Spacing, BorderRadius, Shadows, StatusColors, StatusLabels } from '@utils/constants';

export default function DispatchDetailScreen() {
  const route = useRoute();
  const navigation = useNavigation();
  const { dispatchId } = route.params as { dispatchId: number };
  
  const [dispatch, setDispatch] = useState<Dispatch | null>(null);
  const [loading, setLoading] = useState(true);
  const [isGPSTracking, setIsGPSTracking] = useState(false);
  const [pickupPhoto, setPickupPhoto] = useState<string | null>(null);
  const [deliveryPhoto, setDeliveryPhoto] = useState<string | null>(null);

  useEffect(() => {
    loadDispatch();
    checkGPSTracking();
  }, [dispatchId]);

  useEffect(() => {
    // 배차가 진행 중이면 GPS 추적 자동 시작
    if (dispatch?.status === 'in_progress' && dispatch.vehicle_id && !isGPSTracking) {
      startGPSTracking();
    }
  }, [dispatch?.status]);

  const loadDispatch = async () => {
    try {
      const data = await dispatchService.getDispatch(dispatchId);
      setDispatch(data);
    } catch (error) {
      console.error('Failed to load dispatch:', error);
      Alert.alert('오류', '배차 정보를 불러올 수 없습니다');
    } finally {
      setLoading(false);
    }
  };

  const checkGPSTracking = () => {
    setIsGPSTracking(gpsService.isActive());
  };

  const startGPSTracking = async () => {
    if (!dispatch?.vehicle_id) {
      Alert.alert('오류', '차량 정보가 없습니다');
      return;
    }

    try {
      await gpsService.startTracking(dispatch.vehicle_id);
      setIsGPSTracking(true);
      Alert.alert('성공', 'GPS 추적이 시작되었습니다');
    } catch (error) {
      Alert.alert('오류', 'GPS 추적을 시작할 수 없습니다');
    }
  };

  const stopGPSTracking = async () => {
    try {
      await gpsService.stopTracking();
      setIsGPSTracking(false);
      Alert.alert('성공', 'GPS 추적이 중지되었습니다');
    } catch (error) {
      Alert.alert('오류', 'GPS 추적 중지에 실패했습니다');
    }
  };

  const takePickupPhoto = async () => {
    try {
      const photo = await cameraService.takePicture();
      if (photo) {
        setPickupPhoto(photo.uri);
        
        // 서버에 업로드
        const result = await cameraService.uploadDeliveryProof(
          dispatchId,
          photo,
          'pickup'
        );
        
        if (result.success) {
          Alert.alert('성공', '픽업 사진이 업로드되었습니다');
        } else {
          Alert.alert('알림', '오프라인 모드: 사진이 나중에 업로드됩니다');
        }
      }
    } catch (error) {
      Alert.alert('오류', '사진 촬영에 실패했습니다');
    }
  };

  const takeDeliveryPhoto = async () => {
    try {
      const photo = await cameraService.takePicture();
      if (photo) {
        setDeliveryPhoto(photo.uri);
        
        // 서버에 업로드
        const result = await cameraService.uploadDeliveryProof(
          dispatchId,
          photo,
          'delivery'
        );
        
        if (result.success) {
          Alert.alert('성공', '배송 사진이 업로드되었습니다');
        } else {
          Alert.alert('알림', '오프라인 모드: 사진이 나중에 업로드됩니다');
        }
      }
    } catch (error) {
      Alert.alert('오류', '사진 촬영에 실패했습니다');
    }
  };

  const updateStatus = async (newStatus: Dispatch['status']) => {
    // 상태별 필수 조건 확인
    if (newStatus === 'in_progress') {
      if (!pickupPhoto) {
        Alert.alert('알림', '픽업 사진을 먼저 촬영해주세요');
        return;
      }
    }

    if (newStatus === 'completed') {
      if (!deliveryPhoto) {
        Alert.alert('알림', '배송 사진을 먼저 촬영해주세요');
        return;
      }
      
      // GPS 추적 중지
      if (isGPSTracking) {
        await stopGPSTracking();
      }
    }

    try {
      await dispatchService.updateDispatchStatus(dispatchId, newStatus);
      await loadDispatch();
      Alert.alert('성공', '상태가 업데이트되었습니다');
    } catch (error) {
      Alert.alert('오류', '상태 업데이트에 실패했습니다');
    }
  };

  const acceptDispatch = async () => {
    Alert.alert(
      '배차 수락',
      '이 배차를 수락하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '수락',
          onPress: async () => {
            await updateStatus('assigned');
          },
        },
      ]
    );
  };

  const rejectDispatch = async () => {
    Alert.alert(
      '배차 거절',
      '이 배차를 거절하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '거절',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatchService.rejectDispatch(dispatchId);
              Alert.alert('성공', '배차가 거절되었습니다');
              navigation.goBack();
            } catch (error) {
              Alert.alert('오류', '배차 거절에 실패했습니다');
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  if (!dispatch) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.errorText}>배차 정보를 찾을 수 없습니다</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.dispatchNumber}>{dispatch.dispatch_number}</Text>
          <View style={[styles.statusBadge, { backgroundColor: StatusColors.dispatch[dispatch.status] }]}>
            <Text style={styles.statusText}>{StatusLabels.dispatch[dispatch.status]}</Text>
          </View>
        </View>

        {/* Vehicle Info */}
        <Section title="차량 정보">
          {dispatch.vehicle ? (
            <>
              <InfoRow label="차량 번호" value={dispatch.vehicle.vehicle_plate_number} />
              <InfoRow label="차량 종류" value={dispatch.vehicle.vehicle_type} />
              <InfoRow label="용량" value={`${dispatch.vehicle.capacity_kg} kg`} />
            </>
          ) : (
            <Text style={styles.emptyText}>차량이 배정되지 않았습니다</Text>
          )}
        </Section>

        {/* Driver Info */}
        <Section title="운전자 정보">
          {dispatch.driver ? (
            <>
              <InfoRow label="이름" value={dispatch.driver.driver_name} />
              <InfoRow label="전화번호" value={dispatch.driver.phone} />
              <InfoRow label="평점" value={`${dispatch.driver.rating.toFixed(1)} ⭐`} />
            </>
          ) : (
            <Text style={styles.emptyText}>운전자가 배정되지 않았습니다</Text>
          )}
        </Section>

        {/* Schedule Info */}
        <Section title="일정 정보">
          <InfoRow label="픽업 예정" value={formatDateTime(dispatch.scheduled_pickup_time)} />
          <InfoRow label="배송 예정" value={formatDateTime(dispatch.scheduled_delivery_time)} />
          {dispatch.actual_pickup_time && (
            <InfoRow label="실제 픽업" value={formatDateTime(dispatch.actual_pickup_time)} />
          )}
          {dispatch.actual_delivery_time && (
            <InfoRow label="실제 배송" value={formatDateTime(dispatch.actual_delivery_time)} />
          )}
        </Section>

        {/* Order Info */}
        {dispatch.order && (
          <Section title="주문 정보">
            <InfoRow label="주문 번호" value={dispatch.order.order_number} />
            <InfoRow label="픽업 위치" value={dispatch.order.pickup_location} />
            <InfoRow label="배송 위치" value={dispatch.order.delivery_location} />
            <InfoRow label="무게" value={`${dispatch.order.weight_kg} kg`} />
            {dispatch.order.required_temperature_min && (
              <InfoRow 
                label="온도 범위" 
                value={`${dispatch.order.required_temperature_min}°C ~ ${dispatch.order.required_temperature_max}°C`} 
              />
            )}
          </Section>
        )}

        {/* GPS Tracking Status */}
        {dispatch.status === 'in_progress' && (
          <View style={styles.gpsSection}>
            <View style={styles.gpsHeader}>
              <Text style={styles.gpsTitleText}>GPS 추적</Text>
              <View style={[styles.gpsStatusBadge, isGPSTracking ? styles.gpsActive : styles.gpsInactive]}>
                <Text style={styles.gpsStatusText}>
                  {isGPSTracking ? '활성' : '비활성'}
                </Text>
              </View>
            </View>
            {!isGPSTracking && (
              <TouchableOpacity style={styles.gpsButton} onPress={startGPSTracking}>
                <Text style={styles.gpsButtonText}>GPS 추적 시작</Text>
              </TouchableOpacity>
            )}
            {isGPSTracking && (
              <TouchableOpacity 
                style={[styles.gpsButton, styles.gpsStopButton]} 
                onPress={stopGPSTracking}
              >
                <Text style={styles.gpsButtonText}>GPS 추적 중지</Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        {/* Photos Section */}
        <Section title="배송 증명">
          <View style={styles.photosContainer}>
            <View style={styles.photoItem}>
              <Text style={styles.photoLabel}>픽업 사진</Text>
              {pickupPhoto ? (
                <Image source={{ uri: pickupPhoto }} style={styles.photo} />
              ) : (
                <TouchableOpacity style={styles.photoPlaceholder} onPress={takePickupPhoto}>
                  <Text style={styles.photoPlaceholderText}>📷 촬영하기</Text>
                </TouchableOpacity>
              )}
            </View>
            <View style={styles.photoItem}>
              <Text style={styles.photoLabel}>배송 사진</Text>
              {deliveryPhoto ? (
                <Image source={{ uri: deliveryPhoto }} style={styles.photo} />
              ) : (
                <TouchableOpacity 
                  style={styles.photoPlaceholder} 
                  onPress={takeDeliveryPhoto}
                  disabled={dispatch.status !== 'in_progress'}
                >
                  <Text style={styles.photoPlaceholderText}>
                    {dispatch.status === 'in_progress' ? '📷 촬영하기' : '운송 시작 후 촬영'}
                  </Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        </Section>

        {/* Actions */}
        <View style={styles.actionsContainer}>
          {dispatch.status === 'pending' && (
            <>
              <ActionButton
                title="배차 수락"
                color={Colors.primary}
                onPress={acceptDispatch}
              />
              <ActionButton
                title="배차 거절"
                color={Colors.error}
                onPress={rejectDispatch}
              />
            </>
          )}
          {dispatch.status === 'assigned' && (
            <ActionButton
              title="운송 시작"
              color={Colors.success}
              onPress={() => updateStatus('in_progress')}
              disabled={!pickupPhoto}
            />
          )}
          {dispatch.status === 'in_progress' && (
            <ActionButton
              title="완료 처리"
              color={Colors.success}
              onPress={() => updateStatus('completed')}
              disabled={!deliveryPhoto}
            />
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

function Section({ title, children }: SectionProps) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.sectionContent}>
        {children}
      </View>
    </View>
  );
}

interface InfoRowProps {
  label: string;
  value: string;
}

function InfoRow({ label, value }: InfoRowProps) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

interface ActionButtonProps {
  title: string;
  color: string;
  onPress: () => void;
  disabled?: boolean;
}

function ActionButton({ title, color, onPress, disabled = false }: ActionButtonProps) {
  return (
    <TouchableOpacity
      style={[
        styles.actionButton, 
        { backgroundColor: disabled ? Colors.border : color }
      ]}
      onPress={onPress}
      disabled={disabled}
    >
      <Text style={styles.actionButtonText}>{title}</Text>
    </TouchableOpacity>
  );
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR');
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
  errorText: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    backgroundColor: Colors.white,
    padding: Spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dispatchNumber: {
    fontSize: FontSizes['2xl'],
    fontWeight: 'bold',
    color: Colors.text.primary,
  },
  statusBadge: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
  },
  statusText: {
    color: Colors.white,
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
  section: {
    backgroundColor: Colors.white,
    marginTop: Spacing.md,
    padding: Spacing.lg,
  },
  sectionTitle: {
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
    color: Colors.text.primary,
    marginBottom: Spacing.md,
  },
  sectionContent: {
    gap: Spacing.sm,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: Spacing.xs,
  },
  infoLabel: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
  },
  infoValue: {
    fontSize: FontSizes.md,
    color: Colors.text.primary,
    fontWeight: '500',
  },
  emptyText: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
    fontStyle: 'italic',
  },
  actionsContainer: {
    padding: Spacing.lg,
    gap: Spacing.md,
  },
  actionButton: {
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    ...Shadows.sm,
  },
  actionButtonText: {
    color: Colors.white,
    fontSize: FontSizes.lg,
    fontWeight: '600',
  },
  gpsSection: {
    backgroundColor: Colors.white,
    marginTop: Spacing.md,
    padding: Spacing.lg,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  gpsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  gpsTitleText: {
    fontSize: FontSizes.lg,
    fontWeight: 'bold',
    color: Colors.text.primary,
  },
  gpsStatusBadge: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.sm,
  },
  gpsActive: {
    backgroundColor: Colors.success,
  },
  gpsInactive: {
    backgroundColor: Colors.text.secondary,
  },
  gpsStatusText: {
    color: Colors.white,
    fontSize: FontSizes.sm,
    fontWeight: '600',
  },
  gpsButton: {
    backgroundColor: Colors.primary,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
  },
  gpsStopButton: {
    backgroundColor: Colors.error,
  },
  gpsButtonText: {
    color: Colors.white,
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
  photosContainer: {
    flexDirection: 'row',
    gap: Spacing.md,
  },
  photoItem: {
    flex: 1,
  },
  photoLabel: {
    fontSize: FontSizes.md,
    fontWeight: '600',
    color: Colors.text.primary,
    marginBottom: Spacing.sm,
  },
  photo: {
    width: '100%',
    height: 150,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.background,
  },
  photoPlaceholder: {
    width: '100%',
    height: 150,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.background,
    borderWidth: 2,
    borderColor: Colors.border,
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
  },
  photoPlaceholderText: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
  },
});
