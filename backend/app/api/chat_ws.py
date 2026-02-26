"""
실시간 채팅 WebSocket 엔드포인트
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Set, Optional, List
import json
import logging
from datetime import datetime

from app.core.database import get_db
from app.models import ChatRoom, ChatMessage, ChatParticipant, User

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatConnectionManager:
    """채팅 WebSocket 연결 관리자"""
    
    def __init__(self):
        # room_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # WebSocket -> user_id
        self.user_connections: Dict[WebSocket, int] = {}
    
    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        """WebSocket 연결"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        
        self.active_connections[room_id].add(websocket)
        self.user_connections[websocket] = user_id
        
        logger.info(f"✅ User {user_id} connected to room {room_id}")
    
    def disconnect(self, websocket: WebSocket, room_id: int):
        """WebSocket 연결 해제"""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        user_id = self.user_connections.pop(websocket, None)
        logger.info(f"❌ User {user_id} disconnected from room {room_id}")
    
    async def broadcast_to_room(self, room_id: int, message: dict, exclude: Optional[WebSocket] = None):
        """채팅방의 모든 사용자에게 메시지 브로드캐스트"""
        if room_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections[room_id]:
            if connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(connection)
        
        # 연결이 끊긴 WebSocket 제거
        for conn in disconnected:
            self.disconnect(conn, room_id)
    
    def get_room_users(self, room_id: int) -> Set[int]:
        """채팅방의 현재 접속 사용자 ID 목록"""
        if room_id not in self.active_connections:
            return set()
        
        return {
            self.user_connections[ws]
            for ws in self.active_connections[room_id]
            if ws in self.user_connections
        }


# 전역 연결 관리자
chat_manager = ChatConnectionManager()


@router.websocket("/chat/{room_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    채팅 WebSocket 엔드포인트
    
    - room_id: 채팅방 ID
    - token: JWT 인증 토큰 (쿼리 파라미터)
    """
    try:
        # 토큰 검증 (간단한 방법)
        from app.api.auth import decode_token
        user_id = decode_token(token)
        
        if not user_id:
            await websocket.close(code=4001, reason="Unauthorized")
            return
        
        # 채팅방 존재 확인
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        if not room or not room.is_active:
            await websocket.close(code=4004, reason="Room not found")
            return
        
        # 참가자 확인
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == user_id,
            ChatParticipant.is_active == True
        ).first()
        
        if not participant:
            # 자동 참가 (옵션: 제거하고 수동 참가만 허용)
            participant = ChatParticipant(
                room_id=room_id,
                user_id=user_id,
                role='member'
            )
            db.add(participant)
            db.commit()
        
        # WebSocket 연결
        await chat_manager.connect(websocket, room_id, user_id)
        
        # 연결 알림 브로드캐스트
        await chat_manager.broadcast_to_room(
            room_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "online_users": list(chat_manager.get_room_users(room_id))
            }
        )
        
        # 메시지 수신 루프
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get("type", "message")
            
            if message_type == "message":
                # 메시지 저장
                message_content = data.get("message", "")
                reply_to_id = data.get("reply_to_id")
                file_url = data.get("file_url")
                file_name = data.get("file_name")
                file_size = data.get("file_size")
                
                msg = ChatMessage(
                    room_id=room_id,
                    user_id=user_id,
                    message=message_content,
                    message_type=data.get("message_type", "text"),
                    file_url=file_url,
                    file_name=file_name,
                    file_size=file_size,
                    reply_to_id=reply_to_id
                )
                
                db.add(msg)
                db.commit()
                db.refresh(msg)
                
                # 사용자 정보 조회
                user = db.query(User).filter(User.id == user_id).first()
                
                # 브로드캐스트
                await chat_manager.broadcast_to_room(
                    room_id,
                    {
                        "type": "message",
                        "message_id": msg.id,
                        "user_id": user_id,
                        "user_name": user.name if user else "Unknown",
                        "message": message_content,
                        "message_type": msg.message_type,
                        "file_url": file_url,
                        "file_name": file_name,
                        "file_size": file_size,
                        "reply_to_id": reply_to_id,
                        "created_at": msg.created_at.isoformat(),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            elif message_type == "typing":
                # 타이핑 상태 브로드캐스트 (저장하지 않음)
                await chat_manager.broadcast_to_room(
                    room_id,
                    {
                        "type": "typing",
                        "user_id": user_id,
                        "is_typing": data.get("is_typing", False)
                    },
                    exclude=websocket
                )
            
            elif message_type == "read":
                # 읽음 상태 업데이트
                message_id = data.get("message_id")
                if message_id:
                    participant.last_read_message_id = message_id
                    participant.last_read_at = datetime.utcnow()
                    db.commit()
    
    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, room_id)
        
        # 연결 해제 알림 브로드캐스트
        await chat_manager.broadcast_to_room(
            room_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "online_users": list(chat_manager.get_room_users(room_id))
            }
        )
        
        logger.info(f"User {user_id} disconnected from room {room_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        chat_manager.disconnect(websocket, room_id)
        await websocket.close(code=1011, reason="Internal error")
