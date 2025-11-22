"""
Direct database setup for integrations
NOTE: DO NOT hardcode API tokens here. Use environment variables instead.
"""
from app.database import SessionLocal
from app.models.organization import Organization
from app.models.integration import IntegrationConfig, IntegrationType, IntegrationStatus
import json
import os

def setup_integrations():
    """Create organization and integrations directly in database"""
    db = SessionLocal()
    
    # Load tokens from environment
    github_token = os.getenv("GITHUB_TOKEN", "")
    jira_api_token = os.getenv("JIRA_API_TOKEN", "")
    
    if not github_token or not jira_api_token:
        print("❌ Error: GITHUB_TOKEN and JIRA_API_TOKEN environment variables must be set")
        print("   Set them with:")
        print("   export GITHUB_TOKEN=your_github_token")
        print("   export JIRA_API_TOKEN=your_jira_token")
        return
    
    try:
        # Create or get organization
        org = db.query(Organization).filter(Organization.slug == "demo-org").first()
        if not org:
            org = Organization(
                name="Demo Organization",
                slug="demo-org",
                description="Demo organization for DevMetrics AI"
            )
            db.add(org)
            db.flush()
            print(f"✅ Created organization: {org.name} (ID: {org.id})")
        else:
            print(f"✅ Using existing organization: {org.name} (ID: {org.id})")
        
        # Create GitHub integration
        github_config = db.query(IntegrationConfig).filter(
            IntegrationConfig.organization_id == org.id,
            IntegrationConfig.type == IntegrationType.GITHUB
        ).first()
        
        if not github_config:
            github_config = IntegrationConfig(
                organization_id=org.id,
                type=IntegrationType.GITHUB,
                status=IntegrationStatus.ACTIVE,
                config={
                    "organization_name": "yxsh7",
                    "access_token": github_token
                }
            )
            db.add(github_config)
            print("✅ Created GitHub integration")
        else:
            print("✅ GitHub integration already exists")
        
        # Create Jira integration
        jira_config = db.query(IntegrationConfig).filter(
            IntegrationConfig.organization_id == org.id,
            IntegrationConfig.type == IntegrationType.JIRA
        ).first()
        
        if not jira_config:
            jira_config = IntegrationConfig(
                organization_id=org.id,
                type=IntegrationType.JIRA,
                status=IntegrationStatus.ACTIVE,
                config={
                    "url": "https://yashkamthe03.atlassian.net",
                    "username": "yashkamthe03@gmail.com",
                    "api_token": jira_api_token,
                    "project_keys": ["MBA"]
                }
            )
            db.add(jira_config)
            print("✅ Created Jira integration")
        else:
            print("✅ Jira integration already exists")
        
        db.commit()
        
        print("\n" + "="*60)
        print("✅ Integration setup complete!")
        print("="*60)
        print(f"\nOrganization ID: {org.id}")
        print(f"GitHub Integration: Active")
        print(f"Jira Integration: Active")
        print("\nNote: Data sync will happen automatically via Celery")
        print("or you can trigger it manually through the API/UI")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    setup_integrations()

