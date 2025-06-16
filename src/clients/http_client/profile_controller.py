import allure

from src.clients.http_client.base_client import BaseClient
from src.config.api_endpoints import ApiEndpoints
from src.models.api_model import ProfileResponse


class ProfileController:
    """Клиент для работы с профилем через API."""

    def __init__(self, base_client: BaseClient):
        self.api = base_client

    @allure.step('Получение информации профиля пользователя')
    def get_profile_info(self) -> ProfileResponse:
        """Получение профиля пользователя."""
        return self.api.post_parse_request(
            path=ApiEndpoints.PROFILE_INFO,
            response_model=ProfileResponse
        )