import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, desc, join, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from operations.models import Manga, Categories

from pydantic import BaseModel
from datetime import datetime

class Manga_create(BaseModel):
    id: int
    autor: str
    head: str
    cont: str
    categories: int
    created_at: datetime

router = APIRouter(
    prefix='/content',
    tags=['Content']
)

# Роутер для получения всех манги по названию
@router.get('/')
async def get_manga_by_name(name: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(
                Manga.c.head,
                Manga.c.author,
                Manga.c.about,
                Manga.c.path_to_manga,
                Categories.c.type
            )
            .select_from(
                join(
                    Manga,
                    Categories,
                    Manga.c.categories == Categories.c.id
                )
            )
            .where(Manga.c.head.like(f'%{name}%'))
        )

        result = await session.execute(query)
        manga_list = []
        for row in result:
            manga = {
                'title': row.head,
                'author': row.author,
                'description': row.about,
                'path': row.path_to_manga,
                'category': row.type
            }
            manga_list.append(manga)

        return manga_list

    except sqlalchemy.exc.SQLAlchemyError as e:
        return {
            'status_code': 500,
            'status': 'error',
            'data': None,
            'details': str(e)
        }

@router.get('/')
async def get_manga_by_categories(type: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(
                Manga.c.head,
                Manga.c.author,
                Manga.c.about,
                Manga.c.path_to_manga,
                Categories.c.type
            )
            .select_from(
                join(
                    Manga,
                    Categories,
                    Manga.c.categories == Categories.c.id
                )
            )
            .where(Manga.c.categories == type)
        )

        result = await session.execute(query)
        manga_list = []
        for row in result:
            manga = {
                'title': row.head,
                'author': row.author,
                'description': row.about,
                'path': row.path_to_manga,
                'category': row.type
            }
            manga_list.append(manga)

        return manga_list

    except sqlalchemy.exc.SQLAlchemyError as e:
        return {
            'status_code': 500,
            'status': 'error',
            'data': None,
            'details': str(e)
        }

@router.get('/')
async def get_last_manga(session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(
                Manga.c.head,
                Manga.c.author,
                Manga.c.about,
                Manga.c.path_to_manga,
                Categories.c.type
            )
            .select_from(
                join(
                    Manga,
                    Categories,
                    Manga.c.categories == Categories.c.id
                )
            )
            .order_by(Manga.c.created_at.desc())
        )

        result = await session.execute(query)
        manga_list = []

        for row in result:
            # Проверка длины заголовка
            if len(row.head) >= 4:
                manga = {
                    'title': row.head,
                    'author': row.author,
                    'description': row.about,
                    'path': row.path_to_manga,
                    'category': row.type
                }
                manga_list.append(manga)

        return manga_list

    except sqlalchemy.exc.SQLAlchemyError as e:
        return {
            'status_code': 500,
            'status': 'error',
            'data': None,
            'details': str(e)
        }

@router.get('/count')
async def count_manga_by_title(title: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(func.count(Manga.c.id))
            .select_from(
                join(
                    Manga,
                    Categories,
                    Manga.c.categories == Categories.c.id
                )
            )
            .where(Manga.c.head == title)
        )

        result = await session.execute(query)
        count = result.scalar()

        return {"title": title, "count": count}

    except sqlalchemy.exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Роутер для добавления новой манги пользователем
@router.post('/')
async def add_article(new_content: Manga_create, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Manga).values(**new_content.dict())
    await session.execute(stmt)
    await session.commit()
    return {'status': 'good'}