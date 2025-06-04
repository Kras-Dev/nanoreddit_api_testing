import allure
import pytest
from pydantic import ValidationError

from src.models.api_model import AdminUserResponse, BanUserResponse, UnbanUserResponse

@allure.feature("Admin Controller")
@allure.story("Admin Operations Positive")
@pytest.mark.positive
class TestAdmin:
    @allure.title("Получение информации о пользователе по ID")
    def test_get_user_profile(self, admin_user, admin_auth_token, user, admin_service, sql_client):
        """
        Тест получения информации о пользователе по ID с правами администратора.
        """
        with allure.step("Отправка запроса на получение информации о пользователе по ID (для админа)"):
            try:
                response = admin_service.get_user_profile(user.get("user_id"))
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при получении информации о пользователе: {e}")

        with allure.step("Валидация ответа информации о пользователе (для админа)"):
            try:
                validation_response = AdminUserResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа информации о пользователе (для админа): {e}")

            assert validation_response.status == "ok", "Статус ответа не 'ok'"
            assert validation_response.responseData.id == user.get("user_id"), \
                "ID пользователя в ответе не совпадает с ожидаемым"

    @allure.title("Бан пользователя по email")
    def test_ban_user_by_email(self, admin_user, admin_auth_token, user, admin_service, sql_client):
        """
        Тест блокировки пользователя по email с правами администратора.
        """
        with allure.step("Отправка запроса на бан пользователя по email"):
            try:
                response = admin_service.ban_user(user.get("email"), 40)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при бане пользователя по email: {e}")

        with allure.step("Валидация ответа на бан пользователя (для админа)"):
            try:
                validation_response = BanUserResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа на бан пользователя (для админа): {e}")

            assert validation_response.status == "ok", "Статус ответа не 'ok'"
            assert validation_response.message == "User banned", \
                f"Сообщение в ответе не соответствует ожидаемому: {validation_response.message}"
            assert sql_client.get_user_by_email(user.get("email")).banned_until is not None, \
                "Пользователь не заблокирован в базе данных"


    @allure.title("Разбан пользователя по email")
    def test_unban_user_by_email(self, admin_user, user, admin_auth_token, admin_service, sql_client):
        """
        Тест разблокировки пользователя по email с правами администратора.
        """
        with allure.step("Отправка запроса на разбан пользователя по email"):
            try:
                response = admin_service.unban_user(user.get("email"))
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при разбане пользователя по email: {e}")

            with allure.step("Валидация ответа на разбан пользователя (для админа)"):
                try:
                    validation_response = UnbanUserResponse.model_validate(response.json())
                except ValidationError as e:
                    pytest.fail(f"Ошибка валидации ответа на разбан пользователя (для админа): {e}")

            assert validation_response.status == "ok", "Статус ответа не 'ok'"
            assert validation_response.message == "User unbanned", \
                f"Сообщение в ответе не соответствует ожидаемому: {validation_response.message}"
            assert sql_client.get_user_by_email(user.get("email")).banned_until is None, \
                "Пользователь не разблокирован в базе данных"

