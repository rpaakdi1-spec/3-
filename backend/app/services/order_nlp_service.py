"""
Natural Language Order Parsing Service
자연어 주문 파싱 서비스

거래처의 자연어 요청을 구조화된 주문으로 변환
"""
import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session
from loguru import logger

from app.models.client import Client
from app.models.order import TemperatureZone


class OrderNLPService:
    """자연어 주문 파싱 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # 온도대 키워드 매핑
        self.temp_keywords = {
            '냉동': TemperatureZone.FROZEN,
            '동결': TemperatureZone.FROZEN,
            '프로즌': TemperatureZone.FROZEN,
            'frozen': TemperatureZone.FROZEN,
            '냉장': TemperatureZone.REFRIGERATED,
            '저온': TemperatureZone.REFRIGERATED,
            '칠드': TemperatureZone.REFRIGERATED,
            'chilled': TemperatureZone.REFRIGERATED,
            'refrigerated': TemperatureZone.REFRIGERATED,
            '상온': TemperatureZone.AMBIENT,
            'ambient': TemperatureZone.AMBIENT,
            '실온': TemperatureZone.AMBIENT,
        }
    
    def parse_order_text(self, text: str) -> List[Dict]:
        """
        자연어 텍스트를 파싱하여 주문 목록 반환
        
        Args:
            text: 자연어 주문 텍스트
            
        Returns:
            파싱된 주문 목록
        """
        logger.info(f"📝 주문 텍스트 파싱 시작...")
        
        # 1. 텍스트를 줄 단위로 분리
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 2. 날짜 추출
        order_date = self._extract_date(text)
        logger.info(f"📅 추출된 날짜: {order_date}")
        
        # 3. 각 줄을 주문으로 파싱
        orders = []
        for line in lines:
            # 날짜/제목 줄은 스킵
            if self._is_header_line(line):
                continue
            
            # 화살표나 → 기호가 있는 줄만 처리
            if '→' in line or '->' in line or '에서' in line:
                order = self._parse_single_order(line, order_date)
                if order:
                    orders.append(order)
        
        logger.info(f"✅ 총 {len(orders)}건의 주문 파싱 완료")
        return orders
    
    def _extract_date(self, text: str) -> Optional[date]:
        """텍스트에서 날짜 추출"""
        # [02/03], 2/3, 02-03 등 다양한 형식 지원
        patterns = [
            r'\[(\d{1,2})/(\d{1,2})\]',  # [02/03]
            r'(\d{1,2})/(\d{1,2})',       # 02/03
            r'(\d{1,2})-(\d{1,2})',       # 02-03
        ]
        
        current_year = datetime.now().year
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                month = int(match.group(1))
                day = int(match.group(2))
                try:
                    return date(current_year, month, day)
                except ValueError:
                    continue
        
        # 날짜를 찾지 못하면 오늘 날짜
        return date.today()
    
    def _is_header_line(self, line: str) -> bool:
        """제목/헤더 줄인지 확인"""
        header_keywords = ['배차요청', '배차', '주문', '**', '###', '---']
        return any(keyword in line for keyword in header_keywords)
    
    def _parse_single_order(self, line: str, order_date: Optional[date]) -> Optional[Dict]:
        """단일 주문 줄 파싱"""
        try:
            result = {
                'order_date': order_date or date.today(),
                'raw_text': line,
                'confidence': 0.0,
                'needs_review': False
            }
            
            # 1. 온도대 추출
            temp_zone = self._extract_temperature(line)
            if temp_zone:
                result['temperature_zone'] = temp_zone
                result['confidence'] += 0.3
            
            # 2. 팔레트/톤수 추출
            pallet_count, weight_kg = self._extract_quantity(line)
            if pallet_count:
                result['pallet_count'] = pallet_count
                result['confidence'] += 0.2
            if weight_kg:
                result['weight_kg'] = weight_kg
                result['confidence'] += 0.1
            
            # 3. 거래처 추출 (화살표 기준)
            pickup_name, delivery_name = self._extract_clients(line)
            
            if pickup_name:
                # Fuzzy 매칭으로 거래처 찾기
                pickup_client = self._match_client(pickup_name)
                if pickup_client:
                    result['pickup_client_id'] = pickup_client.id
                    result['pickup_client_name'] = pickup_client.name
                    result['pickup_address'] = pickup_client.address
                    result['confidence'] += 0.3
                else:
                    result['pickup_client_name'] = pickup_name
                    result['needs_review'] = True
                    logger.warning(f"⚠️  상차 거래처 매칭 실패: {pickup_name}")
            
            if delivery_name:
                delivery_client = self._match_client(delivery_name)
                if delivery_client:
                    result['delivery_client_id'] = delivery_client.id
                    result['delivery_client_name'] = delivery_client.name
                    result['delivery_address'] = delivery_client.address
                    result['confidence'] += 0.3
                else:
                    result['delivery_client_name'] = delivery_name
                    result['needs_review'] = True
                    logger.warning(f"⚠️  하차 거래처 매칭 실패: {delivery_name}")
            
            # 4. 시간 추출 (15:30, 16:30 등)
            pickup_time = self._extract_time(line)
            if pickup_time:
                result['pickup_start_time'] = pickup_time
                result['confidence'] += 0.1
            
            # 신뢰도가 너무 낮으면 검토 필요
            if result['confidence'] < 0.5:
                result['needs_review'] = True
            
            logger.info(f"✅ 파싱 완료: {pickup_name or '?'} → {delivery_name or '?'} (신뢰도: {result['confidence']:.0%})")
            return result
            
        except Exception as e:
            logger.error(f"❌ 주문 파싱 실패: {line}, 오류: {e}")
            return None
    
    def _extract_temperature(self, text: str) -> Optional[TemperatureZone]:
        """온도대 추출"""
        text_lower = text.lower()
        for keyword, temp_zone in self.temp_keywords.items():
            if keyword in text_lower:
                return temp_zone
        return None
    
    def _extract_quantity(self, text: str) -> Tuple[Optional[int], Optional[float]]:
        """팔레트/중량 추출"""
        pallet_count = None
        weight_kg = None
        
        # 팔레트: "16판", "20팔레트" 등
        pallet_patterns = [
            r'(\d+)\s*판',
            r'(\d+)\s*팔레트',
            r'(\d+)\s*pallet',
        ]
        for pattern in pallet_patterns:
            match = re.search(pattern, text)
            if match:
                pallet_count = int(match.group(1))
                break
        
        # 중량: "5톤", "11ton" 등
        weight_patterns = [
            r'(\d+\.?\d*)\s*톤',
            r'(\d+\.?\d*)\s*ton',
            r'(\d+\.?\d*)\s*t\b',
        ]
        for pattern in weight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                weight_kg = float(match.group(1)) * 1000  # 톤을 kg으로 변환
                break
        
        return pallet_count, weight_kg
    
    def _extract_clients(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """거래처명 추출 (화살표 기준)"""
        # 화살표로 분리
        if '→' in text:
            parts = text.split('→')
        elif '->' in text:
            parts = text.split('->')
        elif '에서' in text and '로' in text:
            # "백암에서 경산으로"
            match = re.search(r'(\S+)\s*에서\s+(\S+)\s*[으로로]', text)
            if match:
                return match.group(1).strip(), match.group(2).strip()
            return None, None
        else:
            return None, None
        
        if len(parts) != 2:
            return None, None
        
        pickup = parts[0].strip()
        delivery = parts[1].strip()
        
        # 불필요한 부분 제거
        # "백암 _ 저온" → "백암"
        pickup = re.sub(r'[_\-].*', '', pickup).strip()
        # "경산 16판 1대" → "경산"
        delivery = re.split(r'\s+\d+', delivery)[0].strip()
        
        return pickup, delivery
    
    def _extract_time(self, text: str) -> Optional[str]:
        """시간 추출 (HH:MM 형식)"""
        match = re.search(r'(\d{1,2}):(\d{2})', text)
        if match:
            hour = match.group(1).zfill(2)
            minute = match.group(2)
            return f"{hour}:{minute}"
        return None
    
    def _match_client(self, client_name: str) -> Optional[Client]:
        """
        거래처명 매칭 (Fuzzy)
        
        Args:
            client_name: 검색할 거래처명
            
        Returns:
            매칭된 Client 객체 또는 None
        """
        try:
            from fuzzywuzzy import fuzz
        except ImportError:
            logger.warning("fuzzywuzzy not installed, using exact match only")
            # Fuzzy 매칭 불가능하면 정확한 매칭만
            return self.db.query(Client).filter(
                Client.is_active == True,
                Client.name == client_name
            ).first()
        
        # 활성 거래처만 검색
        clients = self.db.query(Client).filter(Client.is_active == True).all()
        
        if not clients:
            return None
        
        best_match = None
        best_score = 0
        
        for client in clients:
            # 이름 유사도
            score = fuzz.ratio(client_name, client.name)
            
            # 코드도 비교
            if client.code:
                code_score = fuzz.ratio(client_name, client.code)
                score = max(score, code_score)
            
            if score > best_score:
                best_score = score
                best_match = client
        
        # 80% 이상 유사도만 매칭
        if best_score >= 80:
            logger.info(f"✅ 거래처 매칭: '{client_name}' → '{best_match.name}' (유사도: {best_score}%)")
            return best_match
        
        return None
    
    def validate_orders(self, orders: List[Dict]) -> List[Dict]:
        """
        파싱된 주문 검증
        
        Args:
            orders: 파싱된 주문 목록
            
        Returns:
            검증된 주문 목록 (오류 메시지 포함)
        """
        validated = []
        
        for order in orders:
            errors = []
            
            # 필수 필드 체크
            if not order.get('pickup_client_id') and not order.get('pickup_address'):
                errors.append('상차지 정보 없음')
            
            if not order.get('delivery_client_id') and not order.get('delivery_address'):
                errors.append('하차지 정보 없음')
            
            if not order.get('pallet_count'):
                errors.append('팔레트 수 없음')
            
            if not order.get('temperature_zone'):
                errors.append('온도대 정보 없음')
            
            order['validation_errors'] = errors
            order['is_valid'] = len(errors) == 0
            
            if not order['is_valid']:
                order['needs_review'] = True
            
            validated.append(order)
        
        return validated


# Helper function for API usage
def parse_order_text(db: Session, text: str) -> Dict:
    """
    API에서 사용할 간단한 헬퍼 함수
    
    Args:
        db: Database session
        text: 자연어 주문 텍스트
        
    Returns:
        {
            'success': bool,
            'orders': List[Dict],
            'count': int,
            'message': str
        }
    """
    try:
        service = OrderNLPService(db)
        orders = service.parse_order_text(text)
        validated_orders = service.validate_orders(orders)
        
        return {
            'success': True,
            'orders': validated_orders,
            'count': len(validated_orders),
            'valid_count': sum(1 for o in validated_orders if o['is_valid']),
            'review_count': sum(1 for o in validated_orders if o.get('needs_review')),
            'message': f'{len(validated_orders)}건의 주문이 파싱되었습니다'
        }
    except Exception as e:
        logger.error(f"주문 파싱 오류: {e}")
        return {
            'success': False,
            'orders': [],
            'count': 0,
            'message': f'파싱 실패: {str(e)}'
        }
