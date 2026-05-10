"""
Migration script to fix existing users with invalid verification_status values.
This converts 'not_submitted' to 'unverified' for all existing users.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings
from models.user import User

def fix_verification_status():
    """Update all users with 'not_submitted' status to 'unverified'"""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Count records to update
        old_count = session.query(User).filter(
            User.verification_status == "not_submitted"
        ).count()
        
        if old_count > 0:
            print(f"🔧 Fixing {old_count} users with 'not_submitted' status...")
            
            # Update all records with 'not_submitted' to 'unverified'
            session.query(User).filter(
                User.verification_status == "not_submitted"
            ).update({"verification_status": "unverified"}, synchronize_session=False)
            
            session.commit()
            print(f"✅ Successfully updated {old_count} users to 'unverified'")
        else:
            print("✅ No users with 'not_submitted' status found. Database is clean.")
            
        # Verify all status values are valid
        invalid_count = session.query(User).filter(
            ~User.verification_status.in_(["unverified", "pending", "verified", "rejected"])
        ).count()
        
        if invalid_count > 0:
            print(f"⚠️  Warning: Found {invalid_count} users with invalid verification_status values")
        else:
            print("✅ All users have valid verification_status values")
            
    except Exception as e:
        print(f"❌ Error fixing verification status: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Starting verification_status migration...")
    fix_verification_status()
    print("✅ Migration complete!")
