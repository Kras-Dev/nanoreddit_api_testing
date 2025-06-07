import requests

from src.clients.http_client.base_client import BaseClient
from src.config.api_endpoints import ApiEndpoints


class ProfileController:
    """
    Клиент для работы с профилем через API.
    """
    def __init__(self, base_client: BaseClient):
        self.api = base_client

    def get_profile_info(self) -> requests.Response:
        """
        Получение профиля пользователя.
        """
        response = self.api.post_request(ApiEndpoints.PROFILE_INFO)
        return response