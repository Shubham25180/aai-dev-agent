import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
            
        return json.dumps(log_entry)

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    json_format: bool = True
) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Name of the logger
        log_file: Optional path to log file
        level: Logging level
        json_format: Whether to use JSON formatting
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # File handler if log_file specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        if json_format:
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
        logger.addHandler(file_handler)
    
    # Always use standard formatting for console
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger

def get_action_logger(component: str) -> logging.Logger:
    """
    Get a logger specifically for agent actions with JSON formatting.
    
    Args:
        component: Name of the component (e.g., 'llm_connector', 'planner')
        
    Returns:
        Logger configured for action logging
    """
    log_file = os.path.join('logs', 'actions', f'{component}_actions.json')
    return setup_logger(
        f'agent.actions.{component}',
        log_file=log_file,
        json_format=True
    )

def get_error_logger(component: str) -> logging.Logger:
    """
    Get a logger specifically for error tracking.
    
    Args:
        component: Name of the component
        
    Returns:
        Logger configured for error logging
    """
    log_file = os.path.join('logs', 'errors', f'{component}_errors.log')
    return setup_logger(
        f'agent.errors.{component}',
        log_file=log_file,
        level=logging.ERROR,
        json_format=False
    ) 