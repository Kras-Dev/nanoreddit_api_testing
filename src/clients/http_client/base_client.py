from typing import Optional, Dict, Any

import requests

from src.config.api_endpoints import ApiEndpoints


class BaseClient:
    def __init__(self):
        """
        Инициализация клиента с базовым URL и сессией requests.
        """
        self.base_url = ApiEndpoints.BASE_URL
        self.session = requests.Session()
        self._token: Optional[str] = None

    def set_token(self, token: str) -> None:
        """
        Установить JWT токен для авторизации.
        Токен добавляется в заголовок Authorization для всех последующих запросов.
        """
        self._token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    @property
    def token(self) -> Optional[str]:
        return self._token

    def clear_token(self) -> None:
        """
        Очистить JWT токен из заголовков сессии.
        """
        self._token = None
        self.session.headers.pop('Authorization', None)

    def _url(self, path: str) -> str:
        """
        Сформировать полный URL, объединяя базовый URL и путь эндпоинта.
        """
        return f"{self.base_url}{path}"

    def post_request(self, path: str, json: Optional[Dict[str, Any]]=None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Отправить POST-запрос по указанному пути с JSON-данными.
        """
        url = self._url(path)
        response = self.session.post(url, json=json, params=params)
        return response

    def get_request(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Отправить GET-запрос по указанному пути с параметрами запроса.
        """
        url = self._url(path)
        response = self.session.get(url, params=params)
        return response

    def close_session(self) -> None:
        """
        Закрыть сессию requests.
        """
        self.session.close()