"""
Application-wide logging configuration.
Provides structured logging for debugging and observability.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color coding for different log levels."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Logger name (usually __name__ from calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, only logs to console
        use_colors: Whether to use colored output in console

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger(__name__, level=logging.DEBUG)
        >>> logger.info("Application started")
        >>> logger.debug("Debug information")
        >>> logger.error("An error occurred")
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Choose formatter based on color preference
    console_format = '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s'
    if use_colors:
        console_formatter = ColoredFormatter(
            console_format,
            datefmt='%H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            console_format,
            datefmt='%H:%M:%S'
        )

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def setup_api_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Set up a logger specifically for API requests with rotating file handler.

    Args:
        log_dir: Directory to store log files

    Returns:
        Configured logger for API
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir_path / f"api_{timestamp}.log"

    return setup_logger("api", level=logging.DEBUG, log_file=str(log_file))


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with standard configuration.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return setup_logger(name, level=logging.INFO)


# Example usage helpers
def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with arguments and return values.

    Example:
        >>> @log_function_call(logger)
        >>> def my_function(x, y):
        >>>     return x + y
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}", exc_info=True)
                raise
        return wrapper
    return decorator
