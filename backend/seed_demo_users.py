"""
Seed script to create demo users for DevMetrics AI
"""
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

def seed_demo_users():
    """Create demo users for testing"""
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"⚠️  Database already has {existing_users} user(s). Skipping seed.")
            return
        
        # Create Manager user
        manager = User(
            email="manager@devmetrics.ai",
            full_name="Demo Manager",
            hashed_password=get_password_hash("Manager123!"),
            role="manager",
            is_active=1
        )
        db.add(manager)
        
        # Create Developer user
        developer = User(
            email="dev@devmetrics.ai",
            full_name="Demo Developer",
            hashed_password=get_password_hash("Dev123!"),
            role="developer",
            is_active=1
        )
        db.add(developer)
        
        # Commit all changes
        db.commit()
        
        print("✅ Successfully created demo users:")
        print(f"   - Manager: manager@devmetrics.ai / Manager123!")
        print(f"   - Developer: dev@devmetrics.ai / Dev123!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating demo users: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_users()
