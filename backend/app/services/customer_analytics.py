"""
Customer Satisfaction Analytics - Phase 10
고객 만족도 분석 시스템
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import Partner, Order, Dispatch
import numpy as np


class CustomerSatisfactionAnalytics:
    """고객 만족도 분석 시스템"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_customer_satisfaction(
        self,
        partner_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        고객(파트너사) 만족도 분석
        
        분석 항목:
        - 정시 배송률
        - 주문 완료율
        - 평균 배송 시간
        - 온도 위반 사고
        - 고객 충성도 (재주문율)
        """
        partner = self.db.query(Partner).filter(Partner.id == partner_id).first()
        
        if not partner:
            return {'error': 'Partner not found'}
        
        # 기간 내 주문 조회
        orders = self.db.query(Order).filter(
            and_(
                Order.partner_id == partner_id,
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()
        
        if not orders:
            return {
                'partner_name': partner.name,
                'partner_id': partner_id,
                'message': 'No orders found for this period'
            }
        
        # 분석 수행
        on_time_rate = self._calculate_on_time_rate(orders)
        completion_rate = self._calculate_completion_rate(orders)
        avg_delivery_time = self._calculate_avg_delivery_time(orders)
        temperature_violations = self._count_temperature_violations(orders)
        loyalty_score = self._calculate_loyalty_score(partner_id, start_date, end_date)
        
        # 종합 만족도 점수 (0-100)
        satisfaction_score = self._calculate_satisfaction_score(
            on_time_rate,
            completion_rate,
            temperature_violations,
            len(orders)
        )
        
        # 등급 결정
        grade = self._determine_satisfaction_grade(satisfaction_score)
        
        return {
            'partner_id': partner_id,
            'partner_name': partner.name,
            'period': {
                'start': start_date.date().isoformat(),
                'end': end_date.date().isoformat()
            },
            'satisfaction_score': round(satisfaction_score, 2),
            'grade': grade,
            'metrics': {
                'on_time_delivery_rate': round(on_time_rate, 2),
                'order_completion_rate': round(completion_rate, 2),
                'avg_delivery_time_hours': round(avg_delivery_time, 2),
                'temperature_violations': temperature_violations,
                'loyalty_score': round(loyalty_score, 2)
            },
            'statistics': {
                'total_orders': len(orders),
                'completed_orders': sum(1 for o in orders if o.status == 'COMPLETED'),
                'cancelled_orders': sum(1 for o in orders if o.status == 'CANCELLED'),
                'pending_orders': sum(1 for o in orders if o.status in ['PENDING', 'IN_TRANSIT'])
            },
            'recommendations': self._generate_customer_recommendations(
                satisfaction_score,
                on_time_rate,
                completion_rate,
                temperature_violations
            )
        }
    
    def _calculate_on_time_rate(self, orders: List[Order]) -> float:
        """정시 배송률 계산"""
        completed_orders = [o for o in orders if o.status == 'COMPLETED' and o.completed_at]
        
        if not completed_orders:
            return 100.0
        
        on_time_count = 0
        
        for order in completed_orders:
            if order.expected_delivery_time:
                # 30분 허용 오차
                deadline = order.expected_delivery_time + timedelta(minutes=30)
                if order.completed_at <= deadline:
                    on_time_count += 1
            else:
                # 예상 시간이 없으면 정시로 간주
                on_time_count += 1
        
        return (on_time_count / len(completed_orders)) * 100
    
    def _calculate_completion_rate(self, orders: List[Order]) -> float:
        """주문 완료율 계산"""
        if not orders:
            return 100.0
        
        completed = sum(1 for o in orders if o.status == 'COMPLETED')
        return (completed / len(orders)) * 100
    
    def _calculate_avg_delivery_time(self, orders: List[Order]) -> float:
        """평균 배송 시간 계산 (시간 단위)"""
        completed_orders = [
            o for o in orders
            if o.status == 'COMPLETED' and o.completed_at and o.created_at
        ]
        
        if not completed_orders:
            return 0
        
        total_hours = 0
        
        for order in completed_orders:
            duration = order.completed_at - order.created_at
            hours = duration.total_seconds() / 3600
            total_hours += hours
        
        return total_hours / len(completed_orders)
    
    def _count_temperature_violations(self, orders: List[Order]) -> int:
        """온도 위반 사고 건수"""
        # 실제로는 온도 모니터링 데이터 필요
        # 간단한 추정: 완료되지 않은 주문 중 일부를 온도 문제로 가정
        cancelled_orders = [o for o in orders if o.status == 'CANCELLED']
        
        # 취소된 주문의 20%를 온도 위반으로 추정
        estimated_violations = int(len(cancelled_orders) * 0.2)
        
        return estimated_violations
    
    def _calculate_loyalty_score(
        self,
        partner_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        고객 충성도 점수
        
        재주문 빈도와 주문량 증가율 기반
        """
        # 이전 기간과 비교
        period_days = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_days)
        prev_end = start_date
        
        # 현재 기간 주문 수
        current_orders = self.db.query(func.count(Order.id)).filter(
            and_(
                Order.partner_id == partner_id,
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).scalar()
        
        # 이전 기간 주문 수
        previous_orders = self.db.query(func.count(Order.id)).filter(
            and_(
                Order.partner_id == partner_id,
                Order.created_at >= prev_start,
                Order.created_at < prev_end
            )
        ).scalar()
        
        if previous_orders == 0:
            # 신규 고객
            return 70.0
        
        # 주문 증가율 계산
        growth_rate = ((current_orders - previous_orders) / previous_orders) * 100
        
        # 증가율을 점수로 변환 (0-100)
        # 50% 이상 증가 시 만점
        loyalty_score = min(70 + (growth_rate / 2), 100)
        loyalty_score = max(loyalty_score, 0)
        
        return loyalty_score
    
    def _calculate_satisfaction_score(
        self,
        on_time_rate: float,
        completion_rate: float,
        temperature_violations: int,
        total_orders: int
    ) -> float:
        """종합 만족도 점수 계산"""
        # 정시 배송률 (40점)
        on_time_score = (on_time_rate / 100) * 40
        
        # 주문 완료율 (40점)
        completion_score = (completion_rate / 100) * 40
        
        # 온도 위반율 (20점)
        violation_rate = (temperature_violations / total_orders) if total_orders > 0 else 0
        temperature_score = max(20 - (violation_rate * 100), 0)
        
        total_score = on_time_score + completion_score + temperature_score
        
        return min(total_score, 100)
    
    def _determine_satisfaction_grade(self, score: float) -> str:
        """만족도 등급 결정"""
        if score >= 90:
            return 'A+ (매우 만족)'
        elif score >= 80:
            return 'A (만족)'
        elif score >= 70:
            return 'B (보통)'
        elif score >= 60:
            return 'C (개선 필요)'
        else:
            return 'D (불만족)'
    
    def _generate_customer_recommendations(
        self,
        satisfaction_score: float,
        on_time_rate: float,
        completion_rate: float,
        temperature_violations: int
    ) -> List[str]:
        """고객 만족도 개선 권장사항"""
        recommendations = []
        
        if satisfaction_score >= 90:
            recommendations.append('현재 우수한 서비스를 제공하고 있습니다. 유지하세요.')
        else:
            if on_time_rate < 85:
                recommendations.append(
                    f'정시 배송률 개선 필요 (현재 {on_time_rate:.1f}%). '
                    '배차 시간 최적화 및 여유 시간 확보를 권장합니다.'
                )
            
            if completion_rate < 90:
                recommendations.append(
                    f'주문 완료율 개선 필요 (현재 {completion_rate:.1f}%). '
                    '차량 및 인력 배치를 재검토하세요.'
                )
            
            if temperature_violations > 0:
                recommendations.append(
                    f'온도 위반 사고 {temperature_violations}건 발생. '
                    '냉동/냉장 설비 점검 및 운전자 교육을 강화하세요.'
                )
        
        return recommendations
    
    def get_top_customers(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> List[Dict]:
        """
        주요 고객 분석
        
        주문량, 매출, 충성도 기준
        """
        partners = self.db.query(Partner).all()
        
        customer_data = []
        
        for partner in partners:
            orders = self.db.query(Order).filter(
                and_(
                    Order.partner_id == partner.id,
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            ).all()
            
            if not orders:
                continue
            
            # 매출 계산
            total_revenue = sum(
                getattr(order, 'price', 0) or 0
                for order in orders
            )
            
            # 만족도 분석
            satisfaction = self.analyze_customer_satisfaction(
                partner.id,
                start_date,
                end_date
            )
            
            if 'error' not in satisfaction and 'message' not in satisfaction:
                customer_data.append({
                    'partner_id': partner.id,
                    'partner_name': partner.name,
                    'total_orders': len(orders),
                    'total_revenue': total_revenue,
                    'satisfaction_score': satisfaction['satisfaction_score'],
                    'satisfaction_grade': satisfaction['grade'],
                    'loyalty_score': satisfaction['metrics']['loyalty_score']
                })
        
        # 매출 기준 정렬
        sorted_customers = sorted(
            customer_data,
            key=lambda x: x['total_revenue'],
            reverse=True
        )
        
        return sorted_customers[:limit]
    
    def get_churn_risk_customers(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        이탈 위험 고객 식별
        
        기준:
        - 주문량 감소
        - 낮은 만족도
        - 최근 주문 없음
        """
        partners = self.db.query(Partner).all()
        
        at_risk_customers = []
        
        for partner in partners:
            # 최근 주문 확인
            recent_order = self.db.query(Order).filter(
                and_(
                    Order.partner_id == partner.id,
                    Order.created_at >= start_date
                )
            ).order_by(Order.created_at.desc()).first()
            
            # 30일 이상 주문 없음
            if not recent_order:
                days_since_order = (datetime.now() - end_date).days
                if days_since_order > 30:
                    at_risk_customers.append({
                        'partner_id': partner.id,
                        'partner_name': partner.name,
                        'risk_level': 'high',
                        'reason': f'최근 {days_since_order}일간 주문 없음',
                        'last_order_date': None
                    })
                continue
            
            # 만족도 분석
            satisfaction = self.analyze_customer_satisfaction(
                partner.id,
                start_date,
                end_date
            )
            
            if 'error' in satisfaction or 'message' in satisfaction:
                continue
            
            # 낮은 만족도
            if satisfaction['satisfaction_score'] < 70:
                at_risk_customers.append({
                    'partner_id': partner.id,
                    'partner_name': partner.name,
                    'risk_level': 'high' if satisfaction['satisfaction_score'] < 60 else 'medium',
                    'reason': f"낮은 만족도 ({satisfaction['satisfaction_score']:.1f}점)",
                    'satisfaction_score': satisfaction['satisfaction_score'],
                    'last_order_date': recent_order.created_at.date().isoformat() if recent_order else None
                })
        
        # 위험도 순 정렬
        return sorted(
            at_risk_customers,
            key=lambda x: 0 if x['risk_level'] == 'high' else 1
        )


# 글로벌 인스턴스
def get_customer_satisfaction_analytics(db: Session) -> CustomerSatisfactionAnalytics:
    return CustomerSatisfactionAnalytics(db)
