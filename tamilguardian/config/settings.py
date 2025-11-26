import os
from typing import Dict, Any
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: str = ""
    nebius_api_key: str = ""
    elevenlabs_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # Database
    database_url: str = "sqlite:///./tamilguardian.db"
    redis_url: str = "redis://localhost:6379"
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    max_tokens: int = 4000
    confidence_threshold: float = 0.7
    
    # Security
    secret_key: str = ""
    encryption_key: str = ""
    
    # MCP Server URLs (for production deployment)
    rag_server_url: str = "http://localhost:8001"
    llm_server_url: str = "http://localhost:8002"
    websearch_server_url: str = "http://localhost:8003"
    parser_server_url: str = "http://localhost:8004"
    elevenlabs_server_url: str = "http://localhost:8005"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "logs/tamilguardian.log",
        },
    },
    "root": {
        "level": settings.log_level,
        "handlers": ["default", "file"],
    },
}