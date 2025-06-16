import allure
import pytest


@allure.feature("User Profile")
@allure.story("Profile Info Negative")
@pytest.mark.negative
@pytest.mark.profile
class TestProfileNegative:
    @allure.title("Получение профиля без авторизации")
    def test_get_profile_no_auth(self, clients):
        """Тест получение информации о профиле без авторизации."""
        validation_response = clients.profile.get_profile_info()

        assert "Access denied" in validation_response.error, \
            f"Ожидалось сообщение 'Access denied', получено '{validation_response.error}'"