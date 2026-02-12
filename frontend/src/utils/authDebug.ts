/**
 * Authentication debugging utilities
 * Development environment only
 */

import { isDevelopment } from '../config/api';

export const debugAuth = () => {
  if (!isDevelopment) return null;
  
  const token = localStorage.getItem('access_token');
  const user = localStorage.getItem('user');
  
  console.log('=== AUTH DEBUG ===');
  console.log('Token exists:', !!token);
  console.log('Token preview:', token ? token.substring(0, 30) + '...' : 'No token');
  console.log('User data:', user ? JSON.parse(user) : 'No user');
  console.log('==================');
  
  return {
    hasToken: !!token,
    token: token,
    user: user ? JSON.parse(user) : null
  };
};

export const testBillingAPI = async () => {
  if (!isDevelopment) {
    console.warn('testBillingAPI is only available in development mode');
    return;
  }
  
  const authInfo = debugAuth();
  
  if (!authInfo?.hasToken) {
    console.error('❌ No token found! User must login first.');
    return;
  }
  
  try {
    console.log('🧪 Testing billing API with token...');
    const response = await fetch('/api/v1/billing/enhanced/dashboard/financial', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authInfo.token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('📊 Response status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ API call successful!', data);
    } else {
      const errorText = await response.text();
      console.error('❌ API call failed:', response.status, errorText);
    }
  } catch (error) {
    console.error('❌ Network error:', error);
  }
};
