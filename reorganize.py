import os
import shutil

print("="*60)
print("📁 REORGANIZING PROJECT STRUCTURE")
print("="*60)

# Create backend folder if not exists
backend_dir = "backend"
if not os.path.exists(backend_dir):
    os.makedirs(backend_dir)
    print(f"✅ Created folder: {backend_dir}/")

# Files to move to backend folder
files_to_move = [
    "controller.py",
    "database.py", 
    "auth.py",
    "scheduler.py"
]

# Create __init__.py
init_file = os.path.join(backend_dir, "__init__.py")
if not os.path.exists(init_file):
    with open(init_file, "w") as f:
        f.write("# Backend package - contains all server-side modules\n")
    print(f"✅ Created: {init_file}")

# Move files
for filename in files_to_move:
    src = filename
    dst = os.path.join(backend_dir, filename)
    
    if os.path.exists(src):
        # Read content and fix imports
        with open(src, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Update internal imports for files that import from each other
        if filename == "scheduler.py":
            content = content.replace(
                "from database import",
                "from backend.database import"
            )
        elif filename == "auth.py":
            content = content.replace(
                "from database import",
                "from backend.database import"
            )
        
        # Write to new location
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Remove old file
        os.remove(src)
        print(f"✅ Moved: {src} → {dst}")
    else:
        print(f"⏭️  Skipped (not found): {src}")

# Update main.py imports
main_file = "main.py"
if os.path.exists(main_file):
    with open(main_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace imports
    content = content.replace(
        "from controller import ParkingLot, ids",
        "from backend.controller import ParkingLot, ids"
    )
    content = content.replace(
        "from database import init_db, get_db, User, Booking, Notification, ActivityLog",
        "from backend.database import init_db, get_db, User, Booking, Notification, ActivityLog"
    )
    content = content.replace(
        "from auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY as JWT_SECRET, ALGORITHM",
        "from backend.auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY as JWT_SECRET, ALGORITHM"
    )
    content = content.replace(
        "from scheduler import start_scheduler, stop_scheduler",
        "from backend.scheduler import start_scheduler, stop_scheduler"
    )
    
    with open(main_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Updated imports in: {main_file}")

# Update init_db.py if it exists
init_db_file = "init_db.py"
if os.path.exists(init_db_file):
    with open(init_db_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace(
        "from database import",
        "from backend.database import"
    )
    
    with open(init_db_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Updated imports in: {init_db_file}")

print("\n" + "="*60)
print("✅ REORGANIZATION COMPLETE!")
print("="*60)
print("\n📂 NEW PROJECT STRUCTURE:\n")
print("""
DDCO PROJECT/
│
├── main.py                 # FastAPI application (entry point)
├── init_db.py              # Database initialization
├── stop_server.py          # Server stop utility
├── .env                    # Environment variables
├── requirements.txt        # Dependencies
├── smart_parking.db        # SQLite database
│
├── backend/                # 🆕 Backend modules
│   ├── __init__.py         # Package init
│   ├── controller.py       # Parking logic, robots, FSM
│   ├── database.py         # SQLAlchemy models
│   ├── auth.py             # JWT authentication
│   └── scheduler.py        # Background tasks
│
├── templates/              # HTML templates
│   ├── index.html
│   ├── login.html
│   └── unified_dashboard.html
│
├── README.md
├── FEATURES_GUIDE.md
└── USER_GUIDE.md
""")

print("\n🚀 To run the project:")
print("   python main.py")
