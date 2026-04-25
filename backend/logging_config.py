"""Structured JSON logging tuned for Railway's log explorer.

Railway parses single-line JSON on stdout and color-codes by the
`level` field. Without this, Python's default logging goes to stderr
and shows up entirely red.
"""

import contextvars
import logging
import sys

from pythonjsonlogger.json import JsonFormatter

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


class RailwayJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["level"] = record.levelname.lower()
        rid = request_id_var.get()
        if rid is not None:
            log_record["request_id"] = rid


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RailwayJsonFormatter("{message}", style="{"))
    logging.basicConfig(handlers=[handler], level=level, force=True)

    # Silence noisy loggers — we'll log one line per request from middleware.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
