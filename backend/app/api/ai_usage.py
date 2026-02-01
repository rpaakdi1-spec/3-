"""
AI 사용량 및 비용 모니터링 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import logging

from app.core.database import get_db
from app.models.ai_usage_log import AIUsageLog
from app.api.deps import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_usage_stats(
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    model_name: Optional[str] = Query(None, description="모델명 필터"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI 사용량 통계 조회
    
    **응답:**
    - total_requests: 총 요청 수
    - total_cost: 총 비용 (USD)
    - total_tokens: 총 토큰 수
    - by_model: 모델별 통계
    - by_date: 날짜별 통계
    - by_status: 상태별 통계
    """
    
    try:
        # 기본 필터 (날짜 범위)
        filters = []
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            filters.append(AIUsageLog.created_at >= start)
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            # 종료일 포함 (23:59:59까지)
            end = end.replace(hour=23, minute=59, second=59)
            filters.append(AIUsageLog.created_at <= end)
        
        if model_name:
            filters.append(AIUsageLog.model_name == model_name)
        
        # 전체 통계
        query = db.query(AIUsageLog)
        if filters:
            query = query.filter(and_(*filters))
        
        logs = query.all()
        
        # 총계 계산
        total_requests = len(logs)
        total_cost = sum(log.total_cost for log in logs)
        total_tokens = sum(log.total_tokens for log in logs)
        total_prompt_tokens = sum(log.prompt_tokens for log in logs)
        total_completion_tokens = sum(log.completion_tokens for log in logs)
        
        # 모델별 통계
        by_model = {}
        for log in logs:
            model = log.model_name
            if model not in by_model:
                by_model[model] = {
                    "requests": 0,
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "avg_response_time_ms": 0,
                    "success_rate": 0.0
                }
            
            by_model[model]["requests"] += 1
            by_model[model]["total_cost"] += log.total_cost
            by_model[model]["total_tokens"] += log.total_tokens
            by_model[model]["prompt_tokens"] += log.prompt_tokens
            by_model[model]["completion_tokens"] += log.completion_tokens
        
        # 모델별 평균 응답 시간 및 성공률 계산
        for model in by_model:
            model_logs = [log for log in logs if log.model_name == model]
            
            # 평균 응답 시간
            response_times = [log.response_time_ms for log in model_logs if log.response_time_ms]
            if response_times:
                by_model[model]["avg_response_time_ms"] = sum(response_times) / len(response_times)
            
            # 성공률
            success_count = len([log for log in model_logs if log.status == "success"])
            by_model[model]["success_rate"] = (success_count / len(model_logs)) * 100 if model_logs else 0
        
        # 날짜별 통계 (최근 7일)
        by_date = {}
        for log in logs:
            log_date = log.created_at.date().isoformat()
            if log_date not in by_date:
                by_date[log_date] = {
                    "date": log_date,
                    "requests": 0,
                    "total_cost": 0.0,
                    "total_tokens": 0
                }
            
            by_date[log_date]["requests"] += 1
            by_date[log_date]["total_cost"] += log.total_cost
            by_date[log_date]["total_tokens"] += log.total_tokens
        
        # 날짜순 정렬
        by_date_list = sorted(by_date.values(), key=lambda x: x["date"])
        
        # 상태별 통계
        by_status = {
            "success": len([log for log in logs if log.status == "success"]),
            "error": len([log for log in logs if log.status == "error"])
        }
        
        # Intent별 통계
        by_intent = {}
        for log in logs:
            intent = log.intent or "unknown"
            if intent not in by_intent:
                by_intent[intent] = {
                    "requests": 0,
                    "total_cost": 0.0
                }
            
            by_intent[intent]["requests"] += 1
            by_intent[intent]["total_cost"] += log.total_cost
        
        return {
            "total_requests": total_requests,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "by_model": by_model,
            "by_date": by_date_list,
            "by_status": by_status,
            "by_intent": by_intent
        }
    
    except Exception as e:
        logger.error(f"사용량 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_usage_logs(
    limit: int = Query(50, ge=1, le=100, description="조회할 로그 수"),
    offset: int = Query(0, ge=0, description="건너뛸 로그 수"),
    model_name: Optional[str] = Query(None, description="모델명 필터"),
    status: Optional[str] = Query(None, description="상태 필터 (success/error)"),
    start_date: Optional[str] = Query(None, description="시작 날짜"),
    end_date: Optional[str] = Query(None, description="종료 날짜"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI 사용량 로그 조회 (페이지네이션)
    """
    
    try:
        # 필터 구성
        filters = []
        
        if model_name:
            filters.append(AIUsageLog.model_name == model_name)
        
        if status:
            filters.append(AIUsageLog.status == status)
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            filters.append(AIUsageLog.created_at >= start)
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end = end.replace(hour=23, minute=59, second=59)
            filters.append(AIUsageLog.created_at <= end)
        
        # 쿼리 실행
        query = db.query(AIUsageLog)
        if filters:
            query = query.filter(and_(*filters))
        
        # 총 개수
        total = query.count()
        
        # 페이지네이션 적용 및 최신순 정렬
        logs = query.order_by(AIUsageLog.created_at.desc()).offset(offset).limit(limit).all()
        
        # 응답 데이터 구성
        items = []
        for log in logs:
            items.append({
                "id": log.id,
                "model_name": log.model_name,
                "provider": log.provider,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "total_tokens": log.total_tokens,
                "total_cost": round(log.total_cost, 6),
                "response_time_ms": log.response_time_ms,
                "status": log.status,
                "intent": log.intent,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat()
            })
        
        return {
            "total": total,
            "items": items,
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error(f"사용량 로그 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost-summary")
async def get_cost_summary(
    period: str = Query("7d", description="기간 (7d, 30d, 90d)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    비용 요약 정보
    
    **기간:**
    - 7d: 최근 7일
    - 30d: 최근 30일
    - 90d: 최근 90일
    """
    
    try:
        # 기간 계산
        period_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90
        }
        
        days = period_days.get(period, 7)
        start_date = datetime.now() - timedelta(days=days)
        
        # 해당 기간 로그 조회
        logs = db.query(AIUsageLog).filter(
            AIUsageLog.created_at >= start_date
        ).all()
        
        # 총 비용
        total_cost = sum(log.total_cost for log in logs)
        
        # 전일 대비 비용 (어제와 비교)
        yesterday_start = datetime.now() - timedelta(days=1)
        yesterday_start = yesterday_start.replace(hour=0, minute=0, second=0)
        yesterday_end = yesterday_start.replace(hour=23, minute=59, second=59)
        
        yesterday_logs = [log for log in logs if yesterday_start <= log.created_at <= yesterday_end]
        yesterday_cost = sum(log.total_cost for log in yesterday_logs)
        
        # 오늘 비용
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        today_logs = [log for log in logs if log.created_at >= today_start]
        today_cost = sum(log.total_cost for log in today_logs)
        
        # 일평균 비용
        avg_daily_cost = total_cost / days if days > 0 else 0
        
        # 모델별 비용
        model_costs = {}
        for log in logs:
            model = log.model_name
            if model not in model_costs:
                model_costs[model] = 0.0
            model_costs[model] += log.total_cost
        
        # 비용 비율 계산
        model_cost_percentage = {}
        for model, cost in model_costs.items():
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            model_cost_percentage[model] = {
                "cost": round(cost, 4),
                "percentage": round(percentage, 2)
            }
        
        return {
            "period": period,
            "period_days": days,
            "total_cost": round(total_cost, 4),
            "today_cost": round(today_cost, 4),
            "yesterday_cost": round(yesterday_cost, 4),
            "avg_daily_cost": round(avg_daily_cost, 4),
            "model_costs": model_cost_percentage,
            "total_requests": len(logs),
            "success_rate": (len([log for log in logs if log.status == "success"]) / len(logs) * 100) if logs else 0
        }
    
    except Exception as e:
        logger.error(f"비용 요약 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
