"""Logging configuration for simple-otp application.

This module configures loguru for comprehensive application logging.
All logs are written to a single file that is recreated on each application start.
"""

from pathlib import Path

from loguru import logger

# Log file path in the project root directory
# __file__ is simple_otp/core/logger.py
# parent: simple_otp/core, parent.parent: simple_otp,
# parent.parent.parent: project root
LOG_FILE = Path(__file__).parent.parent.parent / "simple_otp.log"


def configure_logging():
    """
    Configure loguru for application-wide logging.

    Configuration:
    - Logs to file only (no terminal output)
    - File is recreated on each application start (previous content is lost)
    - Debug level logging for detailed information
    - Automatic exception catching with full tracebacks
    - All logs in English (no localization)
    """
    # Remove default handler (stderr output)
    logger.remove()

    # Add file handler with detailed configuration
    logger.add(
        LOG_FILE,
        # Recreate file on each start (mode="w" truncates existing file)
        mode="w",
        # Log level: DEBUG for detailed logging
        level="DEBUG",
        # Format: timestamp, level, module, function, line number, and message
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}"
        ),
        # Enable backtrace for full call stack in exceptions
        backtrace=True,
        # Enable diagnose to show variable values in tracebacks
        diagnose=True,
        # Disable colorize since we're writing to file
        colorize=False,
        # UTF-8 encoding for proper character support
        encoding="utf-8",
        # Ensure logs are written immediately
        enqueue=True,
    )

    logger.info("=" * 80)
    logger.info("Logging system initialized")
    logger.info(f"Log file: {LOG_FILE.absolute()}")
    logger.info("=" * 80)


def get_log_file_path() -> Path:
    """
    Get the path to the log file.

    Returns:
        Path: Absolute path to the log file
    """
    return LOG_FILE.absolute()


def log_exception(exception: Exception, message: str = "Exception occurred"):
    """
    Log an exception with full traceback.

    This is a convenience function for logging exceptions in try-except blocks.

    Args:
        exception: The exception to log
        message: Custom message to include with the exception

    Example:
        try:
            risky_operation()
        except Exception as e:
            log_exception(e, "Failed to perform risky operation")
    """
    logger.opt(exception=exception).error(message)


# Export logger for use throughout the application
__all__ = ["logger", "configure_logging", "get_log_file_path", "log_exception"]
