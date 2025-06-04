from typing import Dict, Any

import pytest
from faker import Faker
from pydantic import ValidationError

from src.clients.http_client.admin_controller import AdminService
from src.clients.http_client.auth_controller import AuthService
from src.clients.http_client.base_client import BaseClient
from src.clients.http_client.comments_controller import CommentsService
from src.clients.http_client.post_controller import PostsService
from src.clients.http_client.profile_controller import ProfileService
from src.clients.sql_client.sqlalchemy_client import SqlAlchemyClient
from src.models.api_model import ApiResponse, PublishRequest, PostPublishResponse

from src.utils.custom_logger import CustomLogger
custom_logger = CustomLogger(__name__)
fake = Faker()

@pytest.fixture(scope="session")
def sql_client():
    """Создает клиент для работы с базой данных."""
    sql_client = SqlAlchemyClient()

    yield sql_client
    sql_client.clear_all_tables()
    sql_client.disconnect()

@pytest.fixture(scope="session")
def http_client():
    """Создает HTTP клиент для работы с API."""
    http_client = BaseClient()

    yield http_client
    http_client.close_session()

@pytest.fixture(scope="module")
def profile_service(http_client):
    """Создает клиент профиля."""
    return ProfileService(http_client)

@pytest.fixture(scope="module")
def auth_service(http_client):
    """Создает клиент аутентификации."""
    return AuthService(http_client)

def register_user(auth_client, sql_client) -> Dict[str, Any]:
    """Регистрирует пользователя и проверяет его в базе, возвращает данные и пароль."""
    password = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True)

    reg_data = {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": password,
        "passwordConfirmation": password,
    }
    reg_response = None
    try:
        reg_response = auth_client.register(reg_data)
        reg_response.raise_for_status()
    except Exception as e:
        pytest.fail(f"Ошибка при регистрации пользователя: {e}")

    try:
        validation_response = ApiResponse.model_validate(reg_response.json())
        assert validation_response.status == "ok", f"Регистрация не удалась: {reg_response.json()}"
        assert validation_response.responseData is not None, "Отсутствуют данные регистрации"
    except ValidationError as e:
        pytest.fail(f"Ошибка валидации ответа API при регистрации: {e}")

    user = sql_client.get_user_by_email(reg_data["email"])
    assert user is not None, "Пользователь не найден в базе после регистрации"

    return {
        "email": reg_data["email"],
        "username": reg_data["username"],
        "password": password,
        "user_id": user.id,
    }

def login_user(auth_client, email: str, password: str) -> str:
    """Выполняет логин пользователя"""
    login_response = None
    try:
        login_response = auth_client.login({"email": email, "password": password})
        login_response.raise_for_status()
    except Exception as e:
        pytest.fail(f"Ошибка при авторизации пользователя: {e}")
    validated_login = None
    try:
        validated_login = ApiResponse.model_validate(login_response.json())
        assert validated_login.status == "ok", f"Логин не удался: {login_response.json()}"
        assert validated_login.responseData is not None, "responseData отсутствует"
        assert "jwt" in validated_login.responseData and validated_login.responseData["jwt"], "JWT токен отсутствует в ответе логина"
    except (ValidationError, AssertionError) as e:
        pytest.fail(f"Ответ логина не соответствует модели: {e}")
    return validated_login.responseData["jwt"]

@pytest.fixture(scope="module")
def user(auth_service, sql_client):
    """Создает пользователя и осуществляет вход."""
    user_data = register_user(auth_service, sql_client)
    token = login_user(auth_service, user_data["email"], user_data["password"])
    user_data["token"] = token

    yield user_data
    sql_client.clear_user_data(user_data["user_id"])

@pytest.fixture(scope="function")
def user_auth_token(http_client, user):
    """Устанавливает токен обычного пользователя в http_client перед тестом и очищает после."""
    http_client.set_token(user["token"])
    yield
    http_client.clear_token()

@pytest.fixture(scope="module")
def admin_user(auth_service, sql_client):
    """Создает администратора и осуществляет вход."""
    user_data = register_user(auth_service, sql_client)
    sql_client.set_admin_role(user_data["user_id"])
    user = sql_client.get_user_by_email(user_data["email"])
    assert user.role == "ADMIN", f"Ожидалась роль ADMIN, но получена {user.role}"
    token = login_user(auth_service, user_data["email"], user_data["password"])
    user_data["token"] = token

    yield user_data
    sql_client.clear_user_data(user_data["user_id"])

@pytest.fixture(scope="function")
def admin_auth_token(http_client, admin_user):
    """Устанавливает токен администратора в http_client перед тестом и очищает после."""
    http_client.set_token(admin_user["token"])
    yield
    http_client.clear_token()

@pytest.fixture(scope="module")
def admin_service(http_client):
    """Создает клиент администратора (токен устанавливается через фикстуру admin_auth_token)."""
    yield AdminService(http_client)

@pytest.fixture(scope="module")
def posts_service(http_client):
    """Создает клиент постов."""
    return PostsService(http_client)

@pytest.fixture(scope="class")
def publish_post(user, sql_client, posts_service):
    """Создает пост от имени авторизованного пользователя."""
    test_data = {
        "title": fake.text(10),
        "content": fake.text(25)
    }
    response = None
    try:
        response = posts_service.publish_post(PublishRequest.model_validate(test_data).model_dump())
        response.raise_for_status()
    except Exception as e:
        pytest.fail(f"Ошибка при создании поста {e}")

    validation_response = None
    try:
        validation_response = PostPublishResponse.model_validate(response.json())
    except ValidationError as e:
        pytest.fail(f"Ошибка валидации ответа API при создании поста: {e}")

    post_id = validation_response.responseData.id
    db_post = sql_client.get_post_by_id(str(post_id))
    assert db_post is not None, "Пост не найден в базе после создания"

    yield str(post_id)

@pytest.fixture(scope="module")
def comments_service(http_client):
    """Создает клиент комментариев."""
    return CommentsService(http_client)

@pytest.fixture(scope="class")
def add_comment(user, publish_post, sql_client, posts_service):
    """Создает комментарий к посту от имени авторизованного пользователя."""
    test_data = fake.text(15)
    try:
        response = posts_service.add_comment(publish_post, test_data)
        response.raise_for_status()
    except Exception as e:
        pytest.fail(f"Ошибка при создании комментария {e}")

    db_comment = sql_client.get_comment_by_post_id(publish_post)
    assert db_comment is not None, "Комментарий не найден в базе после создания"
    comment_id = db_comment.id

    yield str(comment_id)
