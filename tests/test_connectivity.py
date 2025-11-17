#!/usr/bin/env python3
"""
Quick connectivity test for PostgreSQL backend
"""
import os
import sys
from pathlib import Path

# Load environment variables from .env
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Add client to path
sys.path.insert(0, str(Path(__file__).parent / 'client'))

def test_database_connectivity():
    """Test PostgreSQL connection and basic queries"""
    print("=" * 60)
    print("PostgreSQL Backend Connectivity Test")
    print("=" * 60)

    # Verify environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set in environment")
        return False

    print(f"\n📍 Database URL: {db_url.split('@')[1] if '@' in db_url else db_url}")

    try:
        from storage.postgres_backend import PostgresBackend

        # Initialize connection pool
        print("\n🔌 Initializing connection pool...")
        PostgresBackend.initialize_pool()
        print("✅ Connection pool initialized")

        # Test connection
        print("\n🔍 Testing database connection...")
        with PostgresBackend.get_connection() as conn:
            with conn.cursor() as cur:
                # Test sessions table
                cur.execute('SELECT COUNT(*) FROM sessions')
                session_count = cur.fetchone()[0]
                print(f"✅ Sessions table accessible ({session_count} sessions)")

                # Test other tables
                tables = ['conversation_chunks', 'memories', 'tasks', 'artifacts', 'agents']
                for table in tables:
                    cur.execute(f'SELECT COUNT(*) FROM {table}')
                    count = cur.fetchone()[0]
                    print(f"✅ {table} table accessible ({count} records)")

                # Get session details
                print("\n📋 Session details:")
                cur.execute('SELECT id, title, status, created FROM sessions ORDER BY created DESC LIMIT 5')
                sessions = cur.fetchall()
                if sessions:
                    for session_id, title, status, created in sessions:
                        print(f"   - {session_id}: {title or '(no title)'} ({status}) - {created}")
                else:
                    print("   (No sessions found)")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Database is ready!")
        print("=" * 60)
        return True

    except Exception as e:
        import traceback
        print(f"\n❌ Database connectivity test FAILED")
        print(f"\nError: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("\n" + "=" * 60)
        return False

if __name__ == "__main__":
    success = test_database_connectivity()
    sys.exit(0 if success else 1)
