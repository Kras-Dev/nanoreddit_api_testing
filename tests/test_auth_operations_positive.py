import allure
import pytest
from faker import Faker

from src.models.api_model import LoginRequest, RegistrationRequest

fake = Faker()

@pytest.fixture(scope="module")
def test_data():
    """Генерирует тестовые данные для регистрации и аутентификации пользователя."""
    password = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True)
    return {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": password,
        "passwordConfirmation": password,
    }

@allure.feature("Authentication")
@allure.story("User Registration and Authentication")
@pytest.mark.positive
@pytest.mark.auth
class TestAuth:
    @allure.title("Успешная регистрация")
    def test_register_user(self, clients, test_data):
        """Тест регистрации нового пользователя.

        Проверяет наличие пользователя в базе.
        """
        test_data = RegistrationRequest(**test_data)

        clients.auth.register(test_data)

        with allure.step("Проверка наличия пользователя в базе данных"):
            assert clients.db.get_user_by_email(test_data.email) is not None, \
                    "Пользователь не найден в базе после регистрации"

    @allure.title("Успешная авторизация")
    def test_auth_user(self, clients, test_data):
        """Тест авторизации существующего пользователя."""
        test_data = LoginRequest(email=test_data["email"], password=test_data["password"])

        validation_response = clients.auth.login(test_data)

        assert "jwt" in validation_response.responseData and validation_response.responseData[
                "jwt"], "JWT токен отсутствует в ответе логина"






