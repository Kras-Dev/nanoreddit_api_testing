import allure
import pytest
from faker import Faker

fake = Faker()

@allure.feature("Admin Controller")
@allure.story("Admin Operations Negative")
@pytest.mark.negative
@pytest.mark.admin
class TestAdminNegative:
    @allure.title("Проверка запрета доступа к профилю пользователя без прав администратора")
    def test_get_user_profile_no_admin(self, clients, user, user_auth_token):
        """Тест обычный пользователь не может получить профиль через админский эндпоинт."""
        with pytest.raises(PermissionError) as exc_info:
            clients.admin.get_user_profile(user.get("user_id"))

        assert "требуется роль ADMIN" in str(exc_info.value), "Ожидалось сообщение о необходимости роли ADMIN"

    @allure.title("Получение профиля пользователя с невалидным ID")
    def test_get_user_profile_invalid_id(self, clients, admin_user):
        """Тест получения профиля пользователя с невалидным ID."""
        user_id = fake.random_number(digits=3)
        validation_response = clients.admin.get_user_profile(user_id)

        assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
        assert validation_response.error == f"User not found with id: {user_id}", \
            f"Ожидалось сообщение об ошибке для ID {user_id}"

    @allure.title("Попытка забанить пользователя с несуществующим email")
    def test_ban_user_invalid_email(self, clients, admin_user):
        """Тест блокировки пользователя с несуществующим email."""
        email = fake.email()

        validation_response = clients.admin.ban_user(email, 40)

        assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
        assert validation_response.error == f"User not found with email: {email}", \
            f"Ожидалось сообщение об ошибке для email {email}"
