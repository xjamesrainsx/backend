import requests
from core.database import SessionLocal
from core.models import IngestedData, IngestionLog

from workers.celery_app import celery_app


@celery_app.task
def fetch_periodic_data():
    db = SessionLocal()
    try:
        # Request external REST endpoint via GET/POST to sync delta updates
        response = requests.get("https://httpbin.org/json", timeout=10)
        if response.status_code == 200:
            db_data = IngestedData(source="cron_job", payload=str(response.json()))
            db.add(db_data)
            log = IngestionLog(task_name="fetch_periodic_data", status="SUCCESS", message="Data state sync complete.")
        else:
            log = IngestionLog(task_name="fetch_periodic_data", status="FAILED", message=f"HTTP Endpoint failure code: {response.status_code}")
        db.add(log)
        db.commit()
    except Exception as error:
        log = IngestionLog(task_name="fetch_periodic_data", status="ERROR", message=str(error))
        db.add(log)
        db.commit()
    finally:
        db.close()
