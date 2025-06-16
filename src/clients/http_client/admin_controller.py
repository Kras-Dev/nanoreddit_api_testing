import allure

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

    @allure.step("Получение профиля пользователя по ID: {user_id}")
    def get_user_profile(self, user_id: int) -> AdminUserResponse:
        """Получить профиль пользователя по ID."""
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_PROFILE_INFO.format(user_id=str(user_id))
        response = self.api.post_parse_request(
            path=endpoint,
            response_model=AdminUserResponse
        )
        return response

    @allure.step("Блокировка пользователя с email: {email} на {ban_duration} секунд")
    def ban_user(self, email: str, ban_duration: int) -> BanUserResponse:
        """Заблокировать пользователя по email на заданный период."""
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_BAN_USER.format(email=str(email))
        params = {"email": email, "forSeconds": ban_duration}
        response = self.api.post_parse_request(
            path=endpoint,
            response_model=BanUserResponse,
            params=params)

        return response

    @allure.step("Разблокировка пользователя с email: {email}")
    def unban_user(self, email: str) -> UnbanUserResponse:
        """Разблокировать пользователя по email."""
        self._check_admin()
        endpoint = ApiEndpoints.ADMIN_UNBAN_USER.format(email=str(email))
        params = {"email": email}
        response = self.api.post_parse_request(
            path=endpoint,
            response_model=UnbanUserResponse,
            params=params)

        return response

    @allure.step("Проверка роли ADMIN у текущего пользователя")
    def _check_admin(self) -> None:
        """Проверить роль ADMIN."""
        profile_controller = ProfileController(self.api)
        profile_response = profile_controller.get_profile_info()
        if not profile_response.responseData or "ROLE_ADMIN" not in profile_response.responseData.authorities:
            raise PermissionError("Доступ запрещён: требуется роль ADMIN")
