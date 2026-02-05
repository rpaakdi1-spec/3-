import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function MapScreen({ route }: any) {
  const { dispatch } = route.params;

  return (
    <View style={styles.container}>
      <View style={styles.placeholder}>
        <Ionicons name="map-outline" size={64} color="#9CA3AF" />
        <Text style={styles.placeholderText}>지도 화면</Text>
        <Text style={styles.placeholderSubtext}>
          React Native Maps를 통합하여{'\n'}
          실시간 경로 안내 제공
        </Text>
      </View>

      <View style={styles.info}>
        <Text style={styles.infoText}>출발: {dispatch.pickup_address}</Text>
        <Text style={styles.infoText}>도착: {dispatch.delivery_address}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  placeholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  placeholderText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
    marginTop: 16,
  },
  placeholderSubtext: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
  },
  info: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
  },
  infoText: {
    fontSize: 14,
    color: '#374151',
    marginVertical: 4,
  },
});
