"""
Manually trigger sync for GitHub and Jira integrations
"""
import requests

API_BASE = "http://localhost:8000"
ADMIN_EMAIL = "admin@devmetrics.ai"
ADMIN_PASSWORD = "Admin123!"

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

def trigger_sync(token, integration_id, integration_type):
    """Trigger data sync for an integration"""
    print(f"\n🔄 Triggering {integration_type} sync (ID: {integration_id})...")
    
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
        print(f"❌ Sync failed ({response.status_code}): {response.text}")
        return None

def main():
    print("=" * 60)
    print("Manual Sync Trigger")
    print("=" * 60)
    
    token = login()
    if not token:
        return
    
    # Trigger GitHub sync (ID: 3)
    trigger_sync(token, 3, "GitHub")
    
    # Trigger Jira sync (ID: 4)
    trigger_sync(token, 4, "Jira")
    
    print("\n" + "=" * 60)
    print("✅ Sync jobs submitted!")
    print("=" * 60)
    print("\nCheck Celery worker logs to see progress")
    print("Data should appear in the database within a few minutes")

if __name__ == "__main__":
    main()
