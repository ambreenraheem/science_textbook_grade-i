"""
Structured JSON logging with child-friendly error messages.

Provides dual-layer error handling per Constitution V:
- Technical logs for developers (JSON format)
- Child-friendly messages for Grade-1 users

Example:
    ```python
    from src.utils.logger import get_logger, get_child_friendly_message

    logger = get_logger(__name__)

    try:
        # Some operation
        pass
    except Exception as e:
        logger.error("Database query failed", extra={"query": "SELECT..."})
        user_message = get_child_friendly_message("database_error")
        st.error(user_message)  # Shows: "Oops, something went wrong!"
    ```
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


# Child-friendly error messages (Constitution V: dual-layer errors)
CHILD_FRIENDLY_MESSAGES = {
    "database_error": "Oops, something went wrong! Let's try again.",
    "connection_error": "Hmm, we're having trouble connecting. Please wait a moment.",
    "content_not_found": "We can't find that lesson right now. Let's try another one!",
    "video_error": "Video is resting now! Let's read the lesson together.",
    "image_error": "This picture is taking a nap. Let's keep learning!",
    "general_error": "Oops! Something unexpected happened. Let's try again.",
    "loading_error": "Still loading... This is taking longer than usual.",
    "timeout_error": "This is taking too long. Let's try something else!",
}


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as JSON.

    Includes timestamp, level, message, and extra fields for structured logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up a logger with JSON formatting and console output.

    Args:
        name: Logger name (usually __name__ of the module)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger

    # Set log level from environment or parameter
    if level is None:
        try:
            from .config import get_config
            level = get_config().log_level
        except:
            level = "INFO"

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (usually __name__ of the module)
        level: Optional log level override

    Returns:
        Configured logger instance

    Example:
        ```python
        from src.utils.logger import get_logger

        logger = get_logger(__name__)
        logger.info("Application started")
        logger.error("Database error", extra={"user_id": 123})
        ```
    """
    return setup_logger(name, level)


def get_child_friendly_message(error_type: str, default: Optional[str] = None) -> str:
    """
    Get child-friendly error message for display to Grade-1 users.

    Args:
        error_type: Type of error (e.g., "database_error", "video_error")
        default: Default message if error_type not found

    Returns:
        Child-friendly error message suitable for 6-7 year olds

    Example:
        ```python
        from src.utils.logger import get_child_friendly_message

        try:
            # Some database operation
            pass
        except Exception as e:
            logger.error("Database query failed")
            message = get_child_friendly_message("database_error")
            st.error(message)  # Shows: "Oops, something went wrong!"
        ```
    """
    return CHILD_FRIENDLY_MESSAGES.get(
        error_type,
        default or CHILD_FRIENDLY_MESSAGES["general_error"]
    )


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration_ms: float,
    threshold_ms: float = 500.0
) -> None:
    """
    Log performance metrics and warn if threshold exceeded.

    Per Constitution IX, database queries should be <500ms p95.

    Args:
        logger: Logger instance
        operation: Name of the operation (e.g., "get_lessons_by_chapter")
        duration_ms: Duration in milliseconds
        threshold_ms: Performance threshold in milliseconds (default: 500ms)

    Example:
        ```python
        import time
        from src.utils.logger import get_logger, log_performance

        logger = get_logger(__name__)

        start = time.time()
        # Perform database query
        duration_ms = (time.time() - start) * 1000

        log_performance(logger, "get_all_chapters", duration_ms)
        ```
    """
    log_data = {
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
        "threshold_ms": threshold_ms,
        "exceeded_threshold": duration_ms > threshold_ms,
    }

    if duration_ms > threshold_ms:
        logger.warning(
            f"Performance threshold exceeded for {operation}",
            extra=log_data
        )
    else:
        logger.info(
            f"Performance OK for {operation}",
            extra=log_data
        )


def log_user_action(
    logger: logging.Logger,
    action: str,
    **kwargs
) -> None:
    """
    Log user actions for observability (Constitution V).

    Args:
        logger: Logger instance
        action: Action name (e.g., "chapter_clicked", "lesson_viewed")
        **kwargs: Additional context (chapter_id, lesson_id, etc.)

    Example:
        ```python
        from src.utils.logger import get_logger, log_user_action

        logger = get_logger(__name__)

        log_user_action(
            logger,
            "chapter_clicked",
            chapter_id="abc123",
            chapter_title="Plants"
        )
        ```
    """
    log_data = {"action": action, **kwargs}
    logger.info(f"User action: {action}", extra=log_data)


# Create default application logger
app_logger = get_logger("science_app")
