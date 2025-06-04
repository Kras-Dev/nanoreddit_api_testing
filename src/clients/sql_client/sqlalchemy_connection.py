from typing import Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from src.config.db_config import DataBaseConfig
from src.utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)

class SQLAlchemyConnection:
    """Класс для управления соединением с базой данных PostgresSQL с использованием SQLAlchemy.
    """
    def __init__(self) -> None:
        """Инициализация класса и создание движка базы данных.

            Создаем движок базы данных.\n
            Создаем фабрику сессий.\n
            Используем фабрику для создания новой сессии.
        """
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None

    def connect(self) -> None:
        """Устанавливает соединение с базой данных, создавая движок и фабрику сессий"""

        """
        pool_size (int): Максимальное количество соединений, которые пул будет поддерживать открытыми.
        max_overflow (int): Максимальное количество соединений, которое пул может создать сверх pool_size. 
                           Если это значение равно 0, пул не будет переполняться.
        pool_recycle (int): Количество секунд, после которых соединение будет переработано. Это полезно для 
                           баз данных, которые отключают соединения после определенного периода бездействия.
        """
        try:
            DataBaseConfig.validate()
            self.engine = create_engine(DataBaseConfig.DB_URL, pool_size=5, max_overflow=0, pool_recycle=3600)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False)
        except SQLAlchemyError as e:
            custom_logger.log_with_context(f"Error creating database engine: {e}")
            raise

    def get_session(self) -> Session:
        """Создает новую сессию для взаимодействия с базой данных."""
        if self.SessionLocal is None:
            raise Exception("SessionLocal is not initialized. Call connect() first.")
        session = self.SessionLocal()
        return session

    def disconnect(self) -> None:
        """Закрывает движок базы данных и освобождает ресурсы.
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.SessionLocal = None
