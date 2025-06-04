import allure
import pytest
from pydantic import ValidationError

from src.models.api_model import ProfileResponse


@allure.feature("User Profile")
@allure.story("Profile Info Positive")
@pytest.mark.positive
class TestProfile:
    @allure.title("Получение профиля пользователя")
    def test_profile(self, user, profile_service, sql_client):
        """
        Тест на получение профиля текущего пользователя.
        """
        with allure.step("Отправка запроса на получение профиля пользователя"):
            try:
                response = profile_service.get_profile_info()
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при получении профиля пользователя: {e}")

        with allure.step("Валидация ответа API"):
            try:
                validation_response = ProfileResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа при получении профиля пользователя: {e}")

            assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"
            assert validation_response.responseData.email == user.get("email")
            assert validation_response.responseData.username == user.get("email")

        with allure.step("Проверка наличия пользователя в базе данных"):
            db_user = sql_client.get_user_by_email(user["email"])
            assert db_user is not None, "Пользователь не найден в базе"
            assert db_user.id == user.get("user_id")


