import logging
import json
import re
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
import os

from app.models.order import Order
from app.models.client import Client
from app.models.ai_usage_log import AIUsageLog

logger = logging.getLogger(__name__)

# OpenAI는 선택적으로 import
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️ OpenAI 라이브러리가 설치되지 않았습니다.")

# Gemini는 선택적으로 import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ Gemini 라이브러리가 설치되지 않았습니다.")


class AIChatService:
    """
    AI 채팅 서비스 - OpenAI GPT 또는 Google Gemini를 사용한 자연어 처리
    """
    
    def __init__(self, model_name: str = "auto"):
        """
        Args:
            model_name: "gpt-4", "gpt-3.5-turbo", "gemini-pro", "auto"
                       "auto"는 사용 가능한 첫 번째 모델 자동 선택
        """
        self.model_name = model_name
        self.openai_client = None
        self.gemini_model = None
        
        # OpenAI 설정
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=openai_key)
            logger.info("✅ OpenAI API 키가 설정되었습니다.")
        
        # Gemini 설정
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key and GEMINI_AVAILABLE:
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            logger.info("✅ Gemini API 키가 설정되었습니다.")
        
        # 모델 선택 로직
        if model_name == "auto":
            if self.openai_client:
                self.model_name = "gpt-4"
                logger.info("🤖 자동 선택: GPT-4")
            elif self.gemini_model:
                self.model_name = "gemini-pro"
                logger.info("🤖 자동 선택: Gemini Pro")
            else:
                self.model_name = "simulation"
                logger.warning("⚠️ AI 모델이 설정되지 않았습니다. 시뮬레이션 모드로 실행됩니다.")
        
        logger.info(f"🎯 사용 중인 AI 모델: {self.model_name}")
    
    async def process_message(
        self,
        message: str,
        context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        사용자 메시지 처리 및 의도 파악
        
        Args:
            message: 사용자 입력 메시지
            context: 대화 컨텍스트
            db: 데이터베이스 세션
        
        Returns:
            {
                "intent": str,  # "create_order", "update_order", "query_order", etc.
                "message": str,  # AI 응답 메시지
                "parsed_order": dict,  # 추출된 주문 정보
                "model_used": str  # 사용된 AI 모델
            }
        """
        
        try:
            # 모델별 처리
            if self.model_name in ["gpt-4", "gpt-3.5-turbo"] and self.openai_client:
                result = await self._process_with_openai(message, context, db)
            elif self.model_name == "gemini-pro" and self.gemini_model:
                result = await self._process_with_gemini(message, context, db)
            else:
                # 시뮬레이션 모드 (패턴 매칭)
                result = await self._process_with_simulation(message, context, db)
            
            # 사용된 모델 정보 추가
            result["model_used"] = self.model_name
            return result
        
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
            return {
                "intent": "error",
                "message": f"죄송합니다. 처리 중 오류가 발생했습니다: {str(e)}",
                "parsed_order": None,
                "model_used": self.model_name
            }
    
    async def _process_with_openai(
        self,
        message: str,
        context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        OpenAI GPT를 사용한 메시지 처리
        """
        
        start_time = time.time()
        usage_log = None
        
        try:
            # 시스템 프롬프트 구성
            system_prompt = self._build_system_prompt()
            
            # 사용자 프롬프트 구성 (대화 컨텍스트 포함)
            recent_messages = context.get("recent_messages", [])
            accumulated_context = self._accumulate_context(message, recent_messages)
            user_prompt = self._build_user_prompt(accumulated_context, context)
            
            logger.info(f"🤖 OpenAI API 호출... (메시지 길이: {len(message)}자)")
            
            # 모델 선택 (실제 GPT-4 사용)
            if self.model_name == "gpt-4":
                model = "gpt-4o"  # GPT-4 Omni (최신, 빠름, 저렴)
            elif self.model_name == "gpt-3.5-turbo":
                model = "gpt-3.5-turbo"
            else:
                model = "gpt-4o"  # 기본값
            
            logger.info(f"🎯 사용 모델: {model}")
            
            # OpenAI API 호출 (최신 v1.0+ API)
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # 낮은 온도로 일관된 응답
                max_tokens=2000,
                response_format={"type": "json_object"}  # JSON 응답 강제
            )
            
            # 응답 시간 계산
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 응답 파싱
            ai_response = response.choices[0].message.content
            logger.info(f"✅ OpenAI 응답 받음: {len(ai_response)}자 (응답 시간: {response_time_ms}ms)")
            
            # 사용량 정보 추출
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            # 비용 계산 (모델별 토큰당 비용)
            prompt_cost, completion_cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
            total_cost = prompt_cost + completion_cost
            
            logger.info(f"💰 비용: 입력 {prompt_tokens} 토큰 (${prompt_cost:.4f}) + "
                       f"출력 {completion_tokens} 토큰 (${completion_cost:.4f}) = "
                       f"총 ${total_cost:.4f}")
            
            # JSON 응답 파싱
            result = json.loads(ai_response)
            
            # 사용량 로그 저장
            usage_log = AIUsageLog(
                user_id=context.get("user_id"),
                session_id=context.get("session_id"),
                model_name=model,
                provider="openai",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                prompt_cost=prompt_cost,
                completion_cost=completion_cost,
                total_cost=total_cost,
                response_time_ms=response_time_ms,
                status="success",
                intent=result.get("intent"),
                created_at=datetime.now()
            )
            db.add(usage_log)
            db.commit()
            logger.info(f"💾 사용량 로그 저장 완료 (ID: {usage_log.id})")
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}, 응답: {ai_response[:200]}")
            
            # 에러 로그 저장
            if usage_log:
                usage_log.status = "error"
                usage_log.error_message = f"JSON 파싱 오류: {str(e)}"
                db.commit()
            
            # 실패 시 시뮬레이션 모드로 폴백
            return await self._process_with_simulation(message, context, db)
        
        except Exception as e:
            logger.error(f"OpenAI API 오류: {e}")
            
            # 에러 로그 저장
            response_time_ms = int((time.time() - start_time) * 1000)
            error_log = AIUsageLog(
                user_id=context.get("user_id"),
                session_id=context.get("session_id"),
                model_name=model if 'model' in locals() else self.model_name,
                provider="openai",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                prompt_cost=0.0,
                completion_cost=0.0,
                total_cost=0.0,
                response_time_ms=response_time_ms,
                status="error",
                error_message=str(e),
                created_at=datetime.now()
            )
            db.add(error_log)
            db.commit()
            
            # 실패 시 시뮬레이션 모드로 폴백
            return await self._process_with_simulation(message, context, db)
    
    async def _process_with_gemini(
        self,
        message: str,
        context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Google Gemini를 사용한 메시지 처리
        """
        
        try:
            # 시스템 프롬프트 구성
            system_prompt = self._build_system_prompt()
            
            # 사용자 프롬프트 구성 (대화 컨텍스트 포함)
            recent_messages = context.get("recent_messages", [])
            accumulated_context = self._accumulate_context(message, recent_messages)
            user_prompt = self._build_user_prompt(accumulated_context, context)
            
            # Gemini용 전체 프롬프트 구성
            full_prompt = f"""{system_prompt}

===== 사용자 메시지 =====
{user_prompt}

===== 응답 형식 (반드시 JSON으로만 응답) =====
{{
  "intent": "create_order | create_multiple_orders | update_order | query_order | unknown",
  "message": "사용자에게 보여줄 응답 메시지",
  "parsed_order": {{"temperature_zone": "냉동", "pickup_address": "서울", ...}},
  "parsed_orders": [...],
  "action": "confirm_order | waiting_confirmation | ..."
}}"""
            
            logger.info(f"🤖 Gemini API 호출... (메시지 길이: {len(message)}자)")
            
            # Gemini API 호출
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 2048,
                }
            )
            
            # 응답 파싱
            ai_response = response.text
            logger.info(f"✅ Gemini 응답 받음: {len(ai_response)}자")
            
            # JSON 추출 (Gemini는 때때로 마크다운 코드 블록으로 감쌈)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 일반 JSON 찾기
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = ai_response
            
            # JSON 파싱
            result = json.loads(json_str)
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}, 응답: {ai_response[:200] if 'ai_response' in locals() else 'N/A'}")
            # 실패 시 시뮬레이션 모드로 폴백
            return await self._process_with_simulation(message, context, db)
        except Exception as e:
            logger.error(f"Gemini API 오류: {e}")
            # 실패 시 시뮬레이션 모드로 폴백
            return await self._process_with_simulation(message, context, db)
    
    async def _process_with_simulation(
        self,
        message: str,
        context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        시뮬레이션 모드 (간단한 패턴 매칭)
        OpenAI API 키가 없을 때 사용
        """
        
        message_lower = message.lower()
        
        # 최근 메시지에서 컨텍스트 추출
        recent_messages = context.get("recent_messages", [])
        accumulated_context = self._accumulate_context(message, recent_messages)
        accumulated_lower = accumulated_context.lower()
        
        # 주문 생성 패턴 (누적 컨텍스트에서 키워드 검색)
        # 팔레트 정보가 있거나, 배송 관련 키워드가 있으면 주문 생성 시도
        has_order_keywords = any(keyword in accumulated_lower for keyword in ['보내', '배송', '주문', '등록', '출발'])
        has_pallet_info = '팔레트' in accumulated_lower
        has_temp_zone = any(temp in accumulated_lower for temp in ['냉동', '냉장', '상온'])
        
        if has_order_keywords or (has_pallet_info and has_temp_zone):
            # 1:N 배송 패턴 체크 (여러 하차지) - 누적된 컨텍스트 사용
            parsed_orders = self._extract_multiple_orders_simulation(accumulated_context, db)
            
            if parsed_orders and len(parsed_orders) > 1:
                # 여러 주문 생성
                summary = self._format_multiple_orders_summary(parsed_orders)
                
                # 배차 추천 메시지 추가
                dispatch_recommendation = parsed_orders[0].get('_dispatch_recommendation') if parsed_orders else None
                recommendation_msg = ""
                if dispatch_recommendation and dispatch_recommendation.get('needs_split'):
                    recommendation_msg = dispatch_recommendation.get('message', '')
                
                return {
                    "intent": "create_multiple_orders",
                    "message": f"다음 {len(parsed_orders)}개 주문을 등록하시겠습니까?\n\n{summary}{recommendation_msg}\n\n등록하시려면 '네' 또는 '확인'을 입력해주세요.",
                    "parsed_orders": parsed_orders,
                    "parsed_order": None,
                    "dispatch_recommendation": dispatch_recommendation
                }
            else:
                # 단일 주문 - 누적된 컨텍스트 사용
                parsed_order = parsed_orders[0] if parsed_orders else self._extract_order_info_simulation(accumulated_context, db)
                
                if parsed_order and self._validate_order_info(parsed_order):
                    # 주문 정보 요약
                    summary = self._format_order_summary(parsed_order)
                    
                    return {
                        "intent": "create_order",
                        "message": f"다음 정보로 주문을 등록하시겠습니까?\n\n{summary}\n\n등록하시려면 '네' 또는 '확인'을 입력해주세요.",
                        "parsed_order": parsed_order
                    }
                else:
                    return {
                        "intent": "need_more_info",
                        "message": "주문 정보가 부족합니다. 다음 정보를 포함해주세요:\n• 온도대 (냉동/냉장/상온)\n• 상차지 또는 하차지\n• 팔레트 수\n\n**1:N 배송 예시:**\n'서울에서 부산 10팔레트, 대구 15팔레트, 광주 8팔레트 냉동'",
                        "parsed_order": parsed_order
                    }
        
        # 주문 수정 패턴
        if any(keyword in message_lower for keyword in ['수정', '변경', '바꿔']):
            return {
                "intent": "update_order",
                "message": "주문 수정 기능은 준비 중입니다. 주문번호와 변경할 내용을 알려주세요.",
                "parsed_order": None
            }
        
        # 주문 조회 패턴
        if any(keyword in message_lower for keyword in ['조회', '확인', '찾아', '검색']):
            return {
                "intent": "query_order",
                "message": "주문 조회 기능은 준비 중입니다. 주문번호를 입력해주세요.",
                "parsed_order": None
            }
        
        # 기타
        return {
            "intent": "unknown",
            "message": "죄송합니다. 요청을 이해하지 못했습니다.\n\n**단일 배송:**\n'서울에서 부산으로 냉동 10팔레트 500kg 보내줘'\n\n**1:N 배송 (여러 곳으로):**\n'서울 창고에서 출발\n- 부산: 냉동 10팔레트\n- 대전: 냉동 15팔레트\n- 광주: 냉장 5팔레트'",
            "parsed_order": None
        }
    
    def _extract_order_info_simulation(self, message: str, db: Session) -> Dict[str, Any]:
        """
        시뮬레이션 모드에서 주문 정보 추출 (간단한 정규식)
        """
        
        order_info = {}
        
        # 온도대 추출
        if '냉동' in message:
            order_info['temperature_zone'] = '냉동'
        elif '냉장' in message:
            order_info['temperature_zone'] = '냉장'
        elif '상온' in message:
            order_info['temperature_zone'] = '상온'
        
        # 팔레트 수 추출 (p 약어 지원)
        pallet_match = re.search(r'(\d+)\s*(?:팔레트|p(?:allet)?)', message, re.IGNORECASE)
        if pallet_match:
            order_info['pallet_count'] = int(pallet_match.group(1))
        
        # 중량, 부피는 추출하지 않음
        
        # 상차지/하차지 추출 (간단한 패턴)
        # "서울에서 부산으로" 패턴
        location_match = re.search(r'([가-힣]+)에서\s*([가-힣]+)(?:으로|로)', message)
        if location_match:
            order_info['pickup_address'] = location_match.group(1)
            order_info['delivery_address'] = location_match.group(2)
        
        # 시간 추출 (예: "오전 9시", "14시")
        time_patterns = [
            (r'오전\s*(\d+)시', 'morning'),
            (r'오후\s*(\d+)시', 'afternoon'),
            (r'(\d+)시', 'hour')
        ]
        
        for pattern, time_type in time_patterns:
            matches = list(re.finditer(pattern, message))
            for idx, match in enumerate(matches):
                hour = int(match.group(1))
                
                # 오후 시간 변환
                if time_type == 'afternoon' and hour < 12:
                    hour += 12
                
                time_str = f"{hour:02d}:00"
                
                # 첫 번째 시간은 상차, 두 번째는 하차로 추정
                if idx == 0 or '상차' in message[:match.start()]:
                    order_info['pickup_start_time'] = time_str
                else:
                    order_info['delivery_start_time'] = time_str
        
        # 날짜 추출 (예: "내일", "오늘", "2024-02-05")
        if '내일' in message:
            order_info['order_date'] = (date.today() + timedelta(days=1)).isoformat()
        elif '오늘' in message or '당일' in message:
            order_info['order_date'] = date.today().isoformat()
        
        logger.info(f"추출된 주문 정보: {order_info}")
        return order_info
    
    def _extract_multiple_orders_simulation(self, message: str, db: Session) -> List[Dict[str, Any]]:
        """
        1:N 배송 패턴에서 여러 주문 정보 추출
        
        자동 1:N 인식 패턴:
        1. "서울에서 부산, 대구, 광주" → 상차지 1곳 + 하차지 여러 곳
        2. "서울 창고에서 부산점 10팔레트, 대구점 15팔레트"
        3. "서울에서 출발 - 부산: 10팔레트 - 대구: 15팔레트"
        """
        
        orders = []
        
        # 상차지 추출 (더 유연한 패턴)
        pickup_patterns = [
            r'([가-힣\s]+)(?:창고|센터|물류|점)?(?:에서|서)\s*(?:출발|시작|나가)',
            r'([가-힣\s]+)(?:창고|센터)?에서\s+([가-힣\s,]+)\s*(?:로|으로|배송|보내)',
        ]
        
        pickup_address = None
        for pattern in pickup_patterns:
            match = re.search(pattern, message)
            if match:
                pickup_address = match.group(1).strip()
                break
        
        if not pickup_address:
            # 단일 주문으로 처리
            return [self._extract_order_info_simulation(message, db)]
        
        logger.info(f"🚚 상차지 감지: {pickup_address}")
        logger.info(f"🔍 하차지 추출 시작... (메시지 길이: {len(message)}자)")
        
        # 하차지별 정보 추출 패턴 (더 다양한 형식 지원)
        delivery_patterns = [
            # "부산 10p, 대구 15p" (p = 팔레트 약어)
            r'([가-힣]+(?:점|창고|센터)?)\s+(\d+)\s*p(?:allet)?',
            # "부산 10팔레트, 대구 15팔레트" (쉼표 구분, 가장 일반적)
            r'([가-힣]+(?:점|창고|센터)?)\s+(\d+)\s*팔레트',
            # "부산 10팔레트 500kg" (중량 포함)
            r'([가-힣]+(?:점|창고|센터)?)\s+(\d+)\s*팔레트\s*(\d+(?:\.\d+)?)\s*kg',
            # "- 부산점: 냉동 10팔레트 500kg"
            r'[-•]\s*([가-힣\s]+[가-힣점])\s*[:：]?\s*(냉동|냉장|상온)?\s*(\d+)\s*팔레트\s*(\d+(?:\.\d+)?)\s*kg',
            # "1. 부산점 10팔레트 500kg"
            r'\d+\.\s*([가-힣\s]+(?:점|창고|센터)?)\s+(\d+)\s*팔레트(?:\s*(\d+(?:\.\d+)?)\s*kg)?',
        ]
        
        # 온도대 추출 (전체 메시지에서)
        temperature_zone = None
        if '냉동' in message:
            temperature_zone = '냉동'
        elif '냉장' in message:
            temperature_zone = '냉장'
        elif '상온' in message:
            temperature_zone = '상온'
        
        # 하차지 추출
        found_orders = []
        for pattern in delivery_patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                groups = match.groups()
                
                # 패턴에 따라 파싱
                delivery_address = None
                pallet_count = None
                temp_zone = temperature_zone
                
                if len(groups) == 2:  # 패턴 1: "부산 10팔레트"
                    delivery_address = groups[0].strip()
                    pallet_count = int(groups[1])
                    
                elif len(groups) == 3:
                    # 패턴 2: "부산 10팔레트 500kg" 또는 패턴 4: "1. 부산 10팔레트"
                    delivery_address = groups[0].strip()
                    pallet_count = int(groups[1])
                    # 중량은 무시
                        
                elif len(groups) == 4:  # 패턴 3: "- 부산점: 냉동 10팔레트 500kg"
                    delivery_address = groups[0].strip()
                    temp_zone = groups[1] or temperature_zone
                    pallet_count = int(groups[2])
                    # 중량은 무시
                
                if delivery_address and pallet_count:
                    order_info = {
                        'pickup_address': pickup_address,
                        'delivery_address': delivery_address,
                        'pallet_count': pallet_count
                    }
                    
                    if temp_zone:
                        order_info['temperature_zone'] = temp_zone
                    
                    # 중복 체크 (같은 하차지는 한 번만)
                    if not any(o['delivery_address'] == delivery_address for o in found_orders):
                        found_orders.append(order_info)
                        logger.info(f"  📦 하차지 {len(found_orders)}: {delivery_address} - {pallet_count}팔레트")
        
        if not found_orders:
            logger.warning(f"⚠️ 하차지 추출 실패. 패턴 매칭 안 됨. 메시지 샘플: '{message[:100]}'")
        
        orders = found_orders
        
        # 날짜 추출 (모든 주문에 적용)
        order_date = None
        if '내일' in message:
            order_date = (date.today() + timedelta(days=1)).isoformat()
        elif '오늘' in message or '당일' in message:
            order_date = date.today().isoformat()
        
        if order_date:
            for order in orders:
                order['order_date'] = order_date
        
        # 팔레트 초과 체크 및 N:N 배차 추천
        if orders:
            total_pallets = sum(order.get('pallet_count', 0) for order in orders)
            logger.info(f"📊 총 팔레트: {total_pallets}개")
            
            # 대기 중 차량 조회
            available_vehicles = self._get_available_vehicles(db)
            if available_vehicles and total_pallets > 0:
                # N:N 배차 추천 필요 여부 체크
                dispatch_recommendation = self._recommend_dispatch(orders, available_vehicles, db)
                if dispatch_recommendation:
                    # 배차 추천 정보를 주문에 첨부
                    for order in orders:
                        order['_dispatch_recommendation'] = dispatch_recommendation
        
        logger.info(f"추출된 {len(orders)}개 주문: {orders}")
        return orders if orders else [self._extract_order_info_simulation(message, db)]
    
    def _format_multiple_orders_summary(self, orders: List[Dict[str, Any]]) -> str:
        """
        여러 주문 정보 요약 포맷팅
        """
        lines = []
        
        for idx, order in enumerate(orders, 1):
            lines.append(f"📦 **주문 {idx}**")
            
            if 'pickup_address' in order:
                lines.append(f"  • 상차지: {order['pickup_address']}")
            
            if 'delivery_address' in order:
                lines.append(f"  • 하차지: {order['delivery_address']}")
            
            if 'temperature_zone' in order:
                lines.append(f"  • 온도대: {order['temperature_zone']}")
            
            if 'pallet_count' in order:
                lines.append(f"  • 팔레트: {order['pallet_count']}개")
            
            # 중량은 표시하지 않음
            
            lines.append("")  # 빈 줄
        
        return '\n'.join(lines)
    
    def _accumulate_context(self, current_message: str, recent_messages: List[Dict[str, Any]]) -> str:
        """
        최근 대화 기록을 누적해서 컨텍스트 구성
        
        Args:
            current_message: 현재 메시지
            recent_messages: 최근 대화 기록 [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            누적된 컨텍스트 문자열
        """
        context_parts = []
        
        # 최근 5개 메시지만 사용 (너무 많으면 혼란)
        for msg in recent_messages[-5:]:
            if msg.get("role") == "user":
                context_parts.append(msg.get("content", ""))
        
        # 현재 메시지 추가
        context_parts.append(current_message)
        
        # 공백으로 연결
        accumulated = " ".join(context_parts)
        
        logger.info(f"📝 누적된 컨텍스트: {accumulated[:200]}...")
        
        return accumulated
    
    def _validate_order_info(self, order_info: Dict[str, Any]) -> bool:
        """
        주문 정보 유효성 검증
        """
        # 필수 필드: 온도대, (상차지 또는 하차지), 팔레트
        has_temperature = 'temperature_zone' in order_info
        has_location = 'pickup_address' in order_info or 'delivery_address' in order_info
        has_pallet = 'pallet_count' in order_info  # 중량은 선택 사항
        
        return has_temperature and has_location and has_pallet
    
    def _format_order_summary(self, order_info: Dict[str, Any]) -> str:
        """
        주문 정보 요약 포맷팅
        """
        lines = []
        
        if 'temperature_zone' in order_info:
            lines.append(f"• 온도대: {order_info['temperature_zone']}")
        
        if 'pickup_address' in order_info:
            lines.append(f"• 상차지: {order_info['pickup_address']}")
        
        if 'delivery_address' in order_info:
            lines.append(f"• 하차지: {order_info['delivery_address']}")
        
        if 'pallet_count' in order_info:
            lines.append(f"• 팔레트: {order_info['pallet_count']}개")
        
        # 중량, 부피는 표시하지 않음
        
        if 'pickup_start_time' in order_info:
            lines.append(f"• 상차시간: {order_info['pickup_start_time']}")
        
        if 'delivery_start_time' in order_info:
            lines.append(f"• 하차시간: {order_info['delivery_start_time']}")
        
        if 'order_date' in order_info:
            lines.append(f"• 주문일자: {order_info['order_date']}")
        
        return '\n'.join(lines)
    
    def _get_available_vehicles(self, db: Session) -> List[Dict[str, Any]]:
        """
        대기 중인 차량 조회
        
        Returns:
            [{"code": "V001", "max_pallets": 20, "status": "AVAILABLE"}, ...]
        """
        try:
            from app.models.vehicle import Vehicle
            
            # 대기 중 차량 조회 (상태가 AVAILABLE 또는 IDLE)
            vehicles = db.query(Vehicle).filter(
                Vehicle.is_active == True,
                Vehicle.status.in_(['AVAILABLE', 'IDLE', 'available', 'idle'])
            ).all()
            
            result = []
            for vehicle in vehicles:
                result.append({
                    'code': vehicle.code,
                    'plate_number': vehicle.plate_number,
                    'max_pallets': vehicle.max_pallets or 20,  # 기본값 20
                    'max_weight_kg': vehicle.max_weight_kg or 1000,  # 기본값 1톤
                    'status': vehicle.status
                })
            
            logger.info(f"🚛 대기 중 차량: {len(result)}대")
            return result
        except Exception as e:
            logger.error(f"차량 조회 오류: {e}")
            return []
    
    def _recommend_dispatch(
        self, 
        orders: List[Dict[str, Any]], 
        vehicles: List[Dict[str, Any]],
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        N:N 배차 추천
        
        Args:
            orders: 주문 리스트
            vehicles: 대기 중 차량 리스트
            db: 데이터베이스 세션
        
        Returns:
            {
                "needs_split": bool,  # 분할 필요 여부
                "total_pallets": int,
                "vehicle_assignments": [
                    {
                        "vehicle_code": "V001",
                        "assigned_orders": [0, 1, 2],  # 주문 인덱스
                        "total_pallets": 15,
                        "estimated_distance_km": 120.5,
                        "estimated_duration_min": 180
                    },
                    ...
                ],
                "message": str  # 추천 메시지
            }
        """
        
        if not orders or not vehicles:
            return None
        
        total_pallets = sum(order.get('pallet_count', 0) for order in orders)
        
        # 단일 차량으로 처리 가능한지 체크
        max_vehicle_capacity = max(v['max_pallets'] for v in vehicles)
        
        if total_pallets <= max_vehicle_capacity:
            # 단일 차량으로 처리 가능
            logger.info(f"✅ 단일 차량으로 처리 가능: {total_pallets}팔레트 <= {max_vehicle_capacity}팔레트")
            return None
        
        # N:N 배차 필요
        logger.info(f"⚠️ N:N 배차 필요: {total_pallets}팔레트 > {max_vehicle_capacity}팔레트")
        
        # 간단한 First-Fit 알고리즘으로 차량 할당
        vehicle_assignments = []
        current_vehicle_idx = 0
        current_pallets = 0
        current_orders = []
        
        for idx, order in enumerate(orders):
            order_pallets = order.get('pallet_count', 0)
            
            # 현재 차량에 추가 가능한지 체크
            if current_vehicle_idx < len(vehicles):
                vehicle_capacity = vehicles[current_vehicle_idx]['max_pallets']
                
                if current_pallets + order_pallets <= vehicle_capacity:
                    # 현재 차량에 추가
                    current_pallets += order_pallets
                    current_orders.append(idx)
                else:
                    # 현재 차량 마무리하고 다음 차량으로
                    if current_orders:
                        vehicle_assignments.append({
                            'vehicle_code': vehicles[current_vehicle_idx]['code'],
                            'plate_number': vehicles[current_vehicle_idx]['plate_number'],
                            'assigned_orders': current_orders.copy(),
                            'total_pallets': current_pallets
                        })
                    
                    # 다음 차량
                    current_vehicle_idx += 1
                    if current_vehicle_idx < len(vehicles):
                        current_pallets = order_pallets
                        current_orders = [idx]
                    else:
                        # 차량 부족
                        logger.warning(f"⚠️ 차량 부족: {len(vehicles)}대로 {len(orders)}건 처리 불가")
                        break
        
        # 마지막 차량 추가
        if current_orders and current_vehicle_idx < len(vehicles):
            vehicle_assignments.append({
                'vehicle_code': vehicles[current_vehicle_idx]['code'],
                'plate_number': vehicles[current_vehicle_idx]['plate_number'],
                'assigned_orders': current_orders.copy(),
                'total_pallets': current_pallets
            })
        
        if not vehicle_assignments:
            return None
        
        # 추천 메시지 생성
        message_lines = [
            f"\n🚛 **스마트 배차 추천**",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"총 {total_pallets}팔레트를 {len(vehicle_assignments)}대 차량에 분할 배정",
            ""
        ]
        
        for idx, assignment in enumerate(vehicle_assignments, 1):
            assigned_order_indices = assignment['assigned_orders']
            assigned_orders_info = [orders[i] for i in assigned_order_indices]
            destinations = ", ".join([o.get('delivery_address', '?') for o in assigned_orders_info])
            
            message_lines.append(
                f"🚚 **차량 {idx}**: {assignment['vehicle_code']} ({assignment['plate_number']})"
            )
            message_lines.append(f"   • 팔레트: {assignment['total_pallets']}개")
            message_lines.append(f"   • 하차지: {destinations}")
            message_lines.append("")
        
        return {
            'needs_split': True,
            'total_pallets': total_pallets,
            'vehicle_count': len(vehicle_assignments),
            'vehicle_assignments': vehicle_assignments,
            'message': '\n'.join(message_lines)
        }
    
    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 생성 (대화+주문 모두 지원)"""
        return """당신은 물류 주문 AI 어시스턴트입니다. 일반 대화와 주문 처리 모두 가능합니다.

**대화 유형:**
- 인사/일상 대화 (안녕?, 고마워 등) → intent: "greeting"
- 주문 문의/질문 → intent: "question"  
- 실제 주문 요청 → intent: "create_order" 또는 "create_multiple_orders"

**필수 주문 정보:**
1. 온도대 (temperature_zone): 냉동/냉장/상온 중 하나 (필수)
2. 상차지(pickup_address) 또는 하차지(delivery_address): 최소 하나 (필수)
3. 팔레트 수 (pallet_count): 숫자 + "p"/"P"/"팔레트" (필수)

**선택 정보:**
- order_date: 주문일 (YYYY-MM-DD)
- pickup_start_time, delivery_start_time: HH:MM 형식
- notes: 메모

**응답 형식 (JSON):**

1. 인사/일반 대화:
{
  "intent": "greeting",
  "message": "안녕하세요! 무엇을 도와드릴까요?",
  "parsed_order": {}
}

2. 주문 문의:
{
  "intent": "question",
  "message": "주문하시려면 온도대, 상차지(또는 하차지), 팔레트 수를 알려주세요.",
  "parsed_order": {}
}

3. 정보 부족:
{
  "intent": "need_more_info",
  "message": "주문 정보가 부족합니다. 다음을 알려주세요:\n• 온도대 (냉동/냉장/상온)\n• 상차지 또는 하차지\n• 팔레트 수",
  "parsed_order": {"temperature_zone": "냉동"}
}

4. 단일 주문:
{
  "intent": "create_order",
  "message": "주문이 접수되었습니다.",
  "parsed_order": {
    "temperature_zone": "냉동",
    "pickup_address": "서울",
    "delivery_address": "부산",
    "pallet_count": 10
  }
}

5. 다건 주문 (1:N 배송):
{
  "intent": "create_multiple_orders",
  "message": "3건의 주문이 접수되었습니다.",
  "parsed_orders": [
    {"temperature_zone": "냉동", "pickup_address": "서울", "delivery_address": "부산", "pallet_count": 10},
    {"temperature_zone": "냉동", "pickup_address": "서울", "delivery_address": "대구", "pallet_count": 5}
  ]
}

**처리 규칙:**
1. 주문이 아닌 대화는 intent를 "greeting" 또는 "question"으로 설정
2. 필수 정보 부족 시 "need_more_info" 반환
3. 시간: HH:MM (예: "오전 9시" → "09:00")
4. 날짜: YYYY-MM-DD (예: "내일" → 계산된 날짜)
5. "10p", "5P", "3팔레트" → pallet_count로 변환
6. 하차지가 여러 개면 "create_multiple_orders"로 처리
7. 응답은 반드시 유효한 JSON
8. 친절하고 자연스러운 대화 유지"""

    def _build_user_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """
        사용자 프롬프트 생성
        """
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        prompt_parts = [
            f"**현재 날짜:** {today}",
            f"**내일 날짜:** {tomorrow}",
            f"",
            f"**사용자 입력:**",
            f"{message}",
            f"",
            "위 입력에서 주문 정보를 추출하고 적절한 intent와 message를 생성하세요.",
            "하차지가 여러 개면 parsed_orders 배열로 반환하세요."
        ]
        
        if context.get("pending_order") or context.get("pending_orders"):
            prompt_parts.append(f"\n**현재 확인 대기 중인 주문이 있습니다.**")
        
        return "\n".join(prompt_parts)
        
        if context.get("recent_messages"):
            messages_str = "\n".join([f"- {m['role']}: {m['content']}" for m in context['recent_messages'][-3:]])
            prompt_parts.append(f"\n최근 대화:\n{messages_str}")
        
        return "\n".join(prompt_parts)
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> tuple:
        """
        모델별 토큰당 비용 계산 (USD)
        
        Args:
            model: 모델명 (gpt-4o, gpt-3.5-turbo, etc.)
            prompt_tokens: 입력 토큰 수
            completion_tokens: 출력 토큰 수
        
        Returns:
            (prompt_cost, completion_cost) 튜플
        """
        
        # 모델별 비용 정의 (per 1M tokens)
        # 출처: https://openai.com/pricing
        pricing = {
            "gpt-4o": {
                "prompt": 5.0,      # $5 / 1M input tokens
                "completion": 15.0   # $15 / 1M output tokens
            },
            "gpt-4-turbo": {
                "prompt": 10.0,     # $10 / 1M input tokens
                "completion": 30.0   # $30 / 1M output tokens
            },
            "gpt-3.5-turbo": {
                "prompt": 0.5,      # $0.5 / 1M input tokens
                "completion": 1.5    # $1.5 / 1M output tokens
            },
            "gemini-pro": {
                "prompt": 0.0,      # 무료 (일일 제한 있음)
                "completion": 0.0
            }
        }
        
        # 모델 가격 가져오기 (기본값: gpt-4o)
        model_pricing = pricing.get(model, pricing["gpt-4o"])
        
        # 비용 계산 (토큰 수 / 1,000,000 * 단가)
        prompt_cost = (prompt_tokens / 1_000_000) * model_pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * model_pricing["completion"]
        
        return (prompt_cost, completion_cost)
