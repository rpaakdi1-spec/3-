"""
서버 컨테이너 내부에서 실행: 방 생성 500 에러 원인 파악
실행: docker compose exec backend python debug_room_create.py
"""
import sys
import traceback

print("=" * 60)
print("위치공유 방 생성 디버그 스크립트")
print("=" * 60)

# 1. 모델 임포트
print("\n[1] 모델 임포트...")
try:
    from app.models.location_room import LocationRoom, RoomStatus, RoomDocumentType, RoomDocumentStage
    print(f"   ✅ 임포트 성공")
    print(f"   RoomStatus values: {[e.value for e in RoomStatus]}")
except Exception as e:
    print(f"   ❌ 임포트 실패: {e}")
    traceback.print_exc()
    sys.exit(1)

# 2. create_room 객체 생성
print("\n[2] LocationRoom 객체 생성...")
try:
    room = LocationRoom.create_room(title="디버그 테스트", created_by=1, hours_valid=24)
    print(f"   ✅ 객체 생성 성공")
    print(f"   room_code: {room.room_code}")
    print(f"   status: {room.status!r}")
    print(f"   status.value: {room.status.value!r}")
    print(f"   driver_token: {room.driver_token[:20]}...")
    print(f"   expires_at: {room.expires_at}")
except Exception as e:
    print(f"   ❌ 객체 생성 실패: {e}")
    traceback.print_exc()
    sys.exit(1)

# 3. DB 세션으로 실제 INSERT
print("\n[3] DB INSERT 테스트...")
try:
    from app.core.database import get_db
    db = next(get_db())
    
    print(f"   DB URL: {db.bind.url if hasattr(db, 'bind') else 'unknown'}")
    
    db.add(room)
    db.flush()  # commit 전에 SQL 실행
    print(f"   ✅ flush 성공, id={room.id}")
    
    db.commit()
    db.refresh(room)
    print(f"   ✅ commit 성공!")
    print(f"   id={room.id}")
    print(f"   status after commit: {room.status!r}")
    
    # 테스트 데이터 삭제
    db.delete(room)
    db.commit()
    print(f"   ✅ 테스트 데이터 삭제 완료")
    
except Exception as e:
    print(f"   ❌ DB INSERT 실패!")
    print(f"   에러 타입: {type(e).__name__}")
    print(f"   에러 메시지: {str(e)}")
    print("\n   전체 traceback:")
    traceback.print_exc()
    try:
        db.rollback()
    except:
        pass
    sys.exit(1)

# 4. Enum 컬럼 타입 확인
print("\n[4] Enum 컬럼 타입 확인...")
try:
    col_status = LocationRoom.__table__.c['status']
    print(f"   status column type: {col_status.type}")
    print(f"   status native_enum: {getattr(col_status.type, 'native_enum', 'N/A')}")
    
    from app.models.location_room import RoomDocument
    col_dtype = RoomDocument.__table__.c['document_type']
    col_stage = RoomDocument.__table__.c['stage']
    print(f"   document_type native_enum: {getattr(col_dtype.type, 'native_enum', 'N/A')}")
    print(f"   stage native_enum: {getattr(col_stage.type, 'native_enum', 'N/A')}")
except Exception as e:
    print(f"   ❌ 컬럼 타입 확인 실패: {e}")

print("\n" + "=" * 60)
print("✅ 모든 테스트 통과!")
print("=" * 60)
