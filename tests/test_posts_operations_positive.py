import allure
import pytest
from faker import Faker

from src.models.api_model import PublishRequest

fake = Faker()

@allure.feature("Post Controller")
@allure.story("Post Operations")
@pytest.mark.positive
@pytest.mark.posts
class TestPosts:
    @allure.title("Публикация нового поста")
    def test_publish_post(self, clients, user):
        """Тест на публикацию нового поста и проверку его создания в базе."""
        test_data = PublishRequest(title=fake.text(15), content=fake.text(25))

        validation_response = clients.posts.publish_post(test_data)

        assert validation_response.responseData is not None, "responseData отсутствует в ответе"
        assert validation_response.responseData.title == test_data.title, "Заголовок поста не совпадает"
        assert validation_response.responseData.content == test_data.content, "Содержимое поста не совпадает"
        assert validation_response.responseData.author == user["email"], "Автор поста не совпадает с пользователем"

        with allure.step("Проверка записи поста в базе данных"):
            db_post = clients.db.get_post_by_id(validation_response.responseData.id)
            assert db_post is not None, "Пост не найден в базе"
            assert db_post.id == validation_response.responseData.id, "ID поста в базе не совпадает с ответом API"

    @allure.title("Добавление комментария к посту")
    def test_add_comment(self, clients, publish_post):
        """Тест на добавление комментария к существующему посту и проверку его сохранения в базе."""
        test_data = fake.text(25)

        validation_response = clients.posts.add_comment(publish_post, test_data)

        assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"
        with allure.step("Проверка комментария в базе данных"):
            db_comment = clients.db.get_comment_by_post_id(publish_post)
            assert db_comment is not None, "Комментарий не найден в базе"
            assert db_comment.text == test_data, "Текст комментария в базе не совпадает с тестовым"

    @allure.title("Голосование за пост")
    def test_vote_post(self, clients, publish_post):
        """Тест на голосование за пост и проверку результата в базе."""
        validation_response = clients.posts.vote_post(publish_post, 1)

        with allure.step("Проверка голосования за пост базе данных"):
            db_vote = clients.db.get_post_vote_value(publish_post)
            assert db_vote is not None, "Голоса за пост не найдены в базе"
            assert db_vote == 1, "Количество голосов в базе не совпадает с тестовым"

    @allure.title("Получение информации о посте")
    def test_get_post_info(self, clients, user, publish_post):
        """Тест на получение информации о посте и проверку данных в ответе и базе."""
        validation_response = clients.posts.get_post(publish_post)

        assert validation_response.responseData.post.author == user.get("email"), \
        "Автор поста не совпадает с пользователем"
        assert str(validation_response.responseData.post.id) == publish_post, \
        "ID поста в ответе не совпадает с ожидаемым"

        with allure.step("Проверка поста в базе данных"):
            db_post = clients.db.get_post_by_id(publish_post)
            assert db_post is not None, "Пост не найден в базе"

    @allure.title("Получение списка постов")
    def test_get_posts_list(self, clients, publish_post):
        """Тест на получение списка постов и проверку корректности ответа."""
        validation_response = clients.posts.get_posts_list()

        assert validation_response.responseData is not None, "responseData отсутствует в ответе API"

