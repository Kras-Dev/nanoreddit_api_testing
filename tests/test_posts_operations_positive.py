import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import (
    ApiResponse,
    PostDataResponse,
    PostPublishResponse,
    PostsResponse,
    PublishRequest,
)

fake = Faker()

@allure.feature("Post Controller")
@allure.story("Post Operations")
@pytest.mark.positive
class TestPosts:
    @allure.title("Публикация нового поста")
    def test_publish_post(self, user, sql_client, posts_controller):
        """
        Тест на публикацию нового поста и проверку его создания в базе.
        """
        test_data = {
          "title": fake.text(15),
          "content": fake.text(25)
        }
        with allure.step("Валидация данных запроса публикации поста"):
            PublishRequest.model_validate(test_data)

        with allure.step("Отправка запроса на публикацию поста"):
            try:
                response = posts_controller.publish_post(test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при публикации поста: {e}")

        with allure.step("Валидация ответа публикации поста"):
            try:
                validation_response = PostPublishResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа публикации поста: {e}")

            assert validation_response.responseData is not None, "responseData отсутствует в ответе"
            assert validation_response.responseData.title == test_data.get("title"), "Заголовок поста не совпадает"
            assert validation_response.responseData.content == test_data.get("content"), "Содержимое поста не совпадает"
            assert validation_response.responseData.author == user["email"], "Автор поста не совпадает с пользователем"

        with allure.step("Проверка записи поста в базе данных"):
            db_post = sql_client.get_post_by_id(validation_response.responseData.id)
            assert db_post is not None, "Пост не найден в базе"
            assert db_post.id == validation_response.responseData.id, "ID поста в базе не совпадает с ответом API"

    @allure.title("Добавление комментария к посту")
    def test_add_comment(self, publish_post, posts_controller, sql_client):
        """
        Тест на добавление комментария к существующему посту и проверку его сохранения в базе.
        """
        test_data = fake.text(25)
        with allure.step("Отправка запроса на публикацию комментария"):
            try:
                response = posts_controller.add_comment(publish_post, test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при добавлении комментария: {e}")

        with allure.step("Валидация ответа добавления комментария"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа добавления комментария: {e}")

            assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"

        with allure.step("Проверка комментария в базе данных"):
            db_comment = sql_client.get_comment_by_post_id(publish_post)
            assert db_comment is not None, "Комментарий не найден в базе"
            assert db_comment.text == test_data, "Текст комментария в базе не совпадает с тестовым"

    @allure.title("Голосование за пост")
    def test_vote_post(self, posts_controller, publish_post, sql_client):
        """
        Тест на голосование за пост и проверку результата в базе.
        """
        with allure.step("Отправка запроса голосования за пост"):
            try:
                response = posts_controller.vote_post(publish_post, 1)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при голосовании за пост: {e}")

        with allure.step("Валидация ответа голосования за пост"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа голосования за пост: {e}")

            assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"

        with allure.step("Проверка голосования за пост базе данных"):
            db_vote = sql_client.get_post_vote_value(publish_post)
            assert db_vote is not None, "Голоса за пост не найдены в базе"
            assert db_vote == 1, "Количество голосов в базе не совпадает с тестовым"

    @allure.title("Получение информации о посте")
    def test_get_post_info(self, posts_controller, publish_post, user, sql_client):
        """
        Тест на получение информации о посте и проверку данных в ответе и базе.
        """
        with allure.step("Отправка запроса на получение информации о посте"):
            try:
                response = posts_controller.get_post(publish_post)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при получении информации о посте: {e}")

        with allure.step("Валидация ответа информации о посте"):
            try:
                validation_response = PostDataResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа информации о посте: {e}")

            assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"
            assert validation_response.responseData.post.author == user.get("email"), \
                "Автор поста не совпадает с пользователем"
            assert str(validation_response.responseData.post.id) == publish_post, \
                "ID поста в ответе не совпадает с ожидаемым"

        with allure.step("Проверка поста в базе данных"):
            db_post = sql_client.get_post_by_id(publish_post)
            assert db_post is not None, "Пост не найден в базе"

    @allure.title("Получение списка постов")
    def test_get_posts_list(self, posts_controller, publish_post):
        """
        Тест на получение списка постов и проверку корректности ответа.
        """
        with allure.step("Отправка запроса на получение списка постов"):
            try:
                response = posts_controller.get_posts_list()
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при получении списка постов: {e}")

        with allure.step("Валидация ответа списка постов"):
            try:
                validation_response = PostsResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа списка постов: {e}")

            assert validation_response.status == "ok", f"Статус ответа не 'ok': {validation_response.status}"
            assert validation_response.responseData is not None, "responseData отсутствует в ответе API"

