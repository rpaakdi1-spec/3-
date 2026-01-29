#!/usr/bin/env python3
"""
SQLite에서 PostgreSQL로 데이터 마이그레이션 스크립트

Usage:
    python migrate_data.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    SQLITE_DB_PATH: Path to SQLite database file (default: ./dispatch.db)
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base

# Import all models
from app.models.client import Client
from app.models.vehicle import Vehicle
from app.models.order import Order
from app.models.dispatch import Dispatch, DispatchRoute
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle_location import VehicleLocation
from app.models.uvis_gps import UvisAccessKey, UvisApiLog, VehicleGPSLog, VehicleTemperatureLog, TemperatureAlert
from app.models.purchase_order import PurchaseOrder
from app.models.notice import Notice
from app.models.band_message import BandChatRoom, BandMessage, BandMessageSchedule

# SQLite database path
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', './dispatch.db')

def create_sqlite_engine(db_path: str):
    """Create SQLite engine"""
    if not os.path.exists(db_path):
        print(f"❌ SQLite database not found: {db_path}")
        sys.exit(1)
    
    return create_engine(f"sqlite:///{db_path}", echo=False)

def get_table_names(engine):
    """Get all table names from database"""
    inspector = inspect(engine)
    return inspector.get_table_names()

def migrate_table(model, sqlite_session, pg_session, batch_size=100):
    """
    Migrate data from SQLite to PostgreSQL for a specific model.
    
    Args:
        model: SQLAlchemy model class
        sqlite_session: SQLite session
        pg_session: PostgreSQL session
        batch_size: Number of records to process at once
    """
    table_name = model.__tablename__
    
    try:
        # Get all records from SQLite
        records = sqlite_session.query(model).all()
        total = len(records)
        
        if total == 0:
            print(f"⏭️  {table_name}: No data to migrate")
            return True
        
        print(f"📦 Migrating {total} {table_name} records...")
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]
            
            # Insert into PostgreSQL
            for record in batch:
                # Convert record to dict
                record_dict = {}
                for column in record.__table__.columns:
                    value = getattr(record, column.name)
                    
                    # Skip auto-increment primary keys
                    if column.primary_key and column.autoincrement:
                        continue
                    
                    record_dict[column.name] = value
                
                # Create new record
                new_record = model(**record_dict)
                pg_session.add(new_record)
            
            # Commit batch
            pg_session.commit()
            print(f"  ✅ Migrated {min(i + batch_size, total)}/{total}")
        
        print(f"✅ {table_name} migration completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating {table_name}: {e}")
        pg_session.rollback()
        return False

def reset_sequences(pg_engine):
    """Reset PostgreSQL sequences after data migration"""
    print("\n🔄 Resetting sequences...")
    
    with pg_engine.connect() as conn:
        # Get all sequences
        result = conn.execute("""
            SELECT sequence_name FROM information_schema.sequences
            WHERE sequence_schema = 'public'
        """)
        
        sequences = [row[0] for row in result]
        
        for seq in sequences:
            # Extract table and column name from sequence name
            # Format: tablename_columnname_seq
            parts = seq.split('_')
            if len(parts) >= 3 and parts[-1] == 'seq':
                table_name = '_'.join(parts[:-2])
                column_name = parts[-2]
                
                try:
                    # Reset sequence to max ID + 1
                    conn.execute(f"""
                        SELECT setval('{seq}', 
                            COALESCE((SELECT MAX({column_name}) FROM {table_name}), 1), 
                            true
                        )
                    """)
                    print(f"  ✅ Reset {seq}")
                except Exception as e:
                    print(f"  ⚠️  Could not reset {seq}: {e}")
        
        conn.commit()
    
    print("✅ Sequences reset completed!")

def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 SQLite to PostgreSQL Data Migration")
    print("=" * 60)
    
    # Check PostgreSQL connection
    print(f"\n📡 PostgreSQL: {settings.DATABASE_URL[:50]}...")
    print(f"📁 SQLite: {SQLITE_DB_PATH}")
    
    # Create engines
    sqlite_engine = create_sqlite_engine(SQLITE_DB_PATH)
    pg_engine = create_engine(settings.DATABASE_URL, echo=False)
    
    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=pg_engine)
    
    sqlite_session = SQLiteSession()
    pg_session = PostgresSession()
    
    # Check SQLite tables
    sqlite_tables = get_table_names(sqlite_engine)
    print(f"\n📊 SQLite tables found: {len(sqlite_tables)}")
    
    # Check PostgreSQL tables
    pg_tables = get_table_names(pg_engine)
    print(f"📊 PostgreSQL tables found: {len(pg_tables)}")
    
    if len(pg_tables) == 0:
        print("\n❌ PostgreSQL tables not found!")
        print("   Please run: alembic upgrade head")
        sys.exit(1)
    
    # Migration order (respecting foreign key constraints)
    # Parent tables first, child tables later
    migration_order = [
        # Independent tables (no foreign keys)
        (User, "Users"),
        (Client, "Clients"),
        (Driver, "Drivers"),
        (Vehicle, "Vehicles"),
        (UvisAccessKey, "UVIS Access Keys"),
        (BandChatRoom, "Band Chat Rooms"),
        (Notice, "Notices"),
        (PurchaseOrder, "Purchase Orders"),
        
        # Tables with foreign keys
        (Order, "Orders"),
        (Dispatch, "Dispatches"),
        (DispatchRoute, "Dispatch Routes"),
        (VehicleLocation, "Vehicle Locations"),
        (VehicleGPSLog, "Vehicle GPS Logs"),
        (VehicleTemperatureLog, "Vehicle Temperature Logs"),
        (TemperatureAlert, "Temperature Alerts"),
        (UvisApiLog, "UVIS API Logs"),
        (BandMessage, "Band Messages"),
        (BandMessageSchedule, "Band Message Schedules"),
    ]
    
    print("\n" + "=" * 60)
    print("📦 Starting data migration...")
    print("=" * 60 + "\n")
    
    success_count = 0
    total_count = len(migration_order)
    
    for model, description in migration_order:
        table_name = model.__tablename__
        
        # Check if table exists in SQLite
        if table_name not in sqlite_tables:
            print(f"⏭️  {description} ({table_name}): Table not found in SQLite, skipping")
            continue
        
        # Migrate table
        if migrate_table(model, sqlite_session, pg_session):
            success_count += 1
        
        print()  # Empty line for readability
    
    # Close sessions
    sqlite_session.close()
    pg_session.close()
    
    # Reset sequences
    reset_sequences(pg_engine)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Migration Summary")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 Data migration completed successfully!")
        return 0
    else:
        print("\n⚠️  Data migration completed with errors")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
