from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db, engine, Base
from core.models import IngestedData
from config.settings import settings

# Initialize operational database schemas on system launch
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Data Ingestion Gateway Engine")

@app.post("/webhooks/receiver")
def receive_webhook(payload: dict, x_signature: str = Header(None), db: Session = Depends(get_db)):
    # Structural signature token check for push notifications authentication
    if x_signature != settings.API_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Authentication signature mismatch.")
    
    db_data = IngestedData(source="webhook", payload=str(payload))
    db.add(db_data)
    db.commit()
    return {"status": "success", "message": "Real-time payload successfully recorded."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
