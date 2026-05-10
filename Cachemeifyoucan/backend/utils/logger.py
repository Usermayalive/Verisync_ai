import logging
import sys
import json
import os
from datetime import datetime
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.get_message() if hasattr(record, "get_message") else record.getMessage(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)
def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    return logger
