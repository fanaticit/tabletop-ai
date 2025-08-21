# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    mongodb_uri: str
    database_name: str = "tabletop_rules"
    openai_api_key: Optional[str] = None  # Optional for basic testing
    environment: str = "development"
    secret_key: str = "your-secret-key-change-this-in-production"  # For JWT tokens
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra fields in .env

# Load settings immediately
settings = Settings()