from typing import Any, Dict

import pytest
from faker import Faker

from src.models.api_model import LoginRequest, RegistrationRequest

fake = Faker()

def register_user(clients) -> Dict[str, Any]:
    """Регистрирует пользователя и проверяет его в базе, возвращает данные и пароль."""
    password = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True)
    reg_data = RegistrationRequest(
        email=fake.email(),
        username=fake.user_name(),
        password=password,
        passwordConfirmation=password
    )
    validation_response = clients.auth.register(reg_data)

    assert validation_response.responseData is not None, "Отсутствуют данные регистрации"

    user = clients.db.get_user_by_email(reg_data.email)
    assert user is not None, "Пользователь не найден в базе после регистрации"

    return {
        "email": reg_data.email,
        "username": reg_data.username,
        "password": password,
        "user_id": user.id,
    }

def login_user(clients, email: str, password: str) -> str:
    """Выполняет логин пользователя."""
    login_data = LoginRequest(email=email, password=password)
    validation_response = clients.auth.login(login_data)

    assert validation_response.responseData is not None, "responseData отсутствует"
    token = validation_response.responseData.get("jwt")
    assert token, "JWT токен отсутствует в ответе логина"

    return token

@pytest.fixture(scope="module")
def user(clients):
    """Создает пользователя и осуществляет вход."""
    user_data = register_user(clients)
    token = login_user(clients, user_data["email"], user_data["password"])
    user_data["token"] = token

    yield user_data
    clients.db.clear_user_data(user_data["user_id"])

@pytest.fixture(scope="function")
def user_auth_token(clients, user):
    """Устанавливает токен обычного пользователя в http_client перед тестом и очищает после."""
    clients.api.set_token(user["token"])
    yield
    clients.api.clear_token()

@pytest.fixture(scope="module")
def admin_user(clients):
    """Создает администратора и осуществляет вход."""
    user_data = register_user(clients)
    clients.db.set_admin_role(user_data["user_id"])
    user = clients.db.get_user_by_email(user_data["email"])
    assert user.role == "ADMIN", f"Ожидалась роль ADMIN, но получена {user.role}"
    token = login_user(clients, user_data["email"], user_data["password"])
    user_data["token"] = token

    yield user_data
    clients.db.clear_user_data(user_data["user_id"])

@pytest.fixture(scope="function")
def admin_auth_token(clients, admin_user):
    """Устанавливает токен администратора в http_client перед тестом и очищает после."""
    clients.api.set_token(admin_user["token"])
    yield
    clients.api.clear_token()