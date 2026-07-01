from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "finguard"
    REDIS_URL: str = "redis://localhost:6379"
    MODEL_PATH: str = "./ai_engine/weights"
    RISK_THRESHOLD: float = 0.65
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
