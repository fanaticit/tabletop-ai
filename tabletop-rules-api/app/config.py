# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    mongodb_uri: str
    database_name: str = "tabletop_rules"
    
    # AI Provider Settings - can use either or both
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_ai_provider: str = "openai"  # "openai" or "anthropic"
    
    # Provider-specific settings
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    environment: str = "development"
    secret_key: str = "your-secret-key-change-this-in-production"  # For JWT tokens
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra fields in .env

# Load settings immediately
settings = Settings()