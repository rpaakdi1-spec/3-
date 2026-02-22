"""
AI 기반 배차 규칙 자동 생성 서비스

규칙 이름과 설명을 분석하여 conditions와 actions를 자동 생성합니다.
"""
import logging
import json
import os
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# OpenAI 또는 Gemini 사용
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class RuleAIGenerator:
    """AI 기반 규칙 생성기"""
    
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        
        # OpenAI 설정
        openai_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized for rule generation")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI initialization failed: {e}")
        
        # Gemini 설정
        gemini_key = os.getenv("GEMINI_API_KEY")
        if GEMINI_AVAILABLE and gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini model initialized for rule generation")
            except Exception as e:
                logger.warning(f"⚠️ Gemini initialization failed: {e}")
    
    async def generate_rule(
        self,
        name: str,
        description: str,
        rule_type: str = "assignment"
    ) -> Dict[str, Any]:
        """
        규칙 이름과 설명으로부터 conditions와 actions 자동 생성
        
        Args:
            name: 규칙 이름 (예: "지게차가능거래처 -> 지게차가능기사로 배차")
            description: 규칙 설명
            rule_type: assignment, constraint, optimization
            
        Returns:
            {
                "conditions": {...},
                "actions": {...},
                "confidence": 0.0-1.0,
                "reasoning": "생성 이유"
            }
        """
        try:
            # AI 프롬프트 생성
            prompt = self._build_prompt(name, description, rule_type)
            
            # AI 모델 호출 (OpenAI 우선, Gemini 대체)
            if self.openai_client:
                result = await self._generate_with_openai(prompt)
            elif self.gemini_model:
                result = await self._generate_with_gemini(prompt)
            else:
                # AI 없으면 규칙 기반 생성
                result = self._generate_rule_based(name, description, rule_type)
            
            logger.info(f"✅ Generated rule: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Rule generation failed: {e}")
            # 실패 시 빈 규칙 반환
            return {
                "conditions": {},
                "actions": {},
                "confidence": 0.0,
                "reasoning": f"생성 실패: {str(e)}"
            }
    
    def _build_prompt(self, name: str, description: str, rule_type: str) -> str:
        """AI 프롬프트 생성 (개선된 버전)"""
        
        prompt = f"""당신은 물류 배차 시스템의 규칙 생성 전문가입니다.

사용자가 다음과 같은 배차 규칙을 만들고 싶어합니다:

**규칙 이름**: {name}
**규칙 설명**: {description}
**규칙 타입**: {rule_type}

이 규칙을 JSON 형태의 조건(conditions)과 액션(actions)으로 변환해주세요.

## 중요한 해석 지침

1. **차량 관련 용어 해석**:
   - "5톤 차량", "대형 차량" → min_vehicle_weight 또는 prefer_vehicle_weight (단위: kg)
   - "차량 적재량", "최대 적재량" → vehicle_weight 필드 사용
   - "팔레트" → total_pallets 필드 사용

2. **조건(conditions)과 액션(actions) 구분**:
   - conditions: 주문이나 거래처의 속성 (무엇을 필터링할지)
   - actions: 차량이나 기사 선택 방법 (어떻게 배정할지)

3. **필드 사용 우선순위**:
   - 온도: order.temperature_zone (조건) + prefer_vehicle_type (액션)
   - 거리: order.estimated_distance_km (조건) + prefer_vehicle_weight (액션)
   - 기사 스킬: client.requires_forklift (조건) + require_driver_skill (액션)
   - 중량: order.weight_kg (조건) + min_vehicle_weight (액션)

## 사용 가능한 필드

### Conditions (조건) - 주문/거래처 속성
- order.temperature_zone: "냉동", "냉장", "상온"
- order.estimated_distance_km: 배송 거리 (숫자, km)
- order.total_pallets: 팔레트 수 (숫자)
- order.weight_kg: 화물 중량 (숫자, kg)
- order.pickup_client_id: 픽업 거래처 ID (숫자)
- order.delivery_time_start: 배송 시작 시간 (HH:MM 형식)
- order.is_fragile: 깨지기 쉬운 화물 (true/false)
- order.cargo_value: 화물 가격 (숫자, 원)
- client.requires_forklift: 지게차 필요 여부 (true/false)
- client.is_vip: VIP 고객 여부 (true/false)
- client.special_requirements: 특수 요구사항 (문자열)
- weather.condition: 날씨 상태 ("rain", "snow", "clear")

### Actions (액션) - 차량/기사 선택 방법
- prefer_vehicle_type: 선호 차량 타입 ("냉동탑차", "냉장탑차", "상온탑차", "대형차량")
- prefer_vehicle_weight: 선호 차량 적재량 (숫자, kg)
- min_vehicle_weight: 최소 차량 적재량 (숫자, kg)
- max_vehicle_weight: 최대 차량 적재량 (숫자, kg)
- require_driver_skill: 필요 기사 기술 ("forklift", "hazmat", "careful_driving", "winter_driving")
- min_driver_experience_years: 최소 경력 (숫자, 년)
- min_driver_rating: 최소 평점 (숫자, 1-5)
- priority_weight: 우선순위 가중치 (1.0-2.0, 높을수록 우선)
- max_distance_km: 최대 배송 거리 제한 (숫자, km)
- max_speed_limit: 최대 속도 제한 (숫자, km/h)
- require_insurance: 보험 필수 (true/false)
- require_gps_tracking: GPS 추적 필수 (true/false)
- consolidate_orders: 주문 통합 (true/false)

### 거리/중량 조건 표현 예시
- {{"$gte": 100}} - 100 이상
- {{"$lte": 50}} - 50 이하
- {{"$between": [50, 100]}} - 50-100 사이

## 응답 형식 (반드시 유효한 JSON만 출력)

{{
  "conditions": {{
    "필드명": 값_또는_조건
  }},
  "actions": {{
    "필드명": 값
  }},
  "confidence": 0.90,
  "reasoning": "이 규칙을 이렇게 해석했습니다: [상세한 설명]"
}}

## 예시

입력: "100km 이상 장거리는 5톤 이상 차량"
출력:
{{
  "conditions": {{
    "order.estimated_distance_km": {{"$gte": 100}}
  }},
  "actions": {{
    "min_vehicle_weight": 5000,
    "prefer_vehicle_weight": 5000,
    "priority_weight": 1.5
  }},
  "confidence": 0.95,
  "reasoning": "100km 이상 장거리 배송은 연료 효율과 안정성을 위해 최소 5톤(5000kg) 적재량의 차량이 필요합니다. min_vehicle_weight로 최소 요구사항을 설정하고 prefer_vehicle_weight로 선호도를 표현했습니다."
}}

**중요**: JSON만 출력하고 다른 텍스트는 넣지 마세요. 마크다운 코드 블록도 사용하지 마세요.
"""
        return prompt
    
    async def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """OpenAI로 규칙 생성"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a logistics dispatch rule expert. Always respond in valid JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # JSON 추출 (```json ... ``` 제거)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def _generate_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Gemini로 규칙 생성"""
        try:
            response = self.gemini_model.generate_content(prompt)
            content = response.text.strip()
            
            # JSON 추출
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    def _generate_rule_based(
        self,
        name: str,
        description: str,
        rule_type: str
    ) -> Dict[str, Any]:
        """
        AI 없이 규칙 기반으로 생성 (폴백)
        
        키워드 매칭으로 간단한 규칙 생성
        우선순위: 지게차 > 온도 > 거리 > 중량
        """
        conditions = {}
        actions = {}
        reasoning = []
        
        text = (name + " " + description).lower()
        
        # 우선순위 1: 지게차 관련 (가장 명확한 요구사항)
        if "지게차" in text or "forklift" in text:
            conditions["client.requires_forklift"] = True
            actions["require_driver_skill"] = "forklift"
            actions["priority_weight"] = 1.5
            reasoning.append("지게차 요구사항 감지")
            
            # 지게차 규칙이면 온도는 무시 (지게차가 주 조건)
            logger.info(f"🔧 Forklift rule detected, ignoring temperature keywords")
        
        # 우선순위 2: 온도 관련 (지게차 규칙이 아닐 때만)
        elif "냉동" in text:
            conditions["order.temperature_zone"] = "냉동"
            actions["prefer_vehicle_type"] = "냉동탑차"
            reasoning.append("냉동 온도대 감지")
        elif "냉장" in text:
            conditions["order.temperature_zone"] = "냉장"
            actions["prefer_vehicle_type"] = "냉장탑차"
            reasoning.append("냉장 온도대 감지")
        elif "상온" in text:
            conditions["order.temperature_zone"] = "상온"
            actions["prefer_vehicle_type"] = "상온탑차"
            reasoning.append("상온 감지")
        
        # 우선순위 3: 거리 관련
        import re
        distance_match = re.search(r'(\d+)\s*km\s*(이상|이하|초과|미만)', text)
        if distance_match:
            distance = int(distance_match.group(1))
            operator = distance_match.group(2)
            
            if operator in ["이상", "초과"]:
                conditions["order.estimated_distance_km"] = {"$gte": distance}
                reasoning.append(f"{distance}km 이상 조건 감지")
                # 거리 제한이 있으면 차량 용량도 추가
                if distance >= 100:
                    actions["prefer_vehicle_weight"] = 5000
                    reasoning.append("장거리는 대형 차량 선호")
            elif operator in ["이하", "미만"]:
                conditions["order.estimated_distance_km"] = {"$lte": distance}
                reasoning.append(f"{distance}km 이하 조건 감지")
        
        # 우선순위 4: 우선순위 가중치
        if "우선" in text or "먼저" in text:
            if "priority_weight" not in actions:
                actions["priority_weight"] = 1.3
            reasoning.append("우선순위 설정")
        
        # 경고: 조건이 없으면 낮은 신뢰도
        if not conditions:
            logger.warning(f"⚠️ No conditions detected from: '{name}' - '{description}'")
            confidence = 0.2
            reasoning.append("⚠️ 명확한 조건을 찾지 못했습니다. 수동으로 조건을 입력해주세요.")
        elif not actions:
            logger.warning(f"⚠️ No actions detected from: '{name}' - '{description}'")
            confidence = 0.3
            reasoning.append("⚠️ 명확한 액션을 찾지 못했습니다. 수동으로 액션을 입력해주세요.")
        else:
            # 조건과 액션이 모두 있으면 중간 신뢰도
            confidence = 0.65
        
        result = {
            "conditions": conditions,
            "actions": actions,
            "confidence": confidence,
            "reasoning": "규칙 기반 생성: " + ", ".join(reasoning) if reasoning else "패턴을 찾지 못했습니다. AI 모델(OpenAI/Gemini)을 설정하면 더 정확합니다."
        }
        
        logger.info(f"📋 Rule-based generation result: confidence={confidence:.2f}, conditions={len(conditions)}, actions={len(actions)}")
        return result
