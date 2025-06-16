import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import LoginRequest, RegistrationRequest

fake = Faker()

@pytest.fixture(scope="module")
def test_data():
    """Фикстура с базовыми данными для регистрации пользователя."""
    password = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True)
    return {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": password,
        "passwordConfirmation": password,
    }

@allure.feature("Authentication")
@allure.story("User Registration and Authentication Negative")
@pytest.mark.negative
@pytest.mark.auth
class TestAuthNegative:
    @allure.title("Регистрация с несовпадающими паролями")
    def test_register_password_mismatch(self, clients, test_data):
        """Тест регистрации с несовпадающими паролями."""
        test_data = {**test_data, "passwordConfirmation": fake.password()}

        with pytest.raises(ValidationError) as exc_info:
            clients.auth.register(RegistrationRequest(**test_data))
        assert 'Should be the same as password' in str(exc_info.value), "Ошибка валидации пароля"

    @allure.title("Регистрация с некорректными паролями")
    @pytest.mark.parametrize("invalid_password",[
        fake.password(length=7, special_chars=False, digits=True, upper_case=False, lower_case=False),
        fake.password(length=8, special_chars=True, digits=False, upper_case=False, lower_case=False),
        fake.password(length=8, special_chars=True, digits=True, upper_case=False, lower_case=False),
        fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=False),
        fake.bothify("??## ??##"),
    ])
    def test_register_incorrect_password(self, clients, test_data, invalid_password):
        """Тест регистрации с различными некорректными паролями."""
        test_data = {**test_data, "password": invalid_password, "passwordConfirmation": invalid_password}

        with pytest.raises(ValidationError, match=r"Password | least 8 characters "):
            clients.auth.register(RegistrationRequest(**test_data))

    @allure.title("Регистрация с уже существующим email")
    def test_register_email_exist(self, clients, user, test_data):
        """Тест регистрации пользователя с email, который уже существует в системе."""
        test_data = {**test_data, "email": user.get("email")}
        reg_data = RegistrationRequest(**test_data)

        validation_response = clients.auth.register(reg_data)

        assert "Username or Email already in use!" in validation_response.error, \
        f"Ожидалось сообщение об ошибке 'Username or Email already in use!', получено '{validation_response.error}'"

    allure.title("Авторизация с некорректными данными")
    def test_auth_invalid_credentials(self, clients, test_data):
        """Тест авторизации с некорректными учетными данными."""
        test_data = {**test_data, "email": fake.email()}
        auth_data = LoginRequest(email=test_data["email"], password=test_data["password"])

        validation_response = clients.auth.login(auth_data)

        assert "Bad credentials" in validation_response.error, \
            f"Ожидалось сообщение об ошибке 'Bad credentials', получено '{validation_response.error}'"

