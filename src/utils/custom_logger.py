import inspect
import logging


class CustomLogger:
    def __init__(self, name:str) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(name)

    def log_with_context(self, message: str) -> None:
        stack = inspect.stack()
        caller_function = stack[1].function
        self.logger.info(f"{message} (called from {caller_function})")
