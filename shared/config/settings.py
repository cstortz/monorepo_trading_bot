"""
Shared configuration settings for the trading bot monorepo.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """Base configuration class."""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Service configuration
    service_name: str = "trading-bot"
    service_version: str = "1.0.0"
    
    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"


class ProductionConfig(BaseConfig):
    """Production configuration."""
    
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"


def get_config() -> BaseConfig:
    """Get configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()
