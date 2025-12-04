"""
Standalone script to initialize/reset the database
Run this if you encounter database errors
"""

from backend.database import init_db, engine, Base
import os
import sys
import time

def reset_database():
    print("\n🗄️  DATABASE INITIALIZATION SCRIPT")
    print("="*60)
    
    db_file = "smart_parking.db"
    
    # Check if database exists
    if os.path.exists(db_file):
        print(f"⚠️  Found existing database: {db_file}")
        print("\n⚠️  WARNING: Server must be stopped before resetting database!")
        print("   1. Stop the server (CTRL+C in server terminal)")
        print("   2. Or run: Get-Process -Name python | Stop-Process -Force")
        print()
        response = input("   Do you want to reset it? (y/N): ")
        
        if response.lower() == 'y':
            try:
                os.remove(db_file)
                print("   ✅ Old database deleted")
            except PermissionError:
                print("\n❌ ERROR: Database is locked by another process")
                print("\n🔧 Quick Fix:")
                print("   1. Open new PowerShell terminal")
                print("   2. Run: Get-Process -Name python | Stop-Process -Force")
                print("   3. Wait 2 seconds")
                print("   4. Run: python init_db.py")
                print("\n   OR close this terminal and try again after stopping server")
                return False
            except Exception as e:
                print(f"\n❌ ERROR: {e}")
                return False
    
    # Create tables
    print("\n📋 Creating tables...")
    try:
        init_db()
        print("✅ SUCCESS! Database initialized")
        print(f"   Location: {os.path.abspath(db_file)}")
        print("\n📊 Tables created:")
        print("   - users")
        print("   - bookings")
        print("   - notifications")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ You can now start the server: python main.py\n")
    return True

if __name__ == "__main__":
    success = reset_database()
    if not success:
        sys.exit(1)

from backend.database import init_db

if __name__ == "__main__":
    print("Initializing Database...")
    try:
        init_db()
        print("✅ Database tables created successfully.")
        print("   - users")
        print("   - bookings")
        print("   - notifications")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
