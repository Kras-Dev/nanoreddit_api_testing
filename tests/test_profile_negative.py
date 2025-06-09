import allure
import pytest
from pydantic import ValidationError

from src.models.api_model import ApiResponse


@allure.feature("User Profile")
@allure.story("Profile Info Negative")
@pytest.mark.negative
@pytest.mark.profile
class TestProfileNegative:
    @allure.title("Получение профиля без авторизации")
    def test_get_profile_no_auth(self, clients):
        """Тест получение информации о профиле без авторизации.
        """
        validation_response = clients.profile.get_profile_info()

        assert validation_response.status == "error", \
            f"Ожидался статус 'error', получен '{validation_response.status}'"
        assert validation_response.error == "Access denied", \
            f"Ожидалось сообщение 'Access denied', получено '{validation_response.error}'"