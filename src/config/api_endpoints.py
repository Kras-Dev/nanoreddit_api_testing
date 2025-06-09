import os

from dotenv import load_dotenv

load_dotenv()

class ApiEndpoints:
    """Класс, содержащий базовый URL и пути к основным API-эндпоинтам сервера.

    Загружает параметры из переменных окружения, определенных в `.env` файле.
    """

    BASE_URL = os.getenv("BASE_URL")
    AUTH_REGISTER = os.getenv("AUTH_REGISTER")
    AUTH_LOGIN = os.getenv("AUTH_LOGIN")
    POSTS = os.getenv("POSTS")
    POST = os.getenv("POST")
    POST_VOTE = os.getenv("POST_VOTE")
    POST_ADD_COMMENT = os.getenv("POST_ADD_COMMENT")
    POST_PUBLISH = os.getenv("POST_PUBLISH")
    PROFILE_INFO = os.getenv("PROFILE_INFO")
    ADMIN_PROFILE_INFO = os.getenv("ADMIN_PROFILE_INFO")
    ADMIN_BAN_USER = os.getenv("ADMIN_BAN_USER")
    ADMIN_UNBAN_USER = os.getenv("ADMIN_UNBAN_USER")
    COMMENT_REPLY = os.getenv("COMMENT_REPLY")