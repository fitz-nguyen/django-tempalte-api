import os

# Logging
BASE_LOG_DIR = "logs"
LOG_FILE_PATH = os.path.join(BASE_LOG_DIR, "logs.log")
LOG_LEVEL = os.environ.get("LOG_LEVEL", default="ERROR")

# LOG STASH
IP_LOGSTASH = os.environ.get("IP_LOGSTASH", default="127.0.0.1")
PORT_LOGSTASH = int(os.environ.get("PORT_LOGSTASH", default=5959))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s"},
        "simple": {"format": "%(levelname)s\t%(asctime)s\t%(filename)s\t%(lineno)d\t%(message)s"},
    },
    "root": {"level": "ERROR", "handlers": ["console", "logstash"]},
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "when": "D",
            "encoding": "utf-8",
            "formatter": "simple",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "logstash": {
            "level": "ERROR",
            "class": "logstash.TCPLogstashHandler",
            "host": IP_LOGSTASH,  # IP/name of our Logstash EC2 instance
            "port": PORT_LOGSTASH,
            "version": 1,
            "message_type": "django",
            "fqdn": False,
            "tags": ["django"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "default", "logstash"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },
    },
}
