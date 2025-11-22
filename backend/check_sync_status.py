from app.database import SessionLocal
from app.models.git_activity import GitCommit
from app.models.work_activity import WorkActivity
from app.models.integration import IntegrationConfig

db = SessionLocal()

# Check synced data
commits = db.query(GitCommit).count()
activities = db.query(WorkActivity).count()

print(f"\n{'='*60}")
print("DATA SYNC STATUS")
print(f"{'='*60}")
print(f"Git Commits: {commits}")
print(f"Work Activities: {activities}")

# Check integration status
integrations = db.query(IntegrationConfig).all()
print(f"\n{'='*60}")
print("INTEGRATION STATUS")
print(f"{'='*60}")
for i in integrations:
    print(f"\n{i.type.value.upper()}:")
    print(f"  Status: {i.status.value}")
    print(f"  Last Sync: {i.last_sync_at}")
    if i.last_error:
        print(f"  Error: {i.last_error[:200]}")

db.close()

if commits > 0:
    print(f"\n✅ SUCCESS! Data sync is working - found {commits} commits!")
else:
    print(f"\n⏳ Waiting for data... sync may still be in progress")
