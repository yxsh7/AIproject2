"""
Create developer profiles for demo users
"""
from app.database import SessionLocal
from app.models.user import User
from app.models.developer import DeveloperProfile, RoleLevel
from app.models.organization import Organization

db = SessionLocal()

try:
    # Get the organization
    org = db.query(Organization).filter(Organization.slug == "demo-org").first()
    if not org:
        print("❌ Organization not found!")
        exit(1)
    
    # Get the developer user
    dev_user = db.query(User).filter(User.email == "dev@devmetrics.ai").first()
    if not dev_user:
        print("❌ Developer user not found!")
        exit(1)
    
    # Check if profile already exists
    existing_profile = db.query(DeveloperProfile).filter(
        DeveloperProfile.user_id == dev_user.id
    ).first()
    
    if existing_profile:
        print("Developer profile already exists, updating...")
        existing_profile.github_username = "yxsh7"  # Your GitHub username
        existing_profile.jira_username = "yashkamthe03@gmail.com"  # Your Jira email
        existing_profile.organization_id = org.id
        db.commit()
        print("✅ Updated developer profile")
    else:
        # Create developer profile
        dev_profile = DeveloperProfile(
            user_id=dev_user.id,
            organization_id=org.id,
            role_level=RoleLevel.MID,
            team="Engineering",
            job_title="Software Engineer",
            github_username="yxsh7",  # Your GitHub username
            jira_username="yashkamthe03@gmail.com"  # Your Jira email
        )
        db.add(dev_profile)
        db.commit()
        print("✅ Created developer profile")
    
    print(f"\nDeveloper Profile:")
    print(f"  User: {dev_user.email}")
    print(f"  GitHub: yxsh7")
    print(f"  Jira: yashkamthe03@gmail.com")
    print(f"  Organization: {org.name}")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
