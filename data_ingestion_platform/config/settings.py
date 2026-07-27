from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/ingestion_db"
    REDIS_URL: str = "redis://redis:6379/0"
    API_SECRET_TOKEN: str = "supersecrettoken"

    class Config:
        env_file = ".env"

settings = Settings()
