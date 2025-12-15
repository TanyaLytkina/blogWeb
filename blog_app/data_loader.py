import json
from typing import List
from .models import User, Post
from .crud import users, posts

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for u in data.get("users", []):
                users.append(User(**u))
            for p in data.get("posts", []):
                posts.append(Post(**p))
        print("Данные успешно загружены из файла.")
    except FileNotFoundError:
        print("Файл данных не найден. Начинаем с пустой базы.")
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")

def save_data():
    data = {
        "users": [user.dict() for user in users],
        "posts": [post.dict() for post in posts]
    }
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        print("Данные успешно сохранены в файл.")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")