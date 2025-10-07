"""
Hello World FastAPI Service

A simple FastAPI service to demonstrate the monorepo structure
and logging configuration.
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

from shared.logging.config import setup_service_logging
from shared.config.settings import get_config

# Configuration
config = get_config()
logger = setup_service_logging("hello-world", config.environment)

# FastAPI app
app = FastAPI(
    title="Hello World Service",
    description="A simple FastAPI service for the trading bot monorepo",
    version="1.0.0",
    debug=config.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HelloResponse(BaseModel):
    message: str
    service: str
    version: str
    environment: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

# Routes
@app.get("/", response_model=HelloResponse)
async def hello():
    """Hello world endpoint."""
    logger.info("Hello endpoint accessed")
    
    return HelloResponse(
        message="Hello from the Trading Bot Monorepo!",
        service="hello-world",
        version="1.0.0",
        environment=config.environment
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check endpoint accessed")
    
    return HealthResponse(
        status="healthy",
        service="hello-world",
        version="1.0.0"
    )

@app.get("/info")
async def service_info():
    """Service information endpoint."""
    logger.info("Service info endpoint accessed")
    
    return {
        "service": "hello-world",
        "version": "1.0.0",
        "environment": config.environment,
        "debug": config.debug,
        "log_level": config.log_level
    }

@app.get("/logs/test")
async def test_logging():
    """Test logging at different levels."""
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    
    return {"message": "Logging test completed - check the logs!"}

if __name__ == "__main__":
    logger.info(f"Starting Hello World service on {config.api_host}:{config.api_port}")
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        log_level=config.log_level.lower()
    )
