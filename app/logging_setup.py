import json
import logging
import time
import uuid
from logging.handlers import RotatingFileHandler

from fastapi import Request


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log)


logger = logging.getLogger("ampla_api")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = RotatingFileHandler(
        "ampla_api.log", maxBytes=5_000_000, backupCount=3  # 5 MB
    )
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000

    logger.info(
        json.dumps(
            {
                "req": request.state.request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration, 1),
            }
        )
    )
    return response


def log_invalid_xml(endpoint: str, request: Request):
    logger.warning(
        json.dumps(
            {
                "req": request.state.request_id,
                "endpoint": endpoint,
                "error": "Invalid XML",
            }
        )
    )
