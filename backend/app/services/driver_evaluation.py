"""
Driver Performance Evaluation System - Phase 10
운전자 평가 시스템
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import User, Dispatch, Order, Vehicle
import numpy as np


class DriverEvaluationSystem:
    """운전자 평가 시스템"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_driver(
        self,
        driver_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        운전자 종합 평가
        
        평가 항목:
        - 배송 완료율
        - 정시 배송률
        - 고객 만족도 (평가가 있는 경우)
        - 안전 운전 점수
        - 효율성 점수
        """
        driver = self.db.query(User).filter(
            and_(
                User.id == driver_id,
                User.role == 'DRIVER'
            )
        ).first()
        
        if not driver:
            return {'error': 'Driver not found'}
        
        # 기간 내 배차 조회 (driver_id 없으므로 driver_name으로 조회)
        # TODO: Vehicle 모델에 driver_id 추가 필요
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).all()
        
        if not dispatches:
            return {
                'driver_name': driver.full_name,
                'driver_id': driver_id,
                'message': 'No dispatch records found for this period'
            }
        
        # 각 항목 평가
        delivery_score = self._evaluate_delivery_completion(dispatches)
        on_time_score = self._evaluate_on_time_delivery(dispatches)
        efficiency_score = self._evaluate_efficiency(dispatches)
        safety_score = self._evaluate_safety(dispatches, driver_id)
        customer_score = self._evaluate_customer_satisfaction(dispatches)
        
        # 종합 점수 계산 (가중 평균)
        overall_score = (
            delivery_score * 0.25 +
            on_time_score * 0.25 +
            efficiency_score * 0.20 +
            safety_score * 0.15 +
            customer_score * 0.15
        )
        
        # 등급 결정
        grade = self._determine_grade(overall_score)
        
        # 통계
        total_deliveries = sum([len(d.orders) for d in dispatches])
        completed_deliveries = sum([
            sum(1 for o in d.orders if o.status == 'COMPLETED')
            for d in dispatches
        ])
        
        return {
            'driver_id': driver_id,
            'driver_name': driver.full_name,
            'period': {
                'start': start_date.date().isoformat(),
                'end': end_date.date().isoformat()
            },
            'overall_score': round(overall_score, 2),
            'grade': grade,
            'scores': {
                'delivery_completion': round(delivery_score, 2),
                'on_time_delivery': round(on_time_score, 2),
                'efficiency': round(efficiency_score, 2),
                'safety': round(safety_score, 2),
                'customer_satisfaction': round(customer_score, 2)
            },
            'statistics': {
                'total_dispatches': len(dispatches),
                'total_deliveries': total_deliveries,
                'completed_deliveries': completed_deliveries,
                'completion_rate': round((completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0, 2)
            },
            'strengths': self._identify_strengths(delivery_score, on_time_score, efficiency_score, safety_score, customer_score),
            'areas_for_improvement': self._identify_weaknesses(delivery_score, on_time_score, efficiency_score, safety_score, customer_score)
        }
    
    def _evaluate_delivery_completion(self, dispatches: List[Dispatch]) -> float:
        """배송 완료율 평가 (0-100점)"""
        total_orders = 0
        completed_orders = 0
        
        for dispatch in dispatches:
            for order in dispatch.orders:
                total_orders += 1
                if order.status == 'COMPLETED':
                    completed_orders += 1
        
        if total_orders == 0:
            return 100.0
        
        completion_rate = (completed_orders / total_orders) * 100
        return completion_rate
    
    def _evaluate_on_time_delivery(self, dispatches: List[Dispatch]) -> float:
        """정시 배송률 평가 (0-100점)"""
        total_deliveries = 0
        on_time_deliveries = 0
        
        for dispatch in dispatches:
            for order in dispatch.orders:
                if order.status == 'COMPLETED' and order.completed_at:
                    total_deliveries += 1
                    
                    # 예상 배송 시간과 실제 배송 시간 비교
                    if order.expected_delivery_time:
                        # 30분 허용 오차
                        deadline = order.expected_delivery_time + timedelta(minutes=30)
                        if order.completed_at <= deadline:
                            on_time_deliveries += 1
                    else:
                        # 예상 시간이 없으면 정시로 간주
                        on_time_deliveries += 1
        
        if total_deliveries == 0:
            return 100.0
        
        on_time_rate = (on_time_deliveries / total_deliveries) * 100
        return on_time_rate
    
    def _evaluate_efficiency(self, dispatches: List[Dispatch]) -> float:
        """효율성 평가 (0-100점)"""
        if not dispatches:
            return 0
        
        efficiency_scores = []
        
        for dispatch in dispatches:
            # 시간당 배송 건수
            if hasattr(dispatch, 'started_at') and hasattr(dispatch, 'completed_at'):
                if dispatch.completed_at and dispatch.started_at:
                    duration_hours = (dispatch.completed_at - dispatch.started_at).total_seconds() / 3600
                    deliveries_count = len(dispatch.orders)
                    
                    if duration_hours > 0:
                        deliveries_per_hour = deliveries_count / duration_hours
                        # 시간당 3건 이상이면 만점
                        score = min((deliveries_per_hour / 3) * 100, 100)
                        efficiency_scores.append(score)
        
        if not efficiency_scores:
            # 대안: 배차당 평균 주문 수 기준
            avg_orders_per_dispatch = sum(len(d.orders) for d in dispatches) / len(dispatches)
            # 배차당 5건 이상이면 만점
            return min((avg_orders_per_dispatch / 5) * 100, 100)
        
        return np.mean(efficiency_scores)
    
    def _evaluate_safety(self, dispatches: List[Dispatch], driver_id: int) -> float:
        """
        안전 운전 평가 (0-100점)
        
        실제로는 다음 데이터 필요:
        - 속도 위반 기록
        - 급정거/급가속 횟수
        - 사고 기록
        - GPS 데이터 분석
        
        현재는 간단한 추정치 사용
        """
        # 사고/위반 기록이 없다고 가정
        base_score = 100.0
        
        # 배송 지연이 안전 문제의 간접 지표일 수 있음
        delayed_deliveries = 0
        total_deliveries = 0
        
        for dispatch in dispatches:
            for order in dispatch.orders:
                if order.status == 'COMPLETED' and order.completed_at:
                    total_deliveries += 1
                    if order.expected_delivery_time:
                        # 1시간 이상 지연
                        if order.completed_at > order.expected_delivery_time + timedelta(hours=1):
                            delayed_deliveries += 1
        
        if total_deliveries > 0:
            delay_rate = delayed_deliveries / total_deliveries
            # 지연율이 높으면 점수 감점
            penalty = delay_rate * 20  # 최대 20점 감점
            base_score -= penalty
        
        return max(base_score, 60)  # 최소 60점
    
    def _evaluate_customer_satisfaction(self, dispatches: List[Dispatch]) -> float:
        """
        고객 만족도 평가 (0-100점)
        
        실제로는 고객 피드백/평점 데이터 필요
        현재는 배송 완료율과 정시 배송률 기반 추정
        """
        # 배송 완료율
        completion_score = self._evaluate_delivery_completion(dispatches)
        
        # 정시 배송률
        on_time_score = self._evaluate_on_time_delivery(dispatches)
        
        # 가중 평균
        satisfaction_score = (completion_score * 0.5 + on_time_score * 0.5)
        
        return satisfaction_score
    
    def _determine_grade(self, score: float) -> str:
        """점수에 따른 등급 결정"""
        if score >= 90:
            return 'S (우수)'
        elif score >= 80:
            return 'A (양호)'
        elif score >= 70:
            return 'B (보통)'
        elif score >= 60:
            return 'C (개선 필요)'
        else:
            return 'D (긴급 개선 필요)'
    
    def _identify_strengths(
        self,
        delivery: float,
        on_time: float,
        efficiency: float,
        safety: float,
        customer: float
    ) -> List[str]:
        """강점 식별"""
        strengths = []
        scores = {
            '배송 완료율': delivery,
            '정시 배송률': on_time,
            '효율성': efficiency,
            '안전 운전': safety,
            '고객 만족도': customer
        }
        
        for metric, score in scores.items():
            if score >= 85:
                strengths.append(f"{metric} 우수 ({score:.1f}점)")
        
        return strengths if strengths else ['전반적으로 양호한 성과']
    
    def _identify_weaknesses(
        self,
        delivery: float,
        on_time: float,
        efficiency: float,
        safety: float,
        customer: float
    ) -> List[str]:
        """개선 영역 식별"""
        weaknesses = []
        scores = {
            '배송 완료율': delivery,
            '정시 배송률': on_time,
            '효율성': efficiency,
            '안전 운전': safety,
            '고객 만족도': customer
        }
        
        for metric, score in scores.items():
            if score < 70:
                weaknesses.append(f"{metric} 개선 필요 ({score:.1f}점)")
        
        return weaknesses if weaknesses else ['현재 개선이 필요한 영역 없음']
    
    def get_driver_rankings(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        전체 운전자 랭킹
        
        Returns:
            운전자별 성과 순위
        """
        drivers = self.db.query(User).filter(User.role == 'DRIVER').all()
        
        driver_evaluations = []
        
        for driver in drivers:
            evaluation = self.evaluate_driver(driver.id, start_date, end_date)
            
            if 'error' not in evaluation and 'message' not in evaluation:
                driver_evaluations.append(evaluation)
        
        # 종합 점수 기준 정렬
        ranked_drivers = sorted(
            driver_evaluations,
            key=lambda x: x['overall_score'],
            reverse=True
        )
        
        # 순위 추가
        for i, driver in enumerate(ranked_drivers, 1):
            driver['rank'] = i
        
        return ranked_drivers
    
    def get_improvement_recommendations(
        self,
        driver_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        운전자별 맞춤 개선 권장사항
        
        Returns:
            구체적인 개선 방안 및 교육 추천
        """
        evaluation = self.evaluate_driver(driver_id, start_date, end_date)
        
        if 'error' in evaluation or 'message' in evaluation:
            return evaluation
        
        recommendations = []
        training_programs = []
        
        scores = evaluation['scores']
        
        # 배송 완료율이 낮은 경우
        if scores['delivery_completion'] < 80:
            recommendations.append({
                'area': '배송 완료율',
                'current_score': scores['delivery_completion'],
                'target_score': 90,
                'actions': [
                    '배송 전 차량 및 장비 점검 철저히',
                    '고객과의 사전 연락 강화',
                    '예상 지연 시 즉시 보고'
                ]
            })
            training_programs.append('배송 프로세스 표준화 교육')
        
        # 정시 배송률이 낮은 경우
        if scores['on_time_delivery'] < 80:
            recommendations.append({
                'area': '정시 배송률',
                'current_score': scores['on_time_delivery'],
                'target_score': 90,
                'actions': [
                    '출발 전 경로 계획 수립',
                    '실시간 교통 정보 활용',
                    '여유 시간 확보'
                ]
            })
            training_programs.append('경로 최적화 및 시간 관리 교육')
        
        # 효율성이 낮은 경우
        if scores['efficiency'] < 70:
            recommendations.append({
                'area': '업무 효율성',
                'current_score': scores['efficiency'],
                'target_score': 85,
                'actions': [
                    '배송 순서 최적화',
                    '하역 시간 단축 방안 모색',
                    '고객별 특이사항 사전 파악'
                ]
            })
            training_programs.append('효율적 업무 수행 기법 교육')
        
        # 안전 점수가 낮은 경우
        if scores['safety'] < 80:
            recommendations.append({
                'area': '안전 운전',
                'current_score': scores['safety'],
                'target_score': 95,
                'actions': [
                    '안전 속도 준수',
                    '충분한 휴식 시간 확보',
                    '차량 정기 점검'
                ]
            })
            training_programs.append('안전 운전 교육 (필수)')
        
        # 고객 만족도가 낮은 경우
        if scores['customer_satisfaction'] < 75:
            recommendations.append({
                'area': '고객 서비스',
                'current_score': scores['customer_satisfaction'],
                'target_score': 90,
                'actions': [
                    '친절한 고객 응대',
                    '화물 취급 주의',
                    '정확한 정보 전달'
                ]
            })
            training_programs.append('고객 서비스 교육')
        
        if not recommendations:
            recommendations.append({
                'message': '현재 모든 영역에서 우수한 성과를 보이고 있습니다. 계속 유지하세요!'
            })
        
        return {
            'driver_id': driver_id,
            'driver_name': evaluation['driver_name'],
            'current_grade': evaluation['grade'],
            'recommendations': recommendations,
            'suggested_training': training_programs,
            'follow_up_date': (datetime.now() + timedelta(days=30)).date().isoformat()
        }


# 글로벌 인스턴스
def get_driver_evaluation_system(db: Session) -> DriverEvaluationSystem:
    return DriverEvaluationSystem(db)
