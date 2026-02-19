import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { Settings, User, Bell, Shield, Save } from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';

const SettingsPage: React.FC = () => {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const [profileData, setProfileData] = useState({
    username: '',
    email: '',
    full_name: ''
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const [notificationSettings, setNotificationSettings] = useState({
    email_notifications: true,
    push_notifications: true,
    order_updates: true,
    dispatch_updates: true,
    maintenance_alerts: true
  });

  const [systemSettings, setSystemSettings] = useState({
    language: 'ko',
    timezone: 'Asia/Seoul',
    date_format: 'YYYY-MM-DD',
    temperature_unit: 'celsius'
  });

  useEffect(() => {
    if (user) {
      setProfileData({
        username: user.username || '',
        email: user.email || '',
        full_name: user.full_name || ''
      });
    }
    loadSettings();
  }, [user]);

  const loadSettings = async () => {
    try {
      // Settings API endpoint doesn't exist yet, use default values
      // TODO: Implement /users/settings endpoint in backend
      console.log('Using default settings (API endpoint not implemented yet)');
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await api.put('/users/profile', profileData);
      setMessage('프로필이 업데이트되었습니다.');
      setTimeout(() => setMessage(''), 3000);
    } catch (error: any) {
      setMessage(error.response?.data?.detail || '프로필 업데이트에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage('새 비밀번호가 일치하지 않습니다.');
      return;
    }

    if (passwordData.new_password.length < 6) {
      setMessage('비밀번호는 최소 6자 이상이어야 합니다.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      await api.put('/users/password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      setMessage('비밀번호가 변경되었습니다.');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      setTimeout(() => setMessage(''), 3000);
    } catch (error: any) {
      setMessage(error.response?.data?.detail || '비밀번호 변경에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationUpdate = async () => {
    setLoading(true);
    setMessage('');

    try {
      await api.put('/users/settings/notifications', notificationSettings);
      setMessage('알림 설정이 저장되었습니다.');
      setTimeout(() => setMessage(''), 3000);
    } catch (error: any) {
      setMessage('알림 설정 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSystemUpdate = async () => {
    setLoading(true);
    setMessage('');

    try {
      await api.put('/users/settings/system', systemSettings);
      setMessage('시스템 설정이 저장되었습니다.');
      setTimeout(() => setMessage(''), 3000);
    } catch (error: any) {
      setMessage('시스템 설정 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', label: '프로필', icon: User },
    { id: 'notifications', label: '알림 설정', icon: Bell },
    { id: 'security', label: '보안', icon: Shield },
    { id: 'system', label: '시스템', icon: Settings }
  ];

  return (
    <Layout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">설정</h1>
          <p className="text-gray-600 mt-1">시스템 및 개인 설정을 관리합니다</p>
        </div>

      {message && (
        <div className={`mb-4 p-4 rounded-lg ${
          message.includes('실패') || message.includes('일치하지') 
            ? 'bg-red-50 text-red-700 border border-red-200' 
            : 'bg-green-50 text-green-700 border border-green-200'
        }`}>
          {message}
        </div>
      )}

      {/* Horizontal Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-1 py-4 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon size={20} className="mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div>
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <Card>
              <h2 className="text-xl font-bold text-gray-800 mb-4">프로필 정보</h2>
              <form onSubmit={handleProfileUpdate} className="space-y-4">
                <Input
                  label="사용자명"
                  value={profileData.username}
                  onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
                  disabled
                />
                <Input
                  label="이메일"
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                />
                <Input
                  label="이름"
                  value={profileData.full_name}
                  onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                />
                <div className="flex justify-end">
                  <Button type="submit" loading={loading}>
                    <Save size={20} className="mr-2" />
                    저장
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <Card>
              <h2 className="text-xl font-bold text-gray-800 mb-4">알림 설정</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b">
                  <div>
                    <p className="font-medium text-gray-800">이메일 알림</p>
                    <p className="text-sm text-gray-600">이메일로 알림을 받습니다</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.email_notifications}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        email_notifications: e.target.checked
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between py-3 border-b">
                  <div>
                    <p className="font-medium text-gray-800">푸시 알림</p>
                    <p className="text-sm text-gray-600">브라우저 푸시 알림을 받습니다</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.push_notifications}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        push_notifications: e.target.checked
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between py-3 border-b">
                  <div>
                    <p className="font-medium text-gray-800">주문 업데이트</p>
                    <p className="text-sm text-gray-600">주문 상태 변경 시 알림</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.order_updates}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        order_updates: e.target.checked
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between py-3 border-b">
                  <div>
                    <p className="font-medium text-gray-800">배차 업데이트</p>
                    <p className="text-sm text-gray-600">배차 상태 변경 시 알림</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.dispatch_updates}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        dispatch_updates: e.target.checked
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between py-3">
                  <div>
                    <p className="font-medium text-gray-800">정비 알림</p>
                    <p className="text-sm text-gray-600">차량 정비 예정일 알림</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.maintenance_alerts}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        maintenance_alerts: e.target.checked
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex justify-end pt-4 border-t">
                  <Button onClick={handleNotificationUpdate} loading={loading}>
                    <Save size={20} className="mr-2" />
                    저장
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <Card>
              <h2 className="text-xl font-bold text-gray-800 mb-4">비밀번호 변경</h2>
              <form onSubmit={handlePasswordChange} className="space-y-4">
                <Input
                  label="현재 비밀번호"
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                  required
                />
                <Input
                  label="새 비밀번호"
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  required
                />
                <Input
                  label="새 비밀번호 확인"
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                  required
                />
                <div className="flex justify-end">
                  <Button type="submit" loading={loading}>
                    <Save size={20} className="mr-2" />
                    변경
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {/* System Tab */}
          {activeTab === 'system' && (
            <Card>
              <h2 className="text-xl font-bold text-gray-800 mb-4">시스템 설정</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    언어
                  </label>
                  <select
                    value={systemSettings.language}
                    onChange={(e) => setSystemSettings({ ...systemSettings, language: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="ko">한국어</option>
                    <option value="en">English</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    시간대
                  </label>
                  <select
                    value={systemSettings.timezone}
                    onChange={(e) => setSystemSettings({ ...systemSettings, timezone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Asia/Seoul">서울 (GMT+9)</option>
                    <option value="UTC">UTC (GMT+0)</option>
                    <option value="America/New_York">뉴욕 (GMT-5)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    날짜 형식
                  </label>
                  <select
                    value={systemSettings.date_format}
                    onChange={(e) => setSystemSettings({ ...systemSettings, date_format: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    온도 단위
                  </label>
                  <select
                    value={systemSettings.temperature_unit}
                    onChange={(e) => setSystemSettings({ ...systemSettings, temperature_unit: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="celsius">섭씨 (°C)</option>
                    <option value="fahrenheit">화씨 (°F)</option>
                  </select>
                </div>

                <div className="flex justify-end pt-4 border-t">
                  <Button onClick={handleSystemUpdate} loading={loading}>
                    <Save size={20} className="mr-2" />
                    저장
                  </Button>
                </div>
              </div>
            </Card>
          )}
      </div>
      </div>
    </Layout>
  );
};

export default SettingsPage;
