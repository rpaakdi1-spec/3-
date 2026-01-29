"""
배송 추적 API

고객용 배송 추적 시스템 엔드포인트:
- 공개 추적 (인증 불필요)
- 추적번호 생성
- 배송 상태 조회
- 타임라인 조회
- 경로 정보 조회
- 알림 전송
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.delivery_tracking_service import DeliveryTrackingService
from app.schemas.tracking import (
    TrackingNumberCreate,
    TrackingNumberResponse,
    DeliveryStatusResponse,
    DeliveryTimelineResponse,
    RouteDetailsResponse,
    PublicTrackingResponse,
    NotificationRequest,
    NotificationResponse
)
from app.models.order import Order

router = APIRouter()


@router.get(
    "/public/{tracking_number}",
    response_model=PublicTrackingResponse,
    summary="공개 배송 추적",
    description="추적번호로 배송 정보를 조회합니다 (인증 불필요)",
    tags=["Public Tracking"]
)
async def get_public_tracking(
    tracking_number: str,
    db: Session = Depends(get_db)
):
    """
    공개 배송 추적
    
    - 인증 없이 추적번호만으로 조회 가능
    - 민감한 정보는 제외하고 제한된 정보만 제공
    - 고객에게 공유하기 위한 용도
    
    **추적번호 형식:** TRK-YYYYMMDD-{8자리 해시}
    
    **반환 정보:**
    - 배송 상태
    - 타임라인
    - 예상 도착 시간
    - 상하차 주소 (상세 주소 제외)
    - 온도대, 팔레트 수
    """
    info = DeliveryTrackingService.get_public_tracking_info(db, tracking_number)
    
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추적 정보를 찾을 수 없습니다. 추적번호를 확인해주세요."
        )
    
    return info


@router.post(
    "/generate",
    response_model=TrackingNumberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="추적번호 생성",
    description="주문에 대한 추적번호를 생성합니다"
)
async def generate_tracking_number(
    data: TrackingNumberCreate,
    db: Session = Depends(get_db)
):
    """
    추적번호 생성
    
    - 주문 ID 또는 주문번호로 추적번호 생성
    - 추측 불가능하고 유일한 추적번호 생성
    - 고객에게 공유하여 배송 추적에 사용
    
    **추적번호 형식:**
    - TRK-YYYYMMDD-{8자리 해시}
    - 예: TRK-20260127-A3F5B2C1
    """
    # 주문 조회
    if data.order_id:
        order = db.query(Order).filter(Order.id == data.order_id).first()
    elif data.order_number:
        order = db.query(Order).filter(Order.order_number == data.order_number).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order_id 또는 order_number 중 하나는 필수입니다"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 추적번호 생성
    tracking_number = DeliveryTrackingService.generate_tracking_number(
        order.id,
        order.order_number
    )
    
    return {
        "tracking_number": tracking_number,
        "order_id": order.id,
        "order_number": order.order_number,
        "message": "추적번호가 생성되었습니다"
    }


@router.get(
    "/status",
    response_model=DeliveryStatusResponse,
    summary="배송 상태 조회",
    description="주문의 현재 배송 상태를 조회합니다"
)
async def get_delivery_status(
    order_id: Optional[int] = Query(None, description="주문 ID"),
    order_number: Optional[str] = Query(None, description="주문번호"),
    db: Session = Depends(get_db)
):
    """
    배송 상태 조회
    
    - order_id 또는 order_number로 조회
    - 현재 배송 상태, 위치, 진행률 반환
    - 배차 정보, 차량/기사 정보 포함
    
    **반환 정보:**
    - 배송 상태 (배차대기, 배차완료, 운송중, 배송완료, 취소)
    - 배차번호, 배차일자
    - 차량번호, 기사 정보
    - 현재 위치 (위경도, 주소)
    - 진행률 (0-100%)
    """
    if not order_id and not order_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order_id 또는 order_number 중 하나는 필수입니다"
        )
    
    # 주문 조회
    if order_id:
        order = db.query(Order).filter(Order.id == order_id).first()
    else:
        order = db.query(Order).filter(Order.order_number == order_number).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 배송 상태 조회
    status_info = DeliveryTrackingService.get_delivery_status(db, order.id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="배송 정보를 찾을 수 없습니다"
        )
    
    return status_info


@router.get(
    "/timeline",
    response_model=DeliveryTimelineResponse,
    summary="배송 타임라인 조회",
    description="주문의 배송 타임라인을 조회합니다"
)
async def get_delivery_timeline(
    order_id: Optional[int] = Query(None, description="주문 ID"),
    order_number: Optional[str] = Query(None, description="주문번호"),
    db: Session = Depends(get_db)
):
    """
    배송 타임라인 조회
    
    - 주문 생성부터 현재까지의 모든 이벤트 반환
    - 시간순으로 정렬된 타임라인
    - 각 이벤트의 상태 (완료, 진행중, 예정)
    
    **타임라인 이벤트:**
    1. 주문 접수
    2. 배차 완료
    3. 상차 예정/완료
    4. 운송 중
    5. 하차 예정/완료
    6. 배송 완료
    """
    if not order_id and not order_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order_id 또는 order_number 중 하나는 필수입니다"
        )
    
    # 주문 조회
    if order_id:
        order = db.query(Order).filter(Order.id == order_id).first()
    else:
        order = db.query(Order).filter(Order.order_number == order_number).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 타임라인 조회
    timeline = DeliveryTrackingService.get_delivery_timeline(db, order.id)
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "timeline": timeline
    }


@router.get(
    "/route",
    response_model=RouteDetailsResponse,
    summary="배송 경로 조회",
    description="주문의 상세 배송 경로를 조회합니다"
)
async def get_route_details(
    order_id: Optional[int] = Query(None, description="주문 ID"),
    order_number: Optional[str] = Query(None, description="주문번호"),
    db: Session = Depends(get_db)
):
    """
    배송 경로 조회
    
    - 전체 배송 경로 정보 반환
    - 각 경유지의 위치, 예상 시간 포함
    - 차량 및 기사 정보
    - 지도 표시용 좌표 제공
    
    **경로 정보:**
    - 차고지 출발
    - 상차 지점들
    - 하차 지점들 (현재 주문 포함)
    - 차고지 복귀
    - 각 지점의 위경도, 예상 도착/출발 시간
    """
    if not order_id and not order_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order_id 또는 order_number 중 하나는 필수입니다"
        )
    
    # 주문 조회
    if order_id:
        order = db.query(Order).filter(Order.id == order_id).first()
    else:
        order = db.query(Order).filter(Order.order_number == order_number).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 경로 조회
    route_details = DeliveryTrackingService.get_route_details(db, order.id)
    
    if not route_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="배송 경로 정보를 찾을 수 없습니다"
        )
    
    return route_details


@router.post(
    "/notify",
    response_model=NotificationResponse,
    summary="알림 전송",
    description="고객에게 배송 알림을 전송합니다"
)
async def send_notification(
    request: NotificationRequest,
    db: Session = Depends(get_db)
):
    """
    알림 전송
    
    - SMS 또는 이메일로 배송 알림 전송
    - 주문 상태 변경 시 자동 알림 가능
    
    **알림 유형:**
    - ORDER_CONFIRMED: 주문 접수 확인
    - DISPATCH_ASSIGNED: 배차 완료 알림
    - IN_TRANSIT: 운송 시작 알림
    - DELIVERED: 배송 완료 알림
    
    **전송 채널:**
    - SMS: 휴대폰 번호로 전송
    - EMAIL: 이메일 주소로 전송
    """
    # 주문 확인
    order = db.query(Order).filter(Order.id == request.order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 알림 전송
    success = DeliveryTrackingService.send_notification(
        order_id=request.order_id,
        notification_type=request.notification_type,
        recipient=request.recipient,
        channel=request.channel
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="알림 전송에 실패했습니다"
        )
    
    return {
        "success": True,
        "message": "알림이 전송되었습니다",
        "notification_type": request.notification_type,
        "channel": request.channel,
        "recipient": request.recipient
    }


@router.get(
    "/estimated-arrival",
    summary="예상 도착 시간 조회",
    description="주문의 예상 도착 시간을 조회합니다"
)
async def get_estimated_arrival(
    order_id: Optional[int] = Query(None, description="주문 ID"),
    order_number: Optional[str] = Query(None, description="주문번호"),
    db: Session = Depends(get_db)
):
    """
    예상 도착 시간 조회
    
    - 현재 위치와 배송지 사이의 거리 계산
    - 평균 속도와 교통 상황을 고려한 예상 시간
    - 실시간 위치 정보 기반 동적 계산
    
    **계산 방식:**
    1. 현재 차량 위치 조회
    2. 배송지까지의 거리 계산 (Haversine 공식)
    3. 평균 속도로 소요 시간 계산
    4. 교통 상황 고려 (+30% 여유)
    """
    if not order_id and not order_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order_id 또는 order_number 중 하나는 필수입니다"
        )
    
    # 주문 조회
    if order_id:
        order = db.query(Order).filter(Order.id == order_id).first()
    else:
        order = db.query(Order).filter(Order.order_number == order_number).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 예상 도착 시간 계산
    estimated_time = DeliveryTrackingService.get_estimated_arrival_time(db, order.id)
    
    if not estimated_time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="예상 도착 시간을 계산할 수 없습니다"
        )
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "estimated_arrival_time": estimated_time,
        "message": "예상 도착 시간이 계산되었습니다"
    }
