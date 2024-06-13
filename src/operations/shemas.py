from datetime import datetime
from pydantic import BaseModel

class Categories_create(BaseModel):
    id: int
    type: str

class Manga_create(BaseModel):
    id: int
    autor: str
    head: str
    cont: str
    categories: int
    chapter: int
    created_at: datetime