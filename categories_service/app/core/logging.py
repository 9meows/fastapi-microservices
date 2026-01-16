import sys
from loguru import logger

logger.remove()

logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    serialize=True,  # JSON
    level="INFO"
)

def get_logger(service_name: str):
    """Возвращает logger с привязанным именем сервиса"""
    return logger.bind(service=service_name)