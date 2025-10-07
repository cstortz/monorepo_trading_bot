"""
Shared logging configuration for the trading bot monorepo.
Provides both development and production logging setups.
"""

import logging
import sys
from typing import Optional
from pathlib import Path


class LoggingConfig:
    """Centralized logging configuration for all services."""
    
    @staticmethod
    def setup_logging(
        service_name: str,
        log_level: str = "INFO",
        environment: str = "development",
        log_file: Optional[str] = None
    ) -> logging.Logger:
        """
        Set up logging for a service.
        
        Args:
            service_name: Name of the service (e.g., 'hello-world')
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            environment: Environment (development, production)
            log_file: Optional log file path
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(service_name)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        if environment == "development":
            # Development logging with detailed formatting
            formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Console handler for development
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
        else:
            # Production logging with JSON formatting
            import json
            import traceback
            
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    log_entry = {
                        'timestamp': self.formatTime(record),
                        'level': record.levelname,
                        'service': service_name,
                        'message': record.getMessage(),
                        'module': record.module,
                        'function': record.funcName,
                        'line': record.lineno
                    }
                    
                    if record.exc_info:
                        log_entry['exception'] = traceback.format_exception(*record.exc_info)
                    
                    return json.dumps(log_entry)
            
            formatter = JSONFormatter()
            
            # Console handler for production
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def get_logger(service_name: str) -> logging.Logger:
        """Get an existing logger for a service."""
        return logging.getLogger(service_name)


def setup_service_logging(service_name: str, environment: str = "development") -> logging.Logger:
    """
    Convenience function to set up logging for a service.
    
    Args:
        service_name: Name of the service
        environment: Environment (development, production)
        
    Returns:
        Configured logger instance
    """
    return LoggingConfig.setup_logging(
        service_name=service_name,
        log_level="DEBUG" if environment == "development" else "INFO",
        environment=environment
    )
