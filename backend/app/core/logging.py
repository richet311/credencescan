import logging
import sys

from app.core.config import settings


def configure_logging() -> logging.Logger:
    """Configure structured console logging so errors are visible in the terminal."""
    logger = logging.getLogger("credencescan")

    if logger.handlers:
        return logger

    level = logging.DEBUG if settings.environment == "development" else logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


logger = configure_logging()
