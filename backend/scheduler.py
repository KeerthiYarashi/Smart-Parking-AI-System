from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from backend.database import SessionLocal, Booking, Notification, ActivityLog

scheduler = BackgroundScheduler()
_parking = None

def _check_expiring_soon():
    """Send warning notifications for bookings expiring in 5 minutes"""
    session = SessionLocal()
    now = datetime.utcnow()
    try:
        soon_expiring = session.query(Booking).filter(
            Booking.status == "ACTIVE",
            Booking.estimated_end_time <= now + timedelta(minutes=5),
            Booking.estimated_end_time > now
        ).all()
        
        for booking in soon_expiring:
            existing = session.query(Notification).filter(
                Notification.booking_id == booking.booking_id,
                Notification.type == "WARNING",
                Notification.message.like("%expires in%")
            ).first()
            
            if not existing:
                session.add(Notification(
                    user_id=booking.user_id,
                    booking_id=booking.booking_id,
                    message=f"⚠️ Your parking slot {booking.slot_id} expires in 5 minutes!",
                    type="WARNING"
                ))
                print(f"⏰ Warning sent for Slot {booking.slot_id}")
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ Expiring soon check error: {e}")
    finally:
        session.close()

def _expire_bookings():
    """Auto-expire bookings and free slots"""
    global _parking
    session = SessionLocal()
    now = datetime.utcnow()
    try:
        expired = session.query(Booking).filter(
            Booking.status == "ACTIVE",
            Booking.estimated_end_time <= now
        ).all()
        
        for booking in expired:
            booking.status = "EXPIRED"
            booking.exit_time = now
            
            session.add(Notification(
                user_id=booking.user_id,
                booking_id=booking.booking_id,
                message=f"⏰ Your parking time for Slot {booking.slot_id} has expired.",
                type="ALERT"
            ))
            
            session.add(ActivityLog(
                user_id=booking.user_id,
                action=f"Booking expired for Slot {booking.slot_id}",
                timestamp=now
            ))
            
            if _parking:
                _parking.exit_vehicle(booking.slot_id)
            
            print(f"🚫 Expired: Slot {booking.slot_id} for User {booking.user_id}")
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ Expiry job error: {e}")
    finally:
        session.close()

def start_scheduler(parking):
    global _parking
    _parking = parking
    if not scheduler.running:
        scheduler.add_job(_check_expiring_soon, "interval", seconds=60, id="expiring_soon")
        scheduler.add_job(_expire_bookings, "interval", seconds=30, id="expire_bookings")
        scheduler.start()
        print("✅ [SCHEDULER] Started - monitoring expirations every 30s, warnings every 60s")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("🛑 [SCHEDULER] Stopped")
