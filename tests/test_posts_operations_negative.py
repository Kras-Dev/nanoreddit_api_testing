import allure
import pytest
from faker import Faker

fake = Faker()

@allure.feature("Post Controller")
@allure.story("Post Operations Negative")
@pytest.mark.negative
@pytest.mark.posts
class TestPostsNegative:
    @allure.title("Получение поста без авторизации")
    def test_get_post_no_auth(self, clients):
        """Тест получения информации о посте без авторизации."""
        post_id = str(fake.uuid4())

        validation_response = clients.posts.get_post(post_id)

        assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
        assert validation_response.error == "Access denied", "Ожидалось сообщение об ошибке 'Access denied'"

    @allure.title("Получение поста с несуществующим ID")
    def test_get_post_invalid_id(self, clients, user):
        """Тест получения поста с несуществующим ID."""
        post_id = fake.uuid4()

        validation_response = clients.posts.get_post(post_id)

        assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
        assert validation_response.error == "Post not found", "Ожидалось сообщение об ошибке 'Post not found'"

    @allure.title("Добавление комментария к несуществующему посту")
    def test_add_comment_invalid_post_id(self, clients, user):
        """Тест добавления комментария к посту с несуществующим ID."""
        test_data = {"post_id": fake.uuid4(), "comment_text": fake.text(12)}

        validation_response = clients.posts.add_comment(**test_data)

        assert validation_response.status == "error", f"Статус ответа не 'error': {validation_response.status}"
        assert validation_response.error == "Post not found", "Ожидалось сообщение об ошибке 'Post not found'"

    @allure.title("Голосование за пост с несуществующим ID")
    def test_vote_post_invalid_id(self, clients, user):
        """Тест голосования за пост с несуществующим ID."""
        test_data = {"post_id": fake.uuid4(), "value": 1}

        validation_response = clients.posts.vote_post(**test_data)

        assert validation_response.status == "error", f"Статус ответа не 'error': {validation_response.status}"
        assert validation_response.error == "Post not found", "Ожидалось сообщение об ошибке 'Post not found'"

