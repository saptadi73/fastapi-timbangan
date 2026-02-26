"""
Quick start untuk database Timbangan

Jalankan script ini untuk setup database (opsional - app sudah auto-setup)
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run command dan print status"""
    print(f"\n📍 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ {description} - OK")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"✗ {description} - FAILED")
        if result.stderr:
            print(result.stderr)
        return False


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         FastAPI Timbangan - Database Quick Start             ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check PostgreSQL connection
    print("\n📋 STEP 1: Checking PostgreSQL Connection")
    print("-" * 50)
    
    try:
        import psycopg2
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="opnpg",
                password="openpgpwd",
                database="timbangan"
            )
            print("✓ PostgreSQL connection successful")
            conn.close()
        except psycopg2.OperationalError as e:
            print(f"✗ PostgreSQL connection failed: {e}")
            print("\nTips:")
            print("  1. Pastikan PostgreSQL sudah running")
            print("  2. Cek credential di .env")
            print("  3. Pastikan database 'timbangan' sudah dibuat")
            sys.exit(1)
    except ImportError:
        print("✗ psycopg2 tidak terinstall")
        print("  Jalankan: pip install psycopg2-binary")
        sys.exit(1)
    
    # Step 2: Check imports
    print("\n📋 STEP 2: Checking Python Imports")
    print("-" * 50)
    
    try:
        from config import settings
        from database import engine, SessionLocal, Base
        from models import Timbangan
        from schemas import TimbanganCreate, TimbanganResponse
        print("✓ Semua imports dapat diload")
    except Exception as e:
        print(f"✗ Import error: {e}")
        sys.exit(1)
    
    # Step 3: Create tables
    print("\n📋 STEP 3: Creating Database Tables")
    print("-" * 50)
    
    try:
        from models import Base
        from database import engine
        
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'timbangan' in tables:
            print("\n📊 Table 'timbangan' columns:")
            columns = inspector.get_columns('timbangan')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("✗ Table 'timbangan' not found")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        sys.exit(1)
    
    # Step 4: Test database connection
    print("\n📋 STEP 4: Testing Database Operations")
    print("-" * 50)
    
    try:
        from database import SessionLocal
        from models import Timbangan
        from datetime import datetime
        
        # Test session
        db = SessionLocal()
        
        # Count records
        count = db.query(Timbangan).count()
        print(f"✓ Database query working (found {count} records)")
        
        # Test create (optional - comment out untuk skip insert test)
        # print("\nTesting insert...")
        # new_record = Timbangan(
        #     nopol="TEST-001",
        #     sopir="Test Driver",
        #     gross=1000.00,
        #     nett=900.00,
        #     petugas="Test Officer",
        #     tanggalwaktu=datetime.utcnow()
        # )
        # db.add(new_record)
        # db.commit()
        # print("✓ Insert test successful")
        
        db.close()
        
    except Exception as e:
        print(f"✗ Database operation error: {e}")
        sys.exit(1)
    
    # All done
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                 ✓ DATABASE SETUP COMPLETE                    ║
╚═══════════════════════════════════════════════════════════════╝

Next steps:
  1. Run aplikasi:
     python main.py

  2. Test API:
     http://localhost:8000/docs

  3. Lihat database migrations:
     python db_migrate.py history

  4. Docs:
     - Database: see DATABASE.md
     - API: http://localhost:8000/docs
     - Scale: see routes/scale.py
    """)


if __name__ == "__main__":
    main()
