"""Logging utilities for the robotape framework."""
import logging
import inspect
from functools import wraps
from typing import Any, Callable

# Global debug flag
DEBUG = False

def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    global DEBUG
    DEBUG = debug
    
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)

def log_execution(func: Callable) -> Callable:
    """Decorator to log function execution if debug mode is enabled."""
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        if DEBUG:
            logging.debug(f"Executing {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = await func(*args, **kwargs)
            if DEBUG:
                logging.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            if DEBUG:
                logging.error(f"Error in {func.__name__}: {str(e)}")
            raise

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        if DEBUG:
            logging.debug(f"Executing {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            if DEBUG:
                logging.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            if DEBUG:
                logging.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
