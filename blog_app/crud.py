from typing import List, Optional
from datetime import datetime
from .models import User, Post, UserCreate, PostCreate

users: List[User] = []
posts: List[Post] = []

def create_user(user_data: UserCreate) -> User:
    new_id = max([u.id for u in users], default=0) + 1
    user = User(
        id=new_id,
        email=user_data.email,
        login=user_data.login,
        password=user_data.password,
        createdAt=datetime.now(),
        updatedAt=datetime.now()
    )
    users.append(user)
    return user

def get_user(user_id: int) -> Optional[User]:
    for user in users:
        if user.id == user_id:
            return user
    return None

def update_user(user_id: int, user_data: UserCreate) -> Optional[User]:
    user = get_user(user_id)
    if user:
        user.email = user_data.email
        user.login = user_data.login
        user.password = user_data.password
        user.updatedAt = datetime.now()
        return user
    return None

def delete_user(user_id: int) -> bool:
    global users
    original_len = len(users)
    users = [u for u in users if u.id != user_id]
    return len(users) < original_len

def create_post(post_data: PostCreate) -> Post:
    new_id = max([p.id for p in posts], default=0) + 1
    post = Post(
        id=new_id,
        authorId=post_data.authorId,
        title=post_data.title,
        content=post_data.content,
        createdAt=datetime.now(),
        updatedAt=datetime.now()
    )
    posts.append(post)
    return post

def get_post(post_id: int) -> Optional[Post]:
    for post in posts:
        if post.id == post_id:
            return post
    return None

def get_posts_by_user(user_id: int) -> List[Post]:
    return [post for post in posts if post.authorId == user_id]

def get_all_posts() -> List[Post]:
    return posts.copy()

def update_post(post_id: int, post_data: PostCreate) -> Optional[Post]:
    post = get_post(post_id)
    if post:
        post.authorId = post_data.authorId
        post.title = post_data.title
        post.content = post_data.content
        post.updatedAt = datetime.now()
        return post
    return None

def delete_post(post_id: int) -> bool:
    global posts
    original_len = len(posts)
    posts = [p for p in posts if p.id != post_id]
    return len(posts) < original_len