import structlog
from structlog import DropEvent
import logging.config
from pydantic import ValidationError
import socket
from .models import LogModel
from configs.log_conf import LOGGING_CONFIG


error_logger = logging.getLogger("my.custom.error")


def pydantic_processor(logger, method_name, event_dict):
    try:
        LogModel(**event_dict)
    except ValidationError as e:
        error_logger.error(e)
        # raise DropEvent
        raise

    event_dict.setdefault("client_ip", socket.gethostbyname(socket.gethostname()))

    return event_dict


def configure_logger():
    logging.config.dictConfig(LOGGING_CONFIG)

    structlog.configure(
        processors=[
            pydantic_processor,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )


configure_logger()
