
from src.clients.http_client.base_client import BaseClient
from src.clients.http_client.profile_controller import ProfileController
from src.config.api_endpoints import ApiEndpoints
from src.models.api_model import (
    AdminUserResponse,
    BanUserResponse,
    UnbanUserResponse,
)


class AdminController:
    """Клиент для работы с админскими операциями через API."""

    def __init__(self, api_client: BaseClient):
        self.api = api_client

    def get_user_profile(self, user_id: int) -> AdminUserResponse:
        """Получить профиль пользователя по ID."""
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_PROFILE_INFO.format(user_id=str(user_id))
        response = self.api.post_request(endpoint)
        validation_response = AdminUserResponse.model_validate(response.json())
        return validation_response

    def ban_user(self, email: str, ban_duration: int) -> BanUserResponse:
        """Заблокировать пользователя по email на заданный период."""
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_BAN_USER.format(email=str(email))
        params = {"email": email, "froSeconds": ban_duration}
        response = self.api.post_request(endpoint, params=params)
        validation_response = BanUserResponse.model_validate(response.json())
        return validation_response

    def unban_user(self, email: str) -> UnbanUserResponse:
        """Разблокировать пользователя по email."""
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_UNBAN_USER.format(email=str(email))
        params = {"email": email}
        response = self.api.post_request(endpoint, params=params)
        validation_response = UnbanUserResponse.model_validate(response.json())
        return validation_response

    def _check_admin(self) -> None:
        """Проверить роль ADMIN."""
        profile_controller = ProfileController(self.api)
        profile_response = profile_controller.get_profile_info()
        if not profile_response.responseData or "ROLE_ADMIN" not in profile_response.responseData.authorities:
            raise PermissionError("Доступ запрещён: требуется роль ADMIN")
