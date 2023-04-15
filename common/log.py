import logging
import os

DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.environ.get("LOG_LEVEL")
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

FORMAT = "{asctime} | {levelname} | {funcName} | {message}"


def setup_logs():
    log_level = LOG_LEVEL.upper() if LOG_LEVEL else None
    invalid = False
    if log_level not in VALID_LOG_LEVELS:
        log_level = DEFAULT_LOG_LEVEL
        invalid = True

    logging.basicConfig(level=log_level, format=FORMAT, style="{")
    if invalid:
        logging.warn(
            f"Invalid or missing LOG_LEVEL supplied: '{LOG_LEVEL}'. "
            f"Defaulting to '{log_level}'"
        )
