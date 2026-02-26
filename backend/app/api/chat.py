"""
채팅 REST API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import User, ChatRoom, ChatParticipant, ChatMessage

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== Schemas =====

class ChatRoomCreate(BaseModel):
    """채팅방 생성 요청"""
    name: str
    room_type: str = "group"  # direct, group, support
    description: Optional[str] = None
    participant_ids: List[int] = []


class ChatRoomResponse(BaseModel):
    """채팅방 응답"""
    id: int
    name: str
    room_type: str
    description: Optional[str]
    is_active: bool
    created_at: str
    unread_count: Optional[int] = 0
    last_message: Optional[dict] = None
    
    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    """채팅 메시지 응답"""
    id: int
    room_id: int
    user_id: int
    user_name: str
    message: str
    message_type: str
    file_url: Optional[str]
    file_name: Optional[str]
    reply_to_id: Optional[int]
    is_edited: bool
    created_at: str
    
    class Config:
        from_attributes = True


# ===== API Endpoints =====

@router.post("/rooms", response_model=ChatRoomResponse)
async def create_chat_room(
    room_data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채팅방 생성
    
    - 채팅방을 생성하고 참가자를 추가합니다.
    """
    try:
        # 채팅방 생성
        room = ChatRoom(
            name=room_data.name,
            room_type=room_data.room_type,
            description=room_data.description,
            created_by=current_user.id
        )
        
        db.add(room)
        db.flush()  # ID 생성
        
        # 생성자 참가
        creator_participant = ChatParticipant(
            room_id=room.id,
            user_id=current_user.id,
            role='admin'
        )
        db.add(creator_participant)
        
        # 다른 참가자 추가
        for user_id in room_data.participant_ids:
            if user_id != current_user.id:
                participant = ChatParticipant(
                    room_id=room.id,
                    user_id=user_id,
                    role='member'
                )
                db.add(participant)
        
        db.commit()
        db.refresh(room)
        
        return ChatRoomResponse(
            id=room.id,
            name=room.name,
            room_type=room.room_type,
            description=room.description,
            is_active=room.is_active,
            created_at=room.created_at.isoformat()
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"채팅방 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_chat_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 채팅방 목록 조회
    
    - 현재 사용자가 참가한 채팅방 목록을 반환합니다.
    """
    try:
        # 참가 중인 채팅방 조회
        participants = db.query(ChatParticipant).filter(
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_active == True
        ).all()
        
        rooms = []
        
        for participant in participants:
            room = participant.room
            if not room or not room.is_active:
                continue
            
            # 마지막 메시지 조회
            last_message = db.query(ChatMessage).filter(
                ChatMessage.room_id == room.id,
                ChatMessage.is_deleted == False
            ).order_by(desc(ChatMessage.created_at)).first()
            
            # 읽지 않은 메시지 수
            unread_count = 0
            if participant.last_read_message_id:
                unread_count = db.query(ChatMessage).filter(
                    ChatMessage.room_id == room.id,
                    ChatMessage.id > participant.last_read_message_id,
                    ChatMessage.user_id != current_user.id,
                    ChatMessage.is_deleted == False
                ).count()
            else:
                unread_count = db.query(ChatMessage).filter(
                    ChatMessage.room_id == room.id,
                    ChatMessage.user_id != current_user.id,
                    ChatMessage.is_deleted == False
                ).count()
            
            rooms.append(ChatRoomResponse(
                id=room.id,
                name=room.name,
                room_type=room.room_type,
                description=room.description,
                is_active=room.is_active,
                created_at=room.created_at.isoformat(),
                unread_count=unread_count,
                last_message={
                    "message": last_message.message,
                    "created_at": last_message.created_at.isoformat()
                } if last_message else None
            ))
        
        # 최근 메시지 순으로 정렬
        rooms.sort(key=lambda x: x.last_message['created_at'] if x.last_message else x.created_at, reverse=True)
        
        return rooms
    
    except Exception as e:
        logger.error(f"채팅방 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    room_id: int,
    limit: int = Query(50, le=100),
    before_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채팅 메시지 조회 (페이지네이션)
    
    - before_id: 이 메시지 ID 이전의 메시지들을 조회 (페이징)
    - limit: 조회할 메시지 수 (기본 50, 최대 100)
    """
    try:
        # 참가 확인
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_active == True
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="이 채팅방에 접근할 수 없습니다")
        
        # 메시지 조회
        query = db.query(ChatMessage).filter(
            ChatMessage.room_id == room_id,
            ChatMessage.is_deleted == False
        )
        
        if before_id:
            query = query.filter(ChatMessage.id < before_id)
        
        messages = query.order_by(desc(ChatMessage.created_at)).limit(limit).all()
        
        # 역순으로 정렬 (시간 순)
        messages.reverse()
        
        # 응답 생성
        result = []
        for msg in messages:
            user = db.query(User).filter(User.id == msg.user_id).first()
            
            result.append(ChatMessageResponse(
                id=msg.id,
                room_id=msg.room_id,
                user_id=msg.user_id,
                user_name=user.name if user else "Unknown",
                message=msg.message,
                message_type=msg.message_type,
                file_url=msg.file_url,
                file_name=msg.file_name,
                reply_to_id=msg.reply_to_id,
                is_edited=msg.is_edited,
                created_at=msg.created_at.isoformat()
            ))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메시지 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rooms/{room_id}")
async def delete_chat_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채팅방 삭제 (비활성화)
    
    - 채팅방을 삭제(비활성화)합니다. (관리자 또는 생성자만 가능)
    """
    try:
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        
        if not room:
            raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")
        
        # 권한 확인
        if room.created_by != current_user.id and current_user.role not in ['admin', 'manager']:
            raise HTTPException(status_code=403, detail="채팅방을 삭제할 권한이 없습니다")
        
        room.is_active = False
        db.commit()
        
        return {"success": True, "message": "채팅방이 삭제되었습니다"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"채팅방 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rooms/{room_id}/leave")
async def leave_chat_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채팅방 나가기
    
    - 채팅방에서 퇴장합니다.
    """
    try:
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=404, detail="참가 정보를 찾을 수 없습니다")
        
        participant.is_active = False
        participant.left_at = datetime.utcnow()
        db.commit()
        
        return {"success": True, "message": "채팅방에서 나갔습니다"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"채팅방 나가기 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
