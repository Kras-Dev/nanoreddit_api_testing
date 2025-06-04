import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import ApiResponse

fake = Faker()

@pytest.fixture(scope="module")
def test_data():
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
class TestAuth:
    @allure.title("Успешная регистрация")
    def test_register_user(self, auth_service, sql_client, test_data):
        """
        Тест регистрации нового пользователя.
        Проверяет успешный ответ API и наличие пользователя в базе.
        """
        with allure.step("Отправка запроса на регистрацию пользователя"):
            try:
                response = auth_service.register(test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при регистрации пользователя: {e}")

        with allure.step("Валидация ответа API"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа API при регистрации: {e}")

            assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"

        with allure.step("Проверка наличия пользователя в базе данных"):
            assert sql_client.get_user_by_email(test_data["email"]) is not None, \
                "Пользователь не найден в базе после регистрации"

    @allure.title("Успешная авторизация")
    def test_auth_user(self, auth_service, test_data):
        """
        Тест авторизации существующего пользователя.
        Проверяет успешный ответ API и наличие JWT токена в ответе.
        """
        auth_data = {
            "email": test_data["email"],
            "password": test_data["password"],
        }
        with allure.step("Отправка запроса на авторизацию пользователя"):
            try:
                response = auth_service.login(auth_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при авторизации пользователя: {e}")

        with allure.step("Валидация ответа API"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа API при авторизации: {e}")

            assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"
            assert "jwt" in validation_response.responseData and validation_response.responseData[
                    "jwt"], "JWT токен отсутствует в ответе логина"





