from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    QDRANT_URL: str = Field(..., env="QDRANT_URL")
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    QDRANT_COLLECTION: str = Field("tools", env="QDRANT_COLLECTION")
    API_PREFIX: str = Field("/api/v1", env="API_PREFIX")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()