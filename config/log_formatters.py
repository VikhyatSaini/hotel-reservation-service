import json
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event"):
            log_data["event"] = record.event

        if hasattr(record, "room_id"):
            log_data["room_id"] = record.room_id

        if hasattr(record, "reservation_reference"):
            log_data["reservation_reference"] = record.reservation_reference

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)