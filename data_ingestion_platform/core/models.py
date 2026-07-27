from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from core.database import Base

class IngestedData(Base):
    __tablename__ = "ingested_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)  # e.g., 'webhook' or 'cron_job'
    payload = Column(Text)
    received_at = Column(DateTime, default=datetime.utcnow)

class IngestionLog(Base):
    __tablename__ = "ingestion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String)
    status = Column(String)  # 'SUCCESS', 'FAILED', 'ERROR'
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
