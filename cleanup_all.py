import os
import shutil

print("=" * 60)
print("🧹 PROJECT CLEANUP - Removing duplicates & organizing")
print("=" * 60)

# Files to DELETE (duplicates, test files, unused)
FILES_TO_DELETE = [
    # Test files
    "test_security.py",
    "test_registration.py", 
    "test_user_system.py",
    "TEST_PASSWORD.py",
    "quick_test.py",
    "quick_fix.py",
    
    # Duplicate/unused scripts
    "reset_db.py",
    "fix_db.py",
    "check_port.py",
    "debug_server.py",
    "cleanup.py",
    "RUN_SERVER.py",
    "run.py",
    
    # PowerShell scripts (optional)
    "Start-Server.ps1",
]

# Folders to DELETE (if they exist and are not needed)
FOLDERS_TO_DELETE = [
    "backend",      # Empty or duplicate structure
    "frontend",     # Empty or duplicate structure  
    "EXTRA",        # Extra files folder
    "__pycache__",  # Python cache
]

# FILES TO KEEP (essential project files)
FILES_TO_KEEP = [
    "main.py",              # Main FastAPI app
    "controller.py",        # Parking logic
    "database.py",          # SQLAlchemy models
    "auth.py",              # JWT authentication
    "scheduler.py",         # Background tasks
    "init_db.py",           # Database initialization
    "stop_server.py",       # Server stop utility
    ".env",                 # Environment config
    ".gitignore",           # Git ignore
    "requirements.txt",     # Dependencies
    "LICENSE",              # License file
    "smart_parking.db",     # Database (keep if exists)
]

print("\n📁 Files to DELETE:")
deleted_count = 0
for filename in FILES_TO_DELETE:
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"   ✅ Deleted: {filename}")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed: {filename} - {e}")
    else:
        print(f"   ⏭️  Not found: {filename}")

print(f"\n📂 Folders to DELETE:")
for folder in FOLDERS_TO_DELETE:
    if os.path.exists(folder) and os.path.isdir(folder):
        try:
            shutil.rmtree(folder)
            print(f"   ✅ Deleted folder: {folder}")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed: {folder} - {e}")
    else:
        print(f"   ⏭️  Not found: {folder}")

print("\n" + "=" * 60)
print(f"✅ Cleanup complete! Removed {deleted_count} items.")
print("=" * 60)

print("\n📂 YOUR CLEAN PROJECT STRUCTURE:")
print("""
DDCO PROJECT/
├── main.py              # FastAPI application
├── controller.py        # Parking lot logic & simulation
├── database.py          # SQLAlchemy models
├── auth.py              # JWT authentication
├── scheduler.py         # Background job scheduler
├── init_db.py           # Database reset script
├── stop_server.py       # Stop server utility
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── smart_parking.db     # SQLite database
└── templates/
    ├── index.html           # Home page (booking UI)
    ├── login.html           # Login/Register page
    └── unified_dashboard.html  # User dashboard
""")

print("\n🚀 To run the project:")
print("   1. python init_db.py     # Reset database (first time)")
print("   2. python main.py        # Start server")
print("   3. Open http://localhost:8000")
