from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# SQLite Database URL
DATABASE_URL = "sqlite:///./smart_parking.db"

# Create Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- MODELS ---

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")

class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    slot_id = Column(Integer)
    vehicle_type = Column(String)
    duration_hours = Column(Float)
    entry_time = Column(DateTime, default=datetime.utcnow)
    estimated_end_time = Column(DateTime)
    exit_time = Column(DateTime, nullable=True)
    billing_cost = Column(Float)
    status = Column(String, default="ACTIVE") # ACTIVE, COMPLETED, EXPIRED
    
    user = relationship("User", back_populates="bookings")
    notifications = relationship("Notification", back_populates="booking", cascade="all, delete-orphan")

class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=True)
    message = Column(String)
    type = Column(String, default="INFO") # INFO, WARNING, SUCCESS
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="notifications")
    booking = relationship("Booking", back_populates="notifications")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="activity_logs")

# --- UTILS ---

def init_db():
    """Creates all tables defined in models"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

def get_db():
    """Dependency for FastAPI Routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
