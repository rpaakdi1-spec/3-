/**
 * k6 Performance Testing Script
 * 
 * Run with:
 *   k6 run backend/tests/performance/k6-performance-test.js
 * 
 * Or with options:
 *   k6 run --vus 100 --duration 5m backend/tests/performance/k6-performance-test.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const dashboardTrend = new Trend('dashboard_duration');
const orderCreationTrend = new Trend('order_creation_duration');
const dispatchOptimizationTrend = new Trend('dispatch_optimization_duration');
const successfulRequests = new Counter('successful_requests');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users over 2 minutes
    { duration: '5m', target: 50 },   // Stay at 50 users for 5 minutes
    { duration: '2m', target: 100 },  // Ramp up to 100 users over 2 minutes
    { duration: '5m', target: 100 },  // Stay at 100 users for 5 minutes
    { duration: '2m', target: 200 },  // Spike to 200 users over 2 minutes
    { duration: '3m', target: 200 },  // Stay at 200 users for 3 minutes
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],  // 95% of requests must complete within 500ms
    'errors': ['rate<0.01'],                            // Error rate must be less than 1%
    'http_req_duration{name:Dashboard}': ['avg<200'],  // Dashboard avg response time < 200ms
    'http_req_duration{name:OrderList}': ['avg<300'],  // Order list avg response time < 300ms
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';
let authToken = '';

// Setup function - runs once per VU
export function setup() {
  // Login to get auth token
  const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify({
    username: 'loadtest_user',
    password: 'LoadTest123!'
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  if (loginRes.status === 200) {
    const token = JSON.parse(loginRes.body).access_token;
    return { token: token };
  }
  
  return { token: 'test_token' };
}

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
  };

  // 1. View Dashboard
  group('Dashboard', () => {
    const res = http.get(`${BASE_URL}/api/v1/analytics/dashboard`, { 
      headers: headers,
      tags: { name: 'Dashboard' }
    });
    
    const success = check(res, {
      'dashboard status is 200': (r) => r.status === 200,
      'dashboard response time < 200ms': (r) => r.timings.duration < 200,
      'dashboard has active_dispatches': (r) => JSON.parse(r.body).active_dispatches !== undefined,
    });
    
    errorRate.add(!success);
    dashboardTrend.add(res.timings.duration);
    
    if (success) {
      successfulRequests.add(1);
    }
  });

  sleep(1);

  // 2. List Orders
  group('Orders', () => {
    const page = Math.floor(Math.random() * 5) + 1;
    const res = http.get(`${BASE_URL}/api/v1/orders?page=${page}&page_size=20`, { 
      headers: headers,
      tags: { name: 'OrderList' }
    });
    
    const success = check(res, {
      'orders status is 200': (r) => r.status === 200,
      'orders response time < 300ms': (r) => r.timings.duration < 300,
      'orders is array': (r) => Array.isArray(JSON.parse(r.body).items || JSON.parse(r.body)),
    });
    
    errorRate.add(!success);
    
    if (success) {
      successfulRequests.add(1);
    }
  });

  sleep(1);

  // 3. Create Order (20% of users)
  if (Math.random() < 0.2) {
    group('Create Order', () => {
      const orderData = {
        client_id: Math.floor(Math.random() * 50) + 1,
        pickup_client_id: Math.floor(Math.random() * 50) + 1,
        delivery_client_id: Math.floor(Math.random() * 50) + 1,
        temperature_type: ['냉동', '냉장', '상온'][Math.floor(Math.random() * 3)],
        pallets: Math.floor(Math.random() * 30) + 1,
        weight_kg: Math.random() * 5000 + 100,
        pickup_location: 'Seoul, Korea',
        delivery_location: 'Busan, Korea',
        notes: `k6 load test order ${Date.now()}`
      };

      const res = http.post(`${BASE_URL}/api/v1/orders`, JSON.stringify(orderData), { 
        headers: headers,
        tags: { name: 'OrderCreate' }
      });
      
      const success = check(res, {
        'create order status is 201': (r) => r.status === 201,
        'create order response time < 500ms': (r) => r.timings.duration < 500,
      });
      
      errorRate.add(!success);
      orderCreationTrend.add(res.timings.duration);
      
      if (success) {
        successfulRequests.add(1);
      }
    });

    sleep(1);
  }

  // 4. View Order Detail
  group('Order Detail', () => {
    const orderId = Math.floor(Math.random() * 1000) + 1;
    const res = http.get(`${BASE_URL}/api/v1/orders/${orderId}`, { 
      headers: headers,
      tags: { name: 'OrderDetail' }
    });
    
    const success = check(res, {
      'order detail status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    });
    
    errorRate.add(!success);
    
    if (success) {
      successfulRequests.add(1);
    }
  });

  sleep(1);

  // 5. List Dispatches
  group('Dispatches', () => {
    const res = http.get(`${BASE_URL}/api/v1/dispatches?page=1&page_size=20`, { 
      headers: headers,
      tags: { name: 'DispatchList' }
    });
    
    const success = check(res, {
      'dispatches status is 200': (r) => r.status === 200,
      'dispatches response time < 300ms': (r) => r.timings.duration < 300,
    });
    
    errorRate.add(!success);
    
    if (success) {
      successfulRequests.add(1);
    }
  });

  sleep(1);

  // 6. Optimize Dispatch (5% of users)
  if (Math.random() < 0.05) {
    group('Optimize Dispatch', () => {
      const orderIds = [];
      for (let i = 0; i < 5; i++) {
        orderIds.push(Math.floor(Math.random() * 100) + 1);
      }

      const res = http.post(`${BASE_URL}/api/v1/dispatches/optimize`, JSON.stringify({
        order_ids: orderIds
      }), { 
        headers: headers,
        tags: { name: 'DispatchOptimize' }
      });
      
      const success = check(res, {
        'optimize status is 200 or 400': (r) => r.status === 200 || r.status === 400,
        'optimize response time < 5000ms': (r) => r.timings.duration < 5000,
      });
      
      errorRate.add(!success);
      dispatchOptimizationTrend.add(res.timings.duration);
      
      if (success) {
        successfulRequests.add(1);
      }
    });

    sleep(2);
  }

  // 7. ML Prediction (10% of users)
  if (Math.random() < 0.1) {
    group('ML Prediction', () => {
      const res = http.post(`${BASE_URL}/api/v1/ml/predict/delivery-time`, JSON.stringify({
        distance_km: Math.random() * 200 + 10,
        traffic_level: ['light', 'moderate', 'heavy'][Math.floor(Math.random() * 3)],
        vehicle_type: 'refrigerated_truck',
        temperature_type: '냉장',
        time_of_day: 'afternoon',
        day_of_week: 'monday'
      }), { 
        headers: headers,
        tags: { name: 'MLPredict' }
      });
      
      const success = check(res, {
        'ml predict status is 200': (r) => r.status === 200,
        'ml predict response time < 1000ms': (r) => r.timings.duration < 1000,
      });
      
      errorRate.add(!success);
      
      if (success) {
        successfulRequests.add(1);
      }
    });

    sleep(1);
  }

  // 8. View Analytics
  group('Analytics', () => {
    const res = http.get(`${BASE_URL}/api/v1/analytics/performance`, { 
      headers: headers,
      tags: { name: 'Analytics' }
    });
    
    const success = check(res, {
      'analytics status is 200': (r) => r.status === 200,
      'analytics response time < 400ms': (r) => r.timings.duration < 400,
    });
    
    errorRate.add(!success);
    
    if (success) {
      successfulRequests.add(1);
    }
  });

  sleep(1);

  // 9. Real-time Monitoring
  group('Realtime Monitoring', () => {
    const vehicleIds = [];
    for (let i = 0; i < 3; i++) {
      vehicleIds.push(Math.floor(Math.random() * 50) + 1);
    }

    const res = http.get(`${BASE_URL}/api/v1/realtime/monitor?vehicle_ids=${vehicleIds.join(',')}`, { 
      headers: headers,
      tags: { name: 'RealtimeMonitor' }
    });
    
    const success = check(res, {
      'realtime status is 200': (r) => r.status === 200,
      'realtime response time < 500ms': (r) => r.timings.duration < 500,
    });
    
    errorRate.add(!success);
    
    if (success) {
      successfulRequests.add(1);
    }
  });

  sleep(1);
}

// Teardown function - runs once after all VUs are done
export function teardown(data) {
  console.log('🏁 k6 performance test completed');
}

// Handle thresholds
export function handleSummary(data) {
  console.log('📊 Test Summary:');
  console.log(`Total Requests: ${data.metrics.http_reqs.values.count}`);
  console.log(`Failed Requests: ${data.metrics.http_req_failed.values.passes}`);
  console.log(`Average Response Time: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms`);
  console.log(`95th Percentile: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms`);
  console.log(`99th Percentile: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms`);
  console.log(`Requests/sec: ${data.metrics.http_reqs.values.rate.toFixed(2)}`);
  
  return {
    'backend/tests/performance/k6-summary.json': JSON.stringify(data),
  };
}
