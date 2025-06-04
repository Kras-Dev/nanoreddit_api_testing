from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy import Column, Text, String, Integer, ForeignKey, BigInteger, Identity, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, Identity(always=True), primary_key=True, nullable=False)
    banned_until = Column(TIMESTAMP(timezone=True), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(String(255), nullable=True)
    username = Column(String(255), unique=True, nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('USER', 'MODERATOR', 'ADMIN')", name="users_role_check"),
    )
    """
    posts — это атрибут (поле) в модели User.
    Он связывает модель User с моделью Post через отношение "один ко многим" (один пользователь может иметь много постов).
    Аргумент "Post" — это имя связанной модели, с которой устанавливается связь.
    Параметр back_populates="user" указывает, что в модели Post есть обратное отношение с именем user, которое 
    ссылается обратно на пользователя.
    Параметр cascade="all" - Все операции с родителем распространяются на дочерние объекты
    Параметр cascade="delete-orphan" - Автоматическое удаление дочерних объектов, которые отсоединены от 
    родителя (не принадлежат никому)
    """
    posts = relationship("Post", back_populates="user")
    votes = relationship("Vote", back_populates="user")
    comments = relationship("Comment", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True)
    title = Column(String(500), nullable=False)
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="posts")
    votes = relationship("Vote",back_populates="post")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True)
    text = Column(Text, nullable=False)
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False )

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    """
    parent — это атрибут (поле) в модели Comment.
    Он связывает модель Comment с самой собой через рекурсивное отношение "многие к одному" (один комментарий может 
    иметь одного родителя).
    Аргумент "Comment" — это имя связанной модели Comment.
    Параметр remote_side=[id] указывает SQLAlchemy, что колонка id является удалённой стороной (родительским ключом) в 
    этой рекурсивной связи. Это необходимо для правильного определения, какой комментарий является родителем, 
    а какой — потомком.
    Параметр backref="children" автоматически создаёт обратное отношение с именем children — список всех дочерних 
    комментариев, которые ссылаются на данный комментарий как на родителя.
    """
    parent = relationship("Comment", remote_side=[id], backref="children")

class Vote(Base):
    __tablename__ = "votes"
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True)
    value = Column(Integer, nullable=False)

    user = relationship("User", back_populates="votes")
    post = relationship("Post", back_populates="votes")


