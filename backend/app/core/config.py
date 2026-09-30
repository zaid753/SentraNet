from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "SENTRANET"
    APP_VERSION: str = "0.1.0"
    
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    
    FRONTEND_URL: str = "http://localhost:5173"
    
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str = Field(default="")
    MODEL_PATH: str = Field(default="")
    DATA_PATH: str = Field(default="./data")

    @property
    def cors_origins(self) -> List[str]:
        origins = [url.strip() for url in self.FRONTEND_URL.split(",") if url.strip()]
        # Support both localhost and 127.0.0.1 for local development
        if "http://localhost:5173" in origins and "http://127.0.0.1:5173" not in origins:
            origins.append("http://127.0.0.1:5173")
        return origins

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
