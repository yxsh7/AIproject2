"""
Script to set up GitHub and Jira integrations for DevMetrics AI
Run this after updating .env with credentials
"""
import requests
import json
import os

# Configuration
API_BASE = "http://localhost:8000"
ADMIN_EMAIL = "admin@devmetrics.ai"
ADMIN_PASSWORD = "Admin123!"

# GitHub configuration
GITHUB_ORG = "yxsh7"  # Your GitHub username/organization
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Load from environment

# Jira configuration
JIRA_URL = "https://yashkamthe03.atlassian.net"
JIRA_USERNAME = "yashkamthe03@gmail.com"  # Your Atlassian email
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN", "")  # Load from environment
JIRA_PROJECT_KEYS = ["MBA"]  # From your Jira board URL

def login():
    """Login and get JWT token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{API_BASE}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def setup_github(token):
    """Set up GitHub integration"""
    print("\n📦 Setting up GitHub integration...")
    
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN environment variable not set")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "organization_name": GITHUB_ORG,
        "access_token": GITHUB_TOKEN
    }
    
    response = requests.post(
        f"{API_BASE}/api/integrations/github",
        headers=headers,
        json=data
    )
    
    if response.status_code in [200, 201]:
        print("✅ GitHub integration configured successfully")
        integration = response.json()
        print(f"   Integration ID: {integration['id']}")
        return integration['id']
    else:
        print(f"❌ GitHub integration failed: {response.text}")
        return None

def setup_jira(token):
    """Set up Jira integration"""
    print("\n📋 Setting up Jira integration...")
    
    if not JIRA_TOKEN:
        print("❌ JIRA_API_TOKEN environment variable not set")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "workspace_url": JIRA_URL,
        "username": JIRA_USERNAME,
        "api_token": JIRA_TOKEN,
        "project_keys": JIRA_PROJECT_KEYS
    }
    
    response = requests.post(
        f"{API_BASE}/api/integrations/jira",
        headers=headers,
        json=data
    )
    
    if response.status_code in [200, 201]:
        print("✅ Jira integration configured successfully")
        integration = response.json()
        print(f"   Integration ID: {integration['id']}")
        return integration['id']
    else:
        print(f"❌ Jira integration failed: {response.text}")
        return None

def trigger_sync(token, integration_id, integration_type):
    """Trigger data sync for an integration"""
    print(f"\n🔄 Triggering {integration_type} sync...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"days_back": 30}  # Sync last 30 days
    
    response = requests.post(
        f"{API_BASE}/api/integrations/{integration_id}/sync",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sync started - Job ID: {result['job_id']}")
        print(f"   {result['message']}")
        return result['job_id']
    else:
        print(f"❌ Sync failed: {response.text}")
        return None

def main():
    print("=" * 60)
    print("DevMetrics AI - Integration Setup")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("\n❌ Setup failed: Could not login")
        return
    
    # Setup GitHub
    github_id = setup_github(token)
    
    # Setup Jira
    jira_id = setup_jira(token)
    
    # Trigger syncs
    if github_id:
        trigger_sync(token, github_id, "GitHub")
    
    if jira_id:
        trigger_sync(token, jira_id, "Jira")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check Celery worker logs to see sync progress")
    print("2. Wait 5-10 minutes for data to sync")
    print("3. Login to http://localhost:3000 to view dashboard")
    print("4. AI analysis will run automatically on synced data")

if __name__ == "__main__":
    main()

