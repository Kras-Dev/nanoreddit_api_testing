from typing import Optional, Callable, Any
from sqlalchemy import text
from src.models.sqlalchemy_model import Base, Post, Comment, Vote
from src.clients.sql_client.sqlalchemy_connection import SQLAlchemyConnection
from src.models.sqlalchemy_model import User
from src.utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)

class SqlAlchemyClient:
    """ Клиент для взаимодействия с базой данных через SQLAlchemy."""
    def __init__(self) -> None:
        """
        Инициализация клиента с соединением с базой данных.
        """
        self.connection = SQLAlchemyConnection()
        self.connection.connect()
        self.metadata = Base.metadata

    def _execute_db_operation(self, operation: Callable[[Any], Any]) -> Optional[Any]:
        """
        Универсальный метод для выполнения операций с базой данных.
        """
        try:
            with self.connection.get_session() as session:
                result = operation(session)
                session.commit()
                return result
        except Exception as e:
            custom_logger.log_with_context(f"Ошибка при работе с базой: {e}")
            return None

    def set_admin_role(self, user_id: int) -> bool:
        """
        Установить роль ADMIN пользователю по user_id.
        """
        def operation(session):
            user = session.query(User).filter_by(id=user_id).one_or_none()
            if not user:
                custom_logger.log_with_context("Пользователь не найден")
                return False
            user.role = "ADMIN"
            return True
        result = self._execute_db_operation(operation)
        return bool(result)

    def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя по user_id.
        """
        def operation(session):
            user = session.query(User).filter_by(id=user_id).one_or_none()
            if not user:
                custom_logger.log_with_context("Пользователь не найден.")
                return False
            session.delete(user)
            return True

        result = self._execute_db_operation(operation)
        return bool(result)

    def get_user_by_email(self, user_email: str) -> Optional[User]:
        """
        Получить пользователя по email.
        """
        def operation(session):
            return session.query(User).filter_by(email=user_email).one_or_none()
        return self._execute_db_operation(operation)

    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        """
        Получить пост по id.
        """
        def operation(session):
            return session.query(Post).filter_by(id=post_id).one_or_none()
        return self._execute_db_operation(operation)

    def delete_post_by_author_id(self, author_id: int) -> bool:
        """
        Удалить пост по post_id.
        """
        def operation(session):
            posts = session.query(Post).filter_by(author_id=author_id).all()
            if not posts:
                return False
            for post in posts:
                session.delete(post)
            return True

        result = self._execute_db_operation(operation)
        return bool(result)

    def get_comment_by_post_id(self, post_id: str) -> Optional[Comment]:
        """
        Получить комментарий по post_id.
        """
        def operation(session):
            return session.query(Comment).filter_by(post_id=post_id).one_or_none()
        return self._execute_db_operation(operation)

    def get_comment_by_id(self, comment_id: str) -> Optional[Comment]:
        """
        Получить комментарий по id.
        """
        def operation(session):
            return session.query(Comment).filter_by(id=comment_id).one_or_none()
        return self._execute_db_operation(operation)

    def delete_comments_by_author_id(self, author_id: int) -> bool:
        """
        Удалить все комментарии пользователя по author_id.
        """
        def operation(session):
            comments = session.query(Comment).filter_by(author_id=author_id).all()
            if not comments:
                return False
            for comment in comments:
                session.delete(comment)
            return True

        result = self._execute_db_operation(operation)
        return bool(result)

    def get_post_vote_value(self, post_id: str) -> Optional[int]:
        """
        Получить количество голосов за пост
        """
        def operation(session):
            vote = session.query(Vote).filter_by(post_id=post_id).first()
            if vote is None:
                return None
            return vote.value

        result = self._execute_db_operation(operation)
        return result

    def delete_votes_by_user_id(self, user_id: int) -> bool:
        """
        Удалить голоса за посты по user_id.
        """
        def operation(session):
            votes = session.query(Vote).filter_by(user_id=user_id).all()
            if not votes:
                return False
            for vote in votes:
                session.delete(vote)
            return True

        result = self._execute_db_operation(operation)
        return bool(result)

    def clear_user_data(self, user_id: int):
        """
        Очищает все данные созданные пользователем и удаляет его.
        """
        self.delete_votes_by_user_id(user_id)
        self.delete_comments_by_author_id(user_id)
        self.delete_post_by_author_id(user_id)
        self.delete_user(user_id)

    def clear_all_tables(self) -> None:
        """
        Очищает все данные из всех таблиц в базе данных.
        """
        def operation(session):
            for table in reversed(self.metadata.sorted_tables):
                session.execute(table.delete())
            custom_logger.log_with_context("Все данные успешно очищены из таблиц.")
            session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
        self._execute_db_operation(operation)

    def disconnect(self) -> None:
        """
        Закрыть соединение с базой.
        """
        self.connection.disconnect()