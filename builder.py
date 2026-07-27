import subprocess
from pathlib import Path


def setup_platform_boilerplate():
    """
    Automated generation script for a complete multi-component Data Ingestion Platform.
    Optimized for Python 3.14 compatibility using updated requirements.txt constraints, 
    Psycopg 3, and modern container runtimes to avoid source compilation bottlenecks.
    Creates structured directories and operational boilerplate code for FastAPI (Webhooks),
    Celery (Cron/Polling tasks), Streamlit (Admin Panel), and full Docker service orchestration.
    Automatically initializes a local project workspace and adds dependencies using modern uv commands.
    """
    base_directory = Path("data_ingestion_platform")
    base_directory.mkdir(exist_ok=True)
    
    files_manifest = {
        "requirements.txt": """
fastapi>=0.139.2
uvicorn[standard]>=0.30.0
celery>=5.4.0
redis>=5.0.7
streamlit>=1.60.0
sqlalchemy>=2.0.31
pydantic-settings>=2.3.4
requests>=2.32.3
psycopg[binary]>=3.2.1
pandas>=2.2.2
""",
        "Dockerfile": """
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies required for compilation and database adapters
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
""",
        "docker-compose.yml": """
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ingestion_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  worker:
    build: .
    command: celery -A workers.celery_app.celery_app worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  beat:
    build: .
    command: celery -A workers.celery_app.celery_app beat --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  admin:
    build: .
    command: streamlit run admin/app.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
""",
        "config/__init__.py": "",
        "config/settings.py": """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/ingestion_db"
    REDIS_URL: str = "redis://redis:6379/0"
    API_SECRET_TOKEN: str = "supersecrettoken"

    class Config:
        env_file = ".env"

settings = Settings()
""",
        "core/__init__.py": "",
        "core/database.py": """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
        "core/models.py": """
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
""",
        "backend/__init__.py": "",
        "backend/main.py": """
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
""",
        "workers/__init__.py": "",
        "workers/celery_app.py": """
from celery import Celery
from celery.schedules import crontab
from config.settings import settings

celery_app = Celery("ingestion_workers", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Automated cron schedules maintaining local repository freshness
celery_app.conf.beat_schedule = {
    "periodic-data-reconciliation-every-5-minutes": {
        "task": "workers.tasks.fetch_periodic_data",
        "schedule": crontab(minute="*/5"),
    },
}

celery_app.autodiscover_tasks(["workers"])
""",
        "workers/tasks.py": """
import requests
from workers.celery_app import celery_app
from core.database import SessionLocal
from core.models import IngestedData, IngestionLog

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
""",
        "admin/__init__.py": "",
        "admin/app.py": """
import streamlit as st
import pandas as pd
from core.database import SessionLocal
from core.models import IngestedData, IngestionLog
from workers.tasks import fetch_periodic_data

st.set_page_config(page_title="Ingestion Platform Dashboard", layout="wide")
st.title("📊 Data Ingestion Platform Admin Control Plane")

db = SessionLocal()

st.sidebar.header("System Control Plane")
if st.sidebar.button("Force Ingestion Synchronizer Run"):
    fetch_periodic_data.delay()
    st.sidebar.success("Dispatched ad-hoc execution queue signal.")

if st.sidebar.button("Refresh Live Telemetry"):
    st.rerun()

left_pane, right_pane = st.columns(2)

with left_pane:
    st.subheader("📥 Incoming Payloads Stream")
    data_rows = db.query(IngestedData).order_by(IngestedData.received_at.desc()).limit(15).all()
    if data_rows:
        df_data = pd.DataFrame([
            {"ID": r.id, "Source Type": r.source, "Payload Text Fragment": r.payload[:80], "Ingested At": r.received_at} 
            for r in data_rows
        ])
        st.dataframe(df_data, use_container_width=True)
    else:
        st.info("No metrics discovered in database streams.")

with right_pane:
    st.subheader("📜 Periodic Reconciliation Engine Logs")
    log_rows = db.query(IngestionLog).order_by(IngestionLog.timestamp.desc()).limit(15).all()
    if log_rows:
        df_logs = pd.DataFrame([
            {"ID": r.id, "Engine Component": r.task_name, "Execution Status": r.status, "Message Summary": r.message, "Timestamp": r.timestamp} 
            for r in log_rows
        ])
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No worker orchestration entries logged yet.")

db.close()
"""
    }

    print(f"[*] Initializing boilerplate structure inside target: ./{base_directory}")
    for relative_path, document_contents in files_manifest.items():
        destination = base_directory / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as target_file:
            target_file.write(document_contents.strip() + "\n")
        print(f" -> Generated: {relative_path}")
    print("[*] Complete file generation finished.")

    # Modern environment automation using uv project workflow
    print("[*] Launching automated project workspace setup via 'uv'...")
    try:
        # Initialize a clean, bare uv managed project workspace
        subprocess.run(["uv", "init", "--bare"], cwd=base_directory, check=True)
        print(" -> Successfully initialized project workspace (pyproject.toml)")
        
        # Add packages using modern 'uv add' toolchain
        dependencies = [
            "fastapi>=0.139.2",
            "uvicorn[standard]>=0.30.0",
            "celery>=5.4.0",
            "redis>=5.0.7",
            "streamlit>=1.60.0",
            "sqlalchemy>=2.0.31",
            "pydantic-settings>=2.3.4",
            "requests>=2.32.3",
            "psycopg[binary]>=3.2.1",
            "pandas>=2.2.2"
        ]
        subprocess.run(["uv", "add"] + dependencies, cwd=base_directory, check=True)
        print(" -> Successfully tracked and locked dependencies via 'uv add'.")
    except FileNotFoundError:
        print("[!] Warning: 'uv' executable not detected in your system PATH.")
        print("    To resolve this, install uv or manually set up your environment inside the generated directory:")
        print(f"    cd {base_directory} && uv init && uv add fastapi uvicorn celery redis streamlit sqlalchemy pydantic-settings requests \"psycopg[binary]\" pandas")
    except subprocess.CalledProcessError as error:
        print(f"[!] Error encountered during environment setup execution: {error}")

if __name__ == "__main__":
    setup_platform_boilerplate()
