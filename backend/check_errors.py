from app.database import SessionLocal
from app.models.integration import IntegrationConfig

db = SessionLocal()
integrations = db.query(IntegrationConfig).all()

for i in integrations:
    print(f"\n{i.type.value.upper()}:")
    print(f"  Status: {i.status.value}")
    print(f"  Last Sync: {i.last_sync_at}")
    if i.last_error:
        print(f"  Error: {i.last_error}")
    else:
        print(f"  Error: None")

db.close()
