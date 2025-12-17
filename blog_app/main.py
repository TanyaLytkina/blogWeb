import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import markdown2
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.middleware.sessions import SessionMiddleware

import blog_app.crud as crud
from blog_app.models import PostCreate, User, UserCreate

app = FastAPI(title="BlogApp")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "super-secret-key"),
)

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory="blog_app/templates")
templates.env.globals["get_user"] = crud.get_user
templates.env.globals["get_user_by_login"] = crud.get_user_by_login


@app.on_event("startup")
async def startup():
    if not os.path.exists("blog.db"):
        conn = sqlite3.connect("blog.db")
        with open("blog_app/schema.sql", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.close()


def get_current_user(request: Request) -> Optional[User]:
    login = request.session.get("login")
    if not login:
        return None
    return crud.get_user_by_login(login)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, q: str = "", page: int = 1):
    user = get_current_user(request)
    if q:
        posts = list(crud.cached_search_posts(q))
        pages = 1
    else:
        posts = crud.get_all_posts(page=page)
        total = len(crud.get_all_posts(page=1, per_page=999))
        pages = (total + 4) // 5
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": posts,
            "user": user,
            "q": q,
            "page": page,
            "pages": pages,
        },
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, login: str = Form(...), password: str = Form(...)):
    user = crud.get_user_by_login(login)
    if user and user.password == password:
        request.session.update(
            {
                "login": login,
                "user_id": user.id,
                "role": user.role,
            }
        )
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Неверный логин или пароль",
        },
    )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
):
    try:
        user_data = UserCreate(email=email, login=login, password=password)
    except ValidationError as e:
        msg = e.errors()[0]["msg"]
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": f"Ошибка валидации: {msg}"},
        )
    try:
        created = crud.create_user(user_data)
        request.session.update(
            {
                "login": created.login,
                "user_id": created.id,
                "role": "user",
            }
        )
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": str(e)},
        )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    saved_ids_str = request.session.get("saved_posts", "[]")
    try:
        saved_ids = json.loads(saved_ids_str)
    except Exception:
        saved_ids = []

    saved_posts = []
    for pid_str in saved_ids:
        try:
            pid = int(pid_str)
        except ValueError:
            continue
        post = crud.get_post(pid)
        if not post:
            continue
        author = crud.get_user(post.authorId)
        if author:
            saved_posts.append({"post": post, "author": author})

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "saved_posts": saved_posts,
            "saved_ids": saved_ids,
        },
    )


@app.post("/profile")
async def update_profile(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    pwd = password if password else user.password
    crud.update_user(user.id, email, pwd)
    return RedirectResponse("/profile", status_code=303)


@app.post("/save-post-toggle")
async def toggle_save_post(
    request: Request,
    post_id: int = Form(...),
    save: bool = Form(...),
):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Не авторизован")

    saved_ids_str = request.session.get("saved_posts", "[]")
    try:
        saved_ids = json.loads(saved_ids_str)
    except Exception:
        saved_ids = []

    if save and str(post_id) not in saved_ids:
        saved_ids.append(str(post_id))
    if not save:
        saved_ids = [id_str for id_str in saved_ids if int(id_str) != post_id]

    request.session["saved_posts"] = json.dumps(saved_ids)
    return JSONResponse({"saved_count": len(saved_ids)})


@app.get("/create-post", response_class=HTMLResponse)
async def create_post_form(request: Request):
    if not get_current_user(request):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("post_create.html", {"request": request})


@app.post("/create-post")
async def create_post_handler(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    try:
        post_data = PostCreate(authorId=user.id, title=title, content=content)
    except ValidationError as e:
        msg = e.errors()[0]["msg"]
        return templates.TemplateResponse(
            "post_create.html",
            {
                "request": request,
                "error": f"Ошибка валидации: {msg}",
                "title": title,
                "content": content,
            },
        )
    crud.create_post(post_data)
    return RedirectResponse("/", status_code=303)


@app.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int):
    post = crud.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    author = crud.get_user(post.authorId)
    content_html = markdown2.markdown(post.content)
    user = get_current_user(request)
    saved_ids_str = request.session.get("saved_posts", "[]")
    try:
        saved_ids = json.loads(saved_ids_str)
    except Exception:
        saved_ids = []
    return templates.TemplateResponse(
        "post_detail.html",
        {
            "request": request,
            "post": post,
            "author": author,
            "content_html": content_html,
            "user": user,
            "saved_ids": saved_ids,
        },
    )


@app.get("/edit-post/{post_id}", response_class=HTMLResponse)
async def edit_post_form(request: Request, post_id: int):
    user = get_current_user(request)
    post = crud.get_post(post_id)
    if not user or not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    if post.authorId != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет прав")
    return templates.TemplateResponse(
        "post_edit.html", {"request": request, "post": post}
    )


@app.post("/edit-post/{post_id}")
async def edit_post_handler(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
):
    user = get_current_user(request)
    post = crud.get_post(post_id)
    if not user or not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    if post.authorId != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет прав")

    try:
        _ = PostCreate(authorId=post.authorId, title=title, content=content)
    except ValidationError as e:
        msg = e.errors()[0]["msg"]
        return templates.TemplateResponse(
            "post_edit.html",
            {"request": request, "post": post, "error": f"Ошибка валидации: {msg}"},
        )

    updated = crud.update_post(post_id, title, content)
    if not updated:
        raise HTTPException(status_code=404, detail="Не удалось обновить пост")
    return RedirectResponse(f"/post/{post_id}", status_code=303)


@app.post("/delete-post/{post_id}")
async def delete_post_api(request: Request, post_id: int):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Не авторизован"}, status_code=401)
    success = crud.delete_post(post_id, user.id, is_admin=(user.role == "admin"))
    if not success:
        return JSONResponse({"error": "Нет прав или пост не найден"}, status_code=403)
    return {"ok": True}


@app.get("/search-users", response_class=HTMLResponse)
async def search_users(request: Request, q: str = ""):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    users = []
    if q:
        conn = sqlite3.connect("blog.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT id, login, email FROM users WHERE login LIKE ?",
            (f"%{q}%",),
        )
        users = [dict(row) for row in cur.fetchall()]
        conn.close()
    return templates.TemplateResponse(
        "search_users.html",
        {"request": request, "users": users, "q": q, "user": user},
    )


@app.post("/upload-avatar")
async def upload_avatar(request: Request, file: UploadFile = File(...)):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Не авторизован"}, status_code=401)
    filename = file.filename.lower()
    if not filename.endswith((".png", ".jpg", ".jpeg")):
        return JSONResponse({"error": "Разрешены только PNG/JPG"}, status_code=400)
    safe_name = f"avatar_{user.id}_{int(datetime.now().timestamp())}.jpg"
    path = BASE_DIR / "static" / "uploads" / safe_name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)
    request.session["avatar"] = safe_name
    return {"url": f"/static/uploads/{safe_name}"}
