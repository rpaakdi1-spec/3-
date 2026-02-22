/**
 * 배차 규칙 템플릿 라이브러리
 * 자주 사용하는 규칙을 템플릿으로 제공
 */

export interface RuleTemplate {
  id: string;
  name: string;
  description: string;
  category: 'temperature' | 'distance' | 'skill' | 'client' | 'capacity' | 'time' | 'special' | 'weather';
  rule_type: 'assignment' | 'constraint' | 'optimization';
  priority: number;
  conditions: Record<string, any>;
  actions: Record<string, any>;
  icon: string;
}

export const ruleTemplates: RuleTemplate[] = [
  // 온도 관련 템플릿
  {
    id: 'frozen-to-frozen-vehicle',
    name: '냉동 주문 → 냉동탑차 우선 배정',
    description: '냉동 제품은 냉동 차량에 우선 배정',
    category: 'temperature',
    rule_type: 'assignment',
    priority: 90,
    conditions: {
      'order.temperature_zone': '냉동'
    },
    actions: {
      'prefer_vehicle_type': '냉동탑차',
      'priority_weight': 1.5
    },
    icon: '❄️'
  },
  {
    id: 'chilled-to-chilled-vehicle',
    name: '냉장 주문 → 냉장탑차 우선 배정',
    description: '냉장 제품은 냉장 차량에 우선 배정',
    category: 'temperature',
    rule_type: 'assignment',
    priority: 85,
    conditions: {
      'order.temperature_zone': '냉장'
    },
    actions: {
      'prefer_vehicle_type': '냉장탑차',
      'priority_weight': 1.4
    },
    icon: '🧊'
  },

  // 거리 관련 템플릿
  {
    id: 'long-distance-large-vehicle',
    name: '100km 이상 → 대형 차량 배정',
    description: '장거리 배송은 연료 효율이 좋은 대형 차량 사용',
    category: 'distance',
    rule_type: 'constraint',
    priority: 75,
    conditions: {
      'order.estimated_distance_km': { '$gte': 100 }
    },
    actions: {
      'prefer_vehicle_weight': 5000,
      'min_vehicle_weight': 4000,
      'priority_weight': 1.3
    },
    icon: '🚛'
  },
  {
    id: 'short-distance-small-vehicle',
    name: '30km 이하 → 소형 차량 배정',
    description: '단거리 배송은 소형 차량으로 효율적 운영',
    category: 'distance',
    rule_type: 'constraint',
    priority: 70,
    conditions: {
      'order.estimated_distance_km': { '$lte': 30 }
    },
    actions: {
      'prefer_vehicle_weight': 2500,
      'max_vehicle_weight': 3500,
      'priority_weight': 1.2
    },
    icon: '🚚'
  },

  // 기사 스킬 관련 템플릿
  {
    id: 'forklift-required',
    name: '지게차 필요 → 지게차 가능 기사 배정',
    description: '지게차 작업이 필요한 거래처는 자격증 보유 기사 배정',
    category: 'skill',
    rule_type: 'assignment',
    priority: 95,
    conditions: {
      'client.requires_forklift': true
    },
    actions: {
      'require_driver_skill': 'forklift',
      'priority_weight': 1.8
    },
    icon: '🏗️'
  },
  {
    id: 'hazmat-required',
    name: '위험물 → 위험물 자격 기사 배정',
    description: '위험물 운송은 위험물 운송 자격증 보유 기사만 가능',
    category: 'skill',
    rule_type: 'assignment',
    priority: 100,
    conditions: {
      'order.is_hazmat': true
    },
    actions: {
      'require_driver_skill': 'hazmat',
      'priority_weight': 2.0
    },
    icon: '⚠️'
  },

  // 고객사 관련 템플릿
  {
    id: 'vip-client-priority',
    name: 'VIP 고객사 → 우수 기사 우선 배정',
    description: 'VIP 고객사는 평점 높은 우수 기사에게 우선 배정',
    category: 'client',
    rule_type: 'assignment',
    priority: 80,
    conditions: {
      'client.is_vip': true
    },
    actions: {
      'min_driver_rating': 4.5,
      'priority_weight': 1.6
    },
    icon: '⭐'
  },
  {
    id: 'dedicated-driver',
    name: '전담 기사 배정 규칙',
    description: '특정 고객사는 전담 기사에게만 배정',
    category: 'client',
    rule_type: 'assignment',
    priority: 90,
    conditions: {
      'order.pickup_client_id': 0  // 실제 고객 ID로 변경 필요
    },
    actions: {
      'prefer_driver_id': 0,  // 실제 기사 ID로 변경 필요
      'priority_weight': 2.0
    },
    icon: '👤'
  },

  // 적재율 관련 템플릿
  {
    id: 'optimize-pallet-loading',
    name: '팔레트 적재율 최적화 (70-95%)',
    description: '차량 적재율을 70-95% 유지하여 공간 효율 극대화',
    category: 'capacity',
    rule_type: 'optimization',
    priority: 65,
    conditions: {
      'vehicle.max_pallets': { '$gte': 10 }
    },
    actions: {
      'target_utilization_min': 0.7,
      'target_utilization_max': 0.95,
      'consolidate_orders': true,
      'priority_weight': 1.1
    },
    icon: '📦'
  },
  {
    id: 'heavy-cargo-capacity',
    name: '중량화물 → 고중량 차량 배정',
    description: '2톤 이상 화물은 5톤 이상 차량 사용',
    category: 'capacity',
    rule_type: 'constraint',
    priority: 85,
    conditions: {
      'order.weight_kg': { '$gte': 2000 }
    },
    actions: {
      'min_vehicle_weight': 5000,
      'priority_weight': 1.5
    },
    icon: '⚖️'
  },

  // 시간 관련 템플릿 (추가)
  {
    id: 'early-morning-delivery',
    name: '새벽 배송 (02:00-06:00) → 경력 기사 배정',
    description: '새벽 시간대 배송은 경험 많은 기사에게 우선 배정',
    category: 'time',
    rule_type: 'assignment',
    priority: 88,
    conditions: {
      'order.delivery_time_start': { '$gte': '02:00', '$lte': '06:00' }
    },
    actions: {
      'min_driver_experience_years': 2,
      'priority_weight': 1.7
    },
    icon: '🌙'
  },
  {
    id: 'rush-hour-avoidance',
    name: '출퇴근 시간 회피 (07:00-09:00, 18:00-20:00)',
    description: '혼잡 시간대는 지역 전문 기사 우선 배정',
    category: 'time',
    rule_type: 'optimization',
    priority: 70,
    conditions: {
      'order.delivery_time_start': { 
        '$in': [
          { '$gte': '07:00', '$lte': '09:00' },
          { '$gte': '18:00', '$lte': '20:00' }
        ]
      }
    },
    actions: {
      'prefer_local_driver': true,
      'priority_weight': 1.4
    },
    icon: '🚦'
  },

  // 특수 주문 템플릿 (추가)
  {
    id: 'fragile-items',
    name: '깨지기 쉬운 화물 → 조심 운전 기사',
    description: '유리, 도자기 등 파손 위험 화물은 조심 운전 기사 배정',
    category: 'special',
    rule_type: 'assignment',
    priority: 92,
    conditions: {
      'order.is_fragile': true
    },
    actions: {
      'require_driver_skill': 'careful_driving',
      'max_speed_limit': 80,
      'priority_weight': 1.8
    },
    icon: '🔴'
  },
  {
    id: 'high-value-cargo',
    name: '고가 화물 (1000만원 이상) → 보험 가입 차량',
    description: '고가 화물은 보험 가입 차량으로만 배송',
    category: 'special',
    rule_type: 'constraint',
    priority: 98,
    conditions: {
      'order.cargo_value': { '$gte': 10000000 }
    },
    actions: {
      'require_insurance': true,
      'require_gps_tracking': true,
      'priority_weight': 2.0
    },
    icon: '💎'
  },

  // 날씨 관련 템플릿 (추가)
  {
    id: 'rain-weather',
    name: '우천 시 → 4WD 차량 우선',
    description: '비오는 날은 4륜구동 차량으로 안전 배송',
    category: 'weather',
    rule_type: 'assignment',
    priority: 75,
    conditions: {
      'weather.condition': 'rain'
    },
    actions: {
      'prefer_vehicle_feature': '4WD',
      'max_speed_limit': 70,
      'priority_weight': 1.4
    },
    icon: '🌧️'
  },
  {
    id: 'snow-weather',
    name: '적설 시 → 체인 장착 차량만',
    description: '눈 오는 날은 체인 장착 차량으로만 배송',
    category: 'weather',
    rule_type: 'constraint',
    priority: 95,
    conditions: {
      'weather.condition': 'snow'
    },
    actions: {
      'require_snow_chains': true,
      'require_driver_skill': 'winter_driving',
      'max_speed_limit': 60,
      'priority_weight': 2.0
    },
    icon: '❄️'
  }
];

export const templateCategories = {
  temperature: { label: '온도 관리', color: 'blue', icon: '❄️' },
  distance: { label: '거리 최적화', color: 'green', icon: '🚛' },
  skill: { label: '기사 스킬', color: 'purple', icon: '🏗️' },
  client: { label: '고객사 관리', color: 'yellow', icon: '⭐' },
  capacity: { label: '적재 최적화', color: 'red', icon: '📦' },
  time: { label: '시간대 관리', color: 'indigo', icon: '🌙' },
  special: { label: '특수 화물', color: 'pink', icon: '💎' },
  weather: { label: '날씨 대응', color: 'cyan', icon: '🌧️' }
};
