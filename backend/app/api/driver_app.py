"""
Phase 16: Driver App API
드라이버 앱 고도화 API 엔드포인트
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.driver_app import (
    NotificationType, DeliveryProofType, ChatMessageType
)
from app.services.notification_service import NotificationService
from app.services.chat_service import ChatService
from app.services.performance_service import PerformanceService


router = APIRouter()


# ==================== Pydantic Schemas ====================

class NotificationCreate(BaseModel):
    """알림 생성 스키마"""
    driver_id: int
    notification_type: NotificationType
    title: str
    message: str
    dispatch_id: Optional[int] = None
    action_required: bool = False
    action_url: Optional[str] = None


class PushTokenRegister(BaseModel):
    """Push 토큰 등록 스키마"""
    token: str
    device_type: Optional[str] = None
    device_id: Optional[str] = None


class ChatRoomCreate(BaseModel):
    """채팅방 생성 스키마"""
    room_name: str
    room_type: str
    participant_ids: List[int]


class ChatMessageCreate(BaseModel):
    """채팅 메시지 생성 스키마"""
    room_id: int
    message_type: ChatMessageType = ChatMessageType.TEXT
    content: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DeliveryProofCreate(BaseModel):
    """배송 증빙 생성 스키마"""
    dispatch_id: int
    order_id: int
    proof_type: DeliveryProofType
    note: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# ==================== 알림 API ====================

@router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    드라이버 알림 목록 조회
    
    - **unread_only**: 읽지 않은 알림만 조회
    - **limit**: 조회 개수
    """
    service = NotificationService(db)
    
    # 드라이버 ID 추출 (임시로 user_id 사용)
    driver_id = current_user.id
    
    notifications = service.get_driver_notifications(
        driver_id=driver_id,
        unread_only=unread_only,
        limit=limit
    )
    
    return {
        "notifications": [
            {
                "id": n.id,
                "notification_type": n.notification_type.value,
                "title": n.title,
                "message": n.message,
                "dispatch_id": n.dispatch_id,
                "is_read": n.is_read,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "action_required": n.action_required,
                "action_url": n.action_url,
                "action_taken": n.action_taken,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ],
        "total": len(notifications)
    }


@router.get("/notifications/unread-count")
async def get_unread_notification_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """읽지 않은 알림 개수"""
    service = NotificationService(db)
    driver_id = current_user.id
    
    count = service.get_unread_count(driver_id)
    
    return {"unread_count": count}


@router.post("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """알림 읽음 표시"""
    service = NotificationService(db)
    driver_id = current_user.id
    
    notification = service.mark_as_read(notification_id, driver_id)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}


@router.post("/notifications/{notification_id}/action")
async def mark_notification_action(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """알림 액션 수행 표시"""
    service = NotificationService(db)
    driver_id = current_user.id
    
    notification = service.mark_action_taken(notification_id, driver_id)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification action marked"}


@router.post("/push-tokens")
async def register_push_token(
    token_data: PushTokenRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Push 토큰 등록"""
    service = NotificationService(db)
    driver_id = current_user.id
    
    push_token = service.register_push_token(
        driver_id=driver_id,
        token=token_data.token,
        device_type=token_data.device_type,
        device_id=token_data.device_id
    )
    
    return {
        "message": "Push token registered successfully",
        "token_id": push_token.id
    }


# ==================== 채팅 API ====================

@router.get("/chat/rooms")
async def get_chat_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """채팅방 목록 조회"""
    service = ChatService(db)
    
    user_id = current_user.id
    user_type = "DRIVER"  # 또는 current_user.role에서 추출
    
    rooms = service.get_user_rooms(user_id, user_type)
    
    return {
        "rooms": [
            {
                "id": r.id,
                "room_name": r.room_name,
                "room_type": r.room_type,
                "participants": r.participants,
                "last_message": r.last_message,
                "last_message_at": r.last_message_at.isoformat() if r.last_message_at else None,
                "is_active": r.is_active,
                "created_at": r.created_at.isoformat()
            }
            for r in rooms
        ],
        "total": len(rooms)
    }


@router.post("/chat/rooms")
async def create_chat_room(
    room_data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """채팅방 생성"""
    service = ChatService(db)
    
    # 참여자 정보 생성
    participants = [
        {"id": pid, "type": "DRIVER" if pid == current_user.id else "DISPATCHER"}
        for pid in room_data.participant_ids
    ]
    
    room = service.create_room(
        room_name=room_data.room_name,
        room_type=room_data.room_type,
        participants=participants
    )
    
    return {
        "message": "Chat room created",
        "room_id": room.id
    }


@router.get("/chat/rooms/{room_id}/messages")
async def get_chat_messages(
    room_id: int,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """채팅방 메시지 조회"""
    service = ChatService(db)
    
    messages = service.get_room_messages(room_id, limit, offset)
    
    return {
        "messages": [
            {
                "id": m.id,
                "room_id": m.room_id,
                "sender_id": m.sender_id,
                "sender_type": m.sender_type,
                "message_type": m.message_type.value,
                "content": m.content,
                "file_url": m.file_url,
                "file_name": m.file_name,
                "latitude": m.latitude,
                "longitude": m.longitude,
                "is_read": m.is_read,
                "read_at": m.read_at.isoformat() if m.read_at else None,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ],
        "total": len(messages)
    }


@router.post("/chat/rooms/{room_id}/messages")
async def send_chat_message(
    room_id: int,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """메시지 전송"""
    service = ChatService(db)
    
    sender_id = current_user.id
    sender_type = "DRIVER"  # 또는 current_user.role에서 추출
    
    message = service.send_message(
        room_id=room_id,
        sender_id=sender_id,
        sender_type=sender_type,
        message_type=message_data.message_type,
        content=message_data.content,
        latitude=message_data.latitude,
        longitude=message_data.longitude
    )
    
    return {
        "message": "Message sent",
        "message_id": message.id
    }


@router.post("/chat/rooms/{room_id}/read")
async def mark_messages_read(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """메시지 읽음 표시"""
    service = ChatService(db)
    
    user_id = current_user.id
    user_type = "DRIVER"
    
    updated = service.mark_messages_as_read(room_id, user_id, user_type)
    
    return {
        "message": "Messages marked as read",
        "updated_count": updated
    }


@router.get("/chat/unread-count")
async def get_unread_chat_count(
    room_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """읽지 않은 메시지 개수"""
    service = ChatService(db)
    
    user_id = current_user.id
    user_type = "DRIVER"
    
    count = service.get_unread_count(user_id, user_type, room_id)
    
    return {"unread_count": count}


# ==================== 성과 API ====================

@router.get("/performance/statistics")
async def get_performance_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    드라이버 성과 통계
    
    오늘/이번 주/이번 달 성과 조회
    """
    service = PerformanceService(db)
    driver_id = current_user.id
    
    statistics = service.get_performance_statistics(driver_id)
    
    return statistics


@router.get("/performance/today")
async def get_today_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """오늘의 성과"""
    service = PerformanceService(db)
    driver_id = current_user.id
    
    performance = service.get_today_performance(driver_id)
    
    if not performance:
        return {"message": "No performance data for today"}
    
    return service._performance_to_dict(performance)


@router.get("/performance/weekly")
async def get_weekly_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """이번 주 성과"""
    service = PerformanceService(db)
    driver_id = current_user.id
    
    performance = service.get_weekly_performance(driver_id)
    
    if not performance:
        return {"message": "No performance data for this week"}
    
    return service._performance_to_dict(performance)


@router.get("/performance/monthly")
async def get_monthly_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """이번 달 성과"""
    service = PerformanceService(db)
    driver_id = current_user.id
    
    performance = service.get_monthly_performance(driver_id)
    
    if not performance:
        return {"message": "No performance data for this month"}
    
    return service._performance_to_dict(performance)


@router.get("/performance/history")
async def get_performance_history(
    period_type: str = "DAILY",
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """성과 이력 조회"""
    service = PerformanceService(db)
    driver_id = current_user.id
    
    performances = service.get_driver_performance(driver_id, period_type, limit)
    
    return {
        "performances": [
            service._performance_to_dict(p)
            for p in performances
        ],
        "total": len(performances)
    }


@router.get("/performance/leaderboard")
async def get_leaderboard(
    period_type: str = "MONTHLY",
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """드라이버 순위표"""
    service = PerformanceService(db)
    
    leaderboard = service.get_leaderboard(period_type, limit)
    
    return {
        "leaderboard": leaderboard,
        "total": len(leaderboard)
    }


# ==================== 배송 증빙 API ====================

@router.post("/delivery-proofs")
async def create_delivery_proof(
    proof_data: DeliveryProofCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    배송 증빙 생성 (간단 버전)
    
    실제로는 파일 업로드를 처리해야 함
    """
    from app.models.driver_app import DeliveryProof
    
    driver_id = current_user.id
    
    proof = DeliveryProof(
        dispatch_id=proof_data.dispatch_id,
        driver_id=driver_id,
        order_id=proof_data.order_id,
        proof_type=proof_data.proof_type,
        note=proof_data.note,
        recipient_name=proof_data.recipient_name,
        recipient_phone=proof_data.recipient_phone,
        latitude=proof_data.latitude,
        longitude=proof_data.longitude
    )
    
    db.add(proof)
    db.commit()
    db.refresh(proof)
    
    return {
        "message": "Delivery proof created",
        "proof_id": proof.id
    }


@router.get("/delivery-proofs")
async def get_delivery_proofs(
    dispatch_id: Optional[int] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """배송 증빙 목록 조회"""
    from app.models.driver_app import DeliveryProof
    from sqlalchemy import and_
    
    driver_id = current_user.id
    
    query = db.query(DeliveryProof).filter(
        DeliveryProof.driver_id == driver_id
    )
    
    if dispatch_id:
        query = query.filter(DeliveryProof.dispatch_id == dispatch_id)
    
    proofs = query.order_by(DeliveryProof.created_at.desc()).limit(limit).all()
    
    return {
        "proofs": [
            {
                "id": p.id,
                "dispatch_id": p.dispatch_id,
                "order_id": p.order_id,
                "proof_type": p.proof_type.value,
                "file_url": p.file_url,
                "file_name": p.file_name,
                "note": p.note,
                "recipient_name": p.recipient_name,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "created_at": p.created_at.isoformat()
            }
            for p in proofs
        ],
        "total": len(proofs)
    }
