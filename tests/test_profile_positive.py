import allure
import pytest

@allure.feature("User Profile")
@allure.story("Profile Info Positive")
@pytest.mark.positive
@pytest.mark.profile
class TestProfile:
    @allure.title("Получение профиля пользователя")
    def test_profile(self, clients, user):
        """Тест на получение профиля текущего пользователя.
        """
        validation_response = clients.profile.get_profile_info()
        assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"
        assert validation_response.responseData.email == user.get("email")
        assert validation_response.responseData.username == user.get("email")

        with allure.step("Проверка наличия пользователя в базе данных"):
            db_user = clients.db.get_user_by_email(user["email"])
            assert db_user is not None, "Пользователь не найден в базе"
            assert db_user.id == user.get("user_id")


