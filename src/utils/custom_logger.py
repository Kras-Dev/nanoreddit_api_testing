import inspect
import logging


class CustomLogger:
    """Класс для логирования сообщений с указанием контекста вызова (имени вызывающей функции)."""

    def __init__(self, name:str) -> None:
        """Инициализация логгера с заданным именем."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(name)

    def log_with_context(self, message: str) -> None:
        """Логирует сообщение с указанием имени функции, из которой был вызов."""
        stack = inspect.stack()
        caller_function = stack[1].function
        self.logger.info(f"{message} (called from {caller_function})")
