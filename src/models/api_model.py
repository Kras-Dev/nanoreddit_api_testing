from datetime import datetime
from typing import Any, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_password_complexity(password: str) -> str:
    """
    Проверяет сложность пароля на соответствие требованиям.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(ch.isdigit() for ch in password):
        raise ValueError("Password must contain at least one digit")
    if not any(ch.islower() for ch in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(ch.isupper() for ch in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if any(ch.isspace() for ch in password):
        raise ValueError("Password must not contain whitespace")
    return password

class ApiResponse(BaseModel):
    """Базовая модель ответа API."""
    status: Literal["ok", "error"] = Field(..., description="Response status")
    error: Optional[str] = Field(None, description="Error message if status is 'error'")
    responseData: Optional[Any] = Field(None, description="Response data payload")

class RegistrationRequest(BaseModel):
    """Модель запроса на регистрацию пользователя.

    Используется в  POST /api/v1/auth/register.
    """
    email: EmailStr = Field(min_length=1, description="Email address - should be valid")
    username: str = Field(min_length=1, description="Username - should be non-empty")
    password: str = Field(min_length=8, description=("Password must be at least 8 characters long, contain at least one digit, "
            "one lowercase letter, one uppercase letter, and no whitespace."
        )
    )
    passwordConfirmation: str = Field(min_length=8, description="Should be the same as password")

    @field_validator("password", mode="after")
    @classmethod
    def password_complexity(cls, password:str) -> str:
        return validate_password_complexity(password)

    @field_validator( "passwordConfirmation", mode="after")
    @classmethod
    def passwords_match(cls, password_confirmation: str, info) -> str:
        password = info.data.get("password")
        if password != password_confirmation:
            raise ValueError("Should be the same as password")
        return password_confirmation

class LoginRequest(BaseModel):
    """Модель запроса авторизации пользователя.

    Используется в POST /api/v1/auth/login.
    """
    email: EmailStr = Field(min_length=1, description="Email address is required")
    password: str = Field(min_length=8, description="Password is required")

    @field_validator("password", mode="after")
    @classmethod
    def password_complexity(cls, password: str) -> str:
        return validate_password_complexity(password)

class ProfileDataComponent(BaseModel):
    """
    Модель данных профиля пользователя.

    Используется в ответах:

    - /api/v1/profile/info
    - /api/v1/admin/user/{id}
    """
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User Email")
    username: str = Field(..., description="User Name")
    bannedUntil: Optional[datetime] = Field(None, description="Ban end date, if any")
    authorities: List[str] = Field(..., description="List of user roles")

class ProfileResponse(ApiResponse):
    """
    Модель ответа на запрос информации о профиле пользователя.

    Используется в POST /api/v1/profile/info.
    """
    responseData: Optional[ProfileDataComponent] = Field(None, description="Profile data or None")
    message: Optional[str] = Field(None, description="Additional message from the server")

class PublishRequest(BaseModel):
    """
    Модель запроса на публикацию нового поста.

    Используется в POST /api/v1/posts/publish.
    """
    title: str = Field(..., min_length=1, max_length=255, description="Title is required, should be less than 255 characters")
    content: str = Field(..., min_length=1, description="Content is required")

class PostPublishComponent(BaseModel):
    """
    Модель данных о созданном посте.

    Используется в ответах на POST /api/v1/posts/publish.
    """
    id: UUID = Field(..., description="Post id")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    author: EmailStr = Field(..., description="Author email")
    createdAt: datetime = Field(..., description="Post creation date")

class PostPublishResponse(ApiResponse):
    """
    Модель ответа на публикацию поста.

    Используется в POST /api/v1/posts/publish.
    """
    responseData: Optional[PostPublishComponent] = Field(None, description="Post data")

class Pageable(BaseModel):
    """
    Модель параметров пагинации.

    Используется в GET /api/v1/posts и других эндпоинтах с пагинацией.
    """
    page: int = Field(..., ge=0, description="Page number (starts with 0)")
    size: int = Field(..., ge=1, description="Number of elements on page")
    sort: Optional[List[str]] = Field(default_factory=list, description="Sort options asc|desc")

class NewCommentRequest(BaseModel):
    """
    Модель запроса на добавление комментария к посту.

    Используется в POST /api/v1/posts/{postId}/addComment.
    """
    text: str = Field(..., max_length=255, description="Comment")

class CommentResponse(BaseModel):
    """
    Модель ответа с данными комментария.

    Включает информацию о самом комментарии и вложенных ответах (реплаях).
    """
    id: UUID = Field(..., description="Post id")
    text: str = Field(..., description="Comment text")
    author: EmailStr = Field(..., description="Author email")
    createdAt: datetime = Field(..., description="Comment creation date")
    replies: List["CommentResponse"] = Field(default_factory=list, description="Replies data")

class CommentApiResponse(ApiResponse):
    """
    Модель ответа API при добавлении ответа на комментарий.

    Используется в POST /api/v1/comments/{parentCommentId}/reply.
    """
    responseData: Optional[CommentResponse] = Field(None, description="Data of the created comment")

class PostDataComponent(BaseModel):
    """
    Модель данных поста с комментариями.

    Используется в ответах GET /api/v1/posts/{postId}.
    """
    post: PostPublishComponent = Field(..., description="Post data")
    comments: List[CommentResponse] = Field(default_factory=list, description="List of comments for the post")
    voteScore: int = Field(..., description="Total number of votes for the post")
    hasMoreComments: bool = Field(..., description="Flag of additional comments")

class PostDataResponse(ApiResponse):
    """
    Модель ответа данных информации о посте.

    Используется в ответах GET /api/v1/posts/{postId}.
    """
    responseData: PostDataComponent = Field(..., description="Post data with comments and votes")

class PostsPageDataComponent(BaseModel):
    """
    Модель данных страницы с постами и информацией о пагинации.

    Используется в ответах GET /api/v1/posts.
    """
    content: List[PostPublishComponent] = Field(..., description="List of posts on the page")
    pageNumber: int = Field(..., ge=0, description="Current page number")
    pageSize: int = Field(..., ge=1, description="Page size")
    totalElements: int = Field(..., ge=0, description="Total number of elements")
    totalPages: int = Field(..., ge=0, description="Total number of pages")

class PostsResponse(ApiResponse):
    """
    Модель ответа на запрос списка постов с пагинацией.

    Используется в GET /api/v1/posts.
    """
    responseData: Optional[PostsPageDataComponent] = Field(None, description="Data with posts and pagination")

class AdminUserResponse(ApiResponse):
    """
    Модель ответа на запрос информации о пользователе по id (для админа).

    Используется в POST /api/v1/admin/user/{id}.
    """
    responseData: Optional[ProfileDataComponent] = Field(None, description="Profile data")

class UnbanUserData(BaseModel):
    """
    Модель данных о результате разбана пользователя (для админа).

    Используется в POST /api/v1/admin/management/unban/byEmail/{email}.
    """
    bannedUntil: Optional[datetime] = Field(None, description="Ban end date")

class UnbanUserResponse(ApiResponse):
    """
    Модель ответа на запрос разбана пользователя (для админа).

    Используется в POST /api/v1/admin/management/unban/byEmail/{email}.
    """
    responseData: Optional[UnbanUserData] = Field(None, description="User unban data")
    message: Optional[str] = Field(None, description="Additional server message")

class BanUserData(BaseModel):
    """
    Модель данных о результате бана пользователя (для админа).

    Используется в POST /api/v1/admin/management/ban/byEmail/{email}.
    """
    bannedUntil: Optional[datetime] = Field(None, description="Ban end date")

class BanUserResponse(ApiResponse):
    """
    Модель ответа на запрос бана пользователя (для админа).

    Используется в POST /api/v1/admin/management/ban/byEmail/{email}.
    """
    responseData: Optional[BanUserData] = Field(None, description="User ban data")
    message: Optional[str] = Field(None, description="Additional server message")

