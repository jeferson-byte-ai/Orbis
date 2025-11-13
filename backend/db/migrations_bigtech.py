"""
Database Migration Script - SQLite to PostgreSQL
BigTech-level database setup
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.db.base import Base
from backend.db.models import *
from backend.db.models_security import *


def create_postgresql_database():
    """Create all tables in PostgreSQL"""
    print("🔧 Creating PostgreSQL database schema...")
    
    # Get database URL from settings
    db_url = settings.database_url
    
    print(f"📊 Database URL: {db_url}")
    
    # Create engine
    engine = create_engine(db_url, echo=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ All tables created successfully!")
    
    return engine


def migrate_data_sqlite_to_postgresql(sqlite_url: str, postgres_url: str):
    """Migrate data from SQLite to PostgreSQL"""
    print("📦 Starting data migration from SQLite to PostgreSQL...")
    
    # Connect to both databases
    sqlite_engine = create_engine(sqlite_url)
    postgres_engine = create_engine(postgres_url)
    
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    
    try:
        # Get all model classes
        models_to_migrate = [
            User, VoiceProfile, Room, RoomParticipant,
            Subscription, UserSession, PasswordReset,
            Recording, Transcript, APIKey, AuditLog,
            RoomEncryptionKey, UsageMetric
        ]
        
        for model_class in models_to_migrate:
            print(f"\n📋 Migrating {model_class.__tablename__}...")
            
            # Get all records from SQLite
            records = sqlite_session.query(model_class).all()
            
            if not records:
                print(f"  ⏭️  No records to migrate")
                continue
            
            # Add to PostgreSQL
            for record in records:
                # Create new instance with same data
                postgres_session.merge(record)
            
            postgres_session.commit()
            print(f"  ✅ Migrated {len(records)} records")
        
        print("\n🎉 Data migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        postgres_session.rollback()
        raise
    finally:
        sqlite_session.close()
        postgres_session.close()


def add_postgresql_extensions(engine):
    """Add useful PostgreSQL extensions"""
    print("\n🔧 Adding PostgreSQL extensions...")
    
    extensions = [
        "uuid-ossp",  # UUID generation
        "pg_trgm",    # Fuzzy text search
        "pgcrypto"    # Encryption functions
    ]
    
    with engine.connect() as conn:
        for ext in extensions:
            try:
                conn.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}"'))
                conn.commit()
                print(f"  ✅ {ext} enabled")
            except Exception as e:
                print(f"  ⚠️  {ext} failed: {e}")


def optimize_postgresql_for_production(engine):
    """Apply production-ready PostgreSQL optimizations"""
    print("\n⚡ Applying performance optimizations...")
    
    optimizations = [
        # Create indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
        "CREATE INDEX IF NOT EXISTS idx_rooms_is_active ON rooms(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_timestamp ON audit_logs(user_id, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_security_events_user ON security_events(user_id, created_at DESC)",
        
        # Full-text search indexes
        "CREATE INDEX IF NOT EXISTS idx_users_email_trgm ON users USING gin(email gin_trgm_ops)",
        "CREATE INDEX IF NOT EXISTS idx_rooms_name_trgm ON rooms USING gin(name gin_trgm_ops)",
    ]
    
    with engine.connect() as conn:
        for sql in optimizations:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"  ✅ Applied: {sql[:60]}...")
            except Exception as e:
                print(f"  ⚠️  Skipped: {str(e)[:60]}...")


def setup_row_level_security(engine):
    """Setup Row-Level Security for multi-tenancy"""
    print("\n🔒 Setting up Row-Level Security...")
    
    rls_policies = [
        # Users can only see their own data
        """
        ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
        CREATE POLICY user_sessions_isolation ON user_sessions
            USING (user_id = current_setting('app.current_user_id')::uuid);
        """,
        
        # API keys isolation
        """
        ALTER TABLE api_keys_secure ENABLE ROW LEVEL SECURITY;
        CREATE POLICY api_keys_isolation ON api_keys_secure
            USING (user_id = current_setting('app.current_user_id')::uuid);
        """
    ]
    
    # Note: RLS requires superuser privileges
    print("  ℹ️  RLS setup requires PostgreSQL superuser")
    print("  ℹ️  Run these manually if needed:")
    for policy in rls_policies:
        print(f"\n{policy}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument("--create", action="store_true", help="Create PostgreSQL schema")
    parser.add_argument("--migrate", action="store_true", help="Migrate data from SQLite")
    parser.add_argument("--optimize", action="store_true", help="Apply production optimizations")
    parser.add_argument("--all", action="store_true", help="Do everything")
    parser.add_argument("--sqlite-url", default="sqlite:///./data/orbis.db", help="SQLite database URL")
    parser.add_argument("--postgres-url", default=None, help="PostgreSQL database URL")
    
    args = parser.parse_args()
    
    # Get PostgreSQL URL
    postgres_url = args.postgres_url or os.getenv("DATABASE_URL")
    
    if not postgres_url:
        print("❌ PostgreSQL URL not provided!")
        print("   Set DATABASE_URL environment variable or use --postgres-url")
        sys.exit(1)
    
    # Validate PostgreSQL URL
    if not postgres_url.startswith("postgresql"):
        print("❌ Invalid PostgreSQL URL!")
        print(f"   Got: {postgres_url}")
        print("   Expected: postgresql://user:pass@host/dbname")
        sys.exit(1)
    
    print("="*60)
    print("🚀 ORBIS DATABASE MIGRATION TO POSTGRESQL")
    print("="*60)
    
    engine = None
    
    try:
        if args.all or args.create:
            engine = create_postgresql_database()
            add_postgresql_extensions(engine)
        
        if args.all or args.migrate:
            if not engine:
                engine = create_engine(postgres_url)
            migrate_data_sqlite_to_postgresql(args.sqlite_url, postgres_url)
        
        if args.all or args.optimize:
            if not engine:
                engine = create_engine(postgres_url)
            optimize_postgresql_for_production(engine)
        
        if not (args.create or args.migrate or args.optimize or args.all):
            parser.print_help()
        
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
