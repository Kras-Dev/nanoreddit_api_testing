import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import ApiResponse, RegistrationRequest

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
class TestAuthNegative:
    @allure.title("Регистрация с несовпадающими паролями")
    def test_register_password_mismatch(self, auth_service, test_data):
        """
        Тест регистрации с несовпадающими паролями.
        """
        test_data = {**test_data, "passwordConfirmation": fake.password()}
        with allure.step("Отправка запроса на регистрацию с несовпадающими паролями"):
            with pytest.raises(ValidationError) as exc_info:
                RegistrationRequest(**test_data)
            assert 'Should be the same as password' in str(exc_info.value), "Ошибка валидации пароля"

    @allure.title("Регистрация с некорректными паролями")
    @pytest.mark.parametrize("invalid_password",[
        fake.password(length=7, special_chars=False, digits=True, upper_case=False, lower_case=False),
        fake.password(length=8, special_chars=True, digits=False, upper_case=False, lower_case=False),
        fake.password(length=8, special_chars=True, digits=True, upper_case=False, lower_case=False),
        fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=False),
        fake.bothify("??## ??##"),
    ])
    def test_register_incorrect_password(self, auth_service, test_data, invalid_password):
        """
        Тест регистрации с различными некорректными паролями.
        """
        test_data = {**test_data, "password": invalid_password, "passwordConfirmation": invalid_password}

        with allure.step(f"Отправка запроса регистрации с паролем: {invalid_password}"):
            with pytest.raises(ValidationError, match=r"Password | least 8 characters "):
                RegistrationRequest(**test_data)

    allure.title("Регистрация с уже существующим email")
    def test_register_email_exist(self, auth_service, user, test_data):
        """
        Тест регистрации пользователя с email, который уже существует в системе.
        """
        test_data = {**test_data, "email": user.get("email")}
        with allure.step("Отправка запроса на регистрацию с уже зарегистрированным email"):
            try:
                response = auth_service.register(test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при регистрации пользователя с уже зарегистрированным email: {e}")

            with allure.step("Валидация ответа API"):
                try:
                    validation_response = ApiResponse.model_validate(response.json())
                except ValidationError as e:
                    pytest.fail(f"Ошибка валидации ответа API при регистрации с существующим email: {e}")

            assert validation_response.status == "error", \
                f"Ожидался статус 'error', получен '{validation_response.status}'"
            assert validation_response.error == "Username or Email already in use!", \
                f"Ожидалось сообщение об ошибке 'Username or Email already in use!', получено '{validation_response.error}'"

    allure.title("Авторизация с некорректными данными")
    def test_auth_invalid_credentials(self, auth_service, test_data):
        """Тест авторизации с некорректными учетными данными."""
        test_data = {**test_data, "email": fake.email()}
        with allure.step("Отправка запроса авторизации с неверными данными"):
            try:
                response = auth_service.login(test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при попытке авторизации с некорректными данными: {e}")

            with allure.step("Валидация ответа API"):
                try:
                    validation_response = ApiResponse.model_validate(response.json())
                except ValidationError as e:
                    pytest.fail(f"Ошибка валидации ответа API при авторизации с некорректными данными: {e}")

                assert validation_response.status == "error",  \
                    f"Ожидался статус 'error', получен '{validation_response.status}'"
                assert validation_response.error == "Bad credentials", \
                    f"Ожидалось сообщение об ошибке 'Bad credentials', получено '{validation_response.error}'"

