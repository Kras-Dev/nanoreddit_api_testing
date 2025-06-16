from faker import Faker

from src.models.api_model import PublishRequest

fake = Faker()

def publish_post_step(clients, user):
    """Создает пост от имени авторизованного пользователя."""
    test_data = PublishRequest(title=fake.text(10), content=fake.text(25))
    validation_response = clients.posts.publish_post(test_data)
    post_id = validation_response.responseData.id
    db_post = clients.db.get_post_by_id(str(post_id))
    assert db_post is not None, "Пост не найден в базе после создания"
    return str(post_id)

def add_comment_step(clients, user, post_id):
    """Создает комментарий к посту от имени авторизованного пользователя."""
    test_data = fake.text(15)
    clients.posts.add_comment(post_id, test_data)
    db_comment = clients.db.get_comment_by_post_id(post_id)
    assert db_comment is not None, "Комментарий не найден в базе после создания"
    return str(db_comment.id)