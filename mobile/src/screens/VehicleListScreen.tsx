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
import vehicleService from '@services/vehicleService';
import { Vehicle } from '@types/index';
import { Colors, FontSizes, Spacing, BorderRadius, Shadows, StatusColors, StatusLabels, VehicleTypeLabels } from '@utils/constants';

export default function VehicleListScreen() {
  const navigation = useNavigation();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadVehicles = useCallback(async () => {
    try {
      const response = await vehicleService.getVehicles({ page: 1, size: 50 });
      setVehicles(response.items);
    } catch (error) {
      console.error('Failed to load vehicles:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadVehicles();
    const interval = setInterval(loadVehicles, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [loadVehicles]);

  const onRefresh = () => {
    setRefreshing(true);
    loadVehicles();
  };

  const renderItem = ({ item }: { item: Vehicle }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => navigation.navigate('VehicleDetail', { vehicleId: item.id })}
    >
      <View style={styles.cardHeader}>
        <View>
          <Text style={styles.vehiclePlate}>{item.vehicle_plate_number}</Text>
          <Text style={styles.vehicleNumber}>{item.vehicle_number}</Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: StatusColors.vehicle[item.status] }]}>
          <Text style={styles.statusText}>{StatusLabels.vehicle[item.status]}</Text>
        </View>
      </View>
      
      <View style={styles.cardBody}>
        <InfoRow label="차종" value={VehicleTypeLabels[item.vehicle_type]} />
        <InfoRow label="용량" value={`${item.capacity_kg} kg`} />
        
        {item.temperature && (
          <View style={styles.temperatureRow}>
            <Text style={styles.infoLabel}>온도:</Text>
            <View style={styles.temperatureContainer}>
              <TemperatureChip label="A" value={item.temperature.temperature_a} />
              <TemperatureChip label="B" value={item.temperature.temperature_b} />
            </View>
          </View>
        )}
        
        {item.current_location && (
          <InfoRow 
            label="속도" 
            value={`${item.current_location.speed_kmh.toFixed(0)} km/h`} 
          />
        )}
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
        <Text style={styles.title}>차량 관리</Text>
        <Text style={styles.subtitle}>{vehicles.length}대</Text>
      </View>
      
      <FlatList
        data={vehicles}
        renderItem={renderItem}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
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

interface TemperatureChipProps {
  label: string;
  value: number | null;
}

function TemperatureChip({ label, value }: TemperatureChipProps) {
  const getColor = (temp: number | null) => {
    if (temp === null) return Colors.gray[400];
    if (temp < -20) return Colors.info;
    if (temp < -15) return Colors.primary;
    if (temp < 5) return Colors.success;
    if (temp < 10) return Colors.warning;
    return Colors.danger;
  };

  return (
    <View style={[styles.tempChip, { backgroundColor: getColor(value) }]}>
      <Text style={styles.tempLabel}>{label}</Text>
      <Text style={styles.tempValue}>{value !== null ? `${value.toFixed(1)}°C` : 'N/A'}</Text>
    </View>
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
  subtitle: {
    fontSize: FontSizes.md,
    color: Colors.text.secondary,
    marginTop: Spacing.xs,
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
    alignItems: 'flex-start',
    marginBottom: Spacing.md,
  },
  vehiclePlate: {
    fontSize: FontSizes.xl,
    fontWeight: 'bold',
    color: Colors.text.primary,
  },
  vehicleNumber: {
    fontSize: FontSizes.sm,
    color: Colors.text.secondary,
    marginTop: Spacing.xs,
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
    width: 60,
  },
  infoValue: {
    fontSize: FontSizes.md,
    color: Colors.text.primary,
    flex: 1,
  },
  temperatureRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  temperatureContainer: {
    flexDirection: 'row',
    gap: Spacing.sm,
    flex: 1,
  },
  tempChip: {
    flex: 1,
    padding: Spacing.sm,
    borderRadius: BorderRadius.sm,
    alignItems: 'center',
  },
  tempLabel: {
    color: Colors.white,
    fontSize: FontSizes.xs,
    fontWeight: '600',
  },
  tempValue: {
    color: Colors.white,
    fontSize: FontSizes.md,
    fontWeight: 'bold',
    marginTop: Spacing.xs,
  },
});
