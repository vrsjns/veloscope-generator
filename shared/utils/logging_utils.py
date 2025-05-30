import logging
import sys
import os
from ..config import ENV

def configure_logger(name, log_level=None):
    """
    Configure and return a logger with consistent formatting
    
    Args:
        name (str): Name of the logger, typically the module name
        log_level (int, optional): Logging level. Defaults to INFO in production, DEBUG otherwise.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Determine log level based on environment if not specified
    if log_level is None:
        log_level = logging.INFO if ENV == "production" else logging.DEBUG
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Optional: Add file logging capability
def add_file_handler(logger, log_dir="/tmp/logs", log_file=None):
    """
    Add a file handler to the logger
    
    Args:
        logger (logging.Logger): Logger to add file handler to
        log_dir (str): Directory to store log files
        log_file (str, optional): Log file name. Defaults to logger name + .log
    """
    if log_file is None:
        log_file = f"{logger.name}.log"
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create file handler
    file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
    file_handler.setLevel(logger.level)
    
    # Use the same formatter as console handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)