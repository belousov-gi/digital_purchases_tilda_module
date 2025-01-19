import logging
import logging.config
from pythonjsonlogger import jsonlogger


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(levelname)s %(module)s %(name)s %(funcName)s %(message)s ",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
        }
    },
    "loggers": {
        "": {"handlers": ["stdout"], "level": "DEBUG", "encoding": "utf-8"},
        "app.api.endpoints.auth": {"handlers": ["stdout"], "level": "DEBUG", "propagate": False, "encoding": "utf-8"},
        "app.services.email.email_sendler_service": {"handlers": ["stdout"], "level": "ERROR", "propagate": False, "encoding": "utf-8"},
        "sqlalchemy.engine": {"handlers": ["stdout"], "level": "ERROR", "propagate": False, "encoding": "utf-8"},
        "app.repositories.db_repo": {"handlers": ["stdout"], "level": "DEBUG", "propagate": False, "encoding": "utf-8"}
        }
}


logging.config.dictConfig(LOGGING)