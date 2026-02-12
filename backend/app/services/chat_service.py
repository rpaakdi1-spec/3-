"""
Phase 16: Chat Service
실시간 채팅 서비스
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.driver_app import (
    ChatRoom,
    ChatMessage,
    ChatMessageType
)


class ChatService:
    """채팅 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_room(
        self,
        room_name: str,
        room_type: str,
        participants: List[Dict[str, Any]]
    ) -> ChatRoom:
        """
        채팅방 생성
        
        Args:
            room_name: 채팅방 이름
            room_type: 채팅방 타입 (1:1/GROUP)
            participants: 참여자 목록
        
        Returns:
            생성된 채팅방
        """
        room = ChatRoom(
            room_name=room_name,
            room_type=room_type,
            participants=participants,
            is_active=True
        )
        
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        
        return room
    
    def get_or_create_direct_room(
        self,
        driver_id: int,
        dispatcher_id: int
    ) -> ChatRoom:
        """
        1:1 채팅방 조회 또는 생성
        
        Args:
            driver_id: 드라이버 ID
            dispatcher_id: 배차 담당자 ID
        
        Returns:
            채팅방
        """
        # 기존 1:1 채팅방 찾기
        rooms = self.db.query(ChatRoom).filter(
            and_(
                ChatRoom.room_type == "1:1",
                ChatRoom.is_active == True
            )
        ).all()
        
        for room in rooms:
            participants = room.participants or []
            participant_ids = [p.get("id") for p in participants]
            
            if driver_id in participant_ids and dispatcher_id in participant_ids:
                return room
        
        # 없으면 생성
        participants = [
            {"id": driver_id, "type": "DRIVER"},
            {"id": dispatcher_id, "type": "DISPATCHER"}
        ]
        
        room_name = f"Driver {driver_id} - Dispatcher {dispatcher_id}"
        
        return self.create_room(
            room_name=room_name,
            room_type="1:1",
            participants=participants
        )
    
    def send_message(
        self,
        room_id: int,
        sender_id: int,
        sender_type: str,
        message_type: ChatMessageType,
        content: Optional[str] = None,
        file_url: Optional[str] = None,
        file_name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """
        메시지 전송
        
        Args:
            room_id: 채팅방 ID
            sender_id: 발신자 ID
            sender_type: 발신자 타입
            message_type: 메시지 타입
            content: 메시지 내용
            file_url: 파일 URL
            file_name: 파일명
            latitude: 위도 (위치 공유)
            longitude: 경도 (위치 공유)
            metadata: 추가 메타데이터
        
        Returns:
            전송된 메시지
        """
        message = ChatMessage(
            room_id=room_id,
            sender_id=sender_id,
            sender_type=sender_type,
            message_type=message_type,
            content=content,
            file_url=file_url,
            file_name=file_name,
            latitude=latitude,
            longitude=longitude,
            message_metadata=metadata or {},
            is_read=False
        )
        
        self.db.add(message)
        
        # 채팅방 업데이트
        room = self.db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        if room:
            room.last_message = content or f"[{message_type.value}]"
            room.last_message_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_room_messages(
        self,
        room_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatMessage]:
        """
        채팅방 메시지 조회
        
        Args:
            room_id: 채팅방 ID
            limit: 조회 개수
            offset: 오프셋
        
        Returns:
            메시지 목록
        """
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.room_id == room_id
        ).order_by(
            desc(ChatMessage.created_at)
        ).limit(limit).offset(offset).all()
        
        return messages
    
    def get_user_rooms(
        self,
        user_id: int,
        user_type: str
    ) -> List[ChatRoom]:
        """
        사용자의 채팅방 목록 조회
        
        Args:
            user_id: 사용자 ID
            user_type: 사용자 타입
        
        Returns:
            채팅방 목록
        """
        rooms = self.db.query(ChatRoom).filter(
            ChatRoom.is_active == True
        ).order_by(
            desc(ChatRoom.last_message_at)
        ).all()
        
        # 참여자 필터링
        user_rooms = []
        for room in rooms:
            participants = room.participants or []
            for p in participants:
                if p.get("id") == user_id and p.get("type") == user_type:
                    user_rooms.append(room)
                    break
        
        return user_rooms
    
    def mark_messages_as_read(
        self,
        room_id: int,
        user_id: int,
        user_type: str
    ) -> int:
        """
        메시지 읽음 표시
        
        Args:
            room_id: 채팅방 ID
            user_id: 사용자 ID
            user_type: 사용자 타입
        
        Returns:
            업데이트된 메시지 개수
        """
        # 본인이 보낸 메시지가 아닌 것만 읽음 처리
        updated = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.room_id == room_id,
                ChatMessage.is_read == False,
                or_(
                    ChatMessage.sender_id != user_id,
                    ChatMessage.sender_type != user_type
                )
            )
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        self.db.commit()
        
        return updated
    
    def get_unread_count(
        self,
        user_id: int,
        user_type: str,
        room_id: Optional[int] = None
    ) -> int:
        """
        읽지 않은 메시지 개수
        
        Args:
            user_id: 사용자 ID
            user_type: 사용자 타입
            room_id: 채팅방 ID (선택)
        
        Returns:
            읽지 않은 메시지 개수
        """
        query = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.is_read == False,
                or_(
                    ChatMessage.sender_id != user_id,
                    ChatMessage.sender_type != user_type
                )
            )
        )
        
        if room_id:
            query = query.filter(ChatMessage.room_id == room_id)
        else:
            # 사용자가 참여한 모든 채팅방의 메시지
            user_rooms = self.get_user_rooms(user_id, user_type)
            room_ids = [room.id for room in user_rooms]
            query = query.filter(ChatMessage.room_id.in_(room_ids))
        
        count = query.count()
        
        return count
    
    def delete_message(
        self,
        message_id: int,
        user_id: int,
        user_type: str
    ) -> bool:
        """
        메시지 삭제 (본인만 가능)
        
        Args:
            message_id: 메시지 ID
            user_id: 사용자 ID
            user_type: 사용자 타입
        
        Returns:
            삭제 성공 여부
        """
        message = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.id == message_id,
                ChatMessage.sender_id == user_id,
                ChatMessage.sender_type == user_type
            )
        ).first()
        
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        
        return False
