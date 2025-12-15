import sqlite3
from typing import List, Optional
from datetime import datetime
from .models import User, Post, UserCreate, PostCreate

DB_PATH = "blog.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_user(user_: UserCreate) -> User:
    conn = get_db()
    cur = conn.cursor()
    now = datetime.now()
    cur.execute("""
        INSERT INTO users (email, login, password, role, created_at, updated_at)
        VALUES (?, ?, ?, 'user', ?, ?)
    """, (user_data.email, user_data.login, user_data.password, now, now))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return User(
        id=user_id,
        email=user_data.email,
        login=user_data.login,
        password=user_data.password,
        role="user",
        createdAt=now,
        updatedAt=now
    )

def get_user(user_id: int) -> Optional[User]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return User.model_validate(dict(row)) if row else None

def get_user_by_login(login: str) -> Optional[User]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE login = ?", (login,))
    row = cur.fetchone()
    conn.close()
    return User.model_validate(dict(row)) if row else None

def update_user(user_id: int, email: str, password: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET email = ?, password = ?, updated_at = ?
        WHERE id = ?
    """, (email, password, datetime.now(), user_id))
    conn.commit()
    conn.close()

def delete_user(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()



def create_post(post_: PostCreate) -> Post:
    conn = get_db()
    cur = conn.cursor()
    now = datetime.now()
    cur.execute("""
        INSERT INTO posts (author_id, title, content, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (post_.authorId, post_.title, post_.content, now, now))
    post_id = cur.lastrowid
    conn.commit()
    conn.close()
    return Post(
        id=post_id,
        authorId=post_.authorId,
        title=post_.title,
        content=post_.content,
        createdAt=now,
        updatedAt=now
    )

def get_post(post_id: int) -> Optional[Post]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cur.fetchone()
    conn.close()
    return Post.model_validate(dict(row)) if row else None

def get_all_posts(page: int = 1, per_page: int = 5) -> List[Post]:
    conn = get_db()
    cur = conn.cursor()
    offset = (page - 1) * per_page
    cur.execute("""
        SELECT * FROM posts ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    rows = cur.fetchall()
    conn.close()
    return [Post.model_validate(dict(row)) for row in rows]

def search_posts(query: str) -> List[Post]:
    conn = get_db()
    cur = conn.cursor()
    q = f"%{query}%"
    cur.execute("""
        SELECT * FROM posts
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY created_at DESC
    """, (q, q))
    rows = cur.fetchall()
    conn.close()
    return [Post.model_validate(dict(row)) for row in rows]

def update_post(post_id: int, title: str, content: str) -> Optional[Post]:

    conn = get_db()
    cur = conn.cursor()
    now = datetime.now()
    cur.execute("""
        UPDATE posts
        SET title = ?, content = ?, updated_at = ?
        WHERE id = ?
    """, (title, content, now, post_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return get_post(post_id) if ok else None

def delete_post(post_id: int, user_id: int, is_admin: bool = False) -> bool:
    conn = get_db()
    cur = conn.cursor()
    if is_admin:
        cur.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    else:
        cur.execute("DELETE FROM posts WHERE id = ? AND author_id = ?", (post_id, user_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok