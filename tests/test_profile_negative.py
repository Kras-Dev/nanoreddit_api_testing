import allure
import pytest
from pydantic import ValidationError

from src.models.api_model import ApiResponse


@allure.feature("User Profile")
@allure.story("Profile Info Negative")
@pytest.mark.negative
class TestProfileNegative:
    @allure.title("Получение профиля без авторизации")
    def test_get_profile_no_auth(self, profile_controller):
        """
        Тест получение информации о профиле без авторизации.
        """
        with allure.step("Отправка запроса на получение информации о профиле без авторизации"):
            try:
                response = profile_controller.get_profile_info()
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при получении профиля без авторизации: {e}")

        with allure.step("Валидация ответа API"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа при получении профиля без авторизации: {e}")

            assert validation_response.status == "error", \
                f"Ожидался статус 'error', получен '{validation_response.status}'"
            assert validation_response.error == "Access denied", \
                f"Ожидалось сообщение 'Access denied', получено '{validation_response.error}'"