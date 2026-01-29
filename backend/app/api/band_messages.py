"""
밴드 메시지 API 엔드포인트
화물 수배 메시지를 생성하고 관리합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta
import random

from ..core.database import get_db
from ..models.band_message import BandMessage, BandChatRoom, BandMessageSchedule
from ..models.dispatch import Dispatch
from ..schemas.band_message import (
    BandMessageCreate,
    BandMessageUpdate,
    BandMessageResponse,
    BandMessageListResponse,
    BandChatRoomCreate,
    BandChatRoomUpdate,
    BandChatRoomResponse,
    BandChatRoomListResponse,
    BandMessageScheduleCreate,
    BandMessageScheduleUpdate,
    BandMessageScheduleResponse,
    BandMessageScheduleListResponse,
    MessageGenerateRequest,
    MessageGenerateResponse,
)
from ..services.band_message_service import BandMessageGenerator

router = APIRouter(tags=["Band Messages"])


# ==================== 메시지 생성 ====================

@router.post("/generate", response_model=MessageGenerateResponse)
def generate_message(
    request: MessageGenerateRequest,
    db: Session = Depends(get_db)
):
    """배차 정보를 기반으로 밴드 메시지 생성"""
    try:
        # 배차 확인
        dispatch = db.query(Dispatch).filter(Dispatch.id == request.dispatch_id).first()
        if not dispatch:
            raise HTTPException(status_code=404, detail="배차 정보를 찾을 수 없습니다")
        
        # 메시지 생성
        result = BandMessageGenerator.generate_message(db, request.dispatch_id)
        
        # 데이터베이스에 저장
        db_message = BandMessage(
            dispatch_id=request.dispatch_id,
            message_content=result["message"],
            variation_seed=result["variation_seed"],
            generated_at=datetime.now()
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        # 다음 스케줄 확인
        schedule = db.query(BandMessageSchedule).filter(
            BandMessageSchedule.dispatch_id == request.dispatch_id,
            BandMessageSchedule.is_active == True
        ).first()
        
        next_schedule = None
        if schedule:
            next_interval = BandMessageGenerator.generate_next_interval(
                schedule.min_interval_seconds,
                schedule.max_interval_seconds
            )
            next_schedule = datetime.now() + timedelta(seconds=next_interval)
        
        return MessageGenerateResponse(
            message=result["message"],
            dispatch_id=request.dispatch_id,
            generated_at=datetime.now(),
            next_schedule=next_schedule
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메시지 생성 실패: {str(e)}")


@router.get("/messages/", response_model=BandMessageListResponse)
def get_messages(
    dispatch_id: Optional[int] = None,
    is_sent: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """메시지 목록 조회"""
    query = db.query(BandMessage)
    
    if dispatch_id:
        query = query.filter(BandMessage.dispatch_id == dispatch_id)
    
    if is_sent is not None:
        query = query.filter(BandMessage.is_sent == is_sent)
    
    total = query.count()
    items = query.order_by(desc(BandMessage.generated_at)).offset(skip).limit(limit).all()
    
    return BandMessageListResponse(total=total, items=items)


@router.get("/messages/{message_id}", response_model=BandMessageResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """메시지 상세 조회"""
    message = db.query(BandMessage).filter(BandMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다")
    
    return message


@router.put("/messages/{message_id}/mark-sent", response_model=BandMessageResponse)
def mark_message_sent(message_id: int, db: Session = Depends(get_db)):
    """메시지를 전송 완료로 표시"""
    message = db.query(BandMessage).filter(BandMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다")
    
    message.is_sent = True
    message.sent_at = datetime.now()
    db.commit()
    db.refresh(message)
    
    return message


# ==================== 채팅방 관리 ====================

@router.get("/chat-rooms/", response_model=BandChatRoomListResponse)
def get_chat_rooms(
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """채팅방 목록 조회"""
    query = db.query(BandChatRoom)
    
    if is_active is not None:
        query = query.filter(BandChatRoom.is_active == is_active)
    
    total = query.count()
    items = query.order_by(BandChatRoom.name).offset(skip).limit(limit).all()
    
    return BandChatRoomListResponse(total=total, items=items)


@router.post("/chat-rooms/", response_model=BandChatRoomResponse)
def create_chat_room(room: BandChatRoomCreate, db: Session = Depends(get_db)):
    """채팅방 추가"""
    db_room = BandChatRoom(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    
    return db_room


@router.put("/chat-rooms/{room_id}", response_model=BandChatRoomResponse)
def update_chat_room(
    room_id: int,
    room_update: BandChatRoomUpdate,
    db: Session = Depends(get_db)
):
    """채팅방 수정"""
    db_room = db.query(BandChatRoom).filter(BandChatRoom.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")
    
    update_data = room_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_room, field, value)
    
    db.commit()
    db.refresh(db_room)
    
    return db_room


@router.delete("/chat-rooms/{room_id}")
def delete_chat_room(room_id: int, db: Session = Depends(get_db)):
    """채팅방 삭제"""
    db_room = db.query(BandChatRoom).filter(BandChatRoom.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")
    
    db.delete(db_room)
    db.commit()
    
    return {"message": "채팅방이 삭제되었습니다"}


# ==================== 스케줄 관리 ====================

@router.get("/schedules/", response_model=BandMessageScheduleListResponse)
def get_schedules(
    dispatch_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """스케줄 목록 조회"""
    query = db.query(BandMessageSchedule)
    
    if dispatch_id:
        query = query.filter(BandMessageSchedule.dispatch_id == dispatch_id)
    
    if is_active is not None:
        query = query.filter(BandMessageSchedule.is_active == is_active)
    
    total = query.count()
    items = query.order_by(desc(BandMessageSchedule.created_at)).offset(skip).limit(limit).all()
    
    return BandMessageScheduleListResponse(total=total, items=items)


@router.post("/schedules/", response_model=BandMessageScheduleResponse)
def create_schedule(schedule: BandMessageScheduleCreate, db: Session = Depends(get_db)):
    """스케줄 생성"""
    # 배차 확인
    dispatch = db.query(Dispatch).filter(Dispatch.id == schedule.dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=404, detail="배차 정보를 찾을 수 없습니다")
    
    # 유효성 검증
    if schedule.start_time >= schedule.end_time:
        raise HTTPException(status_code=400, detail="종료 시간은 시작 시간보다 이후여야 합니다")
    
    if schedule.min_interval_seconds >= schedule.max_interval_seconds:
        raise HTTPException(status_code=400, detail="최대 간격은 최소 간격보다 커야 합니다")
    
    db_schedule = BandMessageSchedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@router.put("/schedules/{schedule_id}", response_model=BandMessageScheduleResponse)
def update_schedule(
    schedule_id: int,
    schedule_update: BandMessageScheduleUpdate,
    db: Session = Depends(get_db)
):
    """스케줄 수정"""
    db_schedule = db.query(BandMessageSchedule).filter(BandMessageSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="스케줄을 찾을 수 없습니다")
    
    update_data = schedule_update.model_dump(exclude_unset=True)
    
    # 유효성 검증
    start_time = update_data.get("start_time", db_schedule.start_time)
    end_time = update_data.get("end_time", db_schedule.end_time)
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="종료 시간은 시작 시간보다 이후여야 합니다")
    
    min_interval = update_data.get("min_interval_seconds", db_schedule.min_interval_seconds)
    max_interval = update_data.get("max_interval_seconds", db_schedule.max_interval_seconds)
    if min_interval >= max_interval:
        raise HTTPException(status_code=400, detail="최대 간격은 최소 간격보다 커야 합니다")
    
    for field, value in update_data.items():
        setattr(db_schedule, field, value)
    
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """스케줄 삭제"""
    db_schedule = db.query(BandMessageSchedule).filter(BandMessageSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="스케줄을 찾을 수 없습니다")
    
    db.delete(db_schedule)
    db.commit()
    
    return {"message": "스케줄이 삭제되었습니다"}


@router.post("/schedules/{schedule_id}/toggle")
def toggle_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """스케줄 활성화/비활성화 토글"""
    db_schedule = db.query(BandMessageSchedule).filter(BandMessageSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="스케줄을 찾을 수 없습니다")
    
    db_schedule.is_active = not db_schedule.is_active
    db.commit()
    db.refresh(db_schedule)
    
    return {
        "schedule_id": schedule_id,
        "is_active": db_schedule.is_active,
        "message": f"스케줄이 {'활성화' if db_schedule.is_active else '비활성화'}되었습니다"
    }
