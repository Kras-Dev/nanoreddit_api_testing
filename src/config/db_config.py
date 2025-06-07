import os

from dotenv import load_dotenv

load_dotenv()

class DataBaseConfig:
    """
     Класс для хранения конфигурационных данных базы данных.
     Загружает параметры подключения к базе данных из переменных окружения,
     определенных в `.env` файле
     """
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")
    DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    @classmethod
    def validate(cls) -> None:
        """
        Проверяет наличие всех обязательных переменных окружения для подключения к базе данных.
        """
        required_vars = [cls.DB_HOST, cls.DB_PORT, cls.DB_USER, cls.DB_PASS, cls.DB_NAME]
        if any(var is None for var in required_vars):
            raise ValueError(
                "All database configuration variables (DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME) must"
                " be set in the environment variables.")