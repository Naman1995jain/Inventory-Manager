import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root and uvicorn loggers to write to a rotating file handler.

    This function is idempotent and can be called multiple times safely.
    """
    root_logger = logging.getLogger()
    # Avoid adding multiple handlers if already configured
    if any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == str(LOG_FILE) for h in root_logger.handlers):
        return

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = RotatingFileHandler(
        filename=str(LOG_FILE),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Stream handler for console (optional) - keep at WARNING to reduce duplicate info
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    # Also configure uvicorn loggers if present
    for uv_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(uv_logger_name)
        uv_logger.setLevel(level)
        # avoid duplicate handlers
        if not any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == str(LOG_FILE) for h in uv_logger.handlers):
            uv_logger.addHandler(file_handler)
