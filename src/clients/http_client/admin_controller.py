import requests

from src.clients.http_client.base_client import BaseClient
from src.clients.http_client.profile_controller import ProfileController
from src.config.api_endpoints import ApiEndpoints
from src.models.api_model import ProfileResponse


class AdminController:
    """
    Клиент для работы с админскими операциями через API.
    """
    def __init__(self, api_client: BaseClient):
        self.api = api_client

    def get_user_profile(self, user_id: int) -> requests.Response:
        """
        Получить профиль пользователя по ID.
        """
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_PROFILE_INFO.format(user_id=str(user_id))
        response = self.api.post_request(endpoint)
        return response

    def ban_user(self, email: str, ban_duration: int) -> requests.Response:
        """
        Заблокировать пользователя по email на заданный период.
        """
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_BAN_USER.format(email=str(email))
        params = {"email": email, "froSeconds": ban_duration}
        response = self.api.post_request(endpoint, params=params)
        return response

    def unban_user(self, email: str) -> requests.Response:
        """
        Разблокировать пользователя по email.
        """
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_UNBAN_USER.format(email=str(email))
        params = {"email": email}
        response = self.api.post_request(endpoint, params=params)
        return response

    def _check_admin(self) -> None:
        """
        Проверить роль ADMIN.
        """
        profile_client = ProfileController(self.api)
        response = profile_client.get_profile_info().json()
        profile_response = ProfileResponse.model_validate(response)
        if not profile_response.responseData or "ROLE_ADMIN" not in profile_response.responseData.authorities:
            raise PermissionError("Доступ запрещён: требуется роль ADMIN")
