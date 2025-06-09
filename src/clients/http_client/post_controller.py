from typing import Any, Dict, Literal, Optional
from uuid import UUID


from src.clients.http_client.base_client import BaseClient
from src.config.api_endpoints import ApiEndpoints
from src.models.api_model import NewCommentRequest, Pageable, PublishRequest, PostPublishResponse, PostDataResponse, \
    ApiResponse, PostsResponse


class PostsController:
    def __init__(self, base_client: BaseClient):
        """Клиент для работы с постами через API.
        """
        self.api = base_client

    def publish_post(self, data: PublishRequest) -> PostPublishResponse:
        """Публикация нового поста"""
        response = self.api.post_request(ApiEndpoints.POST_PUBLISH, json=data.model_dump())
        validation_response = PostPublishResponse.model_validate(response.json())
        return validation_response

    def get_post(self, post_id: str, params: Optional[Dict[str, Any]] = None) -> PostDataResponse:
        """Получить информацию о посте по id с пагинацией комментариев.
        """
        try:
            UUID(post_id)
        except ValueError:
            raise ValueError(f"post_id '{post_id}' не является валидным UUID")

        if params is not None:
            params = Pageable.model_validate(params)
            params_dict = params.model_dump()
        else:
            params_dict = None

        endpoint = ApiEndpoints.POST.format(post_id=post_id)
        response = self.api.get_request(endpoint, params=params_dict)
        validation_response = PostDataResponse.model_validate(response.json())
        return validation_response

    def add_comment(self, post_id: str, comment_text: str) -> ApiResponse:
        """Публикация нового комментария к посту"""
        try:
            UUID(post_id)
        except ValueError:
            raise ValueError(f"post_id '{post_id}' не является валидным UUID")
        data = NewCommentRequest(text=comment_text)
        endpoint = ApiEndpoints.POST_ADD_COMMENT.format(post_id=post_id)
        response = self.api.post_request(endpoint, json=data.model_dump())
        validation_response = ApiResponse.model_validate(response.json())
        return validation_response

    def vote_post(self, post_id: str, value: Literal[-1, 1]) -> ApiResponse:
        """Голосование за пост"""
        try:
            UUID(post_id)
        except ValueError:
            raise ValueError(f"post_id '{post_id}' не является валидным UUID")
        endpoint = ApiEndpoints.POST_VOTE.format(post_id=post_id)
        params = {"value": value}
        response = self.api.post_request(endpoint, params=params)
        validation_response = ApiResponse.model_validate(response.json())
        return validation_response

    def get_posts_list(self, params: Optional[Dict[str, Any]] = None) -> PostsResponse:
        """Получение списка постов, с разбивкой на страницы"""
        if params is not None:
            params = Pageable.model_validate(params)
            params_dict = params.model_dump()
        else:
            params_dict = None
        response = self.api.get_request(ApiEndpoints.POSTS, params_dict)
        validation_response = PostsResponse.model_validate(response.json())
        return validation_response