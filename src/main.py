import os
import shutil
import sys
from datetime import datetime

import rarfile
import logging

from fastapi.params import File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from operations.models import Mang

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

from fastapi import FastAPI, Depends, UploadFile, HTTPException
from fastapi_users import FastAPIUsers
from fastapi.staticfiles import StaticFiles

from auth.base_config import auth_backend
from database import User, get_async_session
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate

from pages.router import router as router_pages
from operations.router import router as operations_router

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(
    title='Manga'
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()

app.include_router(router_pages)
app.include_router(operations_router)

@app.get('/protected-route')
def protected_route(user: User = Depends(current_user)):
    return f'Hello, {user.username}'

@app.get('/unprotected-route')
def unprotected_route():
    return f'Hello, anonymus!'


@app.post('/manga/upload')
async def upload_manga(
        title: str = Form(...),
        about: str = Form(...),
        category: int = Form(...),
        article_file: UploadFile = File(...),
        user: str = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        logger.info("Начало процесса загрузки манги")
        # Проверка расширения файла
        if not article_file.filename.endswith('.rar'):
            logger.error("Неверный формат файла")
            raise HTTPException(status_code=400, detail="Неверный формат файла. Разрешены только .rar файлы.")

        # Сохранение файла
        save_path = f"static/manga/{article_file.filename}"
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(article_file.file, buffer)
        logger.info(f"Файл сохранён по пути {save_path}")

        # Разархивирование файла
        extract_path = f"static/manga/{os.path.splitext(article_file.filename)[0]}"
        os.makedirs(extract_path, exist_ok=True)
        with rarfile.RarFile(save_path) as rf:
            rf.extractall(extract_path)
        logger.info(f"Файл разархивирован в {extract_path}")

        # Запись в базу данных
        new_manga = Manga.insert().values(
            author=user.username,
            head=title,
            about=about,
            path_to_manga=extract_path[13:],
            categories=category,
            chapter=1,
            created_at=datetime.now()
        )
        await session.execute(new_manga)
        await session.commit()
        logger.info("Манга успешно добавлена в базу данных")

        return {"detail": "Манга успешно загружена."}

    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при загрузке манги: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()
        logger.info("Сессия закрыта")

@app.post('/chapter/add')
async def chapter_add(
        manga_id: str = Form(...),
        chapter_number: str = Form(...),
        chapter_file: UploadFile = File(...),
        user: str = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        print(manga_id)
        logger.info("Начало процесса загрузки главы")
        # Проверка расширения файла
        if not chapter_file.filename.endswith('.rar'):
            logger.error("Неверный формат файла")
            raise HTTPException(status_code=400, detail="Неверный формат файла. Разрешены только .rar файлы.")

        #запрос для получения данных основной записи манги
        query = (
            select(
                Manga.c.head,
                Manga.c.path_to_manga
            )
            .select_from(Manga)
            .where(Manga.c.id == int(manga_id))
        )

        result = await session.execute(query)
        manga_list = []
        for row in result:
            manga = {
                'title': row.head,
                'path': row.path_to_manga,
            }
            manga_list.append(manga)
        print(manga_list)
        # Сохранение файла
        save_path = f"static/manga/{manga_list[0]['path']}/{chapter_number}.rar"
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(chapter_file.file, buffer)
        logger.info(f"Файл сохранён по пути {save_path}")

        # Разархивирование файла
        extract_path = f"static/manga/{manga_list[0]['path']}/{chapter_number}"
        os.makedirs(extract_path, exist_ok=True)
        with rarfile.RarFile(save_path) as rf:
            rf.extractall(extract_path)
        logger.info(f"Файл разархивирован в {extract_path}")

        # Запись в базу данных
        new_manga = Manga.insert().values(
            author=user.username,
            head=manga_id,
            about="-",
            path_to_manga=manga_list[0]['path'],
            categories=3,
            chapter=int(chapter_number),
            created_at=datetime.now()
        )
        await session.execute(new_manga)
        await session.commit()
        logger.info("Новая глава успешно добавлена в базу данных")

        return {"detail": "Глава успешно загружена."}

    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при загрузке манги: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()
        logger.info("Сессия закрыта")
