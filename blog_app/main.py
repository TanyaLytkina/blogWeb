from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .models import UserCreate, PostCreate, UserResponse, PostResponse
from .crud import (
    create_user, get_user, update_user, delete_user,
    create_post, get_post, get_all_posts, update_post, delete_post
)
from .data_loader import load_data, save_data
import os

app = FastAPI(title="Blog API")


templates = Jinja2Templates(directory="blog_app/templates")

@app.on_event("startup")
async def startup_event():
    load_data()

@app.on_event("shutdown")
async def shutdown_event():
    save_data()


@app.post("/users/", response_model=UserResponse)
async def create_new_user(user: UserCreate):
    return create_user(user)

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_existing_user(user_id: int, user: UserCreate):
    updated_user = update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}")
async def delete_existing_user(user_id: int):
    success = delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@app.post("/posts/", response_model=PostResponse)
async def create_new_post(post: PostCreate):
    return create_post(post)

@app.get("/posts/{post_id}", response_model=PostResponse)
async def read_post(post_id: int):
    post = get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/posts/", response_model=list[PostResponse])
async def list_all_posts():
    return get_all_posts()

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_existing_post(post_id: int, post: PostCreate):
    updated_post = update_post(post_id, post)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post

@app.delete("/posts/{post_id}")
async def delete_existing_post(post_id: int):
    success = delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    all_posts = get_all_posts()
    return templates.TemplateResponse("index.html", {"request": request, "posts": all_posts})

@app.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int):
    post = get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    author = get_user(post.authorId)
    return templates.TemplateResponse("post_detail.html", {"request": request, "post": post, "author": author})

@app.get("/create-post", response_class=HTMLResponse)
async def show_create_form(request: Request):
    return templates.TemplateResponse("post_create.html", {"request": request})

@app.post("/create-post", response_class=RedirectResponse)
async def handle_create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    authorId: int = Form(...)
):
    post_data = PostCreate(authorId=authorId, title=title, content=content)
    create_post(post_data)
    return RedirectResponse(url="/", status_code=303)

@app.get("/edit-post/{post_id}", response_class=HTMLResponse)
async def show_edit_form(request: Request, post_id: int):
    post = get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("post_edit.html", {"request": request, "post": post})

@app.post("/edit-post/{post_id}", response_class=RedirectResponse)
async def handle_edit_post(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    authorId: int = Form(...)
):
    post_data = PostCreate(authorId=authorId, title=title, content=content)
    updated_post = update_post(post_id, post_data)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return RedirectResponse(url=f"/post/{post_id}", status_code=303)