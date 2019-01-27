from logging import DEBUG, Formatter, Logger, getLogger
from logging.handlers import RotatingFileHandler

from gardnr import settings


def enable_debugging() -> None:
    settings.LOG_LEVEL = DEBUG


def get_logger() -> Logger:
    return getLogger('gardnr')


def setup() -> None:
    file_rotation = RotatingFileHandler(settings.LOG_FILE,
                                        maxBytes=settings.LOG_FILE_SIZE,
                                        backupCount=settings.LOG_FILE_COUNT)
    formatter = Formatter(fmt='%(asctime)s - %(levelname)s - '
                          '%(module)s - %(message)s')

    file_rotation.setFormatter(formatter)

    logger = get_logger()
    logger.setLevel(settings.LOG_LEVEL)
    logger.addHandler(file_rotation)


def debug(msg: str) -> None:
    get_logger().debug(msg)


def info(msg: str) -> None:
    get_logger().info(msg)


def warning(msg: str) -> None:
    get_logger().warning(msg)


def error(msg: str) -> None:
    get_logger().error(msg)


def critical(msg: str) -> None:
    get_logger().critical(msg)


def exception(msg: str) -> None:
    get_logger().exception(msg)
