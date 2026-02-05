import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Switch,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function SettingsScreen({ navigation }: any) {
  const [pushEnabled, setPushEnabled] = useState(true);
  const [locationEnabled, setLocationEnabled] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  const handleLogout = async () => {
    Alert.alert(
      '로그아웃',
      '정말 로그아웃 하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '로그아웃',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.multiRemove(['auth_token', 'token_type']);
              navigation.replace('Auth');
            } catch (error) {
              console.error('Logout error:', error);
            }
          },
        },
      ]
    );
  };

  const SettingItem = ({
    icon,
    title,
    subtitle,
    onPress,
    rightElement,
  }: any) => (
    <TouchableOpacity style={styles.settingItem} onPress={onPress}>
      <View style={styles.settingLeft}>
        <Ionicons name={icon} size={24} color="#3B82F6" />
        <View style={styles.settingText}>
          <Text style={styles.settingTitle}>{title}</Text>
          {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
        </View>
      </View>
      {rightElement || <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />}
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* 프로필 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>계정</Text>
          <View style={styles.card}>
            <SettingItem
              icon="person-outline"
              title="프로필"
              subtitle="개인정보 수정"
              onPress={() => {}}
            />
            <View style={styles.divider} />
            <SettingItem
              icon="key-outline"
              title="비밀번호 변경"
              onPress={() => {}}
            />
          </View>
        </View>

        {/* 알림 설정 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>알림</Text>
          <View style={styles.card}>
            <SettingItem
              icon="notifications-outline"
              title="푸시 알림"
              subtitle="배차 및 긴급 알림"
              rightElement={
                <Switch
                  value={pushEnabled}
                  onValueChange={setPushEnabled}
                  trackColor={{ false: '#E5E7EB', true: '#93C5FD' }}
                  thumbColor={pushEnabled ? '#3B82F6' : '#f4f3f4'}
                />
              }
            />
          </View>
        </View>

        {/* 권한 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>권한</Text>
          <View style={styles.card}>
            <SettingItem
              icon="location-outline"
              title="위치 서비스"
              subtitle="실시간 추적"
              rightElement={
                <Switch
                  value={locationEnabled}
                  onValueChange={setLocationEnabled}
                  trackColor={{ false: '#E5E7EB', true: '#93C5FD' }}
                  thumbColor={locationEnabled ? '#3B82F6' : '#f4f3f4'}
                />
              }
            />
            <View style={styles.divider} />
            <SettingItem
              icon="camera-outline"
              title="카메라"
              subtitle="배송 증빙"
              onPress={() => {}}
            />
          </View>
        </View>

        {/* 앱 설정 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>앱 설정</Text>
          <View style={styles.card}>
            <SettingItem
              icon="language-outline"
              title="언어"
              subtitle="한국어"
              onPress={() => {}}
            />
            <View style={styles.divider} />
            <SettingItem
              icon="moon-outline"
              title="다크 모드"
              rightElement={
                <Switch
                  value={darkMode}
                  onValueChange={setDarkMode}
                  trackColor={{ false: '#E5E7EB', true: '#93C5FD' }}
                  thumbColor={darkMode ? '#3B82F6' : '#f4f3f4'}
                />
              }
            />
          </View>
        </View>

        {/* 지원 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>지원</Text>
          <View style={styles.card}>
            <SettingItem
              icon="help-circle-outline"
              title="도움말"
              onPress={() => {}}
            />
            <View style={styles.divider} />
            <SettingItem
              icon="information-circle-outline"
              title="앱 정보"
              subtitle="버전 1.0.0"
              onPress={() => {}}
            />
            <View style={styles.divider} />
            <SettingItem
              icon="document-text-outline"
              title="이용약관"
              onPress={() => {}}
            />
            <View style={styles.divider} />
            <SettingItem
              icon="shield-outline"
              title="개인정보처리방침"
              onPress={() => {}}
            />
          </View>
        </View>

        {/* 로그아웃 */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Ionicons name="log-out-outline" size={20} color="#EF4444" />
          <Text style={styles.logoutText}>로그아웃</Text>
        </TouchableOpacity>

        {/* 푸터 */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>UVIS 물류 드라이버 앱</Text>
          <Text style={styles.footerText}>© 2026 All rights reserved</Text>
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
    paddingTop: 60,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 8,
    marginLeft: 4,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    overflow: 'hidden',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 12,
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    color: '#111827',
    fontWeight: '500',
  },
  settingSubtitle: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginLeft: 52,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#EF4444',
    marginLeft: 8,
  },
  footer: {
    alignItems: 'center',
    marginTop: 32,
    marginBottom: 16,
  },
  footerText: {
    fontSize: 12,
    color: '#9CA3AF',
    marginVertical: 2,
  },
});
