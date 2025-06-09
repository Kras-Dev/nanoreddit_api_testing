from dataclasses import dataclass
from conftest_users import *
from src.clients.http_client.admin_controller import AdminController
from src.clients.http_client.auth_controller import AuthController
from src.clients.http_client.base_client import BaseClient
from src.clients.http_client.comments_controller import CommentsController
from src.clients.http_client.post_controller import PostsController
from src.clients.http_client.profile_controller import ProfileController
from src.clients.sql_client.sqlalchemy_client import SqlAlchemyClient
from steps.post_steps import publish_post_step, add_comment_step

@pytest.fixture(scope="session")
def sql_client():
    """Создает клиент для работы с базой данных."""
    sql_client = SqlAlchemyClient()

    yield sql_client
    sql_client.clear_all_tables()
    sql_client.disconnect()

@pytest.fixture(scope="session")
def http_client():
    """Создает HTTP клиент для работы с API."""
    http_client = BaseClient()

    yield http_client
    http_client.close_session()

@pytest.fixture(scope="module")
def auth_controller(http_client):
    """Создает клиент аутентификации."""
    return AuthController(http_client)

@pytest.fixture(scope="module")
def admin_controller(http_client):
    """Создает клиент администратора (токен устанавливается через фикстуру admin_auth_token)."""
    yield AdminController(http_client)

@pytest.fixture(scope="module")
def profile_controller(http_client):
    """Создает клиент профиля."""
    return ProfileController(http_client)

@pytest.fixture(scope="module")
def posts_controller(http_client):
    """Создает клиент постов."""
    return PostsController(http_client)

@pytest.fixture(scope="module")
def comments_controller(http_client):
    """Создает клиент комментариев."""
    return CommentsController(http_client)

@dataclass
class Clients:
    db: SqlAlchemyClient
    api: BaseClient
    profile: ProfileController
    auth: AuthController
    posts: PostsController
    comments: CommentsController
    admin: AdminController

@pytest.fixture(scope="module")
def clients(http_client, sql_client, profile_controller, auth_controller, posts_controller, comments_controller,
            admin_controller):
    return Clients(
        db=sql_client,
        api=http_client,
        profile=profile_controller,
        auth=auth_controller,
        posts=posts_controller,
        comments=comments_controller,
        admin=admin_controller
    )

@pytest.fixture(scope="class")
def publish_post(clients, user):
    """Создает пост от имени авторизованного пользователя."""
    post_id = publish_post_step(clients, user)
    yield post_id

@pytest.fixture(scope="class")
def add_comment(clients ,user, publish_post):
    """Создает комментарий к посту от имени авторизованного пользователя."""
    comment_id = add_comment_step(clients, user, publish_post)
    yield comment_id
