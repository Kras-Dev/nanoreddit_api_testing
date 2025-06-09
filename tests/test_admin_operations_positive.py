import allure
import pytest


@allure.feature("Admin Controller")
@allure.story("Admin Operations Positive")
@pytest.mark.positive
@pytest.mark.admin
class TestAdmin:
    @allure.title("Получение информации о пользователе по ID")
    def test_get_user_profile(self, clients, admin_user, admin_auth_token, user):
        """Тест получения информации о пользователе по ID с правами администратора."""
        validation_response = clients.admin.get_user_profile(user.get("user_id"))

        assert validation_response.status == "ok", "Статус ответа не 'ok'"
        assert validation_response.responseData.id == user.get("user_id"), \
        "ID пользователя в ответе не совпадает с ожидаемым"

    @allure.title("Бан пользователя по email")
    def test_ban_user_by_email(self, clients,admin_user, admin_auth_token, user):
        """Тест блокировки пользователя по email с правами администратора."""
        validation_response = clients.admin.ban_user(user.get("email"), 40)

        assert validation_response.status == "ok", "Статус ответа не 'ok'"
        assert validation_response.message == "User banned", \
            f"Сообщение в ответе не соответствует ожидаемому: {validation_response.message}"
        assert clients.db.get_user_by_email(user.get("email")).banned_until is not None, \
            "Пользователь не заблокирован в базе данных"


    @allure.title("Разбан пользователя по email")
    def test_unban_user_by_email(self, clients, admin_user, user, admin_auth_token):
        """Тест разблокировки пользователя по email с правами администратора."""
        validation_response = clients.admin.unban_user(user.get("email"))

        assert validation_response.status == "ok", "Статус ответа не 'ok'"
        assert validation_response.message == "User unbanned", \
            f"Сообщение в ответе не соответствует ожидаемому: {validation_response.message}"
        assert clients.db.get_user_by_email(user.get("email")).banned_until is None, \
            "Пользователь не разблокирован в базе данных"

