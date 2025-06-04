import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import ApiResponse

fake = Faker()

@allure.feature("Admin Controller")
@allure.story("Admin Operations Negative")
@pytest.mark.negative
class TestAdminNegative:
    @allure.title("Проверка запрета доступа к профилю пользователя без прав администратора")
    def test_get_user_profile_no_admin(self, user_auth_token, admin_service, user):
        """
        Тест обычный пользователь не может получить профиль через админский эндпоинт.
        """
        with allure.step("Отправка запроса на получение информации о пользователе по ID без прав администратора"):
            response = admin_service.get_user_profile(user.get("user_id"))
            assert response.status_code == 403, f"Ожидался статус 403, получен {response.status_code}"

            with allure.step("Валидация ответа API"):
                try:
                    validation_response = ApiResponse.model_validate(response.json())
                except ValidationError as e:
                    pytest.fail(f"{e}")

            assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
            assert validation_response.error == "Access denied", "Ожидалось сообщение 'Access denied'"

    @allure.title("Получение профиля пользователя с невалидным ID")
    def test_get_user_profile_invalid_id(self, admin_user, admin_service):
        """
        Тест получения профиля пользователя с невалидным ID.
        """
        user_id = fake.random_number(digits=3)
        with allure.step(f"Отправка запроса на получение информации о пользователе с ID {user_id}"):
            try:
                response = admin_service.get_user_profile(user_id)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при запросе профиля пользователя: {e}")

        with allure.step("Валидация ответа API"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа API: {e}")

            assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
            assert validation_response.error == f"User not found with id: {user_id}", \
                f"Ожидалось сообщение об ошибке для ID {user_id}"

    @allure.title("Попытка забанить пользователя с несуществующим email")
    def test_ban_user_invalid_email(self, admin_user, admin_service):
        """
        Тест блокировки пользователя с несуществующим email.
        """
        email = fake.email()
        with allure.step(f"Отправка запроса на бан пользователя с email {email}"):
            try:
                response = admin_service.ban_user(email,  40)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при бане пользователя: {e}")

        with allure.step("Валидация ответа API"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа API: {e}")

            assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
            assert validation_response.error == f"User not found with email: {email}", \
                f"Ожидалось сообщение об ошибке для email {email}"
