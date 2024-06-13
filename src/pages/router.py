import os

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates

from operations.models import Manga
from operations.router import get_manga_by_name, get_last_manga, get_manga_by_categories
from auth.base_config import fastapi_users
from database import User, get_async_session

current_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix='/pages',
    tags=['Pages']
)

templates = Jinja2Templates(directory='templates')

@router.get('/main', name='pages:main')
def get_manga(request: Request, content=Depends(get_last_manga), user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('main.html', {'request': request, 'content': content, "user": user})
    else:
        return templates.TemplateResponse('main.html', {'request': request, 'content': content})


@router.get('/chapters_choose/{name}', name='pages:chapters_choose')
async def get_manga_chapters(request: Request, name: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(Manga.c.chapter)
            .where(Manga.c.path_to_manga == name)
        )

        res = await session.execute(query)
        chapters = res.fetchall()
        if not chapters:
            raise HTTPException(status_code=404, detail="Манга не найдена")

        # Преобразуем результат в список глав
        chapter_numbers = [chapter.chapter for chapter in chapters]

        return templates.TemplateResponse('chapter_choose.html', {
            "request": request,
            "manga_name": name,
            "chapter_numbers": chapter_numbers
        })

    except sqlalchemy.exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/view/{name}/{chapter}', name='pages:view')
def get_news(request: Request, name: str, chapter: str,  user: User = Depends(current_user)):
    manga_dir = f"static/manga/{name}/{chapter}"

    if not os.path.exists(manga_dir):
        raise HTTPException(status_code=404, detail="Chapter not found")

    images = []
    for i in range(1, 200):
        img_path = f"{manga_dir}/P{str(i).zfill(5)}.jpg"
        if os.path.exists(img_path):
            images.append(f"/static/manga/{name}/{chapter}/P{str(i).zfill(5)}.jpg")
        else:
            break

    if user:
        return templates.TemplateResponse('manga_views.html', {'request': request, "user": user, "images": images})
    else:
        return templates.TemplateResponse('manga_views.html', {'request': request, "images": images})


@router.get('/categories/{type}', name='pages:categories')
def get_by_categories(request: Request, type=Depends(get_manga_by_categories), user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('categories.html', {'request': request, 'content': type, "user": user})
    else:
        return templates.TemplateResponse('categories.html', {'request': request, 'content': type})


@router.get('/choose', name='pages:choose')
def add_content(request: Request, user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('choose.html', {'request': request, "user": user})
    else:
        return templates.TemplateResponse('choose.html', {'request': request})


@router.get('/add_content', name='pages:add_content')
def add_content(request: Request, user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('add_content.html', {'request': request, "user": user})
    else:
        return templates.TemplateResponse('add_content.html', {'request': request})


@router.get('/add_chapter', name='pages:add_chapter')
async def add_content(request: Request, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = (select(
                Manga.c.id,
                Manga.c.head,
                Manga.c.path_to_manga,
            ).select_from(Manga)
        )
    res = await session.execute(query)
    return templates.TemplateResponse("add_chapter.html", {"request": request, "mangas": res, "user": user})


@router.get('/sucses_add_content', name='pages:sucses_add_content')
def add_content(request: Request, user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('sucses_add_content.html', {'request': request, "user": user})
    else:
        return templates.TemplateResponse('sucses_add_content.html', {'request': request})


@router.get('/about', name='pages:about')
def about_info(request: Request, user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('about.html', {'request': request, "user": user})
    else:
        return templates.TemplateResponse('about.html', {'request': request})


@router.get('/contacts', name='pages:contacts')
def about_info(request: Request, user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('contacts.html', {'request': request, "user": user})
    else:
        return templates.TemplateResponse('contacts.html', {'request': request})


@router.get('/search/{name}')
async def search_by_name(request: Request, name=Depends(get_manga_by_name), user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('search.html', {'request': request, 'content': name, "user": user})
    else:
        return templates.TemplateResponse('search.html', {'request': request, 'content': name})


@router.get('/search', name='pages:search')
def defoult_search(request: Request, user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('search.html', {'request': request, "user": user})
    else:
        return templates.TemplateResponse('search.html', {'request': request})


@router.get('/login', name='pages:login')
def profile_page(request: Request):
        return templates.TemplateResponse('login.html', {'request': request})


@router.get('/registed', name='pages:register')
def profile_page(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})


@router.get('/rules', name='pages:rules')
def profile_page( request: Request, user: User = Depends(current_user)):
    return templates.TemplateResponse('rules.html', {'request': request, "user": user})


@router.get('/profile', name='pages:profile')
def profile_page(request: Request, user: User = Depends(current_user)):
    if user:
        return templates.TemplateResponse('profile.html', {'request': request, "user": user})
    else:
        return templates.TemplateResponse('profile.html', {'request': request})